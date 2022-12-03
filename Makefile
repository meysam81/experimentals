PROTOS := $(shell find proto -name '*.proto')

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
