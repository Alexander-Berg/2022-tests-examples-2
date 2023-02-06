import json

import pytest

HANDLE = 'v1/rules/match/'


def _get_ids(json_value):
    return {'match': set(x['id'] for x in json_value['match'])}


def get_ids(response):
    return _get_ids(json.loads(response.content))


async def test_get_ids():
    assert _get_ids(
        {'match': [{'id': 123, 'foo': 'bar'}, {'id': 456, 'kaka': 'byaka'}]},
    ) == {'match': {123, 456}}


@pytest.mark.servicetest
async def test_match_bad_req(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(HANDLE, {})
    assert response.status_code == 400


@pytest.mark.servicetest
async def test_match_empty_result(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-02T22:00:22.000Z',
            'zone_name': 'neverland',
            'time_zone': 'UTC',
        },
    )
    assert response.status_code == 200
    assert json.loads(response.content) == {'match': []}


@pytest.mark.servicetest
async def test_on_top_minimum(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-04-04T01:00:00.000Z',  # 01 UTC -> 06 YEKT
            'time_zone': 'Asia/Yekaterinburg',
            'zone_name': 'zone1',
            'rule_types': ['on_top'],
        },
    )
    assert response.status_code == 200
    assert json.loads(response.content) == {
        'match': [
            {
                'id': '000000000000000000000201',
                'rule_type': 'on_top',
                'sum': 9.99,
                'currency': 'RUB',
                'zone_name': 'zone1',
                'start': '2020-04-01T05:00:00+00:00',
                'end': '2020-05-01T05:00:00+00:00',
                'local_hours': [],
                'local_days_of_week': [],
                'tariff_class': [],
                'is_personal': False,
            },
        ],
    }


@pytest.mark.servicetest
async def test_mfg_minimum(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-04-04T01:00:00.000Z',  # 01 UTC -> 06 YEKT
            'time_zone': 'Asia/Yekaterinburg',
            'zone_name': 'zone1',
            'rule_types': ['mfg'],
        },
    )
    assert response.status_code == 200
    assert json.loads(response.content) == {
        'match': [
            {
                'id': '000000000000000000000202',
                'rule_type': 'mfg',
                'sum': 8.88,
                'currency': 'RUB',
                'zone_name': 'zone1',
                'start': '2020-04-01T05:00:00+00:00',
                'end': '2020-05-01T05:00:00+00:00',
                'local_hours': [],
                'local_days_of_week': [],
                'tariff_class': [],
                'is_personal': False,
            },
        ],
    }


@pytest.mark.servicetest
async def test_on_top_maximum(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-04-04T01:00:00.000Z',
            'time_zone': 'Asia/Yekaterinburg',
            'zone_name': 'zone2',
            'activity_points': 99,
            'tariff_class': 'econom',
            'tags': ['tag1', 'tag2'],
            'rule_types': ['on_top'],
        },
    )
    assert response.status_code == 200
    assert json.loads(response.content) == {
        'match': [
            {
                'id': '000000000000000000000211',
                'group_id': 'group211',
                'rule_type': 'on_top',
                'sum': 9.99,
                'currency': 'RUB',
                'zone_name': 'zone2',
                'start': '2020-04-01T05:00:00+00:00',
                'end': '2020-05-01T05:00:00+00:00',
                'tariff_class': ['econom'],
                'local_hours': [0, 1, 2, 3, 4, 5, 6, 7],
                'local_days_of_week': ['sat', 'sun'],
                'order_payment_type': 'card',
                'geoareas': ['geo1', 'geo2'],
                'tags': ['tag1', 'tag2'],
                'is_personal': False,
            },
        ],
    }


@pytest.mark.servicetest
async def test_mfg_maximum(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-04-04T01:00:00.000Z',
            'time_zone': 'Asia/Yekaterinburg',
            'zone_name': 'zone2',
            'activity_points': 99,
            'tariff_class': 'econom',
            'rule_types': ['mfg'],
            'tags': ['tag1', 'tag2', 'tag3'],
        },
    )
    assert response.status_code == 200
    assert json.loads(response.content) == {
        'match': [
            {
                'id': '000000000000000000000212',
                'group_id': 'group212',
                'rule_type': 'mfg',
                'sum': 8.88,
                'currency': 'RUB',
                'zone_name': 'zone2',
                'start': '2020-04-01T05:00:00+00:00',
                'end': '2020-05-01T05:00:00+00:00',
                'tariff_class': ['econom'],
                'local_hours': [0, 1, 2, 3, 4, 5, 6, 7],
                'local_days_of_week': ['sat', 'sun'],
                'order_payment_type': 'cash',
                'geoareas': ['geo3'],
                'tags': ['tag1'],
                'is_personal': False,
            },
        ],
    }


@pytest.mark.servicetest
async def test_match_on_top(taxi_billing_subventions_x):
    # type=add is_once=false kind=null
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-01-10T01:00:00.000Z',  # 01 UTC -> 06 YEKT
            'time_zone': 'Asia/Yekaterinburg',
            'zone_name': 'ekb',
            'rule_types': ['on_top'],
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {'match': {'000000000000000000000010'}}


@pytest.mark.servicetest
async def test_budget(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-01-10T01:00:00.000Z',  # 01 UTC -> 06 YEKT
            'time_zone': 'Asia/Yekaterinburg',
            'zone_name': 'ekb',
            'rule_types': ['on_top'],
        },
    )
    assert response.status_code == 200
    match = json.loads(response.content)['match']
    assert match[0].get('budget_id') == '0001'


@pytest.mark.servicetest
async def test_match_mfg(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-01-10T00:00:00.000Z',
            'time_zone': 'Asia/Yekaterinburg',
            'zone_name': 'ekb',
            'rule_types': ['mfg'],
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {'match': {'000000000000000000000020'}}


@pytest.mark.servicetest
async def test_match_all_rule_types(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-01-10T00:00:00.000Z',
            'time_zone': 'Asia/Yekaterinburg',
            'zone_name': 'ekb',
            'rule_types': ['mfg', 'on_top'],
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {
        'match': {'000000000000000000000010', '000000000000000000000020'},
    }


@pytest.mark.servicetest
async def test_match_all_rule_types_by_default(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-01-10T00:00:00.000Z',
            'time_zone': 'Asia/Yekaterinburg',
            'zone_name': 'ekb',
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {
        'match': {'000000000000000000000010', '000000000000000000000020'},
    }


@pytest.mark.servicetest
async def test_match_booking_geo(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-01-10T00:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'bulkcity',
            'rule_types': ['booking_geo'],
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {
        'match': {'000000000000000000000301', '000000000000000000000302'},
    }


@pytest.mark.servicetest
async def test_match_do_x_get_y(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-01-10T00:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'bulkcity',
            'rule_types': ['do_x_get_y'],
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {'match': {'group401'}}


@pytest.mark.servicetest
async def test_match_driver_fix(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-01-10T00:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'bulkcity',
            'driver_fix_rule_id': '000000000000000000000601',
            'rule_types': ['driver_fix'],
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {'match': {'000000000000000000000601'}}
