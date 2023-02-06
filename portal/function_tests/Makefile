SHELL:=/bin/bash
VENV_ROOT_DIR:=./
VENV_NAME:=venv
DEV_INSTANCE = $(shell ../tools/instance)


ifneq ($(N),)
    _N ?= -n=$(N)
endif

ifneq ($(K),)
    _K ?= -k="$(K)"
endif

ifneq ($(D),)
    _D ?= "$(D)"
endif

ifneq ($(VENV_ROOT),)
    VENV_ROOT_DIR ?= "$(VENV_ROOT)"
endif

VENV_NAME:="$(VENV_ROOT)$(VENV_NAME)"
VENV_ACTIVATE:=source ${VENV_NAME}/bin/activate

ifneq ($(MORDA_ENV),)
    _MORDA_ENV ?= --morda_env="$(MORDA_ENV)"
endif

ifneq ($(FEATURES),)
    _FEATURES ?= --allure_features="$(FEATURES)"
endif

ifneq ($(STORIES),)
    _STORIES ?= --allure_stories="$(STORIES)"
endif

ifneq ($(DNS_MORDA),)
    _DNS_MORDA ?= --dns_morda="$(DNS_MORDA)"
endif

ifneq ($(DNS_OVERRIDE),)
    _DNS_OVERRIDE ?= --dns_override="$(DNS_OVERRIDE)"
endif

ifneq ($(RETRY_COUNT),)
    _RETRY_COUNT ?= --retry_count="$(RETRY_COUNT)"
endif

default: init

t_simple:
	rm -rf allure-report allure-results; \
	$(VENV_ACTIVATE); \
	py.test $(_K) "tests/schema" --morda_env="$(DEV_INSTANCE).wdevx" -n=5 $(_FEATURES) $(_STORIES) $(_DNS_MORDA) $(_DNS_OVERRIDE)

t_stable:
	rm -rf allure-report allure-results; \
	$(VENV_ACTIVATE); \
	py.test $(_K) --morda_env="$(DEV_INSTANCE).wdevx" -n=5 --allure_features="function_tests_stable" $(_STORIES) $(_DNS_MORDA) $(_DNS_OVERRIDE)

t_api:
	rm -rf allure-report allure-results; \
	$(VENV_ACTIVATE); \
	py.test $(_K) --morda_env="$(DEV_INSTANCE).wdevx" -n=5 --allure_features="api_search_v2" $(_STORIES) $(_DNS_MORDA) $(_DNS_OVERRIDE)

kote_fix:
	sudo chmod ugo+w ./allure-results/ ./venv/ ./schema/ ./.cache/ ./tests/kote/tests/framework_test/mocks/tmp

clean:
	rm -rf venv
	rm -rf allure*

hooks: deps
	$(VENV_ACTIVATE); \
	pre-commit install; \
	pre-commit autoupdate;

schemas:
	./get_api_search_schemas.sh

update_tanker:
	./get_tanker.sh

deps: env schemas
	$(VENV_ACTIVATE); \
	pip install -r requirements.txt;

env:
	test -d $(VENV_NAME) || virtualenv $(VENV_NAME) --python=/usr/bin/python2.7;

t:
	rm -rf allure-report allure-results; \
	$(VENV_ACTIVATE); \
	py.test $(_K) $(_D) $(_MORDA_ENV) $(_N) $(_FEATURES) $(_STORIES) $(_DNS_MORDA) $(_DNS_OVERRIDE) $(_RETRY_COUNT)

tm:
	rm -rf allure-report allure-results; \
	$(VENV_ACTIVATE); \
	py.test $(_K) $(_N) $(_FEATURES) $(_STORIES) $(_DNS_MORDA) $(_DNS_OVERRIDE) --monitoring=1 -m yasm

ta:
	$(MAKE) t; \
	allure generate allure-results -o allure-report

tl:
	$(VENV_ACTIVATE); \
	py.test --collect-only $(_K) $(_FEATURES) $(_STORIES)

tar:
	$(MAKE) ta; \
	$(MAKE) report;

report:
	allure serve allure-results

up: init

init: env deps #hooks

pc:
	$(VENV_ACTIVATE); \
	pre-commit run --all-files

# Набор тестов для проверки в пулл-реквестах
# TODO запускать здесь все тесты
pull-request-check:
	$(MAKE) t FEATURES='morda,portal_set,portal_ntp,config_pp'

install.ok:
	sudo apt install -y python-virtualenv
	touch $@

init_once.ok: init
	touch $@

.PHONY: install
install: install.ok init_once.ok
