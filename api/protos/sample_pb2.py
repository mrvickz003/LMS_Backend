# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: api/protos/sample.proto
# Protobuf Python Version: 5.28.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    28,
    1,
    '',
    'api/protos/sample.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x17\x61pi/protos/sample.proto\"-\n\nOTPRequest\x12\x0f\n\x07user_id\x18\x01 \x01(\t\x12\x0e\n\x06length\x18\x02 \x01(\x05\"/\n\x0bOTPResponse\x12\x0b\n\x03otp\x18\x01 \x01(\t\x12\x13\n\x0b\x65xpiry_time\x18\x02 \x01(\t\"4\n\x14OTPValidationRequest\x12\x0f\n\x07user_id\x18\x01 \x01(\t\x12\x0b\n\x03otp\x18\x02 \x01(\t\"7\n\x15OTPValidationResponse\x12\r\n\x05valid\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t2t\n\nOTPService\x12(\n\x0bGenerateOTP\x12\x0b.OTPRequest\x1a\x0c.OTPResponse\x12<\n\x0bValidateOTP\x12\x15.OTPValidationRequest\x1a\x16.OTPValidationResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'api.protos.sample_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_OTPREQUEST']._serialized_start=27
  _globals['_OTPREQUEST']._serialized_end=72
  _globals['_OTPRESPONSE']._serialized_start=74
  _globals['_OTPRESPONSE']._serialized_end=121
  _globals['_OTPVALIDATIONREQUEST']._serialized_start=123
  _globals['_OTPVALIDATIONREQUEST']._serialized_end=175
  _globals['_OTPVALIDATIONRESPONSE']._serialized_start=177
  _globals['_OTPVALIDATIONRESPONSE']._serialized_end=232
  _globals['_OTPSERVICE']._serialized_start=234
  _globals['_OTPSERVICE']._serialized_end=350
# @@protoc_insertion_point(module_scope)
