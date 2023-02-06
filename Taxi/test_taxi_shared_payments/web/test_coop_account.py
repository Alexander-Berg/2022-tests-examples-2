# pylint: disable=too-many-lines, invalid-string-quote
# flake8: noqa
import datetime
import pytz
import dateutil.parser as dp

import pytest

from aiohttp import web

from taxi.clients import personal

from taxi_shared_payments.common import models
from taxi_shared_payments.repositories import accounts as accounts_repo
from taxi_shared_payments.repositories import members as members_repo
from test_taxi_shared_payments.conftest import DEFAULT_HEADERS

MOCK_ID = 'uuid4'
MOCK_UID = 'user1'
MOCK_UID2 = 'user2'
MOCK_UID3 = 'user3'
MOCK_UID_SHORT_INFO = 'user_for_rides'
MOCK_PORTAL_UID = 'portal_user1'
MOCK_PORTAL_UID3 = 'portal_user3'
MOCK_UID_PASSPORT_FAMILY = 'user_with_family'

UID_HEADER = 'X-Yandex-UID'
TVM_USER_TICKET_HEADER = 'X-Ya-User-Ticket'
CREATE_HEADERS = {
    'X-Request-Application': 'app_brand=yataxi,app_name=light_business',
    'X-Remote-IP': 'amazing_ip',
}
ACCOUNT_HEADER = {'X-YaTaxi-Pass-Flags': 'portal'}
RECREATED_ACCOUNT_ID = '2'


