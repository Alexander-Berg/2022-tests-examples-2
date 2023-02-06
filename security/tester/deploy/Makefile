.PHONY: all build push

VERSION := $(shell date +%Y-%m-%dT%H.%M)

all: push cleanup

build:
	ya package pkg.json --docker --docker-repository=security --custom-version=$(VERSION)

push:
	ya package pkg.json --docker --docker-repository=security --custom-version=$(VERSION) --docker-push
	@echo
	@echo "Well done!"
	@echo "Uploaded: registry.yandex.net/security/skotty-tester:$(VERSION)"

cleanup:
	rm -rf packages.json
	rm -rf skotty-tester.*.tar.gz
