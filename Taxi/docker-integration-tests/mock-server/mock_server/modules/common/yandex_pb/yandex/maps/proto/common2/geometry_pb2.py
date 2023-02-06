# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: yandex/maps/proto/common2/geometry.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='yandex/maps/proto/common2/geometry.proto',
  package='yandex.maps.proto.common2.geometry',
  syntax='proto2',
  serialized_pb=_b('\n(yandex/maps/proto/common2/geometry.proto\x12\"yandex.maps.proto.common2.geometry\"!\n\x05Point\x12\x0b\n\x03lon\x18\x01 \x02(\x01\x12\x0b\n\x03lat\x18\x02 \x02(\x01\"2\n\rCoordSequence\x12\r\n\x05\x66irst\x18\x01 \x01(\x11\x12\x12\n\x06\x64\x65ltas\x18\x02 \x03(\x11\x42\x02\x10\x01\"\x8c\x01\n\x08Polyline\x12?\n\x04lons\x18\x01 \x02(\x0b\x32\x31.yandex.maps.proto.common2.geometry.CoordSequence\x12?\n\x04lats\x18\x02 \x02(\x0b\x32\x31.yandex.maps.proto.common2.geometry.CoordSequence\"C\n\x10PolylinePosition\x12\x15\n\rsegment_index\x18\x01 \x02(\r\x12\x18\n\x10segment_position\x18\x02 \x02(\x01\"\x95\x01\n\x0bSubpolyline\x12\x43\n\x05\x62\x65gin\x18\x01 \x02(\x0b\x32\x34.yandex.maps.proto.common2.geometry.PolylinePosition\x12\x41\n\x03\x65nd\x18\x02 \x02(\x0b\x32\x34.yandex.maps.proto.common2.geometry.PolylinePosition\"\x8e\x01\n\nLinearRing\x12?\n\x04lons\x18\x01 \x02(\x0b\x32\x31.yandex.maps.proto.common2.geometry.CoordSequence\x12?\n\x04lats\x18\x02 \x02(\x0b\x32\x31.yandex.maps.proto.common2.geometry.CoordSequence\"\x92\x01\n\x07Polygon\x12\x42\n\nouter_ring\x18\x01 \x02(\x0b\x32..yandex.maps.proto.common2.geometry.LinearRing\x12\x43\n\x0binner_rings\x18\x02 \x03(\x0b\x32..yandex.maps.proto.common2.geometry.LinearRing\"\xc2\x01\n\x08Geometry\x12\x38\n\x05point\x18\x01 \x01(\x0b\x32).yandex.maps.proto.common2.geometry.Point\x12>\n\x08polyline\x18\x02 \x01(\x0b\x32,.yandex.maps.proto.common2.geometry.Polyline\x12<\n\x07polygon\x18\x03 \x01(\x0b\x32+.yandex.maps.proto.common2.geometry.Polygon\"\x8f\x01\n\x0b\x42oundingBox\x12?\n\x0clower_corner\x18\x01 \x02(\x0b\x32).yandex.maps.proto.common2.geometry.Point\x12?\n\x0cupper_corner\x18\x02 \x02(\x0b\x32).yandex.maps.proto.common2.geometry.Point\"*\n\tDirection\x12\x0f\n\x07\x61zimuth\x18\x01 \x02(\x01\x12\x0c\n\x04tilt\x18\x02 \x02(\x01\"6\n\x04Span\x12\x17\n\x0fhorizontalAngle\x18\x01 \x02(\x01\x12\x15\n\rverticalAngle\x18\x02 \x02(\x01')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_POINT = _descriptor.Descriptor(
  name='Point',
  full_name='yandex.maps.proto.common2.geometry.Point',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='lon', full_name='yandex.maps.proto.common2.geometry.Point.lon', index=0,
      number=1, type=1, cpp_type=5, label=2,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='lat', full_name='yandex.maps.proto.common2.geometry.Point.lat', index=1,
      number=2, type=1, cpp_type=5, label=2,
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
  serialized_start=80,
  serialized_end=113,
)


