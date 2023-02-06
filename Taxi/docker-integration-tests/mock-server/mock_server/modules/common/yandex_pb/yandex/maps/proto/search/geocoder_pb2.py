# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: yandex/maps/proto/search/geocoder.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from ..common2 import geometry_pb2 as yandex_dot_maps_dot_proto_dot_common2_dot_geometry__pb2
from ..common2 import metadata_pb2 as yandex_dot_maps_dot_proto_dot_common2_dot_metadata__pb2
from . import address_pb2 as yandex_dot_maps_dot_proto_dot_search_dot_address__pb2
from . import precision_pb2 as yandex_dot_maps_dot_proto_dot_search_dot_precision__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='yandex/maps/proto/search/geocoder.proto',
  package='yandex.maps.proto.search.geocoder',
  syntax='proto2',
  serialized_options=None,
  serialized_pb=_b('\n\'yandex/maps/proto/search/geocoder.proto\x12!yandex.maps.proto.search.geocoder\x1a(yandex/maps/proto/common2/geometry.proto\x1a(yandex/maps/proto/common2/metadata.proto\x1a&yandex/maps/proto/search/address.proto\x1a(yandex/maps/proto/search/precision.proto\"\xc2\x01\n\x11GeoObjectMetadata\x12\x46\n\x0fhouse_precision\x18\x01 \x01(\x0e\x32-.yandex.maps.proto.search.precision.Precision\x12:\n\x07\x61\x64\x64ress\x18\x02 \x02(\x0b\x32).yandex.maps.proto.search.address.Address\x12\x13\n\x0b\x66ormer_name\x18\x03 \x01(\t\x12\n\n\x02id\x18\x04 \x01(\t*\x08\x08\x64\x10\x80\x80\x80\x80\x02\"u\n\x0fRequestMetadata\x12\x0c\n\x04text\x18\x01 \x02(\t\x12\x43\n\nbounded_by\x18\x02 \x01(\x0b\x32/.yandex.maps.proto.common2.geometry.BoundingBox\x12\x0f\n\x07results\x18\x03 \x01(\x05\"\xb2\x01\n\x10ResponseMetadata\x12\x43\n\x07request\x18\x01 \x02(\x0b\x32\x32.yandex.maps.proto.search.geocoder.RequestMetadata\x12\r\n\x05\x66ound\x18\x02 \x02(\x05\x12@\n\rreverse_point\x18\x03 \x01(\x0b\x32).yandex.maps.proto.common2.geometry.Point*\x08\x08\x64\x10\x80\x80\x80\x80\x02:|\n\x11RESPONSE_METADATA\x12,.yandex.maps.proto.common2.metadata.Metadata\x18\n \x01(\x0b\x32\x33.yandex.maps.proto.search.geocoder.ResponseMetadata:\x7f\n\x13GEO_OBJECT_METADATA\x12,.yandex.maps.proto.common2.metadata.Metadata\x18\x0b \x01(\x0b\x32\x34.yandex.maps.proto.search.geocoder.GeoObjectMetadata')
  ,
  dependencies=[yandex_dot_maps_dot_proto_dot_common2_dot_geometry__pb2.DESCRIPTOR,yandex_dot_maps_dot_proto_dot_common2_dot_metadata__pb2.DESCRIPTOR,yandex_dot_maps_dot_proto_dot_search_dot_address__pb2.DESCRIPTOR,yandex_dot_maps_dot_proto_dot_search_dot_precision__pb2.DESCRIPTOR,])


RESPONSE_METADATA_FIELD_NUMBER = 10
RESPONSE_METADATA = _descriptor.FieldDescriptor(
  name='RESPONSE_METADATA', full_name='yandex.maps.proto.search.geocoder.RESPONSE_METADATA', index=0,
  number=10, type=11, cpp_type=10, label=1,
  has_default_value=False, default_value=None,
  message_type=None, enum_type=None, containing_type=None,
  is_extension=True, extension_scope=None,
  serialized_options=None, file=DESCRIPTOR)
GEO_OBJECT_METADATA_FIELD_NUMBER = 11
GEO_OBJECT_METADATA = _descriptor.FieldDescriptor(
  name='GEO_OBJECT_METADATA', full_name='yandex.maps.proto.search.geocoder.GEO_OBJECT_METADATA', index=1,
  number=11, type=11, cpp_type=10, label=1,
  has_default_value=False, default_value=None,
  message_type=None, enum_type=None, containing_type=None,
  is_extension=True, extension_scope=None,
  serialized_options=None, file=DESCRIPTOR)


