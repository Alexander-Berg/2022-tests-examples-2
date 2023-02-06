# pylint: disable=import-error,invalid-name,useless-object-inheritance
# pylint: disable=undefined-variable,unused-variable,too-many-lines
# pylint: disable=no-name-in-module,wildcard-import,import-only-modules
# pylint: disable=unused-wildcard-import
# flake8: noqa F501 F401 F841 F821


import flatbuffers

import pytest

from ..serialization_common import *
from ..helpers import (
    gen_gzipped_channel_message,
    parse_and_decompress_message,
    gzip_builder,
)

import geobus.fbs.timeleft.TrackingType as TrackingType
import geobus.fbs.timeleft.TimeleftData as TimeleftData
import geobus.fbs.timeleft.Timelefts as Timelefts
import geobus.fbs.timeleft.TimeleftsMessage as TimeleftsMessage
import geobus.fbs.Protocol as FbsProtocol

## === enums serialization
tracking_type_to_fbs_enum_constant = {
    'RouteTracking': TrackingType.TrackingType.RouteTracking,
    'LinearFallback': TrackingType.TrackingType.LinearFallback,
    'UnknownDestination': TrackingType.TrackingType.UnknownDestination,
}


def serialize_tracking_type(input_data: str, builder):
    return tracking_type_to_fbs_enum_constant[input_data]


## === enums deserialization
fbs_enum_constant_to_tracking_type = {
    TrackingType.TrackingType.RouteTracking: 'RouteTracking',
    TrackingType.TrackingType.LinearFallback: 'LinearFallback',
    TrackingType.TrackingType.UnknownDestination: 'UnknownDestination',
}


def deserialize_tracking_type(fbs_data):
    return fbs_enum_constant_to_tracking_type[fbs_data]


## === table serialization
def serialize_timeleft_data(input_data, builder):
    ## define serialization helpers for all fields
    def serialize_field_time_left(field_data, builder):
        return serialize_seconds_int(field_data, builder)

    def serialize_field_distance_left(field_data, builder):
        return serialize_distance_int(field_data, builder)

    def serialize_field_destination_position(field_data, builder):
        return serialize_position(field_data, builder)

    def serialize_field_order_id(field_data, builder):
        return serialize_string(field_data, builder)

    def serialize_field_point_id(field_data, builder):
        return serialize_string(field_data, builder)

    def serialize_field_service_id(field_data, builder):
        return serialize_string(field_data, builder)

    ## execute serialization helpers for all fields
    prepared_time_left = None
    prepared_distance_left = None
    if 'time_left' in input_data and 'distance_left' in input_data:
        prepared_time_left = serialize_field_time_left(
            input_data['time_left'], builder,
        )
        prepared_distance_left = serialize_field_distance_left(
            input_data['distance_left'], builder,
        )
    prepared_order_id = None
    if 'order_id' in input_data:
        prepared_order_id = serialize_field_order_id(
            input_data['order_id'], builder,
        )
    prepared_point_id = None
    if 'point_id' in input_data:
        prepared_point_id = serialize_field_point_id(
            input_data['point_id'], builder,
        )
    prepared_service_id = serialize_field_service_id(
        input_data['service_id'], builder,
    )

    # now, build entire table
    TimeleftData.TimeleftDataStart(builder)
    if prepared_time_left is not None and prepared_distance_left is not None:
        TimeleftData.TimeleftDataAddTimeLeft(builder, prepared_time_left)
        TimeleftData.TimeleftDataAddDistanceLeft(
            builder, prepared_distance_left,
        )
    prepared_destination_position = serialize_field_destination_position(
        input_data['destination_position'], builder,
    )
    TimeleftData.TimeleftDataAddDestinationPosition(
        builder, prepared_destination_position,
    )
    if prepared_order_id is not None:
        TimeleftData.TimeleftDataAddOrderId(builder, prepared_order_id)
    if prepared_point_id is not None:
        TimeleftData.TimeleftDataAddPointId(builder, prepared_point_id)
    TimeleftData.TimeleftDataAddServiceId(builder, prepared_service_id)
    return TimeleftData.TimeleftDataEnd(builder)


