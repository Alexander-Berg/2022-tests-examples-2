# pylint: disable=C0302
import copy

import pytest  # noqa: F401

from tests_cargo_corp import utils


MOCK_NOW = '2021-05-31T19:00:00+00:00'

YANDEX_UID = 'test_ya_uid'
YANDEX_LOGIN = 'test_ya_login'
HEADERS = {
    'X-Yandex-Uid': YANDEX_UID,
    'X-Yandex-Login': YANDEX_LOGIN,
    'X-Ya-User-Ticket': 'test_ya_ticket',
}

LOCAL_CORP_CLIENT_ID = 'long_corp_client_id_of_length_32'

ANOTHER_ROLE_ID = 'another_role_id'
ANOTHER_ROLE_NAME = 'private ryan'
ANOTHER_EMAIL_ID = 'another@ya.ru'

CANDIDATE_CONFIRMATION_CODES = [
    'test_confirmation_code',
    'test_confirmation_code_2',
    'test_confirmation_code_3',
]

CANDIDATE_PHONES = [
    {'number': '12345678910'},
    {'number': '0987654321'},
    {'number': '1029384756'},
    {'number': '3456345656'},
    {'number': '6789384123'},
    {'number': '1673333123'},
]
CANDIDATE_EMAILS = ['test1@ya.ru', 'test2@ya.ru', 'test3@ya.ru']
CANDIDATES = [
    {
        'name': 'Чумабой',
        'phone': CANDIDATE_PHONES[0],
        'role_id': utils.ROLE_ID,
        'email': CANDIDATE_EMAILS[0],
        'role_name': utils.OWNER_ROLE_TRANSLATION,
    },
    {
        'name': 'Чумабой_2',
        'phone': CANDIDATE_PHONES[1],
        'role_id': utils.ROLE_ID,
        'email': CANDIDATE_EMAILS[1],
        'role_name': utils.OWNER_ROLE_TRANSLATION,
    },
    {
        'name': 'Чумабой_3',
        'phone': CANDIDATE_PHONES[2],
        'role_id': utils.ROLE_ID,
        'email': CANDIDATE_EMAILS[2],
        'role_name': utils.OWNER_ROLE_TRANSLATION,
    },
]
CANDIDATE_NON_GENERAL_ROLE = {
    'name': 'Чумабой',
    'phone': CANDIDATE_PHONES[0],
    'role_id': utils.NON_GENERAL_ROLE_ID,
    'email': CANDIDATE_EMAILS[0],
    'role_name': utils.NON_GENERAL_ROLE_NAME,
}
CONFIRMED_CANDIDATE = {
    'id': YANDEX_UID,
    'info': {
        'name': CANDIDATES[0]['name'],
        'email': CANDIDATE_EMAILS[0],
        'phones': [CANDIDATE_PHONES[0]],
        'is_removable': True,
    },
    'roles': [{'id': utils.ROLE_ID, 'name': utils.OWNER_ROLE_TRANSLATION}],
    'is_disabled': False,
    'revision': 1,
}
CONFLICT_BY_PHONE_MSG = 'Уже есть регистрация с таким номером'


@pytest.fixture(name='make_candidate_confirm_request')
def _make_candidate_confirm_request(taxi_cargo_corp):
    async def wrapper(code, corp_client_id=utils.CORP_CLIENT_ID, headers=None):
        response = await taxi_cargo_corp.post(
            'v1/client/employee-candidate/confirm',
            headers=headers or HEADERS,
            params={
                'confirmation_code': code,
                'corp_client_id': corp_client_id,
            },
        )
        return response

    return wrapper


@pytest.mark.pgsql(
    'cargo_corp',
    queries=[
        utils.get_client_create_request(),
        utils.get_candidate_create_request(
            corp_client_id=utils.CORP_CLIENT_ID,
            confirmation_code=CANDIDATE_CONFIRMATION_CODES[0],
            name=CANDIDATES[0]['name'],
            phone_pd_id=f'{CANDIDATE_PHONES[0]["number"]}_id',
            role_id=utils.ROLE_ID,
            email_pd_id=f'{CANDIDATE_EMAILS[0]}_id',
        ),
    ],
)
@pytest.mark.parametrize(
    ('confirmation_code', 'corp_client_id', 'expected_json', 'expected_code'),
    (
        pytest.param(
            CANDIDATE_CONFIRMATION_CODES[0],
            utils.CORP_CLIENT_ID,
            {
                'confirmation_code': CANDIDATE_CONFIRMATION_CODES[0],
                'info': CANDIDATES[0],
                'revision': 1,
                'corp_client_name': utils.CORP_CLIENT_NAME,
                'is_already_confirmed': False,
            },
            200,
            id='ok',
        ),
        pytest.param(
            'test_invalid_confirmation_code',
            utils.CORP_CLIENT_ID,
            {'code': 'not_found', 'message': 'Unknown employee-candidate'},
            404,
            id='not found-candidate',
        ),
        pytest.param(
            CANDIDATE_CONFIRMATION_CODES[0],
            LOCAL_CORP_CLIENT_ID,
            {'code': 'not_found', 'message': 'Unknown corp_client'},
            404,
            id='not found-corp_client',
        ),
    ),
)
async def test_employee_candidate_info(
        mockserver,
        taxi_cargo_corp,
        user_has_rights,
        confirmation_code,
        corp_client_id,
        expected_json,
        expected_code,
):
    @mockserver.json_handler(
        '/cargo-corp/internal/cargo-corp/v1/client/employee/list',
    )
    def _employee_list(request):
        return {'employees': []}

    response = await taxi_cargo_corp.get(
        '/v1/client/employee-candidate/info',
        params={
            'confirmation_code': confirmation_code,
            'corp_client_id': corp_client_id,
        },
        headers={'X-Yandex-Uid': YANDEX_UID},
    )
    assert response.status_code == expected_code
    assert response.json() == expected_json


