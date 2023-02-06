import copy

import pytest

from tests_bank_topup import common

PAYMENT_ID_EMPTY_IP = '5ee391f0-cddc-4776-8316-8b91839da7f3'
PAYMENT_ID_WITH_DENIED_AF_DECISION = '397aa31b-43aa-42d1-befc-285b7d3cf49c'
PAYMENT_ID_WITH_ALLOWED_AF_DECISION = '127ea3d7-f8aa-45a6-b704-caee53ba5450'


@pytest.mark.parametrize(
    'init_status, final_status, risk_has_calls, clear_has_calls',
    [
        ('PAYMENT_RECEIVED', 'SUCCESS_SAVED', True, True),
        ('REFUNDED', 'REFUNDED_SAVED', False, False),
        ('FAILED', 'FAILED_SAVED', True, False),
    ],
)
@pytest.mark.parametrize(
    'payment_id', [common.TEST_PAYMENT_ID, PAYMENT_ID_EMPTY_IP],
)
@pytest.mark.parametrize('wallet_id', ['balance_id', None])
async def test_stq_task_if_core_return_completed(
        stq_runner,
        pgsql,
        mockserver,
        trust_mock,
        bank_core_accounting_mock,
        bank_core_agreement_mock,
        bank_risk,
        init_status,
        final_status,
        risk_has_calls,
        clear_has_calls,
        payment_id,
        wallet_id,
):
    common.set_payment_status(pgsql, payment_id=payment_id, status=init_status)
    bank_core_accounting_mock.set_response({'status': 'COMPLETED'})

    @mockserver.json_handler(
        '/stq-agent/queues/api/add/bank_topup_trust_clear',
    )
    def mock_stq_schedule_clear(request):
        return {}

    common.set_wallet_id(pgsql, common.TEST_PAYMENT_ID, wallet_id)
    await stq_runner.bank_topup_core_topup.call(
        task_id='id', kwargs={'payment_id': payment_id}, expect_fail=False,
    )

    assert bank_risk.risk_calculation_handler.has_calls == risk_has_calls
    assert bank_core_accounting_mock.wallet_topup_save_handler.has_calls
    assert mock_stq_schedule_clear.has_calls == clear_has_calls
    assert (
        common.get_payment_status(pgsql, payment_id=payment_id) == final_status
    )
    assert (
        common.get_trust_payment_id(pgsql, payment_id=payment_id)
        == common.DEFAULT_PAYMENT_METHOD_ID
    )


@pytest.mark.parametrize(
    'init_status, final_status, risk_has_calls',
    [
        ('PAYMENT_RECEIVED', 'SUCCESS_SAVING', True),
        ('REFUNDED', 'REFUNDED_SAVING', False),
        ('FAILED', 'FAILED_SAVING', True),
    ],
)
@pytest.mark.parametrize(
    'payment_id', [common.TEST_PAYMENT_ID, PAYMENT_ID_EMPTY_IP],
)
async def test_stq_task_reschedule_if_core_return_success(
        stq_runner,
        pgsql,
        trust_mock,
        mockserver,
        bank_core_accounting_mock,
        bank_core_agreement_mock,
        bank_risk,
        init_status,
        final_status,
        risk_has_calls,
        payment_id,
):
    common.set_payment_status(pgsql, payment_id=payment_id, status=init_status)
    bank_core_accounting_mock.set_response({'status': 'SUCCESS'})

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(request):
        return {}

    @mockserver.json_handler(
        '/stq-agent/queues/api/add/bank_topup_trust_clear',
    )
    def mock_stq_schedule_clear(request):
        return {}

    await stq_runner.bank_topup_core_topup.call(
        task_id='id', kwargs={'payment_id': payment_id}, expect_fail=False,
    )

    assert bank_risk.risk_calculation_handler.times_called == risk_has_calls
    assert bank_core_accounting_mock.wallet_topup_save_handler.has_calls
    assert not mock_stq_schedule_clear.has_calls
    assert mock_stq_reschedule.has_calls
    assert (
        common.get_payment_status(pgsql, payment_id=payment_id) == final_status
    )
    assert (
        common.get_trust_payment_id(pgsql, payment_id=payment_id)
        == common.DEFAULT_PAYMENT_METHOD_ID
    )


