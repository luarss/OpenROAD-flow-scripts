.PHONY: test
test:
	@echo "Running unit test and coverage..."
	@coverage erase
	@coverage run -m unittest discover test/unit-tests
	@coverage report
	@coverage html -d cov_html

.PHONY: format
format:
	@black .
