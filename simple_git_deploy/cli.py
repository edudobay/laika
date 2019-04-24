#!/usr/bin/env python3
import argparse
import importlib
import sys

from .core import Config, Reporter


def _build_parser():
    parser = argparse.ArgumentParser()
    parser.set_defaults(func=None)

    subparsers = parser.add_subparsers(help='sub-commands')

    modules = (
        'simple_git_deploy.cmd_%s' % cmd for cmd in (
            'build', 'deploy', 'list', 'purge', 'select'
        )
    )

    for module in (importlib.import_module(name) for name in modules):
        module.register(subparsers)

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
