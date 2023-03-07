.PHONY: test
test:
	poetry run pytest $(PYTEST_PARAMS)


.PHONY: test-v
test-v:
	poetry run pytest -vv $(PYTEST_PARAMS)
