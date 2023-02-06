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

import geobus.fbs.universal_signals.GeoPositionSignal as GeoPositionSignal
import geobus.fbs.universal_signals.Sensor as Sensor
import geobus.fbs.universal_signals.UniversalSignal as UniversalSignal
import geobus.fbs.universal_signals.UniversalSignals as UniversalSignals
import geobus.fbs.universal_signals.UniversalSignalsMessage as UniversalSignalsMessage
import geobus.fbs.Protocol as FbsProtocol


## === table serialization
def serialize_position_on_edge(input_data, builder):
    return gen_position_on_edge(
        builder,
        input_data['persistent_edge_id'],
        input_data['edge_displacement'],
    )


def serialize_geo_position_signal(input_data, builder):
    ## define serialization helpers for all fields
    def serialize_field_position(field_data, builder):
        if isinstance(field_data, (list,)):
            return serialize_position(field_data, builder)
        return serialize_position_as_obj(field_data, builder)

    def serialize_field_altitude(field_data, builder):
        return serialize_distance_int(field_data, builder)

    def serialize_field_direction(field_data, builder):
        return serialize_int(field_data, builder)

    def serialize_field_speed(field_data, builder):
        return serialize_double(field_data, builder)

    def serialize_field_accuracy(field_data, builder):
        return serialize_distance_int(field_data, builder)

    ## execute serialization helpers for all fields
    prepared_position = serialize_field_position(
        input_data['position'], builder,
    )
    prepared_altitude = None
    if 'altitude' in input_data:
        prepared_altitude = serialize_field_altitude(
            input_data['altitude'], builder,
        )
    prepared_direction = None
    if 'direction' in input_data:
        prepared_direction = serialize_field_direction(
            input_data['direction'], builder,
        )
    prepared_speed = None
    if 'speed' in input_data:
        prepared_speed = serialize_field_speed(input_data['speed'], builder)
    prepared_accuracy = None
    if 'accuracy' in input_data:
        prepared_accuracy = serialize_field_accuracy(
            input_data['accuracy'], builder,
        )

    # now, build entire table
    GeoPositionSignal.GeoPositionSignalStart(builder)
    GeoPositionSignal.GeoPositionSignalAddPosition(builder, prepared_position)
    if prepared_altitude is not None:
        GeoPositionSignal.GeoPositionSignalAddAltitude(
            builder, prepared_altitude,
        )
    if prepared_direction is not None:
        GeoPositionSignal.GeoPositionSignalAddDirection(
            builder, prepared_direction,
        )
    if prepared_speed is not None:
        GeoPositionSignal.GeoPositionSignalAddSpeed(builder, prepared_speed)
    if prepared_accuracy is not None:
        GeoPositionSignal.GeoPositionSignalAddAccuracy(
            builder, prepared_accuracy,
        )
    return GeoPositionSignal.GeoPositionSignalEnd(builder)


def serialize_universal_signal(input_data, builder):
    ## define serialization helpers for all fields
    def serialize_field_geo_position(field_data, builder):
        return serialize_geo_position_signal(field_data, builder)

    def serialize_field_position_on_edge(field_data, builder):
        return serialize_position_on_edge(field_data, builder)

    def serialize_field_prediction_shift(field_data, builder):
        return serialize_seconds_int(field_data, builder)

    def serialize_field_probability(field_data, builder):
        return serialize_double_in_ubyte(field_data, builder)

    def serialize_field_log_likelihood(field_data, builder):
        return serialize_double(field_data, builder)

    ## execute serialization helpers for all fields
    prepared_geo_position = serialize_field_geo_position(
        input_data['geo_position'], builder,
    )
    prepared_prediction_shift = None
    if 'prediction_shift' in input_data:
        prepared_prediction_shift = serialize_field_prediction_shift(
            input_data['prediction_shift'], builder,
        )
    else:
        prepared_prediction_shift = 0
    prepared_probability = None
    if 'probability' in input_data:
        prepared_probability = serialize_field_probability(
            input_data['probability'], builder,
        )
    else:
        prepared_probability = 255
    prepared_log_likelihood = None
    if 'log_likelihood' in input_data:
        prepared_log_likelihood = serialize_field_log_likelihood(
            input_data['log_likelihood'], builder,
        )

    # now, build entire table
    UniversalSignal.UniversalSignalStart(builder)
    UniversalSignal.UniversalSignalAddGeoPosition(
        builder, prepared_geo_position,
    )
    if 'position_on_edge' in input_data:
        UniversalSignal.UniversalSignalAddPositionOnEdge(
            builder,
            serialize_field_position_on_edge(
                input_data['position_on_edge'], builder,
            ),
        )
    UniversalSignal.UniversalSignalAddPredictionShift(
        builder, prepared_prediction_shift,
    )
    UniversalSignal.UniversalSignalAddProbability(
        builder, prepared_probability,
    )
    if prepared_log_likelihood is not None:
        UniversalSignal.UniversalSignalAddLogLikelihood(
            builder, prepared_log_likelihood,
        )
    return UniversalSignal.UniversalSignalEnd(builder)


