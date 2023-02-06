from typing import List
import uuid

import discounts_match  # pylint: disable=E0401
import pytest

from tests_ride_discounts import common


def _prepare_response(response: dict) -> dict:
    discounts_info = response['discounts_info']
    discounts_info.sort(key=lambda x: (x['hierarchy_name'], x['name']))
    for discount_info in discounts_info:
        discount_info['conditions'].sort(key=lambda x: x['condition_name'])
        discount_info.pop('create_draft_id', None)
    return response


def _compare_responses(response: dict, expected_response: dict):
    assert _prepare_response(response) == _prepare_response(expected_response)


async def _add_rules(
        hierarchy_name: str,
        name: str,
        check_add_rules_validation,
        rules: List[dict],
):
    await check_add_rules_validation(
        False,
        {'affected_discount_ids': [], 'series_id': str(uuid.uuid4())},
        hierarchy_name,
        rules + [discounts_match.VALID_ACTIVE_PERIOD],
        common.make_discount(name, hierarchy_name=hierarchy_name),
    )


async def _init_data(check_add_rules_validation, additional_rules):
    discount_id = int(common.START_DATA_ID)
    for hierarchy_name in (
            'payment_method_money_discounts',
            'experimental_money_discounts',
            'full_money_discounts',
    ):
        await _add_rules(
            hierarchy_name,
            str(discount_id),
            check_add_rules_validation,
            [
                {'condition_name': 'tariff', 'values': ['business']},
                {'condition_name': 'tag', 'values': ['tag3', 'tag4']},
            ]
            + additional_rules,
        )
        discount_id += 1
        await _add_rules(
            hierarchy_name,
            str(discount_id),
            check_add_rules_validation,
            [
                {'condition_name': 'tariff', 'values': ['econom', 'business']},
                {'condition_name': 'tag', 'values': ['tag1', 'tag2']},
            ]
            + additional_rules,
        )
        discount_id += 1


@pytest.mark.now('2019-01-01T00:00:00+00:00')
@pytest.mark.pgsql('ride_discounts', files=['init.sql'])
async def test_admin_load_discounts_info_ok(
        client,
        check_add_rules_validation,
        load_json,
        additional_rules,
        reset_data_id,
):
    await _init_data(check_add_rules_validation, additional_rules)

    request = load_json('request.json')
    response = await client.post(
        '/v1/admin/match-discounts/load-discounts-info',
        headers=common.get_headers(),
        json=request,
    )
    assert response.status == 200
    expected_response = load_json('expected_response.json')
    _compare_responses(response.json(), expected_response)


@pytest.mark.now('2019-01-01T00:00:00+00:00')
@pytest.mark.pgsql('ride_discounts', files=['init.sql'])
async def test_admin_load_discounts_info_fail(
        client,
        check_add_rules_validation,
        load_json,
        additional_rules,
        reset_data_id,
):
    request = load_json('request.json')
    response = await client.post(
        '/v1/admin/match-discounts/load-discounts-info',
        headers=common.get_headers(),
        json=request,
    )
    assert response.status == 400
    expected_response = load_json('expected_response.json')
    assert response.json() == expected_response
