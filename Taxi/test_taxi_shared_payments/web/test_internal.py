# flake8: noqa
# pylint: disable=C0302
import datetime
import pytest
from typing import Optional
from typing import List

from testsuite.utils import ordered_object

from taxi_shared_payments.common import models
from taxi_shared_payments.controllers import passport_family
from taxi_shared_payments.repositories import accounts as accounts_repo
from taxi_shared_payments.repositories import debt_orders as debt_orders_repo

MOCK_UID = 'user1'
MOCK_UUID4 = 'some_uuid4'
MOCK_PORTAL_UID = 'portal_user1'
MOCK_PASSPORT_FAMILY_USER_UID = 'family_user_uid'
MOCK_UNEXISTING_UID = 'user404'
MOCK_PHONE_ID = '00aaaaaaaaaaaaaaaaaaaa01'
MOCK_UNEXISTING_PHONE_ID = '00aaaaaaaaaaaaaaaaaaa404'
MOCK_FOR_RIDES_UID = 'user_for_rides'
MOCK_USER_FOR_PASSPORT_FAMILY = 'user_with_passport_family'
MOCK_PHONE_ID_FAMILY = '00aaaaaaaaaaaaaaaaaaaa10'
MOCK_PHONE_ID_FAMILY_USER = '00aaaaaaaaaaaaaaaaaaaa12'

_NOW = datetime.datetime(2019, 12, 5, 00, 00)

UID_HEADER = 'X-Yandex-UID'

ACCEPT_LANGUAGE = {'Accept-Language': 'ru'}
REMOTE_IP = {'Remote-IP': 'amazing_ip'}


