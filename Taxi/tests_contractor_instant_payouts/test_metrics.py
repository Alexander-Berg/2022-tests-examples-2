import pytest

MODULBANK_PROCESS_PAYOUT_ID = '00000000-0000-0000-0001-000000000000'
MODULBANK_POLL_PAYOUT_ID = '00000000-0000-0000-0001-000000000001'
MOZEN_PROCESS_PAYOUT_ID = '00000000-0000-0000-0002-000000000000'
MOZEN_POLL_PAYOUT_ID = '00000000-0000-0000-0002-000000000001'
QIWI_PROCESS_PAYOUT_ID = '00000000-0000-0000-0003-000000000000'
QIWI_POLL_PAYOUT_ID = '00000000-0000-0000-0003-000000000001'
BANK_PAYOUT_ID = '00000001-0002-0003-0004-000000000005'
BAD_PAYOUT_ID = '00000001-0002-0002-0002-000000000000'

MODULBANK_PROCESS_MOCK_URL = (
    '/contractor-instant-payouts-modulbank/api/payouts'
)

MODULBANK_POLL_MOCK_URL = (
    '/contractor-instant-payouts-modulbank/api/payouts/' + BANK_PAYOUT_ID
)

MOZEN_PROCESS_MOCK_URL = (
    '/contractor-instant-payouts-mozen/api/public/payout/pay'
)

MOZEN_POLL_MOCK_URL = (
    '/contractor-instant-payouts-mozen/api/public/payout/pay/status/'
    + BANK_PAYOUT_ID
)

QIWI_POLL_MOCK_URL = (
    '/contractor-instant-payouts-qiwi/partner/payout/'
    'v1/agents/agent/points/point/payments/' + QIWI_POLL_PAYOUT_ID
)

QIWI_PROCESS_MOCK_URL = (
    '/contractor-instant-payouts-qiwi/partner/payout/'
    'v1/agents/agent/points/point/payments/' + QIWI_PROCESS_PAYOUT_ID
)

QIWI_MOCK_EXECUTE_URL = (
    '/contractor-instant-payouts-qiwi/partner/payout/'
    'v1/agents/agent/points/point/payments/'
    + QIWI_PROCESS_PAYOUT_ID
    + '/execute'
)

MODULBANK_PROCESS_OK_RESPONSE = {
    'status': 'success',
    'data': {'id': BANK_PAYOUT_ID},
}

MODULBANK_POLL_OK_RESPONSE = {
    'status': 'success',
    'data': {
        'id': BANK_PAYOUT_ID,
        'status': 'completed',
        'transactions': [
            {'id': BANK_PAYOUT_ID, 'amount': 100, 'commission': 1.5},
        ],
    },
}


def build_mozen_process_response(payout_id):
    return {
        'id': payout_id,
        'payment_id': BANK_PAYOUT_ID,
        'value': {'currency': 'RUB', 'amount': 10000},
        'comission': {'currency': 'RUB', 'amount': 1500},
        'status': 'accepted',
    }


MOZEN_POLL_OK_RESPONSE = {'payment_id': BANK_PAYOUT_ID, 'status': 'succeed'}

QIWI_PROCESS_OK_RESPONSE = {'status': {'value': 'READY'}}

QIWI_EXECUTE_OK_RESPONSE = {'status': {'value': 'IN_PROGRESS'}}

QIWI_POLL_OK_RESPONSE = {'status': {'value': 'COMPLETED'}}


def get_metrics(metrics_json):
    return {
        'modulbank_ok': metrics_json['modulbank_ok'],
        'modulbank_errors': metrics_json['modulbank_errors'],
        'mozen_ok': metrics_json['mozen_ok'],
        'mozen_errors': metrics_json['mozen_errors'],
        'qiwi_ok': metrics_json['qiwi_ok'],
        'qiwi_errors': metrics_json['qiwi_errors'],
    }


