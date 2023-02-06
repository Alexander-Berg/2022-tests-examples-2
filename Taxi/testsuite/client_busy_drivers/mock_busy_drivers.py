"""
Usage:
@pytest.mark.busy_drivers(
    busy_drivers=[
        {
            'driver_id': 'dbid0_uuid2',
            'order_id': 'unknown',
            'taxi_status': 0,
            'destination': {'lat': 0.0, 'lon': 0.0},
            'final_destination': {'lat': 0.0, 'lon': 0.0},
        },
    ],
    chain_busy_drivers=[
        {
            'driver_id': 'dbid0_uuid2',
            'order_id': 'unknown',
            'destination': {'lat': 0.0, 'lon': 0.0},
            'left_time': 100,
            'left_distance': 1000,
            'tracking_type': 1, # 0 - route_tracking, 1 - linear_fallback
            'flags': '0',
        },
    ],
)
"""

import datetime
import typing

import flatbuffers
import pytest

# pylint: disable=import-error
import busy_drivers.fbs.BusyDriver as BusyDriver  # noqa: I100,I202
import busy_drivers.fbs.BusyDriverList as BusyDriverList
import busy_drivers.fbs.ChainBusyDriver as ChainBusyDriver
import busy_drivers.fbs.ChainBusyDriverList as ChainBusyDriverList
import busy_drivers.fbs.Position as Position


_SERVICE = '/busy-drivers'
_BUSY_DRIVERS_BULK_URL = '/v2/busy_drivers_bulk'
_CHAIN_BUSY_DRIVERS_BULK_URL = '/v2/chain_busy_drivers_bulk'
_BUSY_DRIVERS_MARKER = 'busy_drivers'

_Driver = typing.Dict[str, typing.Any]


class BusyDriversContext:
    _busy_drivers: typing.List[_Driver]
    _chain_busy_drivers: typing.List[_Driver]

    def __init__(self) -> None:
        self._busy_drivers = []
        self._chain_busy_drivers = []

    def reset(self) -> None:
        self._busy_drivers = []
        self._chain_busy_drivers = []

    def set_drivers(
            self,
            busy_drivers: typing.Optional[typing.List[_Driver]] = None,
            chain_busy_drivers: typing.Optional[typing.List[_Driver]] = None,
    ) -> None:
        self._busy_drivers = busy_drivers or []
        self._chain_busy_drivers = chain_busy_drivers or []

    @property
    def busy_drivers(self) -> typing.List[_Driver]:
        return self._busy_drivers

    @property
    def chain_busy_drivers(self) -> typing.List[_Driver]:
        return self._chain_busy_drivers

    def build_busy_drivers(
            self,
            busy_drivers: typing.List[_Driver],
            timestamp: datetime.datetime = datetime.datetime.now(),
    ) -> str:
        built_timestamp = int(self._build_timestamp(timestamp))
        builder = flatbuffers.Builder(0)
        built_drivers = []
        for busy_driver in busy_drivers:
            built_drivers.append(self._build_busy_driver(builder, busy_driver))
        BusyDriverList.BusyDriverListStartListVector(
            builder, len(built_drivers),
        )
        for built_driver in built_drivers:
            builder.PrependUOffsetTRelative(built_driver)
        built_drivers = builder.EndVector(len(built_drivers))
        BusyDriverList.BusyDriverListStart(builder)
        BusyDriverList.BusyDriverListAddTimestamp(builder, built_timestamp)
        BusyDriverList.BusyDriverListAddList(builder, built_drivers)
        obj = BusyDriverList.BusyDriverListEnd(builder)
        builder.Finish(obj)
        return builder.Output()

    def build_chain_busy_drivers(
            self,
            chain_busy_drivers: typing.List[_Driver],
            timestamp: datetime.datetime = datetime.datetime.now(),
    ) -> str:
        built_timestamp = int(self._build_timestamp(timestamp))
        builder = flatbuffers.Builder(0)
        built_drivers = []
        for chain_busy_driver in chain_busy_drivers:
            built_drivers.append(
                self._build_chain_busy_driver(builder, chain_busy_driver),
            )
        ChainBusyDriverList.ChainBusyDriverListStartListVector(
            builder, len(built_drivers),
        )
        for built_driver in built_drivers:
            builder.PrependUOffsetTRelative(built_driver)
        built_drivers = builder.EndVector(len(built_drivers))
        ChainBusyDriverList.ChainBusyDriverListStart(builder)
        ChainBusyDriverList.ChainBusyDriverListAddTimestamp(
            builder, built_timestamp,
        )
        ChainBusyDriverList.ChainBusyDriverListAddList(builder, built_drivers)
        obj = ChainBusyDriverList.ChainBusyDriverListEnd(builder)
        builder.Finish(obj)
        return builder.Output()

    def _build_timestamp(self, timestamp: datetime.datetime) -> float:
        epoch = datetime.datetime.utcfromtimestamp(0)
        return (timestamp - epoch).total_seconds()

    def _build_busy_driver(
            self, builder: flatbuffers.Builder, busy_driver: _Driver,
    ):
        order_id = builder.CreateString(busy_driver['order_id'])
        driver_id = builder.CreateString(busy_driver['driver_id'])
        taxi_status = busy_driver['taxi_status']
        BusyDriver.BusyDriverStart(builder)
        BusyDriver.BusyDriverAddDriverId(builder, driver_id)
        BusyDriver.BusyDriverAddTaxiStatus(builder, taxi_status)
        BusyDriver.BusyDriverAddOrderId(builder, order_id)
        if 'destination' in busy_driver:
            lon = busy_driver['destination']['lon']
            lat = busy_driver['destination']['lat']
            destination = Position.CreatePosition(builder, lon, lat)
            BusyDriver.BusyDriverAddDestination(builder, destination)
        if 'final_destination' in busy_driver:
            lon = busy_driver['final_destination']['lon']
            lat = busy_driver['final_destination']['lat']
            final_destination = Position.CreatePosition(builder, lon, lat)
            BusyDriver.BusyDriverAddFinalDestination(
                builder, final_destination,
            )

        return BusyDriver.BusyDriverEnd(builder)

    def _build_chain_busy_driver(
            self, builder: flatbuffers.Builder, chain_busy_driver: _Driver,
    ):
        order_id = builder.CreateString(chain_busy_driver['order_id'])
        driver_id = builder.CreateString(chain_busy_driver['driver_id'])
        ChainBusyDriver.ChainBusyDriverStart(builder)
        ChainBusyDriver.ChainBusyDriverAddDriverId(builder, driver_id)
        ChainBusyDriver.ChainBusyDriverAddOrderId(builder, order_id)
        lon = chain_busy_driver['destination']['lon']
        lat = chain_busy_driver['destination']['lat']
        destination = Position.CreatePosition(builder, lon, lat)
        ChainBusyDriver.ChainBusyDriverAddDestination(builder, destination)
        ChainBusyDriver.ChainBusyDriverAddTimeLeft(
            builder, chain_busy_driver['left_time'],
        )
        ChainBusyDriver.ChainBusyDriverAddDistanceLeft(
            builder, chain_busy_driver['left_distance'],
        )
        ChainBusyDriver.ChainBusyDriverAddApproximate(
            builder, chain_busy_driver['approximate'],
        )
        ChainBusyDriver.ChainBusyDriverAddFlags(
            builder, chain_busy_driver['flags'],
        )
        return ChainBusyDriver.ChainBusyDriverEnd(builder)


