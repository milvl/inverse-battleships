SHELL := /bin/sh

.PHONY: all cleanup server client venv

PYTHON_VENV_PATH := venv
ACTIVATE := $(PYTHON_VENV_PATH)/bin/activate
SERVER_EXE := server
CLIENT_EXE := client

all: server client

server:
	@echo "=== Building Go server ==="
	cd server/src/ && go build -o ../bin/$(SERVER_EXE) main.go && cd ../..

client: venv
	@echo "=== Building Python client ==="
	. $(ACTIVATE) && pyinstaller --onefile --name $(CLIENT_EXE) client/src/main.py --distpath client/bin

venv:
	@echo "=== Setting up Python virtual environment ==="
	test -d $(PYTHON_VENV_PATH) || python -m venv $(PYTHON_VENV_PATH)
	. $(ACTIVATE) && $(PYTHON_VENV_PATH)/bin/python -m pip install --upgrade pip
	. $(ACTIVATE) && pip install -r requirements.txt

cleanup:
	@echo "=== Cleaning up build artifacts ==="
	rm -rf client/bin/*
	rm -rf build dist *.spec
	rm -rf server/bin/*
	rm -rf $(PYTHON_VENV_PATH)
