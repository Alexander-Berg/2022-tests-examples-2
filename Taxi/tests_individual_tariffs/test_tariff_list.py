# flake8: noqa E501

import datetime

import bson
import pytest


def _normalize_tariff_zones(resp):
    for each in resp['tariffs']:
        each['categories'].sort()
    resp['tariffs'].sort(key=lambda x: x['home_zone'])
    return resp


@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.parametrize(
    'active_time, expected_tariffs_id, request_mode',
    [
        (
            '2019-01-03T00:00:00+00:00',
            ['000000000000000000000002', '5d2374698f19ce8fc02b5c8f'],
            None,
        ),
        ('2000-01-01T11:13:11+00:00', [], None),
        (
            '2100-01-01T11:13:11+00:00',
            ['000000000000000000000002', '5d16326a4885018919768989'],
            None,
        ),
        (
            '2019-01-03T00:00:00+00:00',
            [
                '000000000000000000000002',
                '5d16326a4885018919768989',
                '5d2374698f19ce8fc02b5c8f',
            ],
            'active_and_future',
        ),
    ],
)
@pytest.mark.experiments3(filename='mongo_config_mapping.json')
async def test_v1_get_tariff_list(
        taxi_individual_tariffs,
        active_time,
        expected_tariffs_id,
        request_mode,
):
    request = {'active_at_time': active_time}
    if request_mode:
        request.update({'request_mode': request_mode})
    response = await taxi_individual_tariffs.post(
        '/internal/v1/tariffs/list', json=request,
    )
    assert response.status_code == 200
    resp = response.json()
    tariffs_id = [tariff['id'] for tariff in resp['tariffs']]
    assert sorted(tariffs_id) == expected_tariffs_id


@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.experiments3(filename='mongo_config_mapping.json')
async def test_v1_get_tariff_list_after_cache_update(
        taxi_individual_tariffs, mongodb,
):
    request = {'active_at_time': '2019-01-03T00:00:00+00:00'}

    response = await taxi_individual_tariffs.post(
        '/internal/v1/tariffs/list', request,
    )
    assert response.status_code == 200
    resp = response.json()
    tariffs_id = [tariff['id'] for tariff in resp['tariffs']]
    assert sorted(tariffs_id) == [
        '000000000000000000000002',
        '5d2374698f19ce8fc02b5c8f',
    ]

    update_result = mongodb.tariffs.update_one(
        {'_id': bson.ObjectId('000000000000000000000001')},
        {
            '$set': {
                'date_to': datetime.datetime(2022, 1, 1),
                'updated': datetime.datetime(2021, 1, 1),
            },
        },
    )
    assert update_result.modified_count == 1
    await taxi_individual_tariffs.invalidate_caches(clean_update=False)
    response = await taxi_individual_tariffs.post(
        '/internal/v1/tariffs/list', request,
    )
    assert response.status_code == 200
    resp = response.json()
    tariffs_id = [tariff['id'] for tariff in resp['tariffs']]
    assert sorted(tariffs_id) == [
        '000000000000000000000001',
        '000000000000000000000002',
        '5d2374698f19ce8fc02b5c8f',
    ]


@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.parametrize(
    'tariff_ids, expected_tariffs',
    [
        (
            ['000000000000000000000001', '000000000000000000000002'],
            ['000000000000000000000001', '000000000000000000000002'],
        ),
        (
            [
                '000000000000000000000001',
                '000000000000000000000002',
                '5d16326a4885018919768989',
            ],
            [
                '000000000000000000000001',
                '000000000000000000000002',
                '5d16326a4885018919768989',
            ],
        ),
        ([], []),
        (
            ['000000000000000000000000', '000000000000000000000001'],
            ['000000000000000000000001'],
        ),
    ],
    ids=[
        'two_tariffs',
        'three_tariffs',
        'zero_tariffs',
        'two_tariffs_one_invalid',
    ],
)
@pytest.mark.experiments3(filename='mongo_config_mapping.json')
async def test_v1_tariff_list_bulk(
        taxi_individual_tariffs, tariff_ids, expected_tariffs,
):
    request = {'tariff_ids': tariff_ids}
    response = await taxi_individual_tariffs.post(
        '/internal/v1/tariffs/list_bulk', request,
    )
    assert response.status_code == 200
    resp = response.json()
    tariffs_id = [tariff['id'] for tariff in resp['tariffs']]
    assert sorted(tariffs_id) == expected_tariffs