def pytest_addoption(parser):
    parser.addini(
        name='mocked-busy-drivers',
        type='bool',
        default=True,
        help='Set false to disable mocked busy-drivers by default',
    )


def pytest_configure(config):
    config.addinivalue_line('markers', f'{_BUSY_DRIVERS_MARKER}: busy drivers')


@pytest.fixture(name='busy_drivers_mocks')
def _busy_drivers_mocks(mockserver):
    busy_drivers_context = BusyDriversContext()

    @mockserver.handler(_SERVICE + _BUSY_DRIVERS_BULK_URL)
    def _mock_busy_drivers_bulk(request):
        chunk_idx = int(request.args['chunk_idx'])
        busy_drivers = (
            busy_drivers_context.busy_drivers if chunk_idx == 0 else []
        )
        response_fbs = busy_drivers_context.build_busy_drivers(busy_drivers)
        return mockserver.make_response(
            response_fbs,
            content_type='application/x-flatbuffers',
            charset='utf-8',
        )

    @mockserver.handler(_SERVICE + _CHAIN_BUSY_DRIVERS_BULK_URL)
    def _mock_chain_busy_drivers_bulk(request):
        chunk_idx = int(request.args['chunk_idx'])
        chain_busy_drivers = (
            busy_drivers_context.chain_busy_drivers if chunk_idx == 0 else []
        )
        response_fbs = busy_drivers_context.build_chain_busy_drivers(
            chain_busy_drivers,
        )
        return mockserver.make_response(
            response_fbs,
            content_type='application/x-flatbuffers',
            charset='utf-8',
        )

    return busy_drivers_context


@pytest.fixture(name='busy_drivers_fixture')
def _busy_drivers_fixture(busy_drivers_mocks, request):
    marker = request.node.get_closest_marker(_BUSY_DRIVERS_MARKER)
    if marker:
        busy_drivers_mocks.set_drivers(**marker.kwargs)

    yield busy_drivers_mocks

    busy_drivers_mocks.reset()
