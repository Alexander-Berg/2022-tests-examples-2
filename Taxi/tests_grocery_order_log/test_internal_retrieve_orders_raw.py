# pylint: disable=C5521

import datetime

import pytest

from tests_grocery_order_log import helpers
from tests_grocery_order_log import models
from tests_grocery_order_log.helpers_retrieve import COLD_STORAGE_CURSOR_DATA
from tests_grocery_order_log.helpers_retrieve import create_cart_items
from tests_grocery_order_log.helpers_retrieve import CURSOR_DATA
from tests_grocery_order_log.helpers_retrieve import fetch_delivery_cost
from tests_grocery_order_log.helpers_retrieve import from_template


@CURSOR_DATA
async def test_orders_retrieve_from_pg_basic(
        taxi_grocery_order_log,
        grocery_cold_storage,
        load_json,
        pgsql,
        cursor_data,
):
    orders_info = load_json('grocery_orders_response.json')

    yandex_uid = 'test-uid'
    bound_uid = 'test-uid-1'
    for order_info in orders_info['orders']:
        created_date = datetime.datetime.fromisoformat(
            order_info['created_at'],
        )

        finished_date = datetime.datetime.fromisoformat(
            order_info['closed_at'],
        )
        calculation = order_info['calculation']
        cart_items = create_cart_items(calculation['addends'])
        order_log = models.OrderLog(
            pgsql=pgsql,
            order_id=order_info['order_id'],
            short_order_id=order_info['short_order_id'],
            order_created_date=created_date,
            order_finished_date=finished_date,
            cart_id='cart_id',
            courier=order_info['contact']['courier']['name'],
            destination=order_info['destination'],
            legal_entities=order_info['legal_entities'],
            receipts=order_info['receipts'],
            order_state='closed',
            cart_items=cart_items,
            currency=calculation['currency_code'],
            cart_total_price=from_template(calculation['final_cost']),
            cashback_gain=calculation.get('cashback_gain'),
            cashback_charge=calculation.get('cashback_charge'),
            cart_total_discount=from_template(calculation['discount']),
            delivery_cost=fetch_delivery_cost(calculation['addends']),
            refund=from_template(calculation['refund']),
            yandex_uid=yandex_uid,
            geo_id='test_geo_id',
            country_iso3='RUS',
        )
        order_log.update_db()

        order_log_index = models.OrderLogIndex(
            pgsql=pgsql,
            order_id=order_info['order_id'],
            cart_id='cart_id',
            order_created_date=created_date,
            yandex_uid=yandex_uid,
        )
        order_log_index.update_db()

        order_log.update()
        assert order_log.yandex_uid == yandex_uid

    request_json = {
        'range': cursor_data,
        'user_identity': {
            'yandex_uid': yandex_uid,
            'bound_yandex_uids': [bound_uid, 'test-uid-1'],
        },
    }
    response = await taxi_grocery_order_log.post(
        '/internal/orders/v1/retrieve-raw',
        headers={'X-Request-Application': 'app_brand=yataxi'},
        json=request_json,
    )

    assert response.status_code == 200

    assert response.json() == load_json('expected_response.json')


