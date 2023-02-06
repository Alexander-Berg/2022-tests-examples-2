import pytest

from tests_bank_topup import common


@pytest.mark.parametrize('wallet_id', ['balance_id', None])
@pytest.mark.now('2022-05-11T00:04:33+03')
@pytest.mark.config(
    BANK_TOPUP_FINTECHSPI_60_WORKAROUND={
        'enabled': True,
        'active_periods': [
            {'time_of_day_from': '00:04:30', 'time_of_day_to': '00:04:32'},
        ],
    },
)
async def test_not_reschedule_fintechspi_60(
        mockserver,
        stq_runner,
        pgsql,
        trust_mock,
        bank_core_accounting_mock,
        bank_core_agreement_mock,
        bank_risk,
        wallet_id,
):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(request):
        return {}

    common.set_wallet_id(pgsql, common.TEST_PAYMENT_ID, wallet_id)
    common.set_payment_status(pgsql, status='PAYMENT_RECEIVED')

    await stq_runner.bank_topup_core_topup.call(
        task_id='id',
        kwargs={'payment_id': common.TEST_PAYMENT_ID},
        expect_fail=False,
    )

    assert common.get_payment_status(pgsql) == 'SUCCESS_SAVED'
    assert bank_core_accounting_mock.wallet_topup_save_handler.has_calls
    assert bank_risk.risk_calculation_handler.has_calls

    assert not mock_stq_reschedule.has_calls


@pytest.mark.parametrize('wallet_id', ['balance_id', None])
@pytest.mark.now('2022-05-11T00:04:31+03')
@pytest.mark.config(
    BANK_TOPUP_FINTECHSPI_60_WORKAROUND={
        'enabled': True,
        'active_periods': [
            {'time_of_day_from': '00:04:30', 'time_of_day_to': '00:04:32'},
        ],
    },
)
async def test_reschedule_fintechspi_60(
        mockserver,
        stq_runner,
        pgsql,
        trust_mock,
        bank_core_accounting_mock,
        bank_core_agreement_mock,
        bank_risk,
        wallet_id,
):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(request):
        return {}

    common.set_wallet_id(pgsql, common.TEST_PAYMENT_ID, wallet_id)
    common.set_payment_status(pgsql, status='PAYMENT_RECEIVED')

    await stq_runner.bank_topup_core_topup.call(
        task_id='id',
        kwargs={'payment_id': common.TEST_PAYMENT_ID},
        expect_fail=False,
    )

    assert common.get_payment_status(pgsql) == 'PAYMENT_RECEIVED'
    assert bank_core_accounting_mock.wallet_topup_save_handler.has_calls
    assert bank_risk.risk_calculation_handler.has_calls

    assert mock_stq_reschedule.has_calls
    json = mock_stq_reschedule.next_call()['request'].json
    assert json['queue_name'] == 'bank_topup_core_topup'

    # here value is important:
    # '2022-05-11T00:04:32+03' is '2022-05-10T21:04:32+00'
    assert json['eta'] == '2022-05-10T21:04:32+0000'


@pytest.mark.parametrize('wallet_id', ['balance_id', None])
@pytest.mark.now('2022-05-11T00:04:31-03')
@pytest.mark.config(
    BANK_TOPUP_FINTECHSPI_60_WORKAROUND={
        'enabled': True,
        'active_periods': [
            {'time_of_day_from': '06:04:30', 'time_of_day_to': '06:04:32'},
        ],
    },
)
async def test_reschedule_fintechspi_60_tz(
        mockserver,
        stq_runner,
        pgsql,
        trust_mock,
        bank_core_accounting_mock,
        bank_core_agreement_mock,
        bank_risk,
        wallet_id,
):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(request):
        return {}

    common.set_wallet_id(pgsql, common.TEST_PAYMENT_ID, wallet_id)
    common.set_payment_status(pgsql, status='PAYMENT_RECEIVED')

    await stq_runner.bank_topup_core_topup.call(
        task_id='id',
        kwargs={'payment_id': common.TEST_PAYMENT_ID},
        expect_fail=False,
    )

    assert common.get_payment_status(pgsql) == 'PAYMENT_RECEIVED'
    assert bank_core_accounting_mock.wallet_topup_save_handler.has_calls
    assert bank_risk.risk_calculation_handler.has_calls

    assert mock_stq_reschedule.has_calls
    json = mock_stq_reschedule.next_call()['request'].json
    assert json['queue_name'] == 'bank_topup_core_topup'

    # here value is important:
    # '2022-05-11T06:04:32+03' is '2022-05-11T03:04:32+00'
    assert json['eta'] == '2022-05-11T03:04:32+0000'


