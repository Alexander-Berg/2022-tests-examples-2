import uuid

import pytest

from tests_bank_transfers import common
from tests_bank_transfers import db_helpers


@pytest.mark.parametrize(
    'request_id, status',
    [('aa1234', 'FAILED'), ('aa1235', 'PROCESSING'), ('aa1236', 'SUCCESS')],
)
async def test_poll_task_ok(stq_runner, stq, pgsql, request_id, status):
    transfer_id = db_helpers.insert_transfer(
        pgsql, request_id=request_id, status='PROCESSING',
    )
    await stq_runner.bank_transfers_statuses.call(
        task_id=f'poll_{transfer_id}',
        kwargs={'transfer_id': transfer_id, 'buid': common.TEST_BANK_UID},
    )
    transfer = db_helpers.select_transfer(pgsql, transfer_id)
    assert transfer.status == status
    if status == 'PROCESSING':
        assert transfer.errors is None
        next_stq_call = stq.bank_transfers_statuses.next_call()
        assert next_stq_call['queue'] == 'bank_transfers_statuses'
        assert next_stq_call['id'] == f'poll_{transfer_id}'
    if status == 'FAILED':
        assert set(transfer.errors) == {'500'}


async def test_poll_task_not_found(stq_runner):
    transfer_id = 'e493fa8c-a742-4bfb-96e7-27126d0a9a15'
    await stq_runner.bank_transfers_statuses.call(
        task_id=f'poll_{transfer_id}',
        kwargs={'transfer_id': transfer_id, 'buid': common.TEST_BANK_UID},
        expect_fail=True,
    )


@pytest.mark.parametrize('request_id', ['aa1234', 'aa1235', 'aa1236'])
async def test_poll_without_buid(stq_runner, pgsql, request_id):
    transfer_id = db_helpers.insert_transfer(
        pgsql, request_id=request_id, status='PROCESSING',
    )
    await stq_runner.bank_transfers_statuses.call(
        task_id=f'poll_{transfer_id}',
        kwargs={'transfer_id': transfer_id},
        expect_fail=True,
    )


@pytest.mark.parametrize(
    'request_id, status',
    [('aa1234', 'FAILED'), ('aa1235', 'PROCESSING'), ('aa1236', 'SUCCESS')],
)
async def test_security(stq_runner, stq, pgsql, request_id, status):
    transfer_id = db_helpers.insert_transfer(
        pgsql,
        request_id=request_id,
        status='PROCESSING',
        buid=common.TEST_BANK_UID,
    )
    await stq_runner.bank_transfers_statuses.call(
        task_id=f'poll_{transfer_id}',
        kwargs={'transfer_id': transfer_id, 'buid': str(uuid.uuid4())},
        expect_fail=True,
    )
