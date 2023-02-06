# Общие для всех рецепты тестировани

TARGET_BRANCH = 'develop'


test-show-env: test-show-cfg
	$(info Окружение:)
	@date					|| true
	@env | grep LC_ 		|| true
	@env | grep PYTHON 		|| true
	@env | grep HOSTNAME 	|| true
	@env | grep CONFIGNAME 	|| true
	python3 -V

test-show-cfg:
	$(info Итоговый конфиг:)
	python3 libstall/config.py -D

test-show-ls:
	$(info Файлы проекта:)
	ls -al

test-pytest:
	$(info Тестирование:)
	pytest --verbose --color=auto --tb=native ${SRC}/tests

test-pytest-ci:
	$(info Тестирование в CI:)
	pytest --verbose --capture=no --tb=native --color=auto \
		--teamcity \
		--aiohttp-fast \
		${SRC}/tests

lint:
	$(info Статический анализ кода:)
	find . -type f -name '*.py' \
	| grep -vE '/modules/' \
	| grep -vE '/\.' \
	| xargs pylint -f text \
	    --jobs=${CPUs} \
	    --msg-template=$(PYLINT_MSG_TEMPLATE) \
	    --output-format=teamcity.pylint_reporter.TeamCityReporter \
	    --
test-linters:
	$(info DEPRECATED. Use "make lint" instead)
	$(MAKE) lint

lint-staged:
	$(info Lint staged changes:)
	@python scripts/ci/lint_precommit.py --mode=staged

lint-changed:
	$(info Lint staged, working tree and untracked changes:)
	@python scripts/ci/lint_precommit.py --mode=changed
test-linters-commit:
	$(info DEPRECATED. Use "make lint-changed" instead)
	$(MAKE) lint-changed

test-linters-branch:
	$(info Статический анализ кода текущей ветки:)
	{ git diff --name-only --ignore-submodules --diff-filter=d $(TARGET_BRANCH)...@ && \
      git diff --name-only --ignore-submodules --diff-filter=d @; } \
	| sort \
	| uniq \
 	| grep '\.py$$' \
 	| xargs pylint

test-metrics:
	$(info Метрический анализ кода:)
	@ echo "Cyclomatic Complexity:"
	radon cc --min D --no-assert --ignore ".env" --ignore "modules" ${SRC} && \
		test $$? -eq 0 && echo "ok" || echo "fail"
	@ echo "Maintainability Index:"
	radon mi --min D --ignore ".env" --ignore "modules" ${SRC} && \
		test $$? -eq 0 && echo "ok" || echo "fail"

test-secret:
	$(info Проверям код на секреты)
	ant-secret --all --validate \
		--excludes=".arc,.git,.env,.venv,.venv3,node_modules,tmp,modules"