@pytest.mark.parametrize(
    ('employee_list_response', 'expected_json', 'expected_code'),
    (
        pytest.param(
            [CONFIRMED_CANDIDATE],
            {
                'confirmation_code': CANDIDATE_CONFIRMATION_CODES[0],
                'info': CANDIDATES[0],
                'revision': 1,
                'corp_client_name': utils.CORP_CLIENT_NAME,
                'is_already_confirmed': True,
            },
            200,
            id='already confirmed, ok',
        ),
        pytest.param(
            [CONFIRMED_CANDIDATE, CONFIRMED_CANDIDATE],
            {'code': 'not_found', 'message': 'Unknown employee-candidate'},
            404,
            id='ignore multiple list',
        ),
        pytest.param(
            [dict(CONFIRMED_CANDIDATE, revision=3)],
            {'code': 'not_found', 'message': 'Unknown employee-candidate'},
            404,
            id='ignore modified employee',
        ),
        pytest.param(
            [dict(CONFIRMED_CANDIDATE, is_disabled=True)],
            {'code': 'not_found', 'message': 'Unknown employee-candidate'},
            404,
            id='ignore disabled employee',
        ),
        pytest.param(
            [dict(CONFIRMED_CANDIDATE, robot_external_ref='it is robot')],
            {'code': '500', 'message': 'Internal Server Error'},
            500,
            id='throw on robot employee',
        ),
        pytest.param(
            [dict(CONFIRMED_CANDIDATE, info={'name': 'empty'})],
            {'code': '500', 'message': 'Internal Server Error'},
            500,
            id='throw on employee with no info',
        ),
        pytest.param(
            [dict(CONFIRMED_CANDIDATE, roles=[])],
            {'code': '500', 'message': 'Internal Server Error'},
            500,
            id='throw on employee with no roles',
        ),
    ),
)
async def test_employee_candidate_info_already_confirmed(
        mockserver,
        taxi_cargo_corp,
        user_has_rights,
        employee_list_response,
        expected_json,
        expected_code,
):
    @mockserver.json_handler(
        '/cargo-corp/internal/cargo-corp/v1/client/employee/list',
    )
    def _employee_list(request):
        return {'employees': employee_list_response}

    response = await taxi_cargo_corp.get(
        '/v1/client/employee-candidate/info',
        params={
            'confirmation_code': CANDIDATE_CONFIRMATION_CODES[0],
            'corp_client_id': utils.CORP_CLIENT_ID,
        },
        headers={'X-Yandex-Uid': YANDEX_UID},
    )
    assert response.status_code == expected_code
    assert response.json() == expected_json


@pytest.mark.pgsql(
    'cargo_corp',
    queries=[
        utils.get_client_create_request(),
        # create non general role
        utils.get_role_create_request(
            role_id=CANDIDATE_NON_GENERAL_ROLE['role_id'],
            corp_client_id=utils.CORP_CLIENT_ID,
            role_name=CANDIDATE_NON_GENERAL_ROLE['role_name'],
        ),
        utils.get_candidate_create_request(
            corp_client_id=utils.CORP_CLIENT_ID,
            confirmation_code=CANDIDATE_CONFIRMATION_CODES[0],
            name=CANDIDATE_NON_GENERAL_ROLE['name'],
            phone_pd_id=f'{CANDIDATE_PHONES[0]["number"]}_id',
            role_id=CANDIDATE_NON_GENERAL_ROLE['role_id'],
            email_pd_id=f'{CANDIDATE_NON_GENERAL_ROLE["email"]}_id',
        ),
    ],
)
async def test_employee_candidate_info_with_non_general_role(taxi_cargo_corp):
    response = await taxi_cargo_corp.get(
        '/v1/client/employee-candidate/info',
        params={
            'confirmation_code': CANDIDATE_CONFIRMATION_CODES[0],
            'corp_client_id': utils.CORP_CLIENT_ID,
        },
        headers={'X-Yandex-Uid': YANDEX_UID},
    )
    assert response.status_code == 200
    assert response.json() == {
        'confirmation_code': CANDIDATE_CONFIRMATION_CODES[0],
        'corp_client_name': utils.CORP_CLIENT_NAME,
        'info': CANDIDATE_NON_GENERAL_ROLE,
        'revision': 1,
        'is_already_confirmed': False,
    }


