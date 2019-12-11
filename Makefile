export VENV_BINDIR := $(shell dirname $(shell poetry run which python))
export PATH := $(VENV_BINDIR):$(PATH)

FORMAT_DIRS = \
	simple_git_deploy \
	features \
	tests \
	testing_helpers

.PHONY: setup format test test_unit test_bdd

all:

setup:
	poetry install

format:
	black $(FORMAT_DIRS)

test: test_unit test_bdd

test_unit:
	pytest

test_bdd:
	behave
