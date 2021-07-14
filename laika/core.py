import configparser
import datetime
import json
import os
import subprocess
from pathlib import Path
from typing import Optional, Sequence

from .output import Reporter

DEFAULT_SECTION = "general"


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

    @property
    def shell(self) -> Optional[str]:
        return self.config[DEFAULT_SECTION].get("shell")

    @classmethod
    def read(cls, filename):
        config = configparser.ConfigParser(default_section=DEFAULT_SECTION)

        # defaults
        config.read_dict(
            {"dirs": {"git": ".",}, "purge": {},}
        )

        config_files = [filename]
        if not config.read(config_files):
            raise ConfigFileNotFound(os.path.realpath(filename))

        return cls(config)


class TerminateApplication(RuntimeError):
    def __init__(self, status: int):
        super().__init__(status)
        self.status = status


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


def build_command_line(args):
    return [arg for arg in args if arg is not None]


def load_build(build_id: str, deploy_root: Path,) -> Build:
    path = deploy_root / build_id
    return get_build(path)


def build_shell_command(command: str, config: Config) -> Sequence[str]:
    shell = config.shell or "/bin/sh"
    return [shell, "-c", command]


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
        build_shell_command(command, config),
        cwd=build.path,
        env=hydrated_environment,
        check=True,
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
