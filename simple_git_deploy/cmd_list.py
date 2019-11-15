from .core import Config, Reporter, list_builds


def cmd_list(args, config: Config, reporter: Reporter):
    builds = list_builds(config.deploy_root)
    for build in sorted(builds, key=lambda build: build.build_id):
        print(
            "{selected:<1s} {id}".format(
                selected="*" if builds.is_selected(build) else "", id=build.build_id,
            )
        )


def register(subparsers):
    parser = subparsers.add_parser("list", help="list all prepared builds")
    parser.set_defaults(func=cmd_list)
