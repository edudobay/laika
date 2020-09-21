export VENV_BINDIR := $(shell dirname $(shell poetry run which python))
export PATH := $(VENV_BINDIR):$(PATH)

FORMAT_DIRS = \
	simple_git_deploy \
	features \
	tests \
	testing_helpers

.PHONY: all \
	setup setup-venv setup-hooks \
	pre-commit \
	format type-check \
	test test_unit test_bdd

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
	mypy simple_git_deploy

test: test_unit test_bdd

test_unit:
	pytest

test_bdd:
	behave
