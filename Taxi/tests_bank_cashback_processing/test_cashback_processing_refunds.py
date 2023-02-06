import pytest

from tests_bank_cashback_processing import common

TEST_PARENT_IDEMPOTENCY_TOKEN = 'parent_idempotency_token'
TEST_KWARGS = {'parent_idempotency_token': 'parent_idempotency_token'}
TEST_IDEMPOTENCY_TOKEN = 'idempotency_token'
TEST_IDEMPOTENCY_TOKEN_2 = 'idempotency_token_2'


def set_trust_refund_id(
        pgsql, trust_refund_id, idempotency_token=TEST_IDEMPOTENCY_TOKEN,
):
    cursor = pgsql['bank_cashback_processing'].cursor()
    cursor.execute(
        'update bank_cashback_processing.cashbacks '
        'set trust_refund_id = %s '
        'where idempotency_token = %s',
        (trust_refund_id, idempotency_token),
    )


def get_trust_refund_id(pgsql, idempotency_token=TEST_IDEMPOTENCY_TOKEN):
    cursor = pgsql['bank_cashback_processing'].cursor()
    cursor.execute(
        f'select trust_refund_id from bank_cashback_processing.cashbacks '
        f'where idempotency_token = \'{idempotency_token}\'',
    )

    return cursor.fetchall()[0][0]


async def test_no_jobs(stq_runner, pgsql, trust_mock, _stq_mock):
    common.set_payment_status(pgsql, TEST_IDEMPOTENCY_TOKEN_2, 'ERROR')
    common.set_payment_status(
        pgsql, TEST_IDEMPOTENCY_TOKEN, 'PAYMENT_RECEIVED',
    )

    await stq_runner.bank_cashback_processing_refunds.call(
        task_id='id', kwargs=TEST_KWARGS, expect_fail=False,
    )

    assert not trust_mock.create_refund_handler.has_calls
    assert not trust_mock.refund_status_handler.has_calls
    assert not trust_mock.start_refund_handler.has_calls
    assert not _stq_mock.reschedule_handle.has_calls
    assert not _stq_mock.schedule_handle.has_calls


@pytest.mark.parametrize('refund_status', [None, 'FAILED'])
async def test_create_refund_timeout(
        stq_runner, pgsql, trust_mock, _stq_mock, refund_status, mockserver,
):
    @mockserver.json_handler('/bank-trust-payments/trust-payments/v2/refunds')
    def _create_refund_handler(request):
        assert 'pass_params' not in request.json
        raise mockserver.TimeoutError()

    common.set_payment_status(pgsql, TEST_IDEMPOTENCY_TOKEN, refund_status)
    set_trust_refund_id(pgsql, 'trust_refund_id')

    await stq_runner.bank_cashback_processing_refunds.call(
        task_id='id', kwargs=TEST_KWARGS, expect_fail=True,
    )

    assert _create_refund_handler.has_calls
    assert (
        common.get_payment_status(pgsql, TEST_IDEMPOTENCY_TOKEN)
        == refund_status
    )
    assert get_trust_refund_id(pgsql) == 'trust_refund_id'
    assert not trust_mock.refund_status_handler.has_calls
    assert not trust_mock.start_refund_handler.has_calls
    assert not _stq_mock.reschedule_handle.has_calls
    assert not _stq_mock.schedule_handle.has_calls


@pytest.mark.parametrize('refund_status', [None, 'FAILED'])
async def test_create_and_start_refund(
        stq_runner, pgsql, trust_mock, _stq_mock, refund_status, mockserver,
):
    common.set_payment_status(pgsql, TEST_IDEMPOTENCY_TOKEN, refund_status)
    set_trust_refund_id(pgsql, 'trust_refund_id')

    trust_mock.set_refund_status('wait_for_notification')
    trust_mock.set_refund_id('trust_refund_id_2')

    await stq_runner.bank_cashback_processing_refunds.call(
        task_id='id', kwargs=TEST_KWARGS, expect_fail=False,
    )

    assert trust_mock.create_refund_handler.has_calls
    assert (
        common.get_payment_status(pgsql, TEST_IDEMPOTENCY_TOKEN) == 'STARTED'
    )
    assert get_trust_refund_id(pgsql) == 'trust_refund_id_2'

    assert trust_mock.start_refund_handler.has_calls
    assert _stq_mock.reschedule_handle.has_calls
    assert not trust_mock.refund_status_handler.has_calls
    assert not _stq_mock.schedule_handle.has_calls