@pytest.mark.pgsql(
    'cargo_corp',
    queries=[
        utils.get_client_create_request(),
        utils.get_candidate_create_request(
            corp_client_id=utils.CORP_CLIENT_ID,
            confirmation_code=CANDIDATE_CONFIRMATION_CODES[0],
            name=CANDIDATES[0]['name'],
            phone_pd_id=f'{CANDIDATE_PHONES[0]["number"]}_id',
            role_id=utils.ROLE_ID,
            email_pd_id=f'{CANDIDATE_EMAILS[0]}_id',
        ),
    ],
)
@pytest.mark.config(
    CARGO_CORP_ROLL_OUT_OPTIONS_ENABLED={
        'does_front_supports_several_error_phone_codes_on_confirm': True,
    },
    CARGO_CRM_NOTIFY_PHOENIX_OPTIONS={
        'should_notify_confirm_employee_candidate': True,
    },
)
async def test_employee_candidate_confirm(
        make_candidate_confirm_request,
        user_has_rights,
        mockserver,
        stq,
        blackbox,
        get_employee_candidate_info,
):
    @mockserver.json_handler('/cargo-corp/v1/client/employee-candidate/info')
    def _candidate_info(request):
        candidate = get_employee_candidate_info(
            request.query['confirmation_code'], request.args['corp_client_id'],
        )
        if not candidate:
            return mockserver.make_response(
                status=404,
                json={
                    'code': 'not_found',
                    'message': 'Unknown employee-candidate',
                },
            )
        return mockserver.make_response(status=200, json=candidate)

    # invalid confirmation code
    response = await make_candidate_confirm_request(
        code=CANDIDATE_CONFIRMATION_CODES[1],
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': 'not_found',
        'message': 'Unknown employee-candidate',
    }

    # invalid corp client
    response = await make_candidate_confirm_request(
        code=CANDIDATE_CONFIRMATION_CODES[0],
        corp_client_id=LOCAL_CORP_CLIENT_ID,
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': 'not_found',
        'message': 'Unknown corp_client',
    }

    # phone check (phone number doesn't exist)
    candidate_phone = blackbox.response['users'][0]['phones'].pop()

    response = await make_candidate_confirm_request(
        code=CANDIDATE_CONFIRMATION_CODES[0],
    )
    assert response.status_code == 403
    assert response.json() == {
        'code': 'phone_not_found',
        'message': 'Candidate phone not found in user phones',
    }

    blackbox.response['users'][0]['phones'].append(candidate_phone)

    # phone check (phone number isn't secured)
    for phone in blackbox.response['users'][0]['phones']:
        phone['attributes']['108'] = '0'

    response = await make_candidate_confirm_request(
        code=CANDIDATE_CONFIRMATION_CODES[0],
    )
    assert response.status_code == 403
    assert response.json() == {
        'code': 'phone_not_secured',
        'message': 'Candidate phone found but not secured',
    }

    for phone in blackbox.response['users'][0]['phones']:
        phone['attributes']['108'] = '1'

    # idempotency
    for _ in range(2):
        response = await make_candidate_confirm_request(
            code=CANDIDATE_CONFIRMATION_CODES[0],
        )
        assert response.status_code == 200
        assert response.json() == {
            'company': {
                'id': utils.CORP_CLIENT_ID,
                'is_registration_finished': False,
                'name': 'corp_client_name',
                'source': 'cargo',
            },
            'id': YANDEX_UID,
            'revision': 1,
            'is_disabled': False,
            'info': {
                'phones': [CANDIDATE_PHONES[0]],
                'email': CANDIDATE_EMAILS[0],
                'yandex_login': YANDEX_LOGIN,
                'name': CANDIDATES[0]['name'],
                'is_removable': True,
            },
        }

    # confirming already confirmed candidate
    # with wrong confirmation code
    response = await make_candidate_confirm_request(
        code=CANDIDATE_CONFIRMATION_CODES[1],
    )
    assert response.status_code == 200
    assert response.json() == {
        'company': {
            'id': utils.CORP_CLIENT_ID,
            'is_registration_finished': False,
            'name': 'corp_client_name',
            'source': 'cargo',
        },
        'id': YANDEX_UID,
        'revision': 1,
        'is_disabled': False,
        'info': {
            'phones': [CANDIDATE_PHONES[0]],
            'email': CANDIDATE_EMAILS[0],
            'yandex_login': YANDEX_LOGIN,
            'name': CANDIDATES[0]['name'],
            'is_removable': True,
        },
    }

    assert stq.cargo_c2c_phoenix_notifications.times_called == 1
    stq_params = stq.cargo_c2c_phoenix_notifications.next_call()
    assert stq_params['id'] == f'{utils.CORP_CLIENT_ID}:{YANDEX_UID}'
    assert stq_params['kwargs']['yandex_uid'] == YANDEX_UID
    assert stq_params['kwargs']['role'] == utils.ROLE_ID
    assert stq_params['kwargs']['locale'] == 'ru'


@pytest.mark.parametrize(
    'expected_code',
    (
        pytest.param(
            200,
            marks=pytest.mark.config(
                CARGO_CORP_ROLL_OUT_OPTIONS_ENABLED={
                    'is_candidate_info_idempotence_deployed': False,
                },
            ),
            id='ok, already in db, old way',
        ),
        pytest.param(
            404,
            marks=pytest.mark.config(
                CARGO_CORP_ROLL_OUT_OPTIONS_ENABLED={
                    'is_candidate_info_idempotence_deployed': True,
                },
            ),
            id='do not check db, use info response',
        ),
    ),
)
async def test_employee_candidate_confirm_by_unknown_code(
        make_candidate_confirm_request,
        user_has_rights,
        mockserver,
        blackbox,
        expected_code,
):
    @mockserver.json_handler('/cargo-corp/v1/client/employee-candidate/info')
    def _candidate_info(request):
        return mockserver.make_response(
            status=404,
            json={
                'code': 'not_found',
                'message': 'Unknown employee-candidate',
            },
        )

    # confirming already confirmed candidate
    # with wrong confirmation code
    response = await make_candidate_confirm_request(
        code='some_code',
        headers={
            'X-Yandex-Uid': utils.YANDEX_UID,
            'X-Ya-User-Ticket': 'test_ya_ticket',
        },
    )
    assert response.status_code == expected_code
    if expected_code != 200:
        return
    assert response.json() == {
        'company': {
            'id': utils.CORP_CLIENT_ID,
            'is_registration_finished': False,
            'name': 'corp_client_name',
            'source': 'cargo',
        },
        'id': utils.YANDEX_UID,
        'revision': 1,
        'is_disabled': False,
        'info': {
            'phones': [{'number': utils.PHONE}],
            'name': utils.EMPLOYEE_NAME,
            'is_removable': True,
            'yandex_login': utils.YANDEX_LOGIN,
            'email': utils.YANDEX_EMAIL,
        },
    }


