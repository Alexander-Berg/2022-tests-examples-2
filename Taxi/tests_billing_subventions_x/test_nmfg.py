import json

import pytest

HANDLE = 'v1/rules/match/'


@pytest.mark.servicetest
async def test_nmfg_has_is_net(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'zone_name': 'fields_test',
            'reference_time': '2020-01-10T11:00:11.000Z',
            'time_zone': 'UTC',
            'rule_types': ['nmfg'],
            'driver_branding': 'no_branding',
        },
    )
    assert response.status_code == 200
    rec = json.loads(response.content)['match'][0]
    assert 'is_net' in rec
    assert rec['is_net'] is True


@pytest.mark.servicetest
async def test_nmfg_has_is_test(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'zone_name': 'fields_test',
            'reference_time': '2020-01-10T11:00:11.000Z',
            'time_zone': 'UTC',
            'rule_types': ['nmfg'],
            'driver_branding': 'no_branding',
        },
    )
    assert response.status_code == 200
    rec = json.loads(response.content)['match'][0]
    assert 'is_test' in rec
    assert rec['is_test'] is True


@pytest.mark.servicetest
async def test_nmfg_id_is_group_id(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'zone_name': 'fields_test',
            'reference_time': '2020-01-10T11:00:11.000Z',
            'time_zone': 'UTC',
            'rule_types': ['nmfg'],
        },
    )
    assert response.status_code == 200
    rec = json.loads(response.content)['match'][0]
    assert rec['id'] == rec['group_id']


@pytest.mark.servicetest
async def test_nmfg_steps(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'zone_name': 'fields_test',
            'reference_time': '2020-01-10T11:00:11.000Z',
            'time_zone': 'UTC',
            'rule_types': ['nmfg'],
            'driver_branding': 'no_branding',
        },
    )
    assert response.status_code == 200
    rec = json.loads(response.content)['match'][0]
    assert 'steps' in rec
    assert rec['steps'] == [
        {
            'id': '000000000000000000000101',
            'group_member_id': 'member_1_1',
            'orders_count': 1,
            'bonus': '100.000000',
        },
        {
            'id': '000000000000000000000102',
            'group_member_id': 'member_1_2',
            'orders_count': 2,
            'bonus': '200.000000',
        },
        {
            'id': '000000000000000000000103',
            'group_member_id': 'member_1_3',
            'orders_count': 3,
            'bonus': '300.000000',
        },
    ]


@pytest.mark.servicetest
async def test_nmfg_branding(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'zone_name': 'fields_test',
            'reference_time': '2020-01-10T11:00:11.000Z',
            'time_zone': 'UTC',
            'rule_types': ['nmfg'],
        },
    )
    assert response.status_code == 200
    recs = dict(
        (x['id'], x.get('branding_type'))
        for x in json.loads(response.content)['match']
    )
    assert recs == {
        'rule_1': None,
        'rule_2': 'full_branding',
        'rule_3': 'sticker',
    }


@pytest.mark.servicetest
async def test_nmfg_tagging(taxi_billing_subventions_x):
    response = await taxi_billing_subventions_x.post(
        HANDLE,
        {
            'zone_name': 'tags_test',
            'reference_time': '2020-01-10T11:00:11.000Z',
            'time_zone': 'UTC',
            'rule_types': ['nmfg'],
        },
    )
    assert response.status_code == 200
    recs = sorted([x['id'] for x in json.loads(response.content)['match']])
    assert recs == ['rule_6', 'rule_7']


@pytest.mark.servicetest
@pytest.mark.parametrize(
    'query',
    (
        # 000000000000000000000601, 000000000000000000000501 are applicable.
        # 000000000000000000000601 has higher priority because of tag.
        # Therefore 000000000000000000000501 is ignored although it match,
        # 000000000000000000000601 is ignored eventually due to `tariff_class`
        pytest.param(
            {
                'zone_name': 'tags_test',
                'reference_time': '2020-01-10T11:00:11.000Z',
                'time_zone': 'UTC',
                'rule_types': ['nmfg'],
                'tags': ['tagA'],
                'tariff_class': 'comfort',
            },
            id='nfmg_rule_with_tag_is_god_1',
        ),
        # ... due to `activity_points`
        pytest.param(
            {
                'zone_name': 'tags_test',
                'reference_time': '2020-01-10T11:00:11.000Z',
                'time_zone': 'UTC',
                'rule_types': ['nmfg'],
                'tags': ['tagA'],
                'activity_points': 85,
            },
            id='nfmg_rule_with_tag_is_god_2',
        ),
        pytest.param(
            {
                'zone_name': 'not_approved_test',
                'reference_time': '2020-01-10T11:00:11.000Z',
                'time_zone': 'UTC',
                'rule_types': ['nmfg'],
            },
            id='not_approved_nmfg_ignored',
        ),
    ),
)
async def test_nmfg_matching(taxi_billing_subventions_x, query):
    response = await taxi_billing_subventions_x.post(HANDLE, query)
    assert response.status_code == 200
    assert response.json()['match'] == []
