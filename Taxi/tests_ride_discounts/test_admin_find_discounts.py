from typing import List
from typing import Tuple
import uuid

import discounts_match  # pylint: disable=E0401
import pytest

from tests_ride_discounts import common


def _prepare_response(response: dict) -> dict:
    discounts_info: List[dict] = response['discounts_data']['discounts_info']
    discounts_info.sort(key=lambda x: x['name'])
    for info in discounts_info:
        info.pop('discount_id')
        info.pop('create_draft_id', None)
        info['conditions'].sort(key=lambda x: x['condition_name'])
    return response


def _compare_responses(response: dict, expected_response: dict):
    assert _prepare_response(response) == _prepare_response(expected_response)


async def _add_rules(
        hierarchy_name: str,
        name: str,
        check_add_rules_validation,
        rules: List[dict],
        custom_draft_id: str,
):
    await check_add_rules_validation(
        False,
        {'affected_discount_ids': [], 'series_id': str(uuid.uuid4())},
        hierarchy_name,
        rules + [discounts_match.VALID_ACTIVE_PERIOD],
        common.make_discount(name, hierarchy_name=hierarchy_name),
        custom_draft_id=custom_draft_id,
    )


async def _init_data(
        check_add_rules_validation, additional_rules, hierarchy_name: str,
):
    await _add_rules(
        hierarchy_name,
        common.START_DATA_ID,
        check_add_rules_validation,
        [
            {'condition_name': 'tariff', 'values': ['business']},
            {'condition_name': 'tag', 'values': ['tag3', 'tag4']},
        ]
        + additional_rules,
        '1',
    )
    await _add_rules(
        hierarchy_name,
        str(int(common.START_DATA_ID) + 1),
        check_add_rules_validation,
        [{'condition_name': 'tag', 'values': ['tag3', 'tag4']}]
        + additional_rules,
        '2',
    )
    await _add_rules(
        hierarchy_name,
        str(int(common.START_DATA_ID) + 2),
        check_add_rules_validation,
        [
            {'condition_name': 'tariff', 'values': ['econom', 'business']},
            {'condition_name': 'tag', 'values': ['tag1', 'tag2']},
        ]
        + additional_rules,
        '3',
    )


async def _check_find_discounts(
        client,
        load_json,
        draft_headers,
        request_filename: str,
        response_filename: str,
):
    request = load_json(request_filename)
    response = await client.post(
        '/v1/admin/match-discounts/find-discounts',
        json=request,
        headers=draft_headers,
    )

    expected_response = load_json(response_filename)
    assert response.status_code == 200, expected_response
    _compare_responses(response.json(), expected_response)


TEST_OK_PARAMETRIZE = (
    pytest.param(
        'payment_method_money_discounts',
        'payment_method_discounts_fetch_match_request.json',
        'payment_method_discounts_fetch_match_response.json',
        id='payment_method_discounts_fetch_match_ok',
    ),
    pytest.param(
        'payment_method_money_discounts',
        'payment_method_discounts_with_invalid_ticket_request.json',
        'payment_method_discounts_with_invalid_ticket_response.json',
        id='payment_method_discounts_with_invalid_ticket',
    ),
    pytest.param(
        'payment_method_money_discounts',
        'payment_method_discounts_weak_match_request.json',
        'payment_method_discounts_weak_match_response.json',
        id='payment_method_discounts_weak_match_ok',
    ),
    pytest.param(
        'full_money_discounts',
        'full_discounts_fetch_match_request.json',
        'full_discounts_fetch_match_response.json',
        id='full_discounts_fetch_match_ok',
    ),
    pytest.param(
        'full_money_discounts',
        'full_discounts_weak_match_request.json',
        'full_discounts_weak_match_response.json',
        id='full_discounts_weak_match_ok',
    ),
    pytest.param(
        'experimental_money_discounts',
        'experimental_discounts_fetch_match_request.json',
        'experimental_discounts_fetch_match_response.json',
        id='experimental_discounts_fetch_match_ok',
    ),
    pytest.param(
        'experimental_money_discounts',
        'experimental_discounts_weak_match_request.json',
        'experimental_discounts_weak_match_response.json',
        id='experimental_discounts_weak_match_ok',
    ),
)


@pytest.mark.parametrize(
    'hierarchy_name, request_filename, response_filename', TEST_OK_PARAMETRIZE,
)
@pytest.mark.pgsql('ride_discounts', files=['init.sql'])
@discounts_match.mark_now
@pytest.mark.config(
    USERVICE_AGGLOMERATIONS_CACHE_SETTINGS={
        '__default__': {
            'enabled': True,
            'log_errors': True,
            'verify_on_updates': True,
        },
    },
)
async def test_admin_find_discounts_ok(
        client,
        load_json,
        check_add_rules_validation,
        draft_headers,
        additional_rules,
        reset_data_id,
        hierarchy_name: str,
        request_filename: str,
        response_filename: str,
):
    await _init_data(
        check_add_rules_validation, additional_rules, hierarchy_name,
    )
    await _check_find_discounts(
        client, load_json, draft_headers, request_filename, response_filename,
    )


