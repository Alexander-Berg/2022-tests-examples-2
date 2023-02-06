import copy

import pytest

from tests_ride_discounts import common

START_BEFORE = '2020-01-01T12:00:00+00:00'
START_AT = '2020-01-01T12:00:01+00:00'
START_AFTER = '2020-01-01T12:00:02+00:00'

END_BEFORE = '2021-01-01T00:00:00+00:00'
END_AT = '2021-01-01T00:00:05+00:00'
END_AFTER = '2021-01-01T00:00:10+00:00'

BR_MOSCOW_CONDITION = {
    'condition_name': 'zone',
    'values': [
        {'name': 'br_moscow', 'type': 'geonode', 'is_prioritized': False},
    ],
}


@pytest.mark.parametrize(
    'end',
    (
        pytest.param(END_BEFORE, id='end_before'),
        pytest.param(END_AT, id='end_at'),
        pytest.param(END_AFTER, id='end_after'),
    ),
)
@pytest.mark.parametrize(
    'start',
    (
        pytest.param(START_BEFORE, id='start_before'),
        pytest.param(START_AT, id='start_at'),
        pytest.param(START_AFTER, id='start_after'),
    ),
)
@pytest.mark.pgsql('ride_discounts', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
@pytest.mark.config(
    USERVICE_AGGLOMERATIONS_CACHE_SETTINGS={
        '__default__': {
            'enabled': True,
            'log_errors': True,
            'verify_on_updates': True,
        },
    },
    APPLICATION_MAP_DISCOUNTS={
        'some_application_name': 'some_application_type',
    },
    APPLICATION_MAP_PLATFORM={
        'some_application_name': 'some_application_platform',
    },
    APPLICATION_MAP_BRAND={'some_application_name': 'some_application_brand'},
)
async def test_add_rules_collisions(
        client, start: str, end: str, check_add_rules_validation, add_discount,
):
    hierarchy_name = common.get_random_hierarchy_name()
    await common.init_bin_sets(client)

    existing_active_periods = [
        {
            'start': '2021-01-01T00:00:06+00:00',
            'is_start_utc': False,
            'is_end_utc': False,
            'end': '2021-01-01T00:00:07+00:00',
        },
        {
            'start': '2020-01-01T12:00:01+00:00',
            'is_start_utc': False,
            'end': '2021-01-01T00:00:05+00:00',
            'is_end_utc': False,
        },
    ]
    for active_period in existing_active_periods:
        await add_discount(
            hierarchy_name,
            [
                BR_MOSCOW_CONDITION,
                {'condition_name': 'bins', 'values': ['some_bins']},
                {'condition_name': 'active_period', 'values': [active_period]},
            ],
        )
    updated_active_periods = []

    affected_discount_ids_count = 0
    for active_period in existing_active_periods:
        active_period_start = str(active_period['start'])
        active_period_end = str(active_period['end'])
        if active_period_start < start:
            if active_period_end < start:
                updated_active_periods.append(copy.deepcopy(active_period))
            else:
                affected_discount_ids_count += 1
                updated_active_periods.append(
                    {
                        'start': active_period['start'],
                        'is_start_utc': False,
                        'end': start,
                        'is_end_utc': False,
                    },
                )
        else:
            if active_period_start > end:
                updated_active_periods.append(copy.deepcopy(active_period))
            else:
                affected_discount_ids_count += 1
    rules = [
        BR_MOSCOW_CONDITION,
        {'condition_name': 'bins', 'values': ['some_bins']},
        {
            'condition_name': 'active_period',
            'values': [
                {
                    'start': start,
                    'end': end,
                    'is_start_utc': False,
                    'is_end_utc': False,
                },
            ],
        },
    ]

    affected_discount_ids = await check_add_rules_validation(
        True,
        {'update_existing_discounts': True},
        hierarchy_name,
        rules,
        common.make_discount(hierarchy_name=hierarchy_name),
        200,
        None,
        0,
        affected_discount_ids_count,
    )
    await check_add_rules_validation(
        False,
        {'affected_discount_ids': affected_discount_ids},
        hierarchy_name,
        rules,
        common.make_discount(hierarchy_name=hierarchy_name),
        200,
        None,
    )
    response = await client.post(
        '/v1/admin/match-discounts/find-discounts',
        json={
            'hierarchy_name': hierarchy_name,
            'conditions': [],
            'type': 'FETCH_MATCH',
        },
        headers=common.get_headers(),
    )
    discounts_info = response.json()['discounts_data']['discounts_info']
    active_periods = []
    for item in discounts_info:
        for condition in item['conditions']:
            if condition['condition_name'] == 'active_period':
                active_periods.append(condition['values'][0])
    active_periods.sort(key=lambda x: x['end'])
    expected_active_periods = [
        {
            'end': end,
            'is_end_utc': False,
            'is_start_utc': False,
            'start': start,
        },
        *updated_active_periods,
    ]
    expected_active_periods.sort(key=lambda x: x['end'])
    assert active_periods == expected_active_periods
