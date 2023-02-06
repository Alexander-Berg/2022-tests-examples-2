import pytest


HANDLER = '/v1/autodisable_info'
MOCK_NOW = '2021-09-20T15:00:00+03:00'
PLACE_ID_1 = 1
BRAND_ID_1 = 101
ORIGIN_ID_1 = 'item_origin_1'
ORIGIN_ID_2 = 'item_origin_2'


@pytest.mark.now(MOCK_NOW)
async def test_404_exp_not_exists(taxi_eats_retail_products_autodisable):
    response = await taxi_eats_retail_products_autodisable.post(
        HANDLER,
        json={
            'place_id': PLACE_ID_1,
            'brand_id': BRAND_ID_1,
            'origin_ids': [ORIGIN_ID_1, ORIGIN_ID_2],
        },
    )

    assert response.status == 404
