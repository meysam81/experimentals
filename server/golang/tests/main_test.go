package main

// write a test to make sure grpc server is responding correctly

import (
	"context"
	"os"
	"testing"
	"time"

	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
	pb "grpc_tutorial/proto/greetings"
)

const (
	defaultName = "world"
)

var (
	addr = "localhost:50051"
	name = defaultName
)

// get the name from os and use a default otherwise
func init() {
	if n := os.Getenv("NAME"); n != "" {
		name = n
	}
}

func TestSayHello(t *testing.T) {
	// Set up a connection to the server.
	conn, err := grpc.Dial(addr, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		t.Fatalf("did not connect: %v", err)
	}
	defer conn.Close()
	c := pb.NewGreeterClient(conn)

	// Contact the server and print out its response.
	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	defer cancel()
	r, err := c.SayHello(ctx, &pb.HelloRequest{Name: name})
	if err != nil {
		t.Fatalf("could not greet: %v", err)
	}
	t.Logf("Greeting: %s", r.GetMessage())

	// assert the response
	if r.GetMessage() != "Hello "+name {
		t.Errorf("expected: %s, got: %s", "Hello "+name, r.GetMessage())
	}
}
