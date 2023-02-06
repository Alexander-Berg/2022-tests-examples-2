import pytest

from tests_bank_topup import common


def get_headers(
        bank_uid=common.DEFAULT_YANDEX_BUID,
        idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
):
    return {
        'X-YaBank-SessionUUID': common.DEFAULT_YABANK_SESSION_UUID,
        'X-YaBank-PhoneID': common.DEFAULT_YABANK_PHONE_ID,
        'X-Yandex-BUID': bank_uid,
        'X-Yandex-UID': common.DEFAULT_YANDEX_UID,
        'X-Ya-User-Ticket': common.DEFAULT_USER_TICKET,
        'X-Idempotency-Token': idempotency_token,
    }


class Money(dict):
    def __init__(
            self,
            amount=common.DEFAULT_AMOUNT,
            currency=common.DEFAULT_CURRENCY,
    ):
        dict.__init__(self, amount=amount, currency=currency)


class Threshold(Money):
    pass


def get_body(
        autotopup_type=common.DEFAULT_AUTOTOPUP_TYPE,
        agreement_id=common.DEFAULT_PUBLIC_AGREEMENT_ID,
        payment_method_id=common.DEFAULT_PAYMENT_METHOD_ID,
        money=Money(),
        threshold=Threshold(),
):

    return {
        'type': autotopup_type,
        'agreement_id': agreement_id,
        'payment_method_id': payment_method_id,
        'money': money,
        'threshold': threshold,
    }


def make_money(amount=common.DEFAULT_AMOUNT, currency=common.DEFAULT_CURRENCY):
    return Money(amount=amount, currency=currency)


def make_threshold(
        amount=common.DEFAULT_AMOUNT, currency=common.DEFAULT_CURRENCY,
):
    return Threshold(amount=amount, currency=currency)


def compare_autotopups_wo_time(actual, expected):
    assert actual['bank_uid'] == expected['bank_uid']
    assert actual['yandex_uid'] == expected['yandex_uid']
    assert actual['idempotency_token'] == expected['idempotency_token']
    assert actual['autotopup_id'] == expected['autotopup_id']
    assert actual['autotopup_internal_id'] == expected['autotopup_internal_id']
    assert actual['type'] == expected['type']
    assert actual['enabled'] == expected['enabled']
    assert actual['params'] == expected['params']


def compare_watchdogs_wo_time(actual, expected):
    assert actual['bank_uid'] == expected['bank_uid']
    assert actual['watchdog_id'] == expected['watchdog_id']
    assert actual['autotopup_id'] == expected['autotopup_id']
    assert actual['autotopup_internal_id'] == expected['autotopup_internal_id']


@pytest.mark.parametrize('autotopup_type', ['LIMIT_FILL', 'REGULAR_PERIOD'])
async def test_fail_if_wrong_autotype_type(taxi_bank_topup, autotopup_type):
    response = await taxi_bank_topup.post(
        '/v1/topup/v1/create_autotopup/',
        headers=get_headers(),
        json=get_body(autotopup_type=autotopup_type),
    )
    assert response.status_code == 400


@pytest.mark.parametrize('absent_field', ['money', 'threshold'])
async def test_fail_if_money_or_threshold_are_absent(
        taxi_bank_topup, absent_field,
):
    body = get_body()
    body.pop(absent_field)

    response = await taxi_bank_topup.post(
        '/v1/topup/v1/create_autotopup/', headers=get_headers(), json=body,
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    'money_currency, threshold_currency',
    [('USD', 'RUB'), ('RUB', 'USD'), ('EUR', 'USD')],
)
async def test_fail_if_currency_not_rub(
        taxi_bank_topup, money_currency, threshold_currency,
):
    response = await taxi_bank_topup.post(
        '/v1/topup/v1/create_autotopup/',
        headers=get_headers(),
        json=get_body(
            money=make_money(currency=money_currency),
            threshold=make_threshold(currency=threshold_currency),
        ),
    )
    assert response.status_code == 400


@pytest.mark.parametrize('amount', ['0', '-1', '-0.1'])
async def test_fail_if_negative_or_zero_money(taxi_bank_topup, amount):
    response = await taxi_bank_topup.post(
        '/v1/topup/v1/create_autotopup/',
        headers=get_headers(),
        json=get_body(money=make_money(amount=amount)),
    )
    assert response.status_code == 400


