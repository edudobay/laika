import configparser
import datetime
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Optional

from .output import Reporter


class ConfigError(RuntimeError):
    pass


class ConfigFileNotFound(ConfigError):
    pass


class Config:
    def __init__(self, config: configparser.ConfigParser):
        self.config = config

    def _get_dir(self, dir_spec: str) -> Path:
        return Path(os.path.realpath(os.path.expanduser(dir_spec)))

    @property
    def git_dir(self) -> Path:
        return self._get_dir(self.config["dirs"]["git"])

    @property
    def deploy_root(self) -> Path:
        return self._get_dir(self.config["dirs"]["deploy"])

    @property
    def build_command(self) -> str:
        return self.config["build"]["run"]

    @property
    def post_deploy_command(self) -> Optional[str]:
        return self.config.get("post_deploy", "run", fallback=None)

    @property
    def purge_what(self) -> Optional[str]:
        return self.config["purge"].get("what")

    @classmethod
    def read(cls, filename):
        config = configparser.ConfigParser()

        # defaults
        config.read_dict(
            {"dirs": {"git": ".",}, "purge": {},}
        )

        config_files = [filename]
        if not config.read(config_files):
            raise ConfigFileNotFound(os.path.realpath(filename))

        return cls(config)


class BuildMeta:
    def __init__(self, source_path, git_ref, git_hash, timestamp):
        self.source_path = source_path
        self.git_ref = git_ref
        self.git_hash = git_hash
        self.timestamp = timestamp

    @classmethod
    def from_dict(cls, d):
        d = dict(d)
        version = d.pop("version", "0")

        d["source_path"] = d.pop("source_path", None)
        d["timestamp"] = datetime.datetime.strptime(
            d["timestamp"], "%Y-%m-%dT%H:%M:%SZ"
        )

        if version == "0":
            d["git_hash"] = d.pop("hash", None)

        return cls(**d)

    def to_dict(self):
        return dict(
            version="1",
            source_path=self.source_path,
            git_ref=self.git_ref,
            git_hash=self.git_hash,
            timestamp=self.timestamp,
        )


class Build:
    def __init__(self, build_id: str, path: Path, meta: BuildMeta):
        self.build_id = build_id
        self.path = path
        self.meta = meta


class Builds:
    def __init__(self, builds, current_id):
        self.builds = builds
        self.current_id = current_id

    def __iter__(self):
        return iter(self.builds)

    def __bool__(self):
        return bool(self.builds)

    def is_selected(self, build):
        return build.build_id == self.current_id


class BuildMetaFile:
    _PATH = "_tree_meta.json"

    @classmethod
    def read(cls, build_dir: Path) -> BuildMeta:
        file_path = build_dir / cls._PATH
        if not file_path.exists():
            raise FileNotFoundError(f"Build metadata file not found: {file_path}")

        with file_path.open() as stream:
            return BuildMeta.from_dict(json.load(stream))

    @classmethod
    def write(cls, build_dir: Path, meta: BuildMeta):
        file_path = build_dir / cls._PATH
        with file_path.open("w") as stream:
            json.dump(meta.to_dict(), stream)


def git_rev_parse_short(ref, gitdir=None):
    return subprocess.check_output(
        ["git", "rev-parse", "--short", ref + "^{commit}"],
        cwd=gitdir,
        encoding="utf-8",
    ).strip()


def git_rev_parse(ref, gitdir=None):
    return subprocess.check_output(
        ["git", "rev-parse", ref + "^{commit}"], cwd=gitdir, encoding="utf-8",
    ).strip()


def normalize_refname(refname):
    return re.sub(r"[^a-zA-Z0-9_-]", "--", refname)


def checkout_tree_for_build(
    deploy_root: Path,
    fetch_first: bool,
    git_ref: str,
    git_dir: Path,
    reporter: Reporter,
):
    if fetch_first:
        # TODO: Allow fetching from different remote or from --all
        reporter.info("Fetching from default remote")
        subprocess.run(["git", "fetch"], cwd=git_dir).check_returncode()

    hash = git_rev_parse_short(git_ref, git_dir)
    full_hash = git_rev_parse(git_ref, git_dir)
    timestamp = datetime.datetime.utcnow()

    build_id = "{timestamp:%Y%m%d%H%M%S}_{hash}_{refname}".format(
        timestamp=timestamp, hash=hash, refname=normalize_refname(git_ref),
    )

    path = deploy_root / build_id

    reporter.info(
        "Checking out git ref {git_ref} at directory {path}".format(
            git_ref=git_ref, path=path
        )
    )
    subprocess.run(
        ["git", "worktree", "add", "--detach", str(path), git_ref], cwd=git_dir
    ).check_returncode()

    meta = BuildMeta(
        source_path=os.path.realpath(git_dir),
        git_ref=git_ref,
        git_hash=full_hash,
        timestamp=timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
    )
    BuildMetaFile.write(path, meta)

    return Build(build_id, path, meta)


def load_build(build_id: str, deploy_root: Path,) -> Build:
    path = deploy_root / build_id
    return get_build(path)


def run_command_on_build(
    command: str, build: Build, config: Config, reporter: Reporter
):
    reporter.info("Changing directory to %s" % build.path)
    reporter.info("Running command: %s" % command)

    hydrated_environment = {
        **os.environ,
        "DIR_SOURCE": str(build.meta.source_path),
        "DIR_DEPLOY": str(build.path),
        "DEPLOY_GIT_REF": build.meta.git_ref,
        "DEPLOY_GIT_HASH": build.meta.git_hash,
    }

    subprocess.run(
        command, shell=True, cwd=build.path, env=hydrated_environment, check=True
    )


def run_build(build: Build, config: Config, reporter: Reporter):
    run_command_on_build(config.build_command, build, config, reporter)


def get_build(build_path: Path) -> Build:
    meta = BuildMetaFile.read(build_path)
    return Build(build_path.name, build_path, meta)


def list_builds(deploy_path: Path) -> Builds:
    build_paths = sorted(
        d for d in deploy_path.iterdir() if not d.is_symlink() and d.is_dir()
    )

    def resolve_current_build(build):
        if build.is_symlink():
            if not build.is_dir():
                raise RuntimeError(
                    "current build is not symlink to dir: {}".format(build)
                )
            target = build.resolve(strict=True)
            if not target.parent.samefile(deploy_path):
                raise RuntimeError(
                    "current build does not point to dir in deploy path: {}".format(
                        build
                    )
                )

            return target.name
        elif build.exists():
            raise RuntimeError(
                "current build must be symlink to sibling directory: {}".format(build)
            )
        else:
            return None

    current_build_name = resolve_current_build(deploy_path / "current")

    return Builds([get_build(build) for build in build_paths], current_build_name)


def post_deploy(build: Build, config: Config, reporter: Reporter):
    command = config.post_deploy_command
    if not command:
        return

    run_command_on_build(command, build, config, reporter)


def deploy_prepared_build(build: Build, config: Config, reporter: Reporter):
    deploy_id = build.build_id
    root = config.deploy_root

    current = root / "current"
    current_new = root / "current.new"

    deploy_target = root / deploy_id
    if not deploy_target.is_dir():
        raise RuntimeError("build must exist: {}".format(deploy_target))

    reporter.info("Linking new version (%s)" % deploy_id)
    os.symlink(deploy_id, current_new)
    os.replace(current_new, current)
    reporter.success("Activated deployment %s" % deploy_id)

    post_deploy(build, config, reporter)

    reporter.success("Deployed %s" % deploy_id)
