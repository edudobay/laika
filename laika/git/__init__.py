import re
import subprocess

from laika.core import build_command_line


class GitRevisionParseFail(RuntimeError):
    pass


def git_rev_parse_short(ref, gitdir=None):
    return git_rev_parse(ref, short=True, gitdir=gitdir)


def git_rev_parse(ref, short=False, gitdir=None):
    cmd = build_command_line(
        [
            "git",
            "rev-parse",
            "--verify",
            "--short" if short else None,
            ref + "^{commit}",
        ]
    )

    try:
        return subprocess.check_output(
            cmd, stderr=subprocess.PIPE, cwd=gitdir, encoding="utf-8"
        ).strip()
    except subprocess.CalledProcessError as e:
        if e.stderr.strip() == "fatal: Needed a single revision":
            raise GitRevisionParseFail()
        raise


def normalize_refname(refname):
    return re.sub(r"[^a-zA-Z0-9_-]", "--", refname)
