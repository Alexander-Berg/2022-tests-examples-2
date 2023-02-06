FORMATTERS = black eolfmt jsonfmt yamlfmt

PYTHON_DEPS_DIR ?= /usr/lib/yandex/taxi-py3-2
PYTHON3_PATH = $(firstword $(wildcard $(PYTHON_DEPS_DIR)/bin/python3) python3)

# unification
.PHONY: check-pep8
check-pep8:
	@check-pep8 -- .

.PHONY: smart-check-pep8
smart-check-pep8:
	@check-pep8 --smart -- .

.PHONY: smart-format
smart-format:
ifneq ($(shell which taxi-format),)
	@taxi-format --smart -- .
else
	@echo "Formatting... (There is new version of code-linters, please install: https://github.yandex-team.ru/taxi/code-linters#установка)"
	@$(MAKE) -s $(foreach fmt,$(FORMATTERS),smart-taxi-$(fmt))
endif
