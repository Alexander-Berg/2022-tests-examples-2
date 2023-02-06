from copy import deepcopy
import dataclasses
from typing import Optional

import pytest

ORDERCOMMIT_URL = '3.0/ordercommit'
ORDER_ID = 'order_id'
OFFER_ID = 'offer_id'
USER_IN_COMPLEMENT_EXP = 'user_id_with_cashback_plus'
USER_NOT_IN_COMPLEMENT_EXP = 'another_user_id'

COMPLEMENT = {
    'type': 'personal_wallet',
    'payment_method_id': 'wallet_id/1234567_RUB',
}
COMPLEMENTS = [COMPLEMENT]
WITHDRAW_COMPLEMENT = dict({'withdraw_amount': 99.99}, **COMPLEMENT)
WITHDRAW_COMPLEMENTS = [WITHDRAW_COMPLEMENT]
ANOTHER_COMPLEMENTS = [
    {
        'type': 'personal_wallet',
        'payment_method_id': 'wallet_id/1234567_RUB_1',
    },
]
COMPLEMENTS_KZT = [
    {'type': 'personal_wallet', 'payment_method_id': 'wallet_id/1234567_KZT'},
]
COMPLEMENTS_BYN = [
    {'type': 'personal_wallet', 'payment_method_id': 'wallet_id/1234567_BYN'},
]

DEFAULT_BALANCE = 300
PLUS_BALANCES_RESPONSE = {
    'balances': [
        {
            'wallet_id': 'wallet_id/1234567_RUB',
            'currency': 'RUB',
            'balance': str(DEFAULT_BALANCE),
        },
        {
            'wallet_id': 'wallet_id/1234567_KZT',
            'currency': 'KZT',
            'balance': '100500',
        },
    ],
}

pytestmark = [
    pytest.mark.now('2019-06-26T21:19:09+0300'),
    pytest.mark.order_experiments('fixed_price'),
    pytest.mark.experiments3(filename='experiments3.json'),
    pytest.mark.config(
        PERSONAL_WALLET_ENABLED=True,
        COMPLEMENT_TYPES_COMPATIBILITY_MAPPING={
            'personal_wallet': ['card', 'applepay', 'googlepay'],
        },
        PLUS_WALLET_PROTOCOL_BALANCES_ENABLED=True,
    ),
]


def plus_balances(mockserver, response_code, balance):
    if response_code != 200:
        return mockserver.make_response(status=response_code)
    response = deepcopy(PLUS_BALANCES_RESPONSE)
    response['balances'][0]['balance'] = str(balance)
    return response


@dataclasses.dataclass()
class PlusWalletContext:
    response_code: Optional[int]


@pytest.fixture
def plus_wallet_context():
    return PlusWalletContext(200)


@pytest.fixture(autouse=True)
def mock_plus_balances(mockserver, plus_wallet_context):
    @mockserver.json_handler('/plus_wallet/v1/balances')
    def mock_balances(request):
        assert request.args['yandex_uid'] == 'yandex_uid_with_cashback_plus'
        assert request.args['currencies'] == 'RUB'
        return plus_balances(
            mockserver, plus_wallet_context.response_code, DEFAULT_BALANCE,
        )


def test_complements_checks_ok(taxi_protocol, db, mockserver):
    request = {'id': 'user_id_with_cashback_plus', 'orderid': ORDER_ID}
    response = taxi_protocol.post(ORDERCOMMIT_URL, request)
    assert response.status_code == 200

    proc = db.order_proc.find_one(
        {'order.user_id': request['id'], '_id': request['orderid']},
    )
    assert proc['order']['request']['payment'] == {
        'payment_method_id': 'card-x5619',
        'type': 'card',
        'complements': [
            {
                'type': 'personal_wallet',
                'payment_method_id': 'wallet_id/1234567_RUB',
            },
        ],
    }
    assert proc['payment_tech']['complements'] == [
        {
            'type': 'personal_wallet',
            'payment_method_id': 'wallet_id/1234567_RUB',
        },
    ]


KEY_NO_CASHBACK_PLUS = (
    'DISABLED_PAYMENT_TYPE_PERSONAL_WALLET_IF_NO_CASHBACK_PLUS'
)


