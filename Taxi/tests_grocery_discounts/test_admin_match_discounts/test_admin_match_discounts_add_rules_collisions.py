import datetime
from typing import FrozenSet
from typing import List
from typing import Optional

import pytest

from tests_grocery_discounts import common

START_BEFORE = '2020-01-01T09:00:00+00:00'
START_AT = '2020-01-01T09:00:01+00:00'
START_AFTER = '2020-01-01T09:00:02+00:00'

END_BEFORE = '2020-12-31T23:59:59+00:00'
END_AT = '2021-01-01T00:00:00+00:00'
END_AFTER = '2021-01-01T00:00:10+00:00'


def _common_search_rules_conditions(
        rules: List[dict], start: str, end: str,
) -> List[dict]:
    return [
        rule for rule in rules if rule['condition_name'] != 'active_period'
    ]


def _common_search_rules_expected_data(
        start_str: str,
        end_str: str,
        initial_add_rules_data: dict,
        add_rules_data: dict,
        hierarchy_name: str,
        change_expected: bool,
) -> dict:
    start = datetime.datetime.strptime(start_str, common.DATETIME_FORMAT)
    end = datetime.datetime.strptime(end_str, common.DATETIME_FORMAT)

    result: dict = {}
    for index, data in enumerate(initial_add_rules_data[hierarchy_name]):
        for rule in data['rules']:
            if rule['condition_name'] != 'active_period':
                continue
            for value in rule['values']:
                value_start = datetime.datetime.strptime(
                    value['start'], common.DATETIME_FORMAT,
                )
                active_period: dict = {
                    'condition_name': 'active_period',
                    'values': [
                        {
                            'start': value['start'],
                            'is_start_utc': False,
                            'is_end_utc': False,
                            'end': value['end'],
                        },
                    ],
                }
                if change_expected and value_start < end:
                    if value_start >= start:
                        continue
                    else:
                        active_period['values'][0]['end'] = start_str
                if hierarchy_name not in result:
                    result[hierarchy_name] = []
                result[hierarchy_name].append(
                    {
                        'discount': common.get_added_discount(
                            initial_add_rules_data, hierarchy_name, index,
                        ),
                        'match_path': (
                            common.get_match_path(
                                hierarchy_name, active_period,
                            )['match_path']
                        ),
                        'meta_info': {
                            'create_draft_id': (
                                'draft_id_check_add_rules_validation'
                            ),
                            'create_author': 'user',
                        },
                    },
                )
                break

    if not change_expected:
        return result

    if start_str != end_str:
        if hierarchy_name not in result:
            result[hierarchy_name] = []
        result[hierarchy_name].append(
            {
                'discount': common.get_added_discount(
                    add_rules_data, hierarchy_name,
                ),
                'match_path': (
                    common.get_match_path(
                        hierarchy_name,
                        {
                            'condition_name': 'active_period',
                            'values': [
                                {
                                    'start': start_str,
                                    'end': end_str,
                                    'is_start_utc': False,
                                    'is_end_utc': False,
                                },
                            ],
                        },
                    )['match_path']
                ),
                'meta_info': {
                    'create_draft_id': 'draft_id_check_add_rules_validation',
                    'create_author': 'user',
                },
            },
        )

    return result


def _get_add_rules_data(hierarchy_names: FrozenSet[str]) -> dict:
    add_rules_data = common.get_add_rules_data(
        common.VALID_ACTIVE_PERIOD, hierarchy_names, '1',
    )
    second_discount = common.get_add_rules_data(
        {
            'condition_name': 'active_period',
            'values': [
                {
                    'start': '2021-01-01T00:00:01+00:00',
                    'is_start_utc': False,
                    'is_end_utc': False,
                    'end': '2021-01-01T00:00:04+00:00',
                },
            ],
        },
        hierarchy_names,
        '2',
    )
    for hierarchy_name, rules in add_rules_data.items():
        rules.append(second_discount[hierarchy_name][0])
    return add_rules_data


def _count_affected_revisions(
        hierarchy_name: str,
        start_str: str,
        end_str: str,
        initial_add_rules_data: dict,
) -> int:
    count = 0
    end = datetime.datetime.strptime(end_str, common.DATETIME_FORMAT)

    for data in initial_add_rules_data[hierarchy_name]:
        for rule in data['rules']:
            if rule['condition_name'] == 'active_period':
                for value in rule['values']:
                    value_start = datetime.datetime.strptime(
                        value['start'], common.DATETIME_FORMAT,
                    )
                    if value_start < end:
                        count += 1
                break
    return count


