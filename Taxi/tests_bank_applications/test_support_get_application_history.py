import pytest

from tests_bank_applications import common


HANDLE_URL = HANDLE_URL = '/applications-support/v1/get_application_history'
REGISTRATION_APP_ID = '7948e3a9-623c-4524-a390-9e4264d27a02'
SIMPLIFIED_APP_ID = '7948e3a9-623c-4524-a390-9e4264d27a03'
SIMPLIFIED_ESIA_APP_ID = '7948e3a9-623c-4524-a390-9e4264d27a08'
KYC_APP_ID = '7948e3a9-623c-4524-a390-9e4264d22222'
DIGITAL_CARD_APP_ID = '7948e3a9-623c-4524-a390-9e4264d27a07'
SPLIT_CARD_APP_ID = '7948e3a9-623c-4524-a390-9e4264d11111'
PLUS_APP_ID = '3ac0a2cc-637e-4c50-b7c3-87d1e641cb9c'
DEFAULT_REGISTRATION_FORM = {
    'phone': '80000000000',
    'masked_phone': '8******0000',
    'phone_id': '1',
}
DEFAULT_INITIATOR = {
    'initiator_type': 'BUID',
    'initiator_id': common.DEFAULT_YANDEX_BUID,
}


def common_asserts(
        response,
        history_len,
        application_id,
        app_type,
        history,
        user_id_type='buid',
        cursor=None,
):
    assert response.status_code == 200
    resp = response.json()
    assert len(resp['history']) == history_len
    assert resp['application_id'] == application_id
    assert resp['type'] == app_type
    if user_id_type == 'buid':
        assert resp['buid'] == common.DEFAULT_YANDEX_BUID
    else:
        assert resp['uid'] == common.DEFAULT_YANDEX_UID
    assert resp['history'] == history
    if cursor is not None:
        assert resp['cursor'] == cursor


def build_registration_app(status, db_status, minute, form):
    return {
        'status': status,
        'db_status': db_status,
        'form': form,
        'initiator': {
            'initiator_type': 'UID',
            'initiator_id': common.DEFAULT_YANDEX_UID,
        },
        'operation_type': 'INSERT',
        'operation_at': f'2022-02-02T20:{minute}:58.838783+00:00',
        'additional_params': {},
    }


def build_card_issue(status, minute):
    return {
        'status': status,
        'db_status': status,
        'initiator': DEFAULT_INITIATOR,
        'operation_type': 'INSERT',
        'operation_at': f'2022-02-07T20:{minute}:58.838783+00:00',
    }


def build_simpl_or_kyc_app(
        status, db_status, minute, form=None, add_params=None, reason=False,
):
    res = {
        'status': status,
        'db_status': db_status,
        'initiator': DEFAULT_INITIATOR,
        'operation_type': 'INSERT',
        'operation_at': f'2022-02-03T20:{minute}:58.838783+00:00',
    }
    if reason:
        res['reason'] = 'error1'
    if form is not None:
        res['form'] = form
    if add_params is not None:
        res['additional_params'] = add_params
    return res


@pytest.mark.parametrize(
    'application_id',
    [
        REGISTRATION_APP_ID,
        SIMPLIFIED_APP_ID,
        KYC_APP_ID,
        DIGITAL_CARD_APP_ID,
        SPLIT_CARD_APP_ID,
        PLUS_APP_ID,
    ],
)
async def test_get_application_history_permission_denied(
        taxi_bank_applications,
        mockserver,
        access_control_mock,
        application_id,
):
    response = await taxi_bank_applications.post(
        HANDLE_URL,
        headers=common.get_support_headers(''),
        json={'application_id': application_id, 'limit': 1},
    )

    assert response.status_code == 401


async def test_get_application_history_app_not_found(
        taxi_bank_applications, mockserver, access_control_mock,
):
    response = await taxi_bank_applications.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={
            'application_id': '11111111-1111-1111-1111-111111111111',
            'limit': 1,
        },
    )

    assert response.status_code == 404


