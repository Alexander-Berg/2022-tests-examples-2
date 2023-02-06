import pytest


async def run_stq(
        poster,
        task_id='task_id',
        event_type='bind',
        portal_uid='portal',
        phonish_uid='phonish',
        event_at=None,
):
    request_body = {
        'queue_name': 'uid_notify',
        'task_id': task_id,
        'args': [],
        'kwargs': {
            'event_type': event_type,
            'portal_uid': portal_uid,
            'phonish_uid': phonish_uid,
        },
    }
    if event_at:
        request_body['kwargs']['event_at'] = event_at

    return await poster.post('testsuite/stq', json=request_body)


@pytest.mark.config(
    UID_NOTIFY_CONSUMERS_CONFIG_2=[
        {
            'enabled': True,
            'events': ['bind'],
            'delivery_type': 'stq',
            'delivery_settings': {'stq': {'queue': 'plus_migration_queue'}},
        },
    ],
)
@pytest.mark.parametrize('event,called', [('bind', True), ('unbind', False)])
async def test_uid_notify_stq_call(taxi_zalogin, event, called, mockserver):
    @mockserver.json_handler(
        r'/stq-agent/queues/api/add/(?P<queue_name>\w+)', regex=True,
    )
    def _mock_agent(request, queue_name):
        return {}

    response = await run_stq(taxi_zalogin, event_type=event)
    assert response.status_code == 200
    assert response.json() == {'failed': False}

    times_called = 1 if called else 0
    assert _mock_agent.times_called == times_called


@pytest.mark.config(
    UID_NOTIFY_CONSUMERS_CONFIG_2=[
        {
            'enabled': True,
            'events': ['bind'],
            'delivery_type': 'stq',
            'delivery_settings': {'stq': {'queue': 'plus_migration_queue'}},
        },
    ],
)
@pytest.mark.now('2020-05-14 19:01:53.000000+03')
@pytest.mark.parametrize(
    'event_at, expected_event_at',
    [
        (None, '2020-05-14T16:01:53+0000'),
        ('2019-02-23 19:01:53.000000+03', '2019-02-23 19:01:53.000000+03'),
    ],
)
async def test_event_at(
        taxi_zalogin, mockserver, event_at, expected_event_at, stq,
):
    await run_stq(taxi_zalogin, event_type='bind', event_at=event_at)

    assert stq['plus_migration_queue'].times_called == 1
    assert (
        stq['plus_migration_queue'].next_call()['kwargs']['event_at']
        == expected_event_at
    )
