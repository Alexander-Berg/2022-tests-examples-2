import json

import pytest

from tests_bank_topup import common


def default_headers():
    return {
        'X-Yandex-UID': 'uid',
        'X-Yandex-BUID': 'buid',
        'X-YaBank-SessionUUID': 'session_uuid',
        'X-YaBank-PhoneID': 'phone_id',
        'X-Remote-Ip': 'remote_ip',
        'X-Idempotency-Token': '67754336-d4d1-43c1-aadb-cabd06674ea6',
        'X-Ya-User-Ticket': 'user_ticket',
    }


class HandleInfo:
    def __init__(
            self,
            version,
            path,
            balance_id_key,
            balance_id_pg_key,
            balance_id_pg_value,
            body,
            db_balance_fields,
            db_balance_values,
    ):
        self.version = version
        self.path = path
        self.balance_id_key = balance_id_key
        self.balance_id_pg_key = balance_id_pg_key
        self.balance_id_pg_value = balance_id_pg_value
        self.body = body
        self.db_balance_fields = db_balance_fields
        self.db_balance_values = db_balance_values


def get_v1_handle_info():
    return HandleInfo(
        1,
        '/v1/topup/v1/payment',
        'wallet_id',
        'wallet_id',
        common.TEST_WALLET_ID,
        {
            'money': {
                'amount': '100',
                'currency': 'RUB',
                'wallet_id': common.TEST_WALLET_ID,
            },
        },
        'public_agreement_id, wallet_id',
        f'\'{common.DEFAULT_PUBLIC_AGREEMENT_ID}\', \'{common.TEST_WALLET_ID}\'',
    )


def get_v2_handle_info():
    return HandleInfo(
        2,
        '/v1/topup/v2/payment',
        'agreement_id',
        'public_agreement_id',
        common.DEFAULT_PUBLIC_AGREEMENT_ID,
        {
            'money': {'amount': '100', 'currency': 'RUB'},
            'agreement_id': common.DEFAULT_PUBLIC_AGREEMENT_ID,
        },
        'public_agreement_id',
        f'\'{common.DEFAULT_PUBLIC_AGREEMENT_ID}\'',
    )


def _default_bank_core_statement_response(handle_info):
    def get_balance(amount, currency, wallet_id):
        return {'amount': amount, 'currency': currency, 'wallet_id': wallet_id}

    def get_limit(currency, threshold, remaining='0'):
        return {
            'period_start': '2020-08-01T00:00:00+00:00',
            'period': 'MONTH',
            'threshold': {'amount': threshold, 'currency': currency},
            'remaining': {'amount': remaining, 'currency': currency},
        }

    root_key = 'wallets' if handle_info.version == 1 else 'agreements'
    return {
        root_key: [
            {
                'balance': get_balance('20', 'RUB', '123456'),
                'debit_limit': [
                    get_limit('RUB', '40000'),
                    get_limit('RUB', '15000'),
                ],
                'credit_limit': [
                    get_limit('RUB', '40000'),
                    get_limit('RUB', '15000'),
                ],
                'public_agreement_id': '123456',
                'agreement_id': '123456',
                'id': '123456',
            },
            {
                'balance': get_balance('20', 'USD', '2'),
                'debit_limit': [get_limit('USD', '40000')],
                'credit_limit': [get_limit('USD', '15000')],
                'public_agreement_id': '2',
                'agreement_id': '2',
                'id': '2',
            },
            {
                'balance': get_balance('20', 'RUB', '3'),
                'debit_limit': [get_limit('RUB', '40000')],
                'credit_limit': [get_limit('RUB', '15000')],
                'public_agreement_id': '3',
                'agreement_id': '3',
                'id': '3',
            },
        ],
    }


def json_mock_trust(request, show_trust_payment_id=True):
    assert request.headers['X-Uid'] == 'uid'
    basket = {'purchase_token': 'token'}
    if (
            show_trust_payment_id
            and request.json.get('show_trust_payment_id', 0) == 1
    ):
        basket['trust_payment_id'] = common.DEFAULT_PAYMENT_METHOD_ID
    return basket


CUSTOMIZED_FORM_FIELDS = {
    'auto_start_payment': True,
    'payment_completion_action': 'spin',
    'blocks_visibility': {'cardSelector': False, 'payment_button_logo': False},
    'email': 'robot-fintechmobtc@yandex-team.ru',
    'ya_logo': 'yandex',
    'show_payment_user': False,
}


