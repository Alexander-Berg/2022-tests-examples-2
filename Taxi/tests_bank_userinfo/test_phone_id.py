def select_phone(pgsql, phone_id):
    cursor = pgsql['bank_userinfo'].cursor()
    cursor.execute(
        (
            f'SELECT phone '
            f'FROM bank_userinfo.phones '
            f'WHERE phone_id = \'{phone_id}\''
        ),
    )
    return list(cursor)


async def test_nonexistent_phone(taxi_bank_userinfo, mockserver, pgsql):
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/get_phone_id', json={'phone': '+79111111112'},
    )
    resp = response.json()
    phone_id = resp.pop('phone_id')
    assert len(phone_id) > 1

    pg_result = select_phone(pgsql, phone_id)
    db_phone = pg_result[0]

    assert db_phone == ('+79111111112',)
