import functools
import json
import math
import operator

import pytest

import tests_cctv_workers.pgsql_helpers as pgsql_helpers
import tests_cctv_workers.utils as utils

CCTV_WORKERS_PG_CACHES_CONFIG = {
    '__default__': {
        'full_update': {'chunk_size': 0, 'correction_ms': 10000},
        'incremental_update': {'chunk_size': 0, 'correction_ms': 1000},
    },
    'guest-fast-append-index': {
        'full_update': {'chunk_size': 0, 'correction_ms': 10000},
        'incremental_update': {'chunk_size': 0, 'correction_ms': 1000},
    },
}
EXPECTED_SIGNATURE_DIM = 10


def _parse_input_json_storage_data(json_data):
    result = dict()
    for item in json_data:
        result[item['id']] = {
            'signature': item['signature'],
            'updated_ts': utils.parse_date_str(item['updated_ts']),
        }
    return result


def _parse_input_json_index_update_result(json_data):
    result = json_data['index_build_statistics'].copy()
    result['updated_ts'] = utils.parse_date_str(
        result['index_last_updated_ts'],
    )
    result.pop('index_last_updated_ts')
    return result


def _parse_storage_update_result(json_data):
    result = {
        'storage': {},
        'updated_ts': utils.date_from_ms(json_data['storage_last_updated_ts']),
        'is_full_update': json_data['is_full_update'],
    }
    result_storage = result['storage']
    for item in json_data['records']:
        result_storage[item['id']] = {
            'signature': item['signature'],
            'updated_ts': utils.date_from_ms(item['updated_ts']),
        }
    return result


def _parse_index_update_result(json_data):
    result = json_data.copy()
    result['updated_ts'] = utils.date_from_ms(result['index_last_updated_ts'])
    result.pop('index_last_updated_ts')
    return result


def _fill_storage_with_input_data(pgsql, json_storage_data):
    data = _parse_input_json_storage_data(json_storage_data)
    pgsql_helpers.upsert_face_signatures(pgsql, data)
    # assert data == pgsql_helpers.get_face_signatures(pgsql)


def _load_data_from_storage(pgsql):
    result = dict()
    raw_data = pgsql_helpers.get_face_signatures(pgsql)
    for key, value in raw_data.items():
        if len(value['signature']) != EXPECTED_SIGNATURE_DIM:
            continue
        result[f'{key}'] = value
    return result


def _compare_storage_data(data, expected):
    assert len(data) == len(expected)
    for key, value in data.items():
        expected_value = expected.get(key)
        assert expected_value, '\'{}\' is not present in expected'.format(key)
        assert value['updated_ts'] == expected_value['updated_ts']
        signature = value['signature']
        expected_signature = expected_value['signature']
        err_message = (
            'data[\'signature\'] != expected[\'signature\']: {} != {}'.format(
                signature, expected_signature,
            )
        )
        assert len(signature) == len(expected_signature), err_message
        for i, item in enumerate(signature):
            assert math.fabs(item - expected_signature[i]) < 1e-6, err_message


async def _send_detection_event(
        taxi_cctv_workers, event, identification_tp=None,
):
    data = json.dumps(
        {'timestamp': event['timestamp'], 'event': event['event']},
    )
    message = {
        'consumer': 'events-consumer',
        'topic': '/taxi/cctv/testing/events',
        'cookie': 'cookie',
    }
    message['data'] = '{}\n'.format(data)
    response = await taxi_cctv_workers.post(
        'tests/logbroker/messages', data=json.dumps(message),
    )
    assert response.status_code == 200
    if identification_tp:
        return (await identification_tp.wait_call())['data']
    return {}


async def _invalidate_and_update_fai(
        taxi_cctv_workers, full_update=False, fai_tp=None,
):
    await taxi_cctv_workers.invalidate_caches(
        clean_update=full_update, cache_names=['guest-fast-append-index'],
    )
    if not fai_tp:
        return {}
    return (await fai_tp.wait_call())['data']


async def _invalidate_and_update_fsi(
        taxi_cctv_workers, full_update=False, fsi_tp=None,
):
    await taxi_cctv_workers.invalidate_caches(
        clean_update=full_update, cache_names=['guest-fast-search-index'],
    )
    if not fsi_tp:
        return {}
    return (await fsi_tp.wait_call())['data']