@pytest.mark.pgsql(
    'cargo_corp',
    queries=[
        utils.get_client_create_request(),
        utils.get_candidate_create_request(
            corp_client_id=utils.CORP_CLIENT_ID,
            confirmation_code=CANDIDATE_CONFIRMATION_CODES[1],
            name=CANDIDATES[1]['name'],
            phone_pd_id=f'{CANDIDATE_PHONES[1]["number"]}_id',
            role_id=utils.ROLE_ID,
            email_pd_id=f'{CANDIDATE_EMAILS[1]}_id',
        ),
    ],
)
async def test_candidate_confirm_invalid_role(
        make_candidate_confirm_request, mockserver, blackbox, remove_role,
):
    @mockserver.json_handler('/cargo-corp/v1/client/employee-candidate/info')
    def _candidate_info(request):
        candidate = {
            'confirmation_code': CANDIDATE_CONFIRMATION_CODES[1],
            'revision': 1,
            'info': CANDIDATES[1],
            'corp_client_name': utils.CORP_CLIENT_NAME,
        }
        return mockserver.make_response(status=200, json=candidate)

    remove_role(utils.ROLE_ID)
    response = await make_candidate_confirm_request(
        code=CANDIDATE_CONFIRMATION_CODES[1],
    )
    assert response.status_code == 404
    assert response.json() == {'code': 'not_found', 'message': 'Unknown role'}


@pytest.fixture(name='make_employee_candidate_upsert_request')
def _make_employee_candidate_upsert_request(taxi_cargo_corp):
    async def _wrapper(request_json):
        return await taxi_cargo_corp.put(
            '/internal/cargo-corp/v1/client/employee-candidate/upsert',
            headers={
                'X-B2B-Client-Id': utils.CORP_CLIENT_ID,
                'Origin': 'dostavka.yandex.ru',
            },
            json=request_json,
        )

    return _wrapper


def _assert_stq_invitation_params(
        stq_params, confirmation_code, contact, invitation_kind, phone=None,
):
    corp_client_id = utils.CORP_CLIENT_ID
    corp_client_country = 'rus'
    if invitation_kind == 'sms':
        contact_pd_id = contact['number'] + '_id'
    elif invitation_kind == 'email':
        contact_pd_id = contact + '_id'
        phone_pd_id = phone['number'] + '_id'

    assert stq_params['id'] == f'{corp_client_id}:{contact_pd_id}'
    assert stq_params['kwargs']['invitation_kind'] == invitation_kind
    assert stq_params['kwargs']['corp_client_id'] == corp_client_id
    assert stq_params['kwargs']['confirmation_code'] == confirmation_code
    assert stq_params['kwargs']['contact_pd_id'] == contact_pd_id
    assert stq_params['kwargs']['country'] == corp_client_country
    assert stq_params['kwargs']['started_at'] == MOCK_NOW
    assert stq_params['kwargs']['host'] == 'dostavka.yandex.ru'
    assert stq_params['kwargs']['locale'] == 'ru'  # default

    if invitation_kind == 'email':
        assert stq_params['kwargs']['phone_pd_id'] == phone_pd_id


