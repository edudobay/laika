export VENV_BINDIR := $(shell dirname $(shell poetry run which python))
export PATH := $(VENV_BINDIR):$(PATH)

SRC_DIR = laika

FORMAT_DIRS = \
	$(SRC_DIR) \
	features \
	tests \
	testing_helpers

.PHONY: all \
	setup setup-venv setup-hooks \
	pre-commit \
	format type-check \
	test test_unit test_bdd \
	release release_upload

all:

setup: setup-venv setup-hooks

setup-venv:
	poetry install

setup-hooks:
	development/setup-hooks.sh

pre-commit: format-check type-check

format:
	black $(FORMAT_DIRS)

format-check:
	black --check $(FORMAT_DIRS)

type-check:
	mypy $(SRC_DIR)

test: test_unit test_bdd

test_unit:
	pytest

test_bdd:
	behave

release:
	poetry build

release_upload:
	@echo "Please run manually (editing as necessary):"
	@echo "twine upload -s dist/*"
