import pytest

HANDLER = '/v1/market/shop_info'


@pytest.mark.pgsql(
    'eats_retail_market_integration', files=['fill_shop_info.sql'],
)
async def test_404_shop_id_not_found(taxi_eats_retail_market_integration):
    not_found_place_ids = ['3', '4']
    for not_found_place_id in not_found_place_ids:
        response = await taxi_eats_retail_market_integration.get(
            HANDLER + f'?place_id={not_found_place_id}',
        )
        assert response.status == 404


@pytest.mark.pgsql(
    'eats_retail_market_integration', files=['fill_shop_info.sql'],
)
async def test_market_shop_info(taxi_eats_retail_market_integration):
    expected_place_id_to_shop_id = {'1': 1, '2': 2}
    for place_id in expected_place_id_to_shop_id:
        response = await taxi_eats_retail_market_integration.get(
            HANDLER + f'?place_id={place_id}',
        )
        assert response.status == 200
        assert response.json() == {
            'shop_id': expected_place_id_to_shop_id[place_id],
        }