@pytest.mark.config(BANK_TOPUP_CORE_STATUS_SUCCESS_AS_COMPLETED=True)
@pytest.mark.parametrize(
    'init_status, final_status, risk_has_calls, clear_has_calls',
    [
        ('PAYMENT_RECEIVED', 'SUCCESS_SAVED', True, True),
        ('REFUNDED', 'REFUNDED_SAVED', False, False),
        ('FAILED', 'FAILED_SAVED', True, False),
    ],
)
@pytest.mark.parametrize(
    'payment_id', [common.TEST_PAYMENT_ID, PAYMENT_ID_EMPTY_IP],
)
async def test_stq_task_if_core_return_success_as_completed(
        stq_runner,
        pgsql,
        trust_mock,
        mockserver,
        bank_core_accounting_mock,
        bank_core_agreement_mock,
        bank_risk,
        init_status,
        final_status,
        risk_has_calls,
        clear_has_calls,
        payment_id,
):
    common.set_payment_status(pgsql, payment_id=payment_id, status=init_status)
    bank_core_accounting_mock.set_response({'status': 'SUCCESS'})

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(request):
        return {}

    @mockserver.json_handler(
        '/stq-agent/queues/api/add/bank_topup_trust_clear',
    )
    def mock_stq_schedule_clear(request):
        return {}

    await stq_runner.bank_topup_core_topup.call(
        task_id='id', kwargs={'payment_id': payment_id}, expect_fail=False,
    )

    assert bank_risk.risk_calculation_handler.times_called == risk_has_calls
    assert bank_core_accounting_mock.wallet_topup_save_handler.has_calls
    assert mock_stq_schedule_clear.has_calls == clear_has_calls
    assert not mock_stq_reschedule.has_calls
    assert (
        common.get_payment_status(pgsql, payment_id=payment_id) == final_status
    )
    assert (
        common.get_trust_payment_id(pgsql, payment_id=payment_id)
        == common.DEFAULT_PAYMENT_METHOD_ID
    )


@pytest.mark.parametrize(
    'init_status, risk_has_calls',
    [
        ('SUCCESS_SAVING', True),
        ('REFUNDED_SAVING', False),
        ('FAILED_SAVING', True),
    ],
)
@pytest.mark.parametrize(
    'payment_id', [common.TEST_PAYMENT_ID, PAYMENT_ID_EMPTY_IP],
)
async def test_stq_task_reschedule_if_core_return_success_for_saving_payment(
        stq_runner,
        pgsql,
        trust_mock,
        mockserver,
        bank_core_accounting_mock,
        bank_core_agreement_mock,
        bank_risk,
        init_status,
        risk_has_calls,
        payment_id,
):
    common.set_payment_status(pgsql, payment_id=payment_id, status=init_status)
    bank_core_accounting_mock.set_response({'status': 'SUCCESS'})

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(request):
        return {}

    @mockserver.json_handler(
        '/stq-agent/queues/api/add/bank_topup_trust_clear',
    )
    def mock_stq_schedule_clear(request):
        return {}

    await stq_runner.bank_topup_core_topup.call(
        task_id='id', kwargs={'payment_id': payment_id}, expect_fail=False,
    )

    assert bank_risk.risk_calculation_handler.times_called == risk_has_calls
    assert bank_core_accounting_mock.wallet_topup_save_handler.has_calls
    assert not mock_stq_schedule_clear.has_calls
    assert mock_stq_reschedule.has_calls
    assert (
        common.get_payment_status(pgsql, payment_id=payment_id) == init_status
    )
    assert (
        common.get_trust_payment_id(pgsql, payment_id=payment_id)
        == common.DEFAULT_PAYMENT_METHOD_ID
    )


