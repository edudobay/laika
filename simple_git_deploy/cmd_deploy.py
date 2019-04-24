from .core import Config, Reporter, prepare_new_tree, run_build, select_deploy_id


def cmd_deploy(args, config: Config, reporter: Reporter):
    reporter.info('Selecting git repository %s' % config.git_dir)
    tree = prepare_new_tree(
        deploy_root=config.deploy_root,
        fetch_first=args.fetch_first,
        git_ref=args.ref,
        git_dir=config.git_dir,
        reporter=reporter
    )
    run_build(tree, config.build_command, reporter)
    select_deploy_id(tree.tree_id, config, reporter)


def register(subparsers):
    parser = subparsers.add_parser('deploy', help='prepare a tree and deploy it')
    parser.add_argument('ref', help='the Git ref (commit, branch, tag) that should be deployed')
    parser.add_argument(
        '--no-fetch', dest='fetch_first', action='store_false',
        help='don\'t fetch from remote before running Git commands')
    parser.set_defaults(func=cmd_deploy)