@pytest.mark.parametrize('limit', [2, 10])
async def test_registration_get_application_history_ok(
        taxi_bank_applications, mockserver, access_control_mock, limit,
):
    response = await taxi_bank_applications.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={'application_id': REGISTRATION_APP_ID, 'limit': limit},
    )

    common_asserts(
        response,
        min(4, limit),
        REGISTRATION_APP_ID,
        'REGISTRATION',
        [
            build_registration_app('SUCCESS', 'SUCCESS', '31', {}),
            build_registration_app('PROCESSING', 'PROCESSING', '30', {}),
            build_registration_app(
                'CREATED', 'SMS_CODE_SENT', '29', DEFAULT_REGISTRATION_FORM,
            ),
            build_registration_app(
                'CREATED', 'CREATED', '28', DEFAULT_REGISTRATION_FORM,
            ),
        ][:limit],
        user_id_type='uid',
    )


@pytest.mark.parametrize('limit', [3, 10])
async def test_simplified_identification_get_application_history_ok(
        taxi_bank_applications, mockserver, access_control_mock, limit,
):
    response = await taxi_bank_applications.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={'application_id': SIMPLIFIED_APP_ID, 'limit': limit},
    )

    common_asserts(
        response,
        min(6, limit),
        SIMPLIFIED_APP_ID,
        'SIMPLIFIED_IDENTIFICATION',
        [
            build_simpl_or_kyc_app('FAILED', 'FAILED', '33', reason=True),
            build_simpl_or_kyc_app(
                'PROCESSING',
                'CORE_BANKING',
                '32',
                form=common.get_standard_normalized_form(),
                add_params={
                    'prenormalized_form': common.get_standard_submitted_form(),
                },
            ),
            build_simpl_or_kyc_app(
                'PROCESSING',
                'AGREEMENTS_ACCEPTED',
                '31',
                form=common.get_standard_normalized_form(),
                add_params={
                    'prenormalized_form': common.get_standard_submitted_form(),
                },
            ),
            build_simpl_or_kyc_app(
                'PROCESSING',
                'SUBMITTED',
                '30',
                form=common.get_standard_normalized_form(),
                add_params={
                    'prenormalized_form': common.get_standard_submitted_form(),
                },
            ),
            build_simpl_or_kyc_app(
                'CREATED',
                'DRAFT_SAVED',
                '29',
                form={'last_name': 'Петров', 'first_name': 'Петр'},
            ),
            build_simpl_or_kyc_app('CREATED', 'CREATED', '28'),
        ][:limit],
    )


@pytest.mark.parametrize('limit', [2, 10])
async def test_kyc_get_application_history_ok(
        taxi_bank_applications, mockserver, access_control_mock, limit,
):
    response = await taxi_bank_applications.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={'application_id': KYC_APP_ID, 'limit': limit},
    )

    common_asserts(
        response,
        min(5, limit),
        KYC_APP_ID,
        'KYC',
        [
            build_simpl_or_kyc_app('SUCCESS', 'SUCCESS', '32'),
            build_simpl_or_kyc_app(
                'PROCESSING',
                'AGREEMENTS_ACCEPTED',
                '31',
                add_params={'kyc_form': common.get_standard_normalized_form()},
            ),
            build_simpl_or_kyc_app(
                'PROCESSING',
                'CORE_BANKING',
                '30',
                add_params={'kyc_form': common.get_standard_normalized_form()},
            ),
            build_simpl_or_kyc_app(
                'PROCESSING',
                'PROCESSING',
                '29',
                add_params={'kyc_form': common.get_standard_normalized_form()},
            ),
            build_simpl_or_kyc_app('CREATED', 'CREATED', '28'),
        ][:limit],
    )


@pytest.mark.parametrize('limit', [1, 10])
@pytest.mark.parametrize(
    'app_type,application_id',
    [
        ('DIGITAL_CARD_ISSUE', DIGITAL_CARD_APP_ID),
        ('SPLIT_CARD_ISSUE', SPLIT_CARD_APP_ID),
    ],
)
async def test_digital_or_split_card_issue_get_application_history_ok(
        taxi_bank_applications,
        mockserver,
        access_control_mock,
        app_type,
        application_id,
        limit,
):
    response = await taxi_bank_applications.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={'application_id': application_id, 'limit': limit},
    )

    history = None
    history_len = None
    if app_type == 'DIGITAL_CARD_ISSUE':
        history_len = min(2, limit)
        history = [
            build_card_issue('PROCESSING', '29'),
            build_card_issue('CREATED', '28'),
        ][:limit]
    elif app_type == 'SPLIT_CARD_ISSUE':
        history_len = min(3, limit)
        history = [
            build_card_issue('SUCCESS', '30'),
            build_card_issue('PROCESSING', '29'),
            build_card_issue('CREATED', '28'),
        ][:limit]

    common_asserts(response, history_len, application_id, app_type, history)


