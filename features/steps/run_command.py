import os.path
import shlex
import subprocess

from assertpy import assert_that
from behave import *

from testing_helpers.fixtures.git import TARGET_DIR, SOURCE_DIR

KNOWN_DIRS = {
    "target": TARGET_DIR,
    "deployment": TARGET_DIR + "/current",
    "source": SOURCE_DIR,
}


def resolve_known_dir(directory, context):
    path = KNOWN_DIRS[directory]
    return os.path.join(context.root_dir.path, path)


@when("on the {directory} dir we run the command: {command}")
def step_impl(context, directory, command):
    """
    :type context: behave.runner.Context
    :type directory: str
    :type command: str
    """
    args = shlex.split(command)
    cwd = resolve_known_dir(directory, context)
    env = {**os.environ, "NO_COLOR": ""}

    proc = subprocess.run(args, cwd=cwd, env=env, capture_output=True, encoding="utf-8")
    context.last_command_status_code = proc.returncode
    context.last_command_output = proc.stdout
    context.last_command_error_output = proc.stderr


@then("we should get status code {expected_status_code:d} and the following output")
def step_impl(context, expected_status_code):
    """
    :type context: behave.runner.Context
    :type expected_status_code: int
    """
    assert_that(context.last_command_status_code).is_equal_to(expected_status_code)
    assert_that(context.last_command_output).is_equal_to(context.text)


@then(
    "we should get status code {expected_status_code:d} and the following error output"
)
def step_impl(context, expected_status_code):
    """
    :type context: behave.runner.Context
    :type expected_status_code: int
    """
    assert_that(context.last_command_status_code).is_equal_to(expected_status_code)
    assert_that(context.last_command_error_output).is_equal_to(context.text)


@then("we should get status code {expected_status_code:d}")
def step_impl(context, expected_status_code):
    """
    :type context: behave.runner.Context
    :type expected_status_code: int
    """
    assert_that(context.last_command_status_code).is_equal_to(expected_status_code)
