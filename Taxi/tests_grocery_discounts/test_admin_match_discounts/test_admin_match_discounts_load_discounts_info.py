import copy
from typing import List
from typing import Optional

import discounts_match  # pylint: disable=E0401
import pytest

from tests_grocery_discounts import common


async def check_load_discounts_info(
        taxi_grocery_discounts,
        hierarchy_name: str,
        revisions: List[int],
        expected_data: Optional[dict],
        expected_status_code: int,
):
    def _make_response_rules(result_data: Optional[dict]):
        if result_data is None:
            return
        for discount in result_data['discounts_info']:
            discount.pop('revision')

    expected_data = copy.deepcopy(expected_data)

    request = {
        'hierarchy_name': hierarchy_name,
        'revisions': revisions,
        'conditions_names': ['active_period'],
    }

    response = await taxi_grocery_discounts.post(
        'v3/admin/match-discounts/load-discounts-info/',
        request,
        headers=common.get_headers(),
    )

    response_json = response.json()

    assert response.status_code == expected_status_code, response_json

    if expected_status_code != 200:
        if expected_data is not None:
            assert response_json == expected_data
        return

    if expected_data is not None:
        _make_response_rules(response_json)

        assert response_json == expected_data


def _common_expected_data(
        hierarchy_name: Optional[str] = None,
        active_period: Optional[dict] = None,
) -> dict:

    valid_active_period = {
        'condition_name': 'active_period',
        'value': {
            'start': '2020-01-01T09:00:01+00:00',
            'is_start_utc': False,
            'is_end_utc': False,
            'end': '2021-01-01T00:00:00+00:00',
        },
    }

    result: dict = {
        'discounts_info': [
            {'match_path_params': [valid_active_period], 'name': '1'},
        ],
    }
    return result


@pytest.mark.parametrize(
    'hierarchy_name',
    (
        pytest.param('menu_discounts', id='menu_discounts_hierarchy'),
        pytest.param('cart_discounts', id='cart_discounts_hierarchy'),
        pytest.param(
            'payment_method_discounts',
            id='payment_method_discounts_hierarchy',
        ),
        pytest.param('dynamic_discounts', id='dynamic_discounts_hierarchy'),
    ),
)
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
@pytest.mark.config(
    GROCERY_DISCOUNTS_APPLICATION_NAME_VALIDATION={
        'application_names': ['some_application_name'],
        'enabled': True,
    },
    GROCERY_DISCOUNTS_USE_NAMED_GROUPS=True,
)
async def test_load_discounts_info_common(
        taxi_grocery_discounts,
        pgsql,
        mocked_time,
        hierarchy_name: str,
        add_rules,
) -> None:

    await add_rules(
        common.get_add_rules_data(hierarchy_names=frozenset([hierarchy_name])),
    )

    await check_load_discounts_info(
        taxi_grocery_discounts,
        hierarchy_name,
        [common.get_last_revision(pgsql, hierarchy_name)],
        _common_expected_data(hierarchy_name),
        200,
    )


@pytest.mark.parametrize(
    'hierarchy_name',
    (
        pytest.param(
            'menu_discounts',
            marks=discounts_match.remove_hierarchies('menu_discounts'),
            id='missing_menu_discounts',
        ),
        pytest.param(
            'cart_discounts',
            marks=discounts_match.remove_hierarchies('cart_discounts'),
            id='missing_cart_discounts',
        ),
        pytest.param(
            'payment_method_discounts',
            marks=discounts_match.remove_hierarchies(
                'payment_method_discounts',
            ),
            id='missing_payment_method_discounts',
        ),
        pytest.param(
            'dynamic_discounts',
            marks=discounts_match.remove_hierarchies('dynamic_discounts'),
            id='missing_dynamic_discounts',
        ),
    ),
)
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
@pytest.mark.config(
    GROCERY_DISCOUNTS_APPLICATION_NAME_VALIDATION={
        'application_names': ['some_application_name'],
        'enabled': True,
    },
    GROCERY_DISCOUNTS_USE_NAMED_GROUPS=True,
)
async def test_load_discounts_info_missing_hierarchy(
        taxi_grocery_discounts, hierarchy_name,
) -> None:
    expected_data: dict = {
        'code': 'Validation error',
        'message': f'hierarchy {hierarchy_name} not found',
    }
    expected_status_code = 400

    await check_load_discounts_info(
        taxi_grocery_discounts,
        hierarchy_name,
        [],
        expected_data,
        expected_status_code,
    )


@pytest.mark.parametrize(
    'hierarchy_name',
    (
        pytest.param('menu_discounts', id='menu_discounts'),
        pytest.param('cart_discounts', id='cart_discounts'),
    ),
)
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
@pytest.mark.config(
    GROCERY_DISCOUNTS_APPLICATION_NAME_VALIDATION={
        'application_names': ['some_application_name'],
        'enabled': True,
    },
    GROCERY_DISCOUNTS_USE_NAMED_GROUPS=True,
)
async def test_load_discounts_info_several_revisions(
        taxi_grocery_discounts, pgsql, hierarchy_name, add_rules,
) -> None:
    count = 3
    revisions = []
    for num in range(count):
        active_period = {
            'condition_name': 'active_period',
            'values': [
                {
                    'start': f'2020-01-0{num+1}T09:00:00+00:00',
                    'is_start_utc': True,
                    'is_end_utc': True,
                    'end': f'2020-01-0{num+1}T10:00:00+00:00',
                },
            ],
        }
        await add_rules(
            common.get_add_rules_data(
                active_period, hierarchy_names=frozenset([hierarchy_name]),
            ),
        )
        revisions.append(common.get_last_revision(pgsql, hierarchy_name))

    await check_load_discounts_info(
        taxi_grocery_discounts, hierarchy_name, revisions, None, 200,
    )
