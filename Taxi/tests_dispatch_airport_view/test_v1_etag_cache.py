import json

import pytest

from tests_dispatch_airport_view import common
import tests_dispatch_airport_view.utils as utils


DRIVER_META = {
    # 09 october 2020 14:15:15 - 1602252915
    'dbid_uuid0': {'geobus_ts': '1602252915', 'updated_ts': '1602252915'},
    'dbid_uuid1': {'geobus_ts': '1602252915', 'updated_ts': '1602252915'},
    # 09 october 2020 15:15:15 - 1602256515
    'dbid_uuid2': {'geobus_ts': '1602256515', 'updated_ts': '1602256516'},
    'dbid_uuid3': {'geobus_ts': '1602256515', 'updated_ts': '1602256516'},
    'dbid_uuid4': {
        'geobus_ts': '1602256515',
        'updated_ts': '1602256516',
        'is_hidden': 'false',
    },
    'dbid_uuid5': {
        'geobus_ts': '1602256515',
        'updated_ts': '1602256516',
        'is_hidden': 'true',
    },
}


@pytest.mark.redis_store(
    # driver hashes
    [
        'hmset',
        utils.driver_info_key('dbid_uuid0'),
        {**DRIVER_META['dbid_uuid0'], 'pins': json.dumps([])},
    ],
    [
        'hmset',
        utils.driver_info_key('dbid_uuid1'),
        {**DRIVER_META['dbid_uuid1'], 'pins': json.dumps([])},
    ],
    [
        'hmset',
        utils.driver_info_key('dbid_uuid2'),
        {**DRIVER_META['dbid_uuid2'], 'pins': json.dumps([])},
    ],
    [
        'hmset',
        utils.driver_info_key('dbid_uuid3'),
        {**DRIVER_META['dbid_uuid3'], 'pins': json.dumps([])},
    ],
    [
        'hmset',
        utils.driver_info_key('dbid_uuid4'),
        {**DRIVER_META['dbid_uuid4'], 'pins': json.dumps([])},
    ],
    [
        'hmset',
        utils.driver_info_key('dbid_uuid5'),
        {**DRIVER_META['dbid_uuid5'], 'pins': json.dumps([])},
    ],
)
async def test_v1_etag_cache(taxi_dispatch_airport_view, taxi_config):
    url = '/v1/etag-cache/full'
    headers = common.DEFAULT_DISPATCH_AIRPORT_VIEW_HEADER

    response = await taxi_dispatch_airport_view.get(
        url, params={'current_chunk': 1}, headers=headers,
    )
    r_json = response.json()
    assert r_json['code'] == 'invalid_query_params'

    response = await taxi_dispatch_airport_view.get(
        url, params={'current_chunk': 1, 'total_chunks': 1}, headers=headers,
    )
    r_json = response.json()
    assert r_json['code'] == 'invalid_query_params'

    response = await taxi_dispatch_airport_view.get(url, headers=headers)
    r_json = response.json()
    r_json['etags'].sort(key=lambda x: x['dbid_uuid'])
    assert r_json == {
        'current_chunk': 0,
        'total_chunks': 2,
        'etags': [
            {'dbid_uuid': 'dbid_uuid0', 'etag': 1602252915},
            {'dbid_uuid': 'dbid_uuid4', 'etag': 1602256516},
        ],
    }

    response = await taxi_dispatch_airport_view.get(
        url, params={'current_chunk': 1, 'total_chunks': 2}, headers=headers,
    )
    r_json = response.json()
    r_json['etags'].sort(key=lambda x: x['dbid_uuid'])
    assert r_json == {
        'current_chunk': 1,
        'total_chunks': 2,
        'etags': [
            {'dbid_uuid': 'dbid_uuid1', 'etag': 1602252915},
            {'dbid_uuid': 'dbid_uuid2', 'etag': 1602256516},
            {'dbid_uuid': 'dbid_uuid3', 'etag': 1602256516},
        ],
    }
