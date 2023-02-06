# Используется в основной lavka-репе
include mk/test.mk

# Вызывается в агенте TeamCity на шаге запуска тестов.
# Трогаем .pylinrc. Это симлинк, а докер их не копирует в образ при билде
# поэтому превращаем симлинк в файл, а после билда - безопасно кладём обратно
test-libstall-teamcity:
	mv .pylintrc .pylintrc_dump && cp -L .pylintrc_dump .pylintrc
	docker-compose \
		up --force-recreate --build --abort-on-container-exit --remove-orphans app-ci

test-libstall-teamcity-cleanup:
	docker-compose \
		logs &> dockers/compose/artifacts/all_dockers.log
	docker-compose down --remove-orphans
	rm -f .pylinrc && mv .pylintrc_dump .pylintrc

# БД
test-sql-wait:: sql_test_wait_test
test-sql-upgrade:: sql_test_upgrade_test

# Запуск тестов внутри docker-compose сети
test-ci:: test-show-env test-show-ls lint test-metrics \
	test-sql-wait test-sql-upgrade test-pytest-ci

# Запуск тестов на локальной машине используя проброс портов от сервисов
test:: test-sql-wait test-sql-upgrade lint test-metrics test-pytest
