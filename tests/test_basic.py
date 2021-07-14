import pytest

from testing_helpers.dirs import DirectoryContext
from testing_helpers.git import GitRepo


@pytest.fixture
def git_repo():
    with DirectoryContext() as tempdir:
        repo = GitRepo(tempdir.path)
        repo.create()
        yield repo


# noinspection PyShadowingNames
def test_one(git_repo: GitRepo):
    with open(git_repo.dirname / "hello.txt", "w") as stream:
        stream.write("hello world")

    git_repo.run(["git", "add", "."])
    git_repo.run(["git", "commit", "-m", "C1"])

    cmd = git_repo.run(
        ["git", "log", "--oneline", "--pretty=format:%s"], encoding="ascii"
    )
    assert cmd.stdout == "C1"