@pytest.mark.parametrize(
    'init_status, final_status, risk_has_calls, clear_has_calls',
    [
        ('SUCCESS_SAVING', 'SUCCESS_SAVED', True, True),
        ('REFUNDED_SAVING', 'REFUNDED_SAVED', False, False),
        ('FAILED_SAVING', 'FAILED_SAVED', True, False),
    ],
)
@pytest.mark.parametrize(
    'payment_id', [common.TEST_PAYMENT_ID, PAYMENT_ID_EMPTY_IP],
)
async def test_stq_task_if_core_return_completed_after_success(
        stq_runner,
        pgsql,
        trust_mock,
        mockserver,
        bank_core_accounting_mock,
        bank_core_agreement_mock,
        bank_risk,
        init_status,
        final_status,
        risk_has_calls,
        clear_has_calls,
        payment_id,
):
    common.set_payment_status(pgsql, payment_id=payment_id, status=init_status)
    bank_core_accounting_mock.set_response({'status': 'COMPLETED'})

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(request):
        return {}

    @mockserver.json_handler(
        '/stq-agent/queues/api/add/bank_topup_trust_clear',
    )
    def mock_stq_schedule_clear(request):
        return {}

    await stq_runner.bank_topup_core_topup.call(
        task_id='id', kwargs={'payment_id': payment_id}, expect_fail=False,
    )

    assert bank_risk.risk_calculation_handler.times_called == risk_has_calls
    assert bank_core_accounting_mock.wallet_topup_save_handler.has_calls
    assert not mock_stq_reschedule.has_calls
    assert mock_stq_schedule_clear.has_calls == clear_has_calls
    assert (
        common.get_payment_status(pgsql, payment_id=payment_id) == final_status
    )
    assert (
        common.get_trust_payment_id(pgsql, payment_id=payment_id)
        == common.DEFAULT_PAYMENT_METHOD_ID
    )


@pytest.mark.parametrize(
    'init_status, status_for_core',
    [
        ('SUCCESS_SAVING', 'SUCCESS'),
        ('REFUNDED_SAVING', 'FAILURE'),
        ('FAILED_SAVING', 'FAILURE'),
    ],
)
@pytest.mark.parametrize(
    'payment_id', [common.TEST_PAYMENT_ID, PAYMENT_ID_EMPTY_IP],
)
async def test_stq_task_failed_if_core_return_refund_for_saving_payment(
        stq_runner,
        pgsql,
        trust_mock,
        mockserver,
        bank_risk,
        init_status,
        status_for_core,
        payment_id,
):
    common.set_payment_status(pgsql, payment_id=payment_id, status=init_status)

    @mockserver.json_handler(
        '/bank-core-accounting/v1/wallets/topup/save', prefix=False,
    )
    def topup_save_handler(request):
        assert request.json['payment_status'] == status_for_core
        return mockserver.make_response(json={'status': 'REFUND'})

    await stq_runner.bank_topup_core_topup.call(
        task_id='id', kwargs={'payment_id': payment_id}, expect_fail=True,
    )

    assert topup_save_handler.has_calls
    assert (
        common.get_payment_status(pgsql, payment_id=payment_id) == init_status
    )
    assert (
        common.get_trust_payment_id(pgsql, payment_id=payment_id)
        == common.DEFAULT_PAYMENT_METHOD_ID
    )


@pytest.mark.parametrize('wallet_id', ['balance_id', None])
async def test_stq_task_no_trust_payment_id(
        stq_runner,
        pgsql,
        trust_mock,
        bank_core_accounting_mock,
        bank_core_agreement_mock,
        wallet_id,
):
    common.set_wallet_id(pgsql, common.TEST_PAYMENT_ID, wallet_id)
    common.set_payment_status(pgsql, status='PAYMENT_RECEIVED')

    await stq_runner.bank_topup_core_topup.call(
        task_id='id',
        kwargs={'payment_id': common.TEST_PAYMENT_ID},
        expect_fail=False,
    )

    assert common.get_payment_status(pgsql) == 'SUCCESS_SAVED'
    assert (
        common.get_trust_payment_id(pgsql) == common.DEFAULT_PAYMENT_METHOD_ID
    )
    assert bank_core_accounting_mock.wallet_topup_save_handler.has_calls


