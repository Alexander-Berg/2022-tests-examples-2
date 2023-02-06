import pytest

from tests_eats_customer_slots import utils


@utils.slots_enabled()
@utils.daily_slots_config()
@utils.settings_config()
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
@pytest.mark.parametrize('place_id', [0, 1, 2, 3, 4, 5, 6, 7, 666])
async def test_catalog_storage_places_cache(
        taxi_eats_customer_slots, testpoint, catalog_storage_cache, place_id,
):
    order = utils.make_order(place_id=place_id, estimated_picking_time=200)

    @testpoint('catalog_storage_place_info')
    def catalog_storage_place_info_tp(data):
        place = catalog_storage_cache[place_id]
        assert data['place_id'] == place_id
        if 'origin_id' in place:
            assert data['place_origin_id'] == place['origin_id']
        else:
            assert data['place_origin_id'] is None
        if 'brand' in place:
            assert data['brand_id'] == place['brand']['id']
        else:
            assert data['brand_id'] is None

    response = await taxi_eats_customer_slots.post(
        '/api/v1/order/calculate-slots', json=order,
    )
    assert response.status == 200

    assert catalog_storage_place_info_tp.times_called == int(
        place_id in catalog_storage_cache,
    )
