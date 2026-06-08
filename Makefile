.PHONY: format lint check test all

format:
	ruff format .

lint:
	ruff check .

check:
	ruff format --check . && ruff check .

test:
	python3 -m pytest tests/ -v

all: check test