@CURSOR_DATA
@pytest.mark.parametrize(
    'order_state,status_raw',
    [
        ('created', 'created'),
        ('closed', 'closed'),
        ('canceled', 'canceled'),
        ('returned', 'closed'),
        ('assembling', 'assembling'),
        ('delivering', 'delivering'),
    ],
)
async def test_orders_retrieve_from_pg_states(
        taxi_grocery_order_log,
        load_json,
        pgsql,
        cursor_data,
        order_state,
        status_raw,
):
    orders_info = load_json('grocery_orders_response.json')

    for order_info in orders_info['orders']:
        created_date = datetime.datetime.fromisoformat(
            order_info['created_at'],
        )
        finished_date = datetime.datetime.fromisoformat(
            order_info['closed_at'],
        )
        calculation = order_info['calculation']
        order_log = models.OrderLog(
            pgsql=pgsql,
            order_id=order_info['order_id'],
            order_created_date=created_date,
            order_finished_date=finished_date,
            cart_id='cart_id',
            courier=order_info['contact']['courier']['name'],
            destination=order_info['destination'],
            legal_entities=order_info['legal_entities'],
            receipts=order_info['receipts'],
            order_state=order_state,
            cart_items=create_cart_items(calculation['addends']),
            currency=calculation['currency_code'],
            cart_total_price=from_template(calculation['final_cost']),
            cashback_gain=calculation.get('cashback_gain'),
            cashback_charge=calculation.get('cashback_charge'),
            cart_total_discount=from_template(calculation['discount']),
            delivery_cost=fetch_delivery_cost(calculation['addends']),
            refund=from_template(calculation['refund']),
            yandex_uid='test-uid',
            geo_id='test_geo_id',
            country_iso3='RUS',
        )
        order_log.update_db()

        order_log_index = models.OrderLogIndex(
            pgsql=pgsql,
            order_id=order_info['order_id'],
            cart_id='cart_id',
            order_created_date=created_date,
            yandex_uid='test-uid',
        )
        order_log_index.update_db()

        order_log.update()
        assert order_log.yandex_uid == 'test-uid'

    request_json = {
        'range': cursor_data,
        'user_identity': {
            'yandex_uid': 'test-uid',
            'bound_yandex_uids': ['test-uid-1', 'test-uid-1'],
        },
    }
    response = await taxi_grocery_order_log.post(
        '/internal/orders/v1/retrieve-raw',
        headers={'X-Request-Application': 'app_brand=yataxi'},
        json=request_json,
    )

    assert response.status_code == 200
    assert response.json()['orders'][0]['status'] == status_raw


CREATED_1 = datetime.datetime(
    year=2020, month=1, day=10, tzinfo=datetime.timezone.utc,
)
CREATED_2 = datetime.datetime(
    year=2020, month=2, day=10, tzinfo=datetime.timezone.utc,
)
CREATED_3 = datetime.datetime(
    year=2020, month=3, day=10, tzinfo=datetime.timezone.utc,
)
DATES = [CREATED_1, CREATED_2, CREATED_3]


@pytest.mark.parametrize(
    'count,older_than_index,expected',
    [(3, None, 3), (2, 2, 2), (2, 1, 1), (3, 0, 0)],
)
async def test_bulk_retrieve_from_pg(
        taxi_grocery_order_log, pgsql, count, older_than_index, expected,
):
    order_ids = []
    for i, created in enumerate(DATES):
        order_log = models.OrderLog(
            pgsql,
            order_id='order_' + str(i),
            order_created_date=created,
            yandex_uid='test-uid-1',
        )
        order_log_info = models.OrderLogIndex(
            pgsql,
            order_id='order_' + str(i),
            order_created_date=created,
            yandex_uid='test-uid-1',
        )
        order_ids.append(order_log.order_id)
        order_log.update_db()
        order_log_info.update_db()
    cursor_data = {'count': count}
    if older_than_index is not None:
        cursor_data['older_than'] = order_ids[older_than_index]
    request_json = {
        'range': cursor_data,
        'user_identity': {
            'yandex_uid': 'test-uid',
            'bound_yandex_uids': ['test-uid-1', 'test-uid-1'],
        },
    }
    response = await taxi_grocery_order_log.post(
        '/internal/orders/v1/retrieve-raw',
        headers={'X-Request-Application': 'app_brand=yataxi'},
        json=request_json,
    )
    assert response.status_code == 200
    if expected > 0:
        assert len(response.json()['orders']) == expected


@pytest.mark.parametrize(
    'order_id', [pytest.param('some_id', id='non grocery id')],
)
async def test_not_found_200(
        taxi_grocery_order_log, grocery_cold_storage, mockserver, order_id,
):
    request_json = {
        'range': {'order_id': order_id},
        'user_identity': {
            'yandex_uid': 'test-uid',
            'bound_yandex_uids': ['test-uid-1', 'test-uid-1'],
        },
    }

    response = await taxi_grocery_order_log.post(
        '/internal/orders/v1/retrieve-raw',
        headers={'X-Request-Application': 'app_brand=yataxi'},
        json=request_json,
    )
    assert response.status_code == 200


