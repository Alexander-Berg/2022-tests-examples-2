# pylint: disable=C5521

import datetime

import pytest

from tests_grocery_order_log import models
from tests_grocery_order_log.helpers_retrieve import (
    CONFIG_CURRENCY_FORMATTING_RULES,
)
from tests_grocery_order_log.helpers_retrieve import create_cart_items
from tests_grocery_order_log.helpers_retrieve import CURSOR_DATA
from tests_grocery_order_log.helpers_retrieve import fetch_delivery_cost
from tests_grocery_order_log.helpers_retrieve import from_template


def _get_destination(response):
    return response['orders'][0]['destinations'][0]


@CONFIG_CURRENCY_FORMATTING_RULES
@pytest.mark.translations(
    grocery_order_log={
        'delivery_tin': {'ru': 'ИНН лавки'},
        'address': {'ru': 'address'},
    },
)
@CURSOR_DATA
@pytest.mark.parametrize('personal_error_code', (None, '404'))
@pytest.mark.experiments3(filename='restore_deep_links.json')
async def test_orders_retrieve_from_pg_basic(
        taxi_grocery_order_log,
        load_json,
        pgsql,
        cursor_data,
        personal,
        personal_error_code,
):
    orders_info = load_json('grocery_orders_response.json')
    if personal_error_code is not None:
        orders_info['orders'][0]['legal_entities'][0]['additional_properties'][
            1
        ]['value'] = models.DELIVERY_TIN
    personal.error_code = personal_error_code
    personal.tin = models.DELIVERY_TIN
    personal.personal_tin_id = models.DELIVERY_TIN_ID

    yandex_uid = 'test-uid'

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
            order_state='closed',
            cart_items=create_cart_items(calculation['addends']),
            delivery_cost=fetch_delivery_cost(calculation['addends']),
            currency=calculation['currency_code'],
            cart_total_discount=from_template(calculation['discount']),
            cart_total_price=from_template(calculation['final_cost']),
            refund=from_template(calculation['refund']),
            yandex_uid=yandex_uid,
            geo_id='test_geo_id',
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
            'bound_yandex_uids': ['test-uid-1', 'test-uid-1'],
        },
        'include_service_metadata': True,
    }
    response = await taxi_grocery_order_log.post(
        '/internal/orders/v1/retrieve',
        headers={
            'Accept-Language': 'ru-RU',
            'X-Request-Application': 'app_name=lavka_iphone',
        },
        json=request_json,
    )
    assert response.status_code == 200

    assert response.json() == load_json('expected_response.json')


