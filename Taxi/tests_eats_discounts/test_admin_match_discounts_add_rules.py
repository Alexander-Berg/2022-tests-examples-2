import json

import discounts_match  # pylint: disable=E0401
import pytest

from tests_eats_discounts import common


async def _check_add_rules(
        client,
        draft_headers,
        request: dict,
        match_discounts_request: dict,
        expected_match_discounts_response: dict,
):
    response = await client.post(
        common.ADD_RULES_URL, request, headers=draft_headers,
    )
    assert response.status_code == 200, response.text
    assert not response.content or response.content == b'{}'
    await common.check_admin_match_discounts(
        client,
        draft_headers,
        match_discounts_request,
        expected_match_discounts_response,
        200,
    )


async def _check_add_rules_check(
        client,
        draft_headers,
        request: dict,
        expected_response: dict,
        match_discounts_request: dict,
        expected_match_discounts_response: dict,
):
    response = await client.post(
        common.ADD_RULES_CHECK_URL, request, headers=draft_headers,
    )
    assert response.status_code == 200, response.json()
    assert response.json() == expected_response

    await common.check_admin_match_discounts(
        client,
        draft_headers,
        match_discounts_request,
        expected_match_discounts_response,
        200,
    )


@discounts_match.mark_now
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
async def test_add_rules_cart_discounts(client, draft_headers, load_json):
    await _check_add_rules(
        client,
        draft_headers,
        load_json('request.json'),
        load_json('admin_match_discounts_request.json'),
        load_json('admin_match_discounts_response.json'),
    )


@discounts_match.mark_now
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
async def test_add_rules_check_cart_discounts(
        client, draft_headers, load_json,
):
    await _check_add_rules_check(
        client,
        draft_headers,
        load_json('request.json'),
        load_json('response.json'),
        load_json('admin_match_discounts_request.json'),
        load_json('admin_match_discounts_response.json'),
    )


@discounts_match.mark_now
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
async def test_add_rules_menu_discounts(client, draft_headers, load_json):
    await _check_add_rules(
        client,
        draft_headers,
        load_json('request.json'),
        load_json('admin_match_discounts_request.json'),
        load_json('admin_match_discounts_response.json'),
    )


@discounts_match.mark_now
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
async def test_add_rules_check_menu_discounts(
        client, draft_headers, load_json,
):
    await _check_add_rules_check(
        client,
        draft_headers,
        load_json('request.json'),
        load_json('response.json'),
        load_json('admin_match_discounts_request.json'),
        load_json('admin_match_discounts_response.json'),
    )


@discounts_match.mark_now
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
async def test_add_rules_retail_menu_discounts(
        client, draft_headers, load_json,
):
    await _check_add_rules(
        client,
        draft_headers,
        load_json('request.json'),
        load_json('admin_match_discounts_request.json'),
        load_json('admin_match_discounts_response.json'),
    )


@discounts_match.mark_now
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
async def test_add_rules_check_retail_menu_discounts(
        client, draft_headers, load_json,
):
    await _check_add_rules_check(
        client,
        draft_headers,
        load_json('request.json'),
        load_json('response.json'),
        load_json('admin_match_discounts_request.json'),
        load_json('admin_match_discounts_response.json'),
    )


@discounts_match.mark_now
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
async def test_add_rules_payment_method_discounts(
        client, draft_headers, load_json,
):
    await common.init_bin_sets(client)
    await _check_add_rules(
        client,
        draft_headers,
        load_json('request.json'),
        load_json('admin_match_discounts_request.json'),
        load_json('admin_match_discounts_response.json'),
    )


@discounts_match.mark_now
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
async def test_add_rules_check_payment_method_discounts(
        client, draft_headers, load_json,
):
    await common.init_bin_sets(client)
    await _check_add_rules_check(
        client,
        draft_headers,
        load_json('request.json'),
        load_json('response.json'),
        load_json('admin_match_discounts_request.json'),
        load_json('admin_match_discounts_response.json'),
    )


@discounts_match.mark_now
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
async def test_add_rules_place_delivery_discounts(
        client, draft_headers, load_json,
):
    await common.init_bin_sets(client)
    await _check_add_rules(
        client,
        draft_headers,
        load_json('request.json'),
        load_json('admin_match_discounts_request.json'),
        load_json('admin_match_discounts_response.json'),
    )


@discounts_match.mark_now
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
async def test_add_rules_check_place_delivery_discounts(
        client, draft_headers, load_json,
):
    await common.init_bin_sets(client)
    await _check_add_rules_check(
        client,
        draft_headers,
        load_json('request.json'),
        load_json('response.json'),
        load_json('admin_match_discounts_request.json'),
        load_json('admin_match_discounts_response.json'),
    )


@discounts_match.mark_now
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
async def test_add_rules_yandex_delivery_discounts(
        client, draft_headers, load_json,
):
    await common.init_bin_sets(client)
    await _check_add_rules(
        client,
        draft_headers,
        load_json('request.json'),
        load_json('admin_match_discounts_request.json'),
        load_json('admin_match_discounts_response.json'),
    )


@discounts_match.mark_now
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
async def test_add_rules_check_yandex_delivery_discounts(
        client, draft_headers, load_json,
):
    await common.init_bin_sets(client)
    await _check_add_rules_check(
        client,
        draft_headers,
        load_json('request.json'),
        load_json('response.json'),
        load_json('admin_match_discounts_request.json'),
        load_json('admin_match_discounts_response.json'),
    )


