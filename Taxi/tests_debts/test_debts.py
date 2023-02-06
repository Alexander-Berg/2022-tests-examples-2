import decimal
import http

# pylint: disable=import-error
from metrics_aggregations import helpers as metrics_helpers
import pytest


def get_cursor(pgsql):
    return pgsql['debts'].cursor()


def sql_debt_to_json(res):
    schema = [
        'order_id',
        'order_info',
        'status',
        'yandex_uid',
        'phone_id',
        'brand',
        'created',
        'updated',
        'value',
        'currency',
        'reason_code',
    ]
    json = {}
    for i, elem in enumerate(schema):
        json[elem] = res[i]
    return json


def generate_patch(**kwargs):
    patch = {
        'patch_time': kwargs.get('patch_time', '2019-01-01T00:00:00.0Z'),
        'action': kwargs.get('action', 'set_debt'),
        'order_info': kwargs.get('order_info', {}),
        'yandex_uid': kwargs.get('yandex_uid', 'yandex_uid_1'),
        'phone_id': kwargs.get('phone_id', 'phone_id_1'),
        'created_at': kwargs.get('created_at', '2018-01-01T00:00:00.0Z'),
        'brand': kwargs.get('brand', 'yataxi'),
    }
    if 'value' in kwargs:
        patch['value'] = kwargs.get('value')
    if 'currency' in kwargs:
        patch['currency'] = kwargs.get('currency')
    if 'reason_code' in kwargs:
        patch['reason_code'] = kwargs.get('reason_code')

    return patch


def get_debts_by_yandex_uid(yandex_uid, pgsql):
    db = get_cursor(pgsql)
    db.execute(
        'select * from debts.taxi_order_debts where yandex_uid=\'{}\''.format(
            yandex_uid,
        ),
    )
    return [sql_debt_to_json(x) for x in db]


async def test_4xx_set_patch(taxi_debts):
    params = {'order_id': 'order_id'}

    patch = generate_patch(currency='RUB')
    response = await taxi_debts.patch('v1/debts', json=patch, params=params)
    assert response.status_code == http.HTTPStatus.BAD_REQUEST

    patch = generate_patch(value='0', currency='RUB')
    response = await taxi_debts.patch('v1/debts', json=patch, params=params)
    assert response.status_code == http.HTTPStatus.BAD_REQUEST

    patch = generate_patch(value='100')
    response = await taxi_debts.patch('v1/debts', json=patch, params=params)
    assert response.status_code == http.HTTPStatus.BAD_REQUEST

    patch = generate_patch(value='100', currency='')
    response = await taxi_debts.patch('v1/debts', json=patch, params=params)
    assert response.status_code == http.HTTPStatus.BAD_REQUEST

    patch = generate_patch(brand='')
    response = await taxi_debts.patch('v1/debts', json=patch, params=params)
    assert response.status_code == http.HTTPStatus.BAD_REQUEST


async def test_4xx_reset_patch(taxi_debts):
    params = {'order_id': 'order_id'}

    patch = generate_patch(action='reset_debt', reason_code='')
    response = await taxi_debts.patch('v1/debts', json=patch, params=params)
    assert response.status_code == http.HTTPStatus.BAD_REQUEST


async def test_debt_set_patch_simple(taxi_debts, pgsql):
    patch = generate_patch(value='300', currency='RUB')
    response = await taxi_debts.patch(
        'v1/debts', json=patch, params={'order_id': 'order_id'},
    )
    assert response.status_code == http.HTTPStatus.OK

    debt = get_debts_by_yandex_uid(patch['yandex_uid'], pgsql)[0]
    assert debt['value'] == decimal.Decimal(patch['value'])
    assert debt['currency'] == patch['currency']
    assert debt['order_id'] == 'order_id'
    assert debt['yandex_uid'] == patch['yandex_uid']
    assert debt['phone_id'] == patch['phone_id']
    assert debt['brand'] == patch['brand']


async def test_debt_set_patch_2_times(taxi_debts, pgsql):
    patch = generate_patch(value='300', currency='RUB')
    response = await taxi_debts.patch(
        'v1/debts', json=patch, params={'order_id': 'order_id'},
    )
    assert response.status_code == http.HTTPStatus.OK

    patch_2 = generate_patch(value='400', currency='EUR')
    response = await taxi_debts.patch(
        'v1/debts', json=patch_2, params={'order_id': 'order_id'},
    )
    assert response.status_code == http.HTTPStatus.OK

    debt = get_debts_by_yandex_uid(patch['yandex_uid'], pgsql)[0]
    assert debt['value'] == decimal.Decimal(patch['value'])
    assert debt['currency'] == patch['currency']
    assert debt['order_id'] == 'order_id'
    assert debt['yandex_uid'] == patch['yandex_uid']
    assert debt['phone_id'] == patch['phone_id']
    assert debt['brand'] == patch['brand']


async def test_debt_reset_patch_simple(taxi_debts, pgsql):
    patch = generate_patch(action='reset_debt', reason_code='moved_to_cash')
    response = await taxi_debts.patch(
        'v1/debts', json=patch, params={'order_id': 'order_id'},
    )
    assert response.status_code == http.HTTPStatus.OK

    debt = get_debts_by_yandex_uid(patch['yandex_uid'], pgsql)[0]
    assert debt['value'] is None
    assert debt['currency'] is None
    assert debt['order_id'] == 'order_id'
    assert debt['yandex_uid'] == patch['yandex_uid']
    assert debt['phone_id'] == patch['phone_id']
    assert debt['status'] == 'nodebt'
    assert debt['reason_code'] == patch['reason_code']
    assert debt['brand'] == patch['brand']


