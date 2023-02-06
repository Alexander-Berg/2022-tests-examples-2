import datetime
import json

import pytest


def convert_datetime_to_yt_format(timestamp: str) -> str:
    return datetime.datetime.strptime(
        timestamp, '%Y-%m-%dT%H:%M:%S%z',
    ).strftime('%Y-%m-%d %H:%M:%S')


@pytest.mark.yt(
    schemas=['yt_depot_state_raw_schema.yaml'],
    dyn_table_data=['yt_depot_state_raw.yaml'],
)
async def test_basic(
        taxi_grocery_cold_storage, yt_apply, load_json, redis_store,
):
    assert redis_store.keys() == []

    request = load_json('get_depot_state_request.json')
    response = await taxi_grocery_cold_storage.post(
        '/internal/v1/cold-storage/v1/get/depot-state', json=request,
    )

    assert response.status_code == 200
    response_json = response.json()
    expected_response = load_json('get_depot_state_response.json')
    assert response_json == expected_response

    depot_id = request['item_ids'][0]
    from_ts = convert_datetime_to_yt_format(request['item_ids'][1])
    to_ts = convert_datetime_to_yt_format(request['item_ids'][2])

    scope = 'grocery_dispatch_tracking_depot_state_raw'
    redis_key = bytes(
        scope + ':' + depot_id + '_' + from_ts + '_' + to_ts, 'utf-8',
    )

    assert redis_store.keys() == [redis_key]
    del response_json['items'][0]['item_id']
    del response_json['items'][1]['item_id']

    res = redis_store.smembers(redis_key)
    res_decoded = sorted([elem.decode() for elem in res])

    assert [json.loads(elem) for elem in res_decoded] == response_json['items']
