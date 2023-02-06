def select_forms(pgsql, yandex_uid):
    cursor = pgsql['bank_forms'].cursor()
    cursor.execute(
        (
            'SELECT form_id, yandex_uid, phone '
            'FROM bank_forms.registration '
            f'WHERE yandex_uid = \'{yandex_uid}\''
        ),
    )
    return list(cursor)


def get_body():
    return {'phone': '+79999999999'}


YANDEX_UID = '1111'


def get_headers():
    return {
        'X-Yandex-UID': YANDEX_UID,
        'X-YaBank-SessionUUID': 'session_uuid1',
        'X-YaBank-PhoneID': 'phone_id1',
    }


def get_default_line():
    return YANDEX_UID, '+79999999999'


async def test_set_registration_form(taxi_bank_forms, pgsql):
    headers = get_headers()
    body = get_body()
    response = await taxi_bank_forms.post(
        '/v1/forms/v1/set_registration_form', json=body, headers=headers,
    )
    assert response.status_code == 200

    pg_result = select_forms(pgsql, YANDEX_UID)
    assert len(pg_result) == 1
    db_form = pg_result[0]

    assert db_form == (1, *get_default_line())


async def test_double_set_registration_form(taxi_bank_forms, pgsql):
    headers = get_headers()
    body = get_body()
    response = await taxi_bank_forms.post(
        '/v1/forms/v1/set_registration_form', json=body, headers=headers,
    )
    assert response.status_code == 200

    pg_result = select_forms(pgsql, YANDEX_UID)
    assert len(pg_result) == 1
    assert pg_result[0] == (1, *get_default_line())

    body['phone'] = '+79000000000'
    response = await taxi_bank_forms.post(
        '/v1/forms/v1/set_registration_form', json=body, headers=headers,
    )
    assert response.status_code == 200

    pg_result = select_forms(pgsql, YANDEX_UID)
    assert len(pg_result) == 2
    assert pg_result[0] == (1, *get_default_line())
    assert pg_result[1] == (2, YANDEX_UID, '+79000000000')


async def test_set_registration_form_empty_phone(taxi_bank_forms):
    headers = get_headers()
    body = get_body()
    body['phone'] = ''
    response = await taxi_bank_forms.post(
        '/v1/forms/v1/set_registration_form', json=body, headers=headers,
    )
    assert response.status_code == 200


async def test_set_registration_form_invalid_phone(taxi_bank_forms):
    headers = get_headers()
    body = get_body()
    body['phone'] = '+7123'
    response = await taxi_bank_forms.post(
        '/v1/forms/v1/set_registration_form', json=body, headers=headers,
    )
    assert response.status_code == 200


async def test_set_registration_form_no_phone(taxi_bank_forms):
    headers = get_headers()
    body = {}
    response = await taxi_bank_forms.post(
        '/v1/forms/v1/set_registration_form', json=body, headers=headers,
    )
    assert response.status_code == 200


async def test_set_registration_form_no_body(taxi_bank_forms):
    headers = get_headers()
    response = await taxi_bank_forms.post(
        '/v1/forms/v1/set_registration_form', headers=headers,
    )
    assert response.status_code == 400


async def test_set_registration_form_header_empty(taxi_bank_forms):
    headers = get_headers()
    headers['X-Yandex-UID'] = ''
    body = get_body()
    response = await taxi_bank_forms.post(
        '/v1/forms/v1/set_registration_form', json=body, headers=headers,
    )
    assert response.status_code == 500


async def test_set_registration_form_no_uid(taxi_bank_forms):
    body = get_body()
    response = await taxi_bank_forms.post(
        '/v1/forms/v1/set_registration_form', json=body,
    )
    assert response.status_code == 500