@pytest.mark.config(CCTV_WORKERS_PG_CACHES=CCTV_WORKERS_PG_CACHES_CONFIG)
@pytest.mark.config(
    CCTV_WORKERS_IDENTIFICATION_THRESHOLD={
        'assume_similar': 0.0,
        'assume_different': 0.0,
    },
)
async def test_guest_fai_update(
        taxi_cctv_workers, pgsql, testpoint, mocked_time, load_json,
):
    @testpoint('guest_fast_append_index_update_tp')
    def _guest_fai_update_testpoint(data):
        pass

    @testpoint('identification-events')
    def _identify_person(data):
        signatures = pgsql_helpers.get_face_signatures(pgsql)
        assert int(data['person']) in signatures

    @testpoint('guest_fast_search_index_update_tp')
    def _guest_fsi_index_update_testpoint(data):
        pass

    @testpoint('guest_fast_search_index_storage_update_tp')
    def _guest_fsi_storage_update_testpoint(data):
        pass

    def flush_all_testpoints():
        _guest_fai_update_testpoint.flush()
        _identify_person.flush()
        _guest_fsi_index_update_testpoint.flush()
        _guest_fsi_storage_update_testpoint.flush()

    await taxi_cctv_workers.enable_testpoints()

    # ***** Step 1 - charge DB with new signatures  *****
    # 1.1 clean database
    # clean database with signatures and corresponding indexes
    pgsql_helpers.clear_face_signatures_table(pgsql)
    await taxi_cctv_workers.invalidate_caches(
        clean_update=True,
        cache_names=['guest-fast-search-index', 'guest-fast-append-index'],
    )
    flush_all_testpoints()

    input_data = load_json('events_step1.json')
    input_events = input_data['events']

    # 1.2 set now
    mocked_time.set(utils.parse_date_str(input_data['now']))
    # 1.3. invalidate and clean all caches to distribute time value.
    # and check FAI-index is empty
    index_data = await _invalidate_and_update_fai(
        taxi_cctv_workers, True, _guest_fai_update_testpoint,
    )
    assert not index_data['fixed_part']
    assert len(index_data['append_part']['chunks']) == 1
    assert not index_data['append_part']['chunks'][0]
    # 1.3 push events
    for event in input_events:
        await _send_detection_event(taxi_cctv_workers, event, _identify_person)
    # 1.4 invalidate FSI
    await _invalidate_and_update_fsi(
        taxi_cctv_workers, False, _guest_fsi_storage_update_testpoint,
    )
    # 1.5 invalidate FAI, and try to check items
    index_data = await _invalidate_and_update_fai(
        taxi_cctv_workers, False, _guest_fai_update_testpoint,
    )
    assert (
        len(index_data['fixed_part']) == input_data['expected_fixed_part_size']
    )
    assert len(index_data['append_part']['chunks']) == 2
    assert (
        len(index_data['append_part']['chunks'][0])
        == input_data['expected_append_part_size']
    )
    assert not index_data['append_part']['chunks'][1]

    # ***** Step 2 - add new signatures, update  FAI *****
    input_data = load_json('events_step2.json')
    input_events = input_data['events']

    # 2.1 set now
    mocked_time.set(utils.parse_date_str(input_data['now']))
    # 2.2 push events
    for event in input_events:
        await _send_detection_event(taxi_cctv_workers, event, _identify_person)
    # 2.3 invalidate FSI
    await _invalidate_and_update_fsi(
        taxi_cctv_workers, False, _guest_fsi_storage_update_testpoint,
    )
    # 2.4 invalidate FAI, and try to check items
    index_data = await _invalidate_and_update_fai(
        taxi_cctv_workers, False, _guest_fai_update_testpoint,
    )
    assert (
        len(index_data['fixed_part']) == input_data['expected_fixed_part_size']
    )
    assert len(index_data['append_part']['chunks']) == 3
    assert not index_data['append_part']['chunks'][2]
    append_part_len = functools.reduce(
        operator.add, map(len, index_data['append_part']['chunks']),
    )
    assert append_part_len == input_data['expected_append_part_size']

    # ***** Step 3 - add new signatures, update  FAI *****
    input_data = load_json('events_step3.json')
    input_events = input_data['events']

    # 3.1 set now
    mocked_time.set(utils.parse_date_str(input_data['now']))
    # 3.2 push events
    for event in input_events:
        await _send_detection_event(taxi_cctv_workers, event, _identify_person)
    # 3.3 invalidate FSI
    await _invalidate_and_update_fsi(
        taxi_cctv_workers, False, _guest_fsi_storage_update_testpoint,
    )
    # 3.4 invalidate FAI, and try to check items
    index_data = await _invalidate_and_update_fai(
        taxi_cctv_workers, False, _guest_fai_update_testpoint,
    )
    assert (
        len(index_data['fixed_part']) == input_data['expected_fixed_part_size']
    )
    assert len(index_data['append_part']['chunks']) == 2
    assert not index_data['append_part']['chunks'][1]
    append_part_len = functools.reduce(
        operator.add, map(len, index_data['append_part']['chunks']),
    )
    assert append_part_len == input_data['expected_append_part_size']

    # ***** Step 4 - add new signatures, update FSI and FAI *****
    input_data = load_json('events_step4.json')

    # 4.1 set now
    mocked_time.set(utils.parse_date_str(input_data['now']))

    # 2.3 invalidate FSI
    await _invalidate_and_update_fsi(
        taxi_cctv_workers, False, _guest_fsi_storage_update_testpoint,
    )
    await _guest_fsi_index_update_testpoint.wait_call()
    # 2.4 invalidate FAI
    # expect it to be empty
    index_data = await _invalidate_and_update_fai(
        taxi_cctv_workers, False, _guest_fai_update_testpoint,
    )
    assert (
        len(index_data['fixed_part']) == input_data['expected_fixed_part_size']
    )
    assert len(index_data['append_part']['chunks']) == 2
    assert not index_data['append_part']['chunks'][1]
    append_part_len = functools.reduce(
        operator.add, map(len, index_data['append_part']['chunks']),
    )
    assert append_part_len == input_data['expected_append_part_size']