@pytest.mark.parametrize('wallet_id', ['balance_id', None])
async def test_stq_task_refund_init(
        stq_runner,
        pgsql,
        trust_mock,
        bank_core_accounting_mock,
        bank_core_agreement_mock,
        wallet_id,
):
    common.set_wallet_id(pgsql, common.TEST_PAYMENT_ID, wallet_id)
    common.set_payment_status(pgsql, status='PAYMENT_RECEIVED')

    bank_core_accounting_mock.set_response({'status': 'REFUND'})

    await stq_runner.bank_topup_core_topup.call(
        task_id='id',
        kwargs={'payment_id': common.TEST_PAYMENT_ID},
        expect_fail=False,
    )

    assert common.get_payment_status(pgsql) == 'REFUNDING'
    assert bank_core_accounting_mock.wallet_topup_save_handler.has_calls


@pytest.mark.parametrize(
    'status',
    [
        'PAYMENT_RECEIVED',
        'FAILED',
        'REFUNDED',
        'FAILED_SAVING',
        'REFUNDED_SAVING',
        'SUCCESS_SAVING',
    ],
)
@pytest.mark.parametrize('wallet_id', ['balance_id', None])
async def test_stq_task_retry(
        mockserver,
        stq_runner,
        pgsql,
        trust_mock,
        status,
        bank_core_accounting_mock,
        bank_core_agreement_mock,
        wallet_id,
):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(request):
        return {}

    common.set_wallet_id(pgsql, common.TEST_PAYMENT_ID, wallet_id)
    common.set_payment_status(pgsql, status=status)

    bank_core_accounting_mock.set_response({'status': 'RETRY'})

    await stq_runner.bank_topup_core_topup.call(
        task_id='id',
        kwargs={'payment_id': common.TEST_PAYMENT_ID},
        expect_fail=False,
    )

    assert bank_core_accounting_mock.wallet_topup_save_handler.has_calls
    assert common.get_payment_status(pgsql) == status

    assert mock_stq_reschedule.has_calls
    assert (
        mock_stq_reschedule.next_call()['request'].json['queue_name']
        == 'bank_topup_core_topup'
    )


@pytest.mark.parametrize('wallet_id', ['balance_id', None])
async def test_stq_task_payed_bad_request(
        mockserver,
        stq_runner,
        pgsql,
        trust_mock,
        bank_core_accounting_mock,
        bank_core_agreement_mock,
        wallet_id,
):
    @mockserver.json_handler(
        r'/stq-agent/queues/api/add/(?P<queue_name>\w+)', regex=True,
    )
    def _mock_stq_schedule(request, queue_name):
        return {}

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(request):
        return {}

    common.set_wallet_id(pgsql, common.TEST_PAYMENT_ID, wallet_id)
    bank_core_accounting_mock.set_response(
        {'code': 'Bad request', 'message': 'bad data'},
    )
    bank_core_accounting_mock.set_http_status_code(400)

    common.set_payment_status(pgsql, status='PAYMENT_RECEIVED')

    await stq_runner.bank_topup_core_topup.call(
        task_id='id',
        kwargs={'payment_id': common.TEST_PAYMENT_ID},
        expect_fail=False,
    )

    assert bank_core_accounting_mock.wallet_topup_save_handler.has_calls
    assert common.get_payment_status(pgsql) == 'REFUNDING'
    assert _mock_stq_schedule.times_called == 1
    assert not mock_stq_reschedule.has_calls
    stq_schedule_next_call = _mock_stq_schedule.next_call()
    stq_req_json = stq_schedule_next_call['request'].json
    assert stq_req_json['task_id'] == f'bank_topup_{common.TEST_PAYMENT_ID}'
    stq_queue_name = stq_schedule_next_call['queue_name']
    assert stq_queue_name == 'bank_topup_trust_refund'