@pytest.mark.parametrize(
    'body, revision, expected_status, expected_response',
    [
        pytest.param(
            {
                'details': {'color': '000000'},
                'type': 'family',
                'payment': {
                    'payment_methods': [
                        {'type': 'card', 'payment_method_id': 'pm_id'},
                    ],
                    'main_payment_method_id': 'pm_id',
                },
                'tz_offset': '-0300',
                'user_agreement': {
                    'user_agreement_required': True,
                    'user_agreement_accepted': True,
                },
            },
            'revision1',
            200,
            {
                'id': f'family-{MOCK_ID}',
                'revision': 'revision1',
                'type': 'family',
                'details': {'name': 'Семейный аккаунт', 'color': '000000'},
                'payment': {
                    'payment_methods': [
                        {'type': 'card', 'payment_method_id': 'pm_id'},
                    ],
                    'main_payment_method_id': 'pm_id',
                },
                'members_description': 'N участников',
                'members': [
                    {
                        'details': {
                            'nickname': 'Владелец аккаунта',
                            'phone': '+79876541234',
                        },
                        'limits': {'has_specific_limit': False},
                        'revision': MOCK_ID,
                        'id': MOCK_ID,
                        'role': 'owner',
                        'is_myself': True,
                    },
                ],
                'is_active': True,
                'has_specific_limit': False,
            },
            id='all_fields_ok',
        ),
        pytest.param(
            {
                'details': {'color': '000000'},
                'type': 'family',
                'payment': {
                    'payment_methods': [{'type': 'card', 'id': 'pm_id'}],
                    'main_payment_method_id': 'pm_id',
                },
                'tz_offset': '-0300',
                'user_agreement': {
                    'user_agreement_required': True,
                    'user_agreement_accepted': True,
                },
            },
            'revision1',
            200,
            {
                'id': f'family-{MOCK_ID}',
                'revision': 'revision1',
                'type': 'family',
                'details': {'name': 'Семейный аккаунт', 'color': '000000'},
                'payment': {
                    'payment_methods': [
                        {'type': 'card', 'payment_method_id': 'pm_id'},
                    ],
                    'main_payment_method_id': 'pm_id',
                },
                'members_description': 'N участников',
                'members': [
                    {
                        'details': {
                            'nickname': 'Владелец аккаунта',
                            'phone': '+79876541234',
                        },
                        'limits': {'has_specific_limit': False},
                        'revision': MOCK_ID,
                        'id': MOCK_ID,
                        'role': 'owner',
                        'is_myself': True,
                    },
                ],
                'is_active': True,
                'has_specific_limit': False,
            },
            id='all_fields_ok (check hotfix: use id instead payment_method_id)',
        ),
        pytest.param(
            {
                'details': {'color': '000000'},
                'type': 'business',
                'payment': {
                    'payment_methods': [
                        {'type': 'card', 'payment_method_id': 'pm_id'},
                    ],
                    'main_payment_method_id': 'pm_id',
                },
                'tz_offset': '-0300',
                'user_agreement': {'user_agreement_required': False},
            },
            'revision1',
            200,
            {
                'id': f'business-{MOCK_ID}',
                'revision': 'revision1',
                'type': 'business',
                'details': {'name': 'Бизнес аккаунт', 'color': '000000'},
                'payment': {
                    'payment_methods': [
                        {'type': 'card', 'payment_method_id': 'pm_id'},
                    ],
                    'main_payment_method_id': 'pm_id',
                },
                'members_description': 'N участников',
                'members': [
                    {
                        'details': {
                            'nickname': 'Владелец аккаунта',
                            'phone': '+79876541234',
                        },
                        'limits': {'has_specific_limit': False},
                        'revision': MOCK_ID,
                        'id': MOCK_ID,
                        'role': 'owner',
                        'is_myself': True,
                    },
                ],
                'is_active': True,
                'has_specific_limit': False,
            },
            id='business_default_name',
        ),
        pytest.param(
            {
                'details': {'color': '000000'},
                'type': 'family',
                'payment': {
                    'payment_methods': [
                        {'type': 'card', 'payment_method_id': 'pm_id'},
                    ],
                    'main_payment_method_id': 'pm_id',
                },
                'tz_offset': '-0300',
            },
            'revision1',
            400,
            {
                'code': 'GENERAL',
                'message': '',
                'system_message': 'many accounts per owner',
                'details': {},
            },
            marks=pytest.mark.config(
                ANTIFRAUD_COOP_ACCOUNTS={'family': 0, 'business': 0},
            ),
            id='antifraud_fail_1',
        ),
        pytest.param(
            {
                'details': {'color': '000000'},
                'type': 'family',
                'payment': {
                    'payment_methods': [
                        {'type': 'card', 'payment_method_id': 'pm_id'},
                    ],
                    'main_payment_method_id': 'pm_id',
                },
                'tz_offset': '-0300',
            },
            'revision1',
            400,
            {
                'code': 'GENERAL',
                'message': '',
                'system_message': 'many accounts per owner',
                'details': {},
            },
            marks=pytest.mark.config(
                ANTIFRAUD_COOP_ACCOUNTS={'family': 3, 'business': 0},
            ),
            id='antifraud_fail_2',
        ),
        pytest.param(
            {
                'details': {'color': '000000'},
                'type': 'business',
                'payment': {
                    'payment_methods': [
                        {'type': 'card', 'payment_method_id': 'pm_id'},
                    ],
                    'main_payment_method_id': 'pm_id',
                },
                'tz_offset': '-0300',
            },
            'revision1',
            400,
            {
                'code': 'GENERAL',
                'message': '',
                'system_message': 'many accounts per owner',
                'details': {},
            },
            marks=pytest.mark.config(
                ANTIFRAUD_COOP_ACCOUNTS={'family': 0, 'business': 1},
            ),
            id='antifraud_fail_3',
        ),
        pytest.param(
            {
                'details': {'color': '000000'},
                'type': 'business',
                'payment': {
                    'payment_methods': [
                        {'type': 'card', 'payment_method_id': 'pm_id'},
                    ],
                    'main_payment_method_id': 'pm_id',
                },
                'tz_offset': '-0300',
            },
            'revision1',
            400,
            {'code': 'GENERAL', 'message': 'Мало поездок', 'details': {}},
            marks=pytest.mark.config(ANTIFRAUD_SUCCESSFUL_ORDERS=10),
            id='antifraud_fail_4',
        ),
        pytest.param(
            {
                'details': {'color': '000000'},
                'type': 'family',
                'tz_offset': '-0300',
            },
            'revision1',
            200,
            {
                'id': f'family-{MOCK_ID}',
                'revision': 'revision1',
                'type': 'family',
                'details': {'name': 'Семейный аккаунт', 'color': '000000'},
                'members_description': 'N участников',
                'members': [
                    {
                        'details': {
                            'nickname': 'Владелец аккаунта',
                            'phone': '+79876541234',
                        },
                        'limits': {'has_specific_limit': False},
                        'revision': MOCK_ID,
                        'id': MOCK_ID,
                        'role': 'owner',
                        'is_myself': True,
                    },
                ],
                # todo: почему раньше тут не было ошибки?
                'payment_error_description': 'Нет способа оплаты',
                'has_specific_limit': False,
                'is_active': False,
            },
            id='no_payment_ok',
        ),
        pytest.param(
            None,
            'revision1',
            400,
            # todo
            # {
            #     'code': 'REQUEST_VALIDATION_ERROR',
            #     'message': '',
            #     'system_message': 'empty request body',
            #     'details': {},
            # },
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {'reason': 'body is required'},
                'message': 'Some parameters are invalid',
            },
            id='empty_body',
        ),
        pytest.param(
            {
                'details': {'name': 'Ивановы Inc.', 'color': '000000'},
                'type': 'wrong',
                'payment': {
                    'payment_methods': [
                        {'type': 'card', 'payment_method_id': '123'},
                    ],
                    'main_payment_method_id': 'payment_method_id',
                },
                'tz_offset': '000',
            },
            'revision1',
            400,
            # {
            #     'code': 'REQUEST_VALIDATION_ERROR',
            #     'message': '',
            #     'system_message': 'Invalid input',
            #     'details': {
            #         'payment.payment_methods.0.payment_method_id': [
            #             '123 is not of type \'string\''
            #         ],
            #         'type': [
            #             '\'wrong\' is not one of [\'family\', \'business\']'
            #         ],
            #         'tz_offset': ['\'000\' does not match \'^[+-]\\\\d{4}$\''],
            #     },
            # },
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {
                    'reason': (
                        'Invalid value for type: \'wrong\' must be one of '
                        '[\'family\', \'business\']'
                    ),
                },
                'message': 'Some parameters are invalid',
            },
            id='wrong_fields',
        ),
        pytest.param(
            {
                'details': {'name': 'Ивановы Inc.', 'color': '000000'},
                'type': 'business',
                'payment': {
                    'payment_methods': [
                        {'type': 'card', 'payment_method_id': 'pm_id'},
                    ],
                    'main_payment_method_id': 'pm_id',
                },
                'tz_offset': '-0300',
                'user_agreement': {
                    'user_agreement_required': False,
                    'user_agreement_accepted': True,
                },
            },
            'revision1',
            200,
            {
                'id': RECREATED_ACCOUNT_ID,
                'details': {'name': 'Ивановы Inc.', 'color': 'FFFFFF'},
                'payment': {
                    'payment_methods': [
                        {'type': 'card', 'payment_method_id': 'pm_id2'},
                    ],
                    'main_payment_method_id': 'pm_id2',
                },
                'revision': 'revision1',
                'type': 'business',
                'has_specific_limit': False,
                'is_active': True,
                'members_description': 'N участников',
                'members': [
                    {
                        'details': {
                            'nickname': 'Иванов',
                            'phone': '+79876541234',
                        },
                        'limits': {'has_specific_limit': False},
                        'revision': 'revision11',
                        'id': 'memb11',
                        'role': 'owner',
                        'is_myself': True,
                    },
                ],
                'email': 'corp@inc.com',
                'report_frequency': 'never',
            },
            id='account_re_create',
        ),
        pytest.param(
            {
                'details': {'name': 'Ивановы Inc.', 'color': '000000'},
                'type': 'business',
                'payment': {
                    'payment_methods': [
                        {'type': 'card', 'payment_method_id': 'pm_id'},
                    ],
                    'main_payment_method_id': 'pm_id',
                },
                'tz_offset': '-0300',
            },
            'revision2',
            409,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'message': 'Такой аккаунт уже есть',
                'details': {},
            },
            id='duplicate_account_name',
        ),
        pytest.param(
            {
                'details': {'color': '000000'},
                'type': 'business',
                'payment': {
                    'payment_methods': [
                        {'type': 'card', 'payment_method_id': 'pm_id'},
                    ],
                    'main_payment_method_id': 'pm_id',
                },
                'tz_offset': '-0300',
                'email': 'email@email.com',
            },
            'revision1',
            200,
            {
                'id': f'business-{MOCK_ID}',
                'revision': 'revision1',
                'type': 'business',
                'details': {'name': 'Бизнес аккаунт', 'color': '000000'},
                'payment': {
                    'payment_methods': [
                        {'type': 'card', 'payment_method_id': 'pm_id'},
                    ],
                    'main_payment_method_id': 'pm_id',
                },
                'members_description': 'N участников',
                'members': [
                    {
                        'details': {
                            'nickname': 'Владелец аккаунта',
                            'phone': '+79876541234',
                        },
                        'limits': {'has_specific_limit': False},
                        'revision': MOCK_ID,
                        'id': MOCK_ID,
                        'role': 'owner',
                        'is_myself': True,
                    },
                ],
                'is_active': True,
                'has_specific_limit': False,
                'email': 'email@email.com',
            },
            id='Create account with email',
        ),
        pytest.param(
            {
                'details': {'color': '000000'},
                'type': 'business',
                'payment': {
                    'payment_methods': [
                        {'type': 'card', 'payment_method_id': 'pm_id'},
                    ],
                    'main_payment_method_id': 'pm_id',
                },
                'tz_offset': '-0300',
                'email': 'email@email.com',
                'report_frequency': 'never',
            },
            'revision1',
            200,
            {
                'id': f'business-{MOCK_ID}',
                'revision': 'revision1',
                'type': 'business',
                'details': {'name': 'Бизнес аккаунт', 'color': '000000'},
                'payment': {
                    'payment_methods': [
                        {'type': 'card', 'payment_method_id': 'pm_id'},
                    ],
                    'main_payment_method_id': 'pm_id',
                },
                'members_description': 'N участников',
                'members': [
                    {
                        'details': {
                            'nickname': 'Владелец аккаунта',
                            'phone': '+79876541234',
                        },
                        'limits': {'has_specific_limit': False},
                        'revision': MOCK_ID,
                        'id': MOCK_ID,
                        'role': 'owner',
                        'is_myself': True,
                    },
                ],
                'is_active': True,
                'has_specific_limit': False,
                'email': 'email@email.com',
                'report_frequency': 'never',
            },
            id='Create account with email and report frequency',
        ),
        pytest.param(
            {
                'details': {'color': '000000'},
                'type': 'business',
                'payment': {
                    'payment_methods': [
                        {'type': 'card', 'payment_method_id': 'pm_id'},
                    ],
                    'main_payment_method_id': 'pm_id',
                },
                'tz_offset': '-0300',
                'report_frequency': 'never',
            },
            'revision1',
            400,
            {
                'code': 'GENERAL',
                'message': '',
                'details': {},
                'system_message': (
                    'Report frequency should be passed with email'
                ),
            },
            id='Create account with report frequency without email',
        ),
    ],
)
@pytest.mark.config(
    COOP_ACCOUNT_TYPES=[
        {'member_max_count': 3, 'account_max_count': 2, 'type': 'family'},
        {'member_max_count': 20, 'account_max_count': 2, 'type': 'business'},
    ],
    ANTIFRAUD_COOP_ACCOUNTS={'family': 5, 'business': 5},
    ANTIFRAUD_DAYS_AFTER_CREATE={'created_accounts': 1, 'created_members': 1},
    USER_API_USE_USER_PHONES_RETRIEVAL_PY3=True,
    COOP_PAYMENT_ERROR_TANKER_KEYS={
        'no_payment_method': 'shared_payments.no_payment_method_error',
    },
    # todo: remove after fix client for personal
    TVM_RULES=[{'dst': 'personal', 'src': 'shared-payments'}],
    COOP_ACCOUNT_SETTINGS=[
        {
            'type': 'business',
            'report_options': [{'title': 'never', 'code': 'never'}],
        },
    ],
)
@pytest.mark.translations(
    client_messages={
        'shared_payments.default_account_name_family': {
            'ru': 'Семейный аккаунт',
        },
        'shared_payments.default_account_name_business': {
            'ru': 'Бизнес аккаунт',
        },
        'shared_payments.account_owner': {'ru': 'Владелец аккаунта'},
        'shared_payments.duplicate_account_error': {
            'ru': 'Такой аккаунт уже есть',
        },
        'shared_payments.members_description': {'ru': 'N участников'},
        'shared_payments.antifraud_successful_orders': {'ru': 'Мало поездок'},
        'shared_payments.no_payment_method_error': {
            'ru': 'Нет способа оплаты',
        },
        'never': {'ru': 'never'},
    },
)
@pytest.mark.now('2018-01-01T12:08:12')
async def test_coop_acc_create(
        web_app_client,
        web_context,
        monkeypatch,
        mock_all_api,
        mockserver,
        stq,
        patch,
        body,
        revision,
        expected_status,
        expected_response,
):
    @patch('taxi_shared_payments.controllers.emails.send_welcome_emails')
    async def _send_welcome_emails(
            context, account_id, locale, brand, user_ip,
    ):
        assert account_id == expected_response['id']
        assert locale == 'ru'
        assert brand == 'yataxi'
        assert user_ip == 'amazing_ip'

    @mockserver.json_handler('/experiments3/v1/experiments')
    def _handler(request):
        return {'items': []}

    @patch('taxi.clients.passport.PassportClient.get_raw_userinfo')
    async def _get_info_by_uid(*args, **kwargs):
        return {}

    @patch('taxi.clients.passport.PassportClient.get_raw_familyinfo')
    async def _get_family_info_by_uid(*args, **kwargs):
        return {}

    monkeypatch.setattr('uuid.UUID.hex', MOCK_ID)

    response = await web_app_client.post(
        '/4.0/coop_account/create',
        json=body,
        headers={
            **DEFAULT_HEADERS,
            **CREATE_HEADERS,
            **ACCOUNT_HEADER,
            UID_HEADER: MOCK_UID,
        },
        params={'revision': revision},
    )

    # Check response
    content = await response.json()
    accepted_at = content.pop('accepted_at', None)
    content.pop('settings', None)
    assert response.status == expected_status
    assert content == expected_response

    if expected_status == 200:
        # Check account has been created
        account = await accounts_repo.get_one_by_id(web_context, content['id'])
        assert dp.isoparse(accepted_at).astimezone(
            pytz.utc,
        ) == account.created_at.replace(microsecond=0, tzinfo=pytz.utc)
        assert account.type.value == body['type']
        if 'email' in body:
            assert account.email_id == 'id-' + body['email']
        if 'report_frequency' in body:
            assert account.report_frequency == body['report_frequency']

        recreated_account = account.id == RECREATED_ACCOUNT_ID
        is_business_account = account.type == models.AccountTypes.BUSINESS
        if is_business_account and not recreated_account:
            assert len(_send_welcome_emails.calls) == 1
            assert stq.shared_payments_creation_notify.times_called == 1