@pytest.mark.config(BANK_TOPUP_CUSTOMIZED_FORM_FIELDS=CUSTOMIZED_FORM_FIELDS)
@pytest.mark.parametrize('selected_card_id', [None, 'card_id'])
async def test_ok(
        mockserver,
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_core_client_mock,
        bank_core_agreement_mock,
        pgsql,
        selected_card_id,
):
    @mockserver.json_handler('/bank-trust-payments/trust-payments/v2/payments')
    def _mock_trust(request):
        dev_payload = request.json.get('developer_payload')
        if selected_card_id:
            expected_dev_payload = CUSTOMIZED_FORM_FIELDS.copy()
            expected_dev_payload.update({'selected_card_id': selected_card_id})
            assert json.loads(dev_payload) == expected_dev_payload
        else:
            assert not dev_payload
        return mockserver.make_response(
            status=201, json=json_mock_trust(request),
        )

    @mockserver.json_handler(
        r'/stq-agent/queues/api/add/(?P<queue_name>\w+)', regex=True,
    )
    def _mock_stq_schedule(request, queue_name):
        return {}

    handle_info = get_v2_handle_info()
    bank_core_statement_mock.set_balance_get_response(
        _default_bank_core_statement_response(handle_info),
    )

    if selected_card_id:
        handle_info.body['selected_card_id'] = selected_card_id
    response = await taxi_bank_topup.post(
        handle_info.path, headers=default_headers(), json=handle_info.body,
    )

    assert response.status == 200
    assert bank_core_statement_mock.balance_handler_has_calls()
    assert _mock_trust.has_calls
    assert _mock_stq_schedule.has_calls
    stq_schedule_next_call = _mock_stq_schedule.next_call()
    stq_request_body = stq_schedule_next_call['request'].json
    stq_queue_name = stq_schedule_next_call['queue_name']
    assert stq_queue_name == 'bank_topup_payment_status_trust'
    assert stq_request_body['task_id'].startswith('bank_topup_')
    assert 'payment_id' in stq_request_body['kwargs']

    payment = common.get_payment_info(
        pgsql, stq_request_body['kwargs']['payment_id'],
    )
    assert payment['bank_uid'] == 'buid'
    assert payment['yandex_uid'] == 'uid'
    assert payment['client_ip'] == 'remote_ip'
    assert payment['session_uuid'] == 'session_uuid'
    assert (
        payment[handle_info.balance_id_pg_key]
        == handle_info.balance_id_pg_value
    )
    assert payment['public_agreement_id'] == common.DEFAULT_PUBLIC_AGREEMENT_ID

    assert response.json().get('purchase_token') == 'token'


@pytest.mark.parametrize(
    'handle_info', [get_v1_handle_info(), get_v2_handle_info()],
)
async def test_no_trust_payment_id(
        mockserver,
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_core_client_mock,
        bank_core_agreement_mock,
        handle_info,
):
    @mockserver.json_handler('/bank-trust-payments/trust-payments/v2/payments')
    def _mock_trust(request):
        return mockserver.make_response(
            status=201,
            json=json_mock_trust(request, show_trust_payment_id=False),
        )

    @mockserver.json_handler(
        r'/stq-agent/queues/api/add/(?P<queue_name>\w+)', regex=True,
    )
    def _mock_stq_schedule(request, queue_name):
        return {}

    bank_core_statement_mock.set_balance_get_response(
        _default_bank_core_statement_response(handle_info),
    )

    response = await taxi_bank_topup.post(
        handle_info.path, headers=default_headers(), json=handle_info.body,
    )

    assert response.status == 500
    assert bank_core_statement_mock.balance_handler_has_calls()
    assert _mock_trust.has_calls


@pytest.mark.parametrize(
    'handle_info', [get_v1_handle_info(), get_v2_handle_info()],
)
async def test_bad_body_no_amount(
        mockserver,
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_core_client_mock,
        bank_core_agreement_mock,
        handle_info,
):
    @mockserver.json_handler('/bank-trust-payments/trust-payments/v2/payments')
    def _mock_trust(request):
        return mockserver.make_response(status=400, json={'status': 'error'})

    json_body = handle_info.body
    json_body['money'].pop('amount')
    response = await taxi_bank_topup.post(
        handle_info.path, headers=default_headers(), json=json_body,
    )

    assert response.status == 400
    assert not bank_core_statement_mock.balance_handler_has_calls()
    assert not _mock_trust.has_calls


