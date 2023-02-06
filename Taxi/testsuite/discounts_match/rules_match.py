import pytest

from testsuite.utils import http


async def _update_cache(client, fail_expected: bool):
    failed = False
    try:
        await client.invalidate_caches(cache_names=['rules-match-cache'])
    except http.HttpResponseError:
        failed = True
    assert fail_expected == failed


async def _call(client, handler_url, headers, fail_expected):
    response = await client.get(handler_url, headers=headers)
    assert response.status_code == (500 if fail_expected else 200)


@pytest.fixture
def check_invalid_rules_match(
        client, hierarchy_descriptions_url, headers, testpoint,
):
    async def func(old_cache_prohibited: bool):
        inject_error_1 = False
        inject_error_2 = False

        @testpoint('rules_match_cache_error_test_point_1')
        def _rules_match_cache_error_test_point_1(data):
            nonlocal inject_error_1
            return {'inject_failure': True} if inject_error_1 else None

        @testpoint('rules_match_cache_error_test_point_2')
        def _rules_match_cache_error_test_point_2(data):
            nonlocal inject_error_2
            return {'inject_failure': True} if inject_error_2 else None

        await _update_cache(client, False)

        inject_error_1 = True

        await _update_cache(client, True)

        await _call(
            client, hierarchy_descriptions_url, headers, old_cache_prohibited,
        )
        await _call(client, 'ping', headers, False)

        inject_error_2 = True

        await _update_cache(client, True)

        await _call(client, hierarchy_descriptions_url, headers, False)
        await _call(client, 'ping', headers, old_cache_prohibited)

    return func
