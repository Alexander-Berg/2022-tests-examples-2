import pytest

from tests_grocery_uber_gw import models

DEPOTS_MAPPING_SETTINGS = {'enabled': True, 'limit': 1}


@pytest.mark.config(
    GROCERY_UBER_GW_DEPOTS_MAPPING_SETTINGS=DEPOTS_MAPPING_SETTINGS,
)
async def test_basic(taxi_grocery_uber_gw, mock_uber_api, testpoint):
    """ Checking that the cache is being built correctly """

    stores = [
        models.Store(store_id='uber_id_1', merchant_store_id='deli_id_3'),
        models.Store(store_id='uber_id_2', merchant_store_id='deli_id_1'),
        models.Store(store_id='uber_id_3', merchant_store_id=None),
        models.Store(store_id='uber_id_4', merchant_store_id='deli_id_5'),
        models.Store(store_id='uber_id_5', merchant_store_id='deli_id_4'),
        models.Store(store_id='uber_id_6', merchant_store_id='deli_id_2'),
        models.Store(store_id='uber_id_7', merchant_store_id=None),
    ]
    mock_uber_api_payload = {'stores': {}}
    for store in stores:
        mock_uber_api_payload['stores'][store.store_id] = store
    mock_uber_api.set_payload(mock_uber_api_payload)

    @testpoint('depots_mapping_cache')
    def depots_mapping_cache(data):
        return data

    await taxi_grocery_uber_gw.invalidate_caches()

    depots_mapping_cache = (await depots_mapping_cache.wait_call())['data']

    expected_in_cache = {
        key: value
        for (key, value) in mock_uber_api_payload['stores'].items()
        if value.merchant_store_id is not None
    }
    assert len(expected_in_cache) == len(depots_mapping_cache)
    for store in expected_in_cache.values():
        assert store.store_id in depots_mapping_cache
        assert depots_mapping_cache[store.store_id] == store.merchant_store_id