async def test_debt_patch_series(taxi_debts, pgsql):
    patches = [
        generate_patch(action='set_debt', value='300', currency='RUB'),
        generate_patch(
            action='reset_debt',
            reason_code='moved_to_cash',
            patch_time='2019-12-01T00:00:00.0Z',
        ),
        generate_patch(
            action='set_debt',
            value='1',
            currency='EUR',
            patch_time='2018-12-01T00:00:00.0Z',
        ),
    ]

    for patch in patches:
        await taxi_debts.patch(
            'v1/debts', json=patch, params={'order_id': 'order_id'},
        )

    last_patch = patches[1]
    debt = get_debts_by_yandex_uid(last_patch['yandex_uid'], pgsql)[0]

    assert debt['value'] is None
    assert debt['currency'] is None
    assert debt['order_id'] == 'order_id'
    assert debt['status'] == 'nodebt'
    assert debt['reason_code'] == last_patch['reason_code']


@pytest.mark.pgsql('debts', files=['taxi_order_debts.sql'])
async def test_set_patch_existing(taxi_debts, pgsql):
    patch = generate_patch(value='800', currency='EUR')
    response = await taxi_debts.patch(
        'v1/debts', json=patch, params={'order_id': 'order_id_1'},
    )
    assert response.status_code == http.HTTPStatus.OK

    debt = get_debts_by_yandex_uid(patch['yandex_uid'], pgsql)[0]
    assert debt['value'] == decimal.Decimal('800')
    assert debt['currency'] == 'EUR'
    assert debt['status'] == 'debt'
    assert debt['brand'] == 'yataxi'


@pytest.mark.skip(reason='TAXIBACKEND-30325: Fail with postgresql-12')
@pytest.mark.pgsql('debts', files=['taxi_order_debts.sql'])
async def test_reset_patch_existing(taxi_debts, pgsql):
    patch = generate_patch(
        yandex_uid='yandex_uid_2', action='reset_debt', reason_code='support',
    )
    response = await taxi_debts.patch(
        'v1/debts', json=patch, params={'order_id': 'order_id_2'},
    )
    assert response.status_code == http.HTTPStatus.OK

    debt = get_debts_by_yandex_uid(patch['yandex_uid'], pgsql)[0]
    assert debt['value'] is None
    assert debt['currency'] is None
    assert debt['reason_code'] == patch['reason_code']
    assert debt['status'] == 'nodebt'
    assert debt['brand'] == 'yataxi'


async def test_set_debts_metrics__created(taxi_debts, taxi_debts_monitor):
    action, brand = 'set_debt', 'yataxi'
    currency, reason_code, payment_type, user_application = (
        'RUB',
        'moved_to_cash',
        'cash',
        'iOS',
    )
    patch = generate_patch(
        value='300',
        currency=currency,
        reason_code=reason_code,
        brand=brand,
        order_info={
            'payment_tech': {'type': payment_type},
            'statistics': {'application': user_application},
        },
    )

    async with metrics_helpers.MetricsCollector(
            taxi_debts_monitor, sensor=action,
    ) as collector:
        response = await taxi_debts.patch(
            'v1/debts', json=patch, params={'order_id': 'order_id'},
        )
        assert response.status_code == http.HTTPStatus.OK

    assert collector.get_single_collected_metric() == metrics_helpers.Metric(
        labels={
            'brand': brand,
            'sensor': action,
            'currency': currency,
            'reason_code': reason_code,
            'payment_type': payment_type,
            'user_application': user_application,
        },
        value=1,
    )


async def test_set_debts_metrics__empty(taxi_debts, taxi_debts_monitor):
    action = 'set_debt'
    params = {'order_id': 'order_id'}
    patch = generate_patch(action=action, reason_code='')

    async with metrics_helpers.MetricsCollector(
            taxi_debts_monitor, sensor=action,
    ) as collector:
        response = await taxi_debts.patch(
            'v1/debts', json=patch, params=params,
        )
        assert response.status_code == http.HTTPStatus.BAD_REQUEST

    assert collector.get_single_collected_metric() is None


async def test_reset_debts_metrics__created(taxi_debts, taxi_debts_monitor):
    action, brand = 'reset_debt', 'yataxi'
    currency, reason_code, payment_type, user_application = (
        'RUB',
        'moved_to_cash',
        'cash',
        'iOS',
    )

    patch = generate_patch(
        action=action,
        currency=currency,
        reason_code=reason_code,
        brand=brand,
        order_info={
            'payment_tech': {'type': payment_type},
            'statistics': {'application': user_application},
        },
    )

    async with metrics_helpers.MetricsCollector(
            taxi_debts_monitor, sensor=action,
    ) as collector:
        response = await taxi_debts.patch(
            'v1/debts', json=patch, params={'order_id': 'order_id'},
        )
        assert response.status_code == http.HTTPStatus.OK

    assert collector.get_single_collected_metric() == metrics_helpers.Metric(
        labels={
            'brand': brand,
            'sensor': action,
            'currency': currency,
            'reason_code': reason_code,
            'payment_type': payment_type,
            'user_application': user_application,
        },
        value=1,
    )


async def test_reset_debts_metrics__empty(taxi_debts, taxi_debts_monitor):
    action = 'reset_debt'
    params = {'order_id': 'order_id'}
    patch = generate_patch(action=action, reason_code='')

    async with metrics_helpers.MetricsCollector(
            taxi_debts_monitor, sensor=action,
    ) as collector:
        response = await taxi_debts.patch(
            'v1/debts', json=patch, params=params,
        )
        assert response.status_code == http.HTTPStatus.BAD_REQUEST

    assert collector.get_single_collected_metric() is None