def serialize_sensor(key, value, builder):
    ## define serialization helpers for all fields
    def serialize_field_key(field_data, builder):
        return serialize_string(field_data, builder)

    def serialize_field_value(field_data, builder):
        return serialize_byte_array(
            field_data, builder, Sensor.SensorStartValueVector,
        )

    ## execute serialization helpers for all fields
    prepared_key = serialize_field_key(key, builder)
    prepared_value = serialize_field_value(value, builder)

    # now, build entire table
    Sensor.SensorStart(builder)
    Sensor.SensorAddKey(builder, prepared_key)
    Sensor.SensorAddValue(builder, prepared_value)
    return Sensor.SensorEnd(builder)


def serialize_universal_signals(input_data, builder):
    ## define serialization helpers for all fields
    def serialize_field_contractor_id(field_data, builder):
        return serialize_dbid_uuid(
            field_data,
            builder,
            UniversalSignals.UniversalSignalsStartContractorIdVector,
        )

    def serialize_field_client_timestamp(field_data, builder):
        return serialize_time_point_in_mcs(field_data, builder)

    def serialize_field_sensors(field_data, builder):
        elems = [serialize_sensor(x, y, builder) for x, y in field_data.items]
        UniversalSignals.UniversalSignalsStartSensorsVector(
            builder, len(elems),
        )
        for elem in reversed(elems):
            builder.PrependUOffsetTRelative(elem)
        return builder.EndVector(len(elems))

    def serialize_field_signals(field_data, builder):
        elems = [serialize_universal_signal(x, builder) for x in field_data]
        UniversalSignals.UniversalSignalsStartSignalsVector(
            builder, len(elems),
        )
        for elem in reversed(elems):
            builder.PrependUOffsetTRelative(elem)
        return builder.EndVector(len(elems))

    source = None
    if 'source' in input_data:
        source = builder.CreateString(input_data['source'])
    ## execute serialization helpers for all fields
    prepared_contractor_id = serialize_field_contractor_id(
        input_data['contractor_id'], builder,
    )
    prepared_client_timestamp = serialize_field_client_timestamp(
        input_data['client_timestamp'], builder,
    )
    prepared_sensors = None
    if 'sensors' in input_data:
        prepared_sensors = serialize_field_sensors(
            input_data['sensors'], builder,
        )
    prepared_signals = serialize_field_signals(input_data['signals'], builder)

    # now, build entire table
    UniversalSignals.UniversalSignalsStart(builder)
    UniversalSignals.UniversalSignalsAddContractorId(
        builder, prepared_contractor_id,
    )
    if prepared_client_timestamp is not None:
        UniversalSignals.UniversalSignalsAddClientTimestamp(
            builder, prepared_client_timestamp,
        )
    if prepared_sensors is not None:
        UniversalSignals.UniversalSignalsAddSensors(builder, prepared_sensors)
    UniversalSignals.UniversalSignalsAddSignals(builder, prepared_signals)

    if source is not None:
        UniversalSignals.UniversalSignalsAddSource(builder, source)

    return UniversalSignals.UniversalSignalsEnd(builder)


def serialize_universal_signals_message(input_data, builder):
    ## define serialization helpers for all fields
    def serialize_field_payload(field_data, builder):
        elems = [serialize_universal_signals(x, builder) for x in field_data]

        UniversalSignalsMessage.UniversalSignalsMessageStartPayloadVector(
            builder, len(elems),
        )
        for elem in reversed(elems):
            builder.PrependUOffsetTRelative(elem)

        return builder.EndVector(len(elems))

    ## execute serialization helpers for all fields
    prepared_payload = serialize_field_payload(input_data['payload'], builder)

    # now, build entire table
    UniversalSignalsMessage.UniversalSignalsMessageStart(builder)
    UniversalSignalsMessage.UniversalSignalsMessageAddPayload(
        builder, prepared_payload,
    )
    return UniversalSignalsMessage.UniversalSignalsMessageEnd(builder)


# ====== table deserialization
def deserialize_position_on_edge(fbs_data):
    ## define serialization helpers for all fields
    def deserialize_field_persistent_edge(fbs_data):
        return deserialize_int(fbs_data.PersistentEdge())

    def deserialize_field_edge_displacement(fbs_data):
        return deserialize_double_in_ubyte(fbs_data.EdgeDisplacement())

    ## execute deserialization helpers for all fields
    result = {}
    result['persistent_edge'] = deserialize_field_persistent_edge(fbs_data)
    result['edge_displacement'] = deserialize_field_edge_displacement(fbs_data)
    return result


