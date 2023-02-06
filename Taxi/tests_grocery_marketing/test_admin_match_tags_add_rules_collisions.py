import datetime
from typing import FrozenSet
from typing import List
from typing import Optional

import pytest

from tests_grocery_marketing import common


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
                        'tag': common.get_added_tag(
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
                'tag': common.get_added_tag(add_rules_data, hierarchy_name),
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
                },
            },
        )

    return result


def _get_add_rules_data(hierarchy_names: FrozenSet[str]) -> dict:
    add_rules_data = common.get_add_rules_data(
        common.VALID_ACTIVE_PERIOD,
        common.RULE_ID_CONDITION,
        hierarchy_names,
        '1',
    )
    second_tag = common.get_add_rules_data(
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
        hierarchy_names=hierarchy_names,
        description='2',
    )
    for hierarchy_name, rules in add_rules_data.items():
        rules.append(second_tag[hierarchy_name][0])
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
    'update_existing_tags',
    (
        pytest.param(True, id='update_existing_tags'),
        pytest.param(False, id='not_update_existing_tags'),
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
    'hierarchy_name', (pytest.param('menu_tags', id='menu_tags'),),
)
@pytest.mark.pgsql('grocery_marketing', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
@pytest.mark.config(
    GROCERY_MARKETING_APPLICATION_NAME_VALIDATION={
        'application_names': ['some_application_name'],
    },
)
async def test_add_rules_check_collisions(
        taxi_grocery_marketing,
        pgsql,
        start: str,
        end: str,
        hierarchy_name: str,
        update_existing_tags: bool,
):
    hierarchy_names = frozenset((hierarchy_name,))
    initial_add_rules_data = _get_add_rules_data(hierarchy_names)

    await common.add_rules(
        taxi_grocery_marketing, pgsql, initial_add_rules_data,
    )

    if update_existing_tags:
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
                'Flag \'update_existing_tags\' is false but '
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
        hierarchy_names=hierarchy_names,
    )
    await common.check_add_rules_validation(
        taxi_grocery_marketing,
        pgsql,
        common.ADD_RULES_CHECK_URL,
        {'update_existing_tags': update_existing_tags},
        hierarchy_name,
        add_rules_data[hierarchy_name][0]['rules'],
        add_rules_data[hierarchy_name][0]['tag'],
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
    'hierarchy_name', (pytest.param('menu_tags', id='menu_tags'),),
)
@pytest.mark.pgsql('grocery_marketing', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
async def test_add_rules_collisions(
        taxi_grocery_marketing,
        pgsql,
        start: str,
        end: str,
        revisions: Optional[List[int]],
        hierarchy_name: str,
):
    hierarchy_names = frozenset((hierarchy_name,))
    initial_add_rules_data = _get_add_rules_data(hierarchy_names)
    await common.add_rules(
        taxi_grocery_marketing, pgsql, initial_add_rules_data,
    )

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
        hierarchy_names=hierarchy_names,
        description='3',
    )

    affected_revisions_count = _count_affected_revisions(
        hierarchy_name, start, end, initial_add_rules_data,
    )
    if revisions is None:
        revisions = await common.check_add_rules_validation(
            taxi_grocery_marketing,
            pgsql,
            common.ADD_RULES_CHECK_URL,
            {'update_existing_tags': True},
            hierarchy_name,
            add_rules_data[hierarchy_name][0]['rules'],
            add_rules_data[hierarchy_name][0]['tag'],
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

    await common.check_add_rules_validation(
        taxi_grocery_marketing,
        pgsql,
        common.ADD_RULES_URL,
        {'revisions': revisions},
        hierarchy_name,
        add_rules_data[hierarchy_name][0]['rules'],
        add_rules_data[hierarchy_name][0]['tag'],
        expected_status_code,
        expected_response,
    )
    await common.check_search_rules(
        taxi_grocery_marketing,
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