@pytest.mark.parametrize(
    'payout_id',
    [
        MODULBANK_PROCESS_PAYOUT_ID,
        MODULBANK_POLL_PAYOUT_ID,
        MOZEN_PROCESS_PAYOUT_ID,
        MOZEN_POLL_PAYOUT_ID,
        QIWI_PROCESS_PAYOUT_ID,
        QIWI_POLL_PAYOUT_ID,
    ],
)
async def test_metrics_ok(
        stq_runner,
        mockserver,
        taxi_contractor_instant_payouts_monitor,
        payout_id,
        mock_api,
):
    @mockserver.json_handler(MODULBANK_PROCESS_MOCK_URL)
    def _modulbank_process_handler(request):
        return MODULBANK_PROCESS_OK_RESPONSE

    @mockserver.json_handler(MODULBANK_POLL_MOCK_URL)
    def _modulbank_poll_handler(request):
        return MODULBANK_POLL_OK_RESPONSE

    @mockserver.json_handler(MOZEN_PROCESS_MOCK_URL)
    def _mozen_process_handler(request):
        return build_mozen_process_response(payout_id)

    @mockserver.json_handler(MOZEN_POLL_MOCK_URL)
    def _mozen_poll_handler(request):
        return MOZEN_POLL_OK_RESPONSE

    @mockserver.json_handler(QIWI_MOCK_EXECUTE_URL)
    def _qiwi_execute_handler(request):
        return QIWI_EXECUTE_OK_RESPONSE

    @mockserver.json_handler(QIWI_POLL_MOCK_URL)
    def _qiwi_poll_handler(request):
        return QIWI_POLL_OK_RESPONSE

    @mockserver.json_handler(QIWI_PROCESS_MOCK_URL)
    def _qiwi_process_handler(request):
        return QIWI_PROCESS_OK_RESPONSE

    metrics_json = await taxi_contractor_instant_payouts_monitor.get_metric(
        'transaction_metrics',
    )
    old_metrics = get_metrics(metrics_json)

    if payout_id == MODULBANK_PROCESS_PAYOUT_ID:
        await stq_runner.contractor_instant_payouts_modulbank_process.call(
            task_id='1', kwargs={'id': payout_id},
        )
    elif payout_id == MODULBANK_POLL_PAYOUT_ID:
        await stq_runner.contractor_instant_payouts_modulbank_poll.call(
            task_id='1', kwargs={'id': payout_id},
        )
    elif payout_id == MOZEN_PROCESS_PAYOUT_ID:
        await stq_runner.contractor_instant_payouts_alfabank_process.call(
            task_id='1', kwargs={'id': payout_id},
        )
    elif payout_id == MOZEN_POLL_PAYOUT_ID:
        await stq_runner.contractor_instant_payouts_alfabank_poll.call(
            task_id='1', kwargs={'id': payout_id},
        )
    elif payout_id == QIWI_PROCESS_PAYOUT_ID:
        await stq_runner.contractor_instant_payouts_qiwi_process.call(
            task_id='1', kwargs={'id': payout_id},
        )
    elif payout_id == QIWI_POLL_PAYOUT_ID:
        await stq_runner.contractor_instant_payouts_qiwi_poll.call(
            task_id='1', kwargs={'id': payout_id},
        )

    metrics_json = await taxi_contractor_instant_payouts_monitor.get_metric(
        'transaction_metrics',
    )
    metrics = get_metrics(metrics_json)

    if payout_id in (MODULBANK_PROCESS_PAYOUT_ID, MODULBANK_POLL_PAYOUT_ID):
        assert metrics['modulbank_ok'] - old_metrics['modulbank_ok'] == 1
        assert metrics['modulbank_errors'] == old_metrics['modulbank_errors']
        assert metrics['mozen_ok'] == old_metrics['mozen_ok']
        assert metrics['mozen_errors'] == old_metrics['mozen_errors']
        assert metrics['qiwi_ok'] == old_metrics['qiwi_ok']
        assert metrics['qiwi_errors'] == old_metrics['qiwi_errors']
    elif payout_id in (MOZEN_PROCESS_PAYOUT_ID, MOZEN_POLL_PAYOUT_ID):
        assert metrics['mozen_ok'] - old_metrics['mozen_ok'] == 1
        assert metrics['mozen_errors'] == old_metrics['mozen_errors']
        assert metrics['modulbank_ok'] == old_metrics['modulbank_ok']
        assert metrics['modulbank_errors'] == old_metrics['modulbank_errors']
        assert metrics['qiwi_ok'] == old_metrics['qiwi_ok']
        assert metrics['qiwi_errors'] == old_metrics['qiwi_errors']
    elif payout_id in (QIWI_PROCESS_PAYOUT_ID, QIWI_POLL_PAYOUT_ID):
        assert metrics['qiwi_ok'] - old_metrics['qiwi_ok'] == 1
        assert metrics['qiwi_errors'] == old_metrics['qiwi_errors']
        assert metrics['mozen_ok'] == old_metrics['mozen_ok']
        assert metrics['mozen_errors'] == old_metrics['mozen_errors']
        assert metrics['modulbank_ok'] == old_metrics['modulbank_ok']
        assert metrics['modulbank_errors'] == old_metrics['modulbank_errors']