_COORDSEQUENCE = _descriptor.Descriptor(
  name='CoordSequence',
  full_name='yandex.maps.proto.common2.geometry.CoordSequence',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='first', full_name='yandex.maps.proto.common2.geometry.CoordSequence.first', index=0,
      number=1, type=17, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='deltas', full_name='yandex.maps.proto.common2.geometry.CoordSequence.deltas', index=1,
      number=2, type=17, cpp_type=1, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=_descriptor._ParseOptions(descriptor_pb2.FieldOptions(), _b('\020\001'))),
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
  serialized_start=115,
  serialized_end=165,
)


_POLYLINE = _descriptor.Descriptor(
  name='Polyline',
  full_name='yandex.maps.proto.common2.geometry.Polyline',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='lons', full_name='yandex.maps.proto.common2.geometry.Polyline.lons', index=0,
      number=1, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='lats', full_name='yandex.maps.proto.common2.geometry.Polyline.lats', index=1,
      number=2, type=11, cpp_type=10, label=2,
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
  serialized_start=168,
  serialized_end=308,
)


_POLYLINEPOSITION = _descriptor.Descriptor(
  name='PolylinePosition',
  full_name='yandex.maps.proto.common2.geometry.PolylinePosition',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='segment_index', full_name='yandex.maps.proto.common2.geometry.PolylinePosition.segment_index', index=0,
      number=1, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='segment_position', full_name='yandex.maps.proto.common2.geometry.PolylinePosition.segment_position', index=1,
      number=2, type=1, cpp_type=5, label=2,
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
  serialized_start=310,
  serialized_end=377,
)


_SUBPOLYLINE = _descriptor.Descriptor(
  name='Subpolyline',
  full_name='yandex.maps.proto.common2.geometry.Subpolyline',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='begin', full_name='yandex.maps.proto.common2.geometry.Subpolyline.begin', index=0,
      number=1, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='end', full_name='yandex.maps.proto.common2.geometry.Subpolyline.end', index=1,
      number=2, type=11, cpp_type=10, label=2,
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
  serialized_start=380,
  serialized_end=529,
)


_LINEARRING = _descriptor.Descriptor(
  name='LinearRing',
  full_name='yandex.maps.proto.common2.geometry.LinearRing',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='lons', full_name='yandex.maps.proto.common2.geometry.LinearRing.lons', index=0,
      number=1, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='lats', full_name='yandex.maps.proto.common2.geometry.LinearRing.lats', index=1,
      number=2, type=11, cpp_type=10, label=2,
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
  serialized_start=532,
  serialized_end=674,
)


_POLYGON = _descriptor.Descriptor(
  name='Polygon',
  full_name='yandex.maps.proto.common2.geometry.Polygon',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='outer_ring', full_name='yandex.maps.proto.common2.geometry.Polygon.outer_ring', index=0,
      number=1, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='inner_rings', full_name='yandex.maps.proto.common2.geometry.Polygon.inner_rings', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
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
  serialized_start=677,
  serialized_end=823,
)


_GEOMETRY = _descriptor.Descriptor(
  name='Geometry',
  full_name='yandex.maps.proto.common2.geometry.Geometry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='point', full_name='yandex.maps.proto.common2.geometry.Geometry.point', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='polyline', full_name='yandex.maps.proto.common2.geometry.Geometry.polyline', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='polygon', full_name='yandex.maps.proto.common2.geometry.Geometry.polygon', index=2,
      number=3, type=11, cpp_type=10, label=1,
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
  serialized_start=826,
  serialized_end=1020,
)


_BOUNDINGBOX = _descriptor.Descriptor(
  name='BoundingBox',
  full_name='yandex.maps.proto.common2.geometry.BoundingBox',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='lower_corner', full_name='yandex.maps.proto.common2.geometry.BoundingBox.lower_corner', index=0,
      number=1, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='upper_corner', full_name='yandex.maps.proto.common2.geometry.BoundingBox.upper_corner', index=1,
      number=2, type=11, cpp_type=10, label=2,
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
  serialized_start=1023,
  serialized_end=1166,
)


