import pytest

from tests_bank_userinfo import utils

CHANGING_PHONE_BUID = '8c9df3f9-1942-4899-1111-f31663f20733'


def select_phone_id_by_phone(pgsql, phone):
    cursor = pgsql['bank_userinfo'].cursor()
    cursor.execute(
        (
            f'SELECT phone_id '
            f'FROM bank_userinfo.phones '
            f'WHERE phone = \'{phone}\''
        ),
    )
    return list(cursor)


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


async def test_set_bank_phone_empty_buid(taxi_bank_userinfo, mockserver):
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/set_bank_phone',
        json={'buid': '', 'phone': '12345'},
    )
    assert response.status == 400


async def test_set_bank_phone_empty_phone(taxi_bank_userinfo, mockserver):
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/set_bank_phone',
        json={'buid': 'b7fcb9d5-19ee-4c2f-9cb1-67d3aa1f5971', 'phone': ''},
    )
    assert response.status == 400


async def test_invalid_buid(taxi_bank_userinfo, mockserver):
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/set_bank_phone',
        json={'buid': 'wrong-format', 'phone': '+79111111111'},
    )
    assert response.status == 400


async def test_set_bank_phone_phone_already_taken(
        taxi_bank_userinfo, mockserver,
):
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/set_bank_phone',
        json={
            'buid': 'b7fcb9d5-19ee-4c2f-9cb1-67d3aa1f5971',
            'phone': '+79111111111',
        },
    )
    assert response.status == 409


async def test_set_bank_phone_phone_already_taken_by_another_user(
        taxi_bank_userinfo, mockserver,
):
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/set_bank_phone',
        json={
            'buid': '41042ac5-8728-4511-8071-ba4b1e19968e',
            'phone': '+79111111118',
        },
    )
    assert response.status_code == 200

    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/set_bank_phone',
        json={
            'buid': '973db1db-2dea-424f-a55f-228a0c2c8002',
            'phone': '+79111111118',
        },
    )
    assert response.status == 409


async def test_set_bank_phone_buid_not_found(taxi_bank_userinfo, mockserver):
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/set_bank_phone',
        json={
            'buid': 'b7fcb9d4-19ee-4c2f-9cb1-67d3aa1f5971',
            'phone': '+7911111113',
        },
    )
    assert response.status == 404


@pytest.mark.parametrize(
    'phone, expected_status', [('+79111111120', 200), ('+79111111112', 409)],
)
async def test_set_bank_phone_changing(
        taxi_bank_userinfo, mockserver, phone, expected_status,
):
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/set_bank_phone',
        json={'buid': CHANGING_PHONE_BUID, 'phone': phone},
    )
    assert response.status == expected_status


@pytest.mark.parametrize(
    'phone,buid', [('+79111111112', '84e91c04-9279-4a07-a6d9-dd8369c82148')],
)
async def test_set_bank_phone_invalid_buid_status(
        taxi_bank_userinfo, mockserver, phone, buid,
):
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/set_bank_phone',
        json={'phone': phone, 'buid': buid},
    )
    assert response.status == 409


@pytest.mark.parametrize(
    'phone,buid', [('+79111111113', '84e91c04-9279-4a07-a6d9-dd8369c82148')],
)
async def test_set_bank_phone_ok_nothing_changed(
        taxi_bank_userinfo, mockserver, phone, buid, pgsql,
):
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/set_bank_phone',
        json={'phone': phone, 'buid': buid},
    )
    assert response.status == 200

    phone_id = select_phone_id_by_phone(pgsql, phone)[0][0]
    assert phone_id == 'c36e1046-7a22-4f9f-92cb-49b778b0860a'

    pg_result = select_buid_by_buid(pgsql, buid)
    assert pg_result == [
        ('111113', phone_id, buid, 'PHONE_CONFIRMED', 'INSERT'),
    ]