@pytest.mark.parametrize(
    'handle_info', [get_v1_handle_info(), get_v2_handle_info()],
)
async def test_bad_headers(
        mockserver,
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_core_client_mock,
        bank_core_agreement_mock,
        handle_info,
):
    @mockserver.json_handler('/bank-trust-payments/trust-payments/v2/payments')
    def _mock_trust(request):
        return mockserver.make_response(status=400, json={'status': 'error'})

    headers = default_headers()
    headers.pop('X-Idempotency-Token')
    response = await taxi_bank_topup.post(
        handle_info.path, headers=headers, json=handle_info.body,
    )

    assert response.status == 400
    assert not bank_core_statement_mock.balance_handler_has_calls()
    assert not _mock_trust.has_calls


@pytest.mark.parametrize(
    'handle_info', [get_v1_handle_info(), get_v2_handle_info()],
)
async def test_trust_returned_400(
        mockserver,
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_core_client_mock,
        bank_core_agreement_mock,
        handle_info,
):
    @mockserver.json_handler('/bank-trust-payments/trust-payments/v2/payments')
    def _mock_trust(request):
        return mockserver.make_response(
            status=400, json={'status': 'error', 'status_code': 'bad data'},
        )

    bank_core_statement_mock.set_balance_get_response(
        _default_bank_core_statement_response(handle_info),
    )

    response = await taxi_bank_topup.post(
        handle_info.path, headers=default_headers(), json=handle_info.body,
    )

    assert response.status == 500
    assert bank_core_statement_mock.balance_handler_has_calls()
    assert _mock_trust.has_calls


@pytest.mark.parametrize(
    'handle_info', [get_v1_handle_info(), get_v2_handle_info()],
)
async def test_trust_returned_500(
        mockserver,
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_core_client_mock,
        bank_core_agreement_mock,
        handle_info,
):
    @mockserver.json_handler('/bank-trust-payments/trust-payments/v2/payments')
    def _mock_trust(request):
        return mockserver.make_response(status=500, json={'status': 'error'})

    bank_core_statement_mock.set_balance_get_response(
        _default_bank_core_statement_response(handle_info),
    )

    response = await taxi_bank_topup.post(
        handle_info.path, headers=default_headers(), json=handle_info.body,
    )

    assert response.status == 500
    assert bank_core_statement_mock.balance_handler_has_calls()
    assert _mock_trust.has_calls


@pytest.mark.parametrize(
    'handle_info', [get_v1_handle_info(), get_v2_handle_info()],
)
async def test_idempotency_same_token_same_data(
        mockserver,
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_core_client_mock,
        bank_core_agreement_mock,
        handle_info,
):
    @mockserver.json_handler('/bank-trust-payments/trust-payments/v2/payments')
    def _mock_trust(request):
        return mockserver.make_response(
            status=201, json=json_mock_trust(request),
        )

    bank_core_statement_mock.set_balance_get_response(
        _default_bank_core_statement_response(handle_info),
    )

    headers = default_headers()
    json_body = handle_info.body
    response = await taxi_bank_topup.post(
        handle_info.path, headers=headers, json=json_body,
    )

    assert response.status == 200
    assert _mock_trust.times_called == 1
    assert response.json().get('purchase_token') == 'token'

    response = await taxi_bank_topup.post(
        handle_info.path, headers=headers, json=json_body,
    )

    assert response.status == 200
    assert bank_core_statement_mock.balance_handler_has_calls()
    assert _mock_trust.times_called == 1


@pytest.mark.parametrize(
    'handle_info', [get_v1_handle_info(), get_v2_handle_info()],
)
async def test_idempotency_same_token_different_data(
        mockserver,
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_core_client_mock,
        bank_core_agreement_mock,
        handle_info,
):
    @mockserver.json_handler('/bank-trust-payments/trust-payments/v2/payments')
    def _mock_trust(request):
        return mockserver.make_response(
            status=201, json=json_mock_trust(request),
        )

    bank_core_statement_mock.set_balance_get_response(
        _default_bank_core_statement_response(handle_info),
    )

    response = await taxi_bank_topup.post(
        handle_info.path, headers=default_headers(), json=handle_info.body,
    )

    assert response.status == 200
    assert bank_core_statement_mock.balance_handler_has_calls()
    assert _mock_trust.times_called == 1

    json_body = handle_info.body
    json_body['money']['amount'] = '200'
    response = await taxi_bank_topup.post(
        handle_info.path, headers=default_headers(), json=json_body,
    )

    assert response.status == 400
    assert bank_core_statement_mock.balance_handler_has_calls()
    assert _mock_trust.times_called == 1


