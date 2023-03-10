.PHONY: init test install

init:
	python -m pip install -r requirements.txt

install:
	python -m pip install -e ./

format:
	autoflake --remove-all-unused-imports -i **/*.py
	isort **/*.py
	black **/*.py

lint: ## [Local development] Run mypy, pylint and black
	python -m mypy async_batcher
	python -m pylint async_batcher

typecheck:
	python -m mypy async_batcher tests

test:
	python -m unittest

clean:
	rm -rfv **/__pycache__ && echo
	rm -rfv **/.ipynb_checkpoints && echo
	rm -rfv **/.mypy_cache && echo
