PYTEST      ?= taxi-pytest3
PYTEST_ARGS ?= -vvs

test:
	echo $(PYTEST)
	PYTHONPATH=. $(PYTEST) $(PYTEST_ARGS) tests/

check-pep8:
	check-pep8 --watchers .

smart-check-pep8:
	check-pep8 --watchers --smart .

teamcity-check-pep8:
	check-pep8 --teamcity .
