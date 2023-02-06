import pytest

from tests_bank_applications import common


@pytest.mark.parametrize('fail_procaas_times', [0, 1, 2])
async def test_create_loan_registration_happy_path(
        taxi_bank_applications,
        mockserver,
        bank_userinfo_mock,
        taxi_processing_mock,
        fail_procaas_times,
):
    bank_userinfo_mock.buid_status = 'NEW'
    bank_userinfo_mock.phone_id = None

    for iter in range(fail_procaas_times + 1):
        expect_fail = iter < fail_procaas_times
        status_code = 500 if expect_fail else 200
        taxi_processing_mock.set_http_status_code(status_code)
        assert taxi_processing_mock.payloads == []
        response = await taxi_bank_applications.post(
            'applications-internal/v1/loan_registration/create_application',
            {
                'buid': common.DEFAULT_YANDEX_BUID,
                'phone': common.DEFAULT_PHONE,
            },
            headers={'X-Idempotency-Token': common.DEFAULT_IDEMPOTENCY_TOKEN},
        )
        assert response.status_code == status_code
        json = response.json()
        if expect_fail:
            assert json == {'code': '500', 'message': 'Internal Server Error'}
            assert [pl[1] for pl in taxi_processing_mock.payloads] == [
                # some retries
                {'kind': 'init', 'type': 'LOAN_REGISTRATION'},
                {'kind': 'init', 'type': 'LOAN_REGISTRATION'},
                {'kind': 'init', 'type': 'LOAN_REGISTRATION'},
            ]
        else:
            application_id = json['application_id']
            assert json == {'application_id': application_id}
            assert [pl[1] for pl in taxi_processing_mock.payloads] == [
                {'kind': 'init', 'type': 'LOAN_REGISTRATION'},
                {
                    'kind': 'update',
                    'type': 'LOAN_REGISTRATION',
                    'buid': common.DEFAULT_YANDEX_BUID,
                    'yuid': common.DEFAULT_YANDEX_UID,
                },
            ]
        taxi_processing_mock.payloads = []
        # TODO(a-sumin): also check db state

    response = await taxi_bank_applications.post(
        'applications-internal/v1/get_application_data',
        {'application_id': application_id},
    )
    assert response.status_code == 200
    assert response.json() == {'form': {'phone': common.DEFAULT_PHONE}}

    bank_userinfo_mock.buid_status = 'PHONE_CONFIRMED'
    bank_userinfo_mock.phone_id = common.DEFAULT_PHONE

    response = await taxi_bank_applications.post(
        'applications-internal/v1/get_application_status',
        {'application_id': application_id},
    )
    assert response.status_code == 200
    assert response.json() == {'status': common.STATUS_PROCESSING}

    response = await taxi_bank_applications.post(
        'applications-internal/v1/set_application_status',
        {'application_id': application_id, 'status': common.STATUS_SUCCESS},
    )
    assert response.status_code == 200
    assert response.text == ''

    response = await taxi_bank_applications.post(
        'applications-internal/v1/get_application_status',
        {'application_id': application_id},
    )
    assert response.status_code == 200
    assert response.json() == {'status': common.STATUS_SUCCESS}
