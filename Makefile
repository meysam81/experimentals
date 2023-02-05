PROTOS := $(shell find ./protobuf/proto -name '*.proto')
PWD := $(shell pwd)

protoc-go:
	for proto in $(PROTOS); do \
		protoc \
			--go_out=./protobuf/server/golang/proto \
			--go_out=./protobuf/client/golang/proto \
			--go-grpc_out=./protobuf/server/golang/proto \
			--go-grpc_out=./protobuf/client/golang/proto \
			$$proto; \
	done

protoc-python:
	python -m grpc_tools.protoc \
		--proto_path=./protobuf/proto \
		--python_out=./protobuf/server/python/proto_files \
		--pyi_out=./protobuf/server/python/proto_files \
		--grpc_python_out=./protobuf/server/python/proto_files \
		--python_out=./protobuf/client/python/proto_files \
		--pyi_out=./protobuf/client/python/proto_files \
		--grpc_python_out=./protobuf/client/python/proto_files \
		$(PROTOS)

build-golang-client:
	cd ./protobuf/client/golang && go build -o client.out ./app/

build-golang-server:
	cd ./protobuf/server/golang && go build -o server.out ./app/

build-golang: build-golang-client build-golang-server

run-supervisor:
	supervisord -c ./supervisord/supervisord.conf

update-supervisord:
	supervisorctl -c ./supervisord/supervisord.conf update

reload-supervisord:
	supervisorctl -c ./supervisord/supervisord.conf reload

install-requirements-python-client:
	pip install -r ./protobuf/client/python/requirements.txt

install-requirements-python-server:
	pip install -r ./protobuf/server/python/requirements.txt

install-requirements-python: install-requirements-python-server install-requirements-python-client

install-requirements-golang-client:
	cd ./protobuf/client/golang && go mod tidy

install-requirements-golang-server:
	cd ./protobuf/server/golang && go mod tidy

install-requirements-golang: install-requirements-golang-server install-requirements-golang-client

lint-python:
	pre-commit run -a

lint-golang-client:
	cd ./protobuf/client/golang && golangci-lint run

lint-golang-server:
	cd ./protobuf/server/golang && golangci-lint run

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
	grpcurl -proto ./protobuf/proto/v1/greetings.proto -plaintext -d '{"name": "world"}' localhost:50050 greetings.Greeter/SayHello

grpcurl-datastore:
	grpcurl -proto ./protobuf/proto/v1/data_store.proto -plaintext -d '{"key": "hello", "value": "world"}' localhost:50050 data_store.DataStore/Save
	grpcurl -proto ./protobuf/proto/v1/data_store.proto -plaintext -d '{"key": "hello"}' localhost:50050 data_store.DataStore/Load

protoc: protoc-go protoc-python

add-etcd-ip-addrs:
	sudo ip a add 172.16.0.10/24 dev lo || true
	sudo ip a add 172.16.0.20/24 dev lo || true
	sudo ip a add 172.16.0.30/24 dev lo	|| true

reload-prometheus:
	curl -X POST http://localhost:9090/-/reload

create-grafana-api-token-file: apikey := promlens
create-grafana-api-token-file:
	$(eval token := $(shell curl -s -X POST -H "Content-Type: application/json" -d '{"name":"$(apikey)", "role": "Admin"}' \
		http://admin:admin@localhost:3000/api/auth/keys | jq -er .key))
	test "$(token)" != "null" && echo "$(token)" | tee ./prometheus/grafana-api-token-file.txt || true

promtool-check:
	promtool check config ./prometheus/prometheus.yml

amtool-check:
	amtool check-config ./prometheus/alertmanager.yml

promrule-test:
	promtool test rules ./prometheus/rules/tests/*

cert-ca:
	step certificate create root-ca ./prometheus/certs/ca.crt ./prometheus/certs/ca.key --insecure --no-password --profile root-ca --san localhost
	step certificate create intermediate-ca ./prometheus/certs/intermediate.crt ./prometheus/certs/intermediate.key --insecure --no-password --profile intermediate-ca --san localhost --ca ./prometheus/certs/ca.crt --ca-key ./prometheus/certs/ca.key

cert-prometheus:
	step certificate create prometheus ./prometheus/certs/prometheus.crt ./prometheus/certs/prometheus.key --san localhost --insecure --no-password --ca ./prometheus/certs/intermediate.crt --ca-key ./prometheus/certs/intermediate.key --bundle

cert-prom-client:
	step certificate create prom-client ./prometheus/certs/prom-client.crt ./prometheus/certs/prom-client.key --insecure --no-password --ca ./prometheus/certs/intermediate.crt --ca-key ./prometheus/certs/intermediate.key --bundle
	step certificate p12 ./prometheus/certs/prom-client.p12 ./prometheus/certs/prom-client.crt ./prometheus/certs/prom-client.key --ca ./prometheus/certs/intermediate.crt --no-password --insecure

certs: cert-ca cert-prometheus cert-prom-client
