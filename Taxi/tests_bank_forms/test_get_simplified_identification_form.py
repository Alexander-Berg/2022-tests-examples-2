# flake8: noqa
# pylint: disable=import-error,wildcard-import
from bank_forms_plugins.generated_tests import *


def get_headers():
    return {
        'X-Yandex-BUID': '563ae42c-2e92-4b37-b3e0-424a656fd7b4',
        'X-Yandex-UID': '1234',
        'X-YaBank-SessionUUID': 'session_uuid1',
        'X-YaBank-PhoneID': 'phone_id1',
        'X-Remote-IP': '127.0.0.1',
        'X-Ya-User-Ticket': 'user_ticket',
    }


def get_default_response():
    return get_headers()['X-Yandex-BUID'], 'Петров', 'Пётр', '2000-07-02'


def insert_form(pgsql, bank_uid, surname, name, date_of_birth):
    cursor = pgsql['bank_forms'].cursor()

    cursor.execute(
        'INSERT INTO bank_forms.simplified_identification '
        '(bank_uid, last_name, first_name, birthday) '
        f'VALUES (\'{bank_uid}\', \'{surname}\', '
        f'\'{name}\', \'{date_of_birth}\')',
    )


def select_forms(pgsql, bank_uid):
    cursor = pgsql['bank_forms'].cursor()
    cursor.execute(
        (
            'SELECT form_id, bank_uid, last_name, first_name, birthday '
            'FROM bank_forms.simplified_identification '
            f'WHERE bank_uid = \'{bank_uid}\''
        ),
    )
    return list(cursor)


async def test_get_after_set_simplified_identification_form(
        taxi_bank_forms, pgsql, blackbox_mock,
):
    headers = get_headers()
    insert_form(pgsql, *(get_default_response()))

    pg_result = select_forms(pgsql, headers['X-Yandex-BUID'])
    assert len(pg_result) == 1
    assert pg_result[0] == (4, *(get_default_response()[:4]))

    response = await taxi_bank_forms.post(
        '/forms-internal/v1/get_simplified_identification_form',
        headers=headers,
    )
    assert response.status_code == 200
    assert not blackbox_mock.blackbox_handler.has_calls

    assert response.json() == {
        'last_name': get_default_response()[1],
        'first_name': get_default_response()[2],
        'birthday': get_default_response()[3],
    }


async def test_get_unset_simplified_identification_form(
        taxi_bank_forms, pgsql, blackbox_mock,
):
    headers = get_headers()

    response = await taxi_bank_forms.post(
        '/forms-internal/v1/get_simplified_identification_form',
        headers=headers,
    )
    assert response.status_code == 200
    assert blackbox_mock.blackbox_handler.has_calls

    assert response.json() == {
        'last_name': get_default_response()[1],
        'first_name': get_default_response()[2],
        'birthday': get_default_response()[3],
    }
    pg_result = select_forms(pgsql, headers['X-Yandex-BUID'])
    assert len(pg_result) == 1


async def test_get_unset_simplified_identification_form_not_full_info(
        taxi_bank_forms, pgsql, blackbox_mock,
):
    headers = get_headers()
    headers['X-Yandex-UID'] = '1235'

    response = await taxi_bank_forms.post(
        '/forms-internal/v1/get_simplified_identification_form',
        headers=headers,
    )
    assert response.status_code == 200
    assert blackbox_mock.blackbox_handler.has_calls

    assert response.json() == {
        'last_name': get_default_response()[1],
        'first_name': get_default_response()[2],
    }
    pg_result = select_forms(pgsql, headers['X-Yandex-BUID'])
    assert len(pg_result) == 1


async def test_get_unset_simplified_identification_form_not_found(
        taxi_bank_forms, pgsql, blackbox_mock,
):
    headers = get_headers()
    headers['X-Yandex-UID'] = '123'

    response = await taxi_bank_forms.post(
        '/forms-internal/v1/get_simplified_identification_form',
        headers=headers,
    )
    assert response.status_code == 200
    assert blackbox_mock.blackbox_handler.has_calls

    assert response.json() == {}
    pg_result = select_forms(pgsql, headers['X-Yandex-BUID'])
    assert not pg_result