def serialize_timelefts(input_data, builder):
    ## define serialization helpers for all fields
    def serialize_field_timestamp(field_data, builder):
        return serialize_time_point_in_ms(field_data, builder)

    def serialize_field_tracking_type(field_data, builder):
        return serialize_tracking_type(field_data, builder)

    def serialize_field_contractor_id(field_data, builder):
        return serialize_dbid_uuid(
            field_data, builder, Timelefts.TimeleftsStartContractorIdVector,
        )

    def serialize_field_route_id(field_data, builder):
        return serialize_string(field_data, builder)

    def serialize_field_adjusted_pos(field_data, builder):
        return serialize_position(field_data, builder)

    def serialize_field_timeleft_data(field_data, builder):
        elems = [serialize_timeleft_data(x, builder) for x in field_data]

        Timelefts.TimeleftsStartTimeleftDataVector(builder, len(elems))
        for elem in reversed(elems):
            builder.PrependUOffsetTRelative(elem)

        return builder.EndVector(len(elems))

    def serialize_field_adjusted_segment_index(field_data, builder):
        return serialize_int(field_data, builder)

    def serialize_field_update_timestamp(field_data, builder):
        return serialize_time_point_in_ms(field_data, builder)

    ## execute serialization helpers for all fields
    prepared_timestamp = serialize_field_timestamp(
        input_data['timestamp'], builder,
    )
    prepared_tracking_type = serialize_field_tracking_type(
        input_data['tracking_type'], builder,
    )
    prepared_contractor_id = serialize_field_contractor_id(
        input_data['contractor_id'], builder,
    )
    prepared_route_id = serialize_field_route_id(
        input_data['route_id'], builder,
    )
    prepared_timeleft_data = serialize_field_timeleft_data(
        input_data['timeleft_data'], builder,
    )
    prepared_adjusted_segment_index = serialize_field_adjusted_segment_index(
        input_data['adjusted_segment_index'], builder,
    )
    prepared_update_timestamp = serialize_field_update_timestamp(
        input_data['update_timestamp'], builder,
    )

    # now, build entire table
    Timelefts.TimeleftsStart(builder)
    Timelefts.TimeleftsAddTimestamp(builder, prepared_timestamp)
    Timelefts.TimeleftsAddTrackingType(builder, prepared_tracking_type)
    Timelefts.TimeleftsAddContractorId(builder, prepared_contractor_id)
    Timelefts.TimeleftsAddRouteId(builder, prepared_route_id)
    prepared_adjusted_pos = serialize_field_adjusted_pos(
        input_data['adjusted_pos'], builder,
    )
    Timelefts.TimeleftsAddAdjustedPos(builder, prepared_adjusted_pos)
    Timelefts.TimeleftsAddTimeleftData(builder, prepared_timeleft_data)
    Timelefts.TimeleftsAddAdjustedSegmentIndex(
        builder, prepared_adjusted_segment_index,
    )
    Timelefts.TimeleftsAddUpdateTimestamp(builder, prepared_update_timestamp)
    return Timelefts.TimeleftsEnd(builder)


def serialize_timelefts_message(input_data, builder):
    ## define serialization helpers for all fields
    def serialize_field_payload(field_data, builder):
        elems = [serialize_timelefts(x, builder) for x in field_data]

        TimeleftsMessage.TimeleftsMessageStartPayloadVector(
            builder, len(elems),
        )
        for elem in reversed(elems):
            builder.PrependUOffsetTRelative(elem)

        return builder.EndVector(len(elems))

    ## execute serialization helpers for all fields
    prepared_payload = serialize_field_payload(input_data['payload'], builder)

    # now, build entire table
    TimeleftsMessage.TimeleftsMessageStart(builder)
    TimeleftsMessage.TimeleftsMessageAddPayload(builder, prepared_payload)
    return TimeleftsMessage.TimeleftsMessageEnd(builder)


