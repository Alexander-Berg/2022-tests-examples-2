import pytest


@pytest.mark.pgsql('maas', files=['orders.sql'])
@pytest.mark.parametrize(
    'order_ids, expected_response',
    [
        pytest.param([], [], id='empty'),
        pytest.param(
            ['order_id_fail', 'order_id_new', 'order_id_success'],
            [
                {
                    'order_id': 'order_id_fail',
                    'is_maas_order': True,
                    'subscription_applied': False,
                },
                {
                    'order_id': 'order_id_new',
                    'is_maas_order': False,
                    'subscription_applied': False,
                },
                {
                    'order_id': 'order_id_success',
                    'is_maas_order': True,
                    'subscription_applied': True,
                },
            ],
            id='mixed',
        ),
    ],
)
async def test_ok(taxi_maas, order_ids, expected_response):
    response = await taxi_maas.post(
        '/internal/v1/mark-maas-orders', json={'order_ids': order_ids},
    )
    assert response.status == 200
    assert response.json()['maas_infos'] == expected_response
