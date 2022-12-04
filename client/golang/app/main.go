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
	host     = getEnv("SERVER_HOST", "localhost")
	port     = getEnv("SERVER_PORT", "50050")
	addr     = fmt.Sprintf("%s:%s", host, port)
	name     = getEnv("NAME", "world")
	infinite = getEnv("INFINITE", "false")
)

func main() {
	grpcClient, err := grpc.Dial(addr, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		log.Fatalf("did not connect: %v", err)
	}
	defer grpcClient.Close()
	c := pb.NewGreeterClient(grpcClient)

	// Contact the server and print out its response.
	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	defer cancel()
	if infinite == "true" {
		for i := 1; ; i++ {
			// if deadline exceeded, reconnect to the server
			if err := ctx.Err(); err != nil {
				log.Printf("context deadline exceeded, reconnecting...: %v", err)
				ctx, cancel = context.WithTimeout(context.Background(), time.Second)
			}

			r, err := c.SayHello(ctx, &pb.HelloRequest{Name: fmt.Sprintf("%s-%d", name, i)})
			if err != nil {
				log.Printf("could not greet: %v", err)
				continue
			}
			log.Printf("Greeting: %s", r.Message)
		}

	} else {
		r, err := c.SayHello(ctx, &pb.HelloRequest{Name: name})
		if err != nil {
			log.Fatalf("could not greet: %v", err)
		}
		log.Printf("Greeting: %s", r.Message)
	}
}
