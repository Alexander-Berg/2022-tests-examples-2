import json

import pytest


METHOD = 'driver/requestconfirm/fine/cost?db=999&session=qwerty'
SQL_INSERT_ORDER_TEMPLATE = (
    'INSERT INTO orders_0 '
    '(park_id, id, number, driver_id, rule_type_id, date_create, date_booking)'
    ' VALUES (\'999\', \'order{num}\', {num}, \'888\', \'{rule_type}\', '
    'now(), now())'
)


@pytest.mark.redis_store(
    [
        'hset',
        'RuleType:Items:999',
        'rule1',
        json.dumps({'Name': 'Rule', 'CancelCost': 100.99}),
    ],
)
@pytest.mark.sql(
    'taximeter', SQL_INSERT_ORDER_TEMPLATE.format(num=1, rule_type='rule1'),
)
def test_regular_rule_type(taxi_driver_protocol, driver_authorizer_service):
    driver_authorizer_service.set_session('999', 'qwerty', '888')

    response = taxi_driver_protocol.post(METHOD, params={'order': 'order1'})
    assert response.status_code == 200
    response_obj = response.json()
    assert abs(response_obj['sum'] - 100.99) < 1e-6


@pytest.mark.redis_store(
    [
        'hmset',
        'RuleType:Items:999',
        {
            'yandexrule1': json.dumps({'Name': 'Яндекс'}),
            'yandexrule2': json.dumps(
                {'Name': 'Яндекс.безналичный', 'CancelCost': 10.0},
            ),
            'yandexrule3': json.dumps(
                {'Name': 'яндекс.безналичный', 'CancelCost': 999.0},
            ),
        },
    ],
)
@pytest.mark.sql(
    'taximeter',
    SQL_INSERT_ORDER_TEMPLATE.format(num=1, rule_type='yandexrule1'),
    SQL_INSERT_ORDER_TEMPLATE.format(num=2, rule_type='yandexrule2'),
    SQL_INSERT_ORDER_TEMPLATE.format(num=3, rule_type='yandexrule3'),
)
def test_yandex_rule_type(taxi_driver_protocol, driver_authorizer_service):
    driver_authorizer_service.set_session('999', 'qwerty', '888')

    response = taxi_driver_protocol.post(METHOD, params={'order': 'order1'})
    assert response.status_code == 200
    response_obj = response.json()
    assert response_obj['sum'] == 0.0

    response = taxi_driver_protocol.post(METHOD, params={'order': 'order2'})
    assert response.status_code == 200
    response_obj = response.json()
    assert response_obj['sum'] == 0.0

    response = taxi_driver_protocol.post(METHOD, params={'order': 'order3'})
    assert response.status_code == 200
    response_obj = response.json()
    assert response_obj['sum'] == 0.0


@pytest.mark.sql(
    'taximeter', SQL_INSERT_ORDER_TEMPLATE.format(num=1, rule_type='rule1'),
)
def test_missing_order(taxi_driver_protocol, driver_authorizer_service):
    driver_authorizer_service.set_session('999', 'qwerty', '888')

    response = taxi_driver_protocol.post(
        METHOD, params={'order': 'nonexistent'},
    )
    assert response.status_code == 404


@pytest.mark.redis_store(
    [
        'hmset',
        'RuleType:Items:999',
        {'yandexrule1': json.dumps({'Name': 'Яндекс'})},
    ],
)
@pytest.mark.sql(
    'taximeter',
    SQL_INSERT_ORDER_TEMPLATE.format(num=1, rule_type='nonexistent'),
)
def test_missing_rule_type(taxi_driver_protocol, driver_authorizer_service):
    driver_authorizer_service.set_session('999', 'qwerty', '888')

    response = taxi_driver_protocol.post(METHOD, params={'order': 'order1'})
    assert response.status_code == 200
    response_obj = response.json()
    assert response_obj['sum'] == 0.0


@pytest.mark.redis_store(
    [
        'hmset',
        'RuleType:Items:999',
        {
            'otherrule1': json.dumps(
                {'Name': 'Other rule', 'CancelCost': 1.0},
            ),
            'otherrule2': json.dumps(
                {'Name': 'Другое правило', 'CancelCost': 2.0},
            ),
            'nocancelcostrule': json.dumps({'Name': 'No CancelCost'}),
            'yandexrule': json.dumps({'Name': 'Яндекс.безналичный'}),
        },
    ],
)
@pytest.mark.sql(
    'taximeter',
    SQL_INSERT_ORDER_TEMPLATE.format(num=1, rule_type='otherrule1'),
    SQL_INSERT_ORDER_TEMPLATE.format(num=2, rule_type='otherrule2'),
    SQL_INSERT_ORDER_TEMPLATE.format(num=3, rule_type='nocancelcostrule'),
    SQL_INSERT_ORDER_TEMPLATE.format(num=4, rule_type='yandexrule'),
)
def test_smoke(taxi_driver_protocol, driver_authorizer_service):
    driver_authorizer_service.set_session('999', 'qwerty', '888')

    response = taxi_driver_protocol.post(METHOD, params={'order': 'order1'})
    assert response.status_code == 200
    response_obj = response.json()
    assert abs(response_obj['sum'] - 1.0) < 1e-6

    response = taxi_driver_protocol.post(METHOD, params={'order': 'order2'})
    assert response.status_code == 200
    response_obj = response.json()
    assert abs(response_obj['sum'] - 2.0) < 1e-6

    response = taxi_driver_protocol.post(METHOD, params={'order': 'order3'})
    assert response.status_code == 200
    response_obj = response.json()
    assert response_obj['sum'] == 0.0

    response = taxi_driver_protocol.post(METHOD, params={'order': 'order4'})
    assert response.status_code == 200
    response_obj = response.json()
    assert response_obj['sum'] == 0.0