@pytest.mark.now('2021-01-21T12:00:00+03:00')
async def test_retrieve_no_created_date(
        taxi_grocery_order_log, load_json, pgsql, now,
):

    orders_info = load_json('grocery_orders_response.json')
    order_state = 'created'

    for order_info in orders_info['orders']:
        calculation = order_info['calculation']
        order_log = models.OrderLog(
            pgsql=pgsql,
            order_id=order_info['order_id'],
            order_created_date=None,
            order_finished_date=None,
            cart_id='cart_id',
            courier=order_info['contact']['courier']['name'],
            destination=order_info['destination'],
            legal_entities=order_info['legal_entities'],
            receipts=order_info['receipts'],
            order_state=order_state,
            cart_items=create_cart_items(calculation['addends']),
            currency=calculation['currency_code'],
            cart_total_price=from_template(calculation['final_cost']),
            cashback_gain=calculation.get('cashback_gain'),
            cashback_charge=calculation.get('cashback_charge'),
            cart_total_discount=from_template(calculation['discount']),
            delivery_cost=fetch_delivery_cost(calculation['addends']),
            refund=from_template(calculation['refund']),
            yandex_uid='test-uid',
            geo_id='test_geo_id',
            country_iso3='RUS',
        )
        order_log.update_db()

        order_log_index = models.OrderLogIndex(
            pgsql=pgsql,
            order_id=order_info['order_id'],
            cart_id='cart_id',
            yandex_uid='test-uid',
        )
        order_log_index.update_db()

        order_log.update()
        assert order_log.yandex_uid == 'test-uid'
        assert order_log.order_id == order_info['order_id']
        assert order_log.order_created_date is None

    request_json = {
        'range': {'count': 1},
        'user_identity': {
            'yandex_uid': 'test-uid',
            'bound_yandex_uids': ['test-uid-1', 'test-uid-1'],
        },
    }

    response = await taxi_grocery_order_log.post(
        '/internal/orders/v1/retrieve-raw',
        headers={'X-Request-Application': 'app_brand=yataxi'},
        json=request_json,
    )
    assert response.status_code == 200
    assert (
        response.json()['orders'][0]['created_at']
        == now.isoformat() + '+00:00'
    )


@COLD_STORAGE_CURSOR_DATA
async def test_orders_retrieve_from_cold_storage_basic(
        taxi_grocery_order_log,
        grocery_cold_storage,
        load_json,
        pgsql,
        cursor_data,
):
    order_id = 'cold-grocery'
    yandex_uid = 'test-uid'
    created_date = '2020-08-11T00:00:00+00:00'

    helpers.add_cold_storage_and_index(
        grocery_cold_storage, yandex_uid, created_date, order_id, pgsql,
    )

    request_json = {
        'range': cursor_data,
        'user_identity': {
            'yandex_uid': yandex_uid,
            'bound_yandex_uids': ['test-uid-1', 'test-uid-1'],
        },
    }
    response = await taxi_grocery_order_log.post(
        '/internal/orders/v1/retrieve-raw',
        headers={'X-Request-Application': 'app_brand=yataxi'},
        json=request_json,
    )

    assert response.status_code == 200
    assert response.json() == load_json('expected_cold_response.json')


@COLD_STORAGE_CURSOR_DATA
@pytest.mark.config(GROCERY_ORDER_LOG_USE_COLD_STORAGE=False)
async def test_orders_retrieve_from_cold_storage_off_by_config(
        taxi_grocery_order_log,
        grocery_cold_storage,
        load_json,
        pgsql,
        cursor_data,
):
    order_id = 'cold-grocery'
    yandex_uid = 'test-uid'
    created_date = '2020-08-11T00:00:00+00:00'

    helpers.add_cold_storage_and_index(
        grocery_cold_storage, yandex_uid, created_date, order_id, pgsql,
    )

    request_json = {
        'range': cursor_data,
        'user_identity': {
            'yandex_uid': yandex_uid,
            'bound_yandex_uids': ['test-uid-1', 'test-uid-1'],
        },
    }
    response = await taxi_grocery_order_log.post(
        '/internal/orders/v1/retrieve-raw',
        headers={'X-Request-Application': 'app_brand=yataxi'},
        json=request_json,
    )

    assert response.status_code == 200
    assert response.json() == {'orders': []}
