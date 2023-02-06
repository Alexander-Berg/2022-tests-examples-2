import pytest

from tests_bank_topup import common


@pytest.mark.parametrize('basket_status', ['refunded', 'canceled'])
async def test_stq_task_basket_already_refunded(
        mockserver, stq_runner, pgsql, trust_mock, basket_status,
):
    @mockserver.json_handler(
        r'/stq-agent/queues/api/add/(?P<queue_name>\w+)', regex=True,
    )
    def _mock_stq_schedule(request, queue_name):
        return {}

    common.set_payment_status(pgsql, status='REFUNDING')

    trust_mock.set_payment_status(basket_status)
    await stq_runner.bank_topup_trust_refund.call(
        task_id='id',
        kwargs={'payment_id': common.TEST_PAYMENT_ID},
        expect_fail=False,
    )

    assert trust_mock.basket_info_handler.has_calls

    assert common.get_payment_status(pgsql) == 'REFUNDED'
    assert _mock_stq_schedule.has_calls
    assert (
        _mock_stq_schedule.next_call()['request'].json['task_id']
        == f'bank_topup_{common.TEST_PAYMENT_ID}'
    )


async def test_stq_task_unhold(mockserver, stq_runner, pgsql, trust_mock):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def _mock_stq_reschedule(request):
        return {}

    common.set_payment_status(pgsql, status='REFUNDING')

    trust_mock.set_payment_status('authorized')
    await stq_runner.bank_topup_trust_refund.call(
        task_id='id',
        kwargs={'payment_id': common.TEST_PAYMENT_ID},
        expect_fail=False,
    )

    assert trust_mock.unhold_handler.has_calls

    assert common.get_payment_status(pgsql) == 'REFUNDING'
    assert _mock_stq_reschedule.has_calls


async def test_stq_task_bad_basket_status(
        mockserver, stq_runner, pgsql, trust_mock,
):
    common.set_payment_status(pgsql, status='REFUNDING')

    await stq_runner.bank_topup_trust_refund.call(
        task_id='id',
        kwargs={'payment_id': common.TEST_PAYMENT_ID},
        expect_fail=True,
    )

    assert trust_mock.basket_info_handler.has_calls

    assert common.get_payment_status(pgsql) == 'REFUNDING'