# ====== table deserialization
def deserialize_timeleft_data(fbs_data):
    ## define serialization helpers for all fields
    def deserialize_field_time_left(fbs_data):
        return deserialize_seconds_int(fbs_data.TimeLeft())

    def deserialize_field_distance_left(fbs_data):
        return deserialize_distance_int(fbs_data.DistanceLeft())

    def deserialize_field_destination_position(fbs_data):
        return deserialize_position(fbs_data.DestinationPosition())

    def deserialize_field_order_id(fbs_data):
        return deserialize_string(fbs_data.OrderId())

    def deserialize_field_point_id(fbs_data):
        return deserialize_string(fbs_data.PointId())

    def deserialize_field_service_id(fbs_data):
        return deserialize_string(fbs_data.ServiceId())

    ## execute deserialization helpers for all fields
    result = {}
    if fbs_data.TimeLeft() is not None and fbs_data.DistanceLeft() is not None:
        result['time_left'] = deserialize_field_time_left(fbs_data)
        result['distance_left'] = deserialize_field_distance_left(fbs_data)
    result['destination_position'] = deserialize_field_destination_position(
        fbs_data,
    )
    if fbs_data.OrderId() is not None:
        result['order_id'] = deserialize_field_order_id(fbs_data)
    if fbs_data.PointId() is not None:
        result['point_id'] = deserialize_field_point_id(fbs_data)
    result['service_id'] = deserialize_field_service_id(fbs_data)
    return result


def deserialize_timelefts(fbs_data):
    ## define serialization helpers for all fields
    def deserialize_field_timestamp(fbs_data):
        return deserialize_time_point_in_ms(fbs_data.Timestamp())

    def deserialize_field_tracking_type(fbs_data):
        return deserialize_tracking_type(fbs_data.TrackingType())

    def deserialize_field_contractor_id(fbs_data):
        return deserialize_dbid_uuid(fbs_data.ContractorIdAsNumpy())

    def deserialize_field_route_id(fbs_data):
        return deserialize_string(fbs_data.RouteId())

    def deserialize_field_adjusted_pos(fbs_data):
        return deserialize_position(fbs_data.AdjustedPos())

    def deserialize_field_timeleft_data(fbs_data):
        buf = []
        for i in range(fbs_data.TimeleftDataLength()):
            buf.append(deserialize_timeleft_data(fbs_data.TimeleftData(i)))

        return buf

    def deserialize_field_adjusted_segment_index(fbs_data):
        return deserialize_int(fbs_data.AdjustedSegmentIndex())

    def deserialize_field_update_timestamp(fbs_data):
        return deserialize_time_point_in_ms(fbs_data.UpdateTimestamp())

    ## execute deserialization helpers for all fields
    result = {}
    result['timestamp'] = deserialize_field_timestamp(fbs_data)
    result['tracking_type'] = deserialize_field_tracking_type(fbs_data)
    result['contractor_id'] = deserialize_field_contractor_id(fbs_data)
    result['route_id'] = deserialize_field_route_id(fbs_data)
    result['adjusted_pos'] = deserialize_field_adjusted_pos(fbs_data)
    result['timeleft_data'] = deserialize_field_timeleft_data(fbs_data)
    result[
        'adjusted_segment_index'
    ] = deserialize_field_adjusted_segment_index(fbs_data)
    result['update_timestamp'] = deserialize_field_update_timestamp(fbs_data)
    return result


def deserialize_timelefts_message(fbs_data):
    ## define serialization helpers for all fields
    def deserialize_field_payload(fbs_data):
        buf = []
        for i in range(fbs_data.PayloadLength()):
            buf.append(deserialize_timelefts(fbs_data.Payload(i)))

        return buf

    ## execute deserialization helpers for all fields
    result = {}
    result['payload'] = deserialize_field_payload(fbs_data)
    return result


## ==== top-level methods
def serialize_message_data(data):
    builder = flatbuffers.Builder(0)
    # Our version of python flatbuffers doesn't support forceDefaults mode
    # Which is required for this channel to operate.
    # Do not pass '0' as values for members
    # builder.forceDefaults = True

    obj = serialize_timelefts_message(data, builder)
    builder.Finish(obj)

    return gzip_builder(builder)


def deserialize_message_data(msg):
    return deserialize_timelefts_message(msg)


def serialize_message(data, now):
    serialized_data = serialize_message_data(data)

    result = gen_gzipped_channel_message(
        serialized_data, now, FbsProtocol.Protocol.TimeleftsV1,
    )
    return result


def deserialize_message(binary_data):
    decompressed_data = parse_and_decompress_message(binary_data)

    msg = TimeleftsMessage.TimeleftsMessage.GetRootAsTimeleftsMessage(
        decompressed_data, 0,
    )

    return deserialize_message_data(msg)