async def test_stq_task_success_saving_bad_request(
        stq_runner,
        pgsql,
        trust_mock,
        bank_core_accounting_mock,
        bank_core_agreement_mock,
):
    bank_core_accounting_mock.set_response(
        {'code': 'Bad request', 'message': 'bad data'},
    )
    bank_core_accounting_mock.set_http_status_code(400)

    common.set_payment_status(pgsql, status='SUCCESS_SAVING')

    await stq_runner.bank_topup_core_topup.call(
        task_id='id',
        kwargs={'payment_id': common.TEST_PAYMENT_ID},
        expect_fail=True,
    )

    assert bank_core_accounting_mock.wallet_topup_save_handler.has_calls
    assert common.get_payment_status(pgsql) == 'SUCCESS_SAVING'


@pytest.mark.parametrize(
    'status', ['FAILED', 'REFUNDED', 'FAILED_SAVING', 'REFUNDED_SAVING'],
)
@pytest.mark.parametrize('wallet_id', ['balance_id', None])
async def test_stq_task_failed_bad_request(
        stq_runner,
        pgsql,
        trust_mock,
        status,
        bank_core_accounting_mock,
        bank_core_agreement_mock,
        wallet_id,
):
    common.set_wallet_id(pgsql, common.TEST_PAYMENT_ID, wallet_id)
    bank_core_accounting_mock.set_response(
        {'code': 'Bad request', 'message': 'bad data'},
    )
    bank_core_accounting_mock.set_http_status_code(400)

    common.set_payment_status(pgsql, status=status)

    await stq_runner.bank_topup_core_topup.call(
        task_id='id',
        kwargs={'payment_id': common.TEST_PAYMENT_ID},
        expect_fail=True,
    )

    assert bank_core_accounting_mock.wallet_topup_save_handler.has_calls
    assert common.get_payment_status(pgsql) == status


@pytest.mark.parametrize('wallet_id', ['balance_id', None])
@pytest.mark.parametrize(
    'status', ['FAILED_SAVED', 'REFUNDED_SAVED', 'SUCCESS_SAVED'],
)
async def test_stq_task_already_saved(
        trust_mock,
        stq_runner,
        status,
        pgsql,
        bank_core_accounting_mock,
        bank_core_agreement_mock,
        wallet_id,
):
    common.set_wallet_id(pgsql, common.TEST_PAYMENT_ID, wallet_id)
    common.set_payment_status(pgsql, status=status)

    await stq_runner.bank_topup_core_topup.call(
        task_id='id',
        kwargs={'payment_id': common.TEST_PAYMENT_ID},
        expect_fail=False,
    )

    assert not bank_core_accounting_mock.wallet_topup_save_handler.has_calls


async def test_stq_sended_card(
        trust_mock,
        stq_runner,
        pgsql,
        mockserver,
        bank_core_accounting_mock,
        bank_core_agreement_mock,
):
    common.set_payment_status(pgsql, status='PAYMENT_RECEIVED')
    trust_mock.set_card_number('444433****1111')
    common.set_card_info(pgsql, 'VISA', '444433', '1111')

    @mockserver.json_handler(
        '/bank-core-accounting/v1/wallets/topup/save', prefix=False,
    )
    def topup_save_handler(request):
        payment_method = request.json['payment_method']
        assert payment_method['card_type'] == 'VISA'
        assert payment_method['card_num'] == '444433****1111'

        return mockserver.make_response(json={'status': 'SUCCESS'})

    await stq_runner.bank_topup_core_topup.call(
        task_id='id',
        kwargs={'payment_id': common.TEST_PAYMENT_ID},
        expect_fail=False,
    )

    assert topup_save_handler.has_calls


