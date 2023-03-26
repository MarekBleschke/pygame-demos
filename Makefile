.PHONY: help lint lint/flake8 lint/black
.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

lint/flake8: ## check style with flake8
	poetry run flake8 .
lint/black: ## check style with black
	poetry run black --check .
lint/mypy: ## check type annotations
	poetry run mypy --strict .

lint: lint/flake8 lint/black lint/mypy ## check style

black: ## run black on sourcecode
	poetry run black .
