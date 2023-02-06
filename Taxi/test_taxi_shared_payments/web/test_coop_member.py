# flake8: noqa
# pylint: disable=too-many-lines
import datetime

import pytest

from taxi_shared_payments.repositories import accounts as accounts_repo
from taxi_shared_payments.repositories import members as members_repo
from taxi_shared_payments.repositories import users as users_repo
from taxi_shared_payments.repositories import attempt_counters as attempts_repo
from test_taxi_shared_payments.conftest import DEFAULT_HEADERS

MOCK_ID = 'uuid4'
MOCK_UID = 'user1'
MOCK_USER_ID = '_id1'

UID_HEADER = 'X-Yandex-UID'
PHONE_ID_HEADER = 'X-YaTaxi-PhoneId'

PASSPORT_FAMILY_ID = 'acc_with_passport_family'
PHONISH_MEMBER_UID = 'phonish_member_uid'
PHONISH_MEMBER_UID_WITHOUT_PORTAL = 'user4'
PHONISH_MEMBER_PHONE_ID = '00aaaaaaaaaaaaaaaaaaaa10'


@pytest.mark.parametrize(
    'params, body, expected_status, expected_response',
    [
        pytest.param(
            {'revision': '1234', 'account_id': 'acc1'},
            {
                'details': {
                    'nickname': 'Иванов младший',
                    'phone': '89876541234',
                },
                'limits': {
                    'amount': 1000,
                    'has_specific_limit': False,
                    'classes': ['econom'],
                },
            },
            200,
            {'id': 'uuid4', 'revision': '1234'},
            id='all_fields_ok',
        ),
        pytest.param(
            {'revision': '1234', 'account_id': 'acc1'},
            {
                'details': {
                    'nickname': 'Иванов младший',
                    'phone': '89876541234',
                },
                'limits': {
                    'amount': 1000,
                    'has_specific_limit': True,
                    'classes': ['econom'],
                },
            },
            200,
            {
                'id': 'uuid4',
                'limits': {'amount': 1000, 'has_specific_limit': True},
                'revision': '1234',
            },
            marks=[
                pytest.mark.config(
                    COOP_ACCOUNT_SETTINGS=[
                        {'type': 'family', 'set_limits': True},
                    ],
                ),
            ],
            id='all_fields_ok_enable_limits',
        ),
        pytest.param(
            {'revision': '1234', 'account_id': 'acc1'},
            {
                'details': {
                    'nickname': 'Estonian user',
                    'phone': '3720000000',
                },
                'limits': {
                    'amount': 1000,
                    'has_specific_limit': False,
                    'classes': ['econom'],
                },
            },
            200,
            {'id': 'uuid4', 'revision': '1234'},
            id='intl_phone',
        ),
        pytest.param(
            {'revision': '1234', 'account_id': 'acc1'},
            {
                'details': {'nickname': 'Иванов младший', 'phone': '000'},
                'limits': {
                    'amount': 1000,
                    'has_specific_limit': False,
                    'classes': ['econom'],
                },
            },
            400,
            {
                'code': 'UNREGISTERED_PHONE',
                'message': 'У этого человека нет ЯТакси',
                'details': {
                    'sharing_text': [
                        'Я хочу добавить тебя в семейный аккаунт',
                    ],
                },
            },
            id='invalid_phone_family',
        ),
        pytest.param(
            {'revision': '1234', 'account_id': 'acc1'},
            {
                'details': {
                    'nickname': 'Иванов младший',
                    'phone': '+70000000000',
                },
                'limits': {
                    'amount': 1000,
                    'has_specific_limit': False,
                    'classes': ['econom'],
                },
            },
            400,
            {
                'code': 'UNREGISTERED_PHONE',
                'message': 'У этого человека нет ЯТакси',
                'details': {
                    'sharing_text': [
                        'Я хочу добавить тебя в семейный аккаунт',
                    ],
                },
            },
            id='nonexistent_phone_family',
        ),
        pytest.param(
            {'revision': '1234', 'account_id': 'acc_business'},
            {
                'details': {'nickname': 'Иванов младший', 'phone': '000'},
                'limits': {
                    'amount': 1000,
                    'has_specific_limit': False,
                    'classes': ['econom'],
                },
            },
            400,
            {
                'code': 'UNREGISTERED_PHONE',
                'message': 'У этого человека нет ЯТакси',
                'details': {
                    'sharing_text': ['Я хочу добавить тебя в бизнес аккаунт'],
                },
            },
            id='bad_phone_business',
        ),
        pytest.param(
            {'revision': '1234', 'account_id': 'acc403'},
            {
                'details': {
                    'nickname': 'Иванов младший',
                    'phone': '+79876541234',
                },
                'limits': {
                    'amount': 1000,
                    'has_specific_limit': False,
                    'classes': ['econom'],
                },
            },
            403,
            {
                'code': 'GENERAL',
                'message': '',
                'system_message': 'yandex_uid does not match owner_id',
                'details': {},
            },
            id='wrong_account',
        ),
        pytest.param(
            {'revision': '1234', 'account_id': 'acc404'},
            {
                'details': {
                    'nickname': 'Иванов младший',
                    'phone': '+79876541234',
                },
                'limits': {
                    'amount': 1000,
                    'has_specific_limit': False,
                    'classes': ['econom'],
                },
            },
            404,
            {
                'code': 'GENERAL',
                'message': '',
                'system_message': 'account with id acc404 does not exist',
                'details': {},
            },
            id='nonexistent_account',
        ),
        pytest.param(
            {'revision': '1234', 'account_id': 'acc1'},
            None,
            400,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {'reason': 'body is required'},
                'message': 'Some parameters are invalid',
            },
            id='empty_body',
        ),
        pytest.param(
            {'revision': '1234', 'account_id': 'acc1'},
            {'details': {}, 'limits': {'amount': '1000', 'classes': 'econom'}},
            400,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {'reason': 'nickname is required property'},
                'message': 'Some parameters are invalid',
            },
            id='wrong fields',
        ),
        pytest.param(
            {'revision': '1234', 'account_id': 'acc1'},
            {
                'details': {'nickname': '', 'phone': '3720000000'},
                'limits': {
                    'amount': 1000,
                    'has_specific_limit': False,
                    'classes': ['econom'],
                },
            },
            400,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {},
                'message': 'Введите имя участника',
            },
            id='empty_nickname',
        ),
        pytest.param(
            {'revision': '1234', 'account_id': 'acc2'},
            {
                'details': {
                    'nickname': 'Artemy too much',
                    'phone': '89876541235',
                },
            },
            409,
            {
                'code': 'GENERAL',
                'message': 'Слишком много участников',
                'details': {},
            },
            id='too_many_members',
        ),
        pytest.param(
            {'revision': '1234', 'account_id': 'acc1'},
            {
                'details': {
                    'nickname': 'Иванов младший',
                    'phone': '89876541234',
                },
                'limits': {
                    'amount': 1000,
                    'has_specific_limit': False,
                    'classes': ['econom'],
                },
            },
            400,
            {
                'code': 'GENERAL',
                'message': '',
                'system_message': 'many members per account',
                'details': {},
            },
            marks=pytest.mark.config(
                ANTIFRAUD_MEMBERS={'family': 4, 'business': 0},
            ),
            id='antifraud',
        ),
        pytest.param(
            {'revision': '1234', 'account_id': '18'},
            {
                'details': {
                    'nickname': 'Иванов младший',
                    'phone': '89876541234',
                },
            },
            200,
            {
                'id': 'uuid4',
                'revision': '1234',
                'limits': {'has_specific_limit': True, 'amount': 5000},
            },
            id='account_with_limit',
        ),
        pytest.param(
            {'revision': '1234', 'account_id': 'acc5'},
            {'details': {'nickname': 'Гимли', 'phone': '89876541234'}},
            400,
            {
                'code': 'GENERAL',
                'message': '',
                'system_message': 'many members per account',
                'details': {},
            },
            marks=pytest.mark.config(COOP_ACCOUNT_MAX_ADD_MEMBER_ATTEMPTS=25),
            id='attempts_antifraud',
        ),
    ],
)
@pytest.mark.translations(
    client_messages={
        'shared_payments.empty_nickname_error': {
            'ru': 'Введите имя участника',
        },
        'shared_payments.too_many_members_error': {
            'ru': 'Слишком много участников',
        },
        'shared_payments.no_phone_id_error': {
            'ru': 'У этого человека нет ЯТакси',
        },
        'shared_payments.share_family_text': {
            'ru': 'Я хочу добавить тебя в семейный аккаунт',
        },
        'shared_payments.share_business_text': {
            'ru': 'Я хочу добавить тебя в бизнес аккаунт',
        },
        'shared_payments.share_family_text_yataxi': {
            'ru': 'Я хочу добавить тебя в семейный аккаунт Яндекс',
        },
        'shared_payments.share_business_text_yataxi': {
            'ru': 'Я хочу добавить тебя в бизнес аккаунт Яндекс',
        },
    },
)
@pytest.mark.config(
    COOP_ACCOUNT_TYPES=[
        {'member_max_count': 4, 'account_max_count': 1, 'type': 'family'},
        {'member_max_count': 20, 'account_max_count': 1, 'type': 'business'},
    ],
    COOP_ACCOUNT_SHARING_TEXT={
        'default': {
            'family': 'shared_payments.share_family_text',
            'business': 'shared_payments.share_business_text',
        },
        'yataxi': {
            'family': 'shared_payments.share_family_text_yataxi',
            'business': 'shared_payments.share_business_text_yataxi',
        },
    },
    ANTIFRAUD_DAYS_AFTER_CREATE={'created_accounts': 1, 'created_members': 1},
    USER_API_USE_USER_PHONES_RETRIEVAL_PY3=True,
)
@pytest.mark.now('2018-01-01T12:08:12')
async def test_coop_member_create(
        web_app_client,
        web_context,
        mock_all_api,
        monkeypatch,
        params,
        body,
        expected_status,
        expected_response,
):
    monkeypatch.setattr('uuid.UUID.hex', MOCK_ID)
    response = await web_app_client.post(
        '/4.0/coop_account/member/create',
        json=body,
        headers={**DEFAULT_HEADERS, UID_HEADER: MOCK_UID},
        params=params,
    )

    content = await response.json()
    assert response.status == expected_status, content
    assert content == expected_response


