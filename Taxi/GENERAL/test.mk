# Тесты

test-env:
	$(info Запуск тестового окружения:)
	pg_isready -h /tmp/testsuite-postgresql/ || \
		../tests-env --services=postgresql start
	nc -zv localhost 27118 || \
		../tests-env --services=mongo start

test-pytest: test-env
	$(info Тестирование:)
	pytest --no-env --verbose --color=auto .

test-linters:
	$(info Статический анализ кода:)
	cd .. && check-pep8 -j ${CPUs} -- ${SRC}
	
test-metrics:
	$(info Метрический анализ кода:)
	@ echo "Cyclomatic Complexity:"
	@ OUTPUT=` \
		radon cc --min C --no-assert --ignore "generated" ${SRC} | \
			tee /dev/tty \
		`; [ -z "$$OUTPUT" ] && echo "ok"
	@ echo "Maintainability Index:"
	@ OUTPUT=` \
		radon mi --min C --ignore "generated" ${SRC} | \
			tee /dev/tty \
		`; [ -z "$$OUTPUT" ] && echo "ok"

test: gen test-linters test-metrics test-pytest