@pytest.mark.parametrize(
    'update_existing_discounts',
    (
        pytest.param(True, id='update_existing_discounts'),
        pytest.param(False, id='not_update_existing_discounts'),
    ),
)
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
@pytest.mark.parametrize(
    'hierarchy_name',
    (
        pytest.param('menu_discounts', id='menu_discounts'),
        pytest.param('cart_discounts', id='cart_discounts'),
        pytest.param(
            'payment_method_discounts', id='payment_method_discounts',
        ),
        pytest.param('dynamic_discounts', id='dynamic_discounts'),
    ),
)
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
@pytest.mark.config(**common.DEFAULT_CONFIGS)
async def test_add_rules_check_collisions(
        taxi_grocery_discounts,
        start: str,
        end: str,
        hierarchy_name: str,
        update_existing_discounts: bool,
        check_add_rules_validation,
        add_rules,
):
    await common.init_bin_sets(taxi_grocery_discounts)

    hierarchy_names = frozenset((hierarchy_name,))
    initial_add_rules_data = _get_add_rules_data(hierarchy_names)

    await add_rules(initial_add_rules_data, {'series_id': common.SERIES_ID})

    if update_existing_discounts:
        expected_status_code = 200
        expected_response = None
        expected_revisions_count = _count_affected_revisions(
            hierarchy_name, start, end, initial_add_rules_data,
        )
    else:
        expected_status_code = 400
        expected_response = {
            'code': 'Validation error',
            'message': (
                'Flag \'update_existing_discounts\' is false but '
                'rules adding affects some rules'
            ),
        }
        expected_revisions_count = 0

    add_rules_data = common.get_add_rules_data(
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
        hierarchy_names,
    )
    await check_add_rules_validation(
        True,
        {
            'update_existing_discounts': update_existing_discounts,
            'series_id': common.SERIES_ID,
        },
        hierarchy_name,
        add_rules_data[hierarchy_name][0]['rules'],
        add_rules_data[hierarchy_name][0]['discount'],
        expected_status_code,
        expected_response,
        expected_revisions_count,
    )


@pytest.mark.parametrize(
    'revisions',
    (
        pytest.param([], id='empty_revisions'),
        pytest.param(None, id='valid_revisions'),
    ),
)
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
@pytest.mark.parametrize(
    'hierarchy_name',
    (
        pytest.param('menu_discounts', id='menu_discounts'),
        pytest.param('cart_discounts', id='cart_discounts'),
        pytest.param('bundle_discounts', id='bundle_discounts'),
        pytest.param(
            'payment_method_discounts', id='payment_method_discounts',
        ),
        pytest.param('dynamic_discounts', id='dynamic_discounts'),
    ),
)
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
@pytest.mark.config(**common.DEFAULT_CONFIGS)
async def test_add_rules_collisions(
        taxi_grocery_discounts,
        pgsql,
        start: str,
        end: str,
        revisions: Optional[List[int]],
        hierarchy_name: str,
        check_add_rules_validation,
        add_rules,
):
    await common.init_bin_sets(taxi_grocery_discounts)

    hierarchy_names = frozenset((hierarchy_name,))
    initial_add_rules_data = _get_add_rules_data(hierarchy_names)

    await add_rules(initial_add_rules_data, {'series_id': common.SERIES_ID})

    add_rules_data = common.get_add_rules_data(
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
        hierarchy_names,
        '3',
    )

    affected_revisions_count = _count_affected_revisions(
        hierarchy_name, start, end, initial_add_rules_data,
    )
    if revisions is None:
        revisions = await check_add_rules_validation(
            True,
            {'update_existing_discounts': True, 'series_id': common.SERIES_ID},
            hierarchy_name,
            add_rules_data[hierarchy_name][0]['rules'],
            add_rules_data[hierarchy_name][0]['discount'],
            200,
            None,
            affected_revisions_count,
        )
        change_expected = True
        expected_status_code = 200
        expected_response = None
    else:
        change_expected = False
        expected_status_code = 400
        expected_response = {
            'code': 'Validation error',
            'message': (
                'Number of expected affected revisions '
                f'{len(revisions)} does not match '
                f'{affected_revisions_count}'
            ),
        }

    await check_add_rules_validation(
        False,
        {'revisions': revisions, 'series_id': common.SERIES_ID},
        hierarchy_name,
        add_rules_data[hierarchy_name][0]['rules'],
        add_rules_data[hierarchy_name][0]['discount'],
        expected_status_code,
        expected_response,
    )
    await common.check_search_rules(
        taxi_grocery_discounts,
        hierarchy_name,
        _common_search_rules_conditions(
            initial_add_rules_data[hierarchy_name][0]['rules'], start, end,
        ),
        3,
        None,
        _common_search_rules_expected_data(
            start,
            end,
            initial_add_rules_data,
            add_rules_data,
            hierarchy_name,
            change_expected,
        ),
        200,
    )