@pytest.mark.parametrize(
    'handle_info', [get_v1_handle_info(), get_v2_handle_info()],
)
async def test_idempotency_different_token(
        mockserver,
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_core_client_mock,
        bank_core_agreement_mock,
        handle_info,
):
    @mockserver.json_handler('/bank-trust-payments/trust-payments/v2/payments')
    def _mock_trust(request):
        return mockserver.make_response(
            status=201, json=json_mock_trust(request),
        )

    bank_core_statement_mock.set_balance_get_response(
        _default_bank_core_statement_response(handle_info),
    )

    response = await taxi_bank_topup.post(
        handle_info.path, headers=default_headers(), json=handle_info.body,
    )

    assert response.status == 200
    assert bank_core_statement_mock.balance_handler_has_calls()
    assert _mock_trust.times_called == 1

    headers = default_headers()
    headers['X-Idempotency-Token'] = '67754336-d4d1-43c1-aadb-cabd06674ea5'
    response = await taxi_bank_topup.post(
        handle_info.path, headers=headers, json=handle_info.body,
    )

    assert response.status == 200
    assert bank_core_statement_mock.balance_handler_has_calls()
    assert _mock_trust.times_called == 2


@pytest.mark.parametrize(
    'handle_info', [get_v1_handle_info(), get_v2_handle_info()],
)
async def test_race_same_request(
        mockserver,
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_core_client_mock,
        bank_core_agreement_mock,
        pgsql,
        testpoint,
        handle_info,
):
    @mockserver.json_handler('/bank-trust-payments/trust-payments/v2/payments')
    def _mock_trust(request):
        return mockserver.make_response(
            status=201, json=json_mock_trust(request),
        )

    @testpoint('create_payment')
    def _create_payment(stats):

        query = (
            f'INSERT INTO bank_topup.payments '
            f'(bank_uid, yandex_uid, idempotency_token, amount, '
            f'currency, {handle_info.db_balance_fields}, '
            f'purchase_token, trust_payment_id,'
            f'session_uuid, client_ip) '
            f'VALUES (\'buid\', \'yandex_uid\', '
            f'\'67754336-d4d1-43c1-aadb-cabd06674ea6\', '
            f'\'100\', \'RUB\', {handle_info.db_balance_values}, \'token1\', '
            f'\'{common.DEFAULT_PAYMENT_METHOD_ID}\','
            f'\'session_uuid\', \'client_ip\');'
        )

        cursor = pgsql['bank_topup'].cursor()
        cursor.execute(query)

    bank_core_statement_mock.set_balance_get_response(
        _default_bank_core_statement_response(handle_info),
    )

    response = await taxi_bank_topup.post(
        handle_info.path, headers=default_headers(), json=handle_info.body,
    )

    assert response.status == 200
    assert bank_core_statement_mock.balance_handler_has_calls()
    assert response.json().get('purchase_token') == 'token1'


@pytest.mark.parametrize(
    'handle_info', [get_v1_handle_info(), get_v2_handle_info()],
)
async def test_race_different_request(
        mockserver,
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_core_client_mock,
        bank_core_agreement_mock,
        pgsql,
        testpoint,
        handle_info,
):
    @mockserver.json_handler('/bank-trust-payments/trust-payments/v2/payments')
    def _mock_trust(request):
        return mockserver.make_response(
            status=201, json=json_mock_trust(request),
        )

    @testpoint('create_payment')
    def _create_payment(stats):
        cursor = pgsql['bank_topup'].cursor()
        cursor.execute(
            (
                f'INSERT INTO bank_topup.payments '
                f'(bank_uid, yandex_uid, idempotency_token, amount, '
                f'currency, {handle_info.db_balance_fields}, '
                f'purchase_token, trust_payment_id, '
                f'session_uuid, client_ip) '
                f'VALUES (\'buid\', \'yandex_uid\', '
                f'\'67754336-d4d1-43c1-aadb-cabd06674ea6\', '
                f'\'200\', \'RUB\', {handle_info.db_balance_values}, '
                f'\'token1\', '
                f'\'{common.DEFAULT_PAYMENT_METHOD_ID}\','
                f'\'session_uuid\', \'client_ip\');'
            ),
        )

    bank_core_statement_mock.set_balance_get_response(
        _default_bank_core_statement_response(handle_info),
    )

    response = await taxi_bank_topup.post(
        handle_info.path, headers=default_headers(), json=handle_info.body,
    )

    assert response.status == 400
    assert bank_core_statement_mock.balance_handler_has_calls()