MODULBANK_POLL_BAD_RESPONSE = {
    'status': 'success',
    'data': {
        'id': BANK_PAYOUT_ID,
        'status': 'failed',
        'transactions': [
            {
                'id': BANK_PAYOUT_ID,
                'amount': 100,
                'reason_code': 'ERR_INSUFFICIENT_BALANCE',
            },
        ],
    },
}

MOZEN_PROCESS_BAD_RESPONSE = {
    'code': 'NotEnoughMoneyError',
    'message': 'Error message',
}

MOZEN_POLL_BAD_RESPONSE = {'payment_id': BANK_PAYOUT_ID, 'status': 'failed'}

QIWI_PROCESS_BAD_RESPONSE = {'status': {'value': 'READY'}}

QIWI_EXECUTE_BAD_RESPONSE = {
    'status': {'value': 'FAILED', 'errorCode': 'INSUFFICIENT_FUNDS'},
}

QIWI_POLL_BAD_RESPONSE = {
    'status': {'value': 'FAILED', 'errorCode': 'INSUFFICIENT_FUNDS'},
}


@pytest.mark.parametrize(
    'payout_id',
    [
        MODULBANK_POLL_PAYOUT_ID,
        MOZEN_PROCESS_PAYOUT_ID,
        MOZEN_POLL_PAYOUT_ID,
        QIWI_PROCESS_PAYOUT_ID,
        QIWI_POLL_PAYOUT_ID,
    ],
)
async def test_metrics_ok_errors(
        stq_runner,
        mockserver,
        taxi_contractor_instant_payouts_monitor,
        payout_id,
        mock_api,
):
    @mockserver.json_handler(MODULBANK_POLL_MOCK_URL)
    def _modulbank_poll_handler(request):
        return MODULBANK_POLL_BAD_RESPONSE

    @mockserver.json_handler(MOZEN_PROCESS_MOCK_URL)
    def _mozen_process_handler(request):
        return mockserver.make_response(
            status=400, json=MOZEN_PROCESS_BAD_RESPONSE,
        )

    @mockserver.json_handler(MOZEN_POLL_MOCK_URL)
    def _mozen_poll_handler(request):
        return MOZEN_POLL_BAD_RESPONSE

    @mockserver.json_handler(QIWI_MOCK_EXECUTE_URL)
    def _qiwi_execute_handler(request):
        return QIWI_EXECUTE_BAD_RESPONSE

    @mockserver.json_handler(QIWI_POLL_MOCK_URL)
    def _qiwi_poll_handler(request):
        return QIWI_POLL_BAD_RESPONSE

    @mockserver.json_handler(QIWI_PROCESS_MOCK_URL)
    def _qiwi_process_handler(request):
        return QIWI_PROCESS_BAD_RESPONSE

    metrics_json = await taxi_contractor_instant_payouts_monitor.get_metric(
        'transaction_metrics',
    )
    old_metrics = get_metrics(metrics_json)

    if payout_id == MODULBANK_POLL_PAYOUT_ID:
        await stq_runner.contractor_instant_payouts_modulbank_poll.call(
            task_id='1', kwargs={'id': payout_id},
        )
    elif payout_id == MOZEN_PROCESS_PAYOUT_ID:
        await stq_runner.contractor_instant_payouts_alfabank_process.call(
            task_id='1', kwargs={'id': payout_id},
        )
    elif payout_id == MOZEN_POLL_PAYOUT_ID:
        await stq_runner.contractor_instant_payouts_alfabank_poll.call(
            task_id='1', kwargs={'id': payout_id},
        )
    elif payout_id == QIWI_PROCESS_PAYOUT_ID:
        await stq_runner.contractor_instant_payouts_qiwi_process.call(
            task_id='1', kwargs={'id': payout_id},
        )
    elif payout_id == QIWI_POLL_PAYOUT_ID:
        await stq_runner.contractor_instant_payouts_qiwi_poll.call(
            task_id='1', kwargs={'id': payout_id},
        )

    metrics_json = await taxi_contractor_instant_payouts_monitor.get_metric(
        'transaction_metrics',
    )
    metrics = get_metrics(metrics_json)

    if payout_id in (MODULBANK_PROCESS_PAYOUT_ID, MODULBANK_POLL_PAYOUT_ID):
        assert metrics['modulbank_ok'] - old_metrics['modulbank_ok'] == 1
        assert metrics['modulbank_errors'] == old_metrics['modulbank_errors']
        assert metrics['mozen_ok'] == old_metrics['mozen_ok']
        assert metrics['mozen_errors'] == old_metrics['mozen_errors']
        assert metrics['qiwi_ok'] == old_metrics['qiwi_ok']
        assert metrics['qiwi_errors'] == old_metrics['qiwi_errors']
    elif payout_id in (MOZEN_PROCESS_PAYOUT_ID, MOZEN_POLL_PAYOUT_ID):
        assert metrics['mozen_ok'] - old_metrics['mozen_ok'] == 1
        assert metrics['mozen_errors'] == old_metrics['mozen_errors']
        assert metrics['modulbank_ok'] == old_metrics['modulbank_ok']
        assert metrics['modulbank_errors'] == old_metrics['modulbank_errors']
        assert metrics['qiwi_ok'] == old_metrics['qiwi_ok']
        assert metrics['qiwi_errors'] == old_metrics['qiwi_errors']
    elif payout_id in (QIWI_PROCESS_PAYOUT_ID, QIWI_POLL_PAYOUT_ID):
        assert metrics['qiwi_ok'] - old_metrics['qiwi_ok'] == 1
        assert metrics['qiwi_errors'] == old_metrics['qiwi_errors']
        assert metrics['mozen_ok'] == old_metrics['mozen_ok']
        assert metrics['mozen_errors'] == old_metrics['mozen_errors']
        assert metrics['modulbank_ok'] == old_metrics['modulbank_ok']
        assert metrics['modulbank_errors'] == old_metrics['modulbank_errors']


