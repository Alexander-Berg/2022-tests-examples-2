import pytest

from testsuite.utils import http

from tests_ride_discounts import common


PHONE_ID = '1' * 24


async def _update_cache(client, fail_expected: bool):
    failed = False
    try:
        await client.invalidate_caches(cache_names=['rules-match-cache'])
    except http.HttpResponseError:
        failed = True
    assert fail_expected == failed


async def _add_discounts(add_rules):
    """
    Adding any rules, the main thing is that they get into the cache in time
    """
    add_rules_data = common.get_add_rules_data(
        (
            'full_money_discounts',
            'full_cashback_discounts',
            'experimental_money_discounts',
            'experimental_cashback_discounts',
        ),
    )
    await add_rules(add_rules_data)


@pytest.mark.pgsql('ride_discounts', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
async def test_update_cache_with_exception_load_rules(
        client, add_rules, testpoint,
):
    """"
    A cache update failure is simulated
    """
    inject_error = False

    @testpoint('rules_match_cache_error_test_point_in_load_rules')
    def _rules_match_cache_error_test_point_in_load_rules(data):
        return {'inject_failure': True} if inject_error else None

    await _add_discounts(add_rules)
    await _update_cache(client, inject_error)
    inject_error = True
    await _update_cache(client, inject_error)
    inject_error = False
    await _update_cache(client, inject_error)
    request = {
        'common_conditions': {
            'request_time': '2020-01-03T18:00:00+03:00',
            'client_timezone': 'Europe/Moscow',
            'tariff_zone': 'moscow',
            'has_yaplus': True,
            'waypoints': [[1.0, 2.0]],
            'user_info': {
                'user_id': 'user_id',
                'phone_id': PHONE_ID,
                'phone_hash': '138aa82720f81ba2249011d',
                'personal_phone_id': 'personal_phone_id',
                'yandex_uid': 'Yandex_uid',
            },
        },
        'subqueries': [{'tariff': 'econom', 'surge': 1.2}],
    }
    response = await client.post(
        'v3/match-discounts/', headers=common.get_headers(), json=request,
    )
    assert response.status == 200
