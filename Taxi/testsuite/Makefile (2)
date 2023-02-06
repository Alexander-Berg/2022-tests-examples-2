-include Makefile.local

DOCKER_COMPOSE ?= docker-compose
PYTEST         ?= taxi-pytest3
PYTEST_ARGS    ?= -vv
VIRTUALENV_PATH = $(CURDIR)/.venv
VENV_DOCS_PATH  = $(CURDIR)/.venv-docs
VENV_PYTHON     = $(firstword $(shell which python3.9 python3.8 python3.7 python3))

FORMATTERS = black jsonfmt yamlfmt

ifeq ($(NO_SETUP_VENV), 1)
    SETUP_VIRTUALENV_TARGET =
else
    SETUP_VIRTUALENV_TARGET = setup-virtualenv
endif

test: | test-deps-py3 test-virtualenv

runtests: | runtests-testsuite runtests-taxi runtests-example

runtests-testsuite:
	PYTHONPATH=. $(PYTEST) $(PYTEST_ARGS) tests

runtests-taxi:
	PYTHONPATH=. $(PYTEST) $(PYTEST_ARGS) tests-taxi

runtests-taxi-experiments3:
	PYTHONPATH=. $(PYTEST) $(PYTEST_ARGS) tests-taxi/mocks/test_experiments3*

runtests-example:
	$(MAKE) -C docs/examples runtests

test-deps-py3:
	$(MAKE) runtests PYTEST=taxi-pytest3

test-virtualenv: $(SETUP_VIRTUALENV_TARGET)
	$(MAKE) runtests PYTEST="$(VIRTUALENV_PATH)/bin/python -m pytest" \
		PYTEST_ARGS="$(PYTEST_ARGS)"

teamcity-test:
	$(DOCKER_COMPOSE) run --rm taxi-test

teamcity-pull-images:
	$(DOCKER_COMPOSE) pull taxi-test

setup-virtualenv:
	test -x $(VIRTUALENV_PATH)/bin/python || \
		virtualenv --python=$(VENV_PYTHON) $(VIRTUALENV_PATH)
	$(VIRTUALENV_PATH)/bin/pip install -i https://pypi.yandex-team.ru/simple/ \
		-r requirements-taxi.txt
	$(VIRTUALENV_PATH)/bin/pip install -i https://pypi.yandex-team.ru/simple/ \
		-r docs/examples/requirements.txt

check-pep8:
	check-pep8 .

smart-check-pep8:
	check-pep8 --smart .

teamcity-check-pep8:
	check-pep8 --teamcity .

.PHONY: format smart-format
format:
ifneq ($(shell which taxi-format),)
	@taxi-format -q -- .
else
	@echo "Formatting... (There is new version of code-linters, please install: https://github.yandex-team.ru/taxi/code-linters#установка)"
	@$(MAKE) -s $(foreach fmt,$(FORMATTERS),taxi-$(fmt))
endif

smart-format:
ifneq ($(shell which taxi-format),)
	@taxi-format --smart -q -- .
else
	@echo "Formatting... (There is new version of code-linters, please install: https://github.yandex-team.ru/taxi/code-linters#установка)"
	@$(MAKE) -s $(foreach fmt,$(FORMATTERS),smart-taxi-$(fmt))
endif

$(foreach fmt,$(FORMATTERS),taxi-$(fmt)): taxi-%:
	@taxi-$* -q -- .

$(foreach fmt,$(FORMATTERS),smart-taxi-$(fmt)): smart-taxi-%:
	@taxi-$* --smart -q -- .

$(VENV_DOCS_PATH)/.timestamp: setup.py setup.cfg requirements-taxi.txt \
				docs/requirements.txt
	test -x $(VENV_DOCS_PATH)/bin/python || \
		virtualenv --python=$(VENV_PYTHON) $(VENV_DOCS_PATH)
	$(VENV_DOCS_PATH)/bin/pip install -i https://pypi.yandex-team.ru/simple/ \
		-r requirements-taxi.txt
	$(VENV_DOCS_PATH)/bin/pip install -i https://pypi.yandex-team.ru/simple/ \
		-r docs/requirements.txt
	touch $@

setup-docs-venv: $(VENV_DOCS_PATH)/.timestamp

build-docs: build-docs-html

build-docs-%: setup-docs-venv
	PATH=$(VENV_DOCS_PATH)/bin:$(PATH) PYTHONPATH=$(PWD) \
		$(MAKE) -C docs $*

publish-gh-pages: build-docs-dirhtml
	[ "x$(TESTSUITE_GH_PAGES_REPO)" != "x" ] || \
		(echo "TESTSUITE_GH_PAGES_REPO must be set"; exit 1)
	git -C $(TESTSUITE_GH_PAGES_REPO) fetch origin
	git -C $(TESTSUITE_GH_PAGES_REPO) checkout gh-pages
	git -C $(TESTSUITE_GH_PAGES_REPO) reset --hard origin/gh-pages
	git -C $(TESTSUITE_GH_PAGES_REPO) clean -fxd
	cp -R docs/_build/dirhtml/* $(TESTSUITE_GH_PAGES_REPO)
	touch $(TESTSUITE_GH_PAGES_REPO)/.nojekyll
	git -C $(TESTSUITE_GH_PAGES_REPO) add $(TESTSUITE_GH_PAGES_REPO)/*
	if git -C $(TESTSUITE_GH_PAGES_REPO) commit -am 'Update docs'; then	\
	    git -C $(TESTSUITE_GH_PAGES_REPO) push origin gh-pages;		\
	fi


clean:
	rm -rf $(VIRTUALENV_PATH) $(VENV_DOCS_PATH) docs/_build