# FIXME (dipterix): split by parametrize?
@pytest.mark.pgsql(
    'cargo_corp',
    queries=[
        utils.get_client_create_request(),
        utils.get_candidate_create_request(
            corp_client_id=utils.CORP_CLIENT_ID,
            confirmation_code='code_with_reserved_phone',
            name='any_name',
            phone_pd_id='already_reserved_id',
            role_id=utils.ROLE_ID,
            email_pd_id='any_mail@ya.ru',
        ),
    ],
)
@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize('is_roles_config_enabled', (True, False))
async def test_internal_employee_candidate_upsert(
        make_employee_candidate_upsert_request,
        user_has_rights,
        stq,
        taxi_config,
        taxi_cargo_corp,
        is_roles_config_enabled,
):
    # 0. set config:
    taxi_config.set_values(
        {
            'CARGO_CORP_AVAILABLE_ROLE_IDS': {
                'enabled': is_roles_config_enabled,
                'b2b': [utils.ROLE_ID],
            },
        },
    )
    await taxi_cargo_corp.invalidate_caches()

    # 1. insert case:
    response_info = copy.deepcopy(CANDIDATES[0])
    request_info = {
        key: value
        for key, value in response_info.items()
        if key != 'role_name'
    }

    # 1a. idempotence
    for _ in range(2):
        response = await make_employee_candidate_upsert_request(
            request_json=request_info,
        )
        assert response.status_code == 200

    response_json = response.json()
    assert response_json['info'] == response_info
    assert response_json['revision'] == 1
    confirmation_code = response_json['confirmation_code']

    assert stq.cargo_corp_send_employee_invitation.times_called == 2
    stq_params = stq.cargo_corp_send_employee_invitation.next_call()
    _assert_stq_invitation_params(
        stq_params, confirmation_code, request_info['phone'], 'sms',
    )
    stq_params = stq.cargo_corp_send_employee_invitation.next_call()
    _assert_stq_invitation_params(
        stq_params,
        confirmation_code,
        request_info['email'],
        'email',
        request_info['phone'],
    )

    # 1b. create with same phone
    request_info['name'] += '_edited'
    response = await make_employee_candidate_upsert_request(
        request_json=request_info,
    )
    assert response.status_code == 409
    assert response.json() == {
        'code': 'conflict_by_phone',
        'message': CONFLICT_BY_PHONE_MSG,
        'details': {'conflicted_confirmation_code': confirmation_code},
    }

    # 2. update case
    update_request = {
        'confirmation_code': confirmation_code,
        'info': {**request_info},
        'revision': 1,
    }

    # 2a. idempotence
    for _ in range(2):
        response = await make_employee_candidate_upsert_request(
            request_json=update_request,
        )
    assert response.status_code == 200

    expected_ok_json = dict(update_request, **{'revision': 2})
    expected_ok_json['info']['role_name'] = response_info['role_name']
    assert response.json() == expected_ok_json

    assert not stq.cargo_corp_send_employee_invitation.has_calls

    # 2b. update with wrong revision
    update_request['info']['name'] += '_edited'
    response = await make_employee_candidate_upsert_request(
        request_json=update_request,
    )
    assert response.status_code == 409
    assert response.json()['code'] == 'not_actual_revision'

    # 2c. update with reserved phone
    update_request['revision'] = 2
    update_request['info']['phone']['number'] = 'already_reserved'
    response = await make_employee_candidate_upsert_request(
        request_json=update_request,
    )
    assert response.json() == {
        'code': 'conflict_by_phone',
        'message': CONFLICT_BY_PHONE_MSG,
        'details': {
            'conflicted_confirmation_code': 'code_with_reserved_phone',
        },
    }

    assert not stq.cargo_corp_send_employee_invitation.has_calls


@pytest.mark.parametrize(
    ('data_type', 'expected_response'),
    (
        pytest.param(
            'phones', {'code': 'invalid_phone', 'message': 'Invalid phone'},
        ),
        pytest.param(
            'emails', {'code': 'invalid_email', 'message': 'Invalid email'},
        ),
    ),
)
async def test_internal_employee_candidate_upsert_invalid_data(
        make_employee_candidate_upsert_request,
        mockserver,
        data_type,
        expected_response,
):
    @mockserver.json_handler(f'/personal/v1/{data_type}/store')
    def _retireve(request):
        resp = {'code': '400', 'message': 'invalid data'}
        return mockserver.make_response(status=400, json=resp)

    response = await make_employee_candidate_upsert_request(
        request_json=CANDIDATES[0],
    )

    assert response.status_code == 400
    assert response.json() == expected_response


@pytest.mark.config(CARGO_CORP_AVAILABLE_ROLE_IDS={'enabled': True, 'b2b': []})
async def test_employee_candidate_upsert_unavailable_role(
        make_employee_candidate_upsert_request, user_has_rights,
):
    response = await make_employee_candidate_upsert_request(
        request_json=CANDIDATES[0],
    )
    assert response.status_code == 400
    assert response.json()['code'] == 'wrong_role_id'


@pytest.mark.pgsql(
    'cargo_corp',
    queries=[
        utils.get_client_create_request(),
        utils.get_candidate_create_request(
            corp_client_id=utils.CORP_CLIENT_ID,
            confirmation_code=CANDIDATE_CONFIRMATION_CODES[0],
            name=CANDIDATES[0]['name'],
            phone_pd_id=f'{CANDIDATE_PHONES[0]["number"]}_id1',
            role_id=utils.ROLE_ID,
            email_pd_id=f'{CANDIDATE_EMAILS[0]}_id2',
            revision=1,
        ),
        utils.get_candidate_create_request(
            corp_client_id=utils.CORP_CLIENT_ID,
            confirmation_code=CANDIDATE_CONFIRMATION_CODES[1],
            name=CANDIDATES[0]['name'],
            phone_pd_id=f'{CANDIDATE_PHONES[0]["number"]}_id2',
            role_id=utils.ROLE_ID,
            email_pd_id=f'{CANDIDATE_EMAILS[0]}_id2',
            revision=2,
        ),
    ],
)
@pytest.mark.parametrize(
    'confirmation_code, version_to_remove, expected_code',
    (
        pytest.param(CANDIDATE_CONFIRMATION_CODES[0], 1, 200),
        pytest.param(CANDIDATE_CONFIRMATION_CODES[1], 2, 200),
        pytest.param(CANDIDATE_CONFIRMATION_CODES[1], 1, 409),
        pytest.param(CANDIDATE_CONFIRMATION_CODES[2], 1, 200),
    ),
)
async def test_employee_candidate_remove(
        taxi_cargo_corp,
        get_employee_candidate_info,
        confirmation_code,
        version_to_remove,
        expected_code,
):
    response = await taxi_cargo_corp.post(
        'v1/client/employee-candidate/remove',
        headers={
            'X-B2B-Client-Id': utils.CORP_CLIENT_ID,
            'X-Yandex-Uid': utils.YANDEX_UID,
        },
        json={
            'confirmation_code': confirmation_code,
            'revision': version_to_remove,
        },
    )
    assert response.status_code == expected_code

    if expected_code == 200:
        candidate = get_employee_candidate_info(
            confirmation_code, utils.CORP_CLIENT_ID,
        )
        assert not candidate


