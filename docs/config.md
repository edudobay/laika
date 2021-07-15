# Laika configuration file

## `[general]`

* `shell`: the shell that will be used for running commands specified by `run` settings (such as `build.run` and `post_deploy.run`).

    The shell is called with two arguments: `-c` and the command line (as a single argument).

    If not specified, the shell will default to `/bin/sh`.


## Available environment variables

These environment variables are available to all commands run by `laika` in the context of a build directory (such as `build.run` and `post_deploy.run`):

* `DIR_SOURCE`: the directory of the Git repository from which the project is built.
* `DIR_DEPLOY`: the directory to which the project is deployed — a new deployment directory is created for each build.
* `DEPLOY_GIT_REF`: the Git symbolic ref that was referred to when the build was created — typically a branch or tag name. See [`man gitrevisions`](https://git-scm.com/docs/gitrevisions) for more information on symbolic refs.
* `DEPLOY_GIT_HASH`: the actual Git commit from which the build was created. This is the full commit hash.