@pytest.mark.parametrize(
    'body, revision, expected_status, expected_response',
    [
        pytest.param(
            {
                'details': {'color': '000000'},
                'type': 'family',
                'payment': {
                    'payment_methods': [
                        {'type': 'card', 'payment_method_id': 'pm_id'},
                    ],
                    'main_payment_method_id': 'pm_id',
                },
                'tz_offset': '-0300',
            },
            'revision2',
            500,
            {
                'code': 'GENERAL',
                'message': '',
                'system_message': 'just mocking a db failure',
                'details': {},
            },
            id='db_failure_on_owner_creation',
        ),
    ],
)
@pytest.mark.config(
    COOP_ACCOUNT_TYPES=[
        {'member_max_count': 10, 'account_max_count': 10, 'type': 'family'},
    ],
    USER_API_USE_USER_PHONES_RETRIEVAL_PY3=True,
)
@pytest.mark.translations(
    client_messages={
        'shared_payments.account_owner': {'ru': 'Владелец аккаунта'},
    },
)
async def test_coop_acc_failed_owner(
        web_app_client,
        web_context,
        mock_all_api,
        create_member_exception,
        mockserver,
        body,
        revision,
        expected_status,
        expected_response,
):
    @mockserver.json_handler('/experiments3/v1/experiments')
    def _handler(request):
        return {'items': []}

    response = await web_app_client.post(
        '/4.0/coop_account/create',
        json=body,
        headers={**DEFAULT_HEADERS, UID_HEADER: MOCK_UID2},
        params={'revision': revision},
    )
    content = await response.json()
    assert response.status == expected_status, content
    assert content == expected_response

    # check no new accounts created
    account = await accounts_repo.get_one_by_revision(
        web_context, revision, body['details'].get('name'), body['type'],
    )
    assert account is None


@pytest.mark.parametrize(
    'user_agreement',
    [
        {'user_agreement_required': True, 'user_agreement_accepted': False},
        {'user_agreement_required': True},
    ],
)
async def test_coop_acc_failure_user_agreement(
        web_app_client, web_context, mock_all_api, user_agreement,
):
    body = {
        'details': {'color': '000000'},
        'type': 'family',
        'tz_offset': '-0300',
        'user_agreement': user_agreement,
    }

    revision = 'revision2'
    response = await web_app_client.post(
        '/4.0/coop_account/create',
        json=body,
        headers={**DEFAULT_HEADERS, UID_HEADER: MOCK_UID},
        params={'revision': revision},
    )
    assert response.status == 400
    content = await response.json()
    assert content == {
        'code': 'NEED_USER_AGREEMENT',
        'message': '',
        'system_message': 'user did not agree to create account',
        'details': {},
    }

    # check no new accounts created
    account = await accounts_repo.get_one_by_revision(
        web_context, revision, body['details'].get('name'), body['type'],
    )
    assert account is None


@pytest.mark.parametrize(
    'body, expected_status, expected_response',
    [
        pytest.param(
            {
                'details': {'color': '000000'},
                'type': 'family',
                'payment': {
                    'payment_methods': [
                        {'type': 'card', 'payment_method_id': 'pm_id'},
                    ],
                    'main_payment_method_id': 'pm_id',
                },
                'tz_offset': '+0300',
            },
            409,
            {
                'code': 'GENERAL',
                'message': 'Слишком много аккаунтов',
                'details': {},
            },
            id='too_many_family',
        ),
        pytest.param(
            {
                'details': {'name': 'Ивановы Inc2', 'color': '000000'},
                'type': 'business',
                'payment': {
                    'payment_methods': [
                        {'type': 'card', 'payment_method_id': 'pm_id'},
                    ],
                    'main_payment_method_id': 'pm_id',
                },
                'tz_offset': '-0300',
            },
            409,
            {
                'code': 'GENERAL',
                'message': 'Слишком много аккаунтов',
                'details': {},
            },
            id='too_many_business',
        ),
    ],
)
@pytest.mark.translations(
    client_messages={
        'shared_payments.too_many_accounts_error': {
            'ru': 'Слишком много аккаунтов',
        },
        'shared_payments.members_description': {'ru': 'N участников'},
    },
)
@pytest.mark.config(
    COOP_ACCOUNT_TYPES=[
        {'member_max_count': 3, 'account_max_count': 1, 'type': 'family'},
        {'member_max_count': 20, 'account_max_count': 1, 'type': 'business'},
    ],
    ANTIFRAUD_COOP_ACCOUNTS={'family': 5, 'business': 5},
    USER_API_USE_USER_PHONES_RETRIEVAL_PY3=True,
)
async def test_account_create_too_many(
        web_app_client,
        web_context,
        mock_all_api,
        monkeypatch,
        mockserver,
        patch,
        body,
        expected_status,
        expected_response,
):
    @mockserver.json_handler('/experiments3/v1/experiments')
    def _handler(request):
        return {'items': []}

    @patch('taxi.clients.passport.PassportClient.get_raw_userinfo')
    async def _get_info_by_uid(*args, **kwargs):
        return {}

    @patch('taxi.clients.passport.PassportClient.get_raw_familyinfo')
    async def _get_family_info_by_uid(*args, **kwargs):
        return {}

    monkeypatch.setattr('uuid.UUID.hex', MOCK_ID)

    response = await web_app_client.post(
        '/4.0/coop_account/create',
        json=body,
        headers={**DEFAULT_HEADERS, UID_HEADER: MOCK_UID},
        params={'revision': 'revision0'},
    )
    content = await response.json()
    assert response.status == expected_status, content
    assert content == expected_response


