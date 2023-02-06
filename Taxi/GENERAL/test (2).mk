# Тесты

APP_VERSION_FRONT ?= $(shell bash\
  scripts/ci/get_version.sh modules/wms-front \
)
APP_VERSION_PICKER_UI ?= $(shell $(MAKE) -s -C ../wms-picker version)

TEST_ENV_CI ?= ci-back
DC = docker-compose \
	-p $(PROJECT) \
	--file dockers/compose/docker-compose.db.yml \
	--file dockers/compose/docker-compose.${TEST_ENV_CI}.yml
DC_EXEC = $(DC) exec -T
DC_OPT_BUILD ?= --build  # to set it empty for the local in .envrc

# - parallel tests
# - launched at the lavka repo
test-parallel-back:
	make test-teamcity
test-parallel-front:
	make test-fe-teamcity
test-parallel-picker:
	make test-picker-teamcity

# - parallel cleanups
# - launched at the lavka repo
cleanup-parallel-back:: test-teamcity-cleanup
cleanup-parallel-front:: test-fe-teamcity-cleanup
cleanup-parallel-picker:: test-picker-teamcity-cleanup

.SILENT:
_wrapped_test_cmd: ST=$(SKIP_TESTS)
_wrapped_test_cmd:
	@bash -c '\
		if [[ -z "$(ST)" || "$(ST)" == "0" || "$(ST)" == "false" ]]; then \
			$(CMD); \
		fi; \
	'

# <----- TeamCity section ---
test-teamcity:
	$(MAKE) _wrapped_test_cmd CMD="make run-docker-back"

# - test frontend (WMS UI)
# - launched at the lavka and lavka-fe repos
test-fe-teamcity:
	$(MAKE) _wrapped_test_cmd CMD="make run-docker-front"

# - test picker (Polka)
# - launched at the lavka and the wms-picker repos
test-picker-teamcity:
	$(MAKE) _wrapped_test_cmd CMD="make run-docker-picker"

# --

test-teamcity-cleanup:
	$(MAKE) _wrapped_test_cmd CMD="make run-docker-ci-cleanup-back"

test-fe-teamcity-cleanup:
	$(MAKE) _wrapped_test_cmd CMD="make run-docker-ci-cleanup-front"

test-picker-teamcity-cleanup:
	$(MAKE) _wrapped_test_cmd CMD="make run-docker-ci-cleanup-picker"
# ----- TeamCity section ----->

# <----- Runs section ---

# Bash strict mode. See mk/README.md for details
.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS = -ec
IFS = $$'\n\t'
run-docker-back:
	$(info Run full tests set with docker)
	APP_VERSION_FRONT=${APP_VERSION_FRONT} \
	APP_VERSION_PICKER_UI=${APP_VERSION_PICKER_UI} \
	$(DC) up $(DC_OPT_BUILD) --force-recreate -d back
	$(DC_EXEC) back make lint test-metrics
	$(DC_EXEC) back make test-back-do-ci
	$(DC_EXEC) back make test-back-run-tests

.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS = -ec
IFS = $$'\n\t'
run-docker-front:
	$(info Run full tests set with docker)
	APP_VERSION_FRONT=$(shell cd ../wms-front; bash scripts/get_version.sh) \
	REACT_APP_API_URL=http://back \
	REACT_APP_EV_URL=http://back/api/ev/ \
	REACT_APP_GOOGLE_MAPS_API_KEY=${REACT_APP_GOOGLE_MAPS_API_KEY} \
	APP_ENV=${APP_ENV:-ci} \
	$(DC) up $(DC_OPT_BUILD) --force-recreate -d back front
	$(DC_EXEC) back make test-back-do-ci
	$(DC_EXEC) back make test-back-start-serv
	$(DC_EXEC) front make test-front-start-serv
	$(DC_EXEC) front make test-cypress-run-ci

.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS = -ec
IFS = $$'\n\t'
run-docker-picker:
	$(info Run full tests set with docker)
	APP_VERSION_PICKER_UI=$(shell $(MAKE) -s -C ../wms-picker version)
	REACT_APP_GOOGLE_MAPS_API_KEY=${REACT_APP_GOOGLE_MAPS_API_KEY} \
	$(DC) up $(DC_OPT_BUILD) --force-recreate -d back picker
	$(DC_EXEC) back make test-back-do-ci
	$(DC_EXEC) back make test-back-start-serv
	$(DC_EXEC) picker make test-picker-start-serv
	$(DC_EXEC) picker make test-cypress-run

