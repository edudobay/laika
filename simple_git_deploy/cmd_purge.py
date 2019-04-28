import argparse
import sys

from .core import Config, Reporter, purge_deployments
import dateparser  # type: ignore


def cmd_purge(args, config: Config, reporter: Reporter):
    reporter.info('Selecting git repository %s' % config.git_dir)
    purge_deployments(
        deploy_root=config.deploy_root,
        dry_run=args.dry_run,
        keep_latest=args.keep_latest,
        older_than=args.older_than,
        git_dir=config.git_dir,
        reporter=reporter
    )


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