@pytest.mark.translations(
    grocery_order_log={
        'delivery_courier_full_name': {'en': 'delivery_courier_full_name'},
        'delivery_organization_name': {'en': 'delivery_organization_name'},
        'delivery_tin': {'en': 'delivery_tin'},
        'delivery_legal_address': {'en': 'delivery_legal_address'},
        'depot': {'en': 'depot'},
        'address': {'en': 'address'},
        'tin': {'en': 'tin'},
    },
)
@pytest.mark.parametrize(
    'country_iso3, is_self_employed',
    [('ISR', False), ('RUS', False), ('RUS', True), (None, False)],
)
async def test_orders_retrieve_legal_entities(
        taxi_grocery_order_log,
        load_json,
        pgsql,
        country_iso3,
        is_self_employed,
):
    orders_info = load_json('grocery_orders_response.json')

    delivery_company = {
        'title': 'delivery_organization_name',
        'value': 'OOO Romashka',
    }
    delivery_legal_address = {
        'title': 'delivery_legal_address',
        'value': 'Moscow city',
    }
    delivery_courier = {
        'title': 'delivery_courier_full_name',
        'value': 'Ivan Ivanovich',
    }
    orders_info['orders'][0]['legal_entities'][0][
        'additional_properties'
    ].append(delivery_courier)
    if not is_self_employed:
        orders_info['orders'][0]['legal_entities'][0][
            'additional_properties'
        ].append(delivery_company)
        orders_info['orders'][0]['legal_entities'][0][
            'additional_properties'
        ].append(delivery_legal_address)

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
            order_state='closed',
            cart_items=create_cart_items(calculation['addends']),
            delivery_cost=fetch_delivery_cost(calculation['addends']),
            currency=calculation['currency_code'],
            cart_total_discount=from_template(calculation['discount']),
            cart_total_price=from_template(calculation['final_cost']),
            refund=from_template(calculation['refund']),
            yandex_uid='test-uid',
            geo_id='test_geo_id',
            country_iso3=country_iso3,
        )
        order_log.update_db()

        order_log.update()
        assert order_log.yandex_uid == 'test-uid'

    request_json = {
        'range': {'order_id': '5c44b80d-e583-4d0a-a74a-f53cf070b4f6'},
        'user_identity': {
            'yandex_uid': 'test-uid',
            'bound_yandex_uids': ['test-uid-1', 'test-uid-1'],
        },
        'include_service_metadata': True,
    }
    response = await taxi_grocery_order_log.post(
        '/internal/orders/v1/retrieve',
        headers={
            'Accept-Language': 'en',
            'X-Request-Application': 'app_brand=yataxi',
        },
        json=request_json,
    )

    assert response.status_code == 200
    order = response.json()['orders'][0]
    if country_iso3 is None or country_iso3 == 'RUS':
        expected_legal_info = [
            {
                'additional_properties': [
                    {'title': 'delivery_tin', 'value': '7707083893'},
                    delivery_courier,
                ],
                'title': 'Delivery',
                'type': 'delivery_service',
            },
            {
                'additional_properties': [
                    {'title': 'address', 'value': 'Red Rose'},
                    {'title': 'tin', 'value': '12345678'},
                ],
                'title': 'depot',
                'type': 'restaurant',
            },
        ]
        if not is_self_employed:
            expected_legal_info[0]['additional_properties'].append(
                delivery_company,
            )
            expected_legal_info[0]['additional_properties'].append(
                delivery_legal_address,
            )
        assert order['legal_entities'] == expected_legal_info
    else:
        assert order['legal_entities'] == [
            {
                'additional_properties': [delivery_courier],
                'title': 'Delivery',
                'type': 'delivery_service',
            },
            {
                'additional_properties': [
                    {'title': 'address', 'value': 'Red Rose'},
                ],
                'title': 'depot',
                'type': 'restaurant',
            },
        ]


@CURSOR_DATA
@pytest.mark.parametrize(
    'order_state,status',
    [
        ('created', 'created'),
        ('closed', 'closed'),
        ('canceled', 'closed'),
        ('returned', 'closed'),
        ('assembling', 'created'),
        ('delivering', 'created'),
    ],
)
async def test_orders_retrieve_from_pg_states(
        taxi_grocery_order_log,
        load_json,
        pgsql,
        cursor_data,
        order_state,
        status,
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
            delivery_cost=fetch_delivery_cost(calculation['addends']),
            currency=calculation['currency_code'],
            cart_total_discount=from_template(calculation['discount']),
            cart_total_price=from_template(calculation['final_cost']),
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
        'include_service_metadata': True,
    }
    response = await taxi_grocery_order_log.post(
        '/internal/orders/v1/retrieve',
        headers={
            'Accept-Language': 'ru-RU',
            'X-Request-Application': 'app_brand=yataxi',
        },
        json=request_json,
    )

    assert response.status_code == 200
    assert response.json()['orders'][0]['status'] == status


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
        'include_service_metadata': False,
    }
    response = await taxi_grocery_order_log.post(
        '/internal/orders/v1/retrieve',
        headers={
            'Accept-Language': 'ru',
            'X-Request-Application': 'app_brand=yataxi',
        },
        json=request_json,
    )
    assert response.status_code == 200
    assert len(response.json()['orders']) == expected
    assert 'service_metadata' not in response.json()


