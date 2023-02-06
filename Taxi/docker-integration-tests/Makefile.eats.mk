EATS_COMPOSE_FILE=docker-compose.eats.yml

.PHONY: check-root-permissions
check-root-permissions:
	./scripts/check_root_permissions.sh

.PHONY: wait-eats-services
wait-eats-services:
	scripts/make_wait_services.py ${EATS_COMPOSE_FILE} --wait-script /taxi/eats/wait_eats_services.sh

.PHONY: pull-new-eats-images
pull-new-eats-images: COMPOSE_FILES=${EATS_COMPOSE_FILE}
pull-new-eats-images:
	IMAGE_VERSION=latest scripts/make_pull_new_images.py ${COMPOSE_FILES}

.PHONY: build-eats-tests
build-eats-services: | pull-new-eats-images build-backend-cpp build-uservices gen-backend-py3 tag-images

.PHONY: eats-tests-prepare
eats-tests-prepare: export COMPOSE_FILES=${EATS_COMPOSE_FILE}
eats-tests-prepare: export COMPOSE_FILE=${EATS_COMPOSE_FILE}
eats-tests-prepare: | troubleshoot stop-eats check-root-permissions build-eats-services init-db wait-eats-services

.PHONY: run-tests
run-eats-tests: export COMPOSE_FILES=${EATS_COMPOSE_FILE}
run-eats-tests: export COMPOSE_FILE=${EATS_COMPOSE_FILE}
run-eats-tests: | eats-tests-prepare just-run-tests

.PHONY: stop-eats
stop-eats:
	scripts/make_stop.py ${EATS_COMPOSE_FILE}
