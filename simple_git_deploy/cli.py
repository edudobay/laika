#!/usr/bin/env python3
import argparse
import configparser
import datetime
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import inquirer

from .term_color import formatted_span as color


class Reporter:
    def success(self, message):
        print(color('green')('✔ %s' % message))

    def info(self, message):
        print(color('yellow')('> %s' % message))

    def error(self, message):
        print(color('red')('ERROR: %s' % message))


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


    @classmethod
    def read(cls):
        config = configparser.ConfigParser()

        # defaults
        config.read_dict({
            'dirs': {
                'git': '.',
            },
        })

        config_files = ['deploy.ini']
        if not config.read(config_files):
            raise RuntimeError('no configuration file could be read')

        return cls(config)


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


def prepare_new_tree(deploy_root: Path, git_ref: str, git_dir: str, reporter: Reporter):
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

    write_tree_meta(path, {
        'git_ref': git_ref,
        'hash': full_hash,
        'timestamp': timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'),
    })

    return Tree(tree_id, path, git_ref=git_ref)


class Tree:
    def __init__(self, tree_id: str, path: Path, git_ref: str):
        self.tree_id = tree_id
        self.path = path
        self.git_ref = git_ref


def run_build(tree: Tree, build_command: str, reporter: Reporter):
    reporter.info('Changing directory to %s' % tree.path)
    reporter.info('Running command: %s' % build_command)
    subprocess.run(build_command, shell=True, cwd=tree.path) \
        .check_returncode()


def cmd_build(args, config: Config, reporter: Reporter):
    reporter.info('Selecting git repository %s' % config.git_dir)
    tree = prepare_new_tree(config.deploy_root, args.ref, config.git_dir, reporter)
    run_build(tree, config.build_command, reporter)


def cmd_deploy(args, config: Config, reporter: Reporter):
    reporter.info('Selecting git repository %s' % config.git_dir)
    tree = prepare_new_tree(config.deploy_root, args.ref, config.git_dir, reporter)
    run_build(tree, config.build_command, reporter)
    select_deploy_id(tree.tree_id, config, reporter)


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


def get_tree_meta(tree: Path):
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
        meta = get_tree_meta(tree_path)
        git_ref = meta['git_ref'] if meta is not None else 'unknown_git_ref'
        return Tree(tree_path.name, tree_path, git_ref)

    return Trees(
        [get_tree(tree) for tree in tree_paths],
        current_tree_name
    )


def cmd_list(args, config: Config, reporter: Reporter):
    trees = list_trees(config.deploy_root)
    for tree in trees:
        print('{selected:<1s} {id}'.format(
            selected='*' if trees.is_selected(tree) else '',
            id=tree.tree_id,
        ))


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


def cmd_select(args, config: Config, reporter: Reporter):
    if args.deploy_id is None:
        trees = list_trees(config.deploy_root)

        if not trees:
            reporter.error('No deployment trees available')
            sys.exit(1)

        tree_ids = [tree.tree_id for tree in trees]

        questions = [inquirer.List(
            'deploy_id',
            message='Select a tree to deploy',
            choices=tree_ids,
            default=trees.current_id,
        )]
        answers = inquirer.prompt(questions)
        args.deploy_id = answers['deploy_id']

    select_deploy_id(args.deploy_id, config, reporter)


def _build_parser():
    parser = argparse.ArgumentParser()
    parser.set_defaults(func=None)

    subparsers = parser.add_subparsers(help='sub-commands')

    parser_build = subparsers.add_parser('build', help='prepare a new deployment tree, without actually deploying it')
    parser_build.add_argument('ref', help='the Git ref (commit, branch, tag) that should be prepared')
    parser_build.set_defaults(func=cmd_build)

    parser_deploy = subparsers.add_parser('deploy', help='prepare a tree and deploy it')
    parser_deploy.add_argument('ref', help='the Git ref (commit, branch, tag) that should be deployed')
    parser_deploy.set_defaults(func=cmd_deploy)

    parser_select = subparsers.add_parser('select', help='deploy an already prepared tree')
    parser_select.add_argument('deploy_id', nargs='?', help='the ID of the prepared tree')
    parser_select.set_defaults(func=cmd_select)

    parser_select = subparsers.add_parser('list', help='list all prepared trees')
    parser_select.set_defaults(func=cmd_list)

    return parser


def main():
    parser = _build_parser()
    args = parser.parse_args()

    reporter = Reporter()
    config = Config.read()

    if args.func is None:
        parser.print_usage()
        sys.exit(1)

    args.func(args, config, reporter)


if __name__ == '__main__':
    main()