@pytest.mark.parametrize(
    'params, expected_status, expected_response, experiment_response',
    [
        pytest.param(
            {'owner_yandex_uid': MOCK_UID, 'phone_id': MOCK_PHONE_ID},
            200,
            {
                'accounts': [
                    {
                        'id': 'acc1',
                        'details': {
                            'name': 'Семейный аккаунт',
                            'color': 'FFFFFF',
                        },
                        'member_role': 'owner',
                        'type': 'family',
                        'is_active': True,
                        'description': '',
                        'has_rides': False,
                    },
                    {
                        'id': 'acc2',
                        'details': {'name': 'Ивановы Inc.', 'color': 'fff000'},
                        'member_role': 'owner',
                        'type': 'business',
                        'is_active': False,
                        'error_description': 'Нет способа оплаты',
                        'description': '',
                        'has_rides': True,
                    },
                ],
                'payment_methods': [
                    {
                        'id': 'acc1',
                        'type': 'family',
                        'details': {
                            'name': 'Семейный аккаунт',
                            'color': 'FFFFFF',
                        },
                        'member_role': 'owner',
                        'is_active': True,
                        'is_invitation_sent': True,
                        'accepted': True,
                        'description': 'Вы создатель',
                    },
                    {
                        'id': 'acc2',
                        'type': 'business',
                        'details': {'name': 'Ивановы Inc.', 'color': 'fff000'},
                        'member_role': 'user',
                        'is_active': False,
                        'is_invitation_sent': True,
                        'accepted': True,
                        'description': 'Осталось 70 из 100 евро',
                        'error_description': 'Нет способа оплаты',
                    },
                    {
                        'id': 'acc6',
                        'type': 'business',
                        'details': {'name': 'Портальный', 'color': 'fff000'},
                        'member_role': 'user',
                        'is_active': True,
                        'is_invitation_sent': True,
                        'accepted': True,
                        'description': 'Вы участник',
                    },
                ],
            },
            [],
            id='ok',
        ),
        pytest.param(
            {'owner_yandex_uid': MOCK_PORTAL_UID, 'phone_id': MOCK_PHONE_ID},
            200,
            {
                'accounts': [
                    {
                        'id': 'acc1',
                        'details': {
                            'name': 'Семейный аккаунт',
                            'color': 'FFFFFF',
                        },
                        'member_role': 'owner',
                        'type': 'family',
                        'is_active': True,
                        'description': '',
                        'has_rides': False,
                    },
                    {
                        'id': 'acc2',
                        'details': {'name': 'Ивановы Inc.', 'color': 'fff000'},
                        'member_role': 'owner',
                        'type': 'business',
                        'is_active': False,
                        'error_description': 'Нет способа оплаты',
                        'description': '',
                        'has_rides': True,
                    },
                    {
                        'id': 'acc6',
                        'details': {'name': 'Портальный', 'color': 'fff000'},
                        'member_role': 'owner',
                        'type': 'business',
                        'is_active': True,
                        'description': '',
                        'has_rides': False,
                    },
                ],
                'payment_methods': [
                    {
                        'id': 'acc1',
                        'type': 'family',
                        'details': {
                            'name': 'Семейный аккаунт',
                            'color': 'FFFFFF',
                        },
                        'member_role': 'owner',
                        'is_active': True,
                        'is_invitation_sent': True,
                        'accepted': True,
                        'description': 'Вы создатель',
                    },
                    {
                        'id': 'acc2',
                        'type': 'business',
                        'details': {'name': 'Ивановы Inc.', 'color': 'fff000'},
                        'member_role': 'user',
                        'is_active': False,
                        'is_invitation_sent': True,
                        'accepted': True,
                        'description': 'Осталось 70 из 100 евро',
                        'error_description': 'Нет способа оплаты',
                    },
                    {
                        'id': 'acc6',
                        'type': 'business',
                        'details': {'name': 'Портальный', 'color': 'fff000'},
                        'member_role': 'user',
                        'is_active': True,
                        'is_invitation_sent': True,
                        'accepted': True,
                        'description': 'Вы участник',
                    },
                ],
            },
            [
                {
                    'name': passport_family.EXPERIMENT_FAMILY_MIGRATE,
                    'value': {'enabled': True},
                },
            ],
            id='get_phonish_from_portal',
        ),
        pytest.param(
            {'owner_yandex_uid': MOCK_UID, 'phone_id': MOCK_PHONE_ID},
            200,
            {
                'accounts': [
                    {
                        'id': 'acc1',
                        'details': {
                            'name': 'Семейный аккаунт',
                            'color': 'FFFFFF',
                        },
                        'member_role': 'owner',
                        'type': 'family',
                        'is_active': True,
                        'description': '',
                        'has_rides': False,
                    },
                    {
                        'id': 'acc2',
                        'details': {'name': 'Ивановы Inc.', 'color': 'fff000'},
                        'member_role': 'owner',
                        'type': 'business',
                        'is_active': False,
                        'error_description': 'Нет способа оплаты',
                        'description': '',
                        'has_rides': True,
                    },
                ],
                'payment_methods': [
                    {
                        'id': 'acc1',
                        'type': 'family',
                        'details': {
                            'name': 'Семейный аккаунт',
                            'color': 'FFFFFF',
                        },
                        'member_role': 'owner',
                        'is_active': True,
                        'is_invitation_sent': True,
                        'accepted': True,
                        'description': 'Вы создатель',
                    },
                    {
                        'id': 'acc2',
                        'type': 'business',
                        'details': {'name': 'Ивановы Inc.', 'color': 'fff000'},
                        'member_role': 'user',
                        'is_active': False,
                        'is_invitation_sent': True,
                        'accepted': True,
                        'description': 'Осталось 70 из 100 евро',
                        'error_description': 'Нет способа оплаты',
                    },
                    {
                        'id': 'acc6',
                        'type': 'business',
                        'details': {'name': 'Портальный', 'color': 'fff000'},
                        'member_role': 'user',
                        'is_active': True,
                        'is_invitation_sent': True,
                        'accepted': True,
                        'description': 'Вы участник',
                    },
                ],
            },
            [],
            id='get_no_portal_from_phonish',
        ),
        pytest.param(
            {'owner_yandex_uid': MOCK_UID, 'phone_id': 'phone_unbound'},
            200,
            {
                'accounts': [
                    {
                        'id': 'acc1',
                        'details': {
                            'name': 'Семейный аккаунт',
                            'color': 'FFFFFF',
                        },
                        'member_role': 'owner',
                        'type': 'family',
                        'is_active': True,
                        'description': '',
                        'has_rides': False,
                    },
                    {
                        'id': 'acc2',
                        'details': {'name': 'Ивановы Inc.', 'color': 'fff000'},
                        'member_role': 'owner',
                        'type': 'business',
                        'is_active': False,
                        'error_description': 'Нет способа оплаты',
                        'description': '',
                        'has_rides': True,
                    },
                ],
                'payment_methods': [
                    {
                        'id': 'acc4',
                        'type': 'business',
                        'details': {
                            'name': 'С отвязанной картой',
                            'color': 'fff000',
                        },
                        'member_role': 'user',
                        'is_active': False,
                        'is_invitation_sent': True,
                        'accepted': True,
                        'description': 'Вы участник',
                        'error_description': 'Нет способа оплаты',
                    },
                ],
            },
            [],
            id='unbound_card',
        ),
        pytest.param(
            {
                'owner_yandex_uid': MOCK_UNEXISTING_UID,
                'phone_id': MOCK_UNEXISTING_PHONE_ID,
            },
            200,
            {'accounts': [], 'payment_methods': []},
            [],
            id='no_accounts',
        ),
        pytest.param(
            {
                'owner_yandex_uid': MOCK_UNEXISTING_UID,
                'phone_id': '00aaaaaaaaaaaaaaaaaaaa03',
            },
            200,
            {'accounts': [], 'payment_methods': []},
            [],
            id='deleted_member',
        ),
        pytest.param(
            {},
            400,
            # todo:
            # {
            #     'code': 'REQUEST_VALIDATION_ERROR',
            #     'message': '',
            #     'system_message': 'no parameter phone_id provided',
            #     'details': {},
            # },
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {'reason': 'phone_id is required parameter'},
                'message': 'Some parameters are invalid',
            },
            [],
            id='empty_phone_id',
        ),
        pytest.param(
            {'phone_id': MOCK_PHONE_ID},
            200,
            {
                'accounts': [],
                'payment_methods': [
                    {
                        'id': 'acc1',
                        'type': 'family',
                        'details': {
                            'name': 'Семейный аккаунт',
                            'color': 'FFFFFF',
                        },
                        'member_role': 'owner',
                        'is_active': True,
                        'is_invitation_sent': True,
                        'accepted': True,
                        'description': 'Вы создатель',
                    },
                    {
                        'id': 'acc6',
                        'type': 'business',
                        'details': {'name': 'Портальный', 'color': 'fff000'},
                        'member_role': 'user',
                        'is_active': True,
                        'is_invitation_sent': True,
                        'accepted': True,
                        'description': 'Вы участник',
                    },
                    {
                        'id': 'acc2',
                        'type': 'business',
                        'details': {'name': 'Ивановы Inc.', 'color': 'fff000'},
                        'member_role': 'user',
                        'is_active': False,
                        'is_invitation_sent': True,
                        'accepted': True,
                        'description': 'Осталось 70 из 100 евро',
                        'error_description': 'Нет способа оплаты',
                    },
                ],
            },
            [],
            id='empty_uid',
        ),
        pytest.param(
            {
                'owner_yandex_uid': MOCK_USER_FOR_PASSPORT_FAMILY,
                'phone_id': MOCK_PHONE_ID_FAMILY,
            },
            200,
            {
                'accounts': [
                    {
                        'id': 'acc_with_passport_family',
                        'details': {
                            'name': 'Семейный аккаунт',
                            'color': 'FFFFFF',
                            'passport_account': True,
                        },
                        'member_role': 'owner',
                        'type': 'family',
                        'is_active': True,
                        'description': '',
                        'has_rides': False,
                    },
                ],
                'payment_methods': [
                    {
                        'id': 'acc_with_passport_family',
                        'type': 'family',
                        'details': {
                            'name': 'Семейный аккаунт',
                            'color': 'FFFFFF',
                            'passport_account': True,
                        },
                        'member_role': 'owner',
                        'is_active': True,
                        'is_invitation_sent': True,
                        'accepted': True,
                        'description': 'Вы создатель',
                    },
                ],
            },
            [],
            id='new_fields_for_passport_family',
        ),
        pytest.param(
            {
                'phone_id': MOCK_PHONE_ID_FAMILY_USER,
                'owner_yandex_uid': MOCK_PASSPORT_FAMILY_USER_UID,
            },
            200,
            {
                'accounts': [],
                'payment_methods': [
                    {
                        'id': 'acc_with_passport_family',
                        'type': 'family',
                        'details': {
                            'name': 'Семейный аккаунт',
                            'color': 'FFFFFF',
                            'passport_account': True,
                        },
                        'member_role': 'user',
                        'is_active': True,
                        'is_invitation_sent': True,
                        'accepted': True,
                        'description': 'Осталось 50 из 100 руб.',
                    },
                ],
            },
            [],
            id='passport_family_user_description',
        ),
    ],
)
@pytest.mark.translations(
    client_messages={
        'shared_payments.you_are_owner': {'ru': 'Вы создатель'},
        'shared_payments.you_are_member': {'ru': 'Вы участник'},
        'shared_payments.default_account_name_family': {
            'ru': 'Семейный аккаунт',
        },
        'shared_payments.no_payment_method_error': {
            'ru': 'Нет способа оплаты',
        },
        'shared_payments.limit_reached_error': {'ru': 'Лимит исчерпан'},
        'shared_payments.card_expired_error': {
            'ru': 'Срок действия карты кончился',
        },
        'shared_payments.payment_failed_error': {'ru': 'Ошибка оплаты'},
        'shared_payments.limit_amount_left': {
            'ru': 'Осталось {balance} из {limit} {currency}',
        },
    },
    tariff={
        'currency.eur': {'ru': 'евро'},
        'currency.rub': {'ru': 'руб.'},
        # todo: поправить в currency_manager.py - _get_template -> (EUR == eur)
        'currency_with_sign.EUR': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'currency_sign.eur': {'ru': 'евро'},
    },
)
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.config(
    COOP_ACCOUNT_ENABLE_INVITATION=True,
    COOP_ACCOUNT_USE_SHIELD=True,
    # todo: без кодогенерации дефолт был такой, а сейчас дефолт пустой
    COOP_PAYMENT_ERROR_TANKER_KEYS={
        'no_payment_method': 'shared_payments.no_payment_method_error',
        'card_expired': 'shared_payments.card_expired_error',
        'payment_failed': 'shared_payments.payment_failed_error',
        'limit_reached': 'shared_payments.limit_reached_error',
    },
)
@pytest.mark.parametrize('family_card', ['family_user_uid'], indirect=True)
async def test_stats(
        web_app_client,
        mock_all_api,
        mockserver,
        stq,
        family_card,
        patch,
        params,
        expected_status,
        expected_response,
        experiment_response,
):
    @mockserver.json_handler('/experiments3/v1/experiments')
    def _handler(request):
        return {'items': experiment_response}

    @patch('taxi_shared_payments.repositories.cards.get_family_card')
    async def _get_family_card(*args, **kwargs):
        return family_card

    response = await web_app_client.get(
        '/internal/stats',
        headers={**ACCEPT_LANGUAGE, **REMOTE_IP},
        params=params,
    )
    content = await response.json()
    assert response.status == expected_status, content
    assert content == expected_response
    if experiment_response:
        assert stq.shared_payments_migrate_family_to_passport.times_called >= 1


