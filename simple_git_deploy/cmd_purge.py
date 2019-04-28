import argparse
import sys
from typing import Optional

import dateparser  # type: ignore

from .core import Config, PurgeSpecification, Reporter, purge_deployments


def cmd_purge(args, config: Config, reporter: Reporter):
    what_to_purge = _find_what_to_purge(args)
    if what_to_purge is None:
        reporter.error('No valid purge settings found')
        sys.exit(1)

    reporter.info('Selecting git repository %s' % config.git_dir)

    purge_deployments(
        deploy_root=config.deploy_root,
        dry_run=args.dry_run,
        what_to_purge=what_to_purge,
        git_dir=config.git_dir,
        reporter=reporter
    )


def _find_what_to_purge(args) -> Optional[PurgeSpecification]:
    if args.keep_latest is not None:
        return PurgeSpecification.keep_latest(args.keep_latest)
    elif args.older_than is not None:
        return PurgeSpecification.discard_older_than(args.older_than)
    else:
        return None


def relative_time(string):
    parsed = dateparser.parse(string, settings={
        'PREFER_DATES_FROM': 'past',
        'TIMEZONE': 'UTC',
    })
    if parsed is None:
        raise argparse.ArgumentTypeError('%r could not be parsed as a date/time' % string)

    return parsed


def non_negative_int(string):
    value = int(string)
    if value < 0:
        raise argparse.ArgumentTypeError('%r is negative' % string)

    return value


def register(subparsers):
    parser = subparsers.add_parser('purge', help='remove old trees')
    parser.add_argument(
        '--dry-run', action='store_true',
        help='don\'t remove anything, only print what would be removed')

    which = parser.add_mutually_exclusive_group()
    which.add_argument(
        '--older-than', metavar='DATETIME', type=relative_time,
        help='remove deployments older than this date/time')
    which.add_argument(
        '--keep-latest', metavar='N', type=non_negative_int,
        help='keep this amount of latest deployments (besides the current one)')

    parser.set_defaults(func=cmd_purge)