@pytest.mark.experiments3(
    is_config=True,
    name='grocery_orders_source_availability',
    consumers=['grocery-order-log/retrieve'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'available_sources': ['yango', 'web']},
)
@pytest.mark.experiments3(filename='restore_deep_links.json')
@CONFIG_CURRENCY_FORMATTING_RULES
@pytest.mark.translations(
    grocery_order_log={
        'delivery_tin': {'ru': 'ИНН лавки'},
        'address': {'ru': 'address'},
    },
)
@CURSOR_DATA
@pytest.mark.parametrize('order_source', ['yango', 'market', None])
async def test_filter_orders_by_source(
        taxi_grocery_order_log,
        load_json,
        pgsql,
        cursor_data,
        personal,
        order_source,
):
    orders_info = load_json('grocery_orders_response.json')
    personal.tin = models.DELIVERY_TIN
    personal.personal_tin_id = models.DELIVERY_TIN_ID

    yandex_uid = 'test-uid'

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
            order_state='closed',
            cart_items=create_cart_items(calculation['addends']),
            delivery_cost=fetch_delivery_cost(calculation['addends']),
            currency=calculation['currency_code'],
            cart_total_discount=from_template(calculation['discount']),
            cart_total_price=from_template(calculation['final_cost']),
            refund=from_template(calculation['refund']),
            yandex_uid=yandex_uid,
            geo_id='test_geo_id',
            order_source=order_source,
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
            'bound_yandex_uids': ['test-uid-1', 'test-uid-1'],
        },
        'include_service_metadata': True,
    }
    response = await taxi_grocery_order_log.post(
        '/internal/orders/v1/retrieve',
        headers={
            'Accept-Language': 'ru-RU',
            'X-Request-Application': 'app_name=lavka_iphone',
        },
        json=request_json,
    )
    assert response.status_code in [200, 404]

    if order_source != 'market':
        assert response.json() == load_json('expected_response.json')
    elif response.status_code == 200:
        assert response.json() == {'orders': []}


@CONFIG_CURRENCY_FORMATTING_RULES
@pytest.mark.translations(
    grocery_order_log={
        'delivery_tin': {'ru': 'ИНН лавки'},
        'address': {'ru': 'address'},
    },
)
@CURSOR_DATA
@pytest.mark.parametrize(
    'locale',
    [pytest.param('ru', id='ru locale'), pytest.param('fa', id='fa locale')],
)
async def test_orders_retrieve_localize_destination(
        taxi_grocery_order_log, load_json, pgsql, cursor_data, locale,
):
    orders_info = load_json('grocery_orders_response.json')

    yandex_uid = 'test-uid'

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
            order_state='closed',
            cart_items=create_cart_items(calculation['addends']),
            delivery_cost=fetch_delivery_cost(calculation['addends']),
            currency=calculation['currency_code'],
            cart_total_discount=from_template(calculation['discount']),
            cart_total_price=from_template(calculation['final_cost']),
            refund=from_template(calculation['refund']),
            yandex_uid=yandex_uid,
            geo_id='test_geo_id',
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
            'bound_yandex_uids': ['test-uid-1', 'test-uid-1'],
        },
        'include_service_metadata': True,
    }
    response = await taxi_grocery_order_log.post(
        '/internal/orders/v1/retrieve',
        headers={
            'Accept-Language': locale,
            'X-Request-Application': 'app_name=lavka_iphone',
        },
        json=request_json,
    )
    assert response.status_code == 200

    if locale == 'fa':
        expected_destination = _get_destination(
            load_json('expected_response_locale.json'),
        )
        assert _get_destination(response.json()) == expected_destination
    else:
        expected_destination = _get_destination(
            load_json('expected_response.json'),
        )
        assert _get_destination(response.json()) == expected_destination