@pytest.mark.parametrize('amount', ['-1', '-0.1'])
async def test_fail_if_negative_threshold(taxi_bank_topup, amount):
    response = await taxi_bank_topup.post(
        '/v1/topup/v1/create_autotopup/',
        headers=get_headers(),
        json=get_body(threshold=make_money(amount=amount)),
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    'status, code, message, our_status',
    [
        (400, 'BAD_REQUEST', 'You wrong', 400),
        (404, 'NOT_FOUND', 'Something not found', 404),
        (409, 'CONFLICT', 'Conflicting', 409),
    ],
)
async def test_fail_if_balance_watchdog_save_response_with_err(
        taxi_bank_topup,
        bank_core_accounting_mock,
        status,
        code,
        message,
        our_status,
):
    bank_core_accounting_mock.set_expected_watchdog_request()
    bank_core_accounting_mock.set_response({'code': code, 'message': message})
    bank_core_accounting_mock.set_http_status_code(status)

    response = await taxi_bank_topup.post(
        '/v1/topup/v1/create_autotopup/',
        headers=get_headers(),
        json=get_body(),
    )
    assert response.status_code == our_status


async def test_new_autotopup(
        pgsql, taxi_bank_topup, bank_core_accounting_mock,
):
    bank_core_accounting_mock.set_expected_watchdog_request()
    bank_core_accounting_mock.set_response(
        {'watchdog_id': common.DEFAULT_WATCHDOG_ID},
    )
    response = await taxi_bank_topup.post(
        '/v1/topup/v1/create_autotopup/',
        headers=get_headers(),
        json=get_body(),
    )
    assert response.status_code == 200
    autotopup_id = response.json()['autotopup_id']
    compare_autotopups_wo_time(
        common.get_autotopup(pgsql, autotopup_id),
        common.make_autotopup(
            autotopup_id=autotopup_id, autotopup_internal_id=autotopup_id,
        ),
    )
    compare_watchdogs_wo_time(
        common.get_watchdog(pgsql, common.DEFAULT_WATCHDOG_ID),
        common.make_watchdog(
            autotopup_id=autotopup_id, autotopup_internal_id=autotopup_id,
        ),
    )


async def test_new_autotopup_with_zero_threshold(
        pgsql, taxi_bank_topup, bank_core_accounting_mock,
):
    bank_core_accounting_mock.set_expected_watchdog_request(
        threshold_amount='0.0',
    )
    bank_core_accounting_mock.set_response(
        {'watchdog_id': common.DEFAULT_WATCHDOG_ID},
    )
    response = await taxi_bank_topup.post(
        '/v1/topup/v1/create_autotopup/',
        headers=get_headers(),
        json=get_body(threshold=make_threshold(amount='0.0')),
    )
    assert response.status_code == 200
    autotopup_id = response.json()['autotopup_id']
    compare_autotopups_wo_time(
        common.get_autotopup(pgsql, response.json()['autotopup_id']),
        common.make_autotopup(
            autotopup_id=autotopup_id,
            autotopup_internal_id=autotopup_id,
            threshold_amount='0.0',
        ),
    )
    compare_watchdogs_wo_time(
        common.get_watchdog(pgsql, common.DEFAULT_WATCHDOG_ID),
        common.make_watchdog(
            autotopup_id=autotopup_id, autotopup_internal_id=autotopup_id,
        ),
    )


@pytest.mark.parametrize('is_enabled', [True, False])
async def test_same_autotopup_in_db_before_watchdog_subscription(
        pgsql, taxi_bank_topup, bank_core_accounting_mock, is_enabled,
):
    common.insert_autotopup(
        pgsql,
        common.make_autotopup(
            bank_uid=common.DEFAULT_YANDEX_BUID,
            idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
            enabled=is_enabled,
        ),
    )
    response = await taxi_bank_topup.post(
        '/v1/topup/v1/create_autotopup/',
        headers=get_headers(
            bank_uid=common.DEFAULT_YANDEX_BUID,
            idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
        ),
        json=get_body(),
    )
    assert response.status_code == 200
    assert response.json()['autotopup_id'] == common.DEFAULT_AUTOTOPUP_ID
    assert (
        not bank_core_accounting_mock.balance_watchdog_save_handler.has_calls
    )


