import pytest

from tests_bank_applications import common
from tests_bank_applications import db_helpers

SUPPORT_URL = {'support_url': 'http://support.ya/'}

STATUSES_LIST = {
    'REGISTRATION': {
        'FAILED': {'title': 'Upal'},
        'PROCESSING': {
            'title': 'Ваш телефон в обработке!',
            'description': (
                'Обрабатывается! А пока можешь закинуть до 15.000 рублей'
            ),
        },
    },
    'SIMPLIFIED_IDENTIFICATION': {
        'FAILED': {'title': 'Upal2'},
        'PROCESSING': {
            'title': 'Ваш паспорт в обработке!',
            'description': (
                'Обрабатывается! А пока можешь закинуть до 100.000 рублей'
            ),
        },
    },
}


@pytest.mark.config(BANK_APPLICATIONS_STATUS_TITLES=STATUSES_LIST)
@pytest.mark.parametrize(
    'application_type, response_code',
    [('REGISTRATION', 200), ('SIMPLIFIED_IDENTIFICATION', 400)],
)
@pytest.mark.parametrize(
    'application_status', ['CREATED', 'PROCESSING', 'FAILED', 'SUCCESS'],
)
@pytest.mark.config(BANK_SUPPORT_URL=SUPPORT_URL)
async def test_set_status(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        bank_userinfo_mock,
        bank_forms_mock,
        taxi_processing_mock,
        pgsql,
        application_status,
        application_type,
        response_code,
):
    headers = (
        common.headers_without_buid()
        if application_type == 'REGISTRATION'
        else common.default_headers()
    )

    response = await taxi_bank_applications.post(
        'v1/applications/v1/create_application',
        headers=headers,
        json={'type': application_type},
    )
    assert response.status_code == response_code
    if response_code != 200:
        return

    application_id = response.json()['application_id']

    response = await taxi_bank_applications.post(
        'applications-internal/v1/set_application_status',
        json={
            'application_id': application_id,
            'status': application_status,
            'errors': ['1:some_reason'],
        },
    )
    assert response.status_code == response_code

    response = await taxi_bank_applications.post(
        'v1/applications/v1/get_application_status',
        headers=headers,
        json={'application_id': application_id},
    )

    if application_status == 'FAILED':
        assert response.status_code == 200
        assert response.json() == {
            'status': application_status,
            'title': 'Upal' if application_type == 'REGISTRATION' else 'Upal2',
            'support_url': SUPPORT_URL['support_url'],
            'type': application_type,
        }
    elif application_status == 'PROCESSING':
        assert response.status_code == 200
        object_type = (
            'телефон' if application_type == 'REGISTRATION' else 'паспорт'
        )
        amount = '15' if application_type == 'REGISTRATION' else '100'
        assert response.json() == {
            'status': application_status,
            'title': f'Ваш {object_type} в обработке!',
            'description': (
                'Обрабатывается! А пока можешь закинуть '
                f'до {amount}.000 рублей'
            ),
            'support_url': SUPPORT_URL['support_url'],
            'type': application_type,
        }
    elif application_status == 'CREATED':
        assert response.status_code == 404


@pytest.mark.config(BANK_APPLICATIONS_STATUS_TITLES=STATUSES_LIST)
@pytest.mark.parametrize(
    'application_status', ['CREATED', 'PROCESSING', 'FAILED', 'SUCCESS'],
)
@pytest.mark.config(BANK_SUPPORT_URL=SUPPORT_URL)
async def test_set_status_long_get_app_status(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        bank_userinfo_mock,
        bank_forms_mock,
        taxi_processing_mock,
        pgsql,
        application_status,
):
    application_type = 'SIMPLIFIED_IDENTIFICATION'
    headers = common.default_headers()

    response = await taxi_bank_applications.post(
        'v1/applications/v1/create_application',
        headers=headers,
        json={'type': application_type},
    )
    assert response.status_code == 400
    return


async def test_set_status_for_not_existing_application(taxi_bank_applications):
    response = await taxi_bank_applications.post(
        'applications-internal/v1/set_application_status',
        json={
            'application_id': '97754336-d4d1-43c1-aadb-cabd06674ea6',
            'status': 'FAILED',
            'errors': ['1:some_reason'],
        },
    )

    assert response.status_code == 404


