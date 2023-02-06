import pytest


@pytest.mark.pgsql('cashback', files=['basic_cashback.sql'])
async def test_rates_notfound(taxi_cashback_web):
    params = {'order_id': 'order_id_31'}
    response = await taxi_cashback_web.get(
        '/internal/rates/order', params=params,
    )
    assert response.status == 404


@pytest.mark.parametrize(
    'order_id', ['order_id_1', 'order_id_2', 'order_id_3'],
)
@pytest.mark.pgsql('cashback', files=['basic_cashback.sql'])
async def test_rates_info_ok(taxi_cashback_web, order_id):
    params = {'order_id': order_id}
    response = await taxi_cashback_web.get(
        '/internal/rates/order', params=params,
    )
    assert response.status == 200


@pytest.mark.pgsql('cashback', files=['basic_cashback.sql'])
async def test_rates_info_marketing_cashbacks(taxi_cashback_web):
    params = {'order_id': 'order_id_with_marketing_cashbacks'}
    response = await taxi_cashback_web.get(
        '/internal/rates/order', params=params,
    )
    assert response.status == 200

    content = await response.json()
    assert content == {
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
        },
    }
