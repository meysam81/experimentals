// Code generated by protoc-gen-go-grpc. DO NOT EDIT.
// versions:
// - protoc-gen-go-grpc v1.2.0
// - protoc             v3.21.9
// source: proto/v1/data_store.proto

package greetings

import (
	context "context"
	grpc "google.golang.org/grpc"
	codes "google.golang.org/grpc/codes"
	status "google.golang.org/grpc/status"
)

// This is a compile-time assertion to ensure that this generated file
// is compatible with the grpc package it is being compiled against.
// Requires gRPC-Go v1.32.0 or later.
const _ = grpc.SupportPackageIsVersion7

// DataStoreClient is the client API for DataStore service.
//
// For semantics around ctx use and closing/ending streaming RPCs, please refer to https://pkg.go.dev/google.golang.org/grpc/?tab=doc#ClientConn.NewStream.
type DataStoreClient interface {
	// Save a key value pair
	Save(ctx context.Context, in *SaveRequest, opts ...grpc.CallOption) (*SaveReply, error)
	// Get a value by key
	Load(ctx context.Context, in *LoadRequest, opts ...grpc.CallOption) (*LoadReply, error)
}

type dataStoreClient struct {
	cc grpc.ClientConnInterface
}

func NewDataStoreClient(cc grpc.ClientConnInterface) DataStoreClient {
	return &dataStoreClient{cc}
}

func (c *dataStoreClient) Save(ctx context.Context, in *SaveRequest, opts ...grpc.CallOption) (*SaveReply, error) {
	out := new(SaveReply)
	err := c.cc.Invoke(ctx, "/data_store.DataStore/Save", in, out, opts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

func (c *dataStoreClient) Load(ctx context.Context, in *LoadRequest, opts ...grpc.CallOption) (*LoadReply, error) {
	out := new(LoadReply)
	err := c.cc.Invoke(ctx, "/data_store.DataStore/Load", in, out, opts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

// DataStoreServer is the server API for DataStore service.
// All implementations must embed UnimplementedDataStoreServer
// for forward compatibility
type DataStoreServer interface {
	// Save a key value pair
	Save(context.Context, *SaveRequest) (*SaveReply, error)
	// Get a value by key
	Load(context.Context, *LoadRequest) (*LoadReply, error)
	mustEmbedUnimplementedDataStoreServer()
}

// UnimplementedDataStoreServer must be embedded to have forward compatible implementations.
type UnimplementedDataStoreServer struct {
}

func (UnimplementedDataStoreServer) Save(context.Context, *SaveRequest) (*SaveReply, error) {
	return nil, status.Errorf(codes.Unimplemented, "method Save not implemented")
}
func (UnimplementedDataStoreServer) Load(context.Context, *LoadRequest) (*LoadReply, error) {
	return nil, status.Errorf(codes.Unimplemented, "method Load not implemented")
}
func (UnimplementedDataStoreServer) mustEmbedUnimplementedDataStoreServer() {}

// UnsafeDataStoreServer may be embedded to opt out of forward compatibility for this service.
// Use of this interface is not recommended, as added methods to DataStoreServer will
// result in compilation errors.
type UnsafeDataStoreServer interface {
	mustEmbedUnimplementedDataStoreServer()
}

func RegisterDataStoreServer(s grpc.ServiceRegistrar, srv DataStoreServer) {
	s.RegisterService(&DataStore_ServiceDesc, srv)
}

func _DataStore_Save_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(SaveRequest)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(DataStoreServer).Save(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: "/data_store.DataStore/Save",
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(DataStoreServer).Save(ctx, req.(*SaveRequest))
	}
	return interceptor(ctx, in, info, handler)
}

func _DataStore_Load_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(LoadRequest)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(DataStoreServer).Load(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: "/data_store.DataStore/Load",
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(DataStoreServer).Load(ctx, req.(*LoadRequest))
	}
	return interceptor(ctx, in, info, handler)
}

// DataStore_ServiceDesc is the grpc.ServiceDesc for DataStore service.
// It's only intended for direct use with grpc.RegisterService,
// and not to be introspected or modified (even as a copy)
var DataStore_ServiceDesc = grpc.ServiceDesc{
	ServiceName: "data_store.DataStore",
	HandlerType: (*DataStoreServer)(nil),
	Methods: []grpc.MethodDesc{
		{
			MethodName: "Save",
			Handler:    _DataStore_Save_Handler,
		},
		{
			MethodName: "Load",
			Handler:    _DataStore_Load_Handler,
		},
	},
	Streams:  []grpc.StreamDesc{},
	Metadata: "proto/v1/data_store.proto",
}