async def test_invalid_application_id(taxi_bank_applications):
    response = await taxi_bank_applications.post(
        'applications-internal/v1/set_application_status',
        json={
            'application_id': '1-2-3-4-5',
            'status': 'FAILED',
            'errors': ['some_reason'],
        },
    )

    assert response.status_code == 400


async def test_get_processing_applications(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        bank_userinfo_mock,
        bank_forms_mock,
        taxi_processing_mock,
):
    application_type_registration = 'REGISTRATION'
    application_type_simplified = 'SIMPLIFIED_IDENTIFICATION'

    response = await taxi_bank_applications.post(
        'v1/applications/v1/create_application',
        headers=common.headers_without_buid(),
        json={'type': application_type_registration},
    )
    assert response.status_code == 200
    application_id = response.json()['application_id']

    response = await taxi_bank_applications.post(
        'applications-internal/v1/set_application_status',
        json={'application_id': application_id, 'status': 'FAILED'},
    )
    assert response.status_code == 200

    response = await taxi_bank_applications.post(
        'applications-internal/v1/get_processing_applications',
        json={'uid': common.DEFAULT_YANDEX_UID},
    )
    assert response.status_code == 200
    assert response.json() == {'applications': []}

    response = await taxi_bank_applications.post(
        'applications-internal/v1/set_application_status',
        json={'application_id': application_id, 'status': 'PROCESSING'},
    )
    assert response.status_code == 200

    response = await taxi_bank_applications.post(
        'applications-internal/v1/get_processing_applications',
        json={'uid': common.DEFAULT_YANDEX_UID},
    )
    assert response.status_code == 200
    assert response.json() == {
        'applications': [
            {
                'application_id': application_id,
                'type': application_type_registration,
                'is_blocking': True,
            },
        ],
    }

    response = await taxi_bank_applications.post(
        'applications-internal/v1/set_application_status',
        json={'application_id': application_id, 'status': 'SUCCESS'},
    )
    assert response.status_code == 200
    response = await taxi_bank_applications.post(
        'applications-internal/v1/get_processing_applications',
        json={'uid': common.DEFAULT_YANDEX_UID},
    )
    assert response.status_code == 200
    assert response.json() == {'applications': []}

    response = await taxi_bank_applications.post(
        'v1/applications/v1/create_application',
        headers=common.default_headers(),
        json={'type': application_type_simplified},
    )
    assert response.status_code == 400
    return


async def test_get_created_application(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        bank_forms_mock,
        taxi_processing_mock,
        bank_userinfo_mock,
):
    application_type = 'REGISTRATION'

    response = await taxi_bank_applications.post(
        'v1/applications/v1/create_application',
        headers=common.headers_without_buid(),
        json={'type': application_type},
    )
    assert response.status_code == 200
    application_id = response.json()['application_id']

    response = await taxi_bank_applications.post(
        'v1/applications/v1/get_application_status',
        headers=common.headers_without_buid(),
        json={'application_id': application_id},
    )
    assert response.status_code == 404


async def test_get_created_application_long_get_app_status_not_authorized(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        bank_forms_mock,
        taxi_processing_mock,
        bank_userinfo_mock,
):
    application_type = 'SIMPLIFIED_IDENTIFICATION'

    response = await taxi_bank_applications.post(
        'v1/applications/v1/create_application',
        headers=common.default_headers(),
        json={'type': application_type},
    )
    assert response.status_code == 400
    return


async def test_get_created_application_long_get_app_status(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        bank_forms_mock,
        taxi_processing_mock,
        bank_userinfo_mock,
):
    application_type = 'SIMPLIFIED_IDENTIFICATION'

    response = await taxi_bank_applications.post(
        'v1/applications/v1/create_application',
        headers=common.default_headers(),
        json={'type': application_type},
    )
    assert response.status_code == 400


async def test_get_application_status_long_invalid_application_type(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        bank_forms_mock,
        taxi_processing_mock,
        bank_userinfo_mock,
):
    application_type = 'REGISTRATION'

    response = await taxi_bank_applications.post(
        'v1/applications/v1/create_application',
        headers=common.default_headers(),
        json={'type': application_type},
    )
    assert response.status_code == 200
    application_id = response.json()['application_id']

    response = await taxi_bank_applications.post(
        'v1/applications/v1/simplified_identification/'
        'get_application_status/long',
        headers=common.default_headers(),
        json={'application_id': application_id},
    )
    assert response.status_code == 404


