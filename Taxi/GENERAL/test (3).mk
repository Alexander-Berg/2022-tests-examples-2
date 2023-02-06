BASE_URL		?= http://front
BACKEND_URL             ?= http://back
TEST_MODE               ?= normal

ARTS_DIR := dockers/compose/artifacts

# Details about APP_ENV are at [README.md#Env types]
APP_ENV ?= ci

PROJECT := wmsfront
DC = docker-compose \
	-p $(PROJECT) \
	--file dockers/docker-compose.db.yml \
	--file dockers/docker-compose.app.yml
DC_EXEC = $(DC) exec -T
DC_OPT_BUILD ?= --build  # to set it empty for the local in .envrc

ifeq ("${APP_ENV}", "production")
	SKIP_TESTS = true
endif

.SILENT:
_wrapped_test_cmd: ST=$(SKIP_TESTS)
_wrapped_test_cmd:
	@bash -c '\
		if [[ -z "$(ST)" || "$(ST)" == "0" || "$(ST)" == "false" ]]; then \
			$(CMD); \
		fi; \
	'

test-fe-teamcity:
	$(MAKE) _wrapped_test_cmd CMD="make run-tests"

ci-prepare-test-env:
	$(MAKE) _wrapped_test_cmd CMD="make run-prepare-env"

# Bash strict mode. See ../wms-backend/mk/README.md for details
.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS = -ec
IFS = $$'\n\t'
run-prepare-env:
	$(info Prepare test environment)
	docker pull registry.yandex.net/stall/base/${APP_ENV}
	docker pull registry.yandex.net/stall/frontend-base/${APP_ENV}
	APP_VERSION_FRONT=$(shell bash scripts/get_version.sh) \
	REACT_APP_API_URL=http://back \
	REACT_APP_EV_URL=http://back/api/ev/ \
	REACT_APP_GOOGLE_MAPS_API_KEY=${REACT_APP_GOOGLE_MAPS_API_KEY} \
	APP_ENV=${APP_ENV} \
	$(DC) up $(DC_OPT_BUILD) --force-recreate -d back front cypress-director
	$(DC_EXEC) back make test-back-do-ci
	$(DC_EXEC) back make test-back-start-serv
	$(DC_EXEC) front make test-front-start-serv test-front-wait-for-back test-front-wait-for-front

# Bash strict mode. See ../wms-backend/mk/README.md for details
.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS = -ec
IFS = $$'\n\t'
run-tests:
	$(info Run full tests set with docker)
	$(DC_EXEC) front make test-cypress-run-ci

test-fe-teamcity-cleanup:
	make _wrapped_test_cmd CMD="make run-docker-ci-cleanup" ST=$(SKIP_TESTS)

run-docker-ci-cleanup:
	$(info Cleanup, dump logs and artifacts after tests)
	make test-all-dockers-dump \
		test-back-dump-logs \
		test-front-dump-logs \
		test-docker-down

test-show-pahtest:
	$(info Версия тестового пакета)
	pahtest --version

test-parallel: TEST_MODE=parallel
test-parallel: test

test-parallel-dir: TEST_MODE=parallel-dir
test-parallel-dir: test

test-front-wait-for-back:
	for i in `seq 1 90`; do \
		echo "Waiting backend service to start $$i сек ..."; \
		ping -c 1 back &> /dev/null || break; \
		curl -sf ${BACKEND_URL}/ping > /dev/null \
			&& break || sleep 1; \
	done
	ping -c 1 back &> /dev/null || echo "Backend service NOT started";
	curl -sf ${BACKEND_URL}/ping > /dev/null && echo "Backend service started"
	curl -sf \
	  -H "Authorization: Token hello" \
	  -H "Content-Type: application/json" \
	  --data "[]" ${BACKEND_URL}/api/ev/push \
		&& echo '\nEvent push eats token'

test-front-wait-for-front:
	for i in `seq 1 60`; do \
		echo "Waiting frontend service to start $$i сек ..."; \
		ping -c 1 front &> /dev/null || break; \
		curl -sf ${BASE_URL}/ping > /dev/null \
			&& break || sleep 1; \
	done
	ping -c 1 front &> /dev/null || echo "Frontend service NOT started";
	curl -sf ${BASE_URL}/ping > /dev/null && echo "Frontend service started"

test-front-start-serv:
	supervisord --loglevel=error &

test-front-do-ci:: \
	test-front-wait-for-back test-front-start-serv

test-cypress-run-ci:
	Xvfb :99 & export DISPLAY=:99;
	CYPRESS_API_URL='http://cypress-director:1234/' npm run cy:patch;
	(npm run cy:ci && (pkill Xvfb || true)) || (pkill Xvfb && exit 1)

test-cypress-run-local: test-front-wait-for-back test-front-wait-for-front
	yarn cy:local

test: test-show-pahtest test-front-wait-for-front
	$(info Запуск тестов)

	export URL=${BASE_URL} \
	&& export BACKEND_URL=${BACKEND_URL} \
	&& export TIMEOUT=${TIMEOUT} \
	&& bash scripts/ci/run_tests.sh "${ARTIFACTS_DIR}" "${TEST_MODE}"

test-ci:
	$(info Запуск тестов в CI)
	make test ARTIFACTS_DIR=../../dockers/compose/artifacts

test-ci-parallel:
	$(info Запуск тестов в CI в параллель)
	make test-parallel ARTIFACTS_DIR=../../dockers/compose/artifacts

test-ci-parallel-dir:
	$(info Запуск тестов в CI в параллель по директориям)
	make test-parallel-dir ARTIFACTS_DIR=../../dockers/compose/artifacts

test-one:
	export URL=${BASE_URL} \
	&& export BACKEND_URL=${BACKEND_URL} \
	&& bash scripts/ci/run_tests.sh "${ARTIFACTS_DIR}" "${TEST_MODE}" "${TEST_FILE}"

# <----
test-all-dockers-dump:
	$(DC) logs &> $(ARTS_DIR)/all_dockers.log

test-back-dump-logs:
	docker cp wmsfront_back:/var/log/yandex $(ARTS_DIR)/wmsfront_back_supervisor

test-front-dump-logs:
	docker cp wmsfront_front:/var/log/nginx $(ARTS_DIR)/front_nginx
	docker cp wmsfront_front:/var/log/yandex $(ARTS_DIR)/front_supervisor
	docker cp wmsfront_front:/app/cypress/videos $(ARTS_DIR)/front_cypress_videos

test-docker-down:
	$(DC) down --remove-orphans
# ---->
