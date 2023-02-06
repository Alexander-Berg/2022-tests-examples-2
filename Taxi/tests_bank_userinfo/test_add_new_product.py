import pytest

from tests_bank_userinfo import utils

BUID = 'cfac4fc7-21e8-46ae-8cfe-627a67b569d2'
AGREEMENT_ID = 'agreement'
AGREEMENT_ID_2 = 'agreement2'


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


async def test_add_new_product_empty_buid(taxi_bank_userinfo, mockserver):
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/add_new_product',
        json={'buid': '', 'product': 'NEW', 'agreement_id': AGREEMENT_ID},
    )
    assert response.status == 400


async def test_add_new_product_empty_product(taxi_bank_userinfo, mockserver):
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/add_new_product',
        json={'buid': BUID, 'product': '', 'agreement_id': AGREEMENT_ID},
    )
    assert response.status == 400


async def test_add_new_product_invalid_buid(taxi_bank_userinfo, mockserver):
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/add_new_product',
        json={
            'buid': 'wrong-format',
            'product': '',
            'agreement_id': AGREEMENT_ID,
        },
    )
    assert response.status == 400


async def test_add_new_product_no_product(taxi_bank_userinfo, mockserver):
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/add_new_product',
        json={'buid': BUID, 'agreement_id': AGREEMENT_ID},
    )
    assert response.status == 400


async def test_add_new_product_ok_new(taxi_bank_userinfo, mockserver, pgsql):
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/add_new_product',
        json={'buid': BUID, 'product': 'NEW', 'agreement_id': AGREEMENT_ID},
    )
    assert response.status == 200

    pg_result = select_products_by_buid(pgsql, BUID)
    assert pg_result[0][1] == BUID
    assert pg_result[0][2] == 'NEW'


async def test_add_new_product_with_same_agreement_id(
        taxi_bank_userinfo, mockserver, pgsql,
):
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/add_new_product',
        json={'buid': BUID, 'product': 'NEW', 'agreement_id': AGREEMENT_ID},
    )
    assert response.status == 200

    pg_result = select_products_by_buid(pgsql, BUID)
    assert len(pg_result) == 1
    assert pg_result[0][1] == BUID
    assert pg_result[0][2] == 'NEW'

    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/add_new_product',
        json={'buid': BUID, 'product': 'NEW', 'agreement_id': AGREEMENT_ID},
    )
    assert response.status == 200

    pg_result = select_products_by_buid(pgsql, BUID)
    assert len(pg_result) == 1
    assert pg_result[0][1] == BUID
    assert pg_result[0][2] == 'NEW'


async def test_add_new_product_with_another_agreement_id(
        taxi_bank_userinfo, mockserver, pgsql,
):
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/add_new_product',
        json={'buid': BUID, 'product': 'NEW', 'agreement_id': AGREEMENT_ID},
    )
    assert response.status == 200

    pg_result = select_products_by_buid(pgsql, BUID)
    assert len(pg_result) == 1
    assert pg_result[0][1] == BUID
    assert pg_result[0][2] == 'NEW'

    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/add_new_product',
        json={'buid': BUID, 'product': 'NEW', 'agreement_id': AGREEMENT_ID_2},
    )
    assert response.status == 200

    pg_result = select_products_by_buid(pgsql, BUID)
    assert len(pg_result) == 2


async def test_add_new_product_race(
        taxi_bank_userinfo, mockserver, pgsql, testpoint,
):
    @testpoint('insert conflict')
    def _insert_same_product(data):
        insert_product(pgsql, BUID, 'NEW', AGREEMENT_ID)

    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/add_new_product',
        json={'buid': BUID, 'product': 'NEW', 'agreement_id': AGREEMENT_ID},
    )
    assert response.status == 500