@pytest.mark.config(BANK_SUPPORT_URL=SUPPORT_URL)
async def test_get_processing_created_application(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        bank_forms_mock,
        taxi_processing_mock,
        bank_userinfo_mock,
):
    application_type = 'REGISTRATION'

    response = await taxi_bank_applications.post(
        'v1/applications/v1/create_application',
        headers=common.headers_without_buid(),
        json={'type': application_type},
    )
    assert response.status_code == 200
    application_id = response.json()['application_id']

    response = await taxi_bank_applications.post(
        'applications-internal/v1/set_application_status',
        json={'application_id': application_id, 'status': 'PROCESSING'},
    )
    assert response.status_code == 200

    response = await taxi_bank_applications.post(
        'v1/applications/v1/get_application_status',
        headers=common.headers_without_buid(),
        json={'application_id': application_id},
    )
    assert response.status_code == 200
    assert response.json()['status'] == 'PROCESSING'
    assert response.json()['support_url'] == SUPPORT_URL['support_url']


@pytest.mark.config(BANK_SUPPORT_URL=SUPPORT_URL)
async def test_get_processing_created_application_long_get_app_status(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        bank_forms_mock,
        taxi_processing_mock,
        bank_userinfo_mock,
):
    application_type = 'SIMPLIFIED_IDENTIFICATION'

    response = await taxi_bank_applications.post(
        'v1/applications/v1/create_application',
        headers=common.default_headers(),
        json={'type': application_type},
    )
    assert response.status_code == 400


@pytest.mark.config(BANK_SUPPORT_URL=SUPPORT_URL)
async def test_set_application_status_history_tables(
        taxi_bank_applications,
        pgsql,
        mockserver,
        bank_agreements_mock,
        bank_forms_mock,
        taxi_processing_mock,
        bank_userinfo_mock,
):
    application_id = db_helpers.add_application_registration(
        pgsql, common.DEFAULT_YANDEX_UID, 'PROCESSING',
    )
    response = await taxi_bank_applications.post(
        'applications-internal/v1/set_application_status',
        json={
            'application_id': application_id,
            'status': 'FAILED',
            'reason': 'fail',
        },
    )
    assert response.status_code == 200
    application = db_helpers.get_application(pgsql, application_id)
    reg_application = db_helpers.get_app_with_add_params_reg(
        pgsql, application_id,
    )
    assert application.status == reg_application[2]
    assert application.reason == reg_application[3]
    applications_history = db_helpers.get_apps_by_id_in_history(
        pgsql, application_id,
    )
    reg_applications_history = db_helpers.get_apps_by_id_in_history_reg(
        pgsql, application_id,
    )
    assert len(applications_history) == 1
    assert len(reg_applications_history) == 1
    # status
    assert applications_history[0][5] == reg_applications_history[0][4]
    # reason
    assert applications_history[0][8] == reg_applications_history[0][7]


async def test_get_application_status_wrong_user_id(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        bank_forms_mock,
        taxi_processing_mock,
        bank_userinfo_mock,
):
    response = await taxi_bank_applications.post(
        'v1/applications/v1/create_application',
        headers=common.headers_without_buid(),
        json={'type': 'REGISTRATION'},
    )

    assert response.status_code == 200
    application_id_reg = response.json()['application_id']

    response = await taxi_bank_applications.post(
        'applications-internal/v1/set_application_status',
        json={'application_id': application_id_reg, 'status': 'PROCESSING'},
    )
    assert response.status_code == 200

    headers = common.headers_without_buid()
    response = await taxi_bank_applications.post(
        'v1/applications/v1/get_application_status',
        headers=headers,
        json={'application_id': application_id_reg},
    )

    assert response.status_code == 200

    headers = common.headers_without_buid()
    headers['X-Yandex-UID'] = 'trap'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/get_application_status',
        headers=headers,
        json={'application_id': application_id_reg},
    )

    assert response.status_code == 404
