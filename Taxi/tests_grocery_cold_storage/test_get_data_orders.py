import pytest


@pytest.mark.yt(
    schemas=['yt_orders_raw_schema.yaml'],
    dyn_table_data=['yt_orders_raw.yaml'],
)
@pytest.mark.parametrize('test', ['order_info', 'order_history'])
async def test_basic(taxi_grocery_cold_storage, yt_apply, load_json, test):
    request = load_json(f'get_{test}_request.json')
    request['item_ids'].append('9dc2300a4d004a9e9d854a9f5e45816a-grocery')
    response = await taxi_grocery_cold_storage.post(
        '/internal/v1/cold-storage/v1/get/orders', json=request,
    )

    assert response.status_code == 200
    assert response.json() == load_json(f'get_{test}_response.json')


@pytest.mark.yt(
    schemas=['yt_orders_raw_schema.yaml'],
    dyn_table_data=['yt_orders_raw.yaml'],
)
async def test_empty_receipts(taxi_grocery_cold_storage, yt_apply, load_json):
    request = load_json('get_order_info_request.json')
    request['item_ids'].append('86e296390a8447c98f2290b71bae1fdf-grocery')
    response = await taxi_grocery_cold_storage.post(
        '/internal/v1/cold-storage/v1/get/orders', json=request,
    )

    assert response.status_code == 200
    assert response.json() == load_json(
        'get_order_info_empty_receipts_response.json',
    )
