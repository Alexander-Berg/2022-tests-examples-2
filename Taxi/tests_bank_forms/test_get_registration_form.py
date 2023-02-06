# flake8: noqa
# pylint: disable=import-error,wildcard-import
from bank_forms_plugins.generated_tests import *


def get_headers():
    return {
        'X-Yandex-UID': '1234',
        'X-YaBank-SessionUUID': 'session_uuid1',
        'X-YaBank-PhoneID': 'phone_id1',
        'X-Remote-IP': '127.0.0.1',
    }


def get_default_response():
    return (get_headers()['X-Yandex-UID'], '+79999999999', '+7999*****99', '1')


def insert_form(pgsql, yandex_uid, phone):
    cursor = pgsql['bank_forms'].cursor()
    query = (
        'INSERT INTO bank_forms.registration '
        '(yandex_uid, phone) '
        f'VALUES (\'{yandex_uid}\', \'{phone}\')'
    )
    cursor.execute(query)


def select_forms(pgsql, yandex_uid):
    cursor = pgsql['bank_forms'].cursor()
    cursor.execute(
        (
            'SELECT form_id, yandex_uid, phone, masked_phone '
            'FROM bank_forms.registration '
            f'WHERE yandex_uid = \'{yandex_uid}\''
        ),
    )
    return list(cursor)


async def test_get_after_set_registration_form(
        taxi_bank_forms, pgsql, blackbox_mock,
):
    headers = get_headers()
    insert_form(pgsql, *(get_default_response()[:2]))

    pg_result = select_forms(pgsql, headers['X-Yandex-UID'])
    assert len(pg_result) == 1
    assert pg_result[0] == (4, *(get_default_response()[:2]), None)

    response = await taxi_bank_forms.post(
        '/forms-internal/v1/get_registration_form', headers=headers,
    )
    assert response.status_code == 200
    assert not blackbox_mock.blackbox_handler.has_calls

    assert response.json() == {'phone': get_default_response()[1]}


async def test_get_unset_registration_form_has_secured_phone(
        taxi_bank_forms, pgsql, blackbox_mock,
):
    headers = get_headers()

    response = await taxi_bank_forms.post(
        '/forms-internal/v1/get_registration_form', headers=headers,
    )
    assert response.status_code == 200
    assert blackbox_mock.blackbox_handler.has_calls

    assert response.json() == {
        'phone': get_default_response()[1],
        'masked_phone': get_default_response()[2],
        'passport_phone_id': get_default_response()[3],
    }
    pg_result = select_forms(pgsql, headers['X-Yandex-UID'])
    assert len(pg_result) == 1


async def test_get_unset_registration_form_by_confirmed_phone(
        taxi_bank_forms, pgsql, blackbox_mock,
):
    headers = get_headers()
    headers['X-Yandex-UID'] = '1233'

    response = await taxi_bank_forms.post(
        '/forms-internal/v1/get_registration_form', headers=headers,
    )
    assert response.status_code == 200
    assert blackbox_mock.blackbox_handler.has_calls

    assert response.json() == {
        'phone': '+79999999990',
        'masked_phone': '+7999*****90',
        'passport_phone_id': '2',
    }
    pg_result = select_forms(pgsql, headers['X-Yandex-UID'])
    assert len(pg_result) == 1


async def test_get_unset_registration_form_not_full_info(
        taxi_bank_forms, pgsql, blackbox_mock,
):
    headers = get_headers()
    headers['X-Yandex-UID'] = '1235'

    response = await taxi_bank_forms.post(
        '/forms-internal/v1/get_registration_form', headers=headers,
    )
    assert response.status_code == 200
    assert blackbox_mock.blackbox_handler.has_calls

    assert response.json() == {
        'phone': get_default_response()[1],
        'passport_phone_id': get_default_response()[3],
    }
    pg_result = select_forms(pgsql, headers['X-Yandex-UID'])
    assert len(pg_result) == 1


async def test_get_unset_registration_form_no_confirmed_phone(
        taxi_bank_forms, pgsql, blackbox_mock,
):
    headers = get_headers()
    headers['X-Yandex-UID'] = '1236'

    response = await taxi_bank_forms.post(
        '/forms-internal/v1/get_registration_form', headers=headers,
    )
    assert response.status_code == 200
    assert blackbox_mock.blackbox_handler.has_calls

    assert response.json() == {}
    pg_result = select_forms(pgsql, headers['X-Yandex-UID'])
    assert not pg_result


async def test_get_unset_registration_form_not_found(
        taxi_bank_forms, pgsql, blackbox_mock,
):
    headers = get_headers()
    headers['X-Yandex-UID'] = '123'

    response = await taxi_bank_forms.post(
        '/forms-internal/v1/get_registration_form', headers=headers,
    )
    assert response.status_code == 200
    assert blackbox_mock.blackbox_handler.has_calls

    assert response.json() == {}
    pg_result = select_forms(pgsql, headers['X-Yandex-UID'])
    assert not pg_result
