# Laika configuration file

## `[general]`

* `shell`: the shell that will be used for running commands specified by `run` settings (such as `build.run` and `post_deploy.run`).

    The shell is called with two arguments: `-c` and the command line (as a single argument).

    If not specified, the shell will default to `/bin/sh`.
