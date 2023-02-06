# pylint: disable=import-error
# pylint: disable=no-name-in-module

import driver_position_entry.fbs.DriverPositionEntry as DriverPositionEntry
import flatbuffers

import tests_driver_route_watcher.position_fbs as PositionFbs


def serialize_driver_position_entry(entry):
    transport_type_map = {
        'unknown': -1,
        'automobile': 0,
        'pedestrian': 1,
        'bicycle': 2,
        'masstransit': 3,
    }

    position = entry['position']
    direction = entry.get('direction', -1)
    timestamp = entry.get('timestamp', -1)
    transport_type = transport_type_map[entry.get('transport_type')]

    builder = flatbuffers.Builder(0)

    DriverPositionEntry.DriverPositionEntryStart(builder)
    position_fbs = PositionFbs.serialize_position(builder, position)
    DriverPositionEntry.DriverPositionEntryAddPosition(builder, position_fbs)
    DriverPositionEntry.DriverPositionEntryAddDirection(builder, direction)
    DriverPositionEntry.DriverPositionEntryAddTimestamp(builder, timestamp)
    DriverPositionEntry.DriverPositionEntryAddTransportType(
        builder, transport_type,
    )

    obj = DriverPositionEntry.DriverPositionEntryEnd(builder)
    builder.Finish(obj)
    return bytes(builder.Output())
