.PHONY: clean
include .env
export

init:
	@echo "Setting up environment..."
	@../installer.sh

clean:
	@echo "Cleaning up old images"
	@docker rmi orfs-autotuner:latest

base:
	@echo "Building base image..."
	@cd ../../../ && ./build_openroad.sh

docker:
	@echo "Building docker image..."
	@export BASE_TAG=$(shell cd ../../../ && ./etc/DockerTag.sh -dev) && \
		echo "Base image tag: $$BASE_TAG" && \
		docker build -t orfs-autotuner:latest -f Dockerfile . --build-arg BASE_TAG=$$BASE_TAG && \
		docker tag orfs-autotuner:latest orfs-autotuner:$$BASE_TAG

upload:
	@echo "Uploading docker image..."
	@docker login -u $(DOCKERHUB_USERNAME) -p $(DOCKERHUB_PASSWORD)
	@export BASE_TAG=$(shell cd ../../../ && ./etc/DockerTag.sh -dev) && \
		echo "Base image: $$BASE_TAG" && \
		docker tag orfs-autotuner:latest ${DOCKERHUB_USERNAME}/orfs-autotuner:$$BASE_TAG && \
		docker push ${DOCKERHUB_USERNAME}/orfs-autotuner:$$BASE_TAG
	@docker logout

up:
	@echo "Starting Ray cluster..."
	@ray up -y public.yaml

down:
	@echo "Stopping Ray cluster..."
	@ray down -y public.yaml
