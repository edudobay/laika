import datetime
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable, List

from .core import Build, list_builds
from .output import Reporter


class PurgeSpecification(ABC):
    @abstractmethod
    def filter(self, builds: Iterable[Build]) -> List[Build]:
        pass

    @abstractmethod
    def describe(self) -> str:
        pass

    @classmethod
    def sort_latest_first(cls, builds: Iterable[Build]):
        return sorted(builds, key=lambda build: build.meta.timestamp, reverse=True)

    @classmethod
    def keep_latest(cls, num_latest: int) -> "PurgeSpecification":
        return KeepLatestN(num_latest)

    @classmethod
    def discard_older_than(
        cls, oldest_allowed_datetime: datetime.datetime
    ) -> "PurgeSpecification":
        return DiscardOlderThan(oldest_allowed_datetime)


class KeepLatestN(PurgeSpecification):
    def __init__(self, num_latest: int):
        if not isinstance(num_latest, int) or num_latest < 0:
            raise ValueError("num_latest must be a non-negative integer")
        self.num_latest = num_latest

    def filter(self, builds):
        return self.sort_latest_first(builds)[self.num_latest :]

    def describe(self):
        return "Keeping %d latest deployments" % self.num_latest


class DiscardOlderThan(PurgeSpecification):
    def __init__(self, oldest_allowed_datetime: datetime.datetime):
        if not isinstance(oldest_allowed_datetime, datetime.datetime):
            raise TypeError("oldest_allowed_datetime must be a datetime.datetime")
        self.oldest_allowed_datetime = oldest_allowed_datetime

    def filter(self, builds):
        return [
            build
            for build in self.sort_latest_first(builds)
            if build.meta.timestamp < self.oldest_allowed_datetime
        ]

    def describe(self):
        return "Keeping deployments since %s" % self.oldest_allowed_datetime.isoformat(
            " "
        )


def purge_deployments(
    *,
    deploy_root: Path,
    git_dir: Path,
    dry_run: bool,
    what_to_purge: PurgeSpecification,
    reporter: Reporter
):
    builds = list_builds(deploy_root)
    eligible_for_removal = [build for build in builds if not builds.is_selected(build)]

    reporter.info(what_to_purge.describe())

    to_remove = what_to_purge.filter(eligible_for_removal)

    if dry_run:
        reporter.info("Dry-run; not going to remove anything")

    reporter.info(
        "{selected} builds selected for removal, out of {eligible} that could be removed".format(
            eligible=len(eligible_for_removal), selected=len(to_remove),
        )
    )
    for build in to_remove:
        reporter.info(
            "Remove {build.build_id}, created on {build.meta.timestamp:%Y-%m-%d %H:%M:%S UTC}".format(
                build=build
            )
        )
        if not dry_run:
            subprocess.run(
                ["git", "worktree", "remove", "--force", str(build.path)], cwd=git_dir
            ).check_returncode()
