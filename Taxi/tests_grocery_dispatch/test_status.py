import copy
import pytest

from tests_grocery_dispatch import configs
from tests_grocery_dispatch import constants as const
from tests_grocery_dispatch import models

# flake8: noqa F401, IS001
# pylint: disable=C5521
from tests_grocery_dispatch.plugins.models import Point, TimeSlot, OrderInfo

DISPATCH_TYPE = 'cargo_sync'
CLAIM_ID_1 = 'claim_1'
CLAIM_ID_2 = 'claim_2'

COURIER_ID_0 = 'courier_id_0'
COURIER_ID_1 = 'courier_id_1'
COURIER_ID_2 = 'courier_id_2'
DRIVER_ID_0 = 'driver_id_0'
DRIVER_ID_1 = 'driver_id_1'
DRIVER_ID_2 = 'driver_id_2'
PARK_ID_0 = 'park_id_0'
PARK_ID_1 = 'park_id_1'
PARK_ID_2 = 'park_id_2'

NOW = '2020-10-05T16:28:00.000Z'
DELIVERY_ETA_TS = '2020-10-05T16:38:00.000Z'
DELIVERY_ETA_TEST = '2020-10-05T16:38:00+00:00'


@pytest.mark.now(NOW)
async def test_basic_status_200(
        taxi_grocery_dispatch,
        mocked_time,
        cargo,
        grocery_dispatch_pg,
        cargo_pg,
):
    dispatch_info = grocery_dispatch_pg.create_dispatch(
        dispatch_name=DISPATCH_TYPE, status='scheduled',
    )
    cargo_model = cargo_pg.create_claim(
        dispatch_id=dispatch_info.dispatch_id,
        claim_id=CLAIM_ID_1,
        claim_version=123,
    )

    cargo.set_data(
        items=cargo.convert_items(dispatch_info.order.items),
        delivered_eta_ts=DELIVERY_ETA_TS,
        courier_name='test_courier_name',
        version=123,
    )
    cargo.add_performer(
        claim_id=CLAIM_ID_1,
        eats_profile_id=COURIER_ID_0,
        driver_id=DRIVER_ID_0,
        park_id=PARK_ID_0,
    )

    request = {'dispatch_id': dispatch_info.dispatch_id}

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/status', request,
    )
    assert response.status_code == 200
    assert response.json()['eta'] == 10 * 60
    assert response.json()['eta_timestamp'] == DELIVERY_ETA_TEST

    assert cargo_model.claim_version == 123

    mocked_time.sleep(60)
    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/status', request,
    )
    assert response.status_code == 200
    assert response.json()['eta'] == 9 * 60
    assert response.json()['eta_timestamp'] == DELIVERY_ETA_TEST

    assert cargo_model.claim_version == 123
    assert cargo.times_external_info_called() == 2


@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    ['other_claim_status', 'other_dispatch_status', 'batch_order_num'],
    [('pickuped', 'delivering', 1), ('pickuped', 'delivered', 0)],
    # Если заказ в батче отдали, карго вернет pickuped, но мы поставим диспатч в delivered
)
async def test_status_dispatch_in_batch(
        taxi_grocery_dispatch,
        mocked_time,
        cargo,
        other_claim_status,
        other_dispatch_status,
        batch_order_num,
        cargo_pg,
        grocery_dispatch_pg,
):
    dispatch_1 = grocery_dispatch_pg.create_dispatch(
        dispatch_name=DISPATCH_TYPE, status='scheduled',
    )
    dispatch_2 = grocery_dispatch_pg.create_dispatch(
        dispatch_name=DISPATCH_TYPE, status=other_dispatch_status,
    )

    order_location = Point(lon=0.0, lat=0.0)

    cargo_pg.create_claim(
        dispatch_id=dispatch_1.dispatch_id,
        claim_id=CLAIM_ID_1,
        order_location=order_location,
    )
    cargo_pg.create_claim(
        dispatch_id=dispatch_2.dispatch_id,
        claim_id=CLAIM_ID_2,
        claim_status=other_claim_status,
        order_location=order_location,
    )

    cargo.set_data(
        items=cargo.convert_items(dispatch_1.order.items),
        status='pickuped',
        delivered_eta_ts=DELIVERY_ETA_TS,
        courier_name='test_courier_name',
    )
    cargo.add_performer(
        claim_id=CLAIM_ID_2,
        eats_profile_id=COURIER_ID_0,
        driver_id=DRIVER_ID_0,
        park_id=PARK_ID_0,
    )
    cargo.add_performer(
        claim_id=CLAIM_ID_1,
        eats_profile_id=COURIER_ID_0,
        driver_id=DRIVER_ID_0,
        park_id=PARK_ID_0,
    )

    request = {'dispatch_id': dispatch_1.dispatch_id}

    mocked_time.sleep(60)
    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/status', request,
    )
    assert response.status_code == 200
    json = response.json()
    assert json['status_meta'] is not None
    cargo_status_meta = json['status_meta']['cargo_dispatch']
    assert cargo_status_meta is not None
    assert cargo_status_meta['batch_order_num'] == batch_order_num
    assert cargo_status_meta['dispatch_in_batch'] is True
    assert cargo.times_external_info_called() == 1


