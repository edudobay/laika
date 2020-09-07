import pytest

from testing_helpers.dirs import DirectoryContext


@pytest.yield_fixture
def git_dir():
    with DirectoryContext() as tempdir:
        tempdir.run(["git", "init", "."])
        yield tempdir


# noinspection PyShadowingNames
def test_one(git_dir: DirectoryContext):
    with open(git_dir.path / "hello.txt", "w") as stream:
        stream.write("hello world")

    git_dir.run(["git", "add", "."])
    git_dir.run(["git", "commit", "-m", "C1"])

    cmd = git_dir.run(
        ["git", "log", "--oneline", "--pretty=format:%s"],
        capture_output=True,
        encoding='ascii'
    )
    assert cmd.stdout == 'C1'


