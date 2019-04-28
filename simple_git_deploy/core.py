import configparser
import datetime
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Optional

from .output import Reporter


class Config:
    def __init__(self, config):
        self.config = config


    def _get_dir(self, dir_spec: str) -> Path:
        return Path(os.path.realpath(os.path.expanduser(dir_spec)))

    @property
    def git_dir(self) -> Path:
        return self._get_dir(self.config['dirs']['git'])


    @property
    def deploy_root(self) -> Path:
        return self._get_dir(self.config['dirs']['deploy'])


    @property
    def build_command(self) -> str:
        return self.config['build']['run']


    @property
    def purge_what(self) -> Optional[str]:
        return self.config['purge'].get('what')


    @classmethod
    def read(cls, filename):
        config = configparser.ConfigParser()

        # defaults
        config.read_dict({
            'dirs': {
                'git': '.',
            },
            'purge': {
            },
        })

        config_files = [filename]
        if not config.read(config_files):
            raise RuntimeError('no configuration file could be read')

        return cls(config)


class TreeMeta:
    def __init__(self, source_path, git_ref, git_hash, timestamp):
        self.source_path = source_path
        self.git_ref = git_ref
        self.git_hash = git_hash
        self.timestamp = timestamp


    @classmethod
    def from_dict(cls, d):
        d = dict(d)
        version = d.pop('version', '0')

        d['source_path'] = d.pop('source_path', None)
        d['timestamp'] = datetime.datetime.strptime(d['timestamp'], '%Y-%m-%dT%H:%M:%SZ')

        if version == '0':
            d['git_hash'] = d.pop('hash', None)

        return cls(**d)


    def to_dict(self):
        return dict(
            version='1',
            source_path=self.source_path,
            git_ref=self.git_ref,
            git_hash=self.git_hash,
            timestamp=self.timestamp,
        )


class Tree:
    def __init__(self, tree_id: str, path: Path, meta: TreeMeta):
        self.tree_id = tree_id
        self.path = path
        self.meta = meta


class Trees:
    def __init__(self, trees, current_id):
        self.trees = trees
        self.current_id = current_id


    def __iter__(self):
        return iter(self.trees)


    def __bool__(self):
        return bool(self.trees)


    def is_selected(self, tree):
        return tree.tree_id == self.current_id


def git_rev_parse_short(ref, gitdir=None):
    return subprocess.check_output(
        ['git', 'rev-parse', '--short', ref + '^{commit}'],
        cwd=gitdir,
        encoding='utf-8',
    ).strip()


def git_rev_parse(ref, gitdir=None):
    return subprocess.check_output(
        ['git', 'rev-parse', ref + '^{commit}'],
        cwd=gitdir,
        encoding='utf-8',
    ).strip()


def normalize_refname(refname):
    return re.sub(r'[^a-zA-Z0-9_-]', '--', refname)


def prepare_new_tree(deploy_root: Path, fetch_first: bool, git_ref: str, git_dir: Path, reporter: Reporter):
    if fetch_first:
        # TODO: Allow fetching from different remote or from --all
        reporter.info('Fetching from default remote')
        subprocess.run(['git', 'fetch'], cwd=git_dir) \
            .check_returncode()

    hash = git_rev_parse_short(git_ref, git_dir)
    full_hash = git_rev_parse(git_ref, git_dir)
    timestamp = datetime.datetime.utcnow()

    tree_id = '{timestamp:%Y%m%d%H%M%S}_{hash}_{refname}'.format(
        timestamp=timestamp,
        hash=hash,
        refname=normalize_refname(git_ref),
    )

    path = deploy_root / tree_id

    reporter.info('Creating working tree at %s with git ref %s' % (path, git_ref))
    subprocess.run(
        ['git', 'worktree', 'add', '--detach', str(path), git_ref],
        cwd=git_dir
    ) \
        .check_returncode()

    meta = TreeMeta(
        source_path=os.path.realpath(git_dir),
        git_ref=git_ref,
        git_hash=full_hash,
        timestamp=timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'),
    )
    write_tree_meta(path, meta.to_dict())

    return Tree(tree_id, path, meta)


def run_build(
        tree: Tree,
        build_command: str,
        reporter: Reporter,
):
    reporter.info('Changing directory to %s' % tree.path)
    reporter.info('Running command: %s' % build_command)

    hydrated_environment = {
        **os.environ,
        'DIR_SOURCE': str(tree.meta.source_path),
        'DIR_DEPLOY': str(tree.path),
        'DEPLOY_GIT_REF': tree.meta.git_ref,
        'DEPLOY_GIT_HASH': tree.meta.git_hash,
    }

    subprocess.run(
        build_command,
        shell=True,
        cwd=tree.path,
        env=hydrated_environment,
    ) \
        .check_returncode()


def read_tree_meta(tree: Path):
    file_path = tree / '_tree_meta.json'
    if not file_path.exists():
        return None

    with file_path.open() as stream:
        return json.load(stream)


def write_tree_meta(tree: Path, meta: dict):
    file_path = tree / '_tree_meta.json'
    with file_path.open('w') as stream:
        json.dump(meta, stream)


def list_trees(deploy_path: Path) -> Trees:
    tree_paths = sorted(
        d
        for d in deploy_path.iterdir()
        if not d.is_symlink() and d.is_dir()
    )

    def resolve_current_tree(tree):
        if tree.is_symlink():
            if not tree.is_dir():
                raise RuntimeError('current tree is not symlink to dir: {}'.format(tree))
            target = tree.resolve(strict=True)
            if not target.parent.samefile(deploy_path):
                raise RuntimeError('current tree does not point to dir in deploy path: {}'.format(tree))

            return target.name
        elif tree.exists():
            raise RuntimeError('current tree must be symlink to sibling directory: {}'.format(tree))
        else:
            return None

    current_tree_name = resolve_current_tree(deploy_path / 'current')

    def get_tree(tree_path: Path) -> Tree:
        meta = read_tree_meta(tree_path)
        meta = TreeMeta.from_dict(meta)
        return Tree(tree_path.name, tree_path, meta)

    return Trees(
        [get_tree(tree) for tree in tree_paths],
        current_tree_name
    )


def select_deploy_id(deploy_id: str, config: Config, reporter: Reporter):
    root = config.deploy_root

    current = root / 'current'
    if current.is_symlink():
        reporter.info('Unlinking current version (%s)' % os.readlink(current))
        os.unlink(current)

    deploy_target = root / deploy_id
    if not deploy_target.is_dir():
        raise RuntimeError('deployment tree must exist: {}'.format(deploy_target))

    reporter.info('Linking new version (%s)' % deploy_id)
    os.symlink(deploy_id, current)
    reporter.success('Deployed %s' % deploy_id)
