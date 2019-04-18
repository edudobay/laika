# simple-git-deploy

<a href="https://github.com/edudobay/simple-git-deploy/tags" alt="Tags">
  <img src="https://img.shields.io/github/tag/edudobay/simple-git-deploy.svg" alt="Latest tag" /></a>

Script for managing deployments from Git repositories.


## Usage

After installing the application, run `simple-git-deploy --help` for help.


## Installation

```
$ pip install git+https://github.com/edudobay/simple-git-deploy.git
```


## Development setup

* Create a Python virtual environment (Python ≥ 3.6)
    ```
    $ python3 -m venv venv
    ```
* Activate it, then install dependencies
    ```
    $ source venv/bin/activate
    (venv)$ pip install -e . -r requirements.txt -r requirements-dev.txt
    ```

[pip-tools](https://github.com/jazzband/pip-tools) is used for managing dependencies. See more info there and in [A successful pip-tools workflow for managing Python package requirements](https://jamescooke.info/a-successful-pip-tools-workflow-for-managing-python-package-requirements.html).
