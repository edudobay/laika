import os
import pathlib
import subprocess


class GitRepo:
    INITIAL_BRANCH = "main"

    def __init__(self, dirname: pathlib.Path):
        self.dirname = dirname

    def create(self):
        os.makedirs(self.dirname, exist_ok=True)
        self.run(["git", "init", "--initial-branch=" + self.INITIAL_BRANCH, "."])

    def run(self, args, **kwargs):
        run_args = {
            **dict(cwd=self.dirname, check=True, capture_output=True,),
            **kwargs,
        }
        return subprocess.run(args, **run_args)
