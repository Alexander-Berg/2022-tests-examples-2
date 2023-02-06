import pytest

from tests_eats_retail_market_integration import models
from tests_eats_retail_market_integration import utils

MOCK_NOW = '2021-12-24T08:00:00+00:00'
LATITUDE = 55.725326
LONGITUDE = 37.567051
REGION_ID = 1


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(**utils.gen_bool_params('use_sorting'))
async def test_brand_sorting(
        eats_catalog_storage,
        save_brands_to_db,
        save_market_brand_places_to_db,
        save_brand_places_to_storage,
        taxi_eats_retail_market_integration,
        update_taxi_config,
        # parametrize
        use_sorting,
):
    brand_ids = ['1', '2', '3', '4', '5', '6', '7', '8']
    brand_id_to_priority = {
        '1': 0,
        '2': 0,
        '3': 0,
        '4': 100,
        '5': 100,
        '6': 200,
        # 7 not set
        # 8 not set
    }

    update_taxi_config(
        'EATS_RETAIL_MARKET_INTEGRATION_HYPERLOCAL_SHOPS',
        {'sort_places_by_brand_priority': use_sorting},
    )
    update_taxi_config(
        'UMLAAS_EATS_BRAND_WEIGHT_MAPPING', brand_id_to_priority,
    )

    brands = []
    market_brand_places = []
    # brand_id == place_id == shop_id
    for brand_id in brand_ids:
        brand = models.Brand(brand_id=brand_id, slug=brand_id)
        place = models.Place(place_id=brand_id, slug=brand_id)
        brand.add_place(place)
        brands.append(brand)

        market_brand_places.append(
            models.MarketBrandPlace(
                brand_id=brand_id,
                place_id=brand_id,
                business_id=int(brand_id),
                partner_id=int(brand_id),
                feed_id=int(brand_id),
            ),
        )

    save_brand_places_to_storage(brands)
    save_brands_to_db(brands)
    save_market_brand_places_to_db(market_brand_places)

    response = await taxi_eats_retail_market_integration.get(
        '/v1/market/hyperlocal_shops'
        f'?latitude={LATITUDE}&longitude={LONGITUDE}&region_id={REGION_ID}',
    )
    assert response.status_code == 200

    shop_ids = [
        i['market_shop_id']
        for i in _sorted_by_priority(response.json()['shops'])
    ]
    if use_sorting:
        assert shop_ids == [
            6,  # 200
            4,  # 100
            5,  # 100
            1,  # 0
            2,  # 0
            3,  # 0
            7,  # not set
            8,  # not set
        ]
    else:
        assert shop_ids == [8, 7, 6, 5, 4, 3, 2, 1]


def _sorted_by_priority(data):
    return sorted(data, key=lambda item: item['priority'])
