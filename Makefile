PYTHON ?= python3
CONFIG ?= config.json

.PHONY: install run debug clean lint lint-strict

install:
	$(PYTHON) -m pip install -r requirements.txt

run:
	$(PYTHON) pac-man.py "$(CONFIG)"

debug:
	$(PYTHON) -m pdb pac-man.py "$(CONFIG)"

clean:
	find . -type d \( -name .git -o -name .venv -o -name venv \) -prune -o -type d \( -name __pycache__ -o -name .mypy_cache -o -name .pytest_cache -o -name .ruff_cache \) -prune -exec rm -rf {} +

lint:
	$(PYTHON) -m flake8 .
		python3 -m mypy . --exclude '^mazegenerator/' --follow-imports=silent --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
