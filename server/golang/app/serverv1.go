package main

import (
	"context"
	pbv1 "grpc_tutorial/proto/v1"
	"log"
)

type serverGreeter struct {
	pbv1.UnimplementedGreeterServer
}

type serverDataStore struct {
	pbv1.UnimplementedDataStoreServer
}

var inMemoryMap = make(map[string]string)

// SayHello implements helloworld.GreeterServer
func (s *serverGreeter) SayHello(ctx context.Context, in *pbv1.HelloRequest) (*pbv1.HelloReply, error) {
	log.Printf("Received: %v", in.GetName())
	return &pbv1.HelloReply{Message: "Hello " + in.GetName()}, nil
}

func (s *serverDataStore) Save(ctx context.Context, in *pbv1.SaveRequest) (*pbv1.SaveReply, error) {
	log.Printf("Received: %v", in.GetKey())
	inMemoryMap[in.GetKey()] = in.GetValue()
	return &pbv1.SaveReply{Key: in.GetKey(), Value: in.GetValue()}, nil
}

func (s *serverDataStore) Load(ctx context.Context, in *pbv1.LoadRequest) (*pbv1.LoadReply, error) {
	log.Printf("Received: %v %v", in.GetKey(), inMemoryMap[in.GetKey()])
	if inMemoryMap[in.GetKey()] == "" {
		return &pbv1.LoadReply{Value: "Not found"}, nil
	}
	return &pbv1.LoadReply{Value: inMemoryMap[in.GetKey()]}, nil
}
