## Development setup

* Create a Python virtual environment (Python ≥ 3.5)
    ```
    $ python3 -m venv venv
    ```
* Activate it, then install dependencies
    ```
    $ source venv/bin/activate
    (venv)$ pip install -e . -r requirements.txt -r requirements-dev.txt
    ```

[pip-tools](https://github.com/jazzband/pip-tools) is used for managing dependencies. See more info there and in [A successful pip-tools workflow for managing Python package requirements](https://jamescooke.info/a-successful-pip-tools-workflow-for-managing-python-package-requirements.html).
