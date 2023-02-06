import pytest

from tests_bank_applications import common

WRONG_TOKEN = (
    'eyJ0eXAiOiJKV1QiLCJhbGciOiJub25lIn0.eyJzdWIiOiJzdXBwb3J0LWFiYy11.'
)
MOCK_NOW = '2021-09-28T19:31:00+00:00'
REGISTRATION_CONFIG = {'response_with_masked_phone': True}
NEW_PHONE = '+79995556677'


def check_application(pgsql):
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(
        'SELECT * FROM bank_applications.change_phone_applications; ',
    )
    records = cursor.fetchall()
    # assert records == []
    assert len(records) == 1

    cursor.execute(
        'SELECT * FROM bank_applications.applications '
        'WHERE type = \'CHANGE_NUMBER\';',
    )
    records = cursor.fetchall()
    assert len(records) == 1


async def test_change_phone_create_application_ok(
        taxi_bank_applications, access_control_mock, bank_userinfo_mock, pgsql,
):
    # bank_forms_mock.set_http_status_code(200)
    headers = common.get_support_headers(token=common.SUPPORT_TOKEN)
    headers['X-Idempotency-Token'] = common.DEFAULT_IDEMPOTENCY_TOKEN
    response = await taxi_bank_applications.post(
        '/applications-support/v1/change_phone_number/create_application',
        headers=headers,
        json={
            'form': {
                'buid': common.DEFAULT_YANDEX_BUID,
                'new_phone': NEW_PHONE,
                'validation_type': 'REGULAR',
                'chatterbox_id': 'FTB-2115',
            },
        },
    )

    assert response.status_code == 200
    check_application(pgsql)
    assert access_control_mock.apply_policies_handler.times_called == 1
    assert bank_userinfo_mock.get_buid_info_handler.times_called == 2
    assert bank_userinfo_mock.get_phone_id_handler.times_called == 1


@pytest.mark.parametrize(
    'token, buid, phone, response_code',
    [
        (WRONG_TOKEN, common.DEFAULT_YANDEX_BUID, NEW_PHONE, 401),
        (common.SUPPORT_TOKEN, 'bad_buid', NEW_PHONE, 400),
        (
            common.SUPPORT_TOKEN,
            common.DEFAULT_YANDEX_BUID,
            common.DEFAULT_PHONE,
            409,
        ),
    ],
)
async def test_change_phone_create_application_problems(
        taxi_bank_applications,
        access_control_mock,
        bank_userinfo_mock,
        pgsql,
        token,
        buid,
        phone,
        response_code,
):
    # bank_forms_mock.set_http_status_code(200)
    headers = common.get_support_headers(token=token)
    headers['X-Idempotency-Token'] = common.DEFAULT_IDEMPOTENCY_TOKEN
    response = await taxi_bank_applications.post(
        '/applications-support/v1/change_phone_number/create_application',
        headers=headers,
        json={
            'form': {
                'buid': buid,
                'new_phone': phone,
                'validation_type': 'REGULAR',
                'chatterbox_id': 'FTB-2115',
            },
        },
    )

    assert response.status_code == response_code


async def test_change_phone_create_application_double_buid(
        taxi_bank_applications, access_control_mock, bank_userinfo_mock, pgsql,
):
    headers = common.get_support_headers(token=common.SUPPORT_TOKEN)
    headers['X-Idempotency-Token'] = common.DEFAULT_IDEMPOTENCY_TOKEN
    response = await taxi_bank_applications.post(
        '/applications-support/v1/change_phone_number/create_application',
        headers=headers,
        json={
            'form': {
                'buid': common.DEFAULT_YANDEX_BUID,
                'new_phone': NEW_PHONE,
                'validation_type': 'REGULAR',
                'chatterbox_id': 'FTB-2115',
            },
        },
    )

    assert response.status_code == 200
    application_id = response.json()['application_id']

    response = await taxi_bank_applications.post(
        '/applications-support/v1/change_phone_number/create_application',
        headers=headers,
        json={
            'form': {
                'buid': common.DEFAULT_YANDEX_BUID,
                'new_phone': NEW_PHONE,
                'validation_type': 'REGULAR',
                'chatterbox_id': 'FTB-2115',
            },
        },
    )
    assert response.status_code == 409

    response = await taxi_bank_applications.post(
        '/applications-support/v1/change_phone_number/close_application',
        headers=headers,
        json={'application_id': application_id},
    )
    assert response.status_code == 200

    response = await taxi_bank_applications.post(
        '/applications-support/v1/change_phone_number/create_application',
        headers=headers,
        json={
            'form': {
                'buid': common.DEFAULT_YANDEX_BUID,
                'new_phone': NEW_PHONE,
                'validation_type': 'REGULAR',
                'chatterbox_id': 'FTB-2115',
            },
        },
    )

    assert response.status_code == 200
