from typing import Dict
from typing import List
from typing import Optional

import discounts_match  # pylint: disable=E0401
import pytest

from tests_grocery_marketing import common

WITHIN_VALID_ACTIVE_PERIOD = {
    'condition_name': 'active_period',
    'values': [
        {
            'start': '2020-01-01T09:00:02+00:00',
            'is_start_utc': False,
            'is_end_utc': False,
            'end': '2020-12-31T00:00:00+00:00',
        },
    ],
}

AFTER_VALID_ACTIVE_PERIOD = {
    'condition_name': 'active_period',
    'values': [
        {
            'start': '2021-01-01T00:00:01+00:00',
            'is_start_utc': False,
            'is_end_utc': False,
            'end': '2021-01-01T00:00:02+00:00',
        },
    ],
}

BEFORE_VALID_ACTIVE_PERIOD = {
    'condition_name': 'active_period',
    'values': [
        {
            'start': '2020-01-01T08:00:00+00:00',
            'is_start_utc': False,
            'is_end_utc': False,
            'end': '2020-01-01T09:00:00+00:00',
        },
    ],
}


def _common_expected_data(
        hierarchy_name: Optional[str] = None,
        active_period: Optional[dict] = None,
) -> dict:
    result: dict = {
        'menu_tags': [
            {
                'tag': (
                    common.get_added_tag(
                        common.get_add_rules_data(), 'menu_tags',
                    )
                ),
                'match_path': (
                    common.menu_match_path(active_period)['match_path']
                ),
                'meta_info': {
                    'create_draft_id': 'draft_id_check_add_rules_validation',
                },
            },
        ],
    }

    if hierarchy_name is not None:
        for name in result:
            if name != hierarchy_name:
                result[name] = []
    return result


@pytest.mark.parametrize(
    'hierarchy_name', (pytest.param('menu_tags', id='menu_tags_hierarchy'),),
)
@pytest.mark.parametrize(
    'add_rules_data, conditions, limit, offset, expected_data,'
    'expected_status_code',
    (
        pytest.param(
            common.get_add_rules_data(),
            [
                {'condition_name': 'city', 'values': ['213']},
                {'condition_name': 'country', 'values': ['some_country']},
                {'condition_name': 'depot', 'values': ['some_depot']},
                {
                    'condition_name': 'application_name',
                    'values': ['some_application_name'],
                },
            ],
            1,
            0,
            _common_expected_data(),
            200,
            id='add_all_hierarchies_tags',
        ),
        pytest.param(
            common.get_add_rules_data(),
            [],
            1,
            100500,
            _common_expected_data(),
            200,
            id='valid_offset',
        ),
        pytest.param(
            common.get_add_rules_data(),
            [{'condition_name': 'country', 'values': ['another_country']}],
            1,
            0,
            _common_expected_data(''),
            200,
            id='another_country',
        ),
        pytest.param(
            common.get_add_rules_data(),
            [{'condition_name': 'city', 'values': ['214']}],
            1,
            0,
            _common_expected_data(''),
            200,
            id='another_city',
        ),
        pytest.param(
            common.get_add_rules_data(),
            [{'condition_name': 'depot', 'values': ['another_depot']}],
            1,
            0,
            _common_expected_data(''),
            200,
            id='another_depot',
        ),
        pytest.param(
            {
                'menu_tags': [
                    {
                        'rules': [
                            common.VALID_ACTIVE_PERIOD,
                            common.RULE_ID_CONDITION,
                            {'condition_name': 'city', 'values': ['213']},
                            {
                                'condition_name': 'country',
                                'values': ['some_country'],
                            },
                            {
                                'condition_name': 'depot',
                                'values': ['some_depot'],
                            },
                        ],
                        'tag': common.small_menu_tag(),
                    },
                ],
            },
            [],
            1,
            0,
            _common_expected_data('menu_tags'),
            200,
            id='add_menu_hierarchy_tag',
        ),
        pytest.param(
            common.get_add_rules_data(AFTER_VALID_ACTIVE_PERIOD),
            [common.VALID_ACTIVE_PERIOD],
            1,
            0,
            _common_expected_data(''),
            200,
            id='add_future_tags',
        ),
        pytest.param(
            common.get_add_rules_data(BEFORE_VALID_ACTIVE_PERIOD),
            [common.VALID_ACTIVE_PERIOD],
            1,
            0,
            _common_expected_data(''),
            200,
            id='add_past_tags',
        ),
        pytest.param(
            common.get_add_rules_data(WITHIN_VALID_ACTIVE_PERIOD),
            [common.VALID_ACTIVE_PERIOD],
            1,
            0,
            _common_expected_data(None, WITHIN_VALID_ACTIVE_PERIOD),
            200,
            id='add_within_tags',
        ),
        pytest.param(
            common.get_add_rules_data(AFTER_VALID_ACTIVE_PERIOD),
            [],
            1,
            0,
            _common_expected_data(None, AFTER_VALID_ACTIVE_PERIOD),
            200,
            id='add_future_tags_no_active_period',
        ),
        pytest.param(
            common.get_full_add_rules_data(),
            [],
            1,
            0,
            {
                'menu_tags': [
                    {
                        'tag': (
                            common.get_added_tag(
                                common.get_full_add_rules_data(), 'menu_tags',
                            )
                        ),
                        'match_path': (common.menu_match_path()['match_path']),
                        'meta_info': {
                            'create_draft_id': (
                                'draft_id_check_add_rules_validation'
                            ),
                        },
                    },
                ],
            },
            200,
            id='add_full_all_hierarchies_tags',
        ),
    ),
)
@pytest.mark.pgsql('grocery_marketing', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
@pytest.mark.config(
    GROCERY_MARKETING_APPLICATION_NAME_VALIDATION={
        'application_names': ['some_application_name'],
    },
)
async def test_search_rules(
        taxi_grocery_marketing,
        pgsql,
        mocked_time,
        hierarchy_name: str,
        add_rules_data: Dict[str, List[dict]],
        conditions: List[dict],
        expected_data: Optional[dict],
        limit: int,
        expected_status_code,
        offset: Optional[int],
) -> None:
    await common.add_rules(taxi_grocery_marketing, pgsql, add_rules_data)

    await common.check_search_rules(
        taxi_grocery_marketing,
        hierarchy_name,
        conditions,
        limit,
        offset,
        expected_data,
        expected_status_code,
    )


@pytest.mark.parametrize(
    'hierarchy_name', (pytest.param('menu_tags', id='menu_tags'),),
)
@pytest.mark.parametrize(
    'missing_hierarchy_name',
    (
        pytest.param(
            'menu_tags',
            marks=discounts_match.remove_hierarchies('menu_tags'),
            id='missing_menu_tags',
        ),
    ),
)
@pytest.mark.pgsql('grocery_marketing', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
async def test_search_rules_missing_hierarchy(
        taxi_grocery_marketing, hierarchy_name, missing_hierarchy_name,
) -> None:

    if hierarchy_name == missing_hierarchy_name:
        expected_data: dict = {
            'code': '404',
            'message': f'Hierarchy {missing_hierarchy_name} not found',
        }
        expected_status_code = 400
    else:
        expected_data = _common_expected_data('')
        expected_status_code = 200

    await common.check_search_rules(
        taxi_grocery_marketing,
        hierarchy_name,
        [],
        1,
        None,
        expected_data,
        expected_status_code,
    )
