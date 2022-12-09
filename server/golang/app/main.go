package main

import (
	"fmt"
	"log"
	"net"
	"net/http"

	pb "grpc_tutorial/proto/greetings"

	"github.com/grpc-ecosystem/go-grpc-prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"google.golang.org/grpc"
)

var (
	port = getEnv("PORT", "50051")
	// metrics port is 400 plus the last two digits of `port`
	metricsPort = fmt.Sprintf("400%s", port[len(port)-2:])
	grpcServer  *grpc.Server
)

// server is used to implement helloworld.GreeterServer.

func init() {
	grpcServer = grpc.NewServer(
		grpc.StreamInterceptor(grpc_prometheus.StreamServerInterceptor),
		grpc.UnaryInterceptor(grpc_prometheus.UnaryServerInterceptor),
	)
	grpc_prometheus.Register(grpcServer)
	http.Handle("/metrics", promhttp.Handler())
}

func main() {
	log.Println("Starting server ...")
	lis, err := net.Listen("tcp4", fmt.Sprintf(":%s", port))
	if err != nil {
		log.Fatalf("Server failed to listen: %v", err)
	}
	pb.RegisterGreeterServer(grpcServer, &serverGreeter{})
	pb.RegisterDataStoreServer(grpcServer, &serverDataStore{})
	// start prometheus in background
	go func() {
		log.Printf("Prometheus listening on %v", metricsPort)
		log.Fatal(http.ListenAndServe(fmt.Sprintf(":%s", metricsPort), nil))
	}()
	log.Printf("Server started, listening on %v", lis.Addr())
	if err := grpcServer.Serve(lis); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
}