@pytest.mark.parametrize(
    'acc_id, expected_code, expected_response',
    [
        pytest.param(
            'acc1',
            200,
            {
                'owner_uid': 'user1',
                'type': 'card',
                'payment_method_id': 'pm_1',
                'billing_id': '12345678',
                'persistent_id': 'label1',
            },
            id='ok',
        ),
        pytest.param(
            'acc6',
            200,
            {
                'owner_uid': 'user1',
                'type': 'card',
                'payment_method_id': 'pm_1',
                'billing_id': '12345678',
                'persistent_id': 'label1',
            },
            id='ok_portal',
        ),
        pytest.param(
            'acc4',
            200,
            {
                'owner_uid': 'user2',
                'type': 'card',
                'payment_method_id': 'pm_unbound',
                'billing_id': '12345670',
                'persistent_id': 'label2',
            },
            id='ok_unbound',
        ),
        pytest.param(
            'acc2',
            200,
            {
                'owner_uid': 'user1',
                'type': 'card',
                'payment_method_id': 'pm_1',
                'billing_id': '12345678',
                'persistent_id': 'label1',
            },
            id='ok_with_deleted_payment',
        ),
        pytest.param(
            'acc_limits',
            200,
            {
                'owner_uid': 'user3',
                'type': 'card',
                'payment_method_id': 'pm_deleted_1',
                'billing_id': '12345670',
                'persistent_id': 'label2',
            },
            id='ok_with_all_deleted_payment',
        ),
        pytest.param(
            'acc_invalid',
            404,
            {
                'code': 'GENERAL',
                'details': {},
                'message': '',
                'system_message': 'account with id acc_invalid does not exist',
            },
            id='not_found_account_id',
        ),
        pytest.param(
            'acc403',
            404,
            {
                'code': 'GENERAL',
                'details': {},
                'message': '',
                'system_message': (
                    'main payment method for account_id "acc403" not found'
                ),
            },
            id='not_found_payment_for_account_id',
        ),
        pytest.param(
            'acc_with_passport_family',
            200,
            {
                'owner_uid': 'payment.owner',
                'type': 'card',
                'payment_method_id': 'payment.card_id',
                'billing_id': 'payment.billing_card_id',
                'persistent_id': 'payment.persistent_id',
            },
            id='account_with_passport_family_success',
        ),
        pytest.param(
            'acc_with_passport_family_without_card',
            404,
            {
                'code': 'GENERAL',
                'details': {},
                'message': '',
                'system_message': (
                    'main payment method for account_id '
                    '"acc_with_passport_family_without_card" not found'
                ),
            },
            id='account_with_passport_family_failure',
        ),
    ],
)
@pytest.mark.parametrize(
    'url', ['/4.0/paymentmethod', '/internal/coop_account/paymentmethod'],
)
@pytest.mark.parametrize(
    'family_card', ['user_with_passport_family'], indirect=True,
)
async def test_paymentmethod(
        web_app_client,
        mock_all_api,
        patch,
        monkeypatch,
        family_card,
        acc_id,
        expected_code,
        expected_response,
        url,
):
    @patch('taxi_shared_payments.repositories.cards.get_family_card')
    async def _get_family_card(*args, **kwargs):
        if acc_id == 'acc_with_passport_family_without_card':
            return None
        return family_card

    monkeypatch.setattr('uuid.UUID.hex', MOCK_UUID4)

    response = await web_app_client.get(
        url,
        params={
            'account_id': acc_id,
            'yandex_uid': 'user_with_passport_family',
        },
    )
    content = await response.json()
    assert response.status == expected_code, content
    assert content == expected_response