@pytest.mark.parametrize(
    'account_id, expected_status, expected_attempts',
    [
        pytest.param('acc6', 200, 1, id='no account counter created yet'),
        pytest.param('acc7', 200, 1, id='many attempts many time ago'),
        pytest.param('acc8', 200, 25, id='25 attempts ok'),
        pytest.param('acc5', 400, 26, id='26 attempts not ok'),
        pytest.param('acc1', 200, 0, id='family not affecting'),
        pytest.param('acc9', 400, 31, id='<7 days not ok'),
    ],
)
@pytest.mark.config(
    COOP_ACCOUNT_TYPES=[
        {'member_max_count': 4, 'account_max_count': 1, 'type': 'family'},
        {'member_max_count': 20, 'account_max_count': 1, 'type': 'business'},
    ],
    COOP_ACCOUNT_SHARING_TEXT={
        'default': {
            'family': 'shared_payments.share_family_text',
            'business': 'shared_payments.share_business_text',
        },
        'yataxi': {
            'family': 'shared_payments.share_family_text_yataxi',
            'business': 'shared_payments.share_business_text_yataxi',
        },
    },
    ANTIFRAUD_DAYS_AFTER_CREATE={'created_accounts': 1, 'created_members': 1},
    USER_API_USE_USER_PHONES_RETRIEVAL_PY3=True,
    COOP_ACCOUNT_MAX_ADD_MEMBER_ATTEMPTS=25,
)
@pytest.mark.now('2022-06-03T13:16:00')
async def test_coop_member_create_antifraud(
        web_app_client,
        web_context,
        mock_all_api,
        monkeypatch,
        account_id,
        expected_status,
        expected_attempts,
):
    monkeypatch.setattr('uuid.UUID.hex', MOCK_ID)
    params = {'revision': '1234', 'account_id': account_id}
    # some random name and registered phone
    body = {
        'details': {'nickname': 'Гимли', 'phone': '89876541234'},
        'limits': {
            'amount': 1000,
            'has_specific_limit': False,
            'classes': ['econom'],
        },
    }
    response = await web_app_client.post(
        '/4.0/coop_account/member/create',
        json=body,
        headers={**DEFAULT_HEADERS, UID_HEADER: MOCK_UID},
        params=params,
    )

    content = await response.json()
    assert response.status == expected_status, content
    account_attempts = 0
    try:
        attempt_counter = await attempts_repo.get(
            web_context, account_id=account_id,
        )
        account_attempts = attempt_counter.attempt_count
    except attempts_repo.CounterDoesNotExist:
        pass
    assert account_attempts == expected_attempts


