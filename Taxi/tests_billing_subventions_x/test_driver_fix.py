import json

import pytest

HANDLE = 'v1/rules/match/'

# 2020-01-31T12:00:00 -> 1580461200000 start1
# 2020-02-01T12:00:00 -> 1580547600000 pit1
# 2020-02-02T12:00:00 -> 1580634000000 end1, start2
# 2020-02-03T12:00:00 -> 1580720400000 pit2
# 2020-02-04T12:00:00 -> 1580806800000 end2
# 2020-02-05T12:00:00 -> 1580893200000 pit3


def get_ids(response):
    ret = json.loads(response.content)
    return sorted([x['id'].lower() for x in ret['match']])


@pytest.mark.servicetest
async def test_driver_fix_fields(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'zone_name': 'zone1',
            'driver_fix_rule_id': '000000000000000000000101',
            'reference_time': '2020-02-01T12:00:00.000Z',
            'time_zone': 'UTC',
            'rule_types': ['driver_fix'],
        },
    )
    assert response.status_code == 200
    ret = json.loads(response.content)
    assert ret['match']
    rec = ret['match'][0]
    assert rec['profile_tariff_classes'] == ['econom']
    assert rec['profile_payment_type_restrictions'] == 'any'
    assert rec['commission_rate_if_fraud'] == '99.99'
    assert rec['rates'] == [
        {'week_day': 'mon', 'start': '00:10', 'rate_per_minute': '12.11'},
        {'week_day': 'tue', 'start': '02:20', 'rate_per_minute': '12.22'},
        {'week_day': 'wed', 'start': '04:30', 'rate_per_minute': '12.33'},
        {'week_day': 'thu', 'start': '06:40', 'rate_per_minute': '12.44'},
        {'week_day': 'fri', 'start': '08:50', 'rate_per_minute': '12.55'},
        {'week_day': 'sat', 'start': '10:11', 'rate_per_minute': '12.66'},
        {'week_day': 'sun', 'start': '12:21', 'rate_per_minute': '12.77'},
    ]


@pytest.mark.servicetest
async def test_driver_fix_match(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-01T12:00:00.000Z',  # pit1
            'time_zone': 'UTC',
            'driver_fix_rule_id': '000000000000000000000101',
            'rule_types': ['driver_fix'],
            'zone_name': 'zone1',
            'profile_tariff_classes': ['econom'],
            'profile_payment_type_restrictions': 'none',
            'tags': ['foo', 'bar'],
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == ['000000000000000000000101']


@pytest.mark.servicetest
async def test_driver_fix_ignore_filters(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-01T12:00:00.000Z',  # pit1
            'time_zone': 'UTC',
            'driver_fix_rule_id': '000000000000000000000101',
            'rule_types': ['driver_fix'],
            'zone_name': 'zone1',
            'profile_tariff_classes': ['comfort'],
            'profile_payment_type_restrictions': 'none',
            'tags': ['foo', 'bar'],
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == ['000000000000000000000101']


@pytest.mark.servicetest
async def test_driver_fix_active_id(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-01T12:00:00.000Z',  # pit1
            'time_zone': 'UTC',
            'rule_types': ['driver_fix'],
            'driver_fix_rule_id': '000000000000000000000101',
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == ['000000000000000000000101']


@pytest.mark.servicetest
async def test_ignore_disable_all_tag(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-01T12:00:00.000Z',  # pit1
            'time_zone': 'UTC',
            'rule_types': ['driver_fix'],
            'driver_fix_rule_id': '000000000000000000000101',
            'tags': ['subv_disable_all'],
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == ['000000000000000000000101']


@pytest.mark.servicetest
async def test_driver_fix_inactive_id_replaced(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-03T12:00:00.000Z',  # pit2
            'time_zone': 'UTC',
            'rule_types': ['driver_fix'],
            'driver_fix_rule_id': '000000000000000000000101',
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == ['000000000000000000000102']


@pytest.mark.servicetest
async def test_driver_fix_inactive_id_expired(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-02-05T12:00:00.000Z',  # pit3
            'time_zone': 'UTC',
            'rule_types': ['driver_fix'],
            'driver_fix_rule_id': '000000000000000000000101',
            'tags': ['restrictive_tag'],
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == []
