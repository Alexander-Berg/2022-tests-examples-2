import datetime

import pytest

from tests_bank_topup import common


def get_card_info(pgsql, payment_id=common.TEST_PAYMENT_ID):
    cursor = pgsql['bank_topup'].cursor()
    cursor.execute(
        'select card_bin, card_payment_system::TEXT, card_last_digits '
        'from bank_topup.payments '
        'where payment_id = %s::UUID',
        (payment_id,),
    )
    return cursor.fetchall()[0]


def get_rrn(pgsql, payment_id=common.TEST_PAYMENT_ID):
    cursor = pgsql['bank_topup'].cursor()
    cursor.execute(
        'select rrn '
        'from bank_topup.payments '
        'where payment_id = %s::UUID',
        (payment_id,),
    )
    return cursor.fetchall()[0][0]


def set_created_timestamp(pgsql, timestamp, payment_id=common.TEST_PAYMENT_ID):
    cursor = pgsql['bank_topup'].cursor()
    cursor.execute(
        'update bank_topup.payments '
        'set created_at = %s '
        'where payment_id = %s::UUID',
        (timestamp, payment_id),
    )


async def test_stq_task_authorized(mockserver, stq_runner, pgsql, trust_mock):
    @mockserver.json_handler(
        r'/stq-agent/queues/api/add/(?P<queue_name>\w+)', regex=True,
    )
    def _mock_stq_schedule(request, queue_name):
        return {}

    trust_mock.set_payment_status('authorized')
    await stq_runner.bank_topup_payment_status_trust.call(
        task_id='id',
        kwargs={'payment_id': common.TEST_PAYMENT_ID},
        expect_fail=False,
    )

    assert _mock_stq_schedule.times_called == 1
    stq_schedule_next_call = _mock_stq_schedule.next_call()
    stq_req_json = stq_schedule_next_call['request'].json
    stq_queue_name = stq_schedule_next_call['queue_name']
    assert stq_req_json['task_id'] == f'bank_topup_{common.TEST_PAYMENT_ID}'
    assert stq_queue_name == 'bank_topup_core_topup'

    # assert (
    #    _mock_stq_schedule.next_call()['request'].json['queue_name']
    #    == 'bank_topup_core_topup'
    # )
    assert common.get_payment_status(pgsql) == 'PAYMENT_RECEIVED'


async def test_stq_task_payment_cleared(stq_runner, pgsql, trust_mock):
    trust_mock.set_payment_status('cleared')
    await stq_runner.bank_topup_payment_status_trust.call(
        task_id='id',
        kwargs={'payment_id': common.TEST_PAYMENT_ID},
        expect_fail=False,
    )
    assert common.get_payment_status(pgsql) == 'PAYMENT_RECEIVED'


async def test_stq_task_trust_failure(stq_runner, pgsql, trust_mock):
    await stq_runner.bank_topup_payment_status_trust.call(
        task_id='id', kwargs={'payment_id': 'unknown'}, expect_fail=True,
    )
    assert common.get_payment_status(pgsql) == 'CREATED'


async def test_stq_task_trust_network_failure(stq_runner, pgsql, mockserver):
    @mockserver.json_handler(
        '/bank-trust-payments/trust-payments/v2/payments/purchase_token',
    )
    def _foo_handler(request):
        raise mockserver.NetworkError()

    await stq_runner.bank_topup_payment_status_trust.call(
        task_id='id', kwargs={'payment_id': 'unknown'}, expect_fail=True,
    )
    assert common.get_payment_status(pgsql) == 'CREATED'


async def test_stq_task_trust_timeout(stq_runner, pgsql, mockserver):
    @mockserver.json_handler(
        '/bank-trust-payments/trust-payments/v2/payments/purchase_token',
    )
    def _foo_handler(request):
        raise mockserver.TimeoutError()

    await stq_runner.bank_topup_payment_status_trust.call(
        task_id='id', kwargs={'payment_id': 'unknown'}, expect_fail=True,
    )
    assert common.get_payment_status(pgsql) == 'CREATED'


async def test_stq_task_payment_not_authorized(
        mockserver, stq_runner, pgsql, trust_mock,
):
    @mockserver.json_handler(
        r'/stq-agent/queues/api/add/(?P<queue_name>\w+)', regex=True,
    )
    def _mock_stq_schedule(request, queue_name):
        return {}

    trust_mock.set_payment_status('not_authorized')
    await stq_runner.bank_topup_payment_status_trust.call(
        task_id='id',
        kwargs={'payment_id': common.TEST_PAYMENT_ID},
        expect_fail=False,
    )

    assert _mock_stq_schedule.times_called == 1
    assert common.get_payment_status(pgsql) == 'FAILED'


async def test_stq_task_payment_canceled(
        stq_runner, mockserver, pgsql, trust_mock,
):
    @mockserver.json_handler(
        r'/stq-agent/queues/api/add/(?P<queue_name>\w+)', regex=True,
    )
    def _mock_stq_schedule(request, queue_name):
        return {}

    trust_mock.set_payment_status('canceled')
    await stq_runner.bank_topup_payment_status_trust.call(
        task_id='id',
        kwargs={'payment_id': common.TEST_PAYMENT_ID},
        expect_fail=False,
    )

    assert _mock_stq_schedule.has_calls
    assert common.get_payment_status(pgsql) == 'REFUNDED'


