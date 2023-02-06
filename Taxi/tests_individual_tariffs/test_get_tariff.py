import datetime

import pytest

from tests_plugins import json_util


@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.parametrize(
    'tariff_id, expected_code, response_filename, overrides',
    [
        (
            '000000000000000000000123',
            404,
            'tariff_not_found.json',
            {'message': 'Tariff with id 000000000000000000000123 not found'},
        ),
        ('000000000000000000000001', 200, '000000000000000000000001.json', {}),
    ],
)
@pytest.mark.experiments3(filename='mongo_config_mapping.json')
async def test_v1_get_tariff(
        taxi_individual_tariffs,
        load_json,
        tariff_id,
        expected_code,
        response_filename,
        overrides,
):
    response = await taxi_individual_tariffs.get(
        '/internal/v1/tariff', params={'id': tariff_id},
    )
    assert response.status_code == expected_code

    expected_json = load_json(
        response_filename, object_hook=json_util.VarHook(overrides),
    )
    assert response.json() == expected_json


@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.experiments3(filename='mongo_config_mapping.json')
@pytest.mark.filldb(tariffs='empty')
async def test_v1_get_tariff_mongo_fallback(
        taxi_individual_tariffs, load_json, mongodb,
):
    response = await taxi_individual_tariffs.get(
        '/internal/v1/tariff', params={'id': '000000000000000000000001'},
    )
    assert response.status_code == 404
    for tariff in load_json('db_tariffs.json'):
        mongodb.tariffs.insert(tariff)
    response = await taxi_individual_tariffs.get(
        '/internal/v1/tariff', params={'id': '000000000000000000000001'},
    )
    assert response.status_code == 200


@pytest.mark.parametrize(
    'current_time, expected_code, response_filename, overrides',
    [
        (
            '2000-01-01T11:13:11+00:00',
            404,
            'tariff_not_found.json',
            {'message': 'Tariff for zone moscow not found'},
        ),
        (
            '2015-07-05T11:13:11+00:00',
            200,
            '000000000000000000000001.json',
            {},
        ),
        (
            '2020-07-05T11:13:11+00:00',
            200,
            '000000000000000000000002.json',
            {},
        ),
    ],
)
@pytest.mark.experiments3(filename='mongo_config_mapping.json')
async def test_v1_get_actual_tariff_by_zone(
        taxi_individual_tariffs,
        load_json,
        mocked_time,
        current_time,
        expected_code,
        response_filename,
        overrides,
):
    mocked_time.set(datetime.datetime.fromisoformat(current_time))
    await taxi_individual_tariffs.invalidate_caches()

    response = await taxi_individual_tariffs.get(
        '/internal/v1/tariff-by-zone', params={'zone': 'moscow'},
    )
    assert response.status_code == expected_code

    expected_json = load_json(
        response_filename, object_hook=json_util.VarHook(overrides),
    )
    assert response.json() == expected_json


@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.parametrize(
    'at_time, expected_code, response_filename, overrides',
    [
        (
            '2000-01-01T11:13:11+00:00',
            404,
            'tariff_not_found.json',
            {'message': 'Tariff for zone moscow not found'},
        ),
        (
            '2015-07-05T11:13:11+00:00',
            200,
            '000000000000000000000001.json',
            {},
        ),
        (
            '2020-07-05T11:13:11+00:00',
            200,
            '000000000000000000000002.json',
            {},
        ),
    ],
)
@pytest.mark.parametrize(
    'read_from_mongo', [False, True], ids=['use_cache', 'read_db'],
)
@pytest.mark.experiments3(filename='mongo_config_mapping.json')
async def test_v1_get_tariff_by_zone_at_time(
        taxi_individual_tariffs,
        load_json,
        at_time,
        expected_code,
        response_filename,
        overrides,
        read_from_mongo,
):
    params = {'zone': 'moscow', 'active_at_time': at_time}
    if read_from_mongo:
        params.update({'version': 'latest'})

    response = await taxi_individual_tariffs.get(
        '/internal/v1/tariff-by-zone', params=params,
    )
    assert response.status_code == expected_code

    expected_json = load_json(
        response_filename, object_hook=json_util.VarHook(overrides),
    )
    assert response.json() == expected_json