@pytest.mark.parametrize(
    'uid, url, expected_status, bb_userinfo, bb_familyinfo, expected_response',
    [
        pytest.param(
            MOCK_UID,
            '/4.0/coop_account?account_id=1',
            200,
            {},
            {},
            {
                'id': '1',
                'revision': 'revision1',
                'type': 'family',
                'details': {'name': 'Семейный аккаунт', 'color': 'FFFFFF'},
                'payment': {
                    'payment_methods': [
                        {'type': 'card', 'payment_method_id': 'pm_id'},
                    ],
                    'main_payment_method_id': 'pm_id',
                },
                'members_description': 'N участников',
                'members': [
                    {
                        'details': {
                            'nickname': 'Petrov Sr.',
                            'phone': '+79876541234',
                        },
                        'limits': {'has_specific_limit': False},
                        'id': 'memb1',
                        'revision': 'revision2',
                        'role': 'owner',
                        'is_myself': True,
                    },
                    {
                        'details': {
                            'nickname': 'Petrov Jr.',
                            'phone': '+79876541235',
                        },
                        'limits': {'amount': 100, 'has_specific_limit': True},
                        'id': 'memb2',
                        'role': 'user',
                        'is_myself': False,
                        'revision': 'revision3',
                    },
                    {
                        'details': {
                            'nickname': 'Petrov Not Accepted',
                            'phone': '+79876541237',
                        },
                        'limits': {'has_specific_limit': False},
                        'id': 'memb4',
                        'role': 'user',
                        'is_myself': False,
                        'revision': 'revision4',
                    },
                ],
                'has_specific_limit': False,
                'is_active': True,
                'currency_rules': {
                    'code': 'RUB',
                    'sign': '₽',
                    'template': '$VALUE$ $SIGN$$CURRENCY$',
                    'text': 'руб.',
                },
                'accepted_at': '2018-01-01T13:00:00+03:00',
            },
            id='ok_family',
        ),
        pytest.param(
            MOCK_UID3,
            '/4.0/coop_account?account_id=18',
            200,
            {},
            {},
            {
                'id': '18',
                'revision': 'revision1',
                'type': 'family',
                'details': {'color': 'FFFFFF', 'name': 'Семейный аккаунт'},
                'has_specific_limit': True,
                'is_active': True,
                'limit_amount': 5000,
                'payment': {
                    'main_payment_method_id': 'pm_id6',
                    'payment_methods': [
                        {'payment_method_id': 'pm_id6', 'type': 'card'},
                    ],
                },
                'members': [
                    {
                        'details': {
                            'nickname': 'Владелец аккаунта с лимитом',
                            'phone': '+79876541236',
                        },
                        'id': 'memb12',
                        'is_myself': True,
                        'limits': {'has_specific_limit': False},
                        'revision': 'revision11',
                        'role': 'owner',
                    },
                    {
                        'details': {
                            'nickname': 'Пользователь с лимитом',
                            'phone': '+79876541237',
                        },
                        'id': 'memb13',
                        'is_myself': False,
                        'limits': {'amount': 5000, 'has_specific_limit': True},
                        'revision': 'revision11',
                        'role': 'user',
                    },
                ],
                'members_description': 'N участников',
                'accepted_at': '2018-01-01T13:00:00+03:00',
            },
            id='ok_with_limit',
        ),
        pytest.param(
            MOCK_UID,
            '/4.0/coop_account?account_id=2',
            200,
            {},
            {},
            {
                'id': '2',
                'revision': 'revision1',
                'type': 'business',
                'details': {'name': 'Ивановы Inc.', 'color': 'FFFFFF'},
                'payment': {
                    'payment_methods': [
                        {'type': 'card', 'payment_method_id': 'pm_id2'},
                    ],
                    'main_payment_method_id': 'pm_id2',
                },
                'members_description': 'N участников',
                'members': [
                    {
                        'details': {
                            'nickname': 'Иванов',
                            'phone': '+79876541234',
                        },
                        'limits': {'has_specific_limit': False},
                        'id': 'memb11',
                        'revision': 'revision11',
                        'role': 'owner',
                        'is_myself': True,
                    },
                ],
                'has_specific_limit': False,
                'is_active': True,
                'settings': {
                    'set_name': True,
                    'set_limits': False,
                    'set_email': True,
                    'report_options': [],
                },
                'email': 'corp@inc.com',
                'report_frequency': 'never',
                'accepted_at': '2018-01-01T13:00:00+03:00',
            },
            id='ok_business',
        ),
        pytest.param(
            MOCK_PORTAL_UID,
            '/4.0/coop_account?account_id=1',
            200,
            {},
            {},
            {
                'id': '1',
                'revision': 'revision1',
                'type': 'family',
                'details': {'name': 'Семейный аккаунт', 'color': 'FFFFFF'},
                'payment': {
                    'payment_methods': [
                        {'type': 'card', 'payment_method_id': 'pm_id'},
                    ],
                    'main_payment_method_id': 'pm_id',
                },
                'members_description': 'N участников',
                'members': [
                    {
                        'details': {
                            'nickname': 'Petrov Sr.',
                            'phone': '+79876541234',
                        },
                        'limits': {'has_specific_limit': False},
                        'id': 'memb1',
                        'revision': 'revision2',
                        'role': 'owner',
                        'is_myself': True,
                    },
                    {
                        'details': {
                            'nickname': 'Petrov Jr.',
                            'phone': '+79876541235',
                        },
                        'limits': {'amount': 100, 'has_specific_limit': True},
                        'id': 'memb2',
                        'role': 'user',
                        'is_myself': False,
                        'revision': 'revision3',
                    },
                    {
                        'details': {
                            'nickname': 'Petrov Not Accepted',
                            'phone': '+79876541237',
                        },
                        'limits': {'has_specific_limit': False},
                        'id': 'memb4',
                        'role': 'user',
                        'is_myself': False,
                        'revision': 'revision4',
                    },
                ],
                'has_specific_limit': False,
                'is_active': True,
                'currency_rules': {
                    'code': 'RUB',
                    'sign': '₽',
                    'template': '$VALUE$ $SIGN$$CURRENCY$',
                    'text': 'руб.',
                },
                'accepted_at': '2018-01-01T13:00:00+03:00',
            },
            id='portal_user_access',
        ),
        pytest.param(
            MOCK_UID,
            '/4.0/coop_account?account_id=',
            400,
            {},
            {},
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {
                    'reason': (
                        'Invalid value for account_id: \'\' '
                        'length must be greater '
                        'than or equal to 1'
                    ),
                },
                'message': 'Some parameters are invalid',
            },
            id='empty_account_id',
        ),
        pytest.param(
            MOCK_UID,
            '/4.0/coop_account',
            400,
            {},
            {},
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {'reason': 'account_id is required parameter'},
                'message': 'Some parameters are invalid',
            },
            id='no_account_id',
        ),
        pytest.param(
            MOCK_UID,
            '/4.0/coop_account?account_id=404',
            404,
            {},
            {},
            {
                'code': 'GENERAL',
                'message': '',
                'system_message': 'account with id 404 does not exist',
                'details': {},
            },
            id='nonexistent_account_id',
        ),
        pytest.param(
            MOCK_UID,
            '/4.0/coop_account?account_id=403',
            403,
            {},
            {},
            {
                'code': 'GENERAL',
                'message': '',
                'system_message': 'yandex_uid does not match owner_id',
                'details': {},
            },
            id='wrong_account_id',
        ),
        pytest.param(
            MOCK_UID_PASSPORT_FAMILY,
            '/4.0/coop_account?account_id=100',
            200,
            {'users': [{'attributes': {'1022': 'PARENT'}}]},
            {},
            {
                'id': '100',
                'revision': 'revision1',
                'type': 'family',
                'details': {
                    'name': 'Семейный аккаунт',
                    'color': 'FFFFFF',
                    'passport_account': True,
                },
                'payment': {
                    'payment_methods': [
                        {'type': 'card', 'payment_method_id': 'pm_id7'},
                    ],
                    'main_payment_method_id': 'pm_id7',
                },
                'members_description': 'N участников',
                'members': [
                    {
                        'details': {
                            'nickname': 'Petrov Sr.',
                            'phone': '+79291111111',
                        },
                        'limits': {'has_specific_limit': False},
                        'id': 'memb100',
                        'revision': 'revision2',
                        'role': 'owner',
                        'is_myself': True,
                    },
                ],
                'has_specific_limit': False,
                'has_plus_multi': True,
                'is_active': True,
                'currency_rules': {
                    'code': 'RUB',
                    'sign': '₽',
                    'template': '$VALUE$ $SIGN$$CURRENCY$',
                    'text': 'руб.',
                },
                'accepted_at': '2018-01-01T13:00:00+03:00',
            },
            id='ok_family_with_plus_multy',
        ),
        pytest.param(
            MOCK_UID_PASSPORT_FAMILY,
            '/4.0/coop_account?account_id=100',
            200,
            {'users': [{'attributes': {}}]},
            {},
            {
                'id': '100',
                'revision': 'revision1',
                'type': 'family',
                'details': {
                    'name': 'Семейный аккаунт',
                    'color': 'FFFFFF',
                    'passport_account': True,
                },
                'payment': {
                    'payment_methods': [
                        {'type': 'card', 'payment_method_id': 'pm_id7'},
                    ],
                    'main_payment_method_id': 'pm_id7',
                },
                'members_description': 'N участников',
                'members': [
                    {
                        'details': {
                            'nickname': 'Petrov Sr.',
                            'phone': '+79291111111',
                        },
                        'limits': {'has_specific_limit': False},
                        'id': 'memb100',
                        'revision': 'revision2',
                        'role': 'owner',
                        'is_myself': True,
                    },
                ],
                'has_specific_limit': False,
                'has_plus_multi': False,
                'is_active': True,
                'currency_rules': {
                    'code': 'RUB',
                    'sign': '₽',
                    'template': '$VALUE$ $SIGN$$CURRENCY$',
                    'text': 'руб.',
                },
                'accepted_at': '2018-01-01T13:00:00+03:00',
            },
            id='ok_family_without_plus_multy',
        ),
    ],
)
@pytest.mark.translations(
    client_messages={
        'shared_payments.default_account_name_family': {
            'ru': 'Семейный аккаунт',
        },
        'shared_payments.members_description': {'ru': 'N участников'},
        'shared_payments.member_dont_have_go_app': {
            'ru': 'У участника не установлено приложение Go',
        },
    },
    tariff={
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'currency.rub': {'ru': 'руб.'},
        'currency_sign.rub': {'ru': '₽'},
    },
)
@pytest.mark.config(
    COOP_ACCOUNT_SETTINGS=[
        {'type': 'business', 'set_name': True, 'set_email': True},
    ],
    USER_API_USE_USER_PHONES_RETRIEVAL_PY3=True,
    # todo: remove after fix client for personal
    TVM_RULES=[{'dst': 'personal', 'src': 'shared-payments'}],
)
async def test_coop_acc_read(
        web_app_client,
        mock_all_api,
        load_json,
        patch,
        uid,
        url,
        expected_status,
        bb_userinfo,
        bb_familyinfo,
        expected_response,
):
    @patch('taxi.clients.passport.PassportClient.get_raw_userinfo')
    async def _get_info_by_uid(*args, **kwargs):
        return bb_userinfo

    @patch('taxi.clients.passport.PassportClient.get_raw_familyinfo')
    async def _get_family_info_by_uid(*args, **kwargs):
        return bb_familyinfo

    response = await web_app_client.get(
        url, headers={**DEFAULT_HEADERS, UID_HEADER: uid},
    )
    content = await response.json()
    assert content == expected_response
    assert response.status == expected_status


