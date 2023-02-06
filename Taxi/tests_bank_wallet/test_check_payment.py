import pytest

DEFAULT_YABANK_SESSION_UUID = 'session_uuid_1'
DEFAULT_YABANK_PHONE_ID = 'phone_id_1'
DEFAULT_YANDEX_BUID = 'buid_1'
DEFAULT_YANDEX_UID = 'uid_1'
DEFAULT_USER_TICKET = 'user_ticket_1'
DEFAULT_CARD_ID = '11111111-63aa-4838-9ec7-111111111111'
DEFAULT_AGREEMENT_ID = 'agreement_id_123'
DEFAULT_PUBLIC_AGREEMENT_ID = 'public_agreement_id_123'
DEFAULT_PHONE = '+70001002020'
DEFAULT_METHOD_PAYMENT_ID = 'd9abbfb7-84d4-44be-94b3-8f8ea7eb31df'

PAYMENT_CURRENCY = 'RUB'
PAYMENT_AMOUNT = '100'
BALANCE_AMOUNT_BIG = '1000'
BALANCE_AMOUNT_LITTLE = '50'


def default_headers():
    return {
        'X-YaBank-SessionUUID': DEFAULT_YABANK_SESSION_UUID,
        'X-YaBank-PhoneID': DEFAULT_YABANK_PHONE_ID,
        'X-Yandex-BUID': DEFAULT_YANDEX_BUID,
        'X-Yandex-UID': DEFAULT_YANDEX_UID,
        'X-Ya-User-Ticket': DEFAULT_USER_TICKET,
    }


def get_body(
        payment_method_id=DEFAULT_METHOD_PAYMENT_ID,
        amount=PAYMENT_AMOUNT,
        currency=PAYMENT_CURRENCY,
):
    return {
        'payment_method_id': payment_method_id,
        'money': {'amount': amount, 'currency': currency},
    }


def make_client_info(auth_level='ANONYMOUS'):
    return {'auth_level': auth_level, 'phone_number': DEFAULT_PHONE}


def make_card_mapping_info(
        public_agreement_id=DEFAULT_PUBLIC_AGREEMENT_ID,
        buid=DEFAULT_YANDEX_BUID,
        agreement_id=DEFAULT_AGREEMENT_ID,
):
    return {
        'card_id': DEFAULT_CARD_ID,
        'buid': buid,
        'agreement_id': agreement_id,
        'public_agreement_id': public_agreement_id,
    }


def make_limits_info(everytime='15000', month='40000'):
    return [
        {
            'name': 'MAX_TXN_SUM',
            'period': 'EVERYTIME',
            'operations': [],
            'owner': 'FINMON',
            'threshold': {'amount': {'amount': everytime, 'currency': 'RUB'}},
            'remaining': {'amount': {'amount': everytime, 'currency': 'RUB'}},
        },
        {
            'name': 'MAX_MONTHLY_TURNOVER',
            'period': 'MONTH',
            'operations': [],
            'owner': 'FINMON',
            'threshold': {'amount': {'amount': month, 'currency': 'RUB'}},
            'remaining': {'amount': {'amount': month, 'currency': 'RUB'}},
        },
    ]


def make_agreement_balance(
        amount=BALANCE_AMOUNT_BIG,
        currency=PAYMENT_CURRENCY,
        agreement_id=DEFAULT_PUBLIC_AGREEMENT_ID,
):
    return [
        {
            'agreement_id': agreement_id,
            'balance': {'amount': amount, 'currency': currency},
            'credit_limit': [],
            'debit_limit': [],
        },
    ]


@pytest.mark.parametrize('currency', ['EUR', 'USD'])
async def test_fail_if_not_rub_currency(taxi_bank_wallet, currency):

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/check_payment',
        headers=default_headers(),
        json=get_body(currency=currency),
    )

    assert response.status_code == 400


@pytest.mark.parametrize('amount', ['-100.00', '-10', '-0.01'])
async def test_fail_if_negative_amount(taxi_bank_wallet, amount):

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/check_payment',
        headers=default_headers(),
        json=get_body(amount='-100.00'),
    )

    assert response.status_code == 400


@pytest.mark.parametrize(
    'status, code, message',
    [
        (400, 'BAD_REQUEST', 'You wrong'),
        (404, 'NOT_FOUND', 'Card info not found'),
    ],
)
async def test_fail_if_make_card_mapping_info_by_trust_card_id_answer_with_err(
        mockserver, taxi_bank_wallet, status, code, message,
):
    @mockserver.json_handler(
        '/bank-core-card/v1/card/mapping/info/by-trust-card-id',
    )
    def _mock_card_mapping_info_by_trust_card_id(request):
        assert request.headers['X-Yandex-BUID'] == DEFAULT_YANDEX_BUID
        return mockserver.make_response(
            status=status, json={'code': code, 'message': message},
        )

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/check_payment',
        headers=default_headers(),
        json=get_body(),
    )

    assert response.status_code == status