@pytest.mark.parametrize('status', ['PAYMENT_RECEIVED', 'FAILED'])
async def test_stq_task_start_polling_java(
        mockserver, stq_runner, pgsql, trust_mock, status,
):
    @mockserver.json_handler(
        r'/stq-agent/queues/api/add/(?P<queue_name>\w+)', regex=True,
    )
    def _mock_stq_schedule(request, queue_name):
        return {}

    trust_mock.set_payment_status('not_authorized')
    common.set_payment_status(pgsql, status=status)
    await stq_runner.bank_topup_payment_status_trust.call(
        task_id='id',
        kwargs={'payment_id': common.TEST_PAYMENT_ID},
        expect_fail=False,
    )

    assert _mock_stq_schedule.has_calls
    assert common.get_payment_status(pgsql) == status


@pytest.mark.parametrize(
    'status', ['FAILED_SAVED', 'REFUNDED_SAVED', 'SUCCESS_SAVED'],
)
async def test_stq_wrong_status_do_nothing(
        mockserver, stq_runner, pgsql, trust_mock, status,
):
    @mockserver.json_handler(
        r'/stq-agent/queues/api/add/(?P<queue_name>\w+)', regex=True,
    )
    def _mock_stq_schedule(request, queue_name):
        return {}

    trust_mock.set_payment_status('not_authorized')
    common.set_payment_status(pgsql, status=status)
    await stq_runner.bank_topup_payment_status_trust.call(
        task_id='id',
        kwargs={'payment_id': common.TEST_PAYMENT_ID},
        expect_fail=False,
    )

    assert not _mock_stq_schedule.has_calls
    assert common.get_payment_status(pgsql) == status


@pytest.mark.parametrize(
    'status', ['SUCCESS_SAVING', 'REFUNDED_SAVING', 'FAILED_SAVING'],
)
async def test_stq_failed_on_saving_status(
        mockserver, stq_runner, pgsql, trust_mock, status,
):
    @mockserver.json_handler(
        r'/stq-agent/queues/api/add/(?P<queue_name>\w+)', regex=True,
    )
    def _mock_stq_schedule(request, queue_name):
        return {}

    trust_mock.set_payment_status('not_authorized')
    common.set_payment_status(pgsql, status=status)
    await stq_runner.bank_topup_payment_status_trust.call(
        task_id='id',
        kwargs={'payment_id': common.TEST_PAYMENT_ID},
        expect_fail=True,
    )

    assert not _mock_stq_schedule.has_calls
    assert common.get_payment_status(pgsql) == status


async def test_stq_task_payment_not_started_reschedule(
        stq_runner, pgsql, trust_mock, mockserver,
):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(request):
        return {}

    @mockserver.json_handler(
        r'/stq-agent/queues/api/add/(?P<queue_name>\w+)', regex=True,
    )
    def _mock_stq_schedule(request, queue_name):
        return {}

    trust_mock.set_payment_status('not_started')
    await stq_runner.bank_topup_payment_status_trust.call(
        task_id='id',
        kwargs={'payment_id': common.TEST_PAYMENT_ID},
        expect_fail=False,
    )
    assert common.get_payment_status(pgsql) == 'CREATED'
    assert mock_stq_reschedule.has_calls
    assert not _mock_stq_schedule.has_calls


async def test_stq_task_payment_not_started_timed_out(
        stq_runner, pgsql, trust_mock, mockserver,
):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(request):
        return {}

    @mockserver.json_handler(
        r'/stq-agent/queues/api/add/(?P<queue_name>\w+)', regex=True,
    )
    def _mock_stq_schedule(request, queue_name):
        return {}

    trust_mock.set_payment_status('not_started')
    set_created_timestamp(
        pgsql, datetime.datetime.now() - datetime.timedelta(days=1),
    )
    await stq_runner.bank_topup_payment_status_trust.call(
        task_id='id',
        kwargs={'payment_id': common.TEST_PAYMENT_ID},
        expect_fail=False,
    )
    assert common.get_payment_status(pgsql) == 'FAILED'
    assert not mock_stq_reschedule.has_calls
    assert _mock_stq_schedule.has_calls


@pytest.mark.parametrize(
    'card_number, card_bin, payment_system, last_digits',
    [
        ('423412*******1234', '423412', 'VISA', '1234'),
        ('5234*******12', '5234', 'MASTERCARD', '12'),
        ('2234*******1234', '2234', 'MIR', '1234'),
        ('8234*******123', '8234', 'UNKNOWN', '123'),
        (None, None, None, None),
        ('invalid string', None, None, None),
        ('1234*****************1234', None, None, None),
        ('**********1234', None, None, None),
    ],
)
async def test_stq_task_card_number(
        stq_runner,
        pgsql,
        trust_mock,
        card_number,
        card_bin,
        payment_system,
        last_digits,
):
    trust_mock.set_payment_status('started')
    trust_mock.set_card_number(card_number)
    await stq_runner.bank_topup_payment_status_trust.call(
        task_id='id',
        kwargs={'payment_id': common.TEST_PAYMENT_ID},
        expect_fail=False,
    )

    assert get_card_info(pgsql) == (card_bin, payment_system, last_digits)


@pytest.mark.parametrize(
    'trust_rrn,payment_rrn,result_payment_rrn',
    [
        (None, None, None),
        ('12345', None, '12345'),
        (None, '12345', '12345'),
        ('123', '321', '321'),
    ],
)
async def test_stq_task_save_rrn(
        stq_runner,
        pgsql,
        trust_mock,
        trust_rrn,
        payment_rrn,
        result_payment_rrn,
):
    trust_mock.set_payment_status('started')
    trust_mock.set_rrn(trust_rrn)
    common.set_rrn(pgsql, rrn=payment_rrn)
    await stq_runner.bank_topup_payment_status_trust.call(
        task_id='id',
        kwargs={'payment_id': common.TEST_PAYMENT_ID},
        expect_fail=False,
    )
    assert get_rrn(pgsql) == result_payment_rrn
