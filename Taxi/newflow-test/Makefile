FORMATTERS = black jsonfmt yamlfmt

default:

check-pep8:
	check-pep8 .

smart-check-pep8:
	check-pep8 --smart .

teamcity-check-pep8:
	check-pep8 --teamcity .


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

$(foreach fmt,$(FORMATTERS),taxi-$(fmt)): taxi-%:
	@taxi-$* -q -- .

$(foreach fmt,$(FORMATTERS),smart-taxi-$(fmt)): smart-taxi-%:
	@taxi-$* --smart -q -- .
