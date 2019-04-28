# simple-git-deploy

<a href="https://pypi.org/project/simple-git-deploy/" title="Available on PyPI">
  <img src="https://img.shields.io/pypi/v/simple-git-deploy.svg?style=for-the-badge" alt="Latest PyPI version"></a>

A command-line utility for easy and reliable management of manual deployments from Git repositories.

Even manual deployments can be made reliable if some minimal automation is applied. This utility performs _atomic_ deployments from a Git repository, with an optional _build_ phase (e.g. installing dependencies). The previous deployment is not affected until the build completes successfully – no more inconsistency errors when you update your Git branch but your application is not yet fully updated – e.g. missing new dependencies from your package manager.

Each deployment is built in a new directory made just for that deployment. Previous deployments are kept (and can be later purged), and the target is only updated when the build completes – that’s what we meant by _atomic_! If the build fails, the target will not be updated.

The meaning of _build_ is defined by the user; it can be any command runnable from a shell. Configuration is made in a simple `.ini` file.


## Installation

Requirements:

* Python ≥ 3.5 (has been tested with 3.6 and 3.7 but should work with 3.5 nonetheless)
* Git ≥ 2.7 (depends on the `git worktree` feature)

Install via **pip**:

```
$ pip install simple-git-deploy
```

If this fails and you have no idea what to do, you can try adding the `--user` option after `pip install`, though other options can be better in the long run – e.g. you can use [pipsi](https://github.com/mitsuhiko/pipsi/), or simply create a **virtualenv** for your installed scripts.


## Usage

After [installing this utility](#installation), you can run `simple-git-deploy --help` for basic usage instructions.

The easiest way is to run `simple-git-deploy deploy <git-branch-name>`. But before first usage you must create a `deploy.ini` file with at least the settings below (look further for an example):

* `dirs.deploy`: directory where your application will be deployed. The current deployment will be available at `current` under this directory. This will be a symlink to the actual deployment directory.

    So, for example, if you have a PHP application, you can point Nginx to the `/app/deployments/current` directory which will contain a working tree of your Git repository and will be updated whenever you deploy a new version, provided you add this to your `deploy.ini`:

    ```ini
    [dirs]
    deploy = /app/deployments
    ```

    Each deployment will also live in this directory with a name containing the date/time of the deployment, the Git commit hash and the name of the branch/tag that was deployed.

* `build.run`: which command to run in the _build_ phase. Typical usages are running your package manager, copying configuration files, compiling assets.

    This is run as a shell command line – so you can chain commands as in `npm install && npm run build`.

A complete configuration file would thus be:

```ini
[dirs]
deploy = /app/deployments

[build]
run = npm install && npm run build
```

**It is assumed that the build will be run in the same host where the application is to be deployed.** Also, the user running this script must have **permission to write on the deployment directory**.


### Purging old deployments

You can purge old deployments with `simple-git-deploy purge`. There are two ways to specify what exactly is to be removed:

* `--keep-latest N`: keep only the latest _N_ deployments (other than the current one). With _N=0_, only the current deployment is kept, and with _N=1_ only one deployment other than the current is kept.
* `--older-than DATETIME`: discard deployments with a timestamp strictly older than the given date/time. A wide range of both absolute and relative formats is accepted; see the [dateparser documentation](https://dateparser.readthedocs.io/en/latest/) for full information. Common cases may be written as `10d`, `1w` (10 days and 1 week, respectively).


## Development setup

If you want to set this project up for development, see [CONTRIBUTING.md](./CONTRIBUTING.md).
