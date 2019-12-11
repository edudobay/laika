from behave import given, use_fixture

from testing_helpers.fixtures.git import (
    default_git_repo,
    set_build_command,
    set_post_deploy_command,
)


@given("the fixture repository")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    use_fixture(default_git_repo, context)


@given("the build command is set to {command}")
def step_impl(context, command):
    """
    :type context: behave.runner.Context
    :type command: str
    """
    set_build_command(context, command)


@given("the post-deploy command is set to {command}")
def step_impl(context, command):
    """
    :type context: behave.runner.Context
    :type command: str
    """
    set_post_deploy_command(context, command)
