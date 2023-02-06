# pylint: disable=import-error

import datetime

import flatbuffers
import pytest
import pytz
from reposition.fbs.v2.drivers.index import Driver
from reposition.fbs.v2.drivers.index import GeoPoint
from reposition.fbs.v2.drivers.index import Response


def build_response(revision, has_more, drivers):
    builder = flatbuffers.Builder(0)

    serialized_drivers = []

    for driver in drivers:
        driver_id = builder.CreateString(driver['driver_id'])
        park_db_id = builder.CreateString(driver['park_db_id'])

        can_take_orders = driver['can_take_orders']
        can_take_orders_when_busy = driver['can_take_orders_when_busy']
        reposition_check_required = driver['reposition_check_required']

        mode = None
        if 'mode_name' in driver:
            mode = builder.CreateString(driver['mode_name'])

        bonus_until = None
        if 'bonus_until' in driver and driver['bonus_until']:
            bonus_until = int(driver['bonus_until'].timestamp())

        destination_point = None
        if 'destination_point' in driver:
            destination_point = driver['destination_point']

        Driver.DriverStart(builder)
        Driver.DriverAddDriverId(builder, driver_id)
        Driver.DriverAddParkDbId(builder, park_db_id)
        Driver.DriverAddCanTakeOrders(builder, can_take_orders)
        Driver.DriverAddCanTakeOrdersWhenBusy(
            builder, can_take_orders_when_busy,
        )
        Driver.DriverAddRepositionCheckRequired(
            builder, reposition_check_required,
        )

        if mode:
            Driver.DriverAddModeName(builder, mode)

        if bonus_until:
            Driver.DriverAddBonusUntil(builder, bonus_until)

        if destination_point:
            Driver.DriverAddDestinationPoint(
                builder,
                GeoPoint.CreateGeoPoint(
                    builder, destination_point[1], destination_point[0],
                ),
            )

        serialized_drivers.append(Driver.DriverEnd(builder))

    Response.ResponseStartDriversVector(builder, len(serialized_drivers))

    for serialized_driver in reversed(serialized_drivers):
        builder.PrependUOffsetTRelative(serialized_driver)

    serialized_drivers = builder.EndVector(len(serialized_drivers))

    Response.ResponseStart(builder)

    Response.ResponseAddRevision(builder, revision)
    Response.ResponseAddHasMore(builder, has_more)
    Response.ResponseAddDrivers(builder, serialized_drivers)

    response = Response.ResponseEnd(builder)

    builder.Finish(response)

    return builder.Output()


def parse_response(data):
    response = Response.Response.GetRootAsResponse(data, 0)

    drivers = []

    for idx in range(0, response.DriversLength()):
        driver = response.Drivers(idx)

        drivers.append(
            {
                'driver_id': driver.DriverId().decode('utf-8'),
                'park_db_id': driver.ParkDbId().decode('utf-8'),
                'can_take_orders': driver.CanTakeOrders(),
                'can_take_orders_when_busy': (driver.CanTakeOrdersWhenBusy()),
                'reposition_check_required': (
                    driver.RepositionCheckRequired()
                ),
                'mode_name': driver.ModeName().decode('utf-8'),
                'bonus_until': (
                    datetime.datetime.fromtimestamp(
                        int(driver.BonusUntil()), pytz.timezone('UTC'),
                    )
                    if driver.BonusUntil()
                    else None
                ),
                'destination_point': [
                    driver.DestinationPoint().Longitude(),
                    driver.DestinationPoint().Latitude(),
                ],
            },
        )

    return {
        'drivers': drivers,
        'revision': response.Revision(),
        'has_more': response.HasMore(),
    }


@pytest.fixture(name='mock_reposition_index', autouse=True)
def mock_reposition_index(mockserver):
    class Context:
        def __init__(self):
            self.response = {'revision': 0, 'has_more': False, 'drivers': []}

        def set_response(self, drivers, revision=0, has_more=False):
            self.response = {
                'revision': revision,
                'has_more': has_more,
                'drivers': drivers,
            }

    ctx = Context()

    @mockserver.handler('/reposition-api/v2/drivers/index')
    def _mock(request):
        return mockserver.make_response(
            status=200,
            content_type='application/x-flatbuffers',
            response=build_response(**ctx.response),
        )

    return ctx
