import json

import pytest

HANDLE = 'v1/rules/match/'


@pytest.mark.servicetest
async def test_booking_geo_fields(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'zone_name': 'test_fields',
            'geoareas': ['geo1'],
            'reference_time': '2020-01-23T11:00:11.000Z',
            'time_zone': 'Europe/Moscow',
            'rule_types': ['booking_geo'],
        },
    )
    assert response.status_code == 200
    ret = json.loads(response.content)
    assert ret['match']
    rec = ret['match'][0]
    assert 'workshift' in rec
    assert 'start' in rec['workshift']
    assert 'duration' in rec['workshift']
    assert 'payment_type' in rec
    assert 'geoareas' in rec
    assert 'has_commission' in rec
    assert 'profile_payment_type_restrictions' in rec
    assert 'min_online_minutes' in rec
    assert 'rate_free_per_minute' in rec
    assert 'rate_on_order_per_minute' in rec
    assert 'is_relaxed_order_time_matching' in rec
    assert 'is_relaxed_income_matching' in rec
    assert 'budget_holder' in rec


@pytest.mark.servicetest
async def test_booking_geo_omitted_relaxed_income(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-01-23T11:00:11.000Z',
            'time_zone': 'Europe/Moscow',
            'rule_types': ['booking_geo'],
            'zone_name': 'missing_is_relaxed_income_matching',
        },
    )
    assert response.status_code == 200
    rec = json.loads(response.content)['match'][0]
    assert rec['is_relaxed_income_matching'] is True


@pytest.mark.servicetest
async def test_booking_geo_omitted_relaxed_order_time(
        taxi_billing_subventions_x,
):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-01-23T11:00:11.000Z',
            'time_zone': 'Europe/Moscow',
            'rule_types': ['booking_geo'],
            'zone_name': 'missing_is_relaxed_order_time_matching',
        },
    )
    assert response.status_code == 200
    rec = json.loads(response.content)['match'][0]
    assert rec['is_relaxed_order_time_matching'] is False


@pytest.mark.servicetest
async def test_booking_geo_omitted_payment_restrictions(
        taxi_billing_subventions_x,
):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-01-23T11:00:11.000Z',
            'time_zone': 'Europe/Moscow',
            'rule_types': ['booking_geo'],
            'zone_name': 'missing_profile_payment_type_restrictions',
        },
    )
    assert response.status_code == 200
    rec = json.loads(response.content)['match'][0]
    assert rec['profile_payment_type_restrictions'] == 'any'


@pytest.mark.parametrize(
    'zone, errmsg',
    [
        ['missing_workshift', 'omitted workshift'],
        ['missing_min_online_minutes', 'omitted min_online_minutes'],
        ['missing_rate_free_per_minute', 'omitted rate_free_per_minute'],
        [
            'missing_rate_on_order_per_minute',
            'omitted rate_on_order_per_minute',
        ],
        ['missing_geoareas', 'omitted geoareas'],
        ['empty_geoareas', 'empty geoareas'],
    ],
)
@pytest.mark.servicetest
async def test_booking_geo_bad_records(
        taxi_billing_subventions_x, zone, errmsg,
):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-01-23T11:00:11.000Z',
            'time_zone': 'Europe/Moscow',
            'rule_types': ['booking_geo'],
            'zone_name': zone,
        },
    )
    assert response.status_code == 500
    # TODO add caplogging here after ticket `TAXIDATA 1549` is finished.


@pytest.mark.parametrize(
    'query, expected_rule_ids',
    [
        pytest.param(
            {
                'reference_time': '2020-01-23T11:00:11.000Z',
                'time_zone': 'Europe/Moscow',
                'rule_types': ['booking_geo'],
                'zone_name': 'test_match',
                # must be ignored because of geo_booking
                'tariff_class': 'business',
                'order_payment_type': 'card',
                'driver_branding': 'sticker',
            },
            [
                '000000000000000000000301',
                '000000000000000000000302',
                '000000000000000000000303',
                '000000000000000000000304',
                '000000000000000000000305',
            ],
            id='ignore not interesting fields',
        ),
        pytest.param(
            {
                'reference_time': '2020-01-23T04:59:00.000Z',
                'time_zone': 'Europe/Moscow',
                'rule_types': ['booking_geo'],
                'zone_name': 'test_match',
            },
            ['000000000000000000000305'],
            id='honor to workshift',
        ),
        pytest.param(
            {
                'reference_time': '2020-01-23T11:00:11.000Z',
                'time_zone': 'Europe/Moscow',
                'rule_types': ['booking_geo'],
                'zone_name': 'test_match',
                'activity_points': 3,
            },
            [
                '000000000000000000000301',
                '000000000000000000000302',
                '000000000000000000000303',
            ],
            id='ignore rule due to `activity_points`',
        ),
        pytest.param(
            {
                'reference_time': '2020-01-23T11:00:11.000Z',
                'time_zone': 'Europe/Moscow',
                'rule_types': ['booking_geo'],
                'zone_name': 'test_match',
                'profile_payment_type_restrictions': 'cash',
            },
            [
                '000000000000000000000301',
                '000000000000000000000302',
                '000000000000000000000303',
            ],
            id='ignore rule due to `profile_payment_type_restrictions`',
        ),
        pytest.param(
            {
                'reference_time': '2020-01-23T11:00:11.000Z',
                'time_zone': 'Europe/Moscow',
                'rule_types': ['booking_geo'],
                'zone_name': 'test_match',
                'profile_tariff_classes': ['business', 'courier'],
            },
            {
                '000000000000000000000301',
                '000000000000000000000302',
                '000000000000000000000303',
            },
            id='ignore rule due to `profile_tariff_classes`',
        ),
        (
            {
                'reference_time': '2020-01-23T11:00:11.000Z',
                'time_zone': 'Europe/Moscow',
                'rule_types': ['booking_geo'],
                'zone_name': 'test_match',
                'activity_points': 91,
            },
            [
                '000000000000000000000301',
                '000000000000000000000302',
                '000000000000000000000303',
                '000000000000000000000304',
                '000000000000000000000305',
            ],
        ),
        (
            {
                'reference_time': '2020-01-23T11:00:11.000Z',
                'time_zone': 'Europe/Moscow',
                'rule_types': ['booking_geo'],
                'zone_name': 'test_match',
                'profile_payment_type_restrictions': 'online',
            },
            [
                '000000000000000000000301',
                '000000000000000000000302',
                '000000000000000000000303',
                '000000000000000000000304',
                '000000000000000000000305',
            ],
        ),
        (
            {
                'reference_time': '2020-01-23T11:00:11.000Z',
                'time_zone': 'Europe/Moscow',
                'rule_types': ['booking_geo'],
                'zone_name': 'test_match',
                'profile_tariff_classes': ['econom', 'business', 'courier'],
            },
            [
                '000000000000000000000301',
                '000000000000000000000302',
                '000000000000000000000303',
                '000000000000000000000304',
                '000000000000000000000305',
            ],
        ),
    ],
)
@pytest.mark.servicetest
async def test_match(taxi_billing_subventions_x, query, expected_rule_ids):
    response = await taxi_billing_subventions_x.post(HANDLE, query)
    assert response.status_code == 200
    actual_ids = (x['id'] for x in response.json()['match'])
    assert set(actual_ids) == set(expected_rule_ids)