@pytest.mark.parametrize(
    'params, body, expected_status, expected_response',
    [
        pytest.param(
            {'id': 'memb2', 'revision': 'revision3'},
            {
                'details': {
                    'nickname': 'Роман Александрович',
                    'phone': '+79876541234',
                },
                'limits': {
                    'has_specific_limit': True,
                    'amount': 1000,
                    'classes': ['econom'],
                },
            },
            200,
            {'revision': MOCK_ID},
            id='ok',
        ),
        pytest.param(
            {'id': 'memb1', 'revision': 'revision0'},
            {
                'details': {
                    'nickname': 'Роман Александрович',
                    'phone': '+79876541234',
                },
            },
            400,
            {
                'code': 'GENERAL',
                'message': '',
                'system_message': 'cannot change owner',
                'details': {},
            },
            id='owner',
        ),
        pytest.param(
            {'id': 'memb2', 'revision': '1234'},
            {
                'details': {
                    'nickname': 'Роман Александрович',
                    'phone': '+79876541234',
                },
                'limits': {
                    'has_specific_limit': True,
                    'amount': 1000,
                    'classes': ['econom'],
                },
            },
            409,
            {
                'code': 'GENERAL',
                'message': '',
                'system_message': 'revision id does not match',
                'details': {},
            },
            id='wrong_revision',
        ),
        pytest.param(
            {'id': 'memb2', 'revision': '1234'},
            {
                'details': {
                    'nickname': 'Sidorov Jr.',
                    'phone': '+71111111112',
                },
                'limits': {'has_specific_limit': True, 'amount': None},
            },
            200,
            {'revision': 'revision3'},
            id='no_change_wrong_revision',
        ),
        pytest.param(
            {'id': 'memb1', 'revision': '1234'},
            {},
            400,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {'reason': 'details is required property'},
                'message': 'Some parameters are invalid',
            },
            id='empty_body',
        ),
        pytest.param(
            {'id': 'memb1'},
            {
                'details': {
                    'nickname': 'Роман Александрович',
                    'phone': '+79876541234',
                },
            },
            400,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {'reason': 'revision is required parameter'},
                'message': 'Some parameters are invalid',
            },
            id='no_revision',
        ),
        pytest.param(
            {},
            {
                'details': {
                    'nickname': 'Роман Александрович',
                    'phone': '+79876541234',
                },
            },
            400,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {'reason': 'revision is required parameter'},
                'message': 'Some parameters are invalid',
            },
            id='no_query',
        ),
    ],
)
@pytest.mark.translations(
    client_messages={
        'shared_payments.share_family_text': {
            'ru': 'Я хочу добавить тебя в семейный аккаунт',
        },
        'shared_payments.no_phone_id_error': {
            'ru': 'У этого человека нет ЯТакси',
        },
    },
)
@pytest.mark.config(
    COOP_ACCOUNT_SETTINGS=[{'type': 'family', 'set_limits': True}],
    USER_API_USE_USER_PHONES_RETRIEVAL_PY3=True,
)
async def test_coop_member_update_details(
        web_app_client,
        web_context,
        mock_all_api,
        monkeypatch,
        params,
        body,
        expected_status,
        expected_response,
):
    monkeypatch.setattr('uuid.UUID.hex', MOCK_ID)
    response = await web_app_client.put(
        f'/4.0/coop_account/member/details',
        json=body,
        headers={**DEFAULT_HEADERS, UID_HEADER: MOCK_UID},
        params=params,
    )
    content = await response.json()
    assert response.status == expected_status, content
    assert content == expected_response
    if expected_status == 200:
        cur_member = await members_repo.get_one_by_id(
            web_context, params['id'],
        )
        assert cur_member.nickname == body['details']['nickname']
        if 'limits' not in body:
            return

        limits = body['limits']
        if 'has_specific_limit' in limits:
            assert (
                cur_member.has_specific_limit == limits['has_specific_limit']
            )
        if 'amount' in limits:
            if cur_member.limit_amount is None:
                assert limits['amount'] is None
            else:
                assert cur_member.limit_amount == limits['amount'] * 10000

        members = await members_repo.get_members(
            web_context, cur_member.account_id, is_deleted=True,
        )
        for member in members:
            if not member.is_active:
                assert member.deleted_at


