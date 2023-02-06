from typing import Dict

import discounts_match  # pylint: disable=E0401
import pytest

from tests_eats_discounts import common


def _get_prepared_response(response: Dict) -> dict:
    response['match_results'].sort(key=lambda result: result['hierarchy_name'])
    return response


@pytest.mark.now('2020-01-01T00:00:00+00:00')
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
async def test_v2_match_discounts_bad_request(client):
    response = await client.post(
        'v2/match-discounts/',
        headers=common.get_headers(),
        json={
            'common_conditions': {
                'request_time': '2020-02-01T09:00:01+00:00',
                'place_time_zone': 'UTC',
                'conditions': {'product': ['product']},
            },
        },
    )
    assert response.status == 400, response.json()
    assert response.json() == {
        'code': 'Validation error',
        'message': (
            'subqueries or common_conditions.hierarchy_names must be set'
        ),
    }


@pytest.mark.now('2020-01-01T00:00:00+00:00')
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
async def test_v2_match_discounts_ok(client, load_json, add_rules):
    await common.init_bin_sets(client)

    add_rules_data = load_json('add_rules_data.json')
    await add_rules(add_rules_data, {'series_id': common.SERIES_ID})
    await client.invalidate_caches()

    request = load_json('match_discounts_request.json')
    response = await client.post(
        'v2/match-discounts/', headers=common.get_headers(), json=request,
    )
    assert response.status == 200, response.json()
    expected_response = _get_prepared_response(
        load_json('match_discounts_response.json'),
    )
    assert _get_prepared_response(response.json()) == expected_response


@pytest.mark.now('2020-01-01T00:00:00+00:00')
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
@discounts_match.remove_hierarchies(
    'retail_menu_discounts', 'payment_method_discounts',
)
async def test_v2_match_discounts_missing_hierarchies(
        client, load_json, add_rules,
):
    await common.init_bin_sets(client)
    add_rules_data = load_json('add_rules_data.json')
    for hierarchy_name in [
            'retail_menu_discounts',
            'payment_method_discounts',
    ]:
        add_rules_data.pop(hierarchy_name)
    await add_rules(add_rules_data, {'series_id': common.SERIES_ID})
    await client.invalidate_caches()

    request = load_json('match_discounts_request.json')
    response = await client.post(
        'v2/match-discounts/', headers=common.get_headers(), json=request,
    )
    assert response.status == 200, response.json()
    expected_response = _get_prepared_response(
        load_json('match_discounts_response.json'),
    )
    assert _get_prepared_response(response.json()) == expected_response
