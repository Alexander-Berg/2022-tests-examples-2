# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: yandex/maps/proto/driving/annotation.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import action_pb2 as yandex_dot_maps_dot_proto_dot_driving_dot_action__pb2
from . import landmark_pb2 as yandex_dot_maps_dot_proto_dot_driving_dot_landmark__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='yandex/maps/proto/driving/annotation.proto',
  package='yandex.maps.proto.driving.annotation',
  syntax='proto2',
  serialized_pb=_b('\n*yandex/maps/proto/driving/annotation.proto\x12$yandex.maps.proto.driving.annotation\x1a&yandex/maps/proto/driving/action.proto\x1a(yandex/maps/proto/driving/landmark.proto\"\x1d\n\rToponymPhrase\x12\x0c\n\x04text\x18\x01 \x02(\t\".\n\x17LeaveRoundaboutMetadata\x12\x13\n\x0b\x65xit_number\x18\x01 \x02(\r\"\x1f\n\rUturnMetadata\x12\x0e\n\x06length\x18\x01 \x02(\x01\"\xbf\x01\n\x0e\x41\x63tionMetadata\x12K\n\x0euturn_metadata\x18\x01 \x01(\x0b\x32\x33.yandex.maps.proto.driving.annotation.UturnMetadata\x12`\n\x19leave_roundabout_metadata\x18\x02 \x01(\x0b\x32=.yandex.maps.proto.driving.annotation.LeaveRoundaboutMetadata\"\xd1\x02\n\nAnnotation\x12\x41\n\x06\x61\x63tion\x18\x01 \x01(\x0e\x32(.yandex.maps.proto.driving.action.Action:\x07UNKNOWN\x12\x0f\n\x07toponym\x18\x02 \x01(\t\x12\x13\n\x0b\x64\x65scription\x18\x03 \x02(\t\x12M\n\x0f\x61\x63tion_metadata\x18\x04 \x02(\x0b\x32\x34.yandex.maps.proto.driving.annotation.ActionMetadata\x12>\n\x08landmark\x18\x05 \x03(\x0e\x32,.yandex.maps.proto.driving.landmark.Landmark\x12K\n\x0etoponym_phrase\x18\x06 \x01(\x0b\x32\x33.yandex.maps.proto.driving.annotation.ToponymPhrase')
  ,
  dependencies=[yandex_dot_maps_dot_proto_dot_driving_dot_action__pb2.DESCRIPTOR,yandex_dot_maps_dot_proto_dot_driving_dot_landmark__pb2.DESCRIPTOR,])
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_TOPONYMPHRASE = _descriptor.Descriptor(
  name='ToponymPhrase',
  full_name='yandex.maps.proto.driving.annotation.ToponymPhrase',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='text', full_name='yandex.maps.proto.driving.annotation.ToponymPhrase.text', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=166,
  serialized_end=195,
)


_LEAVEROUNDABOUTMETADATA = _descriptor.Descriptor(
  name='LeaveRoundaboutMetadata',
  full_name='yandex.maps.proto.driving.annotation.LeaveRoundaboutMetadata',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='exit_number', full_name='yandex.maps.proto.driving.annotation.LeaveRoundaboutMetadata.exit_number', index=0,
      number=1, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=197,
  serialized_end=243,
)


_UTURNMETADATA = _descriptor.Descriptor(
  name='UturnMetadata',
  full_name='yandex.maps.proto.driving.annotation.UturnMetadata',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='length', full_name='yandex.maps.proto.driving.annotation.UturnMetadata.length', index=0,
      number=1, type=1, cpp_type=5, label=2,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=245,
  serialized_end=276,
)


_ACTIONMETADATA = _descriptor.Descriptor(
  name='ActionMetadata',
  full_name='yandex.maps.proto.driving.annotation.ActionMetadata',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='uturn_metadata', full_name='yandex.maps.proto.driving.annotation.ActionMetadata.uturn_metadata', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='leave_roundabout_metadata', full_name='yandex.maps.proto.driving.annotation.ActionMetadata.leave_roundabout_metadata', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=279,
  serialized_end=470,
)


