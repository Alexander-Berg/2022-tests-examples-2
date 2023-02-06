import pytest

from testsuite.utils import ordered_object

# Feel free to provide your custom implementation to override generated tests.

# pylint: disable=import-error,wildcard-import
from parks_commute_plugins.generated_tests import *  # noqa


async def test_parks_commute_updates(taxi_parks_commute):
    response = await taxi_parks_commute.get(
        'v1/parks/updates',
        params={'consumer': 'test', 'last_known_revision': '0_1234567_2'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'cache_lag' in response_json
    response_json.pop('cache_lag')
    assert response_json == {
        'last_modified': '1970-01-15T06:56:07Z',
        'last_revision': '0_1234567_4',
        'parks': [
            {
                'revision': '0_1234567_3',
                'park_id': 'park_id3',
                'data': {'clid': 'clid1'},
            },
            {
                'revision': '0_1234567_4',
                'park_id': 'park_id4',
                'data': {'clid': 'clid1'},
            },
        ],
    }
    delay_header = response.headers.get('X-Polling-Delay-Ms')
    delay_value = str(10)
    assert delay_header == delay_value
    data_size = 250
    assert int(response.headers.get('Content-Length')) < data_size

    response = await taxi_parks_commute.get(
        'v1/parks/updates',
        params={'consumer': 'test', 'last_known_revision': '0_1234567_4'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'cache_lag' in response_json
    response_json.pop('cache_lag')
    assert response_json == {
        'last_modified': '1970-01-15T06:56:07Z',
        'last_revision': '0_1234567_4',
        'parks': [],
    }
    delay_header = response.headers.get('X-Polling-Delay-Ms')
    delay_value = str(10)
    assert delay_header == delay_value
    assert int(response.headers.get('Content-Length')) < data_size
    # no more changes
    response = await taxi_parks_commute.get(
        'v1/parks/updates',
        params={'consumer': 'test', 'last_known_revision': '0_1234567_5'},
    )
    assert response.status_code == 429


@pytest.mark.config(
    API_OVER_DATA_SERVICES={
        'parks-commute': {
            'deleted_documents_ttl_seconds': 0,
            'incremental_merge_time_limit_ms': 5000,
            'is_dumper_enabled': False,
            'updates_max_documents_count': 2,
            'max_answer_data_size_bytes': 100,
            'max_x_polling_delay_ms': 10,
            'min_x_polling_delay_ms': 0,
        },
    },
)
async def test_parks_commute_updates_empty_revision(taxi_parks_commute):
    response = await taxi_parks_commute.get(
        'v1/parks/updates', params={'consumer': 'test'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'cache_lag' in response_json
    response_json.pop('cache_lag')
    assert response_json == {
        'last_modified': '1970-01-15T06:56:07Z',
        'last_revision': '0_1234567_2',
        'parks': [
            {
                'revision': '0_1234567_1',
                'park_id': 'park_id1',
                'data': {'clid': 'clid1'},
            },
            {
                'revision': '0_1234567_2',
                'park_id': 'park_id2',
                'data': {'clid': 'clid2'},
            },
        ],
    }
    delay_header = response.headers.get('X-Polling-Delay-Ms')
    delay_value = str(0)
    assert delay_header == delay_value
    data_size = 250
    assert int(response.headers.get('Content-Length')) < data_size


async def test_parks_commute_updates_no_consumer(taxi_parks_commute):
    response = await taxi_parks_commute.get('v1/parks/updates', params={})
    assert response.status_code == 400


async def test_parks_commute_retrieve_bad_request(taxi_parks_commute):
    response = await taxi_parks_commute.post(
        'v1/parks/retrieve_by_park_id',
        json={
            'consumer': 'test',
            # deliberate error in parameter name
            'bad_name': ['park_id1'],
        },
    )
    assert response.status_code == 400


async def test_parks_commute_retrieve_by_park_id(taxi_parks_commute):
    response = await taxi_parks_commute.post(
        'v1/parks/retrieve_by_park_id',
        json={'consumer': 'test', 'id_in_set': ['park_id1', 'unknown']},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json == {
        'parks': [
            {
                'revision': '0_1234567_1',
                'park_id': 'park_id1',
                'data': {'clid': 'clid1'},
            },
            {'park_id': 'unknown'},
        ],
    }


async def test_parks_commute_retrieve_projection(taxi_parks_commute):
    response = await taxi_parks_commute.post(
        'v1/parks/retrieve_by_park_id',
        json={
            'consumer': 'test',
            'id_in_set': ['park_id1', 'unknown'],
            'projection': ['park_id'],
        },
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json == {
        'parks': [{'park_id': 'park_id1', 'data': {}}, {'park_id': 'unknown'}],
    }


@pytest.mark.filldb(dbparks='absent_field')
async def test_parks_commute_retrieve_optional(taxi_parks_commute):
    response = await taxi_parks_commute.post(
        'v1/parks/retrieve_by_park_id',
        json={
            'consumer': 'test',
            'id_in_set': ['park_id5', 'unknown'],
            'projection': ['park_id'],
        },
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json == {
        'parks': [{'park_id': 'park_id5', 'data': {}}, {'park_id': 'unknown'}],
    }


async def test_parks_commute_retrieve_by_clid(taxi_parks_commute):
    response = await taxi_parks_commute.post(
        'v1/parks/retrieve_by_clid',
        json={
            'consumer': 'test',
            'clid_in_set': ['clid1', 'clid2', 'unknown'],
        },
    )
    assert response.status_code == 200
    response_json = response.json()
    ordered_object.assert_eq(
        response_json,
        {
            'parks_by_clid': [
                {
                    'clid': 'clid1',
                    'parks': [
                        {
                            'revision': '0_1234567_4',
                            'data': {'clid': 'clid1'},
                            'park_id': 'park_id4',
                        },
                        {
                            'revision': '0_1234567_3',
                            'data': {'clid': 'clid1'},
                            'park_id': 'park_id3',
                        },
                        {
                            'revision': '0_1234567_1',
                            'data': {'clid': 'clid1'},
                            'park_id': 'park_id1',
                        },
                    ],
                },
                {
                    'clid': 'clid2',
                    'parks': [
                        {
                            'revision': '0_1234567_2',
                            'data': {'clid': 'clid2'},
                            'park_id': 'park_id2',
                        },
                    ],
                },
                {'clid': 'unknown', 'parks': []},
            ],
        },
        ['parks_by_clid', 'parks_by_clid.parks'],
    )
