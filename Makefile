PROJECT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
VENV := $(PROJECT_DIR)/.venv
PYTHON := $(VENV)/bin/python

.PHONY: test lint type clean

test:
	$(PYTHON) -m pytest $(PROJECT_DIR)/ari_test/ -v --tb=short

lint:
	$(PYTHON) -m ruff check --fix $(PROJECT_DIR)/ari/ $(PROJECT_DIR)/ari_test/
	$(PYTHON) -m ruff format $(PROJECT_DIR)/ari/ $(PROJECT_DIR)/ari_test/

type:
	$(PYTHON) -m mypy $(PROJECT_DIR)/ari/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .mypy_cache .ruff_cache .pytest_cache .coveragerc