async def _check_account_state(web_context, account_id: str, is_active: bool):
    account = await accounts_repo.get_one_by_id(web_context, account_id)
    assert account.is_active == is_active, account_id


@pytest.mark.parametrize(
    'urls, body, expected_status, expected_response',
    [
        pytest.param(
            ['/internal/coop_account/deactivate?account_id=acc1'],
            {'reason': 'payment_failed'},
            200,
            {},
            id='ok',
        ),
        pytest.param(
            [
                '/internal/coop_account/deactivate?account_id=acc1',
                '/internal/coop_account/deactivate?account_id=acc1',
            ],
            {'reason': 'payment_failed'},
            200,
            {},
            id='double_deactivate',
        ),
    ],
)
async def test_coop_acc_deactivate(
        web_app_client,
        web_context,
        urls,
        body,
        expected_status,
        expected_response,
):
    await _check_account_state(web_context, 'acc1', is_active=True)
    for url in urls:
        response = await web_app_client.post(url, json=body)
    content = await response.json()
    assert response.status == expected_status, content
    assert content == expected_response
    await _check_account_state(web_context, 'acc1', is_active=False)


async def test_coop_acc_activate(web_app_client, web_context):
    account_id = 'acc1'
    await accounts_repo.deactivate(
        web_context, account_id, models.AccountError.PAYMENT_FAILED,
    )
    await _check_account_state(web_context, account_id, is_active=False)
    response = await web_app_client.post(
        f'/internal/coop_account/activate?account_id={account_id}',
    )
    assert response.status == 200
    content = await response.json()
    assert content == {}
    await _check_account_state(web_context, account_id, is_active=True)


