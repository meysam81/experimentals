package main

import (
	"context"
	pbv2 "grpc_tutorial/proto/v2"
	"log"
)

type serverHealthCheck struct {
	pbv2.UnimplementedHealthServer
}

func (*serverHealthCheck) Check(ctx context.Context, in *pbv2.HealthCheckRequest) (*pbv2.HealthCheckResponse, error) {
	log.Printf("Received: %v", in.GetService())
	return &pbv2.HealthCheckResponse{Status: pbv2.HealthCheckResponse_SERVING}, nil
}