@pytest.mark.translations(
    client_messages={
        'shared_payments.found_active_order_error_member': {
            'ru': 'Имеются активные поездки',
        },
    },
)
@pytest.mark.parametrize(
    'urls, expected_status, expected_response',
    [
        pytest.param(
            ['/4.0/coop_account/member/delete?id=memb2'], 200, {}, id='ok',
        ),
        pytest.param(
            [
                '/4.0/coop_account/member/delete?id=memb2',
                '/4.0/coop_account/member/delete?id=memb2',
            ],
            200,
            {},
            id='double_delete_ok',
        ),
        pytest.param(
            ['/4.0/coop_account/member/delete?id=memb1'],
            403,
            {
                'code': 'GENERAL',
                'message': '',
                'system_message': 'account owner cannot remove himself',
                'details': {},
            },
            id='owner_self_removal',
        ),
        pytest.param(
            ['/4.0/coop_account/member/delete'],
            400,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'message': 'Some parameters are invalid',
                'details': {'reason': 'id is required parameter'},
            },
            id='no_query',
        ),
        pytest.param(
            ['/4.0/coop_account/member/delete?id=memb404'],
            404,
            {
                'code': 'GENERAL',
                'message': '',
                'system_message': 'member member_id=memb404 does not exist',
                'details': {},
            },
            id='nonexistent_member',
        ),
        pytest.param(
            ['/4.0/coop_account/member/delete?id=memb403'],
            403,
            {
                'code': 'GENERAL',
                'message': '',
                'system_message': 'yandex_uid does not match owner_id',
                'details': {},
            },
            id='wrong_member',
        ),
    ],
)
async def test_coop_member_delete(
        web_app_client, urls, expected_status, expected_response,
):
    for url in urls:
        response = await web_app_client.delete(
            url, headers={**DEFAULT_HEADERS, UID_HEADER: MOCK_UID},
        )
    content = await response.json()
    assert response.status == expected_status, content
    assert content == expected_response


