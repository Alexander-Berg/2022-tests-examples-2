import pytest


@pytest.mark.parametrize(
    'expected_statuses',
    [
        [
            {'status': 'complete', 'title': 'Завершить'},
            {'status': 'cancelled', 'title': 'Отменить'},
        ],
    ],
)
async def test_get_order_final_statuses_format(
        taxi_eats_picker_orders, taxi_config, expected_statuses,
):
    taxi_config.set_values(
        {
            'EATS_PICKER_ORDERS_ADMIN_GET_ORDER_FINAL_STATUSES': {
                'final_statuses': expected_statuses,
            },
        },
    )
    response = await taxi_eats_picker_orders.get(
        '/admin/v1/order/final-statuses',
    )
    assert response.status == 200

    response_data = response.json()
    assert response_data['statuses'] == expected_statuses