@pytest.mark.parametrize('wallet_id', ['balance_id', None])
async def test_stq_task_save_not_started_basket(
        trust_mock,
        stq_runner,
        pgsql,
        mockserver,
        bank_core_accounting_mock,
        bank_core_agreement_mock,
        wallet_id,
):
    @mockserver.json_handler(
        r'/bank-trust-payments/trust-payments/v2/payments/'
        r'(?P<purchase_token>\w+)',
        regex=True,
    )
    def _basket_info_handler(request, purchase_token):
        basket = {
            'purchase_token': purchase_token,
            'amount': '100',
            'currency': 'RUB',
            'payment_status': 'not_started',
            'orders': [
                {'order_id': '165469887', 'order_ts': '1630656576.123'},
            ],
        }

        return mockserver.make_response(status=200, json=basket)

    common.set_wallet_id(pgsql, common.TEST_PAYMENT_ID, wallet_id)
    common.set_payment_status(pgsql, status='FAILED')

    await stq_runner.bank_topup_core_topup.call(
        task_id='id',
        kwargs={'payment_id': common.TEST_PAYMENT_ID},
        expect_fail=False,
    )

    assert _basket_info_handler.has_calls
    assert bank_core_accounting_mock.wallet_topup_save_handler.has_calls


@pytest.mark.parametrize('wallet_id', ['balance_id', None])
async def test_check_trust_and_af_fields_equality(
        mockserver,
        stq_runner,
        pgsql,
        trust_mock,
        bank_core_accounting_mock,
        bank_core_agreement_mock,
        bank_risk,
        wallet_id,
):
    payment_status = 'PAYMENT_RECEIVED'
    common.set_payment_status(pgsql, status=payment_status)
    common.set_wallet_id(pgsql, common.TEST_PAYMENT_ID, wallet_id)
    trust_mock.set_payment_status(payment_status)

    trust_basket = copy.deepcopy(common.TRUST_BASKET_INFO)
    trust_basket['payment_status'] = payment_status

    @mockserver.json_handler('/bank-risk/risk/calculation/direct_credit_topup')
    def _risk_calculation_handler(request):
        assert request.method == 'POST'
        assert (
            request.json['session_uuid']
            == '9c4e663d-ff6e-4d12-9ebd-48c53c907791'
        )
        assert request.json['buid'] == 'bank_uid'
        assert request.json['client_ip'] == 'client_ip'
        assert 'device_id' in request.json
        assert request.json['yandex_uid'] == 'yandex_uid'
        assert request.json['trust_payment'] == trust_basket
        return mockserver.make_response(
            status=200,
            json={
                'resolution': 'ALLOW',
                'action': [],
                'af_decision_id': 'af_decision_id',
            },
        )

    await stq_runner.bank_topup_core_topup.call(
        task_id='id',
        kwargs={'payment_id': common.TEST_PAYMENT_ID},
        expect_fail=False,
    )


@pytest.mark.parametrize('wallet_id', ['balance_id', None])
async def test_deny_topup_by_new_af_decision_id(
        stq_runner, trust_mock, pgsql, bank_risk, wallet_id,
):
    common.set_payment_status(pgsql, status='PAYMENT_RECEIVED')
    common.set_wallet_id(pgsql, common.TEST_PAYMENT_ID, wallet_id)
    bank_risk.set_response('DENY', [])

    await stq_runner.bank_topup_core_topup.call(
        task_id='id',
        kwargs={'payment_id': common.TEST_PAYMENT_ID},
        expect_fail=False,
    )

    assert common.get_payment_status(pgsql) == 'REFUNDING'
    assert bank_risk.risk_calculation_handler.has_calls


