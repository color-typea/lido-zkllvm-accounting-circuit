PROJECT_DIR:=.
PROJECT_NAME:=circuit
BUILD_DIR:=${PROJECT_DIR}/build
DOCKER_CONTAINER:=zkllvm
DOCKER_IMAGE_NAME:=zkllvm-dev
SCRIPTS_VIRTUALENV_NAME:=${PROJECT_NAME}
SCRIPTS_VIRTUALENV_LOCATION:=~/.virtualenvs/${SCRIPTS_VIRTUALENV_NAME}
SCRIPTS_DEPENDENCIES_FILE:=${PROJECT_DIR}/scripts/requirements.txt

PROOF_MARKET_TOOLCHAIN=/proof-market-toolchain
SRC_DIR=${PROJECT_DIR}/src
OUTPUT_DIR=${PROJECT_DIR}/output
PUBLIC_INPUT=${SRC_DIR}/${PROJECT_NAME}.inp
COMPILED_CIRCUIT=${BUILD_DIR}/src/${PROJECT_NAME}.bc
CRCT_FILE=${OUTPUT_DIR}/${PROJECT_NAME}.crct
ASSIGNMENT_TABLE_FILE=${OUTPUT_DIR}/${PROJECT_NAME}.tbl
STATEMENT_DESC_FILE=${OUTPUT_DIR}/${PROJECT_NAME}.json
PROOF_BINARY=${OUTPUT_DIR}/${PROJECT_NAME}_proof.bin

docker-build:
	docker build -t ${DOCKER_IMAGE_NAME} .

docker-run-first:
	docker run \
		--name ${DOCKER_CONTAINER} \
		--platform=linux/amd64 \
		-it -v $(CURDIR):/opt/circuit \
		-w /opt/circuit \
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

circuit-build:
	cmake --build ${BUILD_DIR} --target circuit

circuit-assign: circuit-build
	assigner -b ${COMPILED_CIRCUIT} -i ${SPUBLIC_INPUT} -t ${ASSIGNMENT_TABLE_FILE} -c ${CRCT_FILE} -e pallas

circuit-transpile: circuit-assign
	transpiler -m gen-test-proof -i ${PUBLIC_INPUT} -t ${ASSIGNMENT_TABLE_FILE} -c ${CRCT_FILE} -o ${OUTPUT_DIR}/gates --optimize-gates

proof-statement: circuit-assign
	python3 ${PROOF_MARKET_TOOLCHAIN}/scripts/prepare_statement.py -c ${CRCT_FILE} -o ${STATEMENT_DESC_FILE} -n ${PROJECT_NAME} -t placeholder-zkllvm

proof-create: proof-statement
	${PROOF_MARKET_TOOLCHAIN}/bin/proof-generator/proof-generator --proof_out=${PROOF_BINARY} --circuit_input=${STATEMENT_DESC_FILE} --public_input=${SRC_DIR}/${PROJECT_NAME}.inp

verify-proof: gen-proof
	echo "TBD verify"

tests-build:
	cmake -DBUILD_PROJECT_TESTS=TRUE -DBUILD_TESTS=FALSE -S . -B ${BUILD_DIR}
	cmake --build ${BUILD_DIR} --target tests

tests-run: tests-build
	CTEST_OUTPUT_ON_FAILURE=1 cmake --build ${BUILD_DIR} --target check

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