@pytest.mark.parametrize(
    'phone,buid', [('12345', 'a1fed95a-eaf7-4ca3-92b4-5f87655d7255')],
)
async def test_set_bank_phone_buid_match_invalid_status(
        taxi_bank_userinfo, mockserver, phone, buid,
):
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/set_bank_phone',
        json={'phone': phone, 'buid': buid},
    )
    assert response.status == 409


@pytest.mark.parametrize(
    'phone,buid', [('12345', '6c6f2aca-4507-4733-b3d4-9669fe8a4b23')],
)
async def test_set_bank_phone_phone_confirmed_without_phone(
        taxi_bank_userinfo, mockserver, phone, buid,
):
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/set_bank_phone',
        json={'phone': phone, 'buid': buid},
    )
    assert response.status == 500


@pytest.mark.parametrize(
    'phone,buid', [('+79111111110', '8c9df3f9-1942-4899-bf72-f31663f20733')],
)
async def test_set_bank_phone_buid_with_phone_new(
        taxi_bank_userinfo, mockserver, phone, buid,
):
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/set_bank_phone',
        json={'phone': phone, 'buid': buid},
    )
    assert response.status == 500


@pytest.mark.parametrize(
    'phone,buid', [('+79111111110', '84e91c04-9279-4a07-a6d9-dd8369c82148')],
)
async def test_set_bank_phone_buid_match_with_different_phone(
        taxi_bank_userinfo, mockserver, phone, buid,
):
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/set_bank_phone',
        json={'phone': phone, 'buid': buid},
    )
    assert response.status == 409


@pytest.mark.parametrize(
    'phone,buid', [('+79111111117', 'f1a69dcc-9b49-41df-84d2-7df5a64ad270')],
)
async def test_set_bank_phone_ok_old_phone_id(
        taxi_bank_userinfo, mockserver, phone, buid, pgsql,
):
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/set_bank_phone',
        json={'phone': phone, 'buid': buid},
    )
    assert response.status == 200

    pg_result = select_buid_by_buid(pgsql, buid)
    assert pg_result == [
        (
            '111117',
            'c34510c3-52b5-4a8c-bbce-0f73e21f45bc',
            buid,
            'PHONE_CONFIRMED',
            'UPDATE',
        ),
    ]


@pytest.mark.parametrize(
    'phone,buid', [('+79111111110', 'f1a69dcc-9b49-41df-84d2-7df5a64ad270')],
)
async def test_set_bank_phone_ok(
        taxi_bank_userinfo, mockserver, phone, buid, pgsql,
):
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/set_bank_phone',
        json={'phone': phone, 'buid': buid},
    )
    assert response.status == 200

    phone_id = select_phone_id_by_phone(pgsql, phone)[0][0]

    pg_result = select_buid_by_buid(pgsql, buid)
    assert pg_result == [
        (
            '111117',
            phone_id,
            'f1a69dcc-9b49-41df-84d2-7df5a64ad270',
            'PHONE_CONFIRMED',
            'UPDATE',
        ),
    ]

    buid_history = utils.select_buid_history(pgsql, buid)
    assert buid_history[0]['operation_type'] == 'UPDATE'
    assert buid_history[0]['phone_id'] == phone_id


async def test_set_bank_phone_data_race(
        taxi_bank_userinfo, mockserver, testpoint, pgsql,
):
    uuid = '973db1db-2dea-424f-a55f-111111111111'

    @testpoint('check status')
    async def _check_application_status(data):
        sql = """
                UPDATE bank_userinfo.buids SET
                    phone_id = %s,
                    status = 'PHONE_CONFIRMED'
                WHERE
                    bank_uid = %s and phone_id is NULL and status = 'NEW'
                RETURNING
                    bank_uid
              """
        cursor = pgsql['bank_userinfo'].cursor()
        cursor.execute(sql, [uuid, uuid])
        cursor.fetchall()

    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/set_bank_phone',
        json={'buid': uuid, 'phone': '+79111111118'},
    )
    assert response.status == 200
