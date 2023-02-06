import pytest

from tests_bank_userinfo import utils
from tests_bank_userinfo import common

BUID = 'cfac4fc7-21e8-46ae-8cfe-627a67b569d2'
AGREEMENT_ID = 'agreement'
AGREEMENT_ID_2 = 'agreement2'
PRODUCT = 'NEW'
REASON = 'some_reason'


def select_products_by_buid(pgsql, buid):
    sql = """
            SELECT * 
            FROM bank_userinfo.user_products
            WHERE buid = %s
        """
    cursor = pgsql['bank_userinfo'].cursor()
    cursor.execute(sql, [buid])
    records = cursor.fetchall()
    return records


def insert_product(pgsql, buid, product, agreement_id):
    sql = """
            INSERT INTO bank_userinfo.user_products (
                buid,
                product,
                agreement_id
            ) VALUES (
                %s,
                %s,
                %s
            );
        """
    cursor = pgsql['bank_userinfo'].cursor()
    cursor.execute(sql, [buid, product, agreement_id])


async def test_support_add_new_product_empty_buid(
        taxi_bank_userinfo, mockserver, access_control_mock,
):
    response = await taxi_bank_userinfo.post(
        '/userinfo-support/v1/add_new_product',
        headers=common.get_support_headers(),
        json={
            'buid': '',
            'reason': REASON,
            'product': PRODUCT,
            'agreement_id': AGREEMENT_ID,
        },
    )
    assert response.status == 400


async def test_support_add_new_product_empty_product(
        taxi_bank_userinfo, mockserver, access_control_mock,
):
    response = await taxi_bank_userinfo.post(
        '/userinfo-support/v1/add_new_product',
        headers=common.get_support_headers(),
        json={
            'buid': BUID,
            'reason': REASON,
            'product': '',
            'agreement_id': AGREEMENT_ID,
        },
    )
    assert response.status == 400


async def test_support_add_new_product_invalid_buid(
        taxi_bank_userinfo, mockserver, access_control_mock,
):
    response = await taxi_bank_userinfo.post(
        '/userinfo-support/v1/add_new_product',
        headers=common.get_support_headers(),
        json={
            'buid': 'wrong-format',
            'reason': REASON,
            'product': '',
            'agreement_id': AGREEMENT_ID,
        },
    )
    assert response.status == 400


async def test_support_add_new_product_no_product(
        taxi_bank_userinfo, mockserver, access_control_mock,
):
    response = await taxi_bank_userinfo.post(
        '/userinfo-support/v1/add_new_product',
        headers=common.get_support_headers(),
        json={'buid': BUID, 'agreement_id': AGREEMENT_ID, 'reason': REASON},
    )
    assert response.status == 400


async def test_support_add_new_product_ok_new(
        taxi_bank_userinfo, mockserver, access_control_mock, pgsql,
):
    response = await taxi_bank_userinfo.post(
        '/userinfo-support/v1/add_new_product',
        headers=common.get_support_headers(),
        json={
            'buid': BUID,
            'reason': REASON,
            'product': PRODUCT,
            'agreement_id': AGREEMENT_ID,
        },
    )
    assert response.status == 200

    pg_result = select_products_by_buid(pgsql, BUID)
    assert pg_result[0][1] == BUID
    assert pg_result[0][2] == PRODUCT
    assert pg_result[0][5] == AGREEMENT_ID
    assert pg_result[0][6] == REASON
    assert pg_result[0][7] == {
        'initiator_id': 'support_login',
        'initiator_type': 'SUPPORT',
    }


async def test_support_add_new_product_with_same_agreement_id(
        taxi_bank_userinfo, mockserver, access_control_mock, pgsql,
):
    response = await taxi_bank_userinfo.post(
        '/userinfo-support/v1/add_new_product',
        headers=common.get_support_headers(),
        json={
            'buid': BUID,
            'reason': REASON,
            'product': PRODUCT,
            'agreement_id': AGREEMENT_ID,
        },
    )
    assert response.status == 200

    pg_result = select_products_by_buid(pgsql, BUID)
    assert len(pg_result) == 1
    assert pg_result[0][1] == BUID
    assert pg_result[0][2] == PRODUCT
    assert pg_result[0][5] == AGREEMENT_ID
    assert pg_result[0][6] == REASON
    assert pg_result[0][7] == {
        'initiator_id': 'support_login',
        'initiator_type': 'SUPPORT',
    }

    response = await taxi_bank_userinfo.post(
        '/userinfo-support/v1/add_new_product',
        headers=common.get_support_headers(),
        json={
            'buid': BUID,
            'reason': REASON,
            'product': PRODUCT,
            'agreement_id': AGREEMENT_ID,
        },
    )
    assert response.status == 200

    pg_result = select_products_by_buid(pgsql, BUID)
    assert len(pg_result) == 1
    assert pg_result[0][1] == BUID
    assert pg_result[0][2] == PRODUCT
    assert pg_result[0][5] == AGREEMENT_ID
    assert pg_result[0][6] == REASON
    assert pg_result[0][7] == {
        'initiator_id': 'support_login',
        'initiator_type': 'SUPPORT',
    }


async def test_support_add_new_product_with_another_agreement_id(
        taxi_bank_userinfo, mockserver, access_control_mock, pgsql,
):
    response = await taxi_bank_userinfo.post(
        '/userinfo-support/v1/add_new_product',
        headers=common.get_support_headers(),
        json={
            'buid': BUID,
            'reason': REASON,
            'product': PRODUCT,
            'agreement_id': AGREEMENT_ID,
        },
    )
    assert response.status == 200

    pg_result = select_products_by_buid(pgsql, BUID)
    assert len(pg_result) == 1
    assert pg_result[0][1] == BUID
    assert pg_result[0][2] == PRODUCT
    assert pg_result[0][5] == AGREEMENT_ID
    assert pg_result[0][6] == REASON
    assert pg_result[0][7] == {
        'initiator_id': 'support_login',
        'initiator_type': 'SUPPORT',
    }

    response = await taxi_bank_userinfo.post(
        '/userinfo-support/v1/add_new_product',
        headers=common.get_support_headers(),
        json={
            'buid': BUID,
            'reason': REASON,
            'product': PRODUCT,
            'agreement_id': AGREEMENT_ID_2,
        },
    )
    assert response.status == 200

    pg_result = select_products_by_buid(pgsql, BUID)
    assert len(pg_result) == 2


async def test_support_add_new_product_race(
        taxi_bank_userinfo, mockserver, access_control_mock, pgsql, testpoint,
):
    @testpoint('insert conflict')
    def _insert_same_product(data):
        insert_product(pgsql, BUID, PRODUCT, AGREEMENT_ID)

    response = await taxi_bank_userinfo.post(
        '/userinfo-support/v1/add_new_product',
        headers=common.get_support_headers(),
        json={
            'buid': BUID,
            'reason': REASON,
            'product': PRODUCT,
            'agreement_id': AGREEMENT_ID,
        },
    )
    assert response.status == 500
