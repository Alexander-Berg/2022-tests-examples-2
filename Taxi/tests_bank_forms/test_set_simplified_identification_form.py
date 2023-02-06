def select_forms(pgsql, bank_uid):
    cursor = pgsql['bank_forms'].cursor()
    cursor.execute(
        (
            'SELECT form_id, bank_uid, last_name, first_name, middle_name, '
            'passport_number, birthday, inn_or_snils '
            'FROM bank_forms.simplified_identification '
            f'WHERE bank_uid = \'{bank_uid}\''
        ),
    )
    return list(cursor)


def get_body():
    return {
        'last_name': 'Петров',
        'first_name': 'Петр',
        'middle_name': 'Петрович',
        'passport_number': '6812000000',
        'birthday': '2000-07-02',
        'inn_or_snils': '19200000000',
    }


BUID = '1234'


def get_headers():
    return {
        'X-Yandex-BUID': BUID,
        'X-Yandex-UID': '1111',
        'X-YaBank-SessionUUID': 'session_uuid1',
        'X-YaBank-PhoneID': 'phone_id1',
        'X-Ya-User-Ticket': 'user_ticket',
    }


def get_default_line():
    return (
        BUID,
        'Петров',
        'Петр',
        'Петрович',
        '6812000000',
        '2000-07-02',
        '19200000000',
    )


async def test_set_simplified_identification_form(taxi_bank_forms, pgsql):
    headers = get_headers()
    body = get_body()
    response = await taxi_bank_forms.post(
        '/v1/forms/v1/set_simplified_identification_form',
        json=body,
        headers=headers,
    )
    assert response.status_code == 200

    pg_result = select_forms(pgsql, BUID)
    assert len(pg_result) == 1
    db_form = pg_result[0]

    assert db_form == (1, *get_default_line())


async def test_double_set_simplified_identification_form(
        taxi_bank_forms, pgsql,
):
    headers = get_headers()
    body = get_body()
    response = await taxi_bank_forms.post(
        '/v1/forms/v1/set_simplified_identification_form',
        json=body,
        headers=headers,
    )
    assert response.status_code == 200

    pg_result = select_forms(pgsql, BUID)
    assert len(pg_result) == 1
    assert pg_result[0] == (1, *get_default_line())

    body['last_name'] = 'Иванов'
    response = await taxi_bank_forms.post(
        '/v1/forms/v1/set_simplified_identification_form',
        json=body,
        headers=headers,
    )
    assert response.status_code == 200

    pg_result = select_forms(pgsql, BUID)
    assert len(pg_result) == 2
    assert pg_result[0] == (1, *get_default_line())
    assert pg_result[1] == (2, BUID, 'Иванов', *(get_default_line()[2:]))


async def test_set_simplified_identification_form_invalid_passport_number(
        taxi_bank_forms,
):
    headers = get_headers()
    body = get_body()
    body['passport_number'] = '1234'
    response = await taxi_bank_forms.post(
        '/v1/forms/v1/set_simplified_identification_form',
        json=body,
        headers=headers,
    )
    assert response.status_code == 200


async def test_set_simplified_identification_form_invalid_date_of_birth(
        taxi_bank_forms,
):
    headers = get_headers()
    body = get_body()
    body['birthday'] = '02-07-2000'
    response = await taxi_bank_forms.post(
        '/v1/forms/v1/set_simplified_identification_form',
        json=body,
        headers=headers,
    )
    assert response.status_code == 200


async def test_set_simplified_identification_form_invalid_inn(taxi_bank_forms):
    headers = get_headers()
    body = get_body()
    body['inn_or_snils'] = '1234'
    response = await taxi_bank_forms.post(
        '/v1/forms/v1/set_simplified_identification_form',
        json=body,
        headers=headers,
    )
    assert response.status_code == 200


async def test_set_simplified_identification_form_buid_empty(taxi_bank_forms):
    headers = get_headers()
    headers['X-Yandex-BUID'] = ''
    body = get_body()
    response = await taxi_bank_forms.post(
        '/v1/forms/v1/set_simplified_identification_form',
        json=body,
        headers=headers,
    )
    assert response.status_code == 500


async def test_set_simplified_identification_form_no_buid(taxi_bank_forms):
    body = get_body()
    response = await taxi_bank_forms.post(
        '/v1/forms/v1/set_simplified_identification_form', json=body,
    )
    assert response.status_code == 500