@pytest.mark.parametrize(
    'handle_info', [get_v1_handle_info(), get_v2_handle_info()],
)
async def test_small_amount(
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_core_client_mock,
        bank_core_agreement_mock,
        handle_info,
):
    bank_core_statement_mock.set_balance_get_response(
        _default_bank_core_statement_response(handle_info),
    )

    json_body = handle_info.body
    json_body['money']['amount'] = '90'
    response = await taxi_bank_topup.post(
        handle_info.path, headers=default_headers(), json=json_body,
    )

    assert response.status_code == 400
    assert bank_core_statement_mock.balance_handler_has_calls()


@pytest.mark.parametrize(
    'handle_info', [get_v1_handle_info(), get_v2_handle_info()],
)
@pytest.mark.config(BANK_TOPUP_WALLET_MIN_LIMITS={})
async def test_no_limit(
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_core_client_mock,
        mockserver,
        bank_core_agreement_mock,
        handle_info,
):
    @mockserver.json_handler('/bank-trust-payments/trust-payments/v2/payments')
    def _mock_trust(request):
        return mockserver.make_response(
            status=201, json=json_mock_trust(request),
        )

    bank_core_statement_mock.set_balance_get_response(
        _default_bank_core_statement_response(handle_info),
    )

    json_body = handle_info.body
    json_body['money']['amount'] = '1'
    response = await taxi_bank_topup.post(
        handle_info.path, headers=default_headers(), json=json_body,
    )

    assert response.status_code == 200
    assert bank_core_statement_mock.balance_handler_has_calls()


@pytest.mark.parametrize(
    'handle_info', [get_v1_handle_info(), get_v2_handle_info()],
)
@pytest.mark.config(BANK_TOPUP_WALLET_MIN_LIMITS={})
async def test_zero_amount(
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_core_client_mock,
        mockserver,
        bank_core_agreement_mock,
        handle_info,
):
    @mockserver.json_handler('/bank-trust-payments/trust-payments/v2/payments')
    def _mock_trust(request):
        return mockserver.make_response(
            status=201, json=json_mock_trust(request),
        )

    bank_core_statement_mock.set_balance_get_response(
        _default_bank_core_statement_response(handle_info),
    )

    json_body = handle_info.body
    json_body['money']['amount'] = '0'
    response = await taxi_bank_topup.post(
        handle_info.path, headers=default_headers(), json=json_body,
    )

    assert response.status_code == 400
    assert bank_core_statement_mock.balance_handler_has_calls()


@pytest.mark.parametrize(
    'handle_info', [get_v1_handle_info(), get_v2_handle_info()],
)
@pytest.mark.parametrize('bad_status', [404, 429])
@pytest.mark.config(BANK_TOPUP_WALLET_MAX_LIMITS_V2={'KYC': {'RUB': '10000'}})
async def test_exactly_max_limit_from_config(
        taxi_bank_topup,
        mockserver,
        bank_core_statement_mock,
        bank_core_client_mock,
        bad_status,
        bank_core_agreement_mock,
        handle_info,
):
    @mockserver.json_handler('/bank-trust-payments/trust-payments/v2/payments')
    def _mock_trust(request):
        return mockserver.make_response(
            status=201, json=json_mock_trust(request),
        )

    bank_core_statement_mock.bad_response_status = bad_status

    json_body = handle_info.body
    json_body['money']['amount'] = '10000'
    response = await taxi_bank_topup.post(
        handle_info.path, headers=default_headers(), json=json_body,
    )

    assert bank_core_client_mock.client_auth_level_handler.has_calls
    assert response.status_code == 200


