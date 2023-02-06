import pytest

from tests_bank_userinfo import utils

SINGLE_BUID = 'cfac4fc7-21e8-46ae-8cfe-627a67b569d2'


def select_buid_by_buid(pgsql, buid):
    cursor = pgsql['bank_userinfo'].cursor()
    cursor.execute(
        (
            f'SELECT yandex_uid, phone_id, bank_uid, status, operation_type '
            f'FROM bank_userinfo.buids '
            f'WHERE bank_uid = \'{buid}\''
        ),
    )
    return list(cursor)


async def test_update_buid_status_empty_buid(taxi_bank_userinfo, mockserver):
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/update_buid_status',
        json={'buid': '', 'status': 'NEW'},
    )
    assert response.status == 400


async def test_update_buid_status_invalid_status(
        taxi_bank_userinfo, mockserver,
):
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/update_buid_status',
        json={
            'buid': 'de334bd1-1dcf-49c6-9e25-eb9228828cd6',
            'status': 'INVALID_TEST_STATUS',
        },
    )
    assert response.status == 400


async def test_update_buid_status_not_found(taxi_bank_userinfo, mockserver):
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/update_buid_status',
        json={'buid': 'de334bd1-1dcf-49c6-9e25-eb9228828cd9', 'status': 'NEW'},
    )
    assert response.status == 404


async def test_update_buid_status_new_with_phone_id(
        taxi_bank_userinfo, mockserver,
):
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/update_buid_status',
        json={'buid': 'de334bd1-1dcf-49c6-9e25-eb9228828cd6', 'status': 'NEW'},
    )
    assert response.status == 409


@pytest.mark.parametrize(
    'buid,status',
    [
        ('15aa5d3b-b849-40bd-9ddd-efccabcea24e', 'FINAL'),
        ('eec3d97f-a6d0-4047-b2a0-cdb64a5fc855', 'PHONE_CONFIRMED'),
    ],
)
async def test_update_buid_status_no_phone_id(
        taxi_bank_userinfo, mockserver, buid, status,
):
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/update_buid_status',
        json={'buid': buid, 'status': status},
    )
    assert response.status == 409


async def test_invalid_buid(taxi_bank_userinfo, mockserver):
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/update_buid_status',
        json={'buid': 'wrong-format', 'status': 'NEW'},
    )
    assert response.status == 400


async def test_update_buid_status_ok_new(
        taxi_bank_userinfo, mockserver, pgsql,
):
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/update_buid_status',
        json={'buid': 'eec3d97f-a6d0-4047-b2a0-cdb64a5fc855', 'status': 'NEW'},
    )
    assert response.status == 200

    pg_result = select_buid_by_buid(
        pgsql, 'eec3d97f-a6d0-4047-b2a0-cdb64a5fc855',
    )
    assert pg_result == [
        (
            '111114',
            None,
            'eec3d97f-a6d0-4047-b2a0-cdb64a5fc855',
            'NEW',
            'UPDATE',
        ),
    ]


async def test_update_buid_status_ok(taxi_bank_userinfo, mockserver, pgsql):
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/update_buid_status',
        json={'buid': SINGLE_BUID, 'status': 'PHONE_CONFIRMED'},
    )
    assert response.status == 200

    pg_result = select_buid_by_buid(pgsql, SINGLE_BUID)
    assert pg_result == [
        ('111112', 'phone_id_2', SINGLE_BUID, 'PHONE_CONFIRMED', 'UPDATE'),
    ]

    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/update_buid_status',
        json={'buid': SINGLE_BUID, 'status': 'FINAL'},
    )
    assert response.status == 200

    pg_result = select_buid_by_buid(pgsql, SINGLE_BUID)
    assert pg_result == [
        ('111112', 'phone_id_2', SINGLE_BUID, 'FINAL', 'UPDATE'),
    ]

    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/update_buid_status',
        json={'buid': SINGLE_BUID, 'status': 'CHANGING_PHONE'},
    )
    assert response.status == 200

    pg_result = select_buid_by_buid(pgsql, SINGLE_BUID)
    assert pg_result == [
        ('111112', 'phone_id_2', SINGLE_BUID, 'CHANGING_PHONE', 'UPDATE'),
    ]

    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/update_buid_status',
        json={'buid': SINGLE_BUID, 'status': 'FINAL'},
    )
    assert response.status == 200

    pg_result = select_buid_by_buid(pgsql, SINGLE_BUID)
    assert pg_result == [
        ('111112', 'phone_id_2', SINGLE_BUID, 'FINAL', 'UPDATE'),
    ]


@pytest.mark.parametrize(
    'buid',
    [
        'de334bd1-1dcf-49c6-9e25-eb9228828cd6',
        '15aa5d3b-b849-40bd-9ddd-efccabcea24e',
        'eec3d97f-a6d0-4047-b2a0-cdb64a5fc855',
    ],
)
async def test_update_buid_status_changing_fail(
        taxi_bank_userinfo, mockserver, pgsql, buid,
):
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/update_buid_status',
        json={'buid': buid, 'status': 'CHANGING_PHONE'},
    )
    assert response.status == 409


@pytest.mark.parametrize(
    'buid,status',
    [
        ('cfac4fc7-21e8-46ae-8cfe-627a67b569d2', 'NEW'),
        ('15aa5d3b-b849-40bd-9ddd-efccabcea24e', 'PHONE_CONFIRMED'),
        ('eec3d97f-a6d0-4047-b2a0-cdb64a5fc855', 'FINAL'),
        ('eec3d97f-a6d0-4047-b2a0-cdb64a5fc866', 'CHANGING_PHONE'),
    ],
)
async def test_update_buid_nothing_changed(
        taxi_bank_userinfo, mockserver, buid, status, pgsql,
):
    pg_result = select_buid_by_buid(pgsql, buid)
    pg_status = pg_result[0][3]
    assert status == pg_status

    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/update_buid_status',
        json={'buid': buid, 'status': status},
    )
    assert response.status == 200

    pg_result_2 = select_buid_by_buid(pgsql, buid)
    assert pg_result == pg_result_2
    assert not utils.select_buid_history(pgsql, buid)
