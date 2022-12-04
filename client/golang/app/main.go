package main

import (
	"context"
	"fmt"
	"log"
	"time"

	pb "grpc_tutorial/proto/greetings"

	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

var (
	host       = getEnv("SERVER_HOST", "localhost")
	port       = getEnv("SERVER_PORT", "50050")
	addr       = fmt.Sprintf("%s:%s", host, port)
	name       = getEnv("NAME", "world")
	grpcClient *grpc.ClientConn
)

func main() {
	var err error
	// Set up a connection to the server.
	grpcClient, err = grpc.Dial(addr, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		log.Fatalf("did not connect: %v", err)
	}
	defer grpcClient.Close()
	c := pb.NewGreeterClient(grpcClient)

	// Contact the server and print out its response.
	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	defer cancel()
	r, err := c.SayHello(ctx, &pb.HelloRequest{Name: name})
	if err != nil {
		log.Fatalf("could not greet: %v", err)
	}
	log.Printf("Greeting: %s", r.GetMessage())
}