async def test_cursor_get_application_history_ok(
        taxi_bank_applications, mockserver, access_control_mock,
):
    app_type = 'SIMPLIFIED_IDENTIFICATION'
    response = await taxi_bank_applications.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={'application_id': SIMPLIFIED_APP_ID, 'limit': 3},
    )

    cursor = 'eyJjdXJzb3Jfa2V5Ijo0fQ=='
    common_asserts(
        response,
        3,
        SIMPLIFIED_APP_ID,
        app_type,
        [
            build_simpl_or_kyc_app('FAILED', 'FAILED', '33', reason=True),
            build_simpl_or_kyc_app(
                'PROCESSING',
                'CORE_BANKING',
                '32',
                form=common.get_standard_normalized_form(),
                add_params={
                    'prenormalized_form': common.get_standard_submitted_form(),
                },
            ),
            build_simpl_or_kyc_app(
                'PROCESSING',
                'AGREEMENTS_ACCEPTED',
                '31',
                form=common.get_standard_normalized_form(),
                add_params={
                    'prenormalized_form': common.get_standard_submitted_form(),
                },
            ),
        ],
        cursor=cursor,
    )

    response = await taxi_bank_applications.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={
            'application_id': SIMPLIFIED_APP_ID,
            'limit': 2,
            'cursor': cursor,
        },
    )

    cursor = 'eyJjdXJzb3Jfa2V5IjoyfQ=='
    common_asserts(
        response,
        2,
        SIMPLIFIED_APP_ID,
        app_type,
        [
            build_simpl_or_kyc_app(
                'PROCESSING',
                'SUBMITTED',
                '30',
                form=common.get_standard_normalized_form(),
                add_params={
                    'prenormalized_form': common.get_standard_submitted_form(),
                },
            ),
            build_simpl_or_kyc_app(
                'CREATED',
                'DRAFT_SAVED',
                '29',
                form={'last_name': 'Петров', 'first_name': 'Петр'},
            ),
        ],
        cursor=cursor,
    )

    response = await taxi_bank_applications.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={
            'application_id': SIMPLIFIED_APP_ID,
            'limit': 2,
            'cursor': cursor,
        },
    )

    common_asserts(
        response,
        1,
        SIMPLIFIED_APP_ID,
        app_type,
        [build_simpl_or_kyc_app('CREATED', 'CREATED', '28')],
    )


async def test_application_history_simplified_identification_esia_status_ok(
        taxi_bank_applications, mockserver, access_control_mock,
):
    app_type = 'SIMPLIFIED_IDENTIFICATION_ESIA'
    response = await taxi_bank_applications.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={'application_id': SIMPLIFIED_ESIA_APP_ID, 'limit': 3},
    )

    common_asserts(
        response,
        1,
        SIMPLIFIED_ESIA_APP_ID,
        app_type,
        [
            {
                'status': common.STATUS_FAILED,
                'db_status': common.STATUS_FAILED,
                'initiator': DEFAULT_INITIATOR,
                'operation_type': 'INSERT',
                'operation_at': f'2022-02-03T20:28:58.838783+00:00',
                'additional_params': {
                    'auth_code': 'auth.code',
                    'redirect_url': 'http://redirect.url',
                    'data_revision': 1234,
                    'esia_state': 'esia.state',
                },
            },
        ],
    )


async def test_application_history_plus_status_ok(
        taxi_bank_applications, mockserver, access_control_mock,
):
    app_type = 'PLUS'
    response = await taxi_bank_applications.post(
        HANDLE_URL,
        headers=common.get_support_headers(),
        json={'application_id': PLUS_APP_ID, 'limit': 3},
    )

    common_asserts(response, 0, PLUS_APP_ID, app_type, [])
