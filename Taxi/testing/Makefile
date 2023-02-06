.PHONY:	all all_push deploy sync build push apply_lb apply_deployment

define GetFromPkg
$(shell node -p "require('../../package.json').$(1)")
endef

PACKAGE_VERSION := $(call GetFromPkg,version)

VENDOR = cr.yandex
IMAGE_NAME = drivers-front
REGISTRY_ID = crpve1keoaktj3501nil
IMAGE_TAG = $(VENDOR)/$(REGISTRY_ID)/$(IMAGE_NAME):$(IMAGE_VERSION)
IMAGE_VERSION = $(PACKAGE_VERSION)
IMAGE_DOCKERFILE = "$(IMAGE_NAME).dockerfile"

all: sync build

all_push: all push

all_deploy: all_push deploy

sync:
	rsync --exclude=kubernetes/ \
	--exclude=.idea/ \
	--exclude=build/ \
	--exclude=node_modules/ \
	--exclude=Dockerfile \
	--exclude=.gitlab-ci.yml \
	--exclude=.gitignore \
	--exclude=yarn.lock \
	--recursive --delete \
	../../ ../build/

build:
	docker build -t $(IMAGE_TAG) -f ../$(IMAGE_DOCKERFILE) ../

push:
	docker push $(IMAGE_TAG)

apply_lb:
	kubectl apply -f ./drivers-front.lb.yaml

apply_deployment:
	kubectl apply -f ./drivers-front.deployment.yaml
	kubectl apply -f ./drivers-backoffice.deployment.yaml

deploy: apply_lb apply_deployment