def deserialize_geo_position_signal(fbs_data):
    ## define serialization helpers for all fields
    def deserialize_field_position(fbs_data):
        return deserialize_position(fbs_data.Position())

    def deserialize_field_altitude(fbs_data):
        return deserialize_distance_int(fbs_data.Altitude())

    def deserialize_field_direction(fbs_data):
        return deserialize_int(fbs_data.Direction())

    def deserialize_field_speed(fbs_data):
        return deserialize_double(fbs_data.Speed())

    def deserialize_field_accuracy(fbs_data):
        return deserialize_distance_int(fbs_data.Accuracy())

    ## execute deserialization helpers for all fields
    result = {}
    result['position'] = deserialize_field_position(fbs_data)
    if fbs_data.Altitude() is not None:
        result['altitude'] = deserialize_field_altitude(fbs_data)
    if fbs_data.Direction() is not None:
        result['direction'] = deserialize_field_direction(fbs_data)
    if fbs_data.Speed() is not None:
        result['speed'] = deserialize_field_speed(fbs_data)
    if fbs_data.Accuracy() is not None:
        result['accuracy'] = deserialize_field_accuracy(fbs_data)
    return result


def deserialize_universal_signal(fbs_data):
    ## define serialization helpers for all fields
    def deserialize_field_geo_position(fbs_data):
        return deserialize_geo_position_signal(fbs_data.GeoPosition())

    def deserialize_field_position_on_edge(fbs_data):
        return deserialize_position_on_edge(fbs_data.PositionOnEdge())

    def deserialize_field_prediction_shift(fbs_data):
        return deserialize_seconds_int(fbs_data.PredictionShift())

    def deserialize_field_probability(fbs_data):
        return deserialize_double_in_ubyte(fbs_data.Probability())

    def deserialize_field_log_likelihood(fbs_data):
        return deserialize_double(fbs_data.LogLikelihood())

    ## execute deserialization helpers for all fields
    result = {}
    result['geo_position'] = deserialize_field_geo_position(fbs_data)
    if fbs_data.PositionOnEdge() is not None:
        result['position_on_edge'] = deserialize_field_position_on_edge(
            fbs_data,
        )
    if fbs_data.PredictionShift() is not None:
        result['prediction_shift'] = deserialize_field_prediction_shift(
            fbs_data,
        )
    if fbs_data.Probability() is not None:
        result['probability'] = deserialize_field_probability(fbs_data)
    if fbs_data.LogLikelihood() is not None:
        result['log_likelihood'] = deserialize_field_log_likelihood(fbs_data)
    return result


def deserialize_sensor(fbs_data):
    ## define serialization helpers for all fields
    def deserialize_field_key(fbs_data):
        return deserialize_string(fbs_data.Key())

    def deserialize_field_value(fbs_data):
        value_bytes = []
        for i in range(fbs_data.ValueLength()):
            value_bytes.append(chr(fbs_data.Value(i)))
        return ''.join(value_bytes)

    ## execute deserialization helpers for all fields
    result = {}
    result['key'] = deserialize_field_key(fbs_data)
    result['value'] = deserialize_field_value(fbs_data)
    return result


def deserialize_universal_signals(fbs_data):
    ## define serialization helpers for all fields
    def deserialize_field_contractor_id(fbs_data):
        return deserialize_dbid_uuid(fbs_data.ContractorIdAsNumpy())

    def deserialize_field_client_timestamp(fbs_data):
        return fbs_data.ClientTimestamp()

    def deserialize_field_source(fbs_data):
        return deserialize_string(fbs_data.Source())

    def deserialize_field_sensors(fbs_data):
        buf = []
        for i in range(fbs_data.SensorsLength()):
            buf.append(deserialize_sensor(fbs_data.Sensors(i)))
        return buf

    def deserialize_field_signals(fbs_data):
        buf = []
        for i in range(fbs_data.SignalsLength()):
            buf.append(deserialize_universal_signal(fbs_data.Signals(i)))

        return buf

    ## execute deserialization helpers for all fields
    result = {}
    result['contractor_id'] = deserialize_field_contractor_id(fbs_data)
    result['client_timestamp'] = deserialize_field_client_timestamp(fbs_data)
    if fbs_data.Source() is not None:
        result['source'] = deserialize_field_source(fbs_data)
    if fbs_data.SensorsLength() != 0:
        result['sensors'] = deserialize_field_sensors(fbs_data)
    result['signals'] = deserialize_field_signals(fbs_data)
    return result


def deserialize_universal_signals_message(fbs_data):
    ## define serialization helpers for all fields
    def deserialize_field_payload(fbs_data):
        buf = []
        for i in range(fbs_data.PayloadLength()):
            buf.append(deserialize_universal_signals(fbs_data.Payload(i)))

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

    obj = serialize_universal_signals_message(data, builder)
    builder.Finish(obj)

    return gzip_builder(builder)


def deserialize_message_data(msg):
    return deserialize_universal_signals_message(msg)


def serialize_message(data, now):
    serialized_data = serialize_message_data(data)

    result = gen_gzipped_channel_message(
        serialized_data, now, FbsProtocol.Protocol.UniversalPositionsV1,
    )
    return result


def deserialize_message(binary_data):
    decompressed_data = parse_and_decompress_message(binary_data)

    msg = (
        UniversalSignalsMessage.UniversalSignalsMessage.GetRootAsUniversalSignalsMessage(
            decompressed_data, 0,
        )
    )

    return deserialize_message_data(msg)
