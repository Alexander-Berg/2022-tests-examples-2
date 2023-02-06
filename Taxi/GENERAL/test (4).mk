BASE_URL		?= http://picker
BACKEND_URL             ?= http://back

PROJECT := wmspicker
DC = docker-compose \
	-p $(PROJECT) \
	--file dockers/docker-compose.db.yml \
	--file dockers/docker-compose.app.yml
DC_EXEC = $(DC) exec -T
DC_OPT_BUILD ?= --build  # to set it empty for the local in .envrc

ifeq ("${APP_ENV}", "production")
	SKIP_TESTS = true
endif

test: test-show-pahtest
	$(info Запуск тестов)
	export URL=${BASE_URL} \
		BACKEND_URL=${BACKEND_URL} \
		SELENIUM_HUB_URL_FIREFOX=${SELENIUM_HUB_URL_FIREFOX} \
		SELENIUM_HUB_URL_CHROME=${SELENIUM_HUB_URL_CHROME} \
		TIMEOUT=${TIMEOUT} \
	&& bash scripts/ci/run_tests.sh "${ARTIFACTS_DIR}"

.SILENT:
_wrapped_test_cmd: ST=$(SKIP_TESTS)
_wrapped_test_cmd:
	bash -c '\
		if [[ -z "$(ST)" || "$(ST)" == "0" || "$(ST)" == "false" ]]; then \
			$(CMD); \
		fi; \
	'

ci-prepare-test-env:
	$(MAKE) _wrapped_test_cmd CMD="make run-prepare-env"

test-picker-teamcity:
	$(MAKE) _wrapped_test_cmd CMD="make run-tests"

# Bash strict mode. See ../wms-backend/mk/README.md for details
.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS = -ec
IFS = $$'\n\t'
run-prepare-env:
	$(info Prepare test environment)
	APP_VERSION_PICKER_UI=$(shell bash scripts/get_version.sh) \
	REACT_APP_GOOGLE_MAPS_API_KEY=${REACT_APP_GOOGLE_MAPS_API_KEY} \
	$(DC) up $(DC_OPT_BUILD) --force-recreate -d back picker
	$(DC_EXEC) back make test-back-do-ci
	$(DC_EXEC) back make test-back-start-serv
	$(DC_EXEC) picker make test-picker-start-serv test-wait-for-back test-wait-for-front

# Bash strict mode. See ../wms-backend/mk/README.md for details
.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS = -ec
IFS = $$'\n\t'
run-tests:
	$(info Run full tests set with docker)
	$(DC_EXEC) picker make test-cypress-run

test-picker-teamcity-cleanup:
	make _wrapped_test_cmd CMD="make run-docker-ci-cleanup" ST=$(SKIP_TESTS)

run-docker-ci-cleanup:
	$(info Cleanup, dump logs and artifacts after tests)
	make test-all-dockers-dump \
		test-back-dump-logs \
		test-picker-dump-logs \
		test-docker-down

test-ci:
	$(info Запуск тестов в CI)
	make test ARTIFACTS_DIR=../../dockers/compose/artifacts

test-show-pahtest:
	$(info Версия тестового пакета)
	pahtest --version

test-wait-for-back:
	for i in `seq 1 1800`; do \
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

test-wait-for-front:
	for i in `seq 1 1800`; do \
		echo "Waiting picker service to start $$i сек ..."; \
		ping -c 1 front &> /dev/null || break; \
		curl -sf ${BASE_URL}/ping > /dev/null \
			&& break || sleep 1; \
	done
	ping -c 1 front &> /dev/null || echo "Picker service NOT started";
	curl -sf ${BASE_URL}/ping > /dev/null && echo "Picker service started"

test-picker-start-serv:
	supervisord --loglevel=error &

test-cypress-run:
	$(shell npm bin)/cypress run --config-file cypress.ci.json -b chrome

# <----
test-all-dockers-dump:
	$(DC) logs &> $(ARTS_DIR)/all_dockers.log

test-back-dump-logs:
	docker cp back_ci:/var/log/yandex $(ARTS_SP_DIR)/back_ci_supervisor

test-picker-dump-logs:
	docker cp picker_ci:/var/log/nginx $(ARTS_DIR)/picker_ci_nginx
	docker cp picker_ci:/var/log/yandex $(ARTS_SP_DIR)/picker_ci_supervisor
	docker cp picker_ci:/app/cypress/videos $(ARTS_DIR)/picker_ci_cypress_videos

test-docker-down:
	$(DC) down --remove-orphans
# ---->
