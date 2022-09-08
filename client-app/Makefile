OWNER := fabianlee
PROJECT := docker-flask-oidc-client-app
#SHELL := /bin/bash
VERSION := 1.0.0
OPV := $(OWNER)/$(PROJECT):$(VERSION)
WEBPORT := 8080:8080
ENV_VARS := -e AUTH_PROVIDER="$(AUTH_PROVIDER)" -e AUTH_SERVER="$(AUTH_SERVER)" -e REALM="$(REALM)" -e CLIENT_ID="$(CLIENT_ID)" -e CLIENT_SECRET="$(CLIENT_SECRET)" -e SCOPE="$(SCOPE)" -e CALLBACK_ROUTE="$(CALLBACK_ROUTE)" -e CA_PEM="$(shell echo $$CA_PEM)"

# NOT using volume mount of file anymore, always passing in as env var 'CA_PEM' now
# DOCKER_VOL_MOUNT := -v $(PWD)/myCA.pem:/home/app_user/app/myCA.pem

# you may need to change to "sudo docker" if not a member of 'docker' group
DOCKERCMD := "docker"

BUILD_TIME := $(shell date -u '+%Y-%m-%d_%H:%M:%S')
# unique id from last git commit
MY_GITREF := $(shell git rev-parse --short HEAD)

run-flask: init
	python src/add_ca.py3
	python src/app.py

init:
	#[ -d flask-oidc ] || git clone https://github.com/fabianlee/flask-oidc.git;
	[ -d flask-oidc ] || git clone git@github.com:fabianlee/flask-oidc.git;
	#[ -d flask-oidc ] && { cd flask-oidc;git pull -r; }
	@echo MY_GITREF is $(MY_GITREF)

## builds docker image
docker-build: init
	@echo MY_GITREF is $(MY_GITREF)
	$(DOCKERCMD) build -f Dockerfile -t $(OPV) .

## cleans docker image
clean:
	$(DOCKERCMD) image rm $(OPV) | true

venv:
	python -m venv .

## runs container in foreground, testing a couple of override values
docker-test-fg: init
	$(DOCKERCMD) run -it --network host -p $(WEBPORT) $(ENV_VARS) --rm $(OPV)

## runs container in foreground, override entrypoint to use use shell
docker-test-cli:
	$(DOCKERCMD) run -it $(ENV_VARS) --rm --entrypoint "/bin/sh" $(OPV)

## run container in background
docker-run-bg:
	$(DOCKERCMD) run --network host -d $(ENV_VARS) -p $(WEBPORT) --rm --name $(PROJECT) $(OPV)

## get into console of container running in background
docker-cli-bg:
	$(DOCKERCMD) exec -it $(PROJECT) /bin/sh

## tails $(DOCKERCMD)logs
docker-logs:
	$(DOCKERCMD) logs -f $(PROJECT)

## stops container running in background
docker-stop:
	$(DOCKERCMD) stop $(PROJECT)

## pushes to $(DOCKERCMD)hub
docker-push:
	$(DOCKERCMD) push $(OPV)
