import pytest

from tests_eats_customer_slots import utils


@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache_data.json')
@utils.places_load_batching(our_picking_batch=2, shop_picking_batch=1)
async def test_places_load_info_cache_update(
        taxi_eats_customer_slots, mockserver,
):
    @mockserver.json_handler(
        '/eats-picker-dispatch/api/v1/places/calculate-load',
    )
    def do_mock_calculate_load(request):
        return mockserver.make_response(json={'places_load_info': []})

    await taxi_eats_customer_slots.invalidate_caches(
        cache_names=['places-load-info-cache'],
    )

    # 5 calls - before test has been run
    # 5 actual calls: 3 for each shop with shop_picking
    # 2 calls: for each pair of shops with our_picking
    assert do_mock_calculate_load.times_called == 10
