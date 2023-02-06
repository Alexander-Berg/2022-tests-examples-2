import json

import pytest

HANDLE = 'v1/rules/match/'


def _get_ids(json_value):
    return {'match': sorted([x['id'].upper() for x in json_value['match']])}


def get_ids(response):
    return _get_ids(json.loads(response.content))


# mfg city=chelyabinsk, start=2020-04-01T00:00:00Z end=2020-05-01T00:00:00Z


@pytest.mark.servicetest
async def test_all_passed(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-04-05T00:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'city0',
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {
        'match': sorted(
            ['000000000000000000000101', '000000000000000000000102'],
        ),
    }


#
# by_payment_type
#
@pytest.mark.servicetest
async def test_accept_by_default_payment_type(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-04-04T10:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'city1',
            'order_payment_type': 'cash',
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {'match': ['000000000000000000000201']}


@pytest.mark.servicetest
async def test_accept_by_matched_payment_type(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-04-04T10:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'city2',
            'order_payment_type': 'card',
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {'match': ['000000000000000000000202']}


@pytest.mark.servicetest
async def test_decline_by_unmatched_payment_type(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-04-04T10:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'city2',
            'order_payment_type': 'cash',
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {'match': []}


#
# by_activity_points
#
@pytest.mark.servicetest
async def test_accept_by_undefined_activity_points(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-04-04T10:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'city3',
            'activity_points': 75,
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {'match': ['000000000000000000000301']}


@pytest.mark.servicetest
async def test_skip_by_activity_points(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-04-04T10:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'city4',
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {'match': ['000000000000000000000302']}


@pytest.mark.servicetest
async def test_accept_by_activity_points(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-04-04T10:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'city4',
            'activity_points': 75,
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {'match': ['000000000000000000000302']}


@pytest.mark.servicetest
async def test_decline_by_activity_points(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-04-04T10:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'city4',
            'activity_points': 25,
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {'match': []}


#
# by_day_of_week
#
@pytest.mark.servicetest
async def test_accept_by_day_of_week(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-04-04T10:00:00.000Z',  # 6/Sat
            'time_zone': 'UTC',
            'zone_name': 'city5',
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {'match': ['000000000000000000000401']}


@pytest.mark.servicetest
async def test_decline_by_day_of_week(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-04-01T10:00:00.000Z',  # 3/Wed
            'time_zone': 'UTC',
            'zone_name': 'city5',
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {'match': []}


#
# by_local_hour
#
@pytest.mark.servicetest
async def test_accept_by_hour(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-04-04T04:00:00.000Z',
            'time_zone': 'Asia/Yekaterinburg',  # GMT +5
            'zone_name': 'city6',
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {'match': ['000000000000000000000501']}


@pytest.mark.servicetest
async def test_decline_by_hour(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-04-04T09:00:00.000Z',
            'time_zone': 'Asia/Yekaterinburg',  # GMT +5
            'zone_name': 'city6',
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {'match': []}


#
# by_geoareas
#
@pytest.mark.servicetest
async def test_accept_by_default_geoareas(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-04-04T10:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'city7',
            'geoareas': ['geo1', 'geo2'],
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {'match': ['000000000000000000000601']}


@pytest.mark.servicetest
async def test_accept_by_all_geoareas(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-04-04T10:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'city8',
            'geoareas': ['geo1', 'geo2'],
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {'match': ['000000000000000000000602']}


@pytest.mark.servicetest
async def test_skip_by_geoareas(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-04-04T10:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'city8',
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {'match': ['000000000000000000000602']}


@pytest.mark.servicetest
async def test_accept_by_some_geoareas(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-04-04T10:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'city8',
            'geoareas': ['geo1', 'geo3'],
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {'match': ['000000000000000000000602']}


@pytest.mark.servicetest
async def test_decline_by_geoareas(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-04-04T10:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'city8',
            'geoareas': ['geo3'],
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {'match': []}


#
# by_tariff_class
#
@pytest.mark.servicetest
async def test_accept_by_default_tariff_class(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-04-04T10:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'city9',
            'tariff_class': 'econom',
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {'match': ['000000000000000000000701']}


@pytest.mark.servicetest
async def test_skip_by_tariff_class(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-04-04T10:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'city10',
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {'match': ['000000000000000000000702']}


@pytest.mark.servicetest
async def test_accept_by_tariff_class(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-04-04T10:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'city10',
            'tariff_class': 'econom',
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {'match': ['000000000000000000000702']}


@pytest.mark.servicetest
async def test_decline_by_tariff_class(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-04-04T10:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'city10',
            'tariff_class': 'comfort',
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {'match': []}


#
# by_tags
#
@pytest.mark.servicetest
async def test_accept_by_default_tags(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-04-04T10:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'city11',
            'tags': ['tag1', 'tag2'],
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {'match': ['000000000000000000000801']}


@pytest.mark.servicetest
async def test_skip_by_tags(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-04-04T10:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'city12',
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {'match': ['000000000000000000000802']}


@pytest.mark.servicetest
async def test_accept_by_all_tags(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-04-04T10:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'city12',
            'tags': ['tag1', 'tag2'],
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {'match': ['000000000000000000000802']}


@pytest.mark.servicetest
async def test_accept_by_some_tags(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-04-04T10:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'city12',
            'tags': ['tag1', 'tag3'],
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {'match': ['000000000000000000000802']}


@pytest.mark.servicetest
async def test_decline_by_missing_tags(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-04-04T10:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'city12',
            'tags': ['tag3'],
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {'match': []}


@pytest.mark.servicetest
async def test_decline_by_unfit1_tags(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-04-04T10:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'city12',
            'tags': ['tag1', 'subv_disable_all'],
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {'match': []}


@pytest.mark.servicetest
async def test_decline_by_unfit2_tags(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-04-04T10:00:00.000Z',
            'time_zone': 'UTC',
            'zone_name': 'city12',
            'tags': ['tag1', 'subv_disable_on_top'],
        },
    )
    assert response.status_code == 200
    assert get_ids(response) == {'match': []}
