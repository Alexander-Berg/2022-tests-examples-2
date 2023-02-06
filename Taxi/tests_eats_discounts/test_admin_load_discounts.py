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


TEST_OK_PARAMETRIZE = (
    pytest.param(
        'payment_method_discounts',
        'discount_ids_request.json',
        'response.json',
        id='payment_method_discounts_discount_ids_ok',
    ),
    pytest.param(
        'payment_method_discounts',
        'revisions_request.json',
        'response.json',
        id='payment_method_discounts_revisions_ok',
    ),
    pytest.param(
        'payment_method_discounts',
        'without_hierarchy_name_request.json',
        'response.json',
        id='without_hierarchy_name_ok',
    ),
    pytest.param(
        'payment_method_discounts',
        'create_draft_id_request.json',
        'create_draft_id_response.json',
        id='payment_method_discounts_create_draft_id_ok',
    ),
    pytest.param(
        'payment_method_discounts',
        'substring_of_name_request.json',
        'substring_of_name_response.json',
        id='payment_method_discounts_substring_of_name_ok',
    ),
)


@pytest.mark.parametrize(
    'hierarchy_name, request_filename, response_filename', TEST_OK_PARAMETRIZE,
)
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
@discounts_match.mark_now
async def test_admin_load_discounts_ok(
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
    await common.check_admin_load_discounts(
        client,
        draft_headers,
        load_json(request_filename),
        load_json(response_filename),
        200,
    )


TEST_FAIL_PARAMETRIZE = (
    pytest.param('bad_discount_id_request.json', id='bad_discount_id_fail'),
    pytest.param(
        'invalid_cursor_request.json', id='invalid_cursor_request_fail',
    ),
    pytest.param(
        'without_hierarchy_and_discount_id.json',
        id='without_hierarchy_and_discount_id',
    ),
)


@pytest.mark.parametrize('request_filename', TEST_FAIL_PARAMETRIZE)
async def test_admin_load_discounts_fail(
        client, load_json, draft_headers, request_filename: str,
):
    await common.check_admin_load_discounts(
        client, draft_headers, load_json(request_filename), None, 400,
    )


TEST_PAGINATION_PARAMETRIZE = (
    pytest.param(
        'payment_method_discounts',
        ('request_1.json', 'response_1.json'),
        ('request_2.json', 'response_2.json'),
        ('request_3.json', 'response_3.json'),
        ('request_4.json', 'response_4.json'),
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
    EATS_DISCOUNTS_ADMIN_LOAD_DISCOUNTS_SETTINGS={'max_discounts': 1},
)
async def test_admin_load_discounts_pagination(
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
    await common.check_admin_load_discounts(
        client, draft_headers, load_json(page_1[0]), load_json(page_1[1]), 200,
    )
    await common.check_admin_load_discounts(
        client, draft_headers, load_json(page_2[0]), load_json(page_2[1]), 200,
    )
    await common.check_admin_load_discounts(
        client, draft_headers, load_json(page_3[0]), load_json(page_3[1]), 200,
    )
    await common.check_admin_load_discounts(
        client, draft_headers, load_json(page_4[0]), load_json(page_4[1]), 200,
    )
