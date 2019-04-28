import datetime
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable, List

from .core import Tree, list_trees
from .output import Reporter


class PurgeSpecification(ABC):
    @abstractmethod
    def filter(self, trees: Iterable[Tree]) -> List[Tree]: pass

    @abstractmethod
    def describe(self) -> str: pass

    @classmethod
    def sort_latest_first(cls, trees: Iterable[Tree]):
        return sorted(
            trees,
            key=lambda tree: tree.meta.timestamp,
            reverse=True
        )

    @classmethod
    def keep_latest(cls, num_latest: int) -> 'PurgeSpecification':
        return KeepLatestN(num_latest)

    @classmethod
    def discard_older_than(cls, oldest_allowed_datetime: datetime.datetime) -> 'PurgeSpecification':
        return DiscardOlderThan(oldest_allowed_datetime)


class KeepLatestN(PurgeSpecification):
    def __init__(self, num_latest: int):
        if not isinstance(num_latest, int) or num_latest < 0:
            raise ValueError('num_latest must be a non-negative integer')
        self.num_latest = num_latest

    def filter(self, trees):
        return self.sort_latest_first(trees)[self.num_latest:]

    def describe(self):
        return 'Keeping %d latest deployments' % self.num_latest


class DiscardOlderThan(PurgeSpecification):
    def __init__(self, oldest_allowed_datetime: datetime.datetime):
        if not isinstance(oldest_allowed_datetime, datetime.datetime):
            raise TypeError('oldest_allowed_datetime must be a datetime.datetime')
        self.oldest_allowed_datetime = oldest_allowed_datetime

    def filter(self, trees):
        return [
            tree for tree in self.sort_latest_first(trees)
            if tree.meta.timestamp < self.oldest_allowed_datetime
        ]

    def describe(self):
        return 'Keeping deployments since %s' % self.oldest_allowed_datetime.isoformat(' ')


def purge_deployments(*,
        deploy_root: Path,
        git_dir: Path,
        dry_run: bool,
        what_to_purge: PurgeSpecification,
        reporter: Reporter
):
    trees = list_trees(deploy_root)
    eligible_for_removal = [
        tree for tree in trees
        if not trees.is_selected(tree)
    ]

    reporter.info(what_to_purge.describe())

    to_remove = what_to_purge.filter(eligible_for_removal)

    if dry_run:
        reporter.info('Dry-run; not going to remove anything')

    reporter.info('{selected} trees selected for removal, out of {eligible} that could be removed'.format(
        eligible=len(eligible_for_removal),
        selected=len(to_remove),
    ))
    for tree in to_remove:
        reporter.info('Remove {tree.tree_id}, created on {tree.meta.timestamp:%Y-%m-%d %H:%M:%S UTC}'.format(tree=tree))
        if not dry_run:
            subprocess.run(
                ['git', 'worktree', 'remove', '--force', str(tree.path)],
                cwd=git_dir
            ).check_returncode()
