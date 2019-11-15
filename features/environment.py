from behave import use_fixture

from testing_helpers.fixtures.git import root_dir


def before_scenario(context, scenario):
    use_fixture(root_dir, context)