@pytest.mark.translations(
    client_messages={
        'shared_payments.default_account_name_family': {
            'ru': 'Семейный аккаунт',
        },
        'shared_payments.members_description': {'ru': 'N участников'},
    },
    tariff={
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'currency.rub': {'ru': 'руб.'},
        'currency_sign.rub': {'ru': '₽'},
    },
)
@pytest.mark.config(
    COOP_ACCOUNT_SETTINGS=[
        {'type': 'business', 'set_name': True, 'set_email': True},
    ],
    USER_API_USE_USER_PHONES_RETRIEVAL_PY3=True,
)
async def test_coop_acc_read_personal_not_available(
        web_app_client, mock_all_api, patch,
):
    @patch('taxi.clients.personal.PersonalApiClient.retrieve')
    async def _retrieve(*args, **kwargs):
        raise personal.BaseError

    response = await web_app_client.get(
        '/4.0/coop_account?account_id=2',
        headers={**DEFAULT_HEADERS, UID_HEADER: MOCK_UID},
    )
    assert response.status == 200
    content = await response.json()
    # todo: было так - assert content['email'] is None, content
    assert content.get('email') is None, content


@pytest.mark.parametrize(
    'params, uid, body, expected_status, expected_response',
    [
        pytest.param(
            {'account_id': '2', 'revision': 'revision1'},
            MOCK_UID,
            {'name': 'ООО Ромашка', 'color': '000000'},
            200,
            {'revision': MOCK_ID},
            id='ok',
        ),
        pytest.param(
            {'account_id': '2', 'revision': 'other_revision'},
            MOCK_UID,
            {'name': 'Ивановы Inc.'},
            200,
            {'revision': 'revision1'},
            id='no_change',
        ),
        pytest.param(
            {'account_id': '2', 'revision': 'bad_revision'},
            MOCK_UID,
            {'name': 'Changed name'},
            409,
            {
                'code': 'GENERAL',
                'message': '',
                'system_message': 'revision id does not match',
                'details': {},
            },
            id='bad_revision',
        ),
        pytest.param(
            {'account_id': '2', 'revision': 'revision1'},
            MOCK_UID2,
            {'name': 'ООО Ромашка', 'color': '000000'},
            403,
            {
                'code': 'GENERAL',
                'message': '',
                'system_message': 'yandex_uid does not match owner_id',
                'details': {},
            },
            id='bad_owner',
        ),
        pytest.param(
            {'account_id': '2', 'revision': 'revision1'},
            MOCK_UID,
            {},
            200,
            {'revision': 'revision1'},
            id='empty_body',
        ),
        pytest.param(
            {'account_id': '2'},
            MOCK_UID,
            {'name': 'ООО Ромашка', 'color': 'FFFFFF'},
            400,
            # {
            #     'code': 'REQUEST_VALIDATION_ERROR',
            #     'message': '',
            #     'system_message': 'no parameter revision provided',
            #     'details': {},
            # },
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {'reason': 'revision is required parameter'},
                'message': 'Some parameters are invalid',
            },
            id='no_revision',
        ),
        pytest.param(
            {},
            MOCK_UID,
            {'name': 'ООО Ромашка', 'color': 'FFFFFF'},
            400,
            # {
            #     'code': 'REQUEST_VALIDATION_ERROR',
            #     'message': '',
            #     'system_message': 'no parameter account_id provided',
            #     'details': {},
            # },
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {'reason': 'account_id is required parameter'},
                'message': 'Some parameters are invalid',
            },
            id='no_query',
        ),
    ],
)
async def test_coop_acc_update_details(
        web_app_client,
        web_context,
        monkeypatch,
        params,
        uid,
        body,
        expected_status,
        expected_response,
):
    monkeypatch.setattr('uuid.UUID.hex', MOCK_ID)

    response = await web_app_client.put(
        '4.0/coop_account/details',
        json=body,
        params=params,
        headers={**DEFAULT_HEADERS, UID_HEADER: uid},
    )
    assert response.status == expected_status
    content = await response.json()
    assert content == expected_response

    if expected_status == 200:
        account = await accounts_repo.get_one_by_id(
            web_context, params['account_id'],
        )
        if 'name' in body:
            assert account.name == body['name']
        if 'color' in body:
            assert account.color == body['color']


