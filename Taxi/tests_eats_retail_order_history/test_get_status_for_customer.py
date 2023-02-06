import pytest


@pytest.mark.config(
    EATS_RETAIL_ORDER_HISTORY_ORDER_STATUS_SETTINGS={'select_batch_size': 10},
)
async def test_get_status_for_customer_no_orders(
        taxi_eats_retail_order_history,
):
    order_nr = '123456'
    response = await taxi_eats_retail_order_history.post(
        '/api/v1/customer/order/status', json={'order_nrs': [f'{order_nr}']},
    )

    assert response.status_code == 200
    assert not response.json()['orders_statuses']


@pytest.mark.config(
    EATS_RETAIL_ORDER_HISTORY_ORDER_STATUS_SETTINGS={'select_batch_size': 1},
)
async def test_get_status_for_customer_200(
        taxi_eats_retail_order_history, create_order,
):
    without_status = '123456'
    with_status = '654321'
    status = 'in_delivery'
    create_order(order_nr=without_status)
    create_order(order_nr=with_status, status_for_customer=status)
    response = await taxi_eats_retail_order_history.post(
        '/api/v1/customer/order/status',
        json={
            'order_nrs': [
                f'{without_status}',
                f'{with_status}',
                'not_existed_nr',
            ],
        },
    )

    assert response.status_code == 200
    assert len(response.json()['orders_statuses']) == 2
    assert 'order_nr' in response.json()['orders_statuses'][0]
    assert response.json()['orders_statuses'][0]['order_nr'] == without_status
    assert 'status' not in response.json()['orders_statuses'][0]

    assert 'order_nr' in response.json()['orders_statuses'][1]
    assert response.json()['orders_statuses'][1]['order_nr'] == with_status
    assert 'status' in response.json()['orders_statuses'][1]
    assert response.json()['orders_statuses'][1]['status'] == status
