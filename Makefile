PROJECT_DIR:=.
PROJECT_NAME:=lido_accounting_circuit
BUILD_DIR:=${PROJECT_DIR}/build
DOCKER_CONTAINER:=zkllvm
DOCKER_IMAGE_NAME:=zkllvm-dev
SCRIPTS_VIRTUALENV_NAME:=${PROJECT_NAME}
SCRIPTS_VIRTUALENV_LOCATION:=~/.virtualenvs/${SCRIPTS_VIRTUALENV_NAME}
SCRIPTS_DEPENDENCIES_FILE:=${PROJECT_DIR}/scripts/requirements.txt

INPUT_LOCATION=${PROJECT_DIR}/src/circuit.inp 
INPUT_JSON_LOCATION=${PROJECT_DIR}/src/circuit-input.json 

OUTPUT_DIR=output
COMPILED_CIRCUIT_LOCATION=${OUTPUT_DIR}/${PROJECT_NAME}.ll
TBL_LOCATION=${OUTPUT_DIR}/assignment.tbl
CRCT_LOCATION=${OUTPUT_DIR}/circuit.crct
STATEMENT_LOCATION=${OUTPUT_DIR}/statement.json
PROOF_LOCATION=${OUTPUT_DIR}/circuit.proof
GATES_OUTPUT_DIR=${OUTPUT_DIR}/gates
PROOVER_CONFIG=/root/.config/config.ini


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
	cmake -S . -B ${BUILD_DIR} -DCMAKE_BUILD_TYPE=Release -DCIRCUIT_ASSEMBLY_OUTPUT=TRUE

cmake-regen: cmake-clean cmake-gen

circuit-build: cmake-gen
	rm -rf ${OUTPUT_DIR} && mkdir ${OUTPUT_DIR}
	cmake --build ${BUILD_DIR} --target ${PROJECT_NAME}
	mv ${BUILD_DIR}/src/${PROJECT_NAME}.ll ${OUTPUT_DIR}/${PROJECT_NAME}.ll

circuit-assign: circuit-build
	assigner -b ${COMPILED_CIRCUIT_LOCATION} -i ${INPUT_LOCATION} -t ${TBL_LOCATION} -c ${CRCT_LOCATION} -e pallas

circuit-statement: circuit-assign
	python3 /opt/proof-market-toolchain/scripts/prepare_statement.py --circuit ${COMPILED_CIRCUIT_LOCATION} --name ${PROJECT_NAME} --type placeholder-zkllvm --output ${STATEMENT_LOCATION}

circuit-only-transpile:
	./transpiler -m gen-gate-argument -i ${OUTPUT_DIR} -o ${GATES_OUTPUT_DIR} -p ${INPUT_LOCATION}

circuit-transpile: circuit-assign
	rm -rf ${GATES_OUTPUT_DIR} && mkdir ${GATES_OUTPUT_DIR}
	# transpiler -m gen-gate-argument -i ${OUTPUT_DIR} -o ${GATES_OUTPUT_DIR} -p ${INPUT_LOCATION}
	transpiler -m gen-test-proof -i ${OUTPUT_DIR} -o ${GATES_OUTPUT_DIR} -p ${INPUT_LOCATION}

circuit-proof: circuit-statement
	[ -f ${PROOVER_CONFIG} ] || (mkdir -p /root/.config && cp proover_config.ini ${PROOVER_CONFIG})
	proof-generator --circuit_input=${STATEMENT_LOCATION} --public_input=${INPUT_JSON_LOCATION} --proof_out=${PROOF_LOCATION}

tests-build:
	cmake -DBUILD_PROJECT_TESTS=TRUE -DBUILD_TESTS=FALSE -S . -B ${BUILD_DIR}
	cmake --build ${BUILD_DIR} --target tests

tests-run: tests-build
	CTEST_OUTPUT_ON_FAILURE=1 cmake --build ${BUILD_DIR} --target test

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

