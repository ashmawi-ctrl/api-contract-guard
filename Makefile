.PHONY: install lint test quality example

install:
	python -m pip install -e ".[dev]"

lint:
	ruff check .

test:
	pytest

quality: lint test

example:
	api-contract-guard examples/baseline.json examples/candidate.json
