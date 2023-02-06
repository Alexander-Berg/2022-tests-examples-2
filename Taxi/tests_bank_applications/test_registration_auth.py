from tests_bank_applications import common

MOCK_NOW = '2021-09-28T19:31:00+00:00'


async def test_create_unauth(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        bank_forms_mock,
        bank_userinfo_mock,
        taxi_processing_mock,
):
    for header in (
            'X-YaBank-SessionStatus',
            'X-Yandex-UID',
            'X-YaBank-SessionUUID',
    ):
        headers = common.headers_without_buid()
        headers.pop(header)

        response = await taxi_bank_applications.post(
            'v1/applications/v1/registration/create_application',
            headers=headers,
        )
        assert response.status_code == 401

        response = await taxi_bank_applications.post(
            'v1/applications/v1/create_application',
            json={'type': 'REGISTRATION'},
            headers=headers,
        )
        assert response.status_code == 401

        headers[header] = ''
        response = await taxi_bank_applications.post(
            'v1/applications/v1/registration/create_application',
            headers=headers,
        )
        assert response.status_code == 401

        response = await taxi_bank_applications.post(
            'v1/applications/v1/create_application',
            json={'type': 'REGISTRATION'},
            headers=headers,
        )
        assert response.status_code == 401


async def test_create_auth(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        bank_forms_mock,
        bank_userinfo_mock,
        taxi_processing_mock,
):
    headers = common.headers_without_buid()

    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/create_application', headers=headers,
    )
    assert response.status_code == 200

    response = await taxi_bank_applications.post(
        'v1/applications/v1/create_application',
        json={'type': 'REGISTRATION'},
        headers=headers,
    )
    assert response.status_code == 200

    headers['X-YaBank-SessionStatus'] = 'required_application_in_progress'

    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/create_application', headers=headers,
    )
    assert response.status_code == 200

    response = await taxi_bank_applications.post(
        'v1/applications/v1/create_application',
        json={'type': 'REGISTRATION'},
        headers=headers,
    )
    assert response.status_code == 200


async def test_status_unauth(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        bank_forms_mock,
        taxi_processing_mock,
        bank_userinfo_mock,
):
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/create_application',
        headers=common.headers_without_buid(),
    )

    assert response.status_code == 200
    application_id = response.json()['application_id']

    response = await taxi_bank_applications.post(
        'applications-internal/v1/set_application_status',
        json={'application_id': application_id, 'status': 'PROCESSING'},
    )
    assert response.status_code == 200

    for header in (
            'X-YaBank-SessionStatus',
            'X-Yandex-UID',
            'X-YaBank-SessionUUID',
    ):
        headers = common.headers_without_buid()
        headers.pop(header)
        response = await taxi_bank_applications.post(
            'v1/applications/v1/registration/get_application_status',
            headers=headers,
            json={'application_id': application_id},
        )
        assert response.status_code == 401

        response = await taxi_bank_applications.post(
            'v1/applications/v1/get_application_status',
            headers=headers,
            json={'application_id': application_id},
        )
        assert response.status_code == 401

        headers[header] = ''
        response = await taxi_bank_applications.post(
            'v1/applications/v1/registration/get_application_status',
            headers=headers,
            json={'application_id': application_id},
        )
        assert response.status_code == 401

        response = await taxi_bank_applications.post(
            'v1/applications/v1/get_application_status',
            headers=headers,
            json={'application_id': application_id},
        )
        assert response.status_code == 401


async def test_status_auth(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        bank_forms_mock,
        taxi_processing_mock,
        bank_userinfo_mock,
):
    headers = common.headers_without_buid()

    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/create_application', headers=headers,
    )

    assert response.status_code == 200
    application_id = response.json()['application_id']

    response = await taxi_bank_applications.post(
        'applications-internal/v1/set_application_status',
        json={'application_id': application_id, 'status': 'PROCESSING'},
    )
    assert response.status_code == 200

    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/get_application_status',
        headers=headers,
        json={'application_id': application_id},
    )
    assert response.status_code == 200

    response = await taxi_bank_applications.post(
        'v1/applications/v1/get_application_status',
        headers=headers,
        json={'application_id': application_id},
    )
    assert response.status_code == 200

    headers['X-YaBank-SessionStatus'] = 'required_application_in_progress'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/get_application_status',
        headers=headers,
        json={'application_id': application_id},
    )
    assert response.status_code == 200

    response = await taxi_bank_applications.post(
        'v1/applications/v1/get_application_status',
        headers=headers,
        json={'application_id': application_id},
    )
    assert response.status_code == 200
