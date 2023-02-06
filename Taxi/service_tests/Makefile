.PHONY: run-tests stop-tests
run-tests:$
	docker-compose -f docker-compose.yml run --rm autotests -c pytest -vv tests

stop-tests:
	docker-compose -f docker-compose.yml down
