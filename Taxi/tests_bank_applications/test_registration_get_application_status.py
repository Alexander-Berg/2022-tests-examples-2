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
}


async def test_registration_get_created_application(
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
        'v1/applications/v1/registration/get_application_status',
        headers=common.headers_without_buid(),
        json={'application_id': application_id},
    )
    assert response.status_code == 404


@pytest.mark.config(BANK_SUPPORT_URL=SUPPORT_URL)
async def test_registration_get_processing_created_application(
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

    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/get_application_status',
        headers=common.headers_without_buid(),
        json={'application_id': application_id},
    )
    assert response.status_code == 200
    assert response.json()['status'] == 'PROCESSING'
    assert response.json()['support_url'] == SUPPORT_URL['support_url']


@pytest.mark.config(BANK_APPLICATIONS_STATUS_TITLES=STATUSES_LIST)
@pytest.mark.parametrize(
    'application_status', ['CREATED', 'PROCESSING', 'FAILED', 'SUCCESS'],
)
@pytest.mark.config(BANK_SUPPORT_URL=SUPPORT_URL)
async def test_registration_set_status(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        bank_userinfo_mock,
        bank_forms_mock,
        taxi_processing_mock,
        pgsql,
        application_status,
):
    headers = common.headers_without_buid()
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/create_application', headers=headers,
    )
    assert response.status_code == 200
    application_id = response.json()['application_id']

    response = await taxi_bank_applications.post(
        'applications-internal/v1/set_application_status',
        json={
            'application_id': application_id,
            'status': application_status,
            'errors': ['1:some_reason'],
        },
    )
    assert response.status_code == 200

    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/get_application_status',
        headers=headers,
        json={'application_id': application_id},
    )

    if application_status == 'FAILED':
        assert response.status_code == 200
        assert response.json() == {
            'status': application_status,
            'title': 'Upal',
            'support_url': SUPPORT_URL['support_url'],
        }
    elif application_status == 'PROCESSING':
        assert response.status_code == 200
        object_type = 'телефон'
        amount = '15'
        assert response.json() == {
            'status': application_status,
            'title': f'Ваш {object_type} в обработке!',
            'description': (
                'Обрабатывается! А пока можешь закинуть '
                f'до {amount}.000 рублей'
            ),
            'support_url': SUPPORT_URL['support_url'],
        }
    elif application_status == 'CREATED':
        assert response.status_code == 404


async def test_registration_set_noncritical_status(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        bank_userinfo_mock,
        bank_forms_mock,
        taxi_processing_mock,
        pgsql,
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
    application_reg = db_helpers.get_application_registration(
        pgsql, application_id,
    )
    assert application_reg.noncritical_status == 'PROCESSING'
    assert application_reg.noncritical_status == application_reg.status

    response = await taxi_bank_applications.post(
        'applications-internal/v1/registration/set_application_noncritical_status',  # noqa
        json={
            'application_id': application_id,
            'status': 'set_bank_phone_in_passport',
        },
    )
    assert response.status_code == 200
    application_reg = db_helpers.get_application_registration(
        pgsql, application_id,
    )
    assert application_reg.noncritical_status == 'set_bank_phone_in_passport'
    assert application_reg.status == 'PROCESSING'


async def test_registration_set_noncritical_status_not_found(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        bank_userinfo_mock,
        bank_forms_mock,
        taxi_processing_mock,
        pgsql,
):
    application_id = '0ad68f44-fdae-4218-8235-db574446cdaa'
    response = await taxi_bank_applications.post(
        'applications-internal/v1/registration/set_application_noncritical_status',  # noqa
        json={'application_id': application_id, 'status': 'PROCESSING'},
    )
    assert response.status_code == 404


async def test_registration_get_application_status_wrong_user_id(
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
    application_id_reg = response.json()['application_id']

    response = await taxi_bank_applications.post(
        'applications-internal/v1/set_application_status',
        json={'application_id': application_id_reg, 'status': 'PROCESSING'},
    )
    assert response.status_code == 200

    headers = common.headers_without_buid()
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/get_application_status',
        headers=headers,
        json={'application_id': application_id_reg},
    )

    assert response.status_code == 200

    headers = common.headers_without_buid()
    headers['X-Yandex-UID'] = 'trap'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/get_application_status',
        headers=headers,
        json={'application_id': application_id_reg},
    )

    assert response.status_code == 404


@pytest.mark.experiments3(filename='bank_action_after_registration.json')
@pytest.mark.parametrize(
    'status,yandex_uid,action',
    [
        ('PROCESSING', common.DEFAULT_YANDEX_UID, None),
        ('FAILED', common.DEFAULT_YANDEX_UID, None),
        ('SUCCESS', 'topup_uid', 'banksdk://registration.action/topup'),
        (
            'SUCCESS',
            'dashboard_uid',
            'banksdk://registration.action/dashboard',
        ),
        ('SUCCESS', 'no_match_uid', None),
    ],
)
async def test_registration_get_application_status_action(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        bank_forms_mock,
        taxi_processing_mock,
        bank_userinfo_mock,
        pgsql,
        status,
        yandex_uid,
        action,
):
    application_id = db_helpers.add_application_registration(
        pgsql, yandex_uid, status,
    )

    headers = common.default_headers()
    headers['X-Yandex-UID'] = yandex_uid
    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/get_application_status',
        headers=headers,
        json={'application_id': application_id},
    )

    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['status'] == status
    assert resp_json.get('action') == action


async def test_registration_get_application_status_no_action_exp(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        bank_forms_mock,
        taxi_processing_mock,
        bank_userinfo_mock,
        pgsql,
):
    application_id = db_helpers.add_application_registration(
        pgsql, common.DEFAULT_YANDEX_UID, 'SUCCESS',
    )

    response = await taxi_bank_applications.post(
        'v1/applications/v1/registration/get_application_status',
        headers=common.default_headers(),
        json={'application_id': application_id},
    )

    assert response.status_code == 200
    assert response.json().get('action') is None