@pytest.mark.parametrize(
    'has_ya_plus,has_cashback_plus,status_code',
    [
        (False, False, 406),
        (True, False, 406),
        (False, True, 406),
        (True, True, 200),
    ],
)
@pytest.mark.config(DISABLE_PAYMENT_PERSONAL_WALLET_IF_NO_YA_PLUS=True)
@pytest.mark.translations(
    client_messages={
        'common_errors.DISABLED_PAYMENT_TYPE_PERSONAL_WALLET_IF_NO_YA_PLUS': {
            'ru': 'Вы не можете тратить кешбек без подписки Яндекс.Плюс',
        },
        ('common_errors.' + KEY_NO_CASHBACK_PLUS): {
            'ru': 'Нужно активировать подписку',
        },
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='disable_payment_personal_wallet_if_no_ya_plus',
    consumers=['protocol/ordercommit'],
    clauses=[
        {
            'title': '',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)
def test_complements_checks_cashback_plus(
        taxi_protocol,
        db,
        mockserver,
        has_ya_plus,
        has_cashback_plus,
        status_code,
):
    request = {'id': 'user_id_with_cashback_plus', 'orderid': ORDER_ID}
    if not has_ya_plus:
        db.users.update(
            {'_id': request['id']}, {'$unset': {'has_ya_plus': True}},
        )
    if not has_cashback_plus:
        db.users.update(
            {'_id': request['id']}, {'$unset': {'has_cashback_plus': True}},
        )
    response = taxi_protocol.post(ORDERCOMMIT_URL, request)
    json = response.json()
    assert response.status_code == status_code
    if has_ya_plus is False:
        assert json['error'] == {
            'code': 'DISABLED_PAYMENT_TYPE_PERSONAL_WALLET_IF_NO_YA_PLUS',
            'text': 'Вы не можете тратить кешбек без подписки Яндекс.Плюс',
        }
    if has_ya_plus and has_cashback_plus is False:
        assert json['error'] == {
            'code': KEY_NO_CASHBACK_PLUS,
            'text': 'Нужно активировать подписку',
        }


@pytest.mark.config(
    DISABLE_PAYMENT_PERSONAL_WALLET_IF_NO_YA_PLUS=True,
    CASHBACK_FOR_PLUS_COUNTRIES={'check_enabled': True, 'countries': []},
)
@pytest.mark.translations(
    client_messages={
        'common_errors.DISABLED_PAYMENT_TYPE_PERSONAL_WALLET_IF_NO_YA_PLUS': {
            'ru': 'Вы не можете тратить кешбек без подписки Яндекс.Плюс',
        },
        ('common_errors.' + KEY_NO_CASHBACK_PLUS): {
            'ru': 'Нужно активировать подписку',
        },
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='disable_payment_personal_wallet_if_no_ya_plus',
    consumers=['protocol/ordercommit'],
    clauses=[
        {
            'title': '',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)
def test_complements_checks_cashback_plus_not_allowed_country(taxi_protocol):
    request = {'id': 'user_id_with_cashback_plus', 'orderid': ORDER_ID}
    response = taxi_protocol.post(ORDERCOMMIT_URL, request)
    json = response.json()
    assert response.status_code == 406
    assert json['error'] == {
        'code': KEY_NO_CASHBACK_PLUS,
        'text': 'Нужно активировать подписку',
    }


@pytest.mark.parametrize(
    'order_complements, offer_complements, compare_ok',
    [
        (COMPLEMENTS, COMPLEMENTS, True),
        (COMPLEMENTS, None, False),
        (None, COMPLEMENTS, False),
        (None, None, True),
        (COMPLEMENTS, [], False),
        ([], COMPLEMENTS, False),
        (COMPLEMENTS, ANOTHER_COMPLEMENTS, False),
        (WITHDRAW_COMPLEMENTS, WITHDRAW_COMPLEMENTS, True),
        (WITHDRAW_COMPLEMENTS, [], False),
        (WITHDRAW_COMPLEMENTS, COMPLEMENTS, False),
        (COMPLEMENTS, WITHDRAW_COMPLEMENTS, False),
    ],
)
def test_complements_not_changed(
        taxi_protocol, db, order_complements, offer_complements, compare_ok,
):
    db.order_proc.update(
        {'_id': ORDER_ID},
        {'$set': {'order.request.payment.complements': order_complements}},
    )
    db.order_offers.update(
        {'_id': OFFER_ID}, {'$set': {'complements': offer_complements}},
    )
    request = {'id': USER_IN_COMPLEMENT_EXP, 'orderid': ORDER_ID}
    response = taxi_protocol.post(ORDERCOMMIT_URL, request)
    if compare_ok:
        assert response.status_code == 200
    else:
        assert response.status_code == 406
        json = response.json()
        assert json['error'] == {'code': 'COMPLEMENT_PAYMENT_CHANGED'}


def do_test_complement_unavailable(
        taxi_protocol, user_id=USER_IN_COMPLEMENT_EXP,
):
    request = {'id': user_id, 'orderid': ORDER_ID}
    response = taxi_protocol.post(ORDERCOMMIT_URL, request)
    assert response.status_code == 406
    json = response.json()
    assert json['error'] == {'code': 'COMPLEMENT_PERSONAL_WALLET_UNAVAILABLE'}


def test_complements_wrong_complements_size(taxi_protocol, db):
    db.order_proc.update(
        {'_id': ORDER_ID},
        {
            '$push': {
                'order.request.payment.complements': {
                    'type': 'personal_wallet',
                    'payment_method_id': 'wallet_id/1234567_RUB',
                },
            },
        },
    )
    db.order_offers.update(
        {'_id': OFFER_ID},
        {
            '$push': {
                'complements': {
                    'type': 'personal_wallet',
                    'payment_method_id': 'wallet_id/1234567_RUB',
                },
            },
        },
    )
    do_test_complement_unavailable(taxi_protocol)


def test_complements_wrong_complements_type(taxi_protocol, db):
    db.order_proc.update(
        {'_id': ORDER_ID},
        {'$set': {'order.request.payment.complements.0.type': 'card'}},
    )
    db.order_offers.update(
        {'_id': OFFER_ID}, {'$set': {'complements.0.type': 'card'}},
    )
    do_test_complement_unavailable(taxi_protocol)


def test_complements_pw_disabled_1(taxi_protocol, db):
    db.tariff_settings.update(
        {'hz': 'moscow'}, {'$pull': {'payment_options': 'personal_wallet'}},
    )
    do_test_complement_unavailable(taxi_protocol)


def test_complements_main_incompatible(taxi_protocol, db):
    db.order_proc.update(
        {'_id': ORDER_ID}, {'$set': {'order.request.payment.type': 'cash'}},
    )
    do_test_complement_unavailable(taxi_protocol)


def test_complements_pw_disabled_for_class(taxi_protocol, db):
    db.tariff_settings.update(
        {'hz': 'moscow'}, {'$set': {'s.0.rpt': ['card']}},
    )
    do_test_complement_unavailable(taxi_protocol)


@pytest.mark.parametrize(
    'complements, wallet_response, currency_ok',
    [
        (COMPLEMENTS, 200, True),
        (COMPLEMENTS_KZT, 200, False),
        (COMPLEMENTS_BYN, 200, False),
        (COMPLEMENTS, 429, False),
        (COMPLEMENTS, 500, False),
    ],
)
@pytest.mark.config(PERSONAL_WALLET_CHECK_CURRENCY=True)
def test_complements_currency(
        taxi_protocol,
        db,
        plus_wallet_context,
        complements,
        wallet_response,
        currency_ok,
):
    db.order_proc.update(
        {'_id': ORDER_ID},
        {'$set': {'order.request.payment.complements': complements}},
    )
    db.order_offers.update(
        {'_id': OFFER_ID}, {'$set': {'complements': complements}},
    )
    plus_wallet_context.response_code = wallet_response

    request = {'id': USER_IN_COMPLEMENT_EXP, 'orderid': ORDER_ID}
    response = taxi_protocol.post(ORDERCOMMIT_URL, request)
    if currency_ok:
        assert response.status_code == 200
    else:
        assert response.status_code == 406
        json = response.json()
        assert json['error'] == {
            'code': 'COMPLEMENT_PERSONAL_WALLET_UNAVAILABLE',
        }


@pytest.mark.config(PERSONAL_WALLET_CHECK_CURRENCY=False)
def test_complements_currency_config_disabled(taxi_protocol, db, mockserver):
    @mockserver.json_handler('/plus_wallet/v1/balances')
    def mock_plus_balances(mockserver):
        assert False

    db.order_proc.update(
        {'_id': ORDER_ID},
        {'$set': {'order.request.payment.complements': COMPLEMENTS_KZT}},
    )
    db.order_offers.update(
        {'_id': OFFER_ID}, {'$set': {'complements': COMPLEMENTS_KZT}},
    )
    request = {'id': USER_IN_COMPLEMENT_EXP, 'orderid': ORDER_ID}
    response = taxi_protocol.post(ORDERCOMMIT_URL, request)
    assert response.status_code == 200
