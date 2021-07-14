import subprocess
import tempfile
from pathlib import Path


class DirectoryContext:
    def __init__(self):
        self.tempdir = tempfile.TemporaryDirectory(prefix="pytest.laika-")

    def __enter__(self):
        return self

    def __exit__(self, *exc_details):
        self.tempdir.__exit__(*exc_details)

    @property
    def path(self) -> Path:
        return Path(self.tempdir.name)

    def run(self, cmd, **kwargs):
        return subprocess.run(cmd, cwd=self.tempdir.name, check=True, **kwargs)
