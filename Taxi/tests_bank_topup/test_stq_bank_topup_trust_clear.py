import pytest

from tests_bank_topup import common


async def test_clear_queued(mockserver, stq_runner, pgsql, trust_mock):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def _mock_stq_reschedule(request):
        return {}

    common.set_payment_status(pgsql, status='SUCCESS_SAVED')

    await stq_runner.bank_topup_trust_clear.call(
        task_id='id',
        kwargs={'payment_id': common.TEST_PAYMENT_ID},
        expect_fail=False,
    )

    assert trust_mock.clear_handler.has_calls

    assert common.get_payment_status(pgsql) == 'CLEARING'
    assert _mock_stq_reschedule.has_calls


async def test_clear_completed(mockserver, stq_runner, pgsql, trust_mock):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def _mock_stq_reschedule(request):
        return {}

    common.set_payment_status(pgsql, status='CLEARING')
    trust_mock.set_payment_status('cleared')

    await stq_runner.bank_topup_trust_clear.call(
        task_id='id',
        kwargs={'payment_id': common.TEST_PAYMENT_ID},
        expect_fail=False,
    )

    assert not _mock_stq_reschedule.has_calls
    assert common.get_payment_status(pgsql) == 'CLEARED'


@pytest.mark.now('2019-01-01T12:00:00+0000')
async def test_clear_not_completed(mockserver, stq_runner, pgsql, trust_mock):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def _mock_stq_reschedule(request):
        assert request.json['eta'] == '2019-01-01T12:04:00+0000'
        return {}

    common.set_payment_status(pgsql, status='CLEARING')
    trust_mock.set_payment_status('authorized')

    await stq_runner.bank_topup_trust_clear.call(
        task_id='id',
        kwargs={'payment_id': common.TEST_PAYMENT_ID},
        reschedule_counter=2,
        expect_fail=False,
    )

    assert _mock_stq_reschedule.has_calls
    assert common.get_payment_status(pgsql) == 'CLEARING'


@pytest.mark.config(BANK_TOPUP_TRUST_CLEAR_MAX_RESCHEDULES=3)
async def test_reschedule_counter_limit(stq_runner, pgsql, trust_mock):
    common.set_payment_status(pgsql, status='CLEARING')
    trust_mock.set_payment_status('authorized')

    await stq_runner.bank_topup_trust_clear.call(
        task_id='id',
        kwargs={'payment_id': common.TEST_PAYMENT_ID},
        reschedule_counter=4,
        expect_fail=True,
    )

    assert common.get_payment_status(pgsql) == 'CLEARING'


@pytest.mark.now('2019-01-01T12:00:00+0000')
@pytest.mark.config(BANK_TOPUP_TRUST_CLEAR_MAX_RESCHEDULES=100)
@pytest.mark.config(BANK_TOPUP_TRUST_CLEAR_MAX_POLLING_INTERVAL=60)
async def test_clear_exp_backoff_max_delay(
        mockserver, stq_runner, pgsql, trust_mock,
):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def _mock_stq_reschedule(request):
        assert request.json['eta'] == '2019-01-01T13:00:00+0000'
        return {}

    common.set_payment_status(pgsql, status='CLEARING')
    trust_mock.set_payment_status('authorized')

    await stq_runner.bank_topup_trust_clear.call(
        task_id='id',
        kwargs={'payment_id': common.TEST_PAYMENT_ID},
        reschedule_counter=100,
        expect_fail=False,
    )

    assert _mock_stq_reschedule.has_calls
    assert common.get_payment_status(pgsql) == 'CLEARING'