@pytest.mark.config(ANTIFRAUD_COOP_ACCOUNTS_WITH_SAME_CARD=5)
@pytest.mark.parametrize(
    'uid, params, body, expected_error, expected_status, expected_response, call_family_pay',
    [
        pytest.param(
            MOCK_UID,
            {'account_id': '1', 'revision': '1234'},
            {
                'payment_methods': [
                    {'type': 'card', 'payment_method_id': 'pm_id'},
                ],
                'main_payment_method_id': 'pm_id',
            },
            None,
            200,
            {'revision': MOCK_ID},
            False,
            id='ok',
        ),
        pytest.param(
            MOCK_UID,
            {'account_id': '1', 'revision': '1234'},
            {
                'payment_methods': [{'type': 'card', 'id': 'pm_id'}],
                'main_payment_method_id': 'pm_id',
            },
            None,
            200,
            {'revision': MOCK_ID},
            False,
            id='ok (hotfix with id instead payment_method_id)',
        ),
        pytest.param(
            MOCK_UID,
            {'account_id': '1', 'revision': '1234'},
            {
                'payment_methods': [
                    {'type': 'card', 'payment_method_id': 'pm_404'},
                ],
                'main_payment_method_id': 'pm_404',
            },
            None,
            400,
            {
                'code': 'GENERAL',
                'message': '',
                'system_message': 'payment with payment_id "pm_404" not found',
                'details': {},
            },
            False,
            id='no_card',
        ),
        pytest.param(
            MOCK_UID2,
            {'account_id': '16', 'revision': '1234'},
            {
                'payment_methods': [
                    {'type': 'card', 'payment_method_id': 'pm_id'},
                ],
                'main_payment_method_id': 'pm_id',
            },
            None,
            200,
            {'revision': MOCK_ID},
            False,
            id='reactivate_without_payment',
        ),
        pytest.param(
            MOCK_UID2,
            {'account_id': '17', 'revision': '1234'},
            {
                'payment_methods': [
                    {'type': 'card', 'payment_method_id': 'pm_id'},
                ],
                'main_payment_method_id': 'pm_id',
            },
            'payment_failed',
            400,
            {
                'code': 'GENERAL',
                'message': 'Нельзя поменять карту',
                'details': {},
            },
            False,
            id='no_reactivate_failed',
        ),
        pytest.param(
            MOCK_UID2,
            {'account_id': '17', 'revision': '1234'},
            {
                'payment_methods': [
                    {'type': 'card', 'payment_method_id': 'pm_id'},
                ],
                'main_payment_method_id': 'pm_id',
            },
            'payment_failed',
            200,
            {'revision': MOCK_ID},
            False,
            id='inactive_account_change_card',
            marks=pytest.mark.config(
                COOP_ACCOUNT_ALLOW_FAILED_PAYMENT_REWRITE=True,
            ),
        ),
        pytest.param(
            MOCK_UID,
            {'account_id': '1', 'revision': '1234'},
            {
                'payment_methods': [
                    {'type': 'card', 'payment_method_id': 'pm_id'},
                ],
                'main_payment_method_id': 'pm_id',
            },
            None,
            400,
            {
                'code': 'GENERAL',
                'message': '',
                'system_message': 'many accounts with the same card',
                'details': {},
            },
            False,
            marks=pytest.mark.config(ANTIFRAUD_COOP_ACCOUNTS_WITH_SAME_CARD=1),
            id='antifraud',
        ),
        pytest.param(
            MOCK_UID,
            {'account_id': '1', 'revision': '1234'},
            {
                'payment_methods': [
                    {'type': 'card', 'payment_method_id': 'pm_expired'},
                ],
                'main_payment_method_id': 'pm_expired',
            },
            None,
            400,
            {
                'code': 'GENERAL',
                'message': '',
                'system_message': 'card has expired',
                'details': {},
            },
            False,
            id='expired',
        ),
        pytest.param(
            MOCK_UID,
            {'account_id': '1', 'revision': '1234'},
            {
                'payment_methods': [
                    {'type': 'card', 'payment_method_id': 'bad_id'},
                ],
                'main_payment_method_id': 'pm_id',
            },
            None,
            400,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'message': '',
                'system_message': 'expected 1 main payment method, found 0',
                'details': {},
            },
            False,
            id='bad_main_payment',
        ),
        pytest.param(
            MOCK_UID,
            {'account_id': '1', 'revision': '1234'},
            {},
            None,
            400,
            # todo:
            # {
            #     'code': 'REQUEST_VALIDATION_ERROR',
            #     'message': '',
            #     'system_message': 'Invalid input',
            #     'details': {
            #         '': [
            #             '\'payment_methods\' is a required property',
            #             '\'main_payment_method_id\' is a required property',
            #         ]
            #     },
            # },
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {'reason': 'payment_methods is required property'},
                'message': 'Some parameters are invalid',
            },
            False,
            id='empty_body',
        ),
        pytest.param(
            MOCK_UID,
            {'account_id': '1'},
            {
                'payment_methods': [
                    {'type': 'card', 'payment_method_id': 'pm_id'},
                ],
                'main_payment_method_id': 'pm_id',
            },
            None,
            400,
            # todo:
            # {
            #     'code': 'REQUEST_VALIDATION_ERROR',
            #     'message': '',
            #     'system_message': 'no parameter revision provided',
            #     'details': {},
            # },
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {'reason': 'revision is required parameter'},
                'message': 'Some parameters are invalid',
            },
            False,
            id='no_revision',
        ),
        pytest.param(
            MOCK_UID,
            {'account_id': '2', 'revision': '1234'},
            {
                'payment_methods': [
                    {'type': 'card', 'payment_method_id': 'pm_id'},
                ],
                'main_payment_method_id': 'pm_id',
            },
            None,
            409,
            {
                'code': 'GENERAL',
                'message': 'Имеются активные поездки',
                'details': {},
            },
            False,
            id='active_order',
        ),
        pytest.param(
            MOCK_UID_PASSPORT_FAMILY,
            {'account_id': '100', 'revision': 'revision1'},
            {
                'payment_methods': [
                    {'type': 'card', 'payment_method_id': 'pm_id7'},
                ],
                'main_payment_method_id': 'pm_id7',
            },
            None,
            200,
            {'revision': MOCK_ID},
            True,
            id='passport_family_card',
        ),
    ],
)
@pytest.mark.translations(
    client_messages={
        'shared_payments.change_locked_payment_method_error': {
            'ru': 'Нельзя поменять карту',
        },
        'shared_payments.found_active_order_error_change_payment': {
            'ru': 'Имеются активные поездки',
        },
    },
)
@pytest.mark.now('2019-01-05')
async def test_coop_acc_update_payment(
        web_app_client,
        web_context,
        mock_all_api,
        monkeypatch,
        patch,
        uid,
        params,
        body,
        expected_error,
        expected_status,
        expected_response,
        call_family_pay,
):
    monkeypatch.setattr('uuid.UUID.hex', MOCK_ID)

    @patch('taxi.clients.family_pay.FamilyPayClient.update_family_card')
    async def _update_family_card(*args, **kwargs):
        return

    response = await web_app_client.put(
        '/4.0/coop_account/payment',
        json=body,
        headers={
            **DEFAULT_HEADERS,
            UID_HEADER: uid,
            TVM_USER_TICKET_HEADER: 'ticket',
        },
        params=params,
    )
    content = await response.json()
    assert response.status == expected_status, content
    assert content == expected_response
    account = await accounts_repo.get_one_by_id(
        web_context, params['account_id'],
    )
    assert account.error_description == expected_error
    assert len(_update_family_card.calls) == int(call_family_pay)


