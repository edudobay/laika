from laika.core import Config, Reporter, list_builds, Build


def cmd_list(args, config: Config, reporter: Reporter):
    def format_flags(build: Build) -> str:
        flags = []
        if build.is_metadata_missing():
            flags.append("(invalid)")

        if flags:
            return " " + " ".join(flags)
        return ""

    builds = list_builds(config.deploy_root)
    for build in sorted(builds, key=lambda build: build.build_id):
        print(
            "{selected:<1s} {id}{flags}".format(
                selected="*" if builds.is_selected(build) else "",
                id=build.build_id,
                flags=format_flags(build),
            )
        )


def register(subparsers):
    parser = subparsers.add_parser("list", help="list all prepared builds")
    parser.set_defaults(func=cmd_list)
