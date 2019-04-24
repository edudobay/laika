from .core import Config, Reporter, list_trees


def cmd_list(args, config: Config, reporter: Reporter):
    trees = list_trees(config.deploy_root)
    for tree in sorted(trees, key=lambda tree: tree.tree_id):
        print('{selected:<1s} {id}'.format(
            selected='*' if trees.is_selected(tree) else '',
            id=tree.tree_id,
        ))


def register(subparsers):
    parser = subparsers.add_parser('list', help='list all prepared trees')
    parser.set_defaults(func=cmd_list)
