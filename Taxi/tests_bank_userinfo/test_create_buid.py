import pytest

from tests_bank_userinfo import utils


def select_buid_by_uid(pgsql, uid):
    cursor = pgsql['bank_userinfo'].cursor()
    cursor.execute(
        (
            f'SELECT yandex_uid, phone_id, bank_uid, status, operation_type '
            f'FROM bank_userinfo.buids '
            f'WHERE yandex_uid = \'{uid}\''
        ),
    )
    return list(cursor)


async def test_create_buid_empty_uid(taxi_bank_userinfo, mockserver):
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/create_buid', json={'uid': ''},
    )
    assert response.status == 400


@pytest.mark.parametrize(
    'uid,buid,status,phone_id',
    [
        (
            '111111',
            'de334bd1-1dcf-49c6-9e25-eb9228828cd6',
            'NOT_NEW_TEST_STATUS',
            'phone_id_1',
        ),
        (
            '111112',
            'cfac4fc7-21e8-46ae-8cfe-627a67b569d2',
            'NEW',
            'phone_id_2',
        ),
        (
            '111113',
            '15aa5d3b-b849-40bd-9ddd-efccabcea24e',
            'NOT_NEW_TEST_STATUS',
            None,
        ),
        ('111114', 'eec3d97f-a6d0-4047-b2a0-cdb64a5fc855', 'NEW', None),
    ],
)
async def test_create_buid_existing_new(
        taxi_bank_userinfo, mockserver, uid, buid, status, phone_id, pgsql,
):
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/create_buid', json={'uid': uid},
    )
    assert response.status == 200
    resp = response.json()
    assert resp['buid'] == buid

    pg_result = select_buid_by_uid(pgsql, uid)
    assert pg_result == [(uid, phone_id, buid, status, 'INSERT')]


@pytest.mark.parametrize('uid', ['111115'])
async def test_create_buid_ok(taxi_bank_userinfo, mockserver, uid, pgsql):
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/create_buid', json={'uid': uid},
    )
    assert response.status == 200
    resp = response.json()
    buid = resp.pop('buid')

    pg_result = select_buid_by_uid(pgsql, uid)
    assert pg_result == [(uid, None, buid, 'NEW', 'INSERT')]

    buid_history = utils.select_buid_history(pgsql, buid)
    assert len(buid_history) == 1
    assert buid_history[0]['operation_type'] == 'INSERT'
