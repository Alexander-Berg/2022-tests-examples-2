# pylint: disable=import-only-modules
import datetime

import pytest

import tests_cctv_admin.utils as utils

CCTV_ADMIN_MONGO_CACHES_CONFIG = {
    '__default__': {
        'full_update': {'correction_ms': 10000},
        'incremental_update': {'correction_ms': 1000},
    },
    'processor-configs-cache': {
        'full_update': {'correction_ms': 10000},
        'incremental_update': {'correction_ms': 10000},
    },
}

NEW_PROCESSOR = {
    '_id': 'processorN',
    'cameras': ['camera_01'],
    'hostname': 'processor.one.com',
}


def _convert_updated_ts(input_configs):
    for item in input_configs:
        item['updated_ts'] = utils.date_to_ms(
            utils.parse_date_str(item['updated_ts']),
        )


def _convert_to_expected(input_configs):
    result = dict()
    for item in input_configs:
        result[item['_id']] = {
            'hostname': item['hostname'],
            'cameras': item['cameras'],
            'updated_ts': item['updated_ts'],
        }
    return result


@pytest.mark.config(CCTV_ADMIN_MONGO_CACHES=CCTV_ADMIN_MONGO_CACHES_CONFIG)
@pytest.mark.parametrize('input_file', [pytest.param('test_cache.json')])
async def test_cache(
        taxi_cctv_admin,
        mongodb,
        mocked_time,
        load_json,
        input_file,
        testpoint,
):
    await taxi_cctv_admin.invalidate_caches(clean_update=True)

    mongodb.cctv_processors.remove({})

    @testpoint('processor_configs_cache_tp')
    def _processor_config_cache_testpoint(data):
        pass

    await taxi_cctv_admin.enable_testpoints()
    _processor_config_cache_testpoint.flush()

    input_data = load_json(input_file)
    initial_value = input_data.get('storage')

    mocked_now = utils.parse_date_str(input_data['now'])
    mocked_time.set(mocked_now)
    await taxi_cctv_admin.invalidate_caches(clean_update=True)
    _processor_config_cache_testpoint.flush()
    _convert_updated_ts(initial_value)

    if initial_value:
        mongodb.cctv_processors.insert(initial_value)

    await taxi_cctv_admin.invalidate_caches(clean_update=True)
    result = await _processor_config_cache_testpoint.wait_call()

    assert result['data']['is_full_update']
    assert result['data']['configs'] == _convert_to_expected(initial_value)

    NEW_PROCESSOR['updated_ts'] = utils.date_to_ms(
        mocked_now - datetime.timedelta(milliseconds=100),
    )
    mongodb.cctv_processors.insert(NEW_PROCESSOR)
    initial_value.append(NEW_PROCESSOR)
    await taxi_cctv_admin.invalidate_caches(clean_update=False)
    result = await _processor_config_cache_testpoint.wait_call()

    assert not result['data']['is_full_update']
    assert result['data']['configs'] == _convert_to_expected(initial_value)
