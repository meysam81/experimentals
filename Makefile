PROTOS := $(shell find proto -name '*.proto')
PWD := $(shell pwd)
PYTHONPATH_SERVER := $(PWD)/server/python/:$(PWD)/server/python/proto_files
PYTHONPATH_CLIENT := $(PWD)/client/python/:$(PWD)/client/python/proto_files

protoc-go:
	protoc \
		--go_out=./server/golang/proto \
		--go_out=./client/golang/proto \
		--go-grpc_out=./server/golang/proto \
		--go-grpc_out=./client/golang/proto \
		$(PROTOS)

protoc-python:
	python -m grpc_tools.protoc \
		--proto_path=./proto \
		--python_out=./server/python/proto_files \
		--pyi_out=./server/python/proto_files \
		--grpc_python_out=./server/python/proto_files \
		--python_out=./client/python/proto_files \
		--pyi_out=./client/python/proto_files \
		--grpc_python_out=./client/python/proto_files \
		$(PROTOS)

build-golang-client:
	cd ./client/golang && go build -o client.out ./app/

build-golang-server:
	cd ./server/golang && go build -o server.out ./app/

build-golang: build-golang-client build-golang-server

run-supervisor: build-golang
	supervisord -c ./supervisord/supervisord.conf

reload-supervisord: build-golang
	supervisorctl -c ./supervisord/supervisord.conf reload

run-server-python: export PYTHONPATH = $(PYTHONPATH_SERVER)
run-server-python:
	watchmedo auto-restart -d $(PWD) -p "*.py" -R -- python ./server/python/main.py

run-server-golang: build-golang-server
	./server/golang/server.out

run-client-python: export PYTHONPATH = $(PYTHONPATH_CLIENT)
run-client-python:
	python ./client/python/main.py

run-client-golang: build-golang-client
	./client/golang/client.out

install-requirements-python-client:
	pip install -r ./client/python/requirements.txt

install-requirements-python-server:
	pip install -r ./server/python/requirements.txt

install-requirements-python: install-requirements-python-server install-requirements-python-client

install-requirements-golang-client:
	cd ./client/golang && go mod tidy

install-requirements-golang-server:
	cd ./server/golang && go mod tidy

install-requirements-golang: install-requirements-golang-server install-requirements-golang-client

lint-python:
	pre-commit run -a

lint-golang-client:
	cd ./client/golang && golangci-lint run

lint-golang-server:
	cd ./server/golang && golangci-lint run

lint-golang: lint-golang-client lint-golang-server
