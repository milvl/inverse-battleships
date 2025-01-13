# use sh for commands on Unix; on Windows, make uses cmd.exe.
SHELL := /bin/sh

# pseudo-targets that don't produce actual files.
.PHONY: all cleanup server client venv

PYTHON_VENV_PATH := venv

# to handle Windows vs. Unix activation
ifeq ($(OS),Windows_NT)
    ACTIVATE = venv\Scripts\activate
	SERVER_EXE = server.exe
	CLIENT_EXE = client.exe
else
    ACTIVATE = venv/bin/activate
	SERVER_EXE = server
	CLIENT_EXE = client
endif

all: server client

server:
	@echo "=== Building Go server ==="
	go build -o ..server/bin/$(SERVER_EXE) server/src/main.go

	# for cross-compile example for Windows:
	# cd server/src && env GOOS=windows GOARCH=amd64 go build -o ../bin/server.exe main.go


client: venv
	@echo "=== Building Python client ==="
	# Activate the venv and build with PyInstaller
	. $(ACTIVATE) && pyinstaller --onefile --name $(CLIENT_EXE) client/src/main.py --distpath client/bin

venv:
	@echo "=== Setting up Python virtual environment ==="
	test -d $(PYTHON_VENV_PATH) || python -m venv $(PYTHON_VENV_PATH)
	. $(ACTIVATE) && pip install --upgrade pip
	. $(ACTIVATE) && pip install -r requirements.txt


cleanup:
	@echo "=== Cleaning up build artifacts ==="
	# Remove PyInstaller build folders and .spec file
	rm -rf build dist *.spec

	# Remove the server binary folder (if desired)
	rm -rf server/bin

	# Optionally remove the entire virtual environment
	rm -rf $(PYTHON_VENV_PATH)