@pytest.mark.pgsql(
    'cargo_corp',
    queries=[
        utils.get_client_create_request(),
        utils.get_client_create_request(
            corp_client_id=LOCAL_CORP_CLIENT_ID,
            corp_client_name='local_corp_client_name',
        ),
        utils.get_candidate_create_request(
            corp_client_id=utils.CORP_CLIENT_ID,
            confirmation_code=CANDIDATE_CONFIRMATION_CODES[0],
            name=CANDIDATES[0]['name'],
            phone_pd_id=f'{CANDIDATE_PHONES[0]["number"]}_id',
            role_id=utils.ROLE_ID,
            email_pd_id=f'{CANDIDATE_EMAILS[0]}_id',
        ),
        utils.get_candidate_create_request(
            corp_client_id=utils.CORP_CLIENT_ID,
            confirmation_code=CANDIDATE_CONFIRMATION_CODES[1],
            name=CANDIDATES[1]['name'],
            phone_pd_id=f'{CANDIDATE_PHONES[1]["number"]}_id',
            role_id=utils.ROLE_ID,
            email_pd_id=f'{CANDIDATE_EMAILS[1]}_id',
        ),
        utils.get_candidate_create_request(
            corp_client_id=LOCAL_CORP_CLIENT_ID,
            confirmation_code=CANDIDATE_CONFIRMATION_CODES[2],
            name=CANDIDATES[2]['name'],
            phone_pd_id=f'{CANDIDATE_PHONES[2]["number"]}_id',
            role_id=utils.ROLE_ID,
            email_pd_id=f'{CANDIDATE_EMAILS[2]}_id',
        ),
    ],
)
@pytest.mark.parametrize(
    (
        'corp_client_id',
        'candidate_phone',
        'confirmation_code',
        'candidate_email',
        'name',
        'expected_json',
        'expected_code',
    ),
    (
        pytest.param(
            utils.CORP_CLIENT_ID,
            None,
            None,
            None,
            None,
            {
                'candidates': [
                    {
                        'confirmation_code': CANDIDATE_CONFIRMATION_CODES[i],
                        'info': CANDIDATES[i],
                        'revision': 1,
                    }
                    for i in range(2)
                ],
            },
            200,
            id='ok-no filters-1',
        ),
        pytest.param(
            LOCAL_CORP_CLIENT_ID,
            None,
            None,
            None,
            None,
            {
                'candidates': [
                    {
                        'confirmation_code': CANDIDATE_CONFIRMATION_CODES[2],
                        'info': CANDIDATES[2],
                        'revision': 1,
                    },
                ],
            },
            200,
            id='ok-no filters-2',
        ),
        pytest.param(
            utils.CORP_CLIENT_ID,
            CANDIDATE_PHONES[0]['number'],
            None,
            None,
            None,
            {
                'candidates': [
                    {
                        'confirmation_code': CANDIDATE_CONFIRMATION_CODES[0],
                        'info': CANDIDATES[0],
                        'revision': 1,
                    },
                ],
            },
            200,
            id='ok-phone filter',
        ),
        pytest.param(
            utils.CORP_CLIENT_ID,
            None,
            CANDIDATE_CONFIRMATION_CODES[0],
            None,
            None,
            {
                'candidates': [
                    {
                        'confirmation_code': CANDIDATE_CONFIRMATION_CODES[0],
                        'info': CANDIDATES[0],
                        'revision': 1,
                    },
                ],
            },
            200,
            id='ok-confirmation code filter',
        ),
        pytest.param(
            utils.CORP_CLIENT_ID,
            CANDIDATE_PHONES[0]['number'],
            CANDIDATE_CONFIRMATION_CODES[0],
            None,
            None,
            {
                'candidates': [
                    {
                        'confirmation_code': CANDIDATE_CONFIRMATION_CODES[0],
                        'info': CANDIDATES[0],
                        'revision': 1,
                    },
                ],
            },
            200,
            id='ok-phone and confirmation code filters',
        ),
        pytest.param(
            utils.CORP_CLIENT_ID,
            None,
            None,
            CANDIDATE_EMAILS[0],
            None,
            {
                'candidates': [
                    {
                        'confirmation_code': CANDIDATE_CONFIRMATION_CODES[0],
                        'info': CANDIDATES[0],
                        'revision': 1,
                    },
                ],
            },
            200,
            id='ok-email filter',
        ),
        pytest.param(
            utils.CORP_CLIENT_ID,
            None,
            None,
            None,
            CANDIDATES[1]['name'],
            {
                'candidates': [
                    {
                        'confirmation_code': CANDIDATE_CONFIRMATION_CODES[1],
                        'info': CANDIDATES[1],
                        'revision': 1,
                    },
                ],
            },
            200,
            id='ok-name filter-1',
        ),
        pytest.param(
            utils.CORP_CLIENT_ID,
            None,
            None,
            None,
            CANDIDATES[0]['name'],
            {
                'candidates': [
                    {
                        'confirmation_code': CANDIDATE_CONFIRMATION_CODES[i],
                        'info': CANDIDATES[i],
                        'revision': 1,
                    }
                    for i in range(2)
                ],
            },
            200,
            id='ok-name filter-2',
        ),
        pytest.param(
            utils.CORP_CLIENT_ID,
            CANDIDATE_PHONES[0]['number'],
            CANDIDATE_CONFIRMATION_CODES[0],
            CANDIDATE_EMAILS[0],
            CANDIDATES[0]['name'],
            {
                'candidates': [
                    {
                        'confirmation_code': CANDIDATE_CONFIRMATION_CODES[0],
                        'info': CANDIDATES[0],
                        'revision': 1,
                    },
                ],
            },
            200,
            id='ok-all filters',
        ),
        pytest.param(
            utils.CORP_CLIENT_ID,
            CANDIDATE_PHONES[2]['number'],
            None,
            None,
            None,
            {'candidates': []},
            200,
            id='ok-wrong phone filter',
        ),
        pytest.param(
            utils.CORP_CLIENT_ID,
            None,
            CANDIDATE_CONFIRMATION_CODES[2],
            None,
            None,
            {'candidates': []},
            200,
            id='ok-wrong confirmation code filter',
        ),
        pytest.param(
            utils.CORP_CLIENT_ID[::-1],
            None,
            None,
            None,
            None,
            {'code': 'not_found', 'message': 'Unknown corp_client'},
            404,
            id='bad-wrong corp_client_id',
        ),
        pytest.param(
            utils.CORP_CLIENT_ID,
            '1111111111',
            None,
            None,
            None,
            {'candidates': []},
            200,
            id='ok-phone does not exist',
        ),
    ),
)
async def test_employee_candidate_list(
        taxi_cargo_corp,
        user_has_rights,
        mockserver,
        corp_client_id,
        candidate_phone,
        confirmation_code,
        candidate_email,
        name,
        expected_json,
        expected_code,
):
    @mockserver.json_handler('/personal/v1/phones/find')
    def _phones_store(request):
        assert request.json.keys() == {'value', 'primary_replica'}
        phone = request.json['value']
        if phone in [p['number'] for p in CANDIDATE_PHONES]:
            return {'id': phone + '_id', 'value': phone}
        return mockserver.make_response(
            status=404,
            json={'code': '404', 'message': 'Doc not found in mongo'},
        )

    @mockserver.json_handler('/personal/v1/emails/find')
    def _emails_store(request):
        assert request.json.keys() == {'value', 'primary_replica'}
        email = request.json['value']
        if email in CANDIDATE_EMAILS:
            return {'id': email + '_id', 'value': email}
        return mockserver.make_response(
            status=404,
            json={'code': '404', 'message': 'Doc not found in mongo'},
        )

    query = {}
    if confirmation_code:
        query['confirmation_code'] = confirmation_code
    if candidate_phone:
        query['candidate_phone'] = candidate_phone
    if candidate_email:
        query['candidate_email'] = candidate_email
    if name:
        query['name'] = name

    response = await taxi_cargo_corp.get(
        '/internal/cargo-corp/v1/client/employee-candidate/list',
        headers={
            'X-Yandex-Uid': YANDEX_UID,
            'X-B2B-Client-Id': corp_client_id,
        },
        params=query,
    )
    assert response.status_code == expected_code
    response_json = response.json()
    if expected_code == 200:
        response_json['candidates'].sort(key=lambda x: x['confirmation_code'])
    assert response_json == expected_json