_GEOOBJECTMETADATA = _descriptor.Descriptor(
  name='GeoObjectMetadata',
  full_name='yandex.maps.proto.search.geocoder.GeoObjectMetadata',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='house_precision', full_name='yandex.maps.proto.search.geocoder.GeoObjectMetadata.house_precision', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='address', full_name='yandex.maps.proto.search.geocoder.GeoObjectMetadata.address', index=1,
      number=2, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='former_name', full_name='yandex.maps.proto.search.geocoder.GeoObjectMetadata.former_name', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='id', full_name='yandex.maps.proto.search.geocoder.GeoObjectMetadata.id', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=True,
  syntax='proto2',
  extension_ranges=[(100, 536870912), ],
  oneofs=[
  ],
  serialized_start=245,
  serialized_end=439,
)


_REQUESTMETADATA = _descriptor.Descriptor(
  name='RequestMetadata',
  full_name='yandex.maps.proto.search.geocoder.RequestMetadata',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='text', full_name='yandex.maps.proto.search.geocoder.RequestMetadata.text', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='bounded_by', full_name='yandex.maps.proto.search.geocoder.RequestMetadata.bounded_by', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='results', full_name='yandex.maps.proto.search.geocoder.RequestMetadata.results', index=2,
      number=3, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=441,
  serialized_end=558,
)


_RESPONSEMETADATA = _descriptor.Descriptor(
  name='ResponseMetadata',
  full_name='yandex.maps.proto.search.geocoder.ResponseMetadata',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='request', full_name='yandex.maps.proto.search.geocoder.ResponseMetadata.request', index=0,
      number=1, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='found', full_name='yandex.maps.proto.search.geocoder.ResponseMetadata.found', index=1,
      number=2, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='reverse_point', full_name='yandex.maps.proto.search.geocoder.ResponseMetadata.reverse_point', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=True,
  syntax='proto2',
  extension_ranges=[(100, 536870912), ],
  oneofs=[
  ],
  serialized_start=561,
  serialized_end=739,
)

_GEOOBJECTMETADATA.fields_by_name['house_precision'].enum_type = yandex_dot_maps_dot_proto_dot_search_dot_precision__pb2._PRECISION
_GEOOBJECTMETADATA.fields_by_name['address'].message_type = yandex_dot_maps_dot_proto_dot_search_dot_address__pb2._ADDRESS
_REQUESTMETADATA.fields_by_name['bounded_by'].message_type = yandex_dot_maps_dot_proto_dot_common2_dot_geometry__pb2._BOUNDINGBOX
_RESPONSEMETADATA.fields_by_name['request'].message_type = _REQUESTMETADATA
_RESPONSEMETADATA.fields_by_name['reverse_point'].message_type = yandex_dot_maps_dot_proto_dot_common2_dot_geometry__pb2._POINT
DESCRIPTOR.message_types_by_name['GeoObjectMetadata'] = _GEOOBJECTMETADATA
DESCRIPTOR.message_types_by_name['RequestMetadata'] = _REQUESTMETADATA
DESCRIPTOR.message_types_by_name['ResponseMetadata'] = _RESPONSEMETADATA
DESCRIPTOR.extensions_by_name['RESPONSE_METADATA'] = RESPONSE_METADATA
DESCRIPTOR.extensions_by_name['GEO_OBJECT_METADATA'] = GEO_OBJECT_METADATA
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

GeoObjectMetadata = _reflection.GeneratedProtocolMessageType('GeoObjectMetadata', (_message.Message,), {
  'DESCRIPTOR' : _GEOOBJECTMETADATA,
  '__module__' : 'yandex.maps.proto.search.geocoder_pb2'
  # @@protoc_insertion_point(class_scope:yandex.maps.proto.search.geocoder.GeoObjectMetadata)
  })
_sym_db.RegisterMessage(GeoObjectMetadata)

RequestMetadata = _reflection.GeneratedProtocolMessageType('RequestMetadata', (_message.Message,), {
  'DESCRIPTOR' : _REQUESTMETADATA,
  '__module__' : 'yandex.maps.proto.search.geocoder_pb2'
  # @@protoc_insertion_point(class_scope:yandex.maps.proto.search.geocoder.RequestMetadata)
  })
_sym_db.RegisterMessage(RequestMetadata)

ResponseMetadata = _reflection.GeneratedProtocolMessageType('ResponseMetadata', (_message.Message,), {
  'DESCRIPTOR' : _RESPONSEMETADATA,
  '__module__' : 'yandex.maps.proto.search.geocoder_pb2'
  # @@protoc_insertion_point(class_scope:yandex.maps.proto.search.geocoder.ResponseMetadata)
  })
_sym_db.RegisterMessage(ResponseMetadata)

RESPONSE_METADATA.message_type = _RESPONSEMETADATA
yandex_dot_maps_dot_proto_dot_common2_dot_metadata__pb2.Metadata.RegisterExtension(RESPONSE_METADATA)
GEO_OBJECT_METADATA.message_type = _GEOOBJECTMETADATA
yandex_dot_maps_dot_proto_dot_common2_dot_metadata__pb2.Metadata.RegisterExtension(GEO_OBJECT_METADATA)

# @@protoc_insertion_point(module_scope)