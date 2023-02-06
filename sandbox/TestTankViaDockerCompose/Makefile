run-task:
	~/arcadia/ya make
	./test-tank-via-docker-compose run --type TEST_TANK_VIA_DOCKER_COMPOSE --enable-taskbox --token ~/.sandbox_token

clean-tests-artifacts:
	find data -name logs -type d | xargs rm -rf
	find data -name bin -type d | xargs rm -rf
	find data -name run -type d | xargs rm -rf
	find data -name *.log -type f -delete

upload-tests: clean-tests-artifacts
	~/arcadia/ya upload data
	
prepare-for-local:
	find data -type d -maxdepth 1 -mindepth 1 | xargs -I{} bash -c 'mkdir -p {}/run'

restart: prepare-for-local
	docker-compose down
	docker-compose up -d --force-recreate

test-pandora-inline:
	docker-compose exec tank tankapi-cmd -t localhost -c /data/pandora_inline/config.yaml

test-pandora-uripost:
	docker-compose exec tank tankapi-cmd -t localhost -c /data/pandora_uripost/config.yaml
