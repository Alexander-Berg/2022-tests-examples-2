import pytest


JOB_NAME = 'cargo-claims-callback-broker'


def get_config(enabled):
    config = {'enabled': enabled, 'chunk_size': 1000, 'sleep_time_ms': 100}
    return config


@pytest.mark.config(CARGO_CLAIMS_CALLBACK_BROKER_WORKMODE=get_config(True))
async def test_worker_empty(run_task_once):
    stats = await run_task_once(JOB_NAME)
    assert stats == {'processed-count': 0, 'limit-reached': 0}


@pytest.mark.config(CARGO_CLAIMS_CALLBACK_BROKER_WORKMODE=get_config(True))
async def test_worker_not_empty(
        stq, pgsql, create_default_claim, run_task_once,
):
    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        f"""
        INSERT INTO cargo_claims.claim_callback(
                    claim_uuid, status, callback_url, updated_ts)
        VALUES ('123', 'new', 'foobar', '2020-01-01 11:59:50+0000'),
               ('123', 'estimating', 'foobar', '2020-01-01 11:59:50+0000');
    """,
    )
    stats = await run_task_once(JOB_NAME)

    assert stats['processed-count'] == 2

    queue = stq.cargo_claims_callback_notify
    assert queue.times_called == 2
    stq_calls = [queue.next_call() for _ in range(queue.times_called)]
    stq_calls = {call['id']: call['kwargs'] for call in stq_calls}
    for kwargs in stq_calls.values():
        kwargs.pop('log_extra')

    assert stq_calls == {
        '123_new_callback_notify': {
            'callback_url': 'foobar',
            'claim_id': '123',
            'updated_ts': {'$date': '2020-01-01T11:59:50.000Z'},
        },
        '123_estimating_callback_notify': {
            'callback_url': 'foobar',
            'claim_id': '123',
            'updated_ts': {'$date': '2020-01-01T11:59:50.000Z'},
        },
    }