@pytest.mark.parametrize(
    'uid, urls, expected_status, expected_response',
    [
        pytest.param(
            MOCK_UID,
            ['/4.0/coop_account/delete?account_id=1'],
            200,
            {},
            id='ok',
        ),
        pytest.param(
            MOCK_UID,
            ['/4.0/coop_account/delete?account_id=2'],
            409,
            {
                'code': 'GENERAL',
                'message': 'Имеются активные поездки',
                'details': {},
            },
            id='active_order',
        ),
        pytest.param(
            MOCK_UID,
            [
                '/4.0/coop_account/delete?account_id=1',
                '/4.0/coop_account/delete?account_id=1',
            ],
            200,
            {},
            id='double_delete_ok',
        ),
        pytest.param(
            MOCK_UID2,
            ['/4.0/coop_account/delete?account_id=17'],
            400,
            {
                'code': 'GENERAL',
                'message': 'Нельзя удалить аккаунт',
                'details': {},
            },
            id='no_delete_failed',
        ),
        pytest.param(
            MOCK_UID,
            ['/4.0/coop_account/delete?account_id=404'],
            404,
            {
                'code': 'GENERAL',
                'message': '',
                'system_message': 'account with id 404 does not exist',
                'details': {},
            },
            id='nonexistent_account_id',
        ),
        pytest.param(
            MOCK_UID,
            ['/4.0/coop_account/delete?account_id=403'],
            403,
            {
                'code': 'GENERAL',
                'message': '',
                'system_message': 'yandex_uid does not match owner_id',
                'details': {},
            },
            id='wrong_account_id',
        ),
    ],
)
@pytest.mark.translations(
    client_messages={
        'shared_payments.found_active_order_error_account': {
            'ru': 'Имеются активные поездки',
        },
        'shared_payments.delete_locked_account_error': {
            'ru': 'Нельзя удалить аккаунт',
        },
    },
)
async def test_coop_acc_delete(
        web_app_client, uid, urls, expected_status, expected_response,
):
    for url in urls:
        response = await web_app_client.delete(
            url, headers={**DEFAULT_HEADERS, UID_HEADER: uid},
        )
    content = await response.json()
    assert response.status == expected_status, content
    assert content == expected_response


@pytest.mark.config(COOP_ACCOUNT_CURRENCY_CODES=['RUB', 'EUR'])
@pytest.mark.parametrize(
    'uid, params, body, expected_status, expected_response',
    [
        pytest.param(
            MOCK_UID,
            {'account_id': '1'},
            {'code': 'RUB'},
            200,
            {
                'currency_rules': {
                    'code': 'RUB',
                    'template': '$VALUE$ $SIGN$$CURRENCY$',
                    'text': 'руб.',
                    'sign': '₽',
                },
            },
            id='ok',
        ),
        pytest.param(
            MOCK_UID2,
            {'account_id': '3'},
            {'code': 'RUB'},
            200,
            {
                'currency_rules': {
                    'code': 'RUB',
                    'template': '$VALUE$ $SIGN$$CURRENCY$',
                    'text': 'руб.',
                    'sign': '₽',
                },
            },
            id='already_selected_ok',
        ),
        pytest.param(
            MOCK_UID2,
            {'account_id': '3'},
            {'code': 'EUR'},
            409,
            {
                'code': 'GENERAL',
                'message': 'Валюта уже выбрана',
                'details': {},
            },
            id='already_selected_error',
        ),
        pytest.param(
            MOCK_UID,
            {'account_id': '1'},
            {'code': 'NOT'},
            404,
            {
                'code': 'GENERAL',
                'message': '',
                'system_message': 'currency NOT not found in config',
                'details': {},
            },
            id='currency_not_found',
        ),
    ],
)
@pytest.mark.translations(
    client_messages={
        'shared_payments.currency_selected_error': {
            'ru': 'Валюта уже выбрана',
        },
    },
    tariff={
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'currency.rub': {'ru': 'руб.'},
        'currency_sign.rub': {'ru': '₽'},
    },
)
async def test_coop_acc_set_currency(
        web_app_client,
        web_context,
        monkeypatch,
        uid,
        params,
        body,
        expected_status,
        expected_response,
):
    monkeypatch.setattr('uuid.UUID.hex', MOCK_ID)

    response = await web_app_client.put(
        '/4.0/coop_account/currency',
        json=body,
        headers={**DEFAULT_HEADERS, UID_HEADER: uid},
        params=params,
    )
    content = await response.json()
    assert response.status == expected_status, content
    assert content == expected_response
    account = await accounts_repo.get_one_by_id(
        web_context, params['account_id'],
    )

    if expected_status != 404:
        assert account.currency_code == 'RUB'