@pytest.mark.parametrize(
    'request_orders, orders_in_db',
    [
        pytest.param(
            ['order_a', 'order_b'],
            ['order_a', 'order_b'],
            id='add two different',
        ),
        pytest.param(
            ['order_a', 'order_a'], ['order_a'], id='add two the same',
        ),
    ],
)
async def test_smart_deactivation(
        web_app_client,
        web_context,
        request_orders: List[str],
        orders_in_db: List[str],
):
    account_id = 'acc1'
    await _check_account_state(web_context, account_id, is_active=True)
    for order_id in request_orders:
        response = await web_app_client.post(
            f'/internal/coop_account/deactivate?account_id={account_id}',
            json={'reason': 'payment_failed', 'debt_order_id': order_id},
        )
        assert response.status == 200, order_id
    await _check_account_state(web_context, account_id, is_active=False)
    account_debt_orders = await debt_orders_repo.find_all_for_account(
        web_context, account_id,
    )
    assert account_debt_orders == orders_in_db


@pytest.mark.parametrize(
    'db_orders_before, paied_order_id, db_orders_after, is_active',
    [
        pytest.param(['order_a'], 'order_a', [], True, id='normal'),
        pytest.param(
            ['order_a', 'order_b'],
            'order_a',
            ['order_b'],
            False,
            id='there are still orders in db',
        ),
        pytest.param(
            [], 'order_a', [], True, id='activate with nonexistent order',
        ),
        pytest.param(
            ['order_a', 'order_c'],
            None,
            [],
            True,
            id='activate without order',
        ),
    ],
)
async def test_smart_activation(
        web_app_client,
        web_context,
        db_orders_before: List[str],
        paied_order_id: str,
        db_orders_after: List[str],
        is_active: bool,
):
    account_id = 'acc1'
    for order_id in db_orders_before:
        await debt_orders_repo.insert(web_context, order_id, account_id)
    await accounts_repo.deactivate(
        web_context, account_id, models.AccountError.PAYMENT_FAILED,
    )
    await _check_account_state(web_context, account_id, False)
    response = await web_app_client.post(
        f'/internal/coop_account/activate?account_id={account_id}',
        json={'debt_order_id': paied_order_id},
    )
    assert response.status == 200
    await _check_account_state(web_context, account_id, is_active)
    account_debt_orders = await debt_orders_repo.find_all_for_account(
        web_context, account_id,
    )
    assert account_debt_orders == db_orders_after


