import pytest


def _get_response_ids(response):
    return [item['product_id'] for item in response.json()['items']]


@pytest.mark.yt(
    schemas=['yt_expiring_products_schema.yaml'],
    static_table_data=['yt_expiring_products.yaml'],
)
async def test_basic(taxi_grocery_cold_storage, yt_apply):
    response_1 = await taxi_grocery_cold_storage.post(
        '/internal/v1/cold-storage/v1/get/expiring-products',
        json={'cursor': 0, 'batch_size': 1},
    )
    assert response_1.status_code == 200
    assert _get_response_ids(response_1) == ['product_1']

    response_2 = await taxi_grocery_cold_storage.post(
        '/internal/v1/cold-storage/v1/get/expiring-products',
        json={'cursor': 1, 'batch_size': 1},
    )
    assert response_2.status_code == 200
    assert _get_response_ids(response_2) == ['product_2']

    response_3 = await taxi_grocery_cold_storage.post(
        '/internal/v1/cold-storage/v1/get/expiring-products',
        json={'cursor': 0, 'batch_size': 2},
    )
    assert response_3.status_code == 200
    assert _get_response_ids(response_3) == ['product_1', 'product_2']
