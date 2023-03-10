# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: yandex/maps/proto/search/common.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='yandex/maps/proto/search/common.proto',
  package='yandex.maps.proto.search.common',
  syntax='proto2',
  serialized_options=None,
  serialized_pb=_b('\n%yandex/maps/proto/search/common.proto\x12\x1fyandex.maps.proto.search.common\"*\n\x0cKeyValuePair\x12\x0b\n\x03key\x18\x01 \x02(\t\x12\r\n\x05value\x18\x02 \x02(\t\"W\n\x06\x41\x63tion\x12\x0c\n\x04type\x18\x01 \x02(\t\x12?\n\x08property\x18\x02 \x03(\x0b\x32-.yandex.maps.proto.search.common.KeyValuePair\"0\n\x05Image\x12\x14\n\x0curl_template\x18\x01 \x02(\t\x12\x0b\n\x03tag\x18\x03 \x03(\tJ\x04\x08\x02\x10\x03\"\x1e\n\x06\x41nchor\x12\t\n\x01x\x18\x01 \x02(\x02\x12\t\n\x01y\x18\x02 \x02(\x02\"v\n\x04Icon\x12\x35\n\x05image\x18\x01 \x02(\x0b\x32&.yandex.maps.proto.search.common.Image\x12\x37\n\x06\x61nchor\x18\x02 \x01(\x0b\x32\'.yandex.maps.proto.search.common.Anchor')
)




_KEYVALUEPAIR = _descriptor.Descriptor(
  name='KeyValuePair',
  full_name='yandex.maps.proto.search.common.KeyValuePair',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='yandex.maps.proto.search.common.KeyValuePair.key', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='value', full_name='yandex.maps.proto.search.common.KeyValuePair.value', index=1,
      number=2, type=9, cpp_type=9, label=2,
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
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=74,
  serialized_end=116,
)


_ACTION = _descriptor.Descriptor(
  name='Action',
  full_name='yandex.maps.proto.search.common.Action',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='type', full_name='yandex.maps.proto.search.common.Action.type', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='property', full_name='yandex.maps.proto.search.common.Action.property', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
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
  serialized_start=118,
  serialized_end=205,
)


_IMAGE = _descriptor.Descriptor(
  name='Image',
  full_name='yandex.maps.proto.search.common.Image',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='url_template', full_name='yandex.maps.proto.search.common.Image.url_template', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='tag', full_name='yandex.maps.proto.search.common.Image.tag', index=1,
      number=3, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
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
  serialized_start=207,
  serialized_end=255,
)


_ANCHOR = _descriptor.Descriptor(
  name='Anchor',
  full_name='yandex.maps.proto.search.common.Anchor',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='x', full_name='yandex.maps.proto.search.common.Anchor.x', index=0,
      number=1, type=2, cpp_type=6, label=2,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='y', full_name='yandex.maps.proto.search.common.Anchor.y', index=1,
      number=2, type=2, cpp_type=6, label=2,
      has_default_value=False, default_value=float(0),
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
  serialized_start=257,
  serialized_end=287,
)


_ICON = _descriptor.Descriptor(
  name='Icon',
  full_name='yandex.maps.proto.search.common.Icon',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='image', full_name='yandex.maps.proto.search.common.Icon.image', index=0,
      number=1, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='anchor', full_name='yandex.maps.proto.search.common.Icon.anchor', index=1,
      number=2, type=11, cpp_type=10, label=1,
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
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=289,
  serialized_end=407,
)

_ACTION.fields_by_name['property'].message_type = _KEYVALUEPAIR
_ICON.fields_by_name['image'].message_type = _IMAGE
_ICON.fields_by_name['anchor'].message_type = _ANCHOR
DESCRIPTOR.message_types_by_name['KeyValuePair'] = _KEYVALUEPAIR
DESCRIPTOR.message_types_by_name['Action'] = _ACTION
DESCRIPTOR.message_types_by_name['Image'] = _IMAGE
DESCRIPTOR.message_types_by_name['Anchor'] = _ANCHOR
DESCRIPTOR.message_types_by_name['Icon'] = _ICON
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

KeyValuePair = _reflection.GeneratedProtocolMessageType('KeyValuePair', (_message.Message,), {
  'DESCRIPTOR' : _KEYVALUEPAIR,
  '__module__' : 'yandex.maps.proto.search.common_pb2'
  # @@protoc_insertion_point(class_scope:yandex.maps.proto.search.common.KeyValuePair)
  })
_sym_db.RegisterMessage(KeyValuePair)

Action = _reflection.GeneratedProtocolMessageType('Action', (_message.Message,), {
  'DESCRIPTOR' : _ACTION,
  '__module__' : 'yandex.maps.proto.search.common_pb2'
  # @@protoc_insertion_point(class_scope:yandex.maps.proto.search.common.Action)
  })
_sym_db.RegisterMessage(Action)

Image = _reflection.GeneratedProtocolMessageType('Image', (_message.Message,), {
  'DESCRIPTOR' : _IMAGE,
  '__module__' : 'yandex.maps.proto.search.common_pb2'
  # @@protoc_insertion_point(class_scope:yandex.maps.proto.search.common.Image)
  })
_sym_db.RegisterMessage(Image)

Anchor = _reflection.GeneratedProtocolMessageType('Anchor', (_message.Message,), {
  'DESCRIPTOR' : _ANCHOR,
  '__module__' : 'yandex.maps.proto.search.common_pb2'
  # @@protoc_insertion_point(class_scope:yandex.maps.proto.search.common.Anchor)
  })
_sym_db.RegisterMessage(Anchor)

Icon = _reflection.GeneratedProtocolMessageType('Icon', (_message.Message,), {
  'DESCRIPTOR' : _ICON,
  '__module__' : 'yandex.maps.proto.search.common_pb2'
  # @@protoc_insertion_point(class_scope:yandex.maps.proto.search.common.Icon)
  })
_sym_db.RegisterMessage(Icon)


# @@protoc_insertion_point(module_scope)
