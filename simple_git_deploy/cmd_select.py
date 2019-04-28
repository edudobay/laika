import sys

import inquirer  # type: ignore

from .core import Config, Reporter, list_trees, select_deploy_id


def cmd_select(args, config: Config, reporter: Reporter):
    if args.deploy_id is None:
        trees = list_trees(config.deploy_root)

        if not trees:
            reporter.error('No deployment trees available')
            sys.exit(1)

        tree_ids = sorted(
            [tree.tree_id for tree in trees],
            reverse=True
        )

        questions = [inquirer.List(
            'deploy_id',
            message='Select a tree to deploy',
            choices=tree_ids,
            default=trees.current_id,
        )]
        answers = inquirer.prompt(questions)
        if answers is None:
            return

        args.deploy_id = answers['deploy_id']

    select_deploy_id(args.deploy_id, config, reporter)


def register(subparsers):
    parser = subparsers.add_parser('select', help='deploy an already prepared tree')
    parser.add_argument('deploy_id', nargs='?', help='the ID of the prepared tree')
    parser.set_defaults(func=cmd_select)
