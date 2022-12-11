PROTOS := $(shell find proto -name '*.proto')
PWD := $(shell pwd)

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

update-supervisord:
	supervisorctl -c ./supervisord/supervisord.conf update

reload-supervisord: build-golang
	supervisorctl -c ./supervisord/supervisord.conf reload

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

lint: lint-python lint-golang

run: run-supervisor

install: install-requirements-python install-requirements-golang

reload: reload-supervisord

ps:
	supervisorctl -c ./supervisord/supervisord.conf avail

restart:
	supervisorctl -c ./supervisord/supervisord.conf restart $(service)

stop:
	supervisorctl -c ./supervisord/supervisord.conf stop $(service)

start:
	supervisorctl -c ./supervisord/supervisord.conf start $(service)

up: run

down:
	supervisorctl -c ./supervisord/supervisord.conf shutdown

tail:
	supervisorctl -c ./supervisord/supervisord.conf tail $(service) $(device)

grpcurl-greetings:
	grpcurl -proto ./proto/greetings.proto -plaintext -d '{"name": "world"}' localhost:50050 greetings.Greeter/SayHello

grpcurl-datastore:
	grpcurl -proto ./proto/data_store.proto -plaintext -d '{"key": "hello", "value": "world"}' localhost:50050 data_store.DataStore/Save
	grpcurl -proto ./proto/data_store.proto -plaintext -d '{"key": "hello"}' localhost:50050 data_store.DataStore/Load

protoc: protoc-go protoc-python

add-etcd-ip-addrs:
	sudo ip a add 172.16.0.10/24 dev lo
	sudo ip a add 172.16.0.20/24 dev lo
	sudo ip a add 172.16.0.30/24 dev lo

promtool-check:
	promtool check config ./prometheus/prometheus.yml

prometheus-reload:
	curl -X POST http://localhost:9090/-/reload

create-grafana-api-token-file: apikey := promlens
create-grafana-api-token-file:
	$(eval token := $(shell curl -s -X POST -H "Content-Type: application/json" -d '{"name":"$(apikey)", "role": "Admin"}' \
		http://admin:admin@localhost:3000/api/auth/keys | jq -er .key))
	test "$(token)" != "null" && echo "$(token)" | tee ./prometheus/grafana-api-token-file.txt || true

amtool-check:
	amtool check-config ./prometheus/alertmanager.yml