@pytest.mark.translations(
    client_messages={
        'shared_payments.found_active_order_error_member_itself': {
            'ru': 'Имеются активные поездки',
        },
    },
)
@pytest.mark.parametrize(
    'url, expected_status, expected_response',
    [
        pytest.param(
            '/4.0/coop_account/member/leave_group?id=acc3', 200, {}, id='ok',
        ),
        pytest.param(
            '/4.0/coop_account/member/leave_group?id=acc1',
            403,
            {
                'code': 'GENERAL',
                'message': '',
                'system_message': 'account owner cannot remove himself',
                'details': {},
            },
            id='owner_self_removal',
        ),
        pytest.param(
            '/4.0/coop_account/member/leave_group',
            400,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {'reason': 'id is required parameter'},
                'message': 'Some parameters are invalid',
            },
            id='no_query',
        ),
        pytest.param(
            '/4.0/coop_account/member/leave_group?id=acc404',
            404,
            {
                'code': 'GENERAL',
                'message': '',
                'system_message': (
                    'member account_id=acc404, '
                    'phone_id=00aaaaaaaaaaaaaaaaaaaa01 '
                    'does not exist'
                ),
                'details': {},
            },
            id='nonexistent_member',
        ),
    ],
)
async def test_coop_member_leave(
        web_app_client, mock_user_api, url, expected_status, expected_response,
):
    response = await web_app_client.delete(
        url, headers={**DEFAULT_HEADERS, UID_HEADER: MOCK_UID},
    )
    content = await response.json()
    assert response.status == expected_status, content
    assert content == expected_response


