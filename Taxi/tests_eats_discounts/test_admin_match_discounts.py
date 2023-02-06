from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
import uuid

import discounts_match  # pylint: disable=E0401
import pytest

from tests_eats_discounts import common


DISCOUNTS = {'payment_method_discounts': common.small_payment_method_discount}


async def _add_rules(
        hierarchy_name: str,
        name: str,
        check_add_rules_validation,
        rules: List[dict],
        revisions: List[int],
        active_period: Optional[Dict] = None,
):
    await check_add_rules_validation(
        False,
        {
            'revisions': revisions,
            'series_id': str(uuid.uuid4()),
            'update_existing_discounts': bool(revisions),
        },
        hierarchy_name,
        rules
        + [
            common.VALID_ACTIVE_PERIOD
            if active_period is None
            else active_period,
        ],
        DISCOUNTS[hierarchy_name](name),
    )


async def _check_add_rules(
        hierarchy_name: str,
        name: str,
        check_add_rules_validation,
        rules: List[dict],
        active_period,
):
    return await check_add_rules_validation(
        True,
        {'series_id': str(uuid.uuid4()), 'update_existing_discounts': True},
        hierarchy_name,
        rules + [active_period],
        DISCOUNTS[hierarchy_name](name),
        200,
        None,
        2,
    )


ACTIVE_PERIOD = {
    'condition_name': 'active_period',
    'values': [
        {
            'start': '2020-01-12T09:00:01+00:00',
            'is_start_utc': True,
            'is_end_utc': True,
            'end': '2021-01-02T00:00:00+00:00',
        },
    ],
}


async def _init_data(
        check_add_rules_validation, additional_rules, hierarchy_name: str,
):
    await _add_rules(
        hierarchy_name,
        common.START_DATA_ID,
        check_add_rules_validation,
        [
            {'condition_name': 'brand', 'values': [1]},
            {'condition_name': 'place', 'values': [3, 4]},
        ]
        + additional_rules,
        [],
    )
    await _add_rules(
        hierarchy_name,
        str(int(common.START_DATA_ID) + 1),
        check_add_rules_validation,
        [{'condition_name': 'place', 'values': [3, 4]}] + additional_rules,
        [],
    )
    await _add_rules(
        hierarchy_name,
        str(int(common.START_DATA_ID) + 2),
        check_add_rules_validation,
        [
            {'condition_name': 'brand', 'values': [1, 2]},
            {'condition_name': 'place', 'values': [1, 2]},
        ]
        + additional_rules,
        [],
    )
    revisions = await _check_add_rules(
        hierarchy_name,
        str(int(common.START_DATA_ID) + 3),
        check_add_rules_validation,
        [
            {'condition_name': 'brand', 'values': [1, 2]},
            {'condition_name': 'place', 'values': [1]},
        ]
        + additional_rules,
        ACTIVE_PERIOD,
    )

    await _add_rules(
        hierarchy_name,
        str(int(common.START_DATA_ID) + 3),
        check_add_rules_validation,
        [
            {'condition_name': 'brand', 'values': [1, 2]},
            {'condition_name': 'place', 'values': [1]},
        ]
        + additional_rules,
        revisions,
        ACTIVE_PERIOD,
    )

    await _add_rules(
        hierarchy_name,
        str(int(common.START_DATA_ID) + 4),
        check_add_rules_validation,
        [
            {'condition_name': 'brand', 'values': [7, 8]},
            {'condition_name': 'place', 'values': [7]},
            {'condition_name': 'experiment', 'values': ['exp']},
        ]
        + additional_rules,
        [],
    )


TEST_OK_PARAMETRIZE = (
    pytest.param(
        'payment_method_discounts',
        'payment_method_discounts_request_1.json',
        'payment_method_discounts_response_1.json',
        id='payment_method_discounts_ok',
    ),
    pytest.param(
        'payment_method_discounts',
        'payment_method_discounts_request_2.json',
        'payment_method_discounts_response_2.json',
        id='payment_method_discounts_experiment_ok',
    ),
)


@pytest.mark.parametrize(
    'hierarchy_name, request_filename, response_filename', TEST_OK_PARAMETRIZE,
)
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
@discounts_match.mark_now
async def test_admin_match_discounts_ok(
        client,
        load_json,
        check_add_rules_validation,
        draft_headers,
        additional_rules,
        hierarchy_name: str,
        request_filename: str,
        response_filename: str,
):
    await _init_data(
        check_add_rules_validation, additional_rules, hierarchy_name,
    )
    await common.check_admin_match_discounts(
        client,
        draft_headers,
        load_json(request_filename),
        load_json(response_filename),
        200,
    )


TEST_PAGINATION_PARAMETRIZE = (
    pytest.param(
        'payment_method_discounts',
        (
            'payment_method_discounts_1_request.json',
            'payment_method_discounts_1_response.json',
        ),
        (
            'payment_method_discounts_2_request.json',
            'payment_method_discounts_2_response.json',
        ),
        (
            'payment_method_discounts_3_request.json',
            'payment_method_discounts_3_response.json',
        ),
        (
            'payment_method_discounts_4_request.json',
            'payment_method_discounts_4_response.json',
        ),
        id='payment_method_discounts_pagination',
    ),
)


@pytest.mark.parametrize(
    'hierarchy_name, page_1, page_2, page_3, page_4',
    TEST_PAGINATION_PARAMETRIZE,
)
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
@discounts_match.mark_now
@pytest.mark.config(
    EATS_DISCOUNTS_ADMIN_MATCH_DISCOUNTS_SETTINGS={'max_discounts': 1},
)
async def test_admin_match_discounts_pagination(
        client,
        load_json,
        check_add_rules_validation,
        draft_headers,
        additional_rules,
        hierarchy_name: str,
        page_1: Tuple[str, str],
        page_2: Tuple[str, str],
        page_3: Tuple[str, str],
        page_4: Tuple[str, str],
):
    await _init_data(
        check_add_rules_validation, additional_rules, hierarchy_name,
    )

    await common.check_admin_match_discounts(
        client, draft_headers, load_json(page_1[0]), load_json(page_1[1]), 200,
    )
    await common.check_admin_match_discounts(
        client, draft_headers, load_json(page_2[0]), load_json(page_2[1]), 200,
    )
    await common.check_admin_match_discounts(
        client, draft_headers, load_json(page_3[0]), load_json(page_3[1]), 200,
    )
    await common.check_admin_match_discounts(
        client, draft_headers, load_json(page_4[0]), load_json(page_4[1]), 200,
    )


async def test_admin_match_discounts_fail(client, draft_headers):
    await common.check_admin_match_discounts(
        client,
        draft_headers,
        {
            'conditions': [{'condition_name': 'brand', 'values': ['']}],
            'hierarchy_name': 'menu_discounts',
        },
        {
            'code': 'Validation error',
            'message': (
                'Exception in AnyOtherConditionsVectorFromGenerated '
                'for \'brand\' : Wrong type!'
            ),
        },
        400,
    )
