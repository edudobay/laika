import os.path
import shlex
import subprocess

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

    proc = subprocess.run(args, cwd=cwd, capture_output=True, encoding="utf-8")
    context.last_command_status_code = proc.returncode
    context.last_command_output = proc.stdout


@then("we should get status code {expected_status_code:d} and the following output")
def step_impl(context, expected_status_code):
    """
    :type context: behave.runner.Context
    :type expected_status_code: int
    """
    actual_status_code = context.last_command_status_code
    assert (
            actual_status_code == expected_status_code
    ), f"Returned status code {actual_status_code} doesn't match expected {expected_status_code}"

    output = context.last_command_output
    assert output == context.text, f"Actual output {output!r} doesn't match expected {context.text!r}"
