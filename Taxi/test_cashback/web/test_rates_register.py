import pytest


def make_request():
    return {
        'cashback': {
            'by_classes': [
                {'class': 'econom', 'value': 0.1, 'max_absolute_value': 50},
                {'class': 'vip', 'value': 0.2},
            ],
        },
    }


@pytest.mark.pgsql('cashback', files=['basic_cashback.sql'])
async def test_register_new(taxi_cashback_web):
    params = {'order_id': 'order_id_31'}
    data = make_request()
    response = await taxi_cashback_web.post(
        '/internal/rates/order', params=params, json=data,
    )
    assert response.status == 200

    response = await taxi_cashback_web.get(
        '/internal/rates/order', params=params,
    )
    assert response.status == 200
    content = await response.json()
    assert len(content['cashback']['by_classes']) == 2


@pytest.mark.pgsql('cashback', files=['basic_cashback.sql'])
async def test_register_existing(taxi_cashback_web, pg_cashback):
    order_id = 'order_id_1'
    rates = await pg_cashback.order_rates.by_ids([order_id])

    params = {'order_id': order_id}
    data = make_request()
    response = await taxi_cashback_web.post(
        '/internal/rates/order', params=params, json=data,
    )
    assert response.status == 200

    new_rates = await pg_cashback.order_rates.by_ids([order_id])
    assert rates == new_rates


@pytest.mark.pgsql('cashback', files=['basic_cashback.sql'])
async def test_register_existing_rates_add_new_possible_cashback(
        taxi_cashback_web, pg_cashback,
):
    order_id = 'order_id_1'

    params = {'order_id': order_id}
    data = make_request()
    data['possible_cashback'] = {'value': 0.1, 'max_absolute_value': 50}

    response = await taxi_cashback_web.post(
        '/internal/rates/order', params=params, json=data,
    )
    assert response.status == 200

    response = await taxi_cashback_web.get(
        '/internal/rates/order', params=params,
    )
    assert response.status == 200
    content = await response.json()
    assert len(content['cashback']['by_classes']) == 1
    assert content.get('possible_cashback') is None


@pytest.mark.pgsql('cashback', files=['basic_cashback.sql'])
async def test_register_rates_add_possible_cashback(
        taxi_cashback_web, pg_cashback,
):
    order_id = 'order_id_111'

    params = {'order_id': order_id}
    data = make_request()
    data['possible_cashback'] = {'value': 0.1, 'max_absolute_value': 50}

    response = await taxi_cashback_web.post(
        '/internal/rates/order', params=params, json=data,
    )
    assert response.status == 200

    response = await taxi_cashback_web.get(
        '/internal/rates/order', params=params,
    )
    assert response.status == 200
    content = await response.json()
    assert len(content['cashback']['by_classes']) == 2
    assert content.get('possible_cashback') is not None
    assert content['possible_cashback']['value'] == 0.1
    assert content['possible_cashback']['max_absolute_value'] == 50


@pytest.mark.pgsql('cashback', files=['basic_cashback.sql'])
async def test_register_existing_rates_and_existing_possible_cashback(
        taxi_cashback_web, pg_cashback,
):
    order_id = 'order_id_possible_cashback'
    rates = await pg_cashback.order_rates.by_ids([order_id])

    params = {'order_id': order_id}
    data = make_request()
    data['possible_cashback'] = {'value': 0.2, 'max_absolute_value': 50}
    response = await taxi_cashback_web.post(
        '/internal/rates/order', params=params, json=data,
    )
    assert response.status == 200

    new_rates = await pg_cashback.order_rates.by_ids([order_id])
    assert rates == new_rates


async def test_register_idempotent(taxi_cashback_web, pg_cashback):
    order_id = 'order_id_1'
    params = {'order_id': order_id}
    data = make_request()

    await taxi_cashback_web.post(
        '/internal/rates/order', params=params, json=data,
    )
    response = await taxi_cashback_web.post(
        '/internal/rates/order', params=params, json=data,
    )
    assert response.status == 200

    rates = await pg_cashback.order_rates.all()
    assert len(rates) == 1


async def test_register_zero(taxi_cashback_web, pg_cashback):
    params = {'order_id': 'order_id_31'}
    data = {'cashback': {'by_classes': [{'class': 'econom', 'value': 0}]}}
    response = await taxi_cashback_web.post(
        '/internal/rates/order', params=params, json=data,
    )
    assert response.status == 200

    response = await taxi_cashback_web.get(
        '/internal/rates/order', params=params,
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'cashback': {'by_classes': [{'class': 'econom', 'value': 0}]},
    }


@pytest.mark.pgsql('cashback', files=['basic_cashback.sql'])
async def test_register_marketing_cashbacks(taxi_cashback_web, pg_cashback):
    order_id = 'order_id_marketing_cashback_new'

    params = {'order_id': order_id}
    data = {
        'cashback': {
            'by_classes': [
                {'class': 'econom', 'value': 0.1, 'max_absolute_value': 100},
            ],
        },
        'possible_cashback': {
            'value': 0.1,
            'max_absolute_value': 100,
            'enabled': True,
        },
        'marketing_cashback': {
            'possible_cashback': {
                'value': 0.1,
                'max_absolute_value': 100,
                'enabled': True,
            },
            'some_new_cashback': {
                'value': 0.1,
                'max_absolute_value': 100,
                'enabled': True,
                'static_payload': {
                    'cashback_type': 'transaction',
                    'service_id': '124',
                    'issuer': 'marketing_experiment',
                    'campaign_name': 'changing_cashback_go',
                    'ticket': 'NEWSERVICE-1689',
                    'budget_owner': 'portal',
                },
            },
            'fintech': {
                'value': 0.05,
                'enabled': False,
                'static_payload': {
                    'cashback_type': 'transaction',
                    'service_id': '124',
                    'issuer': 'marketing_experiment',
                    'campaign_name': 'changing_cashback_go',
                    'ticket': 'NEWSERVICE-1689',
                    'budget_owner': 'portal',
                },
            },
        },
    }
    response = await taxi_cashback_web.post(
        '/internal/rates/order', params=params, json=data,
    )
    assert response.status == 200

    response = await taxi_cashback_web.get(
        '/internal/rates/order', params=params,
    )
    response.status = 200
    content = await response.json()
    assert data == content