def _make_accessor():
    return {
        'accessor_id': '123456',
        'buid': common.DEFAULT_YANDEX_BUID,
        'agreement_id': 'agreement_id',
        'accessor_type': 'WALLET',
        'currency': 'RUB',
    }


@pytest.mark.parametrize(
    'code, body',
    [
        (404, {'code': '404', 'message': 'NotFound'}),
        (200, {'accessors': []}),
        (200, {'accessors': [_make_accessor()] * 2}),
    ],
)
async def test_cant_find_wallet_by_agreement(
        mockserver,
        stq_runner,
        pgsql,
        trust_mock,
        bank_core_accounting_mock,
        bank_risk,
        code,
        body,
):
    @mockserver.json_handler(
        '/bank-core-agreement/v1/accessor/list', prefix=False,
    )
    def _get_accessor_handler(request):
        return mockserver.make_response(status=code, json=body)

    common.set_agreement_id(pgsql, common.TEST_PAYMENT_ID, 'agreement_id')
    common.set_payment_status(pgsql, status='PAYMENT_RECEIVED')

    await stq_runner.bank_topup_core_topup.call(
        task_id='id',
        kwargs={'payment_id': common.TEST_PAYMENT_ID},
        expect_fail=True,
    )

    assert common.get_payment_status(pgsql) == 'PAYMENT_RECEIVED'
    assert not bank_core_accounting_mock.wallet_topup_save_handler.has_calls


async def test_wallet_by_agreement_request(
        mockserver, stq_runner, pgsql, trust_mock, bank_risk,
):
    accessor = _make_accessor()

    @mockserver.json_handler(
        '/bank-core-agreement/v1/accessor/list', prefix=False,
    )
    def _get_accessor_handler(request):
        assert request.json == {
            'agreement_id': 'agreement_id',
            'accessor_type': 'WALLET',
        }
        return mockserver.make_response(
            status=200, json={'accessors': [accessor]},
        )

    @mockserver.json_handler(
        '/bank-core-accounting/v1/wallets/topup/save', prefix=False,
    )
    def _wallet_topup_save_handler(request):
        assert request.json['wallet_id'] == accessor['accessor_id']

        return mockserver.make_response(
            status=200, json={'status': 'COMPLETED'},
        )

    common.set_agreement_id(pgsql, common.TEST_PAYMENT_ID, 'agreement_id')
    common.set_payment_status(pgsql, status='PAYMENT_RECEIVED')
    await stq_runner.bank_topup_core_topup.call(
        task_id='id',
        kwargs={'payment_id': common.TEST_PAYMENT_ID},
        expect_fail=False,
    )

    assert common.get_payment_status(pgsql) == 'SUCCESS_SAVED'
    assert _wallet_topup_save_handler.has_calls


@pytest.mark.parametrize('wallet_id', ['balance_id', None])
@pytest.mark.parametrize('status', ['CREATED', 'STARTED', 'INVALID'])
async def test_stq_task_invalid_status(
        trust_mock,
        stq_runner,
        status,
        pgsql,
        bank_core_accounting_mock,
        bank_core_agreement_mock,
        wallet_id,
):
    common.set_payment_status(pgsql, status=status)
    common.set_wallet_id(pgsql, common.TEST_PAYMENT_ID, wallet_id)
    await stq_runner.bank_topup_core_topup.call(
        task_id='id',
        kwargs={'payment_id': common.TEST_PAYMENT_ID},
        expect_fail=True,
    )

    assert not bank_core_accounting_mock.wallet_topup_save_handler.has_calls