@pytest.mark.pgsql(
    'cargo_corp',
    queries=[
        utils.get_client_create_request(),
        utils.get_role_create_request(
            role_name=ANOTHER_ROLE_NAME, role_id=ANOTHER_ROLE_ID,
        ),
        utils.get_candidate_create_request(
            corp_client_id=utils.CORP_CLIENT_ID,
            confirmation_code=CANDIDATE_CONFIRMATION_CODES[0],
            name=CANDIDATES[0]['name'],
            phone_pd_id=f'{CANDIDATE_PHONES[0]["number"]}_id',
            role_id=utils.ROLE_ID,
            email_pd_id=f'{CANDIDATE_EMAILS[0]}_id',
        ),
        utils.get_candidate_create_request(
            corp_client_id=utils.CORP_CLIENT_ID,
            confirmation_code=CANDIDATE_CONFIRMATION_CODES[1],
            name=CANDIDATES[1]['name'],
            phone_pd_id=f'{CANDIDATE_PHONES[1]["number"]}_id',
            role_id=ANOTHER_ROLE_ID,
            email_pd_id=f'{CANDIDATE_EMAILS[1]}_id',
        ),
    ],
)
async def test_list_role_filter(taxi_cargo_corp, mockserver):
    @mockserver.json_handler('/personal/v1/phones/find')
    def _phones_store(request):
        assert request.json.keys() == {'value', 'primary_replica'}
        phone = request.json['value']
        if phone in [p['number'] for p in CANDIDATE_PHONES]:
            return {'id': phone + '_id', 'value': phone}
        return mockserver.make_response(
            status=404,
            json={'code': '404', 'message': 'Doc not found in mongo'},
        )

    response = await taxi_cargo_corp.get(
        '/internal/cargo-corp/v1/client/employee-candidate/list',
        headers={
            'X-Yandex-Uid': YANDEX_UID,
            'X-B2B-Client-Id': utils.CORP_CLIENT_ID,
        },
        params={'role_id': ANOTHER_ROLE_ID},
    )
    assert response.status_code == 200
    expected_info = CANDIDATES[1].copy()
    expected_info.update(role_id=ANOTHER_ROLE_ID, role_name=ANOTHER_ROLE_NAME)
    assert response.json()['candidates'] == [
        {
            'confirmation_code': CANDIDATE_CONFIRMATION_CODES[1],
            'info': expected_info,
            'revision': 1,
        },
    ]