@pytest.mark.parametrize('is_enabled', [True, False])
async def test_same_autotopup_in_db_after_watchdog_subscription(
        pgsql,
        testpoint,
        taxi_bank_topup,
        bank_core_accounting_mock,
        is_enabled,
):
    bank_core_accounting_mock.set_expected_watchdog_request()
    bank_core_accounting_mock.set_response(
        {'watchdog_id': common.DEFAULT_WATCHDOG_ID},
    )

    @testpoint('create_autotopup')
    def _create_autotopup(stats):
        common.insert_autotopup(
            pgsql,
            common.make_autotopup(
                bank_uid=common.DEFAULT_YANDEX_BUID,
                idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
                enabled=is_enabled,
            ),
        )

    response = await taxi_bank_topup.post(
        '/v1/topup/v1/create_autotopup/',
        headers=get_headers(
            bank_uid=common.DEFAULT_YANDEX_BUID,
            idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
        ),
        json=get_body(),
    )
    assert response.status_code == 500
    assert bank_core_accounting_mock.balance_watchdog_save_handler.has_calls


async def test_dup_wathcdog_id_in_db_after_watchdog_subscription(
        pgsql, testpoint, taxi_bank_topup, bank_core_accounting_mock,
):
    bank_core_accounting_mock.set_expected_watchdog_request()
    bank_core_accounting_mock.set_response(
        {'watchdog_id': common.DEFAULT_WATCHDOG_ID},
    )

    @testpoint('create_autotopup')
    def _create_autotopup(ctx):
        common.insert_autotopup(
            pgsql,
            common.make_autotopup(
                bank_uid=common.ANOTHER_YANDEX_BUID,
                idempotency_token=common.ANOTHER_IDEMPOTENCY_TOKEN,
                autotopup_id=common.DEFAULT_AUTOTOPUP_ID,
            ),
        )
        common.insert_watchdog(
            pgsql,
            common.make_watchdog(
                autotopup_id=common.DEFAULT_AUTOTOPUP_ID,
                watchdog_id=common.DEFAULT_WATCHDOG_ID,
            ),
        )

    response = await taxi_bank_topup.post(
        '/v1/topup/v1/create_autotopup/',
        headers=get_headers(
            bank_uid=common.DEFAULT_YANDEX_BUID,
            idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
        ),
        json=get_body(),
    )
    assert response.status_code == 500
    assert bank_core_accounting_mock.balance_watchdog_save_handler.has_calls


@pytest.mark.parametrize('autotopup_type', ['LIMIT_FILL', 'REGULAR_PERIOD'])
async def test_same_idempotency_autotopup_with_diff_type(
        pgsql, taxi_bank_topup, autotopup_type,
):
    common.insert_autotopup(
        pgsql,
        common.make_autotopup(
            bank_uid=common.DEFAULT_YANDEX_BUID,
            idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
            autotopup_type=autotopup_type,
        ),
    )
    response = await taxi_bank_topup.post(
        '/v1/topup/v1/create_autotopup/',
        headers=get_headers(
            bank_uid=common.DEFAULT_YANDEX_BUID,
            idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
        ),
        json=get_body(),
    )
    assert response.status_code == 409


@pytest.mark.parametrize(
    'field, value',
    [
        ('public_agreement_id', common.ANOTHER_PUBLIC_AGREEMENT_ID),
        ('payment_method_id', common.ANOTHER_METHOD_PAYMENT_ID),
        ('currency', 'USD'),
        ('currency', 'EUR'),
        ('money_amount', common.ANOTHER_AMOUNT),
        ('threshold_amount', common.ANOTHER_AMOUNT),
    ],
)
async def test_same_idempotency_autotopup_with_diff_params(
        pgsql, taxi_bank_topup, field, value,
):
    autotopup = common.make_autotopup(
        bank_uid=common.DEFAULT_YANDEX_BUID,
        idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
    )
    autotopup['params'][field] = value
    common.insert_autotopup(pgsql, autotopup)
    response = await taxi_bank_topup.post(
        '/v1/topup/v1/create_autotopup/',
        headers=get_headers(
            bank_uid=common.DEFAULT_YANDEX_BUID,
            idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
        ),
        json=get_body(),
    )
    assert response.status_code == 409