MODULBANK_POLL_FAIL_RESPONSE = {
    'status': 'success',
    'data': {
        'id': BANK_PAYOUT_ID,
        'status': 'failed',
        'transactions': [
            {
                'id': BANK_PAYOUT_ID,
                'amount': 100,
                'reason_code': 'ERR_UNKNOWN',
            },
        ],
    },
}

MOZEN_PROCESS_FAIL_RESPONSE = {'code': 'Unknown', 'message': 'Error message'}

MOZEN_POLL_FAIL_RESPONSE = {'payment_id': BANK_PAYOUT_ID, 'status': 'error'}

QIWI_PROCESS_FAIL_RESPONSE = {'status': {'value': 'READY'}}

QIWI_EXECUTE_FAIL_RESPONSE = {
    'status': {'value': 'FAILED', 'errorCode': 'BILLING_DECLINED'},
}

QIWI_POLL_FAIL_RESPONSE = {
    'status': {'value': 'FAILED', 'errorCode': 'BILLING_DECLINED'},
}


@pytest.mark.parametrize(
    'payout_id',
    [
        MODULBANK_POLL_PAYOUT_ID,
        MOZEN_PROCESS_PAYOUT_ID,
        MOZEN_POLL_PAYOUT_ID,
        QIWI_PROCESS_PAYOUT_ID,
        QIWI_POLL_PAYOUT_ID,
    ],
)
async def test_metrics_fails(
        stq_runner,
        mockserver,
        taxi_contractor_instant_payouts_monitor,
        payout_id,
        mock_api,
):
    @mockserver.json_handler(MODULBANK_POLL_MOCK_URL)
    def _modulbank_poll_handler(request):
        return MODULBANK_POLL_FAIL_RESPONSE

    @mockserver.json_handler(MOZEN_PROCESS_MOCK_URL)
    def _mozen_process_handler(request):
        return mockserver.make_response(
            status=400, json=MOZEN_PROCESS_FAIL_RESPONSE,
        )

    @mockserver.json_handler(MOZEN_POLL_MOCK_URL)
    def _mozen_poll_handler(request):
        return MOZEN_POLL_FAIL_RESPONSE

    @mockserver.json_handler(QIWI_MOCK_EXECUTE_URL)
    def _qiwi_execute_handler(request):
        return QIWI_EXECUTE_FAIL_RESPONSE

    @mockserver.json_handler(QIWI_POLL_MOCK_URL)
    def _qiwi_poll_handler(request):
        return QIWI_POLL_FAIL_RESPONSE

    @mockserver.json_handler(QIWI_PROCESS_MOCK_URL)
    def _qiwi_process_handler(request):
        return QIWI_PROCESS_FAIL_RESPONSE

    metrics_json = await taxi_contractor_instant_payouts_monitor.get_metric(
        'transaction_metrics',
    )
    old_metrics = get_metrics(metrics_json)

    if payout_id == MODULBANK_POLL_PAYOUT_ID:
        await stq_runner.contractor_instant_payouts_modulbank_poll.call(
            task_id='1', kwargs={'id': payout_id},
        )
    elif payout_id == MOZEN_PROCESS_PAYOUT_ID:
        await stq_runner.contractor_instant_payouts_alfabank_process.call(
            task_id='1', kwargs={'id': payout_id},
        )
    elif payout_id == MOZEN_POLL_PAYOUT_ID:
        await stq_runner.contractor_instant_payouts_alfabank_poll.call(
            task_id='1', kwargs={'id': payout_id},
        )
    elif payout_id == QIWI_PROCESS_PAYOUT_ID:
        await stq_runner.contractor_instant_payouts_qiwi_process.call(
            task_id='1', kwargs={'id': payout_id},
        )
    elif payout_id == QIWI_POLL_PAYOUT_ID:
        await stq_runner.contractor_instant_payouts_qiwi_poll.call(
            task_id='1', kwargs={'id': payout_id},
        )

    metrics_json = await taxi_contractor_instant_payouts_monitor.get_metric(
        'transaction_metrics',
    )
    metrics = get_metrics(metrics_json)

    if payout_id == MODULBANK_POLL_PAYOUT_ID:
        assert (
            metrics['modulbank_errors'] - old_metrics['modulbank_errors'] == 1
        )
        assert metrics['mozen_errors'] == old_metrics['mozen_errors']
        assert metrics['modulbank_ok'] == old_metrics['modulbank_ok']
        assert metrics['mozen_ok'] == old_metrics['mozen_ok']
        assert metrics['qiwi_ok'] == old_metrics['qiwi_ok']
        assert metrics['qiwi_errors'] == old_metrics['qiwi_errors']
    elif payout_id in (MOZEN_PROCESS_PAYOUT_ID, MOZEN_POLL_PAYOUT_ID):
        assert metrics['mozen_errors'] - old_metrics['mozen_errors'] == 1
        assert metrics['mozen_ok'] == old_metrics['mozen_ok']
        assert metrics['modulbank_ok'] == old_metrics['modulbank_ok']
        assert metrics['modulbank_errors'] == old_metrics['modulbank_errors']
        assert metrics['qiwi_ok'] == old_metrics['qiwi_ok']
        assert metrics['qiwi_errors'] == old_metrics['qiwi_errors']
    elif payout_id in (QIWI_PROCESS_PAYOUT_ID, QIWI_POLL_PAYOUT_ID):
        assert metrics['qiwi_errors'] - old_metrics['qiwi_errors'] == 1
        assert metrics['qiwi_ok'] == old_metrics['qiwi_ok']
        assert metrics['mozen_ok'] == old_metrics['mozen_ok']
        assert metrics['mozen_errors'] == old_metrics['mozen_errors']
        assert metrics['modulbank_ok'] == old_metrics['modulbank_ok']
        assert metrics['modulbank_errors'] == old_metrics['modulbank_errors']


