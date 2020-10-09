from .core import (
    Config,
    Reporter,
    checkout_tree_for_build,
    run_build,
    deploy_prepared_build,
    GitRevisionParseFail,
    TerminateApplication,
)


def cmd_deploy(args, config: Config, reporter: Reporter):
    reporter.info("Selecting git repository %s" % config.git_dir)
    try:
        build = checkout_tree_for_build(
            deploy_root=config.deploy_root,
            fetch_first=args.fetch_first,
            git_ref=args.ref,
            git_dir=config.git_dir,
            reporter=reporter,
        )
        run_build(build, config, reporter)
        deploy_prepared_build(build, config, reporter)
    except GitRevisionParseFail:
        reporter.error(f"Invalid git reference: {args.ref}")
        raise TerminateApplication(1)


def register(subparsers):
    parser = subparsers.add_parser("deploy", help="prepare a build and deploy it")
    parser.add_argument(
        "ref", help="the Git ref (commit, branch, tag) that should be deployed"
    )
    parser.add_argument(
        "--no-fetch",
        dest="fetch_first",
        action="store_false",
        help="don't fetch from remote before running Git commands",
    )
    parser.set_defaults(func=cmd_deploy)