@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    ['cargo_status'],
    [
        ['failed'],
        ['cancelled_by_taxi'],
        ['returning'],
        ['performer_not_found'],
        ['return_arrived'],
        ['ready_for_return_confirmation'],
        ['returned'],
        ['returned_finish'],
    ],
)
async def test_status_returns_correct_failure_reason_type(
        taxi_grocery_dispatch,
        cargo,
        cargo_status,
        grocery_dispatch_pg,
        cargo_pg,
):
    dispatch = grocery_dispatch_pg.create_dispatch(
        dispatch_name=DISPATCH_TYPE, status='scheduled',
    )
    claim_model = cargo_pg.create_claim(
        dispatch_id=dispatch.dispatch_id, claim_id=CLAIM_ID_1,
    )
    cargo.set_data(
        items=cargo.convert_items(dispatch.order.items), status=cargo_status,
    )

    request = {'dispatch_id': dispatch.dispatch_id}

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/status', request,
    )
    body = response.json()
    assert response.status_code == 200
    assert body['failure_reason_type'] == cargo_status
    assert claim_model.claim_version == 1


async def test_empty_failure_reason_type(
        taxi_grocery_dispatch, grocery_dispatch_pg,
):
    dispatch = grocery_dispatch_pg.create_dispatch(
        dispatch_name=DISPATCH_TYPE, status='idle',
    )
    request = {'dispatch_id': dispatch.dispatch_id}
    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/status', request,
    )
    body = response.json()
    assert response.status_code == 200
    assert 'failure_reason_type' not in body


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
    dispatch_status = 'scheduled'
    dispatch = grocery_dispatch_pg.create_dispatch(
        dispatch_name=DISPATCH_TYPE, status=dispatch_status,
    )
    cargo_pg.create_claim(
        dispatch_id=dispatch.dispatch_id, claim_id=CLAIM_ID_1,
    )
    cargo.set_data(
        items=cargo.convert_items(dispatch.order.items),
        delivered_eta_ts=DELIVERY_ETA_TS,
        cargo_info_error_code=cargo_error_code,
        cargo_info_timeout=timeout,
    )

    request = {'dispatch_id': dispatch.dispatch_id}

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/status', request,
    )

    assert response.status_code == 200

    response_body = response.json()
    assert response_body['dispatch_id'] == dispatch.dispatch_id
    assert response_body['order_id'] == dispatch.order_id
    assert response_body['status'] == dispatch_status
    assert response_body['dispatch_type'] == DISPATCH_TYPE


@pytest.mark.now(const.NOW)
@configs.DISPATCH_CLAIM_CONFIG
@configs.DISPATCH_GENERAL_CONFIG
@configs.DISPATCH_PRIORITY_CONFIG
@configs.CARGO_AUTH_TOKEN_CONFIG
@configs.MODELER_DECISION_CONFIG_DISABLED
async def test_status_after_create(
        taxi_grocery_dispatch,
        pgsql,
        mockserver,
        yamaps_local,
        personal,
        cargo,
        experiments3,
        grocery_supply,
        cargo_pg,
):
    first_point = copy.deepcopy(models.FIRST_POINT)
    first_point.comment = None

    cargo.check_request(
        route_points=[first_point, models.CLIENT_POINT, models.RETURN_POINT],
        items=cargo.convert_items(const.CREATE_REQUEST_DATA['items'])
        + [models.FAKE_ITEM],
        authorization='Bearer CCC123',
    )

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/create', const.CREATE_REQUEST_DATA,
    )

    assert response.status_code == 200
    assert cargo.times_create_accepted_called() == 1

    response1 = response.json()

    assert (
        response1['status_meta']['cargo_dispatch']['dispatch_delivery_type']
        == 'courier'
    )

    cargo.set_data(courier_name='test_courier_name')
    cargo.add_performer(
        claim_id=CLAIM_ID_1,
        eats_profile_id=COURIER_ID_0,
        driver_id=DRIVER_ID_0,
        park_id=PARK_ID_0,
    )

    request = {'dispatch_id': response1['dispatch_id']}

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/status', request,
    )

    assert response.status_code == 200
    response1 = response.json()

    assert (
        response1['status_meta']['cargo_dispatch']['dispatch_delivery_type']
        == 'courier'
    )