_DIRECTION = _descriptor.Descriptor(
  name='Direction',
  full_name='yandex.maps.proto.common2.geometry.Direction',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='azimuth', full_name='yandex.maps.proto.common2.geometry.Direction.azimuth', index=0,
      number=1, type=1, cpp_type=5, label=2,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='tilt', full_name='yandex.maps.proto.common2.geometry.Direction.tilt', index=1,
      number=2, type=1, cpp_type=5, label=2,
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
  serialized_start=1168,
  serialized_end=1210,
)


_SPAN = _descriptor.Descriptor(
  name='Span',
  full_name='yandex.maps.proto.common2.geometry.Span',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='horizontalAngle', full_name='yandex.maps.proto.common2.geometry.Span.horizontalAngle', index=0,
      number=1, type=1, cpp_type=5, label=2,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='verticalAngle', full_name='yandex.maps.proto.common2.geometry.Span.verticalAngle', index=1,
      number=2, type=1, cpp_type=5, label=2,
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
  serialized_start=1212,
  serialized_end=1266,
)

_POLYLINE.fields_by_name['lons'].message_type = _COORDSEQUENCE
_POLYLINE.fields_by_name['lats'].message_type = _COORDSEQUENCE
_SUBPOLYLINE.fields_by_name['begin'].message_type = _POLYLINEPOSITION
_SUBPOLYLINE.fields_by_name['end'].message_type = _POLYLINEPOSITION
_LINEARRING.fields_by_name['lons'].message_type = _COORDSEQUENCE
_LINEARRING.fields_by_name['lats'].message_type = _COORDSEQUENCE
_POLYGON.fields_by_name['outer_ring'].message_type = _LINEARRING
_POLYGON.fields_by_name['inner_rings'].message_type = _LINEARRING
_GEOMETRY.fields_by_name['point'].message_type = _POINT
_GEOMETRY.fields_by_name['polyline'].message_type = _POLYLINE
_GEOMETRY.fields_by_name['polygon'].message_type = _POLYGON
_BOUNDINGBOX.fields_by_name['lower_corner'].message_type = _POINT
_BOUNDINGBOX.fields_by_name['upper_corner'].message_type = _POINT
DESCRIPTOR.message_types_by_name['Point'] = _POINT
DESCRIPTOR.message_types_by_name['CoordSequence'] = _COORDSEQUENCE
DESCRIPTOR.message_types_by_name['Polyline'] = _POLYLINE
DESCRIPTOR.message_types_by_name['PolylinePosition'] = _POLYLINEPOSITION
DESCRIPTOR.message_types_by_name['Subpolyline'] = _SUBPOLYLINE
DESCRIPTOR.message_types_by_name['LinearRing'] = _LINEARRING
DESCRIPTOR.message_types_by_name['Polygon'] = _POLYGON
DESCRIPTOR.message_types_by_name['Geometry'] = _GEOMETRY
DESCRIPTOR.message_types_by_name['BoundingBox'] = _BOUNDINGBOX
DESCRIPTOR.message_types_by_name['Direction'] = _DIRECTION
DESCRIPTOR.message_types_by_name['Span'] = _SPAN

Point = _reflection.GeneratedProtocolMessageType('Point', (_message.Message,), dict(
  DESCRIPTOR = _POINT,
  __module__ = 'yandex.maps.proto.common2.geometry_pb2'
  # @@protoc_insertion_point(class_scope:yandex.maps.proto.common2.geometry.Point)
  ))
_sym_db.RegisterMessage(Point)

CoordSequence = _reflection.GeneratedProtocolMessageType('CoordSequence', (_message.Message,), dict(
  DESCRIPTOR = _COORDSEQUENCE,
  __module__ = 'yandex.maps.proto.common2.geometry_pb2'
  # @@protoc_insertion_point(class_scope:yandex.maps.proto.common2.geometry.CoordSequence)
  ))
