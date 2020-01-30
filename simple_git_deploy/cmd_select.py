import sys

import inquirer  # type: ignore

from .core import Config, Reporter, list_builds, load_build, deploy_prepared_build


def cmd_select(args, config: Config, reporter: Reporter):
    if args.deploy_id is None:
        builds = list_builds(config.deploy_root)

        if not builds:
            reporter.error("No builds available")
            sys.exit(1)

        build_ids = sorted([build.build_id for build in builds], reverse=True)

        questions = [
            inquirer.List(
                "deploy_id",
                message="Select a build to deploy",
                choices=build_ids,
                default=builds.current_id,
            )
        ]
        answers = inquirer.prompt(questions)
        if answers is None:
            return

        args.deploy_id = answers["deploy_id"]

    build_id = args.deploy_id
    build = load_build(build_id, config.deploy_root)
    deploy_prepared_build(build, config, reporter)


def register(subparsers):
    parser = subparsers.add_parser("select", help="deploy an already prepared build")
    parser.add_argument("deploy_id", nargs="?", help="the ID of the prepared build")
    parser.set_defaults(func=cmd_select)
