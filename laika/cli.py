#!/usr/bin/env python3
import argparse
import importlib
import warnings
import sys

from . import __version__
from .core import Config, Reporter, ConfigFileNotFound


def _build_parser():
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
        help="disable colors in output",
    )

    subparsers = parser.add_subparsers(help="sub-commands")

    modules = (
        "laika.cmd_%s" % cmd for cmd in ("build", "deploy", "list", "purge", "select")
    )

    for module in (importlib.import_module(name) for name in modules):
        module.register(subparsers)

    return parser


def main():
    parser = _build_parser()

    if parser.prog.endswith("simple-git-deploy"):
        from textwrap import dedent

        msg = dedent(
            """\
            simple-git-deploy has been renamed to laika. Please switch to the new command.
            The old command will be removed in the next release.
            """
        )
        warnings.warn(msg, FutureWarning)

    args = parser.parse_args()

    reporter = Reporter(color=args.color)
    try:
        config = Config.read(args.config_file)
    except ConfigFileNotFound as e:
        print("ERROR: Config file not found: %s" % e.args)
        sys.exit(2)

    if args.func is None:
        parser.print_usage()
        sys.exit(1)

    args.func(args, config, reporter)


if __name__ == "__main__":
    main()