async def test_fail_500_if_limit_get_list_answer_404(
        taxi_bank_wallet, mockserver, bank_core_card_mock,
):

    bank_core_card_mock.set_card_mapping_info(make_card_mapping_info())

    @mockserver.json_handler('/bank-core-statement/v1/limit/get/list')
    def _mock_limit_get_list(request):
        assert request.method == 'POST'
        assert request.headers['X-Yandex-BUID'] == DEFAULT_YANDEX_BUID
        assert (
            request.headers['X-YaBank-SessionUUID']
            == DEFAULT_YABANK_SESSION_UUID
        )
        return mockserver.make_response(
            status=404,
            json={'code': 'NOT_FOUND', 'message': 'Limits not found'},
        )

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/check_payment',
        headers=default_headers(),
        json=get_body(),
    )

    assert response.status_code == 500


async def test_fail_500_if_agreements_balance_get_answer_404(
        taxi_bank_wallet,
        mockserver,
        bank_core_card_mock,
        bank_core_statement_mock,
):
    bank_core_card_mock.set_card_mapping_info(make_card_mapping_info())
    bank_core_statement_mock.set_agreement_limits(make_limits_info())

    @mockserver.json_handler('/bank-core-statement/v1/agreements/balance/get')
    def _mock_get_agreements_balances(request):
        assert request.method == 'POST'
        assert request.headers['X-Yandex-BUID'] == DEFAULT_YANDEX_BUID
        assert (
            request.headers['X-YaBank-SessionUUID']
            == DEFAULT_YABANK_SESSION_UUID
        )
        return mockserver.make_response(
            status=404,
            json={'code': 'NOT_FOUND', 'message': 'Agreements not found'},
        )

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/check_payment',
        headers=default_headers(),
        json=get_body(),
    )

    assert response.status_code == 500


@pytest.mark.parametrize('currency', ['EUR', 'USD'])
async def test_fail_500_if_agreements_balance_is_not_rub(
        taxi_bank_wallet,
        bank_core_card_mock,
        bank_core_statement_mock,
        currency,
):
    bank_core_card_mock.set_card_mapping_info(make_card_mapping_info())
    bank_core_statement_mock.set_agreement_limits(make_limits_info())
    bank_core_statement_mock.set_agreements_balances(
        make_agreement_balance(amount=BALANCE_AMOUNT_BIG, currency=currency),
    )

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/check_payment',
        headers=default_headers(),
        json=get_body(),
    )

    assert response.status_code == 500


async def test_return_allowed_if_satisfy_limit_and_balance(
        taxi_bank_wallet, bank_core_card_mock, bank_core_statement_mock,
):
    bank_core_card_mock.set_card_mapping_info(make_card_mapping_info())
    bank_core_statement_mock.set_agreement_limits(make_limits_info())
    bank_core_statement_mock.set_agreements_balances(
        make_agreement_balance(BALANCE_AMOUNT_BIG),
    )

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/check_payment',
        headers=default_headers(),
        json=get_body(),
    )

    assert response.status_code == 200
    assert response.json() == {'resolution': 'ALLOWED'}


async def test_return_cond_topup(
        taxi_bank_wallet, bank_core_card_mock, bank_core_statement_mock,
):
    bank_core_card_mock.set_card_mapping_info(make_card_mapping_info())
    bank_core_statement_mock.set_agreement_limits(make_limits_info())
    bank_core_statement_mock.set_agreements_balances(
        make_agreement_balance(BALANCE_AMOUNT_LITTLE),
    )

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/check_payment',
        headers=default_headers(),
        json=get_body(),
    )

    assert response.status_code == 200
    assert response.json() == {
        'resolution': 'CONDITIONS',
        'condition': 'TOPUP',
    }


@pytest.mark.parametrize(
    'everytime_limit, month_limit', [('99', '1000'), ('1000', '99')],
)
async def test_fail_500_if_client_info_answer_404(
        taxi_bank_wallet,
        mockserver,
        bank_core_card_mock,
        bank_core_statement_mock,
        everytime_limit,
        month_limit,
):
    bank_core_card_mock.set_card_mapping_info(make_card_mapping_info())
    bank_core_statement_mock.set_agreement_limits(
        make_limits_info(everytime=everytime_limit, month=month_limit),
    )

    @mockserver.handler('/bank-core-client/v1/client/info/get')
    def _mock_client_info_get(request):
        return mockserver.make_response(
            status=404,
            json={'code': 'NOT_FOUND', 'message': 'Client not found'},
        )

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/check_payment',
        headers=default_headers(),
        json=get_body(),
    )

    assert response.status_code == 500


