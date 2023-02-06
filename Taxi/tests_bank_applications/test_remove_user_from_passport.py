from tests_bank_applications import common


def default_headers():
    return {'X-Remote-IP': '127.0.0.1'}


async def test_remove_user_from_passport_no_buid(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        bank_userinfo_mock,
        bank_forms_mock,
        taxi_processing_mock,
        passport_internal_mock,
        pgsql,
):
    response = await taxi_bank_applications.post(
        'applications-internal/v1/delete_passport_bank_phone',
        headers=default_headers(),
        json={'buid': ''},
    )
    assert response.status == 400


async def test_remove_user_from_passport_unknown_user(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        bank_userinfo_mock,
        bank_forms_mock,
        taxi_processing_mock,
        passport_internal_mock,
        pgsql,
):
    response = await taxi_bank_applications.post(
        'applications-internal/v1/delete_passport_bank_phone',
        headers=default_headers(),
        json={'buid': '44444444-d4d1-43c1-aadb-cabd06674ea6'},  # wrong_phone
    )
    assert response.status == 400
    assert response.json()['message'] == 'Failed to get phone number'


async def test_remove_user_from_passport_no_passport_phone(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        bank_userinfo_mock,
        bank_forms_mock,
        taxi_processing_mock,
        passport_internal_mock,
        pgsql,
):
    response = await taxi_bank_applications.post(
        'applications-internal/v1/delete_passport_bank_phone',
        headers=default_headers(),
        json={
            'buid': '33333333-d4d1-43c1-aadb-cabd06674ea6',
        },  # no_passport_phone
    )
    assert response.status == 200
    assert response.json()['errors'] == ['alias.not_found']
    assert response.json()['status'] == 'FAILED'


async def test_remove_user_from_passport_no_sid(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        bank_userinfo_mock,
        bank_forms_mock,
        taxi_processing_mock,
        passport_internal_mock,
        pgsql,
):
    response = await taxi_bank_applications.post(
        'applications-internal/v1/delete_passport_bank_phone',
        headers=default_headers(),
        json={
            'buid': '22222222-d4d1-43c1-aadb-cabd06674ea6',
        },  # no_sid_phone_buid
    )
    assert response.status == 200
    assert response.json()['errors'] == [
        'RemoveSidFromPassport error: '
        'DELETE /1/account/yandex_uid/subscription/bank/, status code 404',
    ]
    assert response.json()['status'] == 'FAILED'


async def test_remove_user_from_passport(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        bank_userinfo_mock,
        bank_forms_mock,
        taxi_processing_mock,
        passport_internal_mock,
        pgsql,
):
    response = await taxi_bank_applications.post(
        'applications-internal/v1/delete_passport_bank_phone',
        headers=common.default_headers(),
        json={
            'buid': '67754336-d4d1-43c1-aadb-cabd06674ea6',
            'uid': '111111111',
        },
    )
    assert response.status == 200
    assert response.json()['status'] == 'SUCCESS'