# TODO (dipterix): split into files, move consts to const.py
@pytest.mark.pgsql(
    'cargo_corp',
    queries=[
        utils.get_client_create_request(),
        utils.get_role_create_request(
            role_name=utils.OWNER_ROLE,
            role_id=utils.OWNER_ROLE,
            corp_client_id='',
        ),
        utils.get_role_create_request(
            role_name='system:robot',
            role_id='system:robot',
            corp_client_id='',
        ),
        utils.get_role_create_request(
            role_name=ANOTHER_ROLE_NAME, role_id=ANOTHER_ROLE_ID,
        ),
        utils.get_role_create_request(  # NOT A GENERAL ROLE!!!
            role_name=utils.OWNER_ROLE, role_id='not_general_id',
        ),
        utils.get_role_create_request(role_name='МЫШ', role_id='abcdefg'),
        utils.get_candidate_create_request(
            corp_client_id=utils.CORP_CLIENT_ID,
            confirmation_code='0',
            name=CANDIDATES[0]['name'],
            phone_pd_id=f'{CANDIDATE_PHONES[0]["number"]}_id',
            role_id=utils.ROLE_ID,
            email_pd_id=f'{"test1@ya.ru"}_id',
        ),
        utils.get_candidate_create_request(
            corp_client_id=utils.CORP_CLIENT_ID,
            confirmation_code='1',
            name=CANDIDATES[0]['name'],
            phone_pd_id=f'{CANDIDATE_PHONES[1]["number"]}_id',
            role_id=utils.OWNER_ROLE,
            email_pd_id=f'{"test1@ya.ru"}_id',
        ),
        utils.get_candidate_create_request(
            corp_client_id=utils.CORP_CLIENT_ID,
            confirmation_code='2',
            name=CANDIDATES[0]['name'],
            phone_pd_id=f'{CANDIDATE_PHONES[2]["number"]}_id',
            role_id='system:robot',
            email_pd_id=f'{"test1@ya.ru"}_id',
        ),
        utils.get_candidate_create_request(
            corp_client_id=utils.CORP_CLIENT_ID,
            confirmation_code='3',
            name=CANDIDATES[0]['name'],
            phone_pd_id=f'{CANDIDATE_PHONES[3]["number"]}_id',
            role_id=ANOTHER_ROLE_ID,
            email_pd_id=f'{"test1@ya.ru"}_id',
        ),
        utils.get_candidate_create_request(
            corp_client_id=utils.CORP_CLIENT_ID,
            confirmation_code='4',
            name=CANDIDATES[0]['name'],
            phone_pd_id=f'{CANDIDATE_PHONES[4]["number"]}_id',
            role_id='not_general_id',
            email_pd_id=f'{"test1@ya.ru"}_id',
        ),
        utils.get_candidate_create_request(
            corp_client_id=utils.CORP_CLIENT_ID,
            confirmation_code='5',
            name=CANDIDATES[0]['name'],
            phone_pd_id=f'{CANDIDATE_PHONES[5]["number"]}_id',
            role_id='abcdefg',
            email_pd_id=f'{"test1@ya.ru"}_id',
        ),
    ],
)
async def test_list_translations(taxi_cargo_corp, user_has_rights, mockserver):
    response = await taxi_cargo_corp.get(
        '/internal/cargo-corp/v1/client/employee-candidate/list',
        headers={
            'X-Yandex-Uid': YANDEX_UID,
            'X-B2B-Client-Id': utils.CORP_CLIENT_ID,
        },
    )
    assert response.status_code == 200

    def get_info(role_id, role_name, phone):
        info = CANDIDATES[0].copy()
        info.update(role_id=role_id, role_name=role_name, phone=phone)
        return info

    assert (
        sorted(
            response.json()['candidates'],
            key=lambda info: info['confirmation_code'],
        )
        == [
            {
                'confirmation_code': '0',
                'info': get_info(
                    utils.ROLE_ID,
                    utils.OWNER_ROLE_TRANSLATION,
                    CANDIDATE_PHONES[0],
                ),
                'revision': 1,
            },
            {
                'confirmation_code': '1',
                'info': get_info(
                    utils.OWNER_ROLE,
                    utils.OWNER_ROLE_TRANSLATION,
                    CANDIDATE_PHONES[1],
                ),
                'revision': 1,
            },
            {
                'confirmation_code': '2',
                'info': get_info('system:robot', 'Robot', CANDIDATE_PHONES[2]),
                'revision': 1,
            },
            {
                'confirmation_code': '3',
                'info': get_info(
                    ANOTHER_ROLE_ID, ANOTHER_ROLE_NAME, CANDIDATE_PHONES[3],
                ),
                'revision': 1,
            },
            {
                'confirmation_code': '4',
                'info': get_info(
                    'not_general_id',
                    utils.OWNER_ROLE,  # should not be translated
                    CANDIDATE_PHONES[4],
                ),
                'revision': 1,
            },
            {
                'confirmation_code': '5',
                'info': get_info('abcdefg', 'МЫШ', CANDIDATE_PHONES[5]),
                'revision': 1,
            },
        ]
    )
