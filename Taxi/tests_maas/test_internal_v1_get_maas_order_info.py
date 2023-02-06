import pytest


@pytest.mark.pgsql('maas', files=['orders.sql'])
@pytest.mark.parametrize(
    'order_id, expected_response',
    [
        pytest.param(
            'order_id_success',
            {
                'is_maas_subscription_applied': True,
                'maas_user_id': 'maas_user_id',
                'maas_sub_id': 'maas30000002',
                'external_order_id': 'external_order_id0',
                'maas_trip_id': 'trip_id',
                'is_point_a_near_metro': True,
                'is_point_b_near_metro': False,
            },
            id='order_id_success',
        ),
        pytest.param(
            'order_id_fail',
            {
                'is_maas_subscription_applied': False,
                'maas_user_id': 'maas_user_id',
                'maas_sub_id': 'maas30000002',
                'external_order_id': 'external_order_id1',
                'maas_trip_id': 'trip_id',
                'is_point_a_near_metro': False,
                'is_point_b_near_metro': False,
            },
            id='order_id_fail',
        ),
        pytest.param(
            'order_id_without_field',
            {
                'is_maas_subscription_applied': False,
                'maas_user_id': 'maas_user_id',
                'maas_sub_id': 'maas30000002',
                'external_order_id': 'external_order_id2',
                'is_point_a_near_metro': False,
                'is_point_b_near_metro': False,
            },
            id='order_id_without_field',
        ),
        pytest.param('order_id_new', {}, id='order_id_new'),
    ],
)
async def test_ok(taxi_maas, order_id, expected_response):
    response = await taxi_maas.post(
        '/internal/v1/get-maas-order-info', json={'order_id': order_id},
    )
    if not expected_response:
        assert response.status == 404
        assert response.json() == {
            'code': 'not_found',
            'message': f'Order with order id = {order_id} not found',
        }
        return

    assert response.status == 200
    assert response.json()['maas_order_info'] == expected_response
