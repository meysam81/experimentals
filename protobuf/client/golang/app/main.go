package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"time"

	pb "grpc_tutorial/proto/greetings"

	"github.com/grpc-ecosystem/go-grpc-prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

var (
	host       = getEnv("SERVER_HOST", "localhost")
	port       = getEnv("SERVER_PORT", "50050")
	addr       = fmt.Sprintf("%s:%s", host, port)
	name       = getEnv("NAME", "world")
	infinite   = getEnv("INFINITE", "false")
	grpcClient *grpc.ClientConn
	// metrics port is 400 plus the last two digits of `port`
	metricsPort = getEnv("METRICS_PORT", "20061")
	err         error
)

func init() {
	grpcClient, err = grpc.Dial(
		addr,
		grpc.WithTransportCredentials(insecure.NewCredentials()),
		grpc.WithUnaryInterceptor(grpc_prometheus.UnaryClientInterceptor),
		grpc.WithStreamInterceptor(grpc_prometheus.StreamClientInterceptor),
	)
	if err != nil {
		log.Fatalf("Client failed to connect: %v", err)
	}
	http.Handle("/metrics", promhttp.Handler())
}

func main() {
	defer grpcClient.Close()
	go func() {
		log.Printf("Prometheus listening on %v", metricsPort)
		log.Fatal(http.ListenAndServe(fmt.Sprintf(":%s", metricsPort), nil))
	}()

	c := pb.NewGreeterClient(grpcClient)

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