@pytest.mark.parametrize(
    'params, uid, body, expected_status, expected_response, email_id, next_report_date',
    [
        pytest.param(
            {'account_id': '2', 'revision': 'revision1'},
            MOCK_UID,
            {'email': 'alex manar a@m.ru', 'report_frequency': 'never'},
            200,
            {'revision': MOCK_ID},
            'id-a@m.ru',
            None,
            id='ok',
        ),
        pytest.param(
            {'account_id': '2', 'revision': 'other_revision'},
            MOCK_UID,
            {'email': 'corp@inc.com', 'report_frequency': 'never'},
            200,
            {'revision': 'revision1'},
            'id-corp@inc.com',
            None,
            id='no_change',
        ),
        pytest.param(
            {'account_id': '2', 'revision': 'revision1'},
            MOCK_UID,
            {
                'email': 'John Gowe corp@inc.com',
                'report_frequency': '0 0 1 * *',
            },
            200,
            {'revision': MOCK_ID},
            'id-corp@inc.com',
            datetime.datetime(2019, 2, 1, 0, 0),
            id='month_report',
        ),
        pytest.param(
            {'account_id': '2', 'revision': 'bad_revision'},
            MOCK_UID,
            {'email': 'a@m.ru', 'report_frequency': 'never'},
            409,
            {
                'code': 'GENERAL',
                'message': '',
                'system_message': 'revision id does not match',
                'details': {},
            },
            None,
            None,
            id='bad_revision',
        ),
        pytest.param(
            {'account_id': '2', 'revision': 'revision1'},
            MOCK_UID2,
            {'email': 'a@m.ru', 'report_frequency': 'never'},
            403,
            {
                'code': 'GENERAL',
                'message': '',
                'system_message': 'yandex_uid does not match owner_id',
                'details': {},
            },
            None,
            None,
            id='bad_owner',
        ),
        pytest.param(
            {'account_id': '2', 'revision': 'revision1'},
            MOCK_UID,
            {},
            400,
            # todo:{
            #     'code': 'REQUEST_VALIDATION_ERROR',
            #     'message': '',
            #     'system_message': 'Invalid input',
            #     'details': {
            #         '': [
            #             '\'email\' is a required property',
            #             '\'report_frequency\' is a required property',
            #         ]
            #     },
            # },
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {'reason': 'email is required property'},
                'message': 'Some parameters are invalid',
            },
            None,
            None,
            id='empty_body',
        ),
        pytest.param(
            {'account_id': '2'},
            MOCK_UID,
            {'email': 'a@m.ru', 'report_frequency': 'never'},
            400,
            # {
            #     'code': 'REQUEST_VALIDATION_ERROR',
            #     'message': '',
            #     'system_message': 'no parameter revision provided',
            #     'details': {},
            # },
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {'reason': 'revision is required parameter'},
                'message': 'Some parameters are invalid',
            },
            None,
            None,
            id='no_revision',
        ),
        pytest.param(
            {},
            MOCK_UID,
            {'email': 'a@m.ru', 'report_frequency': 'never'},
            400,
            # {
            #     'code': 'REQUEST_VALIDATION_ERROR',
            #     'message': '',
            #     'system_message': 'no parameter account_id provided',
            #     'details': {},
            # },
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {'reason': 'account_id is required parameter'},
                'message': 'Some parameters are invalid',
            },
            None,
            None,
            id='no_query',
        ),
        pytest.param(
            {'account_id': '2', 'revision': 'revision1'},
            MOCK_UID,
            {'email': 'a@m.ru', 'report_frequency': 'bad'},
            400,
            {
                'code': 'GENERAL',
                'message': '',
                'system_message': (
                    'bad is not one of' ' [\'never\', \'0 0 1 * *\']'
                ),
                'details': {},
            },
            None,
            None,
            id='bad_report_frequency',
        ),
        pytest.param(
            {'account_id': '2', 'revision': 'revision1'},
            MOCK_UID,
            {'email': 'smth a@m.ru invalid', 'report_frequency': 'never'},
            400,
            {
                'code': 'GENERAL',
                'details': {},
                'message': 'Неправильный формат email',
            },
            None,
            None,
            id='invalid_email',
        ),
    ],
)
@pytest.mark.config(
    COOP_ACCOUNT_SETTINGS=[
        {
            'type': 'business',
            'report_options': [
                {'title': 'never', 'code': 'never'},
                {'title': '1th every month', 'code': '0 0 1 * *'},
            ],
        },
    ],
    # todo: remove after fix client for personal
    TVM_RULES=[{'dst': 'personal', 'src': 'shared-payments'}],
)
@pytest.mark.translations(
    client_messages={
        'never': {'ru': 'never'},
        '1th every month': {'ru': '1th every month'},
        'shared_payments.invalid_email_error': {
            'ru': 'Неправильный формат email',
        },
    },
)
@pytest.mark.now('2019-01-05')
async def test_coop_acc_update_reports(
        web_app_client,
        web_context,
        monkeypatch,
        mock_all_api,
        params,
        uid,
        body,
        expected_status,
        expected_response,
        email_id,
        next_report_date,
):
    monkeypatch.setattr('uuid.UUID.hex', MOCK_ID)
    response = await web_app_client.put(
        '4.0/coop_account/reports',
        json=body,
        params=params,
        headers={**DEFAULT_HEADERS, UID_HEADER: uid},
    )
    content = await response.json()
    assert response.status == expected_status, content
    assert content == expected_response

    if expected_status == 200:
        account = await accounts_repo.get_one_by_id(
            web_context, params['account_id'],
        )
        assert account.email_id == email_id
        assert account.report_frequency == body['report_frequency']
        assert account.next_report_date == next_report_date


@pytest.mark.parametrize(
    'params, uid, body, expected_status, expected_response',
    [
        pytest.param(
            {'account_id': '1', 'revision': 'revision1'},
            MOCK_UID,
            {'limit_amount': 5000, 'has_specific_limit': True},
            200,
            {'revision': MOCK_ID},
            id='ok',
        ),
        pytest.param(
            {'account_id': '18', 'revision': 'revision1'},
            MOCK_UID3,
            {'limit_amount': 4000, 'has_specific_limit': True},
            200,
            {'revision': MOCK_ID},
            id='account_with_limit',
        ),
        pytest.param(
            {'account_id': '18', 'revision': 'revision1'},
            MOCK_UID3,
            {'has_specific_limit': False},
            200,
            {'revision': MOCK_ID},
            id='disable_limits',
        ),
        pytest.param(
            {'account_id': '1', 'revision': 'revision1'},
            MOCK_UID,
            {'has_specific_limit': False},
            200,
            {'revision': MOCK_ID},
            id='disable_limits_2',
        ),
    ],
)
@pytest.mark.config(
    COOP_ACCOUNT_SETTINGS=[{'type': 'family', 'set_limits': True}],
)
async def test_coop_acc_update_limit(
        web_app_client,
        web_context,
        monkeypatch,
        params,
        uid,
        body,
        expected_status,
        expected_response,
):
    monkeypatch.setattr('uuid.UUID.hex', MOCK_ID)

    response = await web_app_client.put(
        '4.0/coop_account/limit',
        json=body,
        params=params,
        headers={**DEFAULT_HEADERS, UID_HEADER: uid},
    )
    content = await response.json()
    assert response.status == expected_status, content
    assert content == expected_response

    account = await accounts_repo.get_one_by_id(
        web_context, params['account_id'],
    )

    if body['has_specific_limit']:
        assert account.limit_amount == body['limit_amount'] * (10 ** 4)
    assert account.has_specific_limit == body['has_specific_limit']

    members = await members_repo.get_members(web_context, params['account_id'])

    any_member = await members_repo.get_one_by_id(web_context, 'memb14')
    assert any_member.limit_amount == 12340000

    for member in members:
        if member.role == models.MemberRoles.OWNER:
            assert not member.limit_amount
            assert not member.has_specific_limit
        else:
            if body['has_specific_limit']:
                assert member.limit_amount == body['limit_amount'] * (10 ** 4)

            assert member.has_specific_limit == body['has_specific_limit']


@pytest.mark.parametrize(
    'uid,body,expected_response',
    [
        pytest.param('user777', {}, [], id='uid has no owned accounts'),
        pytest.param(
            MOCK_UID3,
            {},
            [{'type': 'family', 'account_id': '18'}],
            id='uid has one owned account',
        ),
        pytest.param(
            MOCK_UID,
            {},
            [
                {'type': 'family', 'account_id': '1'},
                {'type': 'business', 'account_id': '2'},
            ],
            id='uid has many owned accounts',
        ),
        pytest.param(
            MOCK_UID2,
            {'types': ['business']},
            [{'type': 'business', 'account_id': '3'}],
            id='uid has many owned accounts (filtered)',
        ),
    ],
)
async def test_coop_acc_list_simple(
        web_app_client, uid, body, expected_response,
):
    response = await web_app_client.post(
        '/4.0/coop_account/list', json=body, headers={UID_HEADER: uid},
    )
    assert response.status == 200
    content = await response.json()
    content.sort(key=lambda x: x['account_id'])
    assert content == expected_response


@pytest.mark.parametrize(
    'uid,expected_response',
    [
        pytest.param(
            MOCK_PORTAL_UID3,
            [{'type': 'family', 'account_id': '19'}],
            id='user4 bounded',
        ),
        pytest.param(
            MOCK_PORTAL_UID,
            [
                {'type': 'family', 'account_id': '1'},
                {'type': 'business', 'account_id': '2'},
            ],
            id='user1 bounded',
        ),
    ],
)
async def test_coop_acc_list_bound_uid(web_app_client, uid, expected_response):
    response = await web_app_client.post(
        '/4.0/coop_account/list', json={}, headers={UID_HEADER: uid},
    )
    assert response.status == 200
    content = await response.json()
    content.sort(key=lambda x: x['account_id'])
    assert content == expected_response
