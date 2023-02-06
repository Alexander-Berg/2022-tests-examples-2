import json

import pytest

HANDLE = 'v1/rules/match/'


@pytest.mark.servicetest
async def test_do_x_get_y_fields(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'zone_name': 'test_fields',
            'reference_time': '2020-01-23T11:00:11.000Z',
            'time_zone': 'Europe/Moscow',
            'rule_types': ['do_x_get_y'],
        },
    )
    assert response.status_code == 200
    ret = json.loads(response.content)
    assert ret['match']
    rec = ret['match'][0]
    assert 'tariff_class' in rec
    assert 'order_payment_type' in rec
    assert 'geoareas' in rec
    assert 'branding_type' in rec
    assert 'days_span' in rec
    assert 'steps' in rec
    assert rec['id'] == rec['group_id']


@pytest.mark.parametrize(
    'zone',
    [
        'missing_dayridecount_days',
        'small_dayridecount_days',
        'big_dayridecount_days',
    ],
)
@pytest.mark.servicetest
async def test_do_x_get_y_bad_records(taxi_billing_subventions_x, zone):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-01-23T11:00:11.000Z',
            'time_zone': 'Europe/Moscow',
            'rule_types': ['do_x_get_y'],
            'zone_name': zone,
        },
    )
    assert response.status_code == 500


@pytest.mark.parametrize(
    'tags, expected_rule_ids',
    [
        (None, ['p_0001', 'group9']),
        (['subv_disable_do_x_get_y_personal'], ['group9']),
        (['subv_disable_do_x_get_y'], ['p_0001']),
        (['subv_disable_all'], []),
    ],
)
@pytest.mark.servicetest
async def test_do_x_get_y_disabling_tags(
        taxi_billing_subventions_x, tags, expected_rule_ids,
):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'reference_time': '2020-01-23T11:00:11.000Z',
            'time_zone': 'Europe/Moscow',
            'tags': tags,
            'unique_driver_id': '5afee6c3453b0a524e629614',
            'zone_name': 'test_disabling_tags',
        },
    )
    actual_ids = (x['id'] for x in response.json()['match'])
    assert set(actual_ids) == set(expected_rule_ids)
