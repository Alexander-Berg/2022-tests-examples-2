from tests_bank_applications import common

LAST_NAME = 'volodyav'
MIDDLE_NAME = 'volodyevich'
FIRST_NAME = 'volodya'
PASSPORT_NUMBER = '1212654321'


def select_application(pgsql, application_id, application_type):
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(
        'SELECT user_id_type, user_id, type, status, '
        'initiator, submitted_form '
        'FROM bank_applications.applications '
        f'WHERE application_id=\'{application_id}\';',
    )
    records = list(cursor)

    assert len(records) == 1
    record = records[0]
    assert record[0] == 'BUID'
    assert record[1] == common.DEFAULT_YANDEX_BUID
    assert record[2] == application_type
    assert record[3] == 'PROCESSING'
    assert record[4] == {
        'initiator_type': 'BUID',
        'initiator_id': common.DEFAULT_YANDEX_BUID,
    }
    return record


async def test_submit_application(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        bank_forms_mock,
        taxi_processing_mock,
        pgsql,
        testpoint,
):
    application_type = 'SIMPLIFIED_IDENTIFICATION'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/create_application',
        headers=common.default_headers(),
        json={'type': application_type},
    )

    assert response.status_code == 400


async def test_submit_processing_application(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        bank_forms_mock,
        taxi_processing_mock,
        pgsql,
):
    application_type = 'SIMPLIFIED_IDENTIFICATION'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/create_application',
        headers=common.default_headers(),
        json={'type': application_type},
    )

    assert response.status_code == 400


async def test_invalid_inn_or_snils(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        bank_forms_mock,
        taxi_processing_mock,
):
    application_type = 'SIMPLIFIED_IDENTIFICATION'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/create_application',
        headers=common.default_headers(),
        json={'type': application_type},
    )

    assert response.status_code == 400


async def test_invalid_application_id(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        bank_forms_mock,
        taxi_processing_mock,
):
    response = await taxi_bank_applications.post(
        'v1/applications/v1/submit_form',
        headers=common.headers_with_idempotency(),
        json={
            'application_id': '1-2-3-4-5',
            'form': {
                'last_name': LAST_NAME,
                'first_name': FIRST_NAME,
                'middle_name': MIDDLE_NAME,
                'passport_number': PASSPORT_NUMBER,
                'birthday': '1994-11-15',
                'inn_or_snils': '12345678901',
            },
        },
    )

    assert response.status_code == 400


async def test_double_submit_application(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        bank_forms_mock,
        taxi_processing_mock,
        pgsql,
):
    application_type = 'SIMPLIFIED_IDENTIFICATION'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/create_application',
        headers=common.default_headers(),
        json={'type': application_type},
    )

    assert response.status_code == 400


async def test_submit_permission_violation(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        bank_forms_mock,
        taxi_processing_mock,
):
    application_type = 'SIMPLIFIED_IDENTIFICATION'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/create_application',
        headers=common.default_headers(),
        json={'type': application_type},
    )

    assert response.status_code == 400


async def test_submit_set_simplified_form(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        bank_forms_mock,
        taxi_processing_mock,
):
    application_type = 'SIMPLIFIED_IDENTIFICATION'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/create_application',
        headers=common.default_headers(),
        json={'type': application_type},
    )

    assert response.status_code == 400


async def test_submit_set_simplified_form_failed(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        bank_forms_mock,
        taxi_processing_mock,
):
    application_type = 'SIMPLIFIED_IDENTIFICATION'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/create_application',
        headers=common.default_headers(),
        json={'type': application_type},
    )

    assert response.status_code == 400