@pytest.mark.parametrize(
    'everytime_limit, month_limit', [('99', '1000'), ('1000', '99')],
)
async def test_return_cond_identification_if_pay_greater_current_limits(
        taxi_bank_wallet,
        bank_core_card_mock,
        bank_core_statement_mock,
        bank_core_client_mock,
        everytime_limit,
        month_limit,
):
    bank_core_card_mock.set_card_mapping_info(make_card_mapping_info())
    bank_core_statement_mock.set_agreement_limits(
        make_limits_info(everytime=everytime_limit, month=month_limit),
    )
    bank_core_client_mock.set_user_status()

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/check_payment',
        headers=default_headers(),
        json=get_body(),
    )

    assert not bank_core_statement_mock.agreements_balances_handler.has_calls
    assert response.status_code == 200
    assert response.json() == {
        'resolution': 'CONDITIONS',
        'condition': 'IDENTIFICATION',
    }


@pytest.mark.parametrize(
    'user_limits',
    [
        {
            'IDENTIFIED': {
                'DEBIT': {
                    'EVERYTIME': {'CNY': '60000'},
                    'MONTH': {'RUB': '200000'},
                },
            },
        },
        {
            'IDENTIFIED': {
                'DEBIT': {
                    'EVERYTIME': {'RUB': '60000'},
                    'MONTH': {'CNY': '200000'},
                },
            },
        },
        {
            'IDENTIFIED': {
                'CREDIT': {
                    'EVERYTIME': {'RUB': '60000'},
                    'MONTH': {'RUB': '200000'},
                },
            },
        },
        {
            'ANONYMOUS': {
                'DEBIT': {
                    'EVERYTIME': {'RUB': '60000'},
                    'MONTH': {'RUB': '200000'},
                },
            },
        },
        {
            'KYC': {
                'DEBIT': {
                    'EVERYTIME': {'RUB': '60000'},
                    'MONTH': {'RUB': '200000'},
                },
            },
        },
        {
            'KYC_EDS': {
                'DEBIT': {
                    'EVERYTIME': {'RUB': '60000'},
                    'MONTH': {'RUB': '200000'},
                },
            },
        },
    ],
)
async def test_fail_500_if_identified_limits_absent_in_config(
        taxi_config,
        taxi_bank_wallet,
        bank_core_card_mock,
        bank_core_statement_mock,
        bank_core_client_mock,
        user_limits,
):
    taxi_config.set_values({'BANK_WALLET_USER_LIMITS': user_limits})
    bank_core_card_mock.set_card_mapping_info(make_card_mapping_info())
    bank_core_statement_mock.set_agreement_limits(make_limits_info())
    bank_core_client_mock.set_user_status()

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/check_payment',
        headers=default_headers(),
        json=get_body(amount='65000'),
    )

    assert response.status_code == 500


async def test_return_denied_for_anonymous_if_pay_greater_identified_limits(
        taxi_bank_wallet,
        bank_core_card_mock,
        bank_core_statement_mock,
        bank_core_client_mock,
):
    bank_core_card_mock.set_card_mapping_info(make_card_mapping_info())
    bank_core_statement_mock.set_agreement_limits(make_limits_info())
    bank_core_client_mock.set_user_status()

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/check_payment',
        headers=default_headers(),
        json=get_body(amount='65000'),
    )

    assert not bank_core_statement_mock.agreements_balances_handler.has_calls
    assert response.status_code == 200
    assert response.json() == {'resolution': 'DENIED'}


@pytest.mark.parametrize('user_status', ['IDENTIFIED', 'KYC', 'KYC_EDS'])
async def test_return_denied_for_identified_if_pay_greater_current_limits(
        taxi_bank_wallet,
        bank_core_card_mock,
        bank_core_statement_mock,
        bank_core_client_mock,
        user_status,
):
    bank_core_card_mock.set_card_mapping_info(make_card_mapping_info())
    bank_core_statement_mock.set_agreement_limits(make_limits_info())
    bank_core_client_mock.set_user_status(user_status)

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/check_payment',
        headers=default_headers(),
        json=get_body(amount='65000'),
    )

    assert not bank_core_statement_mock.agreements_balances_handler.has_calls
    assert response.status_code == 200
    assert response.json() == {'resolution': 'DENIED'}