@pytest.mark.parametrize(
    'account_id, body, expected_status, expected_response',
    [
        pytest.param('acc1', {'is_invitation_sent': True}, 200, {}, id='ok'),
        pytest.param('acc1', {'is_invitation_sent': False}, 200, {}, id='ok'),
        pytest.param(
            'acc403',
            {'is_invitation_sent': True},
            404,
            {
                'code': 'GENERAL',
                'message': '',
                'system_message': (
                    'member account_id=acc403, '
                    'phone_id=00aaaaaaaaaaaaaaaaaaaa01 '
                    'does not exist'
                ),
                'details': {},
            },
            id='wrong_account',
        ),
    ],
)
async def test_coop_member_invite_sent(
        web_app_client,
        web_context,
        mock_user_api,
        account_id,
        body,
        expected_status,
        expected_response,
):
    response = await web_app_client.put(
        '/4.0/coop_account/member/invitation_sent',
        json=body,
        headers={**DEFAULT_HEADERS, UID_HEADER: MOCK_UID},
        params={'id': account_id},
    )
    content = await response.json()
    assert response.status == expected_status, content
    assert content == expected_response
    if expected_status == 200:
        phone_id = await users_repo.get_phone_id_by_user_id(
            web_context, MOCK_USER_ID,
        )
        member = await members_repo.get_one_by_phone_id(
            web_context, account_id, phone_id,
        )
        assert member.is_invitation_sent == body['is_invitation_sent']


@pytest.mark.parametrize(
    'params, uid, body, expected_status, expected_response',
    [
        pytest.param(
            {'id': 'memb2', 'revision': 'revision0'},
            MOCK_UID,
            {
                'details': {
                    'nickname': 'Роман Александрович',
                    'phone': '+79876541234',
                },
                'limits': {'has_specific_limit': True, 'amount': 1000},
            },
            200,
            {'revision': MOCK_ID},
            id='ok',
        ),
        pytest.param(
            {'id': 'memb31', 'revision': 'revision1'},
            MOCK_UID,
            {
                'details': {
                    'nickname': 'Роман Александрович',
                    'phone': '+79876541234',
                },
                'limits': {'has_specific_limit': True, 'amount': 1000},
            },
            200,
            {'revision': MOCK_ID},
            id='account_with_limit',
        ),
        pytest.param(
            {'id': 'memb1', 'revision': 'revision0'},
            MOCK_UID,
            {
                'details': {
                    'nickname': 'Роман Александрович',
                    'phone': '+79876541234',
                },
            },
            400,
            {
                'code': 'GENERAL',
                'message': '',
                'system_message': 'cannot change owner',
                'details': {},
            },
            id='owner',
        ),
    ],
)
@pytest.mark.config(
    COOP_ACCOUNT_SETTINGS=[{'type': 'family', 'set_limits': True}],
    USER_API_USE_USER_PHONES_RETRIEVAL_PY3=True,
)
async def test_coop_member_update_limit_v2(
        web_app_client,
        web_context,
        mock_all_api,
        monkeypatch,
        params,
        uid,
        body,
        expected_status,
        expected_response,
):
    monkeypatch.setattr('uuid.UUID.hex', MOCK_ID)

    response = await web_app_client.put(
        '4.0/coop_account/v2/member/details',
        json=body,
        params=params,
        headers={**DEFAULT_HEADERS, UID_HEADER: uid},
    )
    content = await response.json()
    assert response.status == expected_status, content
    assert content == expected_response

    if expected_status != 200:
        return

    cur_member = await members_repo.get_one_by_id(web_context, params['id'])
    account = await accounts_repo.get_one_by_id(
        web_context, cur_member.account_id,
    )
    body_has_limit = body['limits']['has_specific_limit']
    body_limit_amount = body['limits']['amount']

    assert cur_member.has_specific_limit == body_has_limit

    if body_has_limit:
        assert cur_member.limit_amount == body_limit_amount * (10 ** 4)

    members = await members_repo.get_members(
        web_context, cur_member.account_id, is_deleted=True,
    )

    assert not account.limit_amount
    assert not account.has_specific_limit

    for member in members:
        if not member.is_active:
            assert member.deleted_at
        if not cur_member.id == params['id']:
            assert not member.limit_amount
            assert not member.has_specific_limit


