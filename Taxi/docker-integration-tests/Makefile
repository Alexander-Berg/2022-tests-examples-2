# for cron scripts
export PATH := /usr/lib/yandex/taxi-py3-2/bin:/usr/local/bin:$(PATH)
FORMATTERS = jsonfmt yamlfmt

ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

GROCERY_SOURCE_SERVICES ?= 'grocery-fav-goods'
GROCERY_COMPOSE_FILES=$(ROOT_DIR)/base-images.yml \
					  $(ROOT_DIR)/compose/storage.yml \
					  $(ROOT_DIR)/compose/mock-server.yml \
					  $(ROOT_DIR)/compose/taxi-infra.yml \
					  $(ROOT_DIR)/compose/networks.yml \
					  $(ROOT_DIR)/grocery/grocery.yml

# Default compose files
COMPOSE_FILES=$(ROOT_DIR)/docker-compose.yml
COMPOSE_FILES_LIST=$(foreach f, $(COMPOSE_FILES), -f $(f))

.PHONY: check-pep8
check-pep8:
	@check-pep8 -- .

.PHONY: smart-check-pep8
smart-check-pep8:
	@check-pep8 --smart -- .

.PHONY: teamcity-check-pep8
teamcity-check-pep8:
	@check-pep8 --teamcity -- .

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

# legacy
$(foreach fmt,$(FORMATTERS),taxi-$(fmt)): taxi-%:
	@taxi-$* -q -- .

$(foreach fmt,$(FORMATTERS),smart-taxi-$(fmt)): smart-taxi-%:
	@taxi-$* --smart -q -- .

.PHONY: docker-login
docker-login:
	scripts/login.sh

.PHONY: troubleshoot
troubleshoot:
	scripts/troubleshoot.sh

.PHONY: troubleshoot-pocket-taxi
troubleshoot-pocket-taxi:
	scripts/troubleshoot-pocket-taxi.sh

.PHONY: build-taxi-tests
build-taxi-tests: | pull-new-images build-backend-cpp build-uservices gen-backend-py3 tag-images

.PHONY: build-uservices
build-uservices: troubleshoot
	scripts/make_build_uservices.py

.PHONY: build-backend-cpp
build-backend-cpp: troubleshoot
	scripts/make_build_backend_cpp.py

.PHONY: gen-backend-py3
gen-backend-py3: troubleshoot
	scripts/make_gen_backend_py3.py

# from Tanker
.PHONY: update-localizations
update-localizations:
	scripts/update_localizations.py

.PHONY: init-db
init-db: | clean-db
	scripts/make_init_db.py

.PHONY: tests-prepare
tests-prepare: | troubleshoot stop pull-new-images build-taxi-tests init-db wait-services

.PHONY: wait-services
wait-services:
	scripts/make_wait_services.py

.PHONY: pull-new-images
pull-new-images: | troubleshoot pull-sandbox-resources
	IMAGE_VERSION=latest scripts/make_pull_new_images.py ${COMPOSE_FILES}

.PHONY: pull-images
pull-images:
	IMAGE_VERSION=latest docker-compose ${COMPOSE_FILES_LIST} --project-directory $(ROOT_DIR) pull --parallel --ignore-pull-failures || :

.PHONY: pull-sandbox-resources
pull-sandbox-resources:
	scripts/pull_sandbox_resources.sh

.PHONY: tag-images
tag-images: pull-new-images
	scripts/tag_images.py ${COMPOSE_FILES}

.PHONY: just-run-tests
just-run-tests:
	scripts/make_just_run_tests.py

.PHONY: run-tests
run-tests: | tests-prepare just-run-tests

.PHONY: run-no-stop
run-no-stop: | pull-new-images tag-images init-db wait-services just-run-tests

.PHONY: run-taxi-proxy
run-taxi-proxy:
	docker-compose up -d taxi-proxy

.PHONY: just-run-pocket-taxi
just-run-pocket-taxi: | client-mode run-taxi-proxy

.PHONY: run-pocket-taxi-tests
run-pocket-taxi-tests: | run-pocket-taxi just-run-pocket-taxi-tests

.PHONY: just-run-pocket-taxi-tests
just-run-pocket-taxi-tests:
	scripts/make_just_run_pocket_taxi_tests.py

# full build-run cycle for the pocket taxi
.PHONY: run-pocket-taxi
run-pocket-taxi: | troubleshoot troubleshoot-pocket-taxi stop build-taxi-tests init-db wait-services client-mode run-taxi-proxy

# partial rebuild for the pocket taxi, assuming persistent database(s)
.PHONY: rerun-pocket-taxi
rerun-pocket-taxi: | stop build-taxi-tests wait-services client-mode run-taxi-proxy

.PHONY: client-mode
client-mode:
	docker-compose run --rm taxi-bootstrap /taxi/tools/client_mode.sh

.PHONY: clean-containers
clean-containers:
	scripts/clean_containers.sh

.PHONY: clean-images
clean-images: clean-containers
	scripts/clean_images.sh

.PHONY: clean-db
clean-db:
	scripts/clean_databases.sh

.PHONY: docker-cleanup
docker-cleanup:
	scripts/docker_cleanup.sh

# If you do get: "Cannot start service taxi-client: Cannot link to a non
# running". If nothing helps, then try to clean volumes
.PHONY: clean-volumes
clean-volumes:
	scripts/clean_volumes.sh

.PHONY: prune-containers
prune-containers:
	docker container prune -f

.PHONY: stop
stop:
	scripts/make_stop.py

.PHONY: save-logs
save-logs:
	scripts/save_logs.sh