@pytest.mark.parametrize(
    'payout_id',
    [
        MODULBANK_PROCESS_PAYOUT_ID,
        MODULBANK_POLL_PAYOUT_ID,
        MOZEN_PROCESS_PAYOUT_ID,
        MOZEN_POLL_PAYOUT_ID,
        QIWI_PROCESS_PAYOUT_ID,
        QIWI_POLL_PAYOUT_ID,
    ],
)
async def test_metrics_errors(
        stq_runner,
        mockserver,
        taxi_contractor_instant_payouts_monitor,
        payout_id,
        mock_api,
):
    @mockserver.json_handler(MODULBANK_PROCESS_MOCK_URL)
    def _modulbank_process_handler(request):
        return mockserver.make_response('fail', status=500)

    @mockserver.json_handler(MODULBANK_POLL_MOCK_URL)
    def _modulbank_poll_handler(request):
        return mockserver.make_response('fail', status=500)

    @mockserver.json_handler(MOZEN_PROCESS_MOCK_URL)
    def _mozen_process_handler(request):
        return mockserver.make_response('fail', status=500)

    @mockserver.json_handler(MOZEN_POLL_MOCK_URL)
    def _mozen_poll_handler(request):
        return mockserver.make_response('fail', status=500)

    @mockserver.json_handler(QIWI_POLL_MOCK_URL)
    def _qiwi_poll_handler(request):
        return mockserver.make_response('fail', status=500)

    @mockserver.json_handler(QIWI_PROCESS_MOCK_URL)
    def _qiwi_process_handler(request):
        return mockserver.make_response('fail', status=500)

    @mockserver.json_handler(QIWI_MOCK_EXECUTE_URL)
    def _qiwi_execute_handler(request):
        return mockserver.make_response('fail', status=500)

    metrics_json = await taxi_contractor_instant_payouts_monitor.get_metric(
        'transaction_metrics',
    )
    old_metrics = get_metrics(metrics_json)

    if payout_id == MODULBANK_PROCESS_PAYOUT_ID:
        await stq_runner.contractor_instant_payouts_modulbank_process.call(
            task_id='1', kwargs={'id': payout_id}, expect_fail=True,
        )
    elif payout_id == MODULBANK_POLL_PAYOUT_ID:
        await stq_runner.contractor_instant_payouts_modulbank_poll.call(
            task_id='1', kwargs={'id': payout_id}, expect_fail=True,
        )
    elif payout_id == MOZEN_PROCESS_PAYOUT_ID:
        await stq_runner.contractor_instant_payouts_alfabank_process.call(
            task_id='1', kwargs={'id': payout_id}, expect_fail=True,
        )
    elif payout_id == MOZEN_POLL_PAYOUT_ID:
        await stq_runner.contractor_instant_payouts_alfabank_poll.call(
            task_id='1', kwargs={'id': payout_id}, expect_fail=True,
        )
    elif payout_id == QIWI_PROCESS_PAYOUT_ID:
        await stq_runner.contractor_instant_payouts_qiwi_process.call(
            task_id='1', kwargs={'id': payout_id}, expect_fail=True,
        )
    elif payout_id == QIWI_POLL_PAYOUT_ID:
        await stq_runner.contractor_instant_payouts_qiwi_poll.call(
            task_id='1', kwargs={'id': payout_id}, expect_fail=True,
        )

    metrics_json = await taxi_contractor_instant_payouts_monitor.get_metric(
        'transaction_metrics',
    )
    metrics = get_metrics(metrics_json)

    if payout_id == MODULBANK_POLL_PAYOUT_ID:
        assert (
            metrics['modulbank_errors'] - old_metrics['modulbank_errors'] == 1
        )
        assert metrics['mozen_errors'] == old_metrics['mozen_errors']
        assert metrics['modulbank_ok'] == old_metrics['modulbank_ok']
        assert metrics['mozen_ok'] == old_metrics['mozen_ok']
        assert metrics['qiwi_ok'] == old_metrics['qiwi_ok']
        assert metrics['qiwi_errors'] == old_metrics['qiwi_errors']
    elif payout_id in (MOZEN_PROCESS_PAYOUT_ID, MOZEN_POLL_PAYOUT_ID):
        assert metrics['mozen_errors'] - old_metrics['mozen_errors'] == 1
        assert metrics['mozen_ok'] == old_metrics['mozen_ok']
        assert metrics['modulbank_ok'] == old_metrics['modulbank_ok']
        assert metrics['modulbank_errors'] == old_metrics['modulbank_errors']
        assert metrics['qiwi_ok'] == old_metrics['qiwi_ok']
        assert metrics['qiwi_errors'] == old_metrics['qiwi_errors']
    elif payout_id in (QIWI_PROCESS_PAYOUT_ID, QIWI_POLL_PAYOUT_ID):
        assert metrics['qiwi_errors'] - old_metrics['qiwi_errors'] == 1
        assert metrics['qiwi_ok'] == old_metrics['qiwi_ok']
        assert metrics['mozen_ok'] == old_metrics['mozen_ok']
        assert metrics['mozen_errors'] == old_metrics['mozen_errors']
        assert metrics['modulbank_ok'] == old_metrics['modulbank_ok']
        assert metrics['modulbank_errors'] == old_metrics['modulbank_errors']