@pytest.mark.parametrize(
    'handle_info', [get_v1_handle_info(), get_v2_handle_info()],
)
@pytest.mark.config(BANK_TOPUP_WALLET_MAX_LIMITS_V2={})
async def test_no_max_limits(
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_core_client_mock,
        mockserver,
        bank_core_agreement_mock,
        handle_info,
):
    @mockserver.json_handler('/bank-trust-payments/trust-payments/v2/payments')
    def _mock_trust(request):
        return mockserver.make_response(
            status=201, json=json_mock_trust(request),
        )

    bank_core_statement_mock.set_balance_get_response({'wallets': []})

    json_body = handle_info.body
    json_body['money']['amount'] = '100'
    response = await taxi_bank_topup.post(
        handle_info.path, headers=default_headers(), json=json_body,
    )

    assert response.status_code == 500
    assert bank_core_client_mock.client_auth_level_handler.has_calls
    assert bank_core_statement_mock.balance_handler_has_calls()


@pytest.mark.parametrize(
    'handle_info', [get_v1_handle_info(), get_v2_handle_info()],
)
@pytest.mark.parametrize('core_client_bad_response_code', [None, 404])
@pytest.mark.config(
    BANK_TOPUP_WALLET_MAX_LIMITS_V2={'__default__': {'RUB': '1000'}},
)
async def test_max_limit_only_default(
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_core_client_mock,
        mockserver,
        bank_core_agreement_mock,
        core_client_bad_response_code,
        handle_info,
):
    @mockserver.json_handler('/bank-trust-payments/trust-payments/v2/payments')
    def _mock_trust(request):
        return mockserver.make_response(
            status=201, json=json_mock_trust(request),
        )

    bank_core_client_mock.bad_response_code = core_client_bad_response_code
    bank_core_statement_mock.set_balance_get_response({'wallets': []})

    json_body = handle_info.body
    json_body['money']['amount'] = '100'
    response = await taxi_bank_topup.post(
        handle_info.path, headers=default_headers(), json=json_body,
    )

    assert response.status_code == 200
    assert bank_core_client_mock.client_auth_level_handler.has_calls
    assert bank_core_statement_mock.balance_handler_has_calls()


@pytest.mark.parametrize(
    'handle_info', [get_v1_handle_info(), get_v2_handle_info()],
)
@pytest.mark.parametrize('core_client_bad_response_code', [None, 404])
@pytest.mark.config(BANK_TOPUP_WALLET_MAX_LIMITS_V2={'KYC': {'USD': '10000'}})
async def test_no_max_limits_invalid_currency(
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_core_client_mock,
        mockserver,
        bank_core_agreement_mock,
        core_client_bad_response_code,
        handle_info,
):
    @mockserver.json_handler('/bank-trust-payments/trust-payments/v2/payments')
    def _mock_trust(request):
        return mockserver.make_response(
            status=201, json=json_mock_trust(request),
        )

    bank_core_client_mock.bad_response_code = core_client_bad_response_code
    bank_core_statement_mock.set_balance_get_response({'wallets': []})

    json_body = handle_info.body
    json_body['money']['amount'] = '100'
    response = await taxi_bank_topup.post(
        handle_info.path, headers=default_headers(), json=json_body,
    )

    assert response.status_code == 500
    assert bank_core_client_mock.client_auth_level_handler.has_calls
    assert bank_core_statement_mock.balance_handler_has_calls()


@pytest.mark.parametrize(
    'handle_info', [get_v1_handle_info(), get_v2_handle_info()],
)
@pytest.mark.config(
    BANK_TOPUP_WALLET_CURRENCY_PRECISION={'RUB': 0, 'EUR': 0, 'USD': 0},
)
async def test_wrong_currency_precision(
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_core_client_mock,
        bank_core_agreement_mock,
        handle_info,
):
    json_body = handle_info.body
    json_body['money']['amount'] = '1000.1'
    bank_core_statement_mock.set_balance_get_response(
        _default_bank_core_statement_response(handle_info),
    )
    response = await taxi_bank_topup.post(
        handle_info.path, headers=default_headers(), json=json_body,
    )

    assert response.status_code == 400
    assert bank_core_statement_mock.balance_handler_has_calls()


@pytest.mark.parametrize(
    'handle_info', [get_v1_handle_info(), get_v2_handle_info()],
)
@pytest.mark.config(BANK_TOPUP_WALLET_CURRENCY_PRECISION={})
async def test_no_currency_precision(
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_core_client_mock,
        bank_core_agreement_mock,
        handle_info,
):
    json_body = handle_info.body
    json_body['money']['amount'] = '1000.21'
    bank_core_statement_mock.set_balance_get_response(
        _default_bank_core_statement_response(handle_info),
    )
    response = await taxi_bank_topup.post(
        handle_info.path, headers=default_headers(), json=json_body,
    )

    assert response.status_code == 500
    assert bank_core_statement_mock.balance_handler_has_calls()