.PHONY: remove-logs
remove-logs:
	rm -rf _logs/*

.PHONY: remove-sandbox-resources
remove-sandbox-resources:
	rm -rf _sandbox/*

.PHONY: clean-repos
clean-repos:
	scripts/make_clean_repos.py


# ML load testing specific targets
.PHONY: pull-ml-images
pull-ml-images: troubleshoot
	scripts/make_pull_new_images.py --service taxi-proxy-ml

.PHONY: pull-ext-ml-images
pull-ext-ml-images: troubleshoot
	scripts/make_pull_new_images.py --service taxi-proxy-ext-ml

.PHONY: pull-pyml-images
pull-pyml-images: troubleshoot
	scripts/make_pull_new_images.py --service taxi-proxy-pyml

.PHONY: clean
clean: | stop clean-repos stop docker-cleanup clean-images remove-logs remove-sandbox-resources


# Grocery stuff
.PHONY: pull-new-grocery-images
pull-new-grocery-images: export COMPOSE_FILES=${GROCERY_COMPOSE_FILES}
pull-new-grocery-images: export COMPOSE_FILES_LIST=$(foreach f, $(COMPOSE_FILES), -f $(f))
pull-new-grocery-images: | pull-new-images

.PHONY: pull-grocery-images
pull-grocery-images: export COMPOSE_FILES=${GROCERY_COMPOSE_FILES}
pull-grocery-images: export COMPOSE_FILES_LIST=$(foreach f, $(COMPOSE_FILES), -f $(f))
pull-grocery-images: | pull-images

.PHONY: run-pocket-grocery
run-pocket-grocery: | troubleshoot troubleshoot-pocket-taxi stop build-taxi-tests init-db
	docker-compose ${COMPOSE_FILES_LIST} up -d grocery-proxy

.PHONY: build-grocery-bionic
build-grocery-bionic: export CMAKE_OPTS:=${CMAKE_OPTS} -DTARGET_SERVICES=${GROCERY_SOURCE_SERVICES}
build-grocery-bionic:
	@echo "CMAKE OPTIONS ${CMAKE_OPTS}"
	scripts/make_build_grocery.py

.PHONY: build-grocery
build-grocery: | pull-new-images build-grocery-bionic tag-images

.PHONY: prepare-grocery
prepare-grocery: export COMPOSE_FILES=${GROCERY_COMPOSE_FILES}
prepare-grocery: export COMPOSE_FILES_LIST=$(foreach f, $(COMPOSE_FILES), -f $(f))
prepare-grocery: | troubleshoot troubleshoot-pocket-taxi stop build-grocery init-db
	docker-compose ${COMPOSE_ARGS} ${COMPOSE_FILES_LIST} --project-directory $(ROOT_DIR) up -d all-grocery-services

.PHONY: run-pocket-grocery-lite
run-pocket-grocery-lite: export COMPOSE_FILES=${GROCERY_COMPOSE_FILES}
run-pocket-grocery-lite: export COMPOSE_FILES_LIST=$(foreach f, $(COMPOSE_FILES), -f $(f))
run-pocket-grocery-lite: | prepare-grocery
	docker-compose ${COMPOSE_ARGS} ${COMPOSE_FILES_LIST} --project-directory $(ROOT_DIR) up -d grocery-proxy-lite

.PHONY: just-run-grocery-tests
just-run-grocery-tests: export COMPOSE_FILES=${GROCERY_COMPOSE_FILES}
just-run-grocery-tests: export COMPOSE_FILES_LIST=$(foreach f, $(COMPOSE_FILES), -f $(f))
just-run-grocery-tests:
	docker-compose ${COMPOSE_ARGS} ${COMPOSE_FILES_LIST} --project-directory $(ROOT_DIR) run --rm grocery-tests

.PHONY: run-grocery-tests
run-grocery-tests: export COMPOSE_FILES=${GROCERY_COMPOSE_FILES}
run-grocery-tests: export COMPOSE_FILES_LIST=$(foreach f, $(COMPOSE_FILES), -f $(f))
run-grocery-tests: | prepare-grocery just-run-grocery-tests

.PHONY: save-grocery-logs
save-grocery-logs: export COMPOSE_FILES=${GROCERY_COMPOSE_FILES}
save-grocery-logs: export COMPOSE_FILES_LIST=$(foreach f, $(COMPOSE_FILES), -f $(f))
save-grocery-logs:
	grocery/scripts/save_grocery_logs.sh

# Eats stuff
.PHONY: build-eats-core
build-eats-core: | update-eats-core-db
build-eats-core:
	scripts/make_build_eats_core.py --core-path=eats-core --tag=test

.PHONY: update-eats-core-db
update-eats-core-db:
	eats/scripts/update_eats_core_db.sh

# TODO will be removed in https://st.yandex-team.ru/EDAQA-940
.PHONY: switch-to-eats
switch-to-eats:
	cp docker-compose.yml docker-compose.yml.backup
	cp eats/docker-compose.yml docker-compose.yml
	cp volumes/tools/wait_services.sh volumes/tools/wait_services.sh.backup
	cp eats/wait_services.sh volumes/tools/wait_services.sh
	cp volumes/taximeter-emulator/settings_eats.py volumes/taximeter-emulator/settings_tests.py
	./scripts/check_permissions.sh

.PHONY: run-no-stop-eats
run-no-stop-eats:
run-no-stop-eats: | switch-to-eats update-eats-core-db pull-new-images tag-images init-db wait-services just-run-tests

.PHONY: run-all-tests
run-all-tests:
	@echo "Run taxi tests"
	scripts/kill_after_run.sh make run-no-stop
	@echo "Stop taxi containers"
	make stop
	@echo "Switch to eats and run eats tests"
	scripts/kill_after_run.sh make run-no-stop-eats

-include Makefile.*.mk
