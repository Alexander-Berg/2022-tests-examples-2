DOCKER_COMPOSE_ATLAS=docker-compose -f docker-compose.yml -f atlas/docker/docker-compose.atlas.yml

.PHONY: run-init-atlas-db
run-init-atlas-db:
	$(DOCKER_COMPOSE_ATLAS) run --rm taxi-atlas-backend-router /taxi/atlas/bootstrap_db/init_db.sh

.PHONY: atlas-prepare
atlas-prepare: | tests-prepare wait-services client-mode run-init-atlas-db

.PHONY: wait-atlas-services
wait-atlas-services:
	$(DOCKER_COMPOSE_ATLAS) run --rm taxi-atlas-deps /taxi/atlas/run/wait_atlas_services.sh

.PHONY: clean-atlas-db
clean-atlas-db:
	@sudo chown -R ${USER} atlas/mongo
	git clean -fdx atlas/mongo/

.PHONY: rerun-atlas-proxy
rerun-atlas-proxy: | atlas-prepare wait-atlas-services run-atlas-proxy

.PHONY: run-atlas-proxy
run-atlas-proxy:
	$(DOCKER_COMPOSE_ATLAS) up -d taxi-atlas-proxy

.PHONY: run-atlas-all
run-atlas-all: | run-pocket-taxi init-atlas-db wait-atlas-services run-atlas-proxy
