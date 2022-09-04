TEST_PARALLELISM := 0
NETWORK := default

.PHONY: build

setup-venv:
	@python -m venv venv

setup:
	@( \
		source venv/bin/activate ; \
		pip install -r requirements.txt ; \
		python -m pip install --upgrade pip \
	)

build:
	@rm -f ./build/*.teal ./build/*.json
	@mkdir -p ./build/
	@python tools/compile.py

ALLPY = tools contract tests
black:
	black $(ALLPY)

flake8:
	flake8 $(ALLPY)

MYPY = tools contract tests
mypy:
	mypy --show-error-codes $(MYPY)

lint: black flake8 mypy

integration-test: build
	@( \
		[ -z "${SANDBOX_DIR}" ] && echo "SANDBOX_DIR is not set" && exit 1 ; \
		python -m pytest -n ${TEST_PARALLELISM} -s -v tests/ \
	)

deploy: build
	 @python tools/deploy.py $(NETWORK)

undeploy:
	@( \
    		[ -z "${APP_ID}" ] && echo "APP_ID is not set" && exit 1 ; \
	 		python tools/undeploy.py $(APP_ID) $(NETWORK) \
	)
