isort:
	isort lib tests setup.py

black:
	black lib tests setup.py

flake8:
	flake8 lib tests

fmt: isort black

mypy:
	mypy --ignore-missing-imports lib tests

lint: flake8 mypy

test:
	PYTHONPATH="$(PYTHONPATH):$(PWD)" pytest tests

amaze: fmt test lint