EMPTY_RESPONSE_FILE_NAME = 'empty.json'
TARIFF_ZONES_HANDLE = '/internal/v1/tariff-zones'
SUMMARY_HANDLE = '/internal/v1/tariffs/summary'


@pytest.mark.parametrize(
    'current_time, response_filename, summary_response_filename',
    [
        (
            '2019-01-03T00:00:00+00:00',
            'moscow_tel_aviv.json',
            'summary_moscow_tel_aviv.json',
        ),
        (
            '2000-01-01T11:13:11+00:00',
            EMPTY_RESPONSE_FILE_NAME,
            EMPTY_RESPONSE_FILE_NAME,
        ),
        (
            '2100-01-01T11:13:11+00:00',
            'moscow_spb.json',
            'summary_moscow_spb.json',
        ),
    ],
)
@pytest.mark.parametrize('handle', [TARIFF_ZONES_HANDLE, SUMMARY_HANDLE])
@pytest.mark.experiments3(filename='mongo_config_mapping.json')
async def test_v1_get_actual_tariff_zones(
        taxi_individual_tariffs,
        mocked_time,
        load_json,
        current_time,
        handle,
        response_filename,
        summary_response_filename,
):
    mocked_time.set(datetime.datetime.fromisoformat(current_time))
    await taxi_individual_tariffs.invalidate_caches()
    response = await taxi_individual_tariffs.get(handle, params={})
    assert response.status_code == 200
    resp = response.json()
    if handle == TARIFF_ZONES_HANDLE:
        expected = load_json(response_filename)
    else:
        expected = load_json(summary_response_filename)
    assert _normalize_tariff_zones(resp) == _normalize_tariff_zones(expected)


@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.parametrize(
    'at_time, response_filename, summary_response_filename',
    [
        (
            '2000-01-01T11:13:11+00:00',
            EMPTY_RESPONSE_FILE_NAME,
            EMPTY_RESPONSE_FILE_NAME,
        ),
        (
            '2015-07-05T11:13:11+00:00',
            'moscow_only.json',
            'summary_moscow_only.json',
        ),
        (
            '2019-01-02T23:13:11+00:00',
            'moscow_tel_aviv.json',
            'summary_moscow_tel_aviv.json',
        ),
        (
            '2019-07-05T11:13:11+00:00',
            'moscow_spb.json',
            'summary_moscow_spb.json',
        ),
    ],
)
@pytest.mark.parametrize('handle', [TARIFF_ZONES_HANDLE, SUMMARY_HANDLE])
@pytest.mark.experiments3(filename='mongo_config_mapping.json')
async def test_v1_get_tariff_zones_at_time(
        taxi_individual_tariffs,
        load_json,
        at_time,
        response_filename,
        handle,
        summary_response_filename,
):
    response = await taxi_individual_tariffs.get(
        handle, params={'active_at_time': at_time},
    )
    assert response.status_code == 200
    resp = response.json()
    if handle == TARIFF_ZONES_HANDLE:
        expected = load_json(response_filename)
    else:
        expected = load_json(summary_response_filename)
    assert _normalize_tariff_zones(resp) == _normalize_tariff_zones(expected)


