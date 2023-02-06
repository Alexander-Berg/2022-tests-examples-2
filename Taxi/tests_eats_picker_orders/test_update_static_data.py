import pytest


@pytest.mark.parametrize(
    'initial_data, request_data, order_data',
    [
        ({'comment': None}, {'comment': None}, {'comment': None}),
        (
            {'comment': None},
            {'comment': 'request comment'},
            {'comment': 'request comment'},
        ),
        (
            {'comment': 'initial comment'},
            {'comment': None},
            {'comment': 'initial comment'},
        ),
        (
            {'comment': 'initial comment'},
            {'comment': 'request comment'},
            {'comment': 'request comment'},
        ),
    ],
)
async def test_order_update_static_data_200(
        taxi_eats_picker_orders,
        create_order,
        get_order,
        initial_data,
        request_data,
        order_data,
):
    eats_id = 'eats-id'
    order_id = create_order(eats_id=eats_id, **initial_data)

    response = await taxi_eats_picker_orders.post(
        f'api/v1/order/update-static-data?eats_id={eats_id}',
        json=request_data,
    )
    assert response.status == 200

    order = get_order(order_id)
    for key, value in order_data.items():
        assert order[key] == value
    assert order['external_updated_at']


async def test_order_update_static_data_404(taxi_eats_picker_orders):
    eats_id = 'eats-id'
    comment = 'a comment'
    response = await taxi_eats_picker_orders.post(
        f'api/v1/order/update-static-data?eats_id={eats_id}',
        json={'comment': comment},
    )
    assert response.status == 404