_sym_db.RegisterMessage(CoordSequence)

Polyline = _reflection.GeneratedProtocolMessageType('Polyline', (_message.Message,), dict(
  DESCRIPTOR = _POLYLINE,
  __module__ = 'yandex.maps.proto.common2.geometry_pb2'
  # @@protoc_insertion_point(class_scope:yandex.maps.proto.common2.geometry.Polyline)
  ))
_sym_db.RegisterMessage(Polyline)

PolylinePosition = _reflection.GeneratedProtocolMessageType('PolylinePosition', (_message.Message,), dict(
  DESCRIPTOR = _POLYLINEPOSITION,
  __module__ = 'yandex.maps.proto.common2.geometry_pb2'
  # @@protoc_insertion_point(class_scope:yandex.maps.proto.common2.geometry.PolylinePosition)
  ))
_sym_db.RegisterMessage(PolylinePosition)

Subpolyline = _reflection.GeneratedProtocolMessageType('Subpolyline', (_message.Message,), dict(
  DESCRIPTOR = _SUBPOLYLINE,
  __module__ = 'yandex.maps.proto.common2.geometry_pb2'
  # @@protoc_insertion_point(class_scope:yandex.maps.proto.common2.geometry.Subpolyline)
  ))
_sym_db.RegisterMessage(Subpolyline)

LinearRing = _reflection.GeneratedProtocolMessageType('LinearRing', (_message.Message,), dict(
  DESCRIPTOR = _LINEARRING,
  __module__ = 'yandex.maps.proto.common2.geometry_pb2'
  # @@protoc_insertion_point(class_scope:yandex.maps.proto.common2.geometry.LinearRing)
  ))
_sym_db.RegisterMessage(LinearRing)

Polygon = _reflection.GeneratedProtocolMessageType('Polygon', (_message.Message,), dict(
  DESCRIPTOR = _POLYGON,
  __module__ = 'yandex.maps.proto.common2.geometry_pb2'
  # @@protoc_insertion_point(class_scope:yandex.maps.proto.common2.geometry.Polygon)
  ))
_sym_db.RegisterMessage(Polygon)

Geometry = _reflection.GeneratedProtocolMessageType('Geometry', (_message.Message,), dict(
  DESCRIPTOR = _GEOMETRY,
  __module__ = 'yandex.maps.proto.common2.geometry_pb2'
  # @@protoc_insertion_point(class_scope:yandex.maps.proto.common2.geometry.Geometry)
  ))
_sym_db.RegisterMessage(Geometry)

BoundingBox = _reflection.GeneratedProtocolMessageType('BoundingBox', (_message.Message,), dict(
  DESCRIPTOR = _BOUNDINGBOX,
  __module__ = 'yandex.maps.proto.common2.geometry_pb2'
  # @@protoc_insertion_point(class_scope:yandex.maps.proto.common2.geometry.BoundingBox)
  ))
_sym_db.RegisterMessage(BoundingBox)

Direction = _reflection.GeneratedProtocolMessageType('Direction', (_message.Message,), dict(
  DESCRIPTOR = _DIRECTION,
  __module__ = 'yandex.maps.proto.common2.geometry_pb2'
  # @@protoc_insertion_point(class_scope:yandex.maps.proto.common2.geometry.Direction)
  ))
_sym_db.RegisterMessage(Direction)

Span = _reflection.GeneratedProtocolMessageType('Span', (_message.Message,), dict(
  DESCRIPTOR = _SPAN,
  __module__ = 'yandex.maps.proto.common2.geometry_pb2'
  # @@protoc_insertion_point(class_scope:yandex.maps.proto.common2.geometry.Span)
  ))
_sym_db.RegisterMessage(Span)


_COORDSEQUENCE.fields_by_name['deltas'].has_options = True
_COORDSEQUENCE.fields_by_name['deltas']._options = _descriptor._ParseOptions(descriptor_pb2.FieldOptions(), _b('\020\001'))
# @@protoc_insertion_point(module_scope)