@pytest.mark.parametrize('wallet_id', ['balance_id', None])
async def test_deny_topup_by_existed_af_decision_id(
        stq_runner, trust_mock, pgsql, bank_risk, bank_userinfo, wallet_id,
):
    common.set_wallet_id(pgsql, common.TEST_PAYMENT_ID, wallet_id)
    common.set_payment_status(
        pgsql,
        payment_id=PAYMENT_ID_WITH_DENIED_AF_DECISION,
        status='PAYMENT_RECEIVED',
    )

    await stq_runner.bank_topup_core_topup.call(
        task_id='id',
        kwargs={'payment_id': PAYMENT_ID_WITH_DENIED_AF_DECISION},
        expect_fail=False,
    )

    assert (
        common.get_payment_status(
            pgsql, payment_id=PAYMENT_ID_WITH_DENIED_AF_DECISION,
        )
        == 'REFUNDING'
    )
    assert not bank_risk.risk_calculation_handler.has_calls
    assert not bank_userinfo.get_antifraud_info_handler.has_calls


@pytest.mark.parametrize('wallet_id', ['balance_id', None])
async def test_deny_topup_by_existed_af_decision_id_refunded(
        stq_runner,
        trust_mock,
        pgsql,
        bank_risk,
        bank_userinfo,
        bank_core_accounting_mock,
        bank_core_agreement_mock,
        wallet_id,
):
    common.set_wallet_id(pgsql, common.TEST_PAYMENT_ID, wallet_id)
    common.set_payment_status(
        pgsql,
        payment_id=PAYMENT_ID_WITH_DENIED_AF_DECISION,
        status='REFUNDED',
    )

    await stq_runner.bank_topup_core_topup.call(
        task_id='id',
        kwargs={'payment_id': PAYMENT_ID_WITH_DENIED_AF_DECISION},
        expect_fail=False,
    )

    assert (
        common.get_payment_status(
            pgsql, payment_id=PAYMENT_ID_WITH_DENIED_AF_DECISION,
        )
        == 'REFUNDED_SAVED'
    )
    assert not bank_risk.risk_calculation_handler.has_calls
    assert not bank_userinfo.get_antifraud_info_handler.has_calls
    assert bank_core_accounting_mock.wallet_topup_save_handler.has_calls


@pytest.mark.parametrize('wallet_id', ['balance_id', None])
async def test_deny_failed_topup(
        mockserver,
        stq_runner,
        trust_mock,
        pgsql,
        bank_risk,
        bank_core_accounting_mock,
        bank_core_agreement_mock,
        wallet_id,
):
    common.set_wallet_id(pgsql, common.TEST_PAYMENT_ID, wallet_id)
    common.set_payment_status(pgsql, status='FAILED')
    bank_risk.set_response('DENY', [])

    @mockserver.json_handler(
        r'/stq-agent/queues/api/add/(?P<queue_name>\w+)', regex=True,
    )
    def mock_stq_schedule(request, queue_name):
        return {}

    await stq_runner.bank_topup_core_topup.call(
        task_id='id',
        kwargs={'payment_id': common.TEST_PAYMENT_ID},
        expect_fail=False,
    )

    assert common.get_payment_status(pgsql) == 'FAILED_SAVED'
    assert bank_risk.risk_calculation_handler.has_calls
    assert not mock_stq_schedule.has_calls


@pytest.mark.parametrize('wallet_id', ['balance_id', None])
@pytest.mark.parametrize(
    'init_status,final_status',
    [
        ('PAYMENT_RECEIVED', 'SUCCESS_SAVED'),
        ('REFUNDED', 'REFUNDED_SAVED'),
        ('FAILED', 'FAILED_SAVED'),
        ('FAILED_SAVING', 'FAILED_SAVED'),
        ('REFUNDED_SAVING', 'REFUNDED_SAVED'),
        ('SUCCESS_SAVING', 'SUCCESS_SAVED'),
    ],
)
async def test_allow_topup_by_existed_af_decision_id(
        stq_runner,
        pgsql,
        trust_mock,
        bank_core_accounting_mock,
        bank_core_agreement_mock,
        bank_risk,
        bank_userinfo,
        init_status,
        final_status,
        wallet_id,
):
    common.set_wallet_id(pgsql, common.TEST_PAYMENT_ID, wallet_id)
    common.set_payment_status(
        pgsql,
        payment_id=PAYMENT_ID_WITH_ALLOWED_AF_DECISION,
        status=init_status,
    )

    await stq_runner.bank_topup_core_topup.call(
        task_id='id',
        kwargs={'payment_id': PAYMENT_ID_WITH_ALLOWED_AF_DECISION},
        expect_fail=False,
    )

    assert (
        common.get_payment_status(
            pgsql, payment_id=PAYMENT_ID_WITH_ALLOWED_AF_DECISION,
        )
        == final_status
    )
    assert bank_core_accounting_mock.wallet_topup_save_handler.has_calls
    assert not bank_risk.risk_calculation_handler.has_calls
    assert not bank_userinfo.get_antifraud_info_handler.has_calls