@pytest.mark.translations(
    client_messages={
        'shared_payments.account_ride_limit_reached': {
            'ru': 'На вашем семейном акккаунте закончился лимит',
        },
        'shared_payments.member_ride_limit_reached': {
            'ru': 'У вас закончился лимит по семейным поездкам',
        },
    },
)
@pytest.mark.parametrize(
    'url, expected_status, expected_response',
    [
        pytest.param(
            '/internal/coop_account/check_available?'
            'account_id=acc1&phone_id=00aaaaaaaaaaaaaaaaaaaa01',
            200,
            {'available': True},
            id='available_true',
        ),
        pytest.param(
            '/internal/coop_account/check_available?'
            'account_id=acc2&phone_id=00aaaaaaaaaaaaaaaaaaaa01',
            200,
            {'available': False},
            id='available_false',
        ),
        pytest.param(
            '/internal/coop_account/check_available?'
            'account_id=acc1&phone_id=00aaaaaaaaaaaaaaaaaaaa02',
            200,
            {'available': False},
            id='available_with_member_limits',
        ),
        pytest.param(
            '/internal/coop_account/check_available?'
            'account_id=acc1&phone_id=00aaaaaaaaaaaaaaaaaaaa02&locale=ru',
            200,
            {
                'available': False,
                'reason': 'У вас закончился лимит по семейным поездкам',
            },
            id='available_with_member_limits',
        ),
        pytest.param(
            '/internal/coop_account/check_available?'
            'account_id=acc_limits&phone_id=00aaaaaaaaaaaaaaaaaaaa07',
            200,
            {'available': False},
            id='available_with_account_limits',
        ),
        pytest.param(
            '/internal/coop_account/check_available?'
            'account_id=acc_limits&phone_id=00aaaaaaaaaaaaaaaaaaaa07&locale=ru',
            200,
            {
                'available': False,
                'reason': 'На вашем семейном акккаунте закончился лимит',
            },
            id='available_with_account_limits',
        ),
        pytest.param(
            '/internal/coop_account/check_available?'
            'account_id=666&phone_id=00aaaaaaaaaaaaaaaaaaaa01',
            404,
            {
                'code': 'GENERAL',
                'details': {},
                'message': '',
                'system_message': 'account with id 666 does not exist',
            },
            id='available_error',
        ),
        pytest.param(
            '/internal/coop_account/check_available?'
            'account_id=acc1&phone_id=00aaaaaaaaaaaaaaaaaaaa66',
            404,
            {
                'code': 'GENERAL',
                'details': {},
                'message': '',
                'system_message': (
                    'member account_id=acc1, '
                    'phone_id=00aaaaaaaaaaaaaaaaaaaa66 '
                    'does not exist'
                ),
            },
            id='member_not_found',
        ),
        pytest.param(
            '/internal/coop_account/check_available?'
            'account_id=acc_with_passport_family&phone_id=00aaaaaaaaaaaaaaaaaaaa12&cost=50&yandex_uid=1234',
            200,
            {'available': True},
            id='passport_account__ride_with_small_cost',
        ),
        pytest.param(
            '/internal/coop_account/check_available?'
            'account_id=acc_with_passport_family&phone_id=00aaaaaaaaaaaaaaaaaaaa12&cost=51&yandex_uid=1234',
            200,
            {'available': False},
            id='passport_account__ride_with_large_cost',
        ),
    ],
)
@pytest.mark.now('2019-06-03T01:00:00')
@pytest.mark.parametrize(
    'family_card', ['acc_with_passport_family'], indirect=True,
)
async def test_coop_acc_is_available(
        web_app_client,
        family_card,
        patch,
        url,
        expected_status,
        expected_response,
):
    @patch('taxi_shared_payments.repositories.cards.get_family_card')
    async def _get_family_card(*args, **kwargs):
        return family_card

    response = await web_app_client.get(url)
    content = await response.json()
    assert response.status == expected_status, content
    assert content == expected_response