@pytest.mark.parametrize(
    'handle_info', [get_v1_handle_info(), get_v2_handle_info()],
)
@pytest.mark.config(BANK_TOPUP_WALLET_CURRENCY_PRECISION={'RUB': 5})
async def test_no_valid_precision(
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_core_client_mock,
        bank_core_agreement_mock,
        handle_info,
):
    json_body = handle_info.body
    json_body['money']['amount'] = '1000'

    bank_core_statement_mock.set_balance_get_response(
        _default_bank_core_statement_response(handle_info),
    )

    response = await taxi_bank_topup.post(
        handle_info.path, headers=default_headers(), json=json_body,
    )

    assert response.status_code == 500
    assert bank_core_statement_mock.balance_handler_has_calls()


@pytest.mark.parametrize(
    'handle_info', [get_v1_handle_info(), get_v2_handle_info()],
)
@pytest.mark.config(BANK_TOPUP_WALLET_CURRENCY_PRECISION={'RUB': 2})
async def test_no_valid_amount(
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_core_client_mock,
        handle_info,
):
    json_body = handle_info.body
    json_body['money']['amount'] = '100.01.02'

    bank_core_statement_mock.set_balance_get_response(
        _default_bank_core_statement_response(handle_info),
    )

    response = await taxi_bank_topup.post(
        handle_info.path, headers=default_headers(), json=json_body,
    )

    assert response.status_code == 400
    assert not bank_core_statement_mock.balance_handler_has_calls()


@pytest.mark.parametrize(
    'handle_info', [get_v1_handle_info(), get_v2_handle_info()],
)
@pytest.mark.parametrize(
    'amount',
    ['  1000', '1000  ', '1000ty', '1000,45', '92233720368547758.07'],
)
@pytest.mark.config(BANK_TOPUP_WALLET_CURRENCY_PRECISION={'RUB': 2})
async def test_overflow(
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_core_client_mock,
        amount,
        bank_core_agreement_mock,
        handle_info,
):
    json_body = handle_info.body
    json_body['money']['amount'] = amount

    bank_core_statement_mock.set_balance_get_response(
        _default_bank_core_statement_response(handle_info),
    )

    response = await taxi_bank_topup.post(
        handle_info.path, headers=default_headers(), json=json_body,
    )

    assert response.status_code == 400


@pytest.mark.parametrize(
    'handle_info', [get_v1_handle_info(), get_v2_handle_info()],
)
async def test_exactly_max_limit(
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_core_client_mock,
        mockserver,
        bank_core_agreement_mock,
        handle_info,
):
    @mockserver.json_handler('/bank-trust-payments/trust-payments/v2/payments')
    def _mock_trust(request):
        return mockserver.make_response(
            status=201, json=json_mock_trust(request),
        )

    bank_core_statement_mock.set_balance_get_response(
        _default_bank_core_statement_response(handle_info),
    )

    json_body = handle_info.body
    json_body['money']['amount'] = '15000'
    response = await taxi_bank_topup.post(
        handle_info.path, headers=default_headers(), json=json_body,
    )

    assert response.status_code == 200
    assert bank_core_statement_mock.balance_handler_has_calls()


@pytest.mark.parametrize(
    'handle_info', [get_v1_handle_info(), get_v2_handle_info()],
)
async def test_over_max_limit(
        taxi_bank_topup,
        bank_core_statement_mock,
        bank_core_client_mock,
        mockserver,
        bank_core_agreement_mock,
        handle_info,
):
    @mockserver.json_handler('/bank-trust-payments/trust-payments/v2/payments')
    def _mock_trust(request):
        return mockserver.make_response(
            status=201, json=json_mock_trust(request),
        )

    bank_core_statement_mock.set_balance_get_response(
        _default_bank_core_statement_response(handle_info),
    )

    json_body = handle_info.body
    json_body['money']['amount'] = '15001'
    response = await taxi_bank_topup.post(
        handle_info.path, headers=default_headers(), json=json_body,
    )

    assert response.status_code == 400
    assert bank_core_statement_mock.balance_handler_has_calls()