# --

run-docker-ci-cleanup-back:
	$(info Cleanup, dump logs and artifacts after tests)
	make test-all-dockers-dump \
		test-back-dump-logs \
		test-docker-down

run-docker-ci-cleanup-front:
	$(info Cleanup, dump logs and artifacts after tests)
	make test-all-dockers-dump \
		test-back-dump-logs \
		test-front-dump-logs \
		test-docker-down

run-docker-ci-cleanup-picker:
	$(info Cleanup, dump logs and artifacts after tests)
	make test-all-dockers-dump \
		test-back-dump-logs \
		test-picker-dump-logs \
		test-docker-down

# ----- Runs section --->

start_environment:
	$(info DEPRECATED use "make cook_back" instead)
	$(MAKE) cook-back-local

start_light_environment:
	$(info DEPRECATED use "make warm_back" instead)
	$(MAKE) cook-back-local

start_selenium:
	$(info DEPRECATED use "make run_front_docker" instead)
	$(MAKE) cook-back-local

stop_environment:
	$(info DEPRECATED use "make down" instead)
	$(MAKE) down-docker

stop_selenium:
	$(info DEPRECATED use "make down_docker" instead)
	$(MAKE) down-docker

# -- test lavka at docker container
test-back-do-ci:: \
	test-show-env test-show-ls \
	test-clickhouse-wait test-sql-wait \
	test-sql-upgrade

test-back-do-ci-simple:: \
	test-show-env test-show-ls \
	test-sql-wait test-sql-upgrade

test-back-start-serv:
	supervisord --loglevel=error &

# -- prepare DB
test-sql-wait:: sql_main_wait sql_printer_wait sql_analytics_wait sql_tlibstall_wait
test-sql-upgrade:: sql_main_upgrade sql_printer_upgrade sql_analytics_upgrade sql_tlibstall_upgrade

# --- test wait for clickhouse to start
test-clickhouse-wait:
	for i in `seq 1 60`; do \
		echo "Ожидаем поднятие кликхауса $$i сек ..."; \
		ping -c 1 ${CLICKHOUSE_DOMAIN} &> /dev/null || break; \
		curl -sf ${CLICKHOUSE_URL}/ping \
			&& break || sleep 1; \
	done
	ping -c 1 ${CLICKHOUSE_DOMAIN} &> /dev/null || echo "Кликхаус НЕ поднялся";
	curl -sf ${CLICKHOUSE_URL}/ping > /dev/null && echo "Кликхаус поднялся"

# --- test backend on prepared env
test-back-run-tests:
	bash scripts/pytest-parallel

# -- test libstall at local env
test-lib:
	$(info Запуск тестов lib)
	make test -C modules/libstall PYLINTRC=../../.pylintrc

ARTS_SP_DIR := $(ARTS_DIR)/supervisor

# <----
test-all-dockers-dump:
	$(DC) logs &> $(ARTS_DIR)/all_dockers.log

test-back-dump-logs:
	docker cp wmsback_back:/var/log/yandex $(ARTS_DIR)/wmsback_back_supervisor
	docker cp wmsback_clickhouse:/var/log/clickhouse-server $(ARTS_DIR)/clickhouse

test-front-dump-logs:
	docker cp wmsback_front:/var/log/nginx $(ARTS_DIR)/front_nginx
	docker cp wmsback_front:/var/log/yandex $(ARTS_DIR)/front_supervisor
	docker cp wmsback_front:/app/cypress/videos $(ARTS_DIR)/front_cypress_videos

test-picker-dump-logs:
	docker cp wmsback_picker:/var/log/nginx $(ARTS_DIR)/wmsback_picker_nginx
	docker cp wmsback_picker:/var/log/yandex $(ARTS_SP_DIR)/wmsback_picker_supervisor
	docker cp wmsback_picker:/app/cypress/videos $(ARTS_DIR)/wmsback_picker_cypress_videos
# ---->

test-docker-down:
	$(DC) down --remove-orphans
