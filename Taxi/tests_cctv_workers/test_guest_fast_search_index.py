import math

import pytest

import tests_cctv_workers.pgsql_helpers as pgsql_helpers
import tests_cctv_workers.utils as utils

CCTV_WORKERS_PG_CACHES_CONFIG = {
    '__default__': {
        'full_update': {'chunk_size': 0, 'correction_ms': 10000},
        'incremental_update': {'chunk_size': 0, 'correction_ms': 1000},
    },
    'guest-fast-search-index': {
        'full_update': {'chunk_size': 0, 'correction_ms': 10000},
        'incremental_update': {'chunk_size': 0, 'correction_ms': 10000},
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


@pytest.mark.parametrize(
    'input_file',
    [
        pytest.param('test_1.json', id='full only update on empty database'),
        pytest.param(
            'test_2.json', id='full+incremental update on empty database',
        ),
        pytest.param(
            'test_3.json', id='full+index only update with correct data',
        ),
        pytest.param(
            'test_4.json',
            id='full+index only update with some incorrect signatures',
        ),
        pytest.param(
            'test_5.json', id='full + incremental update; no index rebuild',
        ),
        pytest.param(
            'test_6.json', id='full + incremental update; with index rebuild',
        ),
    ],
)
@pytest.mark.config(CCTV_WORKERS_PG_CACHES=CCTV_WORKERS_PG_CACHES_CONFIG)
async def test_guest_fsi_update(
        taxi_cctv_workers,
        pgsql,
        testpoint,
        mocked_time,
        load_json,
        input_file,
):
    is_index_to_be_updated = True

    @testpoint('guest_fast_search_index_update_tp')
    def _guest_fsi_index_update_testpoint(data):
        nonlocal is_index_to_be_updated
        assert is_index_to_be_updated

    @testpoint('guest_fast_search_index_storage_update_tp')
    def _guest_fsi_storage_update_testpoint(data):
        pass

    def flush_all_testpoints():
        _guest_fsi_index_update_testpoint.flush()
        _guest_fsi_storage_update_testpoint.flush()

    await taxi_cctv_workers.enable_testpoints()

    input_data = load_json(input_file)

    # ***** Step 'INITIAL' *****
    # 1. clean database
    pgsql_helpers.clear_face_signatures_table(pgsql)
    initial_input = input_data['initial']

    # 2. set now
    mocked_time.set(utils.parse_date_str(initial_input['now']))

    # 3. invalidate and clean all caches to distribute time value.
    # We make full update of the caches to set the mocked time
    # in 'storage_last_updated_ts' value
    await taxi_cctv_workers.invalidate_caches(clean_update=True)

    # 4. flush all testpoints
    flush_all_testpoints()

    # 5. storing data into the persistent storage
    _fill_storage_with_input_data(pgsql, initial_input['storage'])
    stored_data = _load_data_from_storage(pgsql)

    # 6. triggering cache update
    is_index_to_be_updated = True
    await taxi_cctv_workers.invalidate_caches(clean_update=True)
    storage_update_result = (
        await _guest_fsi_storage_update_testpoint.wait_call()
    )['data']
    index_update_result = (
        await _guest_fsi_index_update_testpoint.wait_call()
    )['data']

    # 7. checking index storage content
    storage_update_result = _parse_storage_update_result(storage_update_result)
    _compare_storage_data(storage_update_result['storage'], stored_data)
    expected_storage_updated_ts = utils.parse_date_str(
        initial_input['expected']['storage_last_update_ts'],
    )

    # 8. checking storage version
    assert storage_update_result['updated_ts'] == expected_storage_updated_ts

    # 9. checking index version update result
    index_update_result = _parse_index_update_result(index_update_result)
    expected_index_update_result = _parse_input_json_index_update_result(
        initial_input['expected'],
    )
    assert index_update_result == expected_index_update_result

    # ***** Step 'UPDATE' *****
    update_input = input_data.get('update')
    if not update_input:
        return

    expected_update_input = update_input['expected']
    expected_index_update_result = expected_update_input.get(
        'index_build_statistics',
    )
    is_index_to_be_updated = bool(expected_index_update_result)

    # 1. set now
    mocked_time.set(utils.parse_date_str(update_input['now']))

    # 2. storing data into the persistent storage
    _fill_storage_with_input_data(pgsql, update_input['storage'])
    stored_data = _load_data_from_storage(pgsql)

    # 3. triggering cache update and setting mocked time
    await taxi_cctv_workers.invalidate_caches(clean_update=False)

    # 4. checking index storage containiments
    storage_update_result = (
        await _guest_fsi_storage_update_testpoint.wait_call()
    )['data']

    storage_update_result = _parse_storage_update_result(storage_update_result)
    _compare_storage_data(storage_update_result['storage'], stored_data)
    expected_storage_updated_ts = utils.parse_date_str(
        update_input['expected']['storage_last_update_ts'],
    )

    assert storage_update_result['updated_ts'] == expected_storage_updated_ts

    if is_index_to_be_updated:
        index_update_result = (
            await _guest_fsi_index_update_testpoint.wait_call()
        )['data']

        index_update_result = _parse_index_update_result(index_update_result)
        expected_index_update_result = _parse_input_json_index_update_result(
            update_input['expected'],
        )

        assert index_update_result == expected_index_update_result