@pytest.mark.now('2019-01-03T00:00:00Z')
@pytest.mark.parametrize(
    'country, response_filename, summary_response_filename',
    [
        (None, 'moscow_tel_aviv.json', 'summary_moscow_tel_aviv.json'),
        ('rus', 'moscow_filtered.json', 'summary_moscow_filtered.json'),
        ('isr', 'tel_aviv_filtered.json', 'summary_tel_aviv_filtered.json'),
        ('ukr', EMPTY_RESPONSE_FILE_NAME, EMPTY_RESPONSE_FILE_NAME),
    ],
)
@pytest.mark.parametrize('handle', [TARIFF_ZONES_HANDLE, SUMMARY_HANDLE])
@pytest.mark.experiments3(filename='mongo_config_mapping.json')
async def test_v1_get_tariff_zones_filter_by_country(
        taxi_individual_tariffs,
        load_json,
        country,
        response_filename,
        handle,
        summary_response_filename,
):
    params = {}
    if country:
        params.update({'country': country})

    response = await taxi_individual_tariffs.get(handle, params=params)

    assert response.status_code == 200
    resp = response.json()
    if handle == TARIFF_ZONES_HANDLE:
        expected = load_json(response_filename)
    else:
        expected = load_json(summary_response_filename)
    assert _normalize_tariff_zones(resp) == _normalize_tariff_zones(expected)


@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.parametrize(
    'filters, response_filename',
    [
        (
            {
                'city_ids': '\\u941c\\u043e\\u0441\\u043a\\u0432\\u0430,\\u041c\\u043e\\u0441\\u043a\\u0432\\u0430',
            },
            'summary_moscow_spb.json',
        ),
        (
            {'city_ids': '99999999999999999999999'},  # invalid id
            EMPTY_RESPONSE_FILE_NAME,
        ),
        (
            {
                'active_at_time': '2015-07-05T11:13:11+00:00',
                'zone_names': 'moscow',
            },
            'summary_moscow_only.json',
        ),
        ({'zone_names': 'moscow,spb'}, 'summary_moscow_spb.json'),
        (
            {
                'active_at_time': '2015-07-05T11:13:11+00:00',
                'city_ids': '\\u941c\\u043e\\u0441\\u043a\\u0432\\u0430,\\u041c\\u043e\\u0441\\u043a\\u0432\\u0430',
                'zone_names': 'moscow',
            },
            'summary_moscow_only.json',
        ),
        (
            {
                'city_ids': (
                    '\\u941c\\u043e\\u0441\\u043a\\u0432\\u0430'
                ),  # spb
                'zone_names': 'moscow',
            },
            EMPTY_RESPONSE_FILE_NAME,
        ),
    ],
)
@pytest.mark.experiments3(filename='mongo_config_mapping.json')
async def test_v1_post_tariffs_summary_filtered(
        taxi_individual_tariffs, load_json, filters, response_filename,
):
    response = await taxi_individual_tariffs.get(
        '/internal/v1/tariffs/summary', params=filters,
    )
    assert response.status_code == 200
    resp = response.json()
    expected = load_json(response_filename)
    assert _normalize_tariff_zones(resp) == _normalize_tariff_zones(expected)


@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.parametrize(
    'exp_match_value',
    [
        {'enabled': False},
        {'enabled': True},
        {'enabled': True, 'value': 'no-cache'},
        {'enabled': True, 'value': 'max-age=60'},
    ],
)
@pytest.mark.parametrize('handle', [TARIFF_ZONES_HANDLE, SUMMARY_HANDLE])
@pytest.mark.experiments3(filename='mongo_config_mapping.json')
async def test_v1_get_tariff_zones_cache_control(
        taxi_individual_tariffs, experiments3, exp_match_value, handle,
):
    experiments3.add_config(
        match={'enabled': True, 'predicate': {'type': 'true'}},
        clauses=[{'value': exp_match_value, 'predicate': {'type': 'true'}}],
        name='individual_tariffs_handlers_cache_control',
        consumers=['individual-tariffs/handler-internal_v1_tariff_zones-get'],
    )
    await taxi_individual_tariffs.invalidate_caches()
    response = await taxi_individual_tariffs.get(handle, params={})
    assert response.status_code == 200
    assert response.headers.get('Cache-Control') == exp_match_value.get(
        'value',
    )