@pytest.mark.parametrize(
    'acc_id, expected_response, expected_code',
    [
        pytest.param(
            'acc1',
            {'yandex_uid': 'user1', 'phone_id': '00aaaaaaaaaaaaaaaaaaaa01'},
            200,
            id='ok',
        ),
        pytest.param(
            'acc6',
            {
                'code': 'GENERAL',
                'details': {},
                'message': '',
                'system_message': 'member account_id=acc6 does not exist',
            },
            404,
            id='error',
        ),
    ],
)
async def test_owner_info(
        web_app_client, acc_id, expected_response, expected_code,
):
    response = await web_app_client.get(
        '/internal/coop_account/owner_info', params={'account_id': acc_id},
    )
    content = await response.json()
    assert response.status == expected_code, content
    assert content == expected_response


@pytest.mark.parametrize(
    'body, response_file',
    [
        pytest.param(
            {
                'yandex_uid': MOCK_UID,
                'users': [
                    {
                        'id': 'id1',
                        'yandex_uid': MOCK_UID,
                        'phone_id': MOCK_PHONE_ID,
                    },
                ],
            },
            'takeout_response_ok.json',
            id='ok',
        ),
        pytest.param(
            {
                'yandex_uid': MOCK_UNEXISTING_UID,
                'users': [
                    {
                        'id': 'id1',
                        'yandex_uid': MOCK_UNEXISTING_UID,
                        'phone_id': MOCK_UNEXISTING_PHONE_ID,
                    },
                ],
            },
            'takeout_response_no_data.json',
            id='no_data',
        ),
    ],
)
@pytest.mark.config(USER_API_USE_USER_PHONES_RETRIEVAL_PY3=True)
async def test_takeout(
        web_app_client, mock_all_api, load_json, body, response_file,
):
    response = await web_app_client.post('/v1/internal/takeout', json=body)

    paths = [
        'data.owned_accounts',
        'data.owned_accounts.members',
        'data.used_accounts',
        'data.used_accounts.members',
    ]

    expected_response = ordered_object.order(load_json(response_file), paths)
    content = ordered_object.order(await response.json(), paths)

    assert expected_response == content


