# pylint: disable=import-only-modules
import pytest

from tests_grocery_dispatch import constants as const
from tests_grocery_dispatch.plugins.models import PerformerInfo

DISPATCH_TYPE = 'cargo_sync'


async def test_basic_status_200(
        taxi_grocery_dispatch,
        experiments3,
        cargo,
        grocery_dispatch_pg,
        cargo_pg,
):
    cargo.add_performer(
        claim_id=const.CLAIM_ID,
        eats_profile_id='123_123',
        driver_id='123',
        park_id='123',
    )

    experiments3.add_config(
        consumers=['grocery_dispatch/dispatch'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='grocery_dispatch_priority',
        default_value={'dispatches': ['cargo']},
    )

    dispatch = grocery_dispatch_pg.create_dispatch(
        dispatch_name=DISPATCH_TYPE,
        status='scheduled',
        performer=PerformerInfo(),
    )
    cargo_pg.create_claim(
        dispatch_id=dispatch.dispatch_id, claim_id=const.CLAIM_ID,
    )
    cargo.set_data(items=cargo.convert_items(dispatch.order.items))

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/performer_contact',
        {'dispatch_id': dispatch.dispatch_id},
    )
    assert response.status_code == 200
    assert response.json() == {
        'performer_id': dispatch.performer_id,
        'ext': cargo.courier_contact_ext,
        'phone': cargo.courier_contact_phone,
    }


@pytest.mark.parametrize(
    ['order_status', 'cargo_status'],
    [
        ['finished', 'delivered_finish'],
        ['canceled', 'cancelled'],
        ['revoked', 'returned_finish'],
    ],
)
async def test_finish_order_status_204(
        order_status,
        cargo_status,
        taxi_grocery_dispatch,
        experiments3,
        cargo,
        grocery_dispatch_pg,
        cargo_pg,
):
    experiments3.add_config(
        consumers=['grocery_dispatch/dispatch'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='grocery_dispatch_priority',
        default_value={'dispatches': ['cargo']},
    )

    cargo.add_performer(
        claim_id=const.CLAIM_ID,
        eats_profile_id='123_123',
        driver_id='123',
        park_id='123',
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
        items=cargo.convert_items(dispatch.order.items), status=cargo_status,
    )

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/performer_contact',
        {'dispatch_id': dispatch.dispatch_id},
    )
    assert response.status_code == 204


async def test_no_performer_status_204(
        taxi_grocery_dispatch, experiments3, grocery_dispatch_pg, cargo_pg,
):
    experiments3.add_config(
        consumers=['grocery_dispatch/dispatch'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='grocery_dispatch_priority',
        default_value={'dispatches': ['cargo']},
    )

    dispatch = grocery_dispatch_pg.create_dispatch(
        dispatch_name=DISPATCH_TYPE, status='scheduled',
    )
    cargo_pg.create_claim(
        dispatch_id=dispatch.dispatch_id, claim_id=const.CLAIM_ID,
    )

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/performer_contact',
        {'dispatch_id': dispatch.dispatch_id},
    )
    assert response.status_code == 204
