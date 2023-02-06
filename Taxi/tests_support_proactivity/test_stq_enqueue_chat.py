import datetime

import pytest

SECOND = datetime.timedelta(seconds=1)


@pytest.mark.config(
    SUPPORT_PROACTIVITY_SETTINGS={
        'create_chat_delay': 10,
        'create_chat_ttl': 20,
        'percentage': 0,
        'short_ride_max_travel_time': 300,
    },
)
@pytest.mark.servicetest
async def test_enqueue_chat(stq_runner, stq):
    now = datetime.datetime.utcnow()
    expected_eta = now + datetime.timedelta(seconds=10)
    expected_expires_at = now + datetime.timedelta(seconds=20)
    await stq_runner.support_proactivity_enqueue_chat.call(
        task_id='some_task_id', kwargs={'order_id': 'some_order_id'},
    )
    assert stq.support_proactivity_create_chat.times_called == 1
    create_chat_call = stq.support_proactivity_create_chat.next_call()
    eta = create_chat_call.pop('eta')
    expires_at = datetime.datetime.strptime(
        create_chat_call['kwargs'].pop('expires_at'), '%Y-%m-%dT%H:%M:%SZ',
    )
    create_chat_call['kwargs'].pop('log_extra')
    assert create_chat_call == {
        'queue': 'support_proactivity_create_chat',
        'id': 'some_task_id',
        'args': [],
        'kwargs': {'order_id': 'some_order_id'},
    }
    assert eta - expected_eta < SECOND
    assert expires_at - expected_expires_at < SECOND