@pytest.mark.parametrize(
    'acc_id, expected_status',
    [
        ('nonexistent_id', 404),
        ('acc_with_rides', 200),
        ('acc_without_rides', 200),
        ('acc_deleted', 404),
    ],
)
async def test_post_account_order(
        web_app_client, web_context, pgsql, acc_id, expected_status,
):
    params = {'account_id': acc_id}
    body = {'order_id': 'id'}
    response = await web_app_client.post(
        '/internal/coop_account/order',
        params=params,
        headers={UID_HEADER: MOCK_FOR_RIDES_UID},
        json=body,
    )

    assert response.status == expected_status

    if expected_status == 200:
        account = await accounts_repo.get_one_by_id(web_context, acc_id)
        assert account.has_rides


@pytest.mark.parametrize(
    'account_id,expected_status,expected_has_rides',
    [
        pytest.param(
            'nonexistent_acc_id', 404, False, id='account doesn\'t exist',
        ),
        pytest.param('acc_with_rides', 200, True, id='has rides'),
        pytest.param(
            'acc_without_rides', 200, False, id='doesn\'t have rides',
        ),
        pytest.param('acc_deleted', 404, False, id='deleted account'),
    ],
)
async def test_get_account_short_info(
        web_app_client, account_id, expected_status, expected_has_rides,
):
    params = {'account_id': account_id}
    response = await web_app_client.get(
        '/internal/coop_account/short_info',
        params=params,
        headers={UID_HEADER: MOCK_FOR_RIDES_UID},
    )

    assert response.status == expected_status
    if expected_status == 200:
        data = await response.json()
        assert data['has_rides'] == expected_has_rides


@pytest.mark.parametrize(
    'account_id, expected_code, expected_response',
    [
        pytest.param('acc_invalid', 404, None, id='account does not exist'),
        pytest.param('acc403', 404, None, id='no payment method for account'),
        pytest.param(
            'acc1',
            200,
            {
                'account_type': 'family',
                'owner_uid': 'user1',
                'payment_method_id': 'pm_1',
                'payment_method_type': 'card',
            },
            id='ok',
        ),
        pytest.param(
            'acc6',
            200,
            {
                'account_type': 'business',
                'owner_uid': 'portal_user1',
                'payment_method_id': 'pm_1',
                'payment_method_type': 'card',
            },
            id='ok_portal',
        ),
    ],
)
async def test_get_paymentmethod_short_info(
        web_app_client, account_id, expected_code, expected_response,
):
    response = await web_app_client.get(
        '/internal/coop_account/paymentmethod/short_info',
        params={'account_id': account_id},
    )

    assert response.status == expected_code
    if expected_code == 200:
        response_json = await response.json()
        assert response_json == expected_response


@pytest.mark.parametrize(
    'account_id,expected_status,expected_resp',
    [
        pytest.param(
            'nonexistent_acc_id', 404, None, id='account doesn\'t exist',
        ),
        pytest.param(
            'acc_with_rides',
            200,
            {
                'type': 'family',
                'details': {'color': 'FFFFFF', 'name': 'Семейный аккаунт'},
            },
            id='family account',
        ),
        pytest.param(
            'acc2',
            200,
            {
                'type': 'business',
                'details': {'color': 'fff000', 'name': 'Ивановы Inc.'},
            },
            id='business with name',
        ),
        pytest.param(
            'acc_wo_name',
            200,
            {
                'type': 'business',
                'details': {'color': 'fff000', 'name': 'Бизнес аккаунт'},
            },
            id='business without name',
        ),
        pytest.param(
            'acc_deleted',
            200,
            {
                'type': 'family',
                'details': {'color': 'FFFFFF', 'name': 'Семейный аккаунт'},
            },
            id='deleted account',
        ),
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
    },
)
async def test_get_history(
        taxi_shared_payments_web, account_id, expected_status, expected_resp,
):
    response = await taxi_shared_payments_web.get(
        '/internal/coop_account/history_info',
        params={'account_id': account_id},
        headers={'X-Request-Language': 'ru'},
    )

    assert response.status == expected_status
    if expected_status == 200:
        data = await response.json()
        assert data == expected_resp