TEST_BY_NAME_OK_PARAMETRIZE = (
    pytest.param(
        'fetch_match_by_name_request.json',
        'fetch_match_by_name_response.json',
        id='fetch_match_by_name_ok',
    ),
    pytest.param(
        'weak_match_by_name_request.json',
        'weak_match_by_name_response.json',
        id='weak_match_by_name_ok',
    ),
    pytest.param(
        'fetch_match_by_missing_name_request.json',
        'fetch_match_by_missing_name_response.json',
        id='fetch_match_by_missing_name_ok',
    ),
    pytest.param(
        'weak_match_by_missing_name_request.json',
        'weak_match_by_missing_name_response.json',
        id='weak_match_by_missing_name_ok',
    ),
)


@pytest.mark.parametrize(
    'request_filename, response_filename', TEST_BY_NAME_OK_PARAMETRIZE,
)
@pytest.mark.pgsql('ride_discounts', files=['init.sql'])
@discounts_match.mark_now
@pytest.mark.config(
    USERVICE_AGGLOMERATIONS_CACHE_SETTINGS={
        '__default__': {
            'enabled': True,
            'log_errors': True,
            'verify_on_updates': True,
        },
    },
)
async def test_admin_find_discounts_by_name_ok(
        client,
        load_json,
        check_add_rules_validation,
        draft_headers,
        additional_rules,
        reset_data_id,
        request_filename: str,
        response_filename: str,
):
    hierarchy_name = 'full_money_discounts'
    await _init_data(
        check_add_rules_validation, additional_rules, hierarchy_name,
    )
    await _check_find_discounts(
        client, load_json, draft_headers, request_filename, response_filename,
    )


TEST_BY_DRAFT_ID_OK_PARAMETRIZE = (
    pytest.param(
        'fetch_match_by_draft_id_request.json',
        'fetch_match_by_draft_id_response.json',
        id='fetch_match_by_draft_id_ok',
    ),
    pytest.param(
        'weak_match_by_draft_id_request.json',
        'weak_match_by_draft_id_response.json',
        id='weak_match_by_draft_id_ok',
    ),
    pytest.param(
        'fetch_match_by_missing_draft_id_request.json',
        'fetch_match_by_missing_draft_id_response.json',
        id='fetch_match_by_missing_draft_id_ok',
    ),
    pytest.param(
        'weak_match_by_missing_draft_id_request.json',
        'weak_match_by_missing_draft_id_response.json',
        id='weak_match_by_missing_draft_id_ok',
    ),
)


@pytest.mark.parametrize(
    'request_filename, response_filename', TEST_BY_DRAFT_ID_OK_PARAMETRIZE,
)
@pytest.mark.pgsql('ride_discounts', files=['init.sql'])
@discounts_match.mark_now
@pytest.mark.config(
    USERVICE_AGGLOMERATIONS_CACHE_SETTINGS={
        '__default__': {
            'enabled': True,
            'log_errors': True,
            'verify_on_updates': True,
        },
    },
)
async def test_admin_find_discounts_by_draft_id_ok(
        client,
        load_json,
        check_add_rules_validation,
        draft_headers,
        additional_rules,
        reset_data_id,
        request_filename: str,
        response_filename: str,
):
    hierarchy_name = 'full_money_discounts'
    await _init_data(
        check_add_rules_validation, additional_rules, hierarchy_name,
    )
    await _check_find_discounts(
        client, load_json, draft_headers, request_filename, response_filename,
    )


TEST_PAGINATION_PARAMETRIZE = (
    pytest.param(
        'full_money_discounts',
        (
            'full_discounts_weak_match_1_request.json',
            'full_discounts_weak_match_1_response.json',
        ),
        (
            'full_discounts_weak_match_2_request.json',
            'full_discounts_weak_match_2_response.json',
        ),
        (
            'full_discounts_weak_match_3_request.json',
            'full_discounts_weak_match_3_response.json',
        ),
        id='full_discounts_weak_match_pagination',
    ),
    pytest.param(
        'payment_method_money_discounts',
        (
            'payment_method_discounts_fetch_match_1_request.json',
            'payment_method_discounts_fetch_match_1_response.json',
        ),
        (
            'payment_method_discounts_fetch_match_2_request.json',
            'payment_method_discounts_fetch_match_2_response.json',
        ),
        (
            'payment_method_discounts_fetch_match_3_request.json',
            'payment_method_discounts_fetch_match_3_response.json',
        ),
        id='payment_method_discounts_fetch_match_pagination',
    ),
)


@pytest.mark.parametrize(
    'hierarchy_name, page_1, page_2, page_3', TEST_PAGINATION_PARAMETRIZE,
)
@pytest.mark.pgsql('ride_discounts', files=['init.sql'])
@discounts_match.mark_now
@pytest.mark.config(
    RIDE_DISCOUNTS_FIND_DISCOUNTS_SETTINGS={'max_discounts': 1},
    USERVICE_AGGLOMERATIONS_CACHE_SETTINGS={
        '__default__': {
            'enabled': True,
            'log_errors': True,
            'verify_on_updates': True,
        },
    },
)
async def test_admin_find_discounts_pagination(
        client,
        load_json,
        check_add_rules_validation,
        draft_headers,
        additional_rules,
        reset_revision,
        reset_data_id,
        hierarchy_name: str,
        page_1: Tuple[str, str],
        page_2: Tuple[str, str],
        page_3: Tuple[str, str],
):
    await _init_data(
        check_add_rules_validation, additional_rules, hierarchy_name,
    )

    await _check_find_discounts(
        client, load_json, draft_headers, page_1[0], page_1[1],
    )
    await _check_find_discounts(
        client, load_json, draft_headers, page_2[0], page_2[1],
    )
    await _check_find_discounts(
        client, load_json, draft_headers, page_3[0], page_3[1],
    )
