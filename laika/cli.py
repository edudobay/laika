#!/usr/bin/env python3
import argparse
import os
import sys

import laika.commands
from . import __version__
from .core import Config, Reporter, ConfigFileNotFound, TerminateApplication


def _build_parser(default_no_color=None):
    parser = argparse.ArgumentParser()
    parser.set_defaults(func=None)

    parser.add_argument(
        "--version",
        action="version",
        version=__version__,
        help="show the program version and exit",
    )

    parser.add_argument(
        "-C",
        "--config-file",
        metavar="FILE",
        default="deploy.ini",
        help="specify an alternate config file (default: %(default)s)",
    )

    parser.add_argument(
        "--no-color",
        action="store_false",
        dest="color",
        help="""
            disable colors in output. Can be also be set via environment variable NO_COLOR
        """,
        default=False if default_no_color else True,
    )

    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="""
            suppress normal informative output
        """,
    )

    subparsers = parser.add_subparsers(help="sub-commands")

    for module in laika.commands.find_available_command_modules():
        module.register(subparsers)

    return parser


def main():
    # See: https://no-color.org/
    default_no_color = os.getenv("NO_COLOR") is not None

    parser = _build_parser(default_no_color=default_no_color)

    args = parser.parse_args()

    reporter = Reporter(color=args.color, quiet=args.quiet)
    try:
        config = Config.read(args.config_file)
    except ConfigFileNotFound as e:
        print("ERROR: Config file not found: %s" % e.args)
        sys.exit(2)

    if args.func is None:
        parser.print_usage()
        sys.exit(1)

    try:
        args.func(args, config, reporter)
    except TerminateApplication as e:
        sys.exit(e.status)


if __name__ == "__main__":
    main()
