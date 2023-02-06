# pylint: disable=import-only-modules
import pytest

from tests_grocery_dispatch import constants as const
from tests_grocery_dispatch.plugins.models import PerformerInfo


DISPATCH_TYPE = 'cargo_sync'


@pytest.mark.parametrize(
    'transport_type',
    [None, 'electric_bicycle', 'pedestrian', 'bicycle', 'car', 'courier_car'],
)
async def test_car_info(
        taxi_grocery_dispatch,
        pgsql,
        mockserver,
        experiments3,
        cargo,
        transport_type,
        grocery_dispatch_pg,
        cargo_pg,
):
    experiments3.add_config(
        consumers=['grocery_dispatch/dispatch'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='grocery_dispatch_priority',
        default_value={'dispatches': ['cargo']},
    )

    eats_profile_id = '123_123'
    driver_id = '111'
    park_id = '222'
    car_number = 'A123B'
    car_model = 'bentley'
    car_color = 'red'
    car_color_hex = '#f44336'
    performer_name = 'test_courier_name'
    cargo.add_performer(
        name=performer_name,
        claim_id=const.CLAIM_ID,
        eats_profile_id=eats_profile_id,
        driver_id=driver_id,
        park_id=park_id,
        transport_type=transport_type,
        car_number=car_number,
        car_model=car_model,
        car_color=car_color,
        car_color_hex=car_color_hex,
    )

    dispatch = grocery_dispatch_pg.create_dispatch(
        dispatch_name=DISPATCH_TYPE,
        status='scheduled',
        performer=PerformerInfo(),
    )
    cargo_pg.create_claim(
        dispatch_id=dispatch.dispatch_id, claim_id=const.CLAIM_ID,
    )
    cargo.set_data(
        items=cargo.convert_items(dispatch.order.items),
        transport_type=transport_type,
        car_number=car_number,
        car_model=car_model,
        car_color=car_color,
        car_color_hex=car_color_hex,
        courier_name=performer_name,
    )

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/performer_info',
        {'dispatch_id': dispatch.dispatch_id},
    )
    assert response.status_code == 200
    body = {
        'driver_id': driver_id,
        'eats_profile_id': eats_profile_id,
        'park_id': park_id,
        'performer_id': park_id + '_' + driver_id,
        'performer_name': performer_name,
    }
    if transport_type is not None:
        body['transport_type'] = transport_type
    if transport_type in ['car', 'courier_car']:
        body['car_number'] = car_number
        body['car_model'] = car_model
        body['car_color'] = car_color
        body['car_color_hex'] = car_color_hex
    assert response.json() == body


@pytest.mark.parametrize(
    ['cargo_error_code', 'timeout'], [(500, False), (200, True)],
)
async def test_cargo_failure(
        taxi_grocery_dispatch,
        cargo,
        cargo_error_code,
        timeout,
        grocery_dispatch_pg,
        cargo_pg,
):
    eats_profile_id = '123_123'
    driver_id = '111'
    park_id = '222'
    car_number = 'A123B'
    performer_name = 'test_courier_name'
    cargo.add_performer(
        name=performer_name,
        claim_id=const.CLAIM_ID,
        eats_profile_id=eats_profile_id,
        driver_id=driver_id,
        park_id=park_id,
        transport_type='pedestrian',
        car_number=car_number,
    )

    dispatch = grocery_dispatch_pg.create_dispatch(
        dispatch_name=DISPATCH_TYPE,
        status='scheduled',
        performer=PerformerInfo(),
    )
    cargo_pg.create_claim(
        dispatch_id=dispatch.dispatch_id, claim_id=const.CLAIM_ID,
    )
    cargo.set_data(
        items=cargo.convert_items(dispatch.order.items),
        cargo_info_error_code=cargo_error_code,
        cargo_info_timeout=timeout,
        courier_name=performer_name,
    )

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/performer_info',
        {'dispatch_id': dispatch.dispatch_id},
    )
    assert response.status_code == 200

    response_body = response.json()
    assert response_body == {
        'performer_id': dispatch.performer.performer_id,
        'eats_profile_id': dispatch.performer.eats_profile_id,
        'performer_name': dispatch.performer.name,
        'driver_id': dispatch.performer.driver_id,
        'park_id': dispatch.performer.park_id,
    }