@pytest.mark.config(USER_API_USE_USER_PHONES_RETRIEVAL_PY3=True)
async def test_coop_member_update_member(
        web_app_client, web_context, mock_all_api, monkeypatch,
):
    monkeypatch.setattr('uuid.UUID.hex', MOCK_ID)

    response = await web_app_client.put(
        '4.0/coop_account/v2/member/details',
        json={
            'details': {
                'nickname': 'Роман Новое Имя',
                'phone': '+79999999999',
            },
        },
        params={'id': 'memb2', 'revision': 'revision0'},
        headers={**DEFAULT_HEADERS, UID_HEADER: MOCK_UID},
    )
    content = await response.json()

    assert response.status == 200, content
    assert content == {'revision': MOCK_ID}

    del_member = await members_repo.get_one_by_id(
        web_context, MOCK_ID, is_deleted=True,
    )

    # created_at not updated, equal to the original value
    assert del_member.created_at == datetime.datetime(2018, 1, 1, 10, 0, 0, 1)


@pytest.mark.parametrize(
    'body, member_uid, need_migrate, expected_response',
    [
        pytest.param(
            {'account_id': 'acc_with_passport_family'},
            PHONISH_MEMBER_UID,
            True,
            {},
            id='ok',
        ),
        pytest.param(
            {'account_id': 'acc_with_passport_family'},
            MOCK_UID,
            False,
            {},
            id='member_without_invite',
        ),
        pytest.param(
            {'account_id': 'acc_with_passport_family'},
            PHONISH_MEMBER_UID_WITHOUT_PORTAL,
            False,
            {},
            id='member_without_portal_account',
        ),
    ],
)
async def test_coop_member_zalogined(
        web_app_client,
        web_context,
        mock_user_api,
        patch,
        body,
        member_uid,
        need_migrate,
        expected_response,
):
    @patch(
        'taxi_shared_payments.controllers.passport_family.add_member_create_task',
    )
    async def _add_member_create_task(*args, **kwargs):
        return

    phone_id = await users_repo.get_phone_id_by_user_id(
        web_context, member_uid,
    )
    if need_migrate:
        invite = await members_repo.get_phonish_invite(
            web_context, phone_id, PASSPORT_FAMILY_ID,
        )
        assert invite.is_already_portal is False

    response = await web_app_client.post(
        '/4.0/coop_account/member/zalogined',
        json=body,
        headers={
            **DEFAULT_HEADERS,
            UID_HEADER: member_uid,
            PHONE_ID_HEADER: PHONISH_MEMBER_PHONE_ID,
        },
    )
    content = await response.json()
    assert response.status == 200, content
    assert content == expected_response

    if not need_migrate:
        return

    # Check this stuff only in success cases
    assert len(_add_member_create_task.calls) == 1
    invite = await members_repo.get_phonish_invite(
        web_context, phone_id, PASSPORT_FAMILY_ID, slave=False,
    )

    # Check, that invite marked as already_portal
    assert invite.is_already_portal is True