@pytest.mark.parametrize(
    'payout_id',
    [
        MODULBANK_PROCESS_PAYOUT_ID,
        MODULBANK_POLL_PAYOUT_ID,
        MOZEN_PROCESS_PAYOUT_ID,
        MOZEN_POLL_PAYOUT_ID,
        QIWI_PROCESS_PAYOUT_ID,
        QIWI_POLL_PAYOUT_ID,
    ],
)
async def test_metrics_parsing_errors(
        stq_runner,
        mockserver,
        taxi_contractor_instant_payouts_monitor,
        payout_id,
        mock_api,
):
    @mockserver.json_handler(MODULBANK_PROCESS_MOCK_URL)
    def _modulbank_process_handler(request):
        return {}

    @mockserver.json_handler(MODULBANK_POLL_MOCK_URL)
    def _modulbank_poll_handler(request):
        return {}

    @mockserver.json_handler(MOZEN_PROCESS_MOCK_URL)
    def _mozen_process_handler(request):
        return {}

    @mockserver.json_handler(MOZEN_POLL_MOCK_URL)
    def _mozen_poll_handler(request):
        return {}

    @mockserver.json_handler(QIWI_POLL_MOCK_URL)
    def _qiwi_poll_handler(request):
        return {}

    @mockserver.json_handler(QIWI_PROCESS_MOCK_URL)
    def _qiwi_process_handler(request):
        return {}

    @mockserver.json_handler(QIWI_MOCK_EXECUTE_URL)
    def _qiwi_execute_handler(request):
        return {}

    metrics_json = await taxi_contractor_instant_payouts_monitor.get_metric(
        'transaction_metrics',
    )
    old_metrics = get_metrics(metrics_json)

    if payout_id == MODULBANK_PROCESS_PAYOUT_ID:
        await stq_runner.contractor_instant_payouts_modulbank_process.call(
            task_id='1', kwargs={'id': payout_id}, expect_fail=True,
        )
    elif payout_id == MODULBANK_POLL_PAYOUT_ID:
        await stq_runner.contractor_instant_payouts_modulbank_poll.call(
            task_id='1', kwargs={'id': payout_id}, expect_fail=True,
        )
    elif payout_id == MOZEN_PROCESS_PAYOUT_ID:
        await stq_runner.contractor_instant_payouts_alfabank_process.call(
            task_id='1', kwargs={'id': payout_id}, expect_fail=True,
        )
    elif payout_id == MOZEN_POLL_PAYOUT_ID:
        await stq_runner.contractor_instant_payouts_alfabank_poll.call(
            task_id='1', kwargs={'id': payout_id}, expect_fail=True,
        )
    elif payout_id == QIWI_PROCESS_PAYOUT_ID:
        await stq_runner.contractor_instant_payouts_qiwi_process.call(
            task_id='1', kwargs={'id': payout_id}, expect_fail=True,
        )
    elif payout_id == QIWI_POLL_PAYOUT_ID:
        await stq_runner.contractor_instant_payouts_qiwi_poll.call(
            task_id='1', kwargs={'id': payout_id}, expect_fail=True,
        )

    metrics_json = await taxi_contractor_instant_payouts_monitor.get_metric(
        'transaction_metrics',
    )
    metrics = get_metrics(metrics_json)

    if payout_id == MODULBANK_POLL_PAYOUT_ID:
        assert (
            metrics['modulbank_errors'] - old_metrics['modulbank_errors'] == 1
        )
        assert metrics['mozen_errors'] == old_metrics['mozen_errors']
        assert metrics['modulbank_ok'] == old_metrics['modulbank_ok']
        assert metrics['mozen_ok'] == old_metrics['mozen_ok']
        assert metrics['qiwi_ok'] == old_metrics['qiwi_ok']
        assert metrics['qiwi_errors'] == old_metrics['qiwi_errors']
    elif payout_id in (MOZEN_PROCESS_PAYOUT_ID, MOZEN_POLL_PAYOUT_ID):
        assert metrics['mozen_errors'] - old_metrics['mozen_errors'] == 1
        assert metrics['mozen_ok'] == old_metrics['mozen_ok']
        assert metrics['modulbank_ok'] == old_metrics['modulbank_ok']
        assert metrics['modulbank_errors'] == old_metrics['modulbank_errors']
        assert metrics['qiwi_ok'] == old_metrics['qiwi_ok']
        assert metrics['qiwi_errors'] == old_metrics['qiwi_errors']
    elif payout_id in (QIWI_PROCESS_PAYOUT_ID, QIWI_POLL_PAYOUT_ID):
        assert metrics['qiwi_errors'] - old_metrics['qiwi_errors'] == 1
        assert metrics['qiwi_ok'] == old_metrics['qiwi_ok']
        assert metrics['mozen_ok'] == old_metrics['mozen_ok']
        assert metrics['mozen_errors'] == old_metrics['mozen_errors']
        assert metrics['modulbank_ok'] == old_metrics['modulbank_ok']
        assert metrics['modulbank_errors'] == old_metrics['modulbank_errors']
