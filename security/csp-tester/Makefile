.PHONY: all build push

all: build push

VERSION := $(shell date +%Y-%m-%dT%H.%M)

build:
	docker build -t product-security/csp-tester .

push:
	docker tag product-security/csp-tester "registry.yandex.net/product-security/csp-tester:${VERSION}"
	docker push "registry.yandex.net/product-security/csp-tester:${VERSION}"
	@echo
	@echo "Well done!"
	@echo "Uploaded: registry.yandex.net/product-security/csp-tester:$(VERSION)"
