# simple-git-deploy

Script for managing deployments from Git repositories.


## Usage

After setting up the application, run `./deploy.py --help` for help.


## Setup

* Create a Python virtual environment (Python ≥ 3.6)
    ```
    $ python3 -m venv venv
    ```
* Activate it, then install dependencies
    ```
    $ source venv/bin/activate
    (venv)$ pip install -r requirements.txt
    ```
* If developing, also install development dependencies
    ```
    (venv)$ pip install -r requirements-dev.txt
    ```

[pip-tools](https://github.com/jazzband/pip-tools) is used for managing dependencies. See more info there and in [A successful pip-tools workflow for managing Python package requirements](https://jamescooke.info/a-successful-pip-tools-workflow-for-managing-python-package-requirements.html).
