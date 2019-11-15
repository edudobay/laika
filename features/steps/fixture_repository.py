from behave import given, use_fixture

from testing_helpers.fixtures.git import default_git_repo


@given("the fixture repository")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    use_fixture(default_git_repo, context)
