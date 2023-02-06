import pytest

from tests_bank_userinfo import common

HANDLE_URL = '/userinfo-support/v1/get_products_by_buid'
BUID_1 = 'cfac4fc7-21e8-46ae-8cfe-627a67b569d1'
BUID_2 = 'cfac4fc7-21e8-46ae-8cfe-627a67b569d2'
BUID_3 = 'cfac4fc7-21e8-46ae-8cfe-627a67b569d3'
BUID_4 = 'cfac4fc7-21e8-46ae-8cfe-627a67b569d4'


async def test_get_products_no_buid(
        taxi_bank_userinfo, mockserver, access_control_mock,
):
    response = await taxi_bank_userinfo.post(
        HANDLE_URL, headers=common.get_support_headers(), json={},
    )
    assert response.status_code == 400


async def test_get_products_access_deny(
        taxi_bank_userinfo, mockserver, access_control_mock,
):
    response = await taxi_bank_userinfo.post(
        HANDLE_URL,
        headers=common.get_support_headers(''),
        json={'buid': BUID_1},
    )
    assert response.status_code == 401
    assert access_control_mock.apply_policies_handler.times_called == 1


async def test_get_products_zero_products(
        taxi_bank_userinfo, mockserver, access_control_mock, pgsql,
):
    response = await taxi_bank_userinfo.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={'buid': BUID_4},
    )
    assert response.status_code == 200
    assert response.json() == {'products': []}
    assert access_control_mock.handler_path == HANDLE_URL


async def test_get_products_ok_two_product_and_one_deleted(
        taxi_bank_userinfo, mockserver, access_control_mock, pgsql,
):
    response = await taxi_bank_userinfo.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={'buid': BUID_1},
    )
    assert response.status_code == 200
    assert response.json() == {
        'products': [
            {'agreement_id': 'agreement_1', 'name': 'PRO'},
            {'agreement_id': 'agreement_2', 'name': 'WALLET'},
        ],
    }
    assert access_control_mock.handler_path == HANDLE_URL


async def test_get_products_ok_one_product(
        taxi_bank_userinfo, mockserver, access_control_mock, pgsql,
):
    response = await taxi_bank_userinfo.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={'buid': BUID_2},
    )
    assert response.status_code == 200
    assert response.json() == {
        'products': [{'agreement_id': 'agreement_4', 'name': 'WALLET'}],
    }
    assert access_control_mock.handler_path == HANDLE_URL


async def test_get_products_ok_one_deleted_product(
        taxi_bank_userinfo, mockserver, access_control_mock, pgsql,
):
    response = await taxi_bank_userinfo.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={'buid': BUID_3},
    )
    assert response.status_code == 200
    assert response.json() == {'products': []}
    assert access_control_mock.handler_path == HANDLE_URL