@pytest.mark.parametrize('wallet_id', ['balance_id', None])
@pytest.mark.parametrize(
    'init_status,final_status, risk_has_calls',
    [
        ('PAYMENT_RECEIVED', 'SUCCESS_SAVED', True),
        ('REFUNDED', 'REFUNDED_SAVED', False),
        ('FAILED', 'FAILED_SAVED', True),
        ('FAILED_SAVING', 'FAILED_SAVED', True),
        ('REFUNDED_SAVING', 'REFUNDED_SAVED', False),
        ('SUCCESS_SAVING', 'SUCCESS_SAVED', True),
    ],
)
async def test_fallback_without_af_and_bank_userinfo(
        stq_runner,
        pgsql,
        trust_mock,
        bank_core_accounting_mock,
        bank_core_agreement_mock,
        bank_risk,
        init_status,
        final_status,
        risk_has_calls,
        bank_userinfo,
        wallet_id,
):
    common.set_wallet_id(pgsql, common.TEST_PAYMENT_ID, wallet_id)
    bank_risk.set_http_status_code(500)
    bank_userinfo.set_http_status_code(500)
    common.set_payment_status(pgsql, status=init_status)

    await stq_runner.bank_topup_core_topup.call(
        task_id='id',
        kwargs={'payment_id': common.TEST_PAYMENT_ID},
        expect_fail=False,
    )

    assert common.get_payment_status(pgsql) == final_status
    assert bank_risk.risk_calculation_handler.has_calls == risk_has_calls
    assert bank_core_accounting_mock.wallet_topup_save_handler.has_calls
    assert bank_userinfo.get_antifraud_info_handler.has_calls


@pytest.mark.parametrize('wallet_id', ['balance_id', None])
@pytest.mark.parametrize(
    'init_status,final_status',
    [
        ('PAYMENT_RECEIVED', 'SUCCESS_SAVED'),
        ('REFUNDED', 'REFUNDED_SAVED'),
        ('FAILED', 'FAILED_SAVED'),
        ('FAILED_SAVING', 'FAILED_SAVED'),
        ('REFUNDED_SAVING', 'REFUNDED_SAVED'),
        ('SUCCESS_SAVING', 'SUCCESS_SAVED'),
    ],
)
async def test_no_device_id_in_antifraud_info(
        stq_runner,
        pgsql,
        trust_mock,
        bank_core_accounting_mock,
        bank_core_agreement_mock,
        bank_risk,
        init_status,
        final_status,
        bank_userinfo,
        wallet_id,
):
    bank_userinfo.set_response({})
    common.set_wallet_id(pgsql, common.TEST_PAYMENT_ID, wallet_id)
    common.set_payment_status(pgsql, status=init_status)

    await stq_runner.bank_topup_core_topup.call(
        task_id='id',
        kwargs={'payment_id': common.TEST_PAYMENT_ID},
        expect_fail=False,
    )

    assert common.get_payment_status(pgsql) == final_status
    assert bank_core_accounting_mock.wallet_topup_save_handler.has_calls
    assert bank_userinfo.get_antifraud_info_handler.has_calls