@pytest.mark.now(NOW)
@configs.MODELER_DECISION_CONFIG_DISABLED
async def test_no_performer(
        taxi_grocery_dispatch,
        mocked_time,
        cargo,
        grocery_dispatch_pg,
        cargo_pg,
):
    dispatch_info = grocery_dispatch_pg.create_dispatch(
        dispatch_name=DISPATCH_TYPE, status='scheduled',
    )
    claim_model = cargo_pg.create_claim(
        dispatch_id=dispatch_info.dispatch_id, claim_id=CLAIM_ID_1,
    )

    cargo.set_data(
        items=cargo.convert_items(dispatch_info.order.items),
        delivered_eta_ts=DELIVERY_ETA_TS,
        version=2,
    )

    request = {'dispatch_id': dispatch_info.dispatch_id}

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/status', request,
    )
    assert response.status_code == 200
    assert 'performer_info' not in response.json()
    assert cargo.times_external_info_called() == 0
    assert claim_model.claim_version == 2


@configs.MODELER_DECISION_CONFIG_DISABLED
async def test_reschedule_status_meta(
        taxi_grocery_dispatch, test_dummy_dispatch_cfg, pgsql, stq, stq_runner,
):
    depot_id = const.DEPOT_ID

    order = {
        'order_id': 'order_id',
        'short_order_id': 'shor_order_id',
        'depot_id': depot_id,
        'location': {'lon': 35.5, 'lat': 55.6},
        'zone_type': 'pedestrian',
        'created_at': '2020-10-05T16:28:00+00:00',
        'max_eta': 900,
        'items': [
            {
                'item_id': 'item_id_1',
                'title': 'some product',
                'price': '12.99',
                'currency': 'RUB',
                'quantity': '1',
            },
        ],
        'user_locale': 'ru',
        'personal_phone_id': 'personal_phone_id_1',
    }

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/create', json=order,
    )
    assert response.status_code == 200
    dispatch_id = response.json()['dispatch_id']
    assert (
        response.json()['status_meta'] == {}
    )  # TODO check if filling this after create is bug or not

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/status', json={'dispatch_id': dispatch_id},
    )
    assert response.status_code == 200
    assert (
        response.json()['status_meta']['_test']['status'] == 'order_assembled'
    )

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v2/manual/reschedule',
        json={
            'order_id': 'order_id',
            'idempotency_token': 'token',
            'options': {},
        },
    )
    assert response.status_code == 200

    assert stq.grocery_dispatch_reschedule_executor.times_called == 1

    task_id = f'{dispatch_id}_token'
    await stq_runner.grocery_dispatch_reschedule_executor.call(
        task_id=task_id,
        kwargs={'dispatch_id': dispatch_id, 'idempotency_token': 'token'},
    )

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/status', json={'dispatch_id': dispatch_id},
    )

    assert response.status_code == 200
    assert (
        response.json()['status_meta']['_test']['status'] == 'order_assembled'
    )


@pytest.mark.now(const.NOW)
@configs.DISPATCH_CLAIM_CONFIG
@configs.DISPATCH_GENERAL_CONFIG
@configs.DISPATCH_PRIORITY_CONFIG
@configs.DISPATCH_COMMENT_CONFIG
async def test_stq_continue_order_market_slot(
        taxi_grocery_dispatch,
        pgsql,
        mockserver,
        yamaps_local,
        personal,
        cargo,
        experiments3,
        grocery_supply,
        grocery_dispatch_pg,
        stq,
        cargo_pg,
):
    dispatch = grocery_dispatch_pg.create_dispatch(
        dispatch_name='cargo_sync',
        status='matching',
        order=OrderInfo(market_slot=TimeSlot()),
    )
    cargo_pg.create_claim(
        dispatch_id=dispatch.dispatch_id, claim_id=CLAIM_ID_1,
    )

    cargo.set_data(
        items=cargo.convert_items(dispatch.order.items),
        status='performer_found',
        delivered_eta_ts=DELIVERY_ETA_TS,
        courier_name='test_courier_name',
    )
    cargo.add_performer(
        claim_id=CLAIM_ID_1,
        eats_profile_id=COURIER_ID_0,
        driver_id=DRIVER_ID_0,
        park_id=PARK_ID_0,
    )

    request = {'dispatch_id': dispatch.dispatch_id}

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/status', request,
    )
    assert response.status_code == 200

    assert stq.grocery_dispatch_continue_order.times_called == 1
