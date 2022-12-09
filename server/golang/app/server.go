package main

import (
	"context"
	pb "grpc_tutorial/proto/greetings"
	"log"
)

type serverGreeter struct {
	pb.UnimplementedGreeterServer
}

type serverDataStore struct {
	pb.UnimplementedDataStoreServer
}

var inMemoryMap = make(map[string]string)

// SayHello implements helloworld.GreeterServer
func (s *serverGreeter) SayHello(ctx context.Context, in *pb.HelloRequest) (*pb.HelloReply, error) {
	log.Printf("Received: %v", in.GetName())
	return &pb.HelloReply{Message: "Hello " + in.GetName()}, nil
}

func (s *serverDataStore) Save(ctx context.Context, in *pb.SaveRequest) (*pb.SaveReply, error) {
	log.Printf("Received: %v", in.GetKey())
	inMemoryMap[in.GetKey()] = in.GetValue()
	return &pb.SaveReply{Key: in.GetKey(), Value: in.GetValue()}, nil
}

func (s *serverDataStore) Load(ctx context.Context, in *pb.LoadRequest) (*pb.LoadReply, error) {
	log.Printf("Received: %v %v", in.GetKey(), inMemoryMap[in.GetKey()])
	if inMemoryMap[in.GetKey()] == "" {
		return &pb.LoadReply{Value: "Not found"}, nil
	}
	return &pb.LoadReply{Value: inMemoryMap[in.GetKey()]}, nil
}
