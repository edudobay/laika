import datetime
import os
import subprocess
from pathlib import Path

from laika.core import BuildMeta, BuildMetaFile, Build
from laika.git import git_rev_parse_short, git_rev_parse, normalize_refname
from laika.output import Reporter


def checkout_tree_for_build(
    deploy_root: Path,
    fetch_first: bool,
    git_ref: str,
    git_dir: Path,
    reporter: Reporter,
):
    if fetch_first:
        # TODO: Allow fetching from different remote or from --all
        reporter.info("Fetching from default remote")
        subprocess.run(["git", "fetch"], cwd=git_dir).check_returncode()

    hash = git_rev_parse_short(git_ref, git_dir)
    full_hash = git_rev_parse(git_ref, git_dir)
    timestamp = datetime.datetime.utcnow()

    build_id = "{timestamp:%Y%m%d%H%M%S}_{hash}_{refname}".format(
        timestamp=timestamp, hash=hash, refname=normalize_refname(git_ref),
    )

    path = deploy_root / build_id

    reporter.info(
        "Checking out git ref {git_ref} at directory {path}".format(
            git_ref=git_ref, path=path
        )
    )

    options = []
    if reporter.quiet:
        options += ["--quiet"]

    subprocess.run(
        ["git", "worktree", "add"] + options + ["--detach", str(path), git_ref],
        cwd=git_dir,
    ).check_returncode()

    meta = BuildMeta(
        source_path=os.path.realpath(git_dir),
        git_ref=git_ref,
        git_hash=full_hash,
        timestamp=timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
    )
    BuildMetaFile.write(path, meta)

    return Build(build_id, path, meta)