async def test_poll_refund(stq_runner, pgsql, trust_mock, _stq_mock):
    common.set_payment_status(pgsql, TEST_IDEMPOTENCY_TOKEN, 'STARTED')
    set_trust_refund_id(pgsql, 'trust_refund_id')

    trust_mock.set_refund_status('wait_for_notification')

    await stq_runner.bank_cashback_processing_refunds.call(
        task_id='id', kwargs=TEST_KWARGS, expect_fail=False,
    )

    assert (
        common.get_payment_status(pgsql, TEST_IDEMPOTENCY_TOKEN) == 'STARTED'
    )
    assert not trust_mock.create_refund_handler.has_calls
    assert not trust_mock.start_refund_handler.has_calls
    assert get_trust_refund_id(pgsql) == 'trust_refund_id'
    assert trust_mock.refund_status_handler.has_calls
    assert _stq_mock.reschedule_handle.has_calls


@pytest.mark.parametrize(
    'trust_refund_status, db_refund_status',
    [('failed', 'FAILED'), ('error', 'ERROR')],
)
async def test_refund_failed(
        stq_runner,
        pgsql,
        trust_mock,
        _stq_mock,
        trust_refund_status,
        db_refund_status,
):
    common.set_payment_status(pgsql, TEST_IDEMPOTENCY_TOKEN, 'STARTED')
    set_trust_refund_id(pgsql, 'trust_refund_id')

    trust_mock.set_refund_status(trust_refund_status)

    await stq_runner.bank_cashback_processing_refunds.call(
        task_id='id', kwargs=TEST_KWARGS, expect_fail=True,
    )

    assert (
        common.get_payment_status(pgsql, TEST_IDEMPOTENCY_TOKEN)
        == db_refund_status
    )
    assert get_trust_refund_id(pgsql) == 'trust_refund_id'
    assert trust_mock.refund_status_handler.has_calls
    assert not _stq_mock.reschedule_handle.has_calls


async def test_refund_finished(stq_runner, pgsql, trust_mock, _stq_mock):
    common.set_payment_status(pgsql, TEST_IDEMPOTENCY_TOKEN, 'STARTED')
    set_trust_refund_id(pgsql, 'trust_refund_id')
    trust_mock.set_refund_status('success')
    await stq_runner.bank_cashback_processing_refunds.call(
        task_id='id', kwargs=TEST_KWARGS, expect_fail=False,
    )

    assert (
        common.get_payment_status(pgsql, TEST_IDEMPOTENCY_TOKEN)
        == 'PAYMENT_RECEIVED'
    )
    assert not trust_mock.create_refund_handler.has_calls
    assert trust_mock.refund_status_handler.has_calls
    assert not trust_mock.start_refund_handler.has_calls
    assert not _stq_mock.reschedule_handle.has_calls
    assert not _stq_mock.schedule_handle.has_calls


async def test_more_pending_refunds(stq_runner, pgsql, trust_mock, _stq_mock):
    common.set_payment_status(pgsql, TEST_IDEMPOTENCY_TOKEN, 'STARTED')
    set_trust_refund_id(pgsql, 'trust_refund_id')
    trust_mock.set_refund_status('success')

    cursor = pgsql['bank_cashback_processing'].cursor()
    cursor.execute(
        'update bank_cashback_processing.cashbacks '
        'set status = %s '
        'where idempotency_token = %s',
        ('FAILED', 'idempotency_token_2'),
    )

    await stq_runner.bank_cashback_processing_refunds.call(
        task_id='id', kwargs=TEST_KWARGS, expect_fail=False,
    )

    assert (
        common.get_payment_status(pgsql, TEST_IDEMPOTENCY_TOKEN)
        == 'PAYMENT_RECEIVED'
    )
    assert _stq_mock.schedule_handle.has_calls
