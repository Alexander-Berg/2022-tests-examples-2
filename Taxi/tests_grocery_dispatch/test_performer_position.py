# pylint: disable=import-only-modules
from tests_grocery_dispatch import constants as const
from tests_grocery_dispatch.plugins.models import PerformerInfo


DIRECTION = 40
LATITUDE = 37.5783920288086
LONGITUDE = -55.7350642053194
SPEED = 10
TIMESTAMP = 90
TIMESTAMP_RESPONCE = '1970-01-01T00:01:30+00:00'

POSITION = {
    'direction': DIRECTION,
    'lat': LATITUDE,
    'lon': LONGITUDE,
    'speed': SPEED,
    'timestamp': TIMESTAMP,
}


async def test_basic_status_200(
        taxi_grocery_dispatch,
        grocery_dispatch_pg,
        mockserver,
        driver_trackstory,
):

    performer = PerformerInfo()
    dispatch = grocery_dispatch_pg.create_dispatch(
        status='scheduled', performer=performer,
    )

    driver_trackstory.set_position(
        driver_id=performer.park_id + '_' + performer.driver_id, **POSITION,
    )

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/performer_position',
        {'dispatch_id': dispatch.dispatch_id},
    )
    assert response.status_code == 200
    assert response.json() == {
        'performer_id': dispatch.performer_id,
        'timestamp': TIMESTAMP_RESPONCE,
        'location': {'lat': LATITUDE, 'lon': LONGITUDE},
        'speed': SPEED,
        'direction': DIRECTION,
    }


async def test_basic_status_204(taxi_grocery_dispatch, grocery_dispatch_pg):
    dispatch = grocery_dispatch_pg.create_dispatch(status='scheduled')

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/performer_position',
        {'dispatch_id': dispatch.dispatch_id},
    )
    assert response.status_code == 204


async def test_basic_status_400(taxi_grocery_dispatch):
    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/performer_position',
        {'dispatch_id': const.DISPATCH_ID},
    )
    assert response.status_code == 404


async def test_basic_status_204_not_park_id(
        taxi_grocery_dispatch, grocery_dispatch_pg,
):
    dispatch = grocery_dispatch_pg.create_dispatch(
        status='scheduled', performer=PerformerInfo(park_id=None),
    )

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/performer_position',
        {'dispatch_id': dispatch.dispatch_id},
    )
    assert response.status_code == 204


async def test_basic_status_204_not_driver_id(
        taxi_grocery_dispatch, grocery_dispatch_pg,
):
    dispatch = grocery_dispatch_pg.create_dispatch(
        status='scheduled', performer=PerformerInfo(driver_id=None),
    )

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/performer_position',
        {'dispatch_id': dispatch.dispatch_id},
    )
    assert response.status_code == 204
