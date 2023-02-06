PYTEST      ?= taxi-pytest3
PYTEST_ARGS ?= -vvs
VIRTUALENV_PATH = $(PWD)/.venv

test: | test-deps-py3 test-virtualenv

runtests: | runtests-testsuite runtests-example

runtests-testsuite:
	PYTHONPATH=. $(PYTEST) $(PYTEST_ARGS) tests/

runtests-example:
	$(MAKE) -C example runtests

test-deps-py3:
	$(MAKE) runtests PYTEST=taxi-pytest3

test-virtualenv: setup-virtualenv
	$(MAKE) runtests PYTEST="$(VIRTUALENV_PATH)/bin/python -m pytest"

setup-virtualenv:
	test -x $(VIRTUALENV_PATH)/bin/python || \
		virtualenv --python=python3.7 $(VIRTUALENV_PATH)
	.venv/bin/pip install -i https://pypi.yandex-team.ru/simple/ \
		-r requirements-dev.txt

check-pep8:
	check-pep8 --watchers .

smart-check-pep8:
	check-pep8 --watchers --smart .

teamcity-check-pep8:
	check-pep8 --teamcity .

taxi-black:
	taxi-black .

smart-taxi-black:
	taxi-black --smart .

clean:
	rm -rf $(VIRTUALENV_PATH)