@discounts_match.mark_now
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
async def test_add_rules_place_cashback(client, draft_headers, load_json):
    await common.init_bin_sets(client)
    await _check_add_rules(
        client,
        draft_headers,
        load_json('request.json'),
        load_json('admin_match_discounts_request.json'),
        load_json('admin_match_discounts_response.json'),
    )


@discounts_match.mark_now
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
async def test_add_rules_check_place_cashback(
        client, draft_headers, load_json,
):
    await common.init_bin_sets(client)
    await _check_add_rules_check(
        client,
        draft_headers,
        load_json('request.json'),
        load_json('response.json'),
        load_json('admin_match_discounts_request.json'),
        load_json('admin_match_discounts_response.json'),
    )


@discounts_match.mark_now
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
async def test_add_rules_place_menu_cashback(client, draft_headers, load_json):
    await common.init_bin_sets(client)
    await _check_add_rules(
        client,
        draft_headers,
        load_json('request.json'),
        load_json('admin_match_discounts_request.json'),
        load_json('admin_match_discounts_response.json'),
    )


@discounts_match.mark_now
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
async def test_add_rules_check_place_menu_cashback(
        client, draft_headers, load_json,
):
    await common.init_bin_sets(client)
    await _check_add_rules_check(
        client,
        draft_headers,
        load_json('request.json'),
        load_json('response.json'),
        load_json('admin_match_discounts_request.json'),
        load_json('admin_match_discounts_response.json'),
    )


@discounts_match.mark_now
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
async def test_add_rules_yandex_cashback(client, draft_headers, load_json):
    await common.init_bin_sets(client)
    await _check_add_rules(
        client,
        draft_headers,
        load_json('request.json'),
        load_json('admin_match_discounts_request.json'),
        load_json('admin_match_discounts_response.json'),
    )


@discounts_match.mark_now
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
async def test_add_rules_check_yandex_cashback(
        client, draft_headers, load_json,
):
    await common.init_bin_sets(client)
    await _check_add_rules_check(
        client,
        draft_headers,
        load_json('request.json'),
        load_json('response.json'),
        load_json('admin_match_discounts_request.json'),
        load_json('admin_match_discounts_response.json'),
    )


@discounts_match.mark_now
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
async def test_add_rules_yandex_menu_cashback(
        client, draft_headers, load_json,
):
    await common.init_bin_sets(client)
    await _check_add_rules(
        client,
        draft_headers,
        load_json('request.json'),
        load_json('admin_match_discounts_request.json'),
        load_json('admin_match_discounts_response.json'),
    )


@discounts_match.mark_now
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
async def test_add_rules_check_yandex_menu_cashback(
        client, draft_headers, load_json,
):
    await common.init_bin_sets(client)
    await _check_add_rules_check(
        client,
        draft_headers,
        load_json('request.json'),
        load_json('response.json'),
        load_json('admin_match_discounts_request.json'),
        load_json('admin_match_discounts_response.json'),
    )


@discounts_match.mark_now
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
async def test_add_rules_restaurant_menu_discounts(
        client, draft_headers, load_json,
):
    await _check_add_rules(
        client,
        draft_headers,
        load_json('request.json'),
        load_json('admin_match_discounts_request.json'),
        load_json('admin_match_discounts_response.json'),
    )


@discounts_match.mark_now
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
async def test_add_rules_check_restaurant_menu_discounts(
        client, draft_headers, load_json,
):
    await _check_add_rules_check(
        client,
        draft_headers,
        load_json('request.json'),
        load_json('response.json'),
        load_json('admin_match_discounts_request.json'),
        load_json('admin_match_discounts_response.json'),
    )


@discounts_match.mark_now
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
async def test_add_rules_restaurant_discounts(
        client, draft_headers, load_json,
):
    await _check_add_rules(
        client,
        draft_headers,
        load_json('request.json'),
        load_json('admin_match_discounts_request.json'),
        load_json('admin_match_discounts_response.json'),
    )


@discounts_match.mark_now
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
async def test_add_rules_check_restaurant_discounts(
        client, draft_headers, load_json,
):
    await _check_add_rules_check(
        client,
        draft_headers,
        load_json('request.json'),
        load_json('response.json'),
        load_json('admin_match_discounts_request.json'),
        load_json('admin_match_discounts_response.json'),
    )


@discounts_match.mark_now
@pytest.mark.config(
    EATS_DISCOUNTS_PROMO_TYPES=[
        {
            'type': 'promo_type',
            'description': 'some_description',
            'name': 'some_name',
        },
    ],
)
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
async def test_add_rules_check_promo_types(client, draft_headers, load_json):
    await client.invalidate_caches()
    await _check_add_rules_check(
        client,
        draft_headers,
        load_json('request.json'),
        load_json('response.json'),
        load_json('admin_match_discounts_request.json'),
        load_json('admin_match_discounts_response.json'),
    )


@discounts_match.mark_now
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
async def test_add_rules_limit(client, draft_headers, load_json, mockserver):
    @mockserver.json_handler('/billing-limits/v1/create')
    def _put_data_handler(request):
        billing_create_request = json.loads(request.get_data())
        assert billing_create_request == load_json(
            'billing_limits_create_request.json',
        )
        return load_json('billing_limits_create_response.json')

    await _check_add_rules(
        client,
        draft_headers,
        load_json('request.json'),
        load_json('admin_match_discounts_request.json'),
        load_json('admin_match_discounts_response.json'),
    )
