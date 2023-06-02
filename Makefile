PROJECT_DIR:=.
PROJECT_NAME:=crypto3_lido_accounting_circuit
BUILD_DIR:=${PROJECT_DIR}/build
DOCKER_CONTAINER:=zkllvm
DOCKER_IMAGE_NAME:=zkllvm-dev
SCRIPTS_VIRTUALENV_NAME:=${PROJECT_NAME}
SCRIPTS_VIRTUALENV_LOCATION:=~/.virtualenvs/${SCRIPTS_VIRTUALENV_NAME}
SCRIPTS_DEPENDENCIES_FILE:=${PROJECT_DIR}/scripts/requirements.txt

docker-build:
	docker build -t ${DOCKER_IMAGE_NAME} .

docker-run-first:
	docker run \
		--name ${DOCKER_CONTAINER} \
		--platform=linux/amd64 \
		-it -v $(CURDIR):/opt/$(shell basename $(CURDIR)) \
		-w /opt/$(shell basename $(CURDIR)) \
		${DOCKER_IMAGE_NAME}:latest

docker-clean:
	docker rm --force ${DOCKER_CONTAINER}

docker-run: docker-clean docker-run-first

docker-continue:
	docker container start -i ${DOCKER_CONTAINER}

git-modules-init:
	git submodule update --init --recursive

git-modules-update:
	git pull --recurse-submodules

git-modules-to-master:
	git submodule foreach --recursive git checkout master

git-modules-reset: git-modules-init git-modules-update git-modules-to-master

git-nuke-modules:
	rm -rf .git/modules && rm -rf libs/crypto3 && rm -rf cmake/modules
	$(MAKE) git-modules-reset

cmake-clean:
	rm -rf ${BUILD_DIR}

cmake-gen:
	cmake -S . -B ${BUILD_DIR}

cmake-regen: cmake-clean cmake-gen

bld:
	cmake --build ${BUILD_DIR} --target ${PROJECT_NAME}

assign: bld
	assigner -b ${BUILD_DIR}/src/${PROJECT_NAME}.bc -i ${PROJECT_DIR}/src/${PROJECT_NAME}.inp -t ${BUILD_DIR}/${PROJECT_NAME}.tbl -c ${BUILD_DIR}/${PROJECT_NAME}.crct -e pallas

tests-build:
	cmake -DBUILD_PROJECT_TESTS=TRUE -DBUILD_TESTS=FALSE -S . -B ${BUILD_DIR}
	cmake --build ${BUILD_DIR} --target tests

tests-run: tests-build
	CTEST_OUTPUT_ON_FAILURE=1 cmake --build ${BUILD_DIR} --target test
	
gen-proof: assign
	echo "TBD proof"

verify-proof: gen-proof
	echo "TBD verify"

e2e: verify-proof

scripts-create-env:
	virtualenv -p python3.11 ${SCRIPTS_VIRTUALENV_LOCATION}

scripts-activate-env:
	. ${SCRIPTS_VIRTUALENV_LOCATION}/bin/activate

scripts-destroy-env: 
	rm -rf ${SCRIPTS_VIRTUALENV_LOCATION}

scripts-install-deps: scripts-activate-env
	pip install -r ${SCRIPTS_DEPENDENCIES_FILE}

scripts-save-deps: scripts-activate-env
	pip freeze > ${SCRIPTS_DEPENDENCIES_FILE}

scripts-recreate-env: scripts-destroy-env scripts-create-env scripts-install-deps

run-script: scripts-activate-env
	python -m $@