_ANNOTATION = _descriptor.Descriptor(
  name='Annotation',
  full_name='yandex.maps.proto.driving.annotation.Annotation',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='action', full_name='yandex.maps.proto.driving.annotation.Annotation.action', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=True, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='toponym', full_name='yandex.maps.proto.driving.annotation.Annotation.toponym', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='description', full_name='yandex.maps.proto.driving.annotation.Annotation.description', index=2,
      number=3, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='action_metadata', full_name='yandex.maps.proto.driving.annotation.Annotation.action_metadata', index=3,
      number=4, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='landmark', full_name='yandex.maps.proto.driving.annotation.Annotation.landmark', index=4,
      number=5, type=14, cpp_type=8, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='toponym_phrase', full_name='yandex.maps.proto.driving.annotation.Annotation.toponym_phrase', index=5,
      number=6, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=473,
  serialized_end=810,
)

_ACTIONMETADATA.fields_by_name['uturn_metadata'].message_type = _UTURNMETADATA
_ACTIONMETADATA.fields_by_name['leave_roundabout_metadata'].message_type = _LEAVEROUNDABOUTMETADATA
_ANNOTATION.fields_by_name['action'].enum_type = yandex_dot_maps_dot_proto_dot_driving_dot_action__pb2._ACTION
_ANNOTATION.fields_by_name['action_metadata'].message_type = _ACTIONMETADATA
_ANNOTATION.fields_by_name['landmark'].enum_type = yandex_dot_maps_dot_proto_dot_driving_dot_landmark__pb2._LANDMARK
_ANNOTATION.fields_by_name['toponym_phrase'].message_type = _TOPONYMPHRASE
DESCRIPTOR.message_types_by_name['ToponymPhrase'] = _TOPONYMPHRASE
DESCRIPTOR.message_types_by_name['LeaveRoundaboutMetadata'] = _LEAVEROUNDABOUTMETADATA
DESCRIPTOR.message_types_by_name['UturnMetadata'] = _UTURNMETADATA
DESCRIPTOR.message_types_by_name['ActionMetadata'] = _ACTIONMETADATA
DESCRIPTOR.message_types_by_name['Annotation'] = _ANNOTATION

ToponymPhrase = _reflection.GeneratedProtocolMessageType('ToponymPhrase', (_message.Message,), dict(
  DESCRIPTOR = _TOPONYMPHRASE,
  __module__ = 'yandex.maps.proto.driving.annotation_pb2'
  # @@protoc_insertion_point(class_scope:yandex.maps.proto.driving.annotation.ToponymPhrase)
  ))
_sym_db.RegisterMessage(ToponymPhrase)

LeaveRoundaboutMetadata = _reflection.GeneratedProtocolMessageType('LeaveRoundaboutMetadata', (_message.Message,), dict(
  DESCRIPTOR = _LEAVEROUNDABOUTMETADATA,
  __module__ = 'yandex.maps.proto.driving.annotation_pb2'
  # @@protoc_insertion_point(class_scope:yandex.maps.proto.driving.annotation.LeaveRoundaboutMetadata)
  ))
_sym_db.RegisterMessage(LeaveRoundaboutMetadata)

UturnMetadata = _reflection.GeneratedProtocolMessageType('UturnMetadata', (_message.Message,), dict(
  DESCRIPTOR = _UTURNMETADATA,
  __module__ = 'yandex.maps.proto.driving.annotation_pb2'
  # @@protoc_insertion_point(class_scope:yandex.maps.proto.driving.annotation.UturnMetadata)
  ))
_sym_db.RegisterMessage(UturnMetadata)

ActionMetadata = _reflection.GeneratedProtocolMessageType('ActionMetadata', (_message.Message,), dict(
  DESCRIPTOR = _ACTIONMETADATA,
  __module__ = 'yandex.maps.proto.driving.annotation_pb2'
  # @@protoc_insertion_point(class_scope:yandex.maps.proto.driving.annotation.ActionMetadata)
  ))
_sym_db.RegisterMessage(ActionMetadata)

Annotation = _reflection.GeneratedProtocolMessageType('Annotation', (_message.Message,), dict(
  DESCRIPTOR = _ANNOTATION,
  __module__ = 'yandex.maps.proto.driving.annotation_pb2'
  # @@protoc_insertion_point(class_scope:yandex.maps.proto.driving.annotation.Annotation)
  ))
_sym_db.RegisterMessage(Annotation)


# @@protoc_insertion_point(module_scope)
