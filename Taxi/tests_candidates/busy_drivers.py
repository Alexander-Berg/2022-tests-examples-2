# pylint: disable=import-error
import busy_drivers.fbs.ChainBusyDriver as ChainBusyDriver
import busy_drivers.fbs.ChainBusyDriverList as ChainBusyDriverList
import busy_drivers.fbs.Position as Position
import flatbuffers


def fbs_chain_busy_drivers(data, timestamp):
    builder = flatbuffers.Builder(0)
    drivers = []
    for driver in data:
        drivers.append(_fbs_chain_busy_driver(builder, driver))
    ChainBusyDriverList.ChainBusyDriverListStartListVector(
        builder, len(drivers),
    )
    for driver in drivers:
        builder.PrependUOffsetTRelative(driver)
    drivers = builder.EndVector(len(drivers))
    ChainBusyDriverList.ChainBusyDriverListStart(builder)
    ChainBusyDriverList.ChainBusyDriverListAddTimestamp(
        builder, int(timestamp),
    )
    ChainBusyDriverList.ChainBusyDriverListAddList(builder, drivers)
    obj = ChainBusyDriverList.ChainBusyDriverListEnd(builder)
    builder.Finish(obj)
    return bytes(builder.Output())


def _fbs_chain_busy_driver(builder, driver):
    order_id = builder.CreateString(driver['order_id'])
    driver_id = builder.CreateString(driver['driver_id'])
    flags = builder.CreateString(driver['flags'])
    ChainBusyDriver.ChainBusyDriverStart(builder)
    ChainBusyDriver.ChainBusyDriverAddDriverId(builder, driver_id)
    ChainBusyDriver.ChainBusyDriverAddOrderId(builder, order_id)
    lon = driver['destination'][0]
    lat = driver['destination'][1]
    destination = Position.CreatePosition(builder, lon, lat)
    ChainBusyDriver.ChainBusyDriverAddDestination(builder, destination)
    ChainBusyDriver.ChainBusyDriverAddLeftTime(builder, driver['left_time'])
    ChainBusyDriver.ChainBusyDriverAddLeftDistance(
        builder, driver['left_distance'],
    )
    ChainBusyDriver.ChainBusyDriverAddApproximate(
        builder, driver['approximate'],
    )
    ChainBusyDriver.ChainBusyDriverAddFlags(builder, flags)
    return ChainBusyDriver.ChainBusyDriverEnd(builder)
