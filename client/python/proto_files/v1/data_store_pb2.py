# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: v1/data_store.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x13v1/data_store.proto\x12\ndata_store")\n\x0bSaveRequest\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t"\'\n\tSaveReply\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t"\x1a\n\x0bLoadRequest\x12\x0b\n\x03key\x18\x01 \x01(\t"\x1a\n\tLoadReply\x12\r\n\x05value\x18\x01 \x01(\t2\x7f\n\tDataStore\x12\x38\n\x04Save\x12\x17.data_store.SaveRequest\x1a\x15.data_store.SaveReply"\x00\x12\x38\n\x04Load\x12\x17.data_store.LoadRequest\x1a\x15.data_store.LoadReply"\x00\x42\x06Z\x04./v1b\x06proto3'
)

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "v1.data_store_pb2", globals())
if _descriptor._USE_C_DESCRIPTORS == False:

    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b"Z\004./v1"
    _SAVEREQUEST._serialized_start = 35
    _SAVEREQUEST._serialized_end = 76
    _SAVEREPLY._serialized_start = 78
    _SAVEREPLY._serialized_end = 117
    _LOADREQUEST._serialized_start = 119
    _LOADREQUEST._serialized_end = 145
    _LOADREPLY._serialized_start = 147
    _LOADREPLY._serialized_end = 173
    _DATASTORE._serialized_start = 175
    _DATASTORE._serialized_end = 302
# @@protoc_insertion_point(module_scope)
