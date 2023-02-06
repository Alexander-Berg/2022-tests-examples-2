import copy
import json

import pytest


REPLICATION_RULE_NAME = 'grocery_order_log_by_id'


def _format_redis_key(item_id):
    return f'{REPLICATION_RULE_NAME}:{item_id}'.encode('ascii')


@pytest.mark.yt(schemas=['yt_schema.yaml'], dyn_table_data=['yt.yaml'])
async def test_basic(taxi_grocery_cold_storage, yt_apply, load_json):
    request = load_json('request.json')
    expected_response = load_json('response.json')

    response = await taxi_grocery_cold_storage.post(
        '/internal/v1/cold-storage/v1/get/order-log', json=request,
    )
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.parametrize('prefetch', [True, False])
@pytest.mark.yt(schemas=['yt_schema.yaml'], dyn_table_data=['yt.yaml'])
async def test_cache(
        taxi_grocery_cold_storage,
        yt_apply,
        load_json,
        taxi_config,
        testpoint,
        redis_store,
        prefetch,
):
    config_name = 'GROCERY_COLD_STORAGE_ORDER_LOG_CACHE_SETTINGS'
    config = taxi_config.get(config_name)
    config['fetch_from_cache'] = True
    taxi_config.set_values({config_name: config})

    request = load_json('request.json')
    expected_response = load_json('response.json')
    item_ids = request['item_ids']

    @testpoint('prefetch_order_log')
    def _prefetch_order_log(data):
        pass

    @testpoint('get_order_log_redis_fetched')
    def _get_order_log_redis_fetched(data):
        pass

    @testpoint('get_order_log_yt_finished')
    def _get_order_log_yt_finished(data):
        pass

    @testpoint('get_order_log_redis_updated')
    def _get_order_log_redis_updated(data):
        pass

    def _check_redis(item_ids):
        redis_keys = redis_store.keys()
        assert set(redis_keys) == set(map(_format_redis_key, item_ids))
        items = filter(
            lambda item: item['item_id'] in item_ids,
            expected_response['items'],
        )

        def _get_item_id(item):
            return item['item_id']

        for item, redis_key in zip(
                sorted(items, key=_get_item_id), sorted(redis_keys),
        ):
            item = copy.deepcopy(item)
            del item['item_id']
            assert redis_store.get(redis_key) == json.dumps(
                item, sort_keys=True, separators=(',', ':'),
            ).encode('ascii')

    prefetched_item_ids = []
    if prefetch:
        prefetch_request = copy.deepcopy(request)
        prefetched_item_ids = prefetch_request['item_ids']
        prefetched_item_ids.pop()
        response = await taxi_grocery_cold_storage.post(
            '/internal/v1/cold-storage/v1/prefetch/order-log',
            json=prefetch_request,
        )
        assert response.status_code == 200
        assert response.json() == {}

        assert (await _prefetch_order_log.wait_call())[
            'data'
        ] == prefetched_item_ids

        _check_redis(prefetched_item_ids)

    response = await taxi_grocery_cold_storage.post(
        '/internal/v1/cold-storage/v1/get/order-log', json=request,
    )
    assert response.status_code == 200
    assert response.json() == expected_response

    assert (await _get_order_log_redis_fetched.wait_call())[
        'data'
    ] == prefetched_item_ids
    assert (await _get_order_log_yt_finished.wait_call())['data'] == item_ids
    assert (await _get_order_log_redis_updated.wait_call())['data'] == item_ids

    _check_redis(item_ids)

    response = await taxi_grocery_cold_storage.post(
        '/internal/v1/cold-storage/v1/get/order-log', json=request,
    )
    assert response.status_code == 200
    assert response.json() == expected_response

    assert (await _get_order_log_redis_fetched.wait_call())['data'] == item_ids
    assert (await _get_order_log_yt_finished.wait_call())['data'] == item_ids
    assert (await _get_order_log_redis_updated.wait_call())['data'] == item_ids

    _check_redis(item_ids)
