# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: yandex/maps/proto/search/precision.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='yandex/maps/proto/search/precision.proto',
  package='yandex.maps.proto.search.precision',
  syntax='proto2',
  serialized_options=None,
  serialized_pb=_b('\n(yandex/maps/proto/search/precision.proto\x12\"yandex.maps.proto.search.precision*9\n\tPrecision\x12\t\n\x05\x45XACT\x10\x00\x12\n\n\x06NUMBER\x10\x01\x12\t\n\x05RANGE\x10\x02\x12\n\n\x06NEARBY\x10\x03')
)

_PRECISION = _descriptor.EnumDescriptor(
  name='Precision',
  full_name='yandex.maps.proto.search.precision.Precision',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='EXACT', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='NUMBER', index=1, number=1,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='RANGE', index=2, number=2,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='NEARBY', index=3, number=3,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=80,
  serialized_end=137,
)
_sym_db.RegisterEnumDescriptor(_PRECISION)

Precision = enum_type_wrapper.EnumTypeWrapper(_PRECISION)
EXACT = 0
NUMBER = 1
RANGE = 2
NEARBY = 3


DESCRIPTOR.enum_types_by_name['Precision'] = _PRECISION
_sym_db.RegisterFileDescriptor(DESCRIPTOR)


# @@protoc_insertion_point(module_scope)
