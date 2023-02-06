import pytest


async def test_stq(taxi_lookup, stq):
    request_body = {
        'order_id': 'some_order_id',
        'event_id': 'some_event_id',
        'reason': 'some_reason',
    }
    response = await taxi_lookup.post('order-event', json=request_body)
    assert response.status_code == 200
    assert stq['lookup_contractor'].times_called == 1


@pytest.mark.now('2021-01-01T16:30:00.00Z')
@pytest.mark.parametrize(
    'reason,order,eta',
    [
        # not delayed (soon order)
        (
            'create',
            {
                '_type': 'soon',
                'created': 1609518600,  # == now
                'request': {
                    'is_delayed': True,
                    'due': 1612197000,  # month later
                },
            },
            '2021-01-01T16:30:00+0000',
        ),
        # delayed by flag
        (
            'create',
            {
                '_type': 'later',
                'created': 1609518600,  # == now
                'request': {
                    'is_delayed': True,
                    'due': 1612197000,  # month later
                },
            },
            '2021-02-01T16:25:00+0000',
        ),
        # delayed by created - due > 15 min
        (
            'create',
            {
                '_type': 'later',
                'created': 1609518600,  # == now
                'request': {'due': 1612197000},  # month later
            },
            '2021-02-01T16:25:00+0000',
        ),
        # not delayed because created - due < 15 min
        (
            'create',
            {
                '_type': 'later',
                'created': 1612197000,  # month later
                'request': {'due': 1612197000},  # month later
            },
            '2021-02-01T16:15:00+0000',
        ),
        # not create reason
        (
            'not_create',
            {
                '_type': 'later',
                'created': 1612197000,  # month later
                'request': {'due': 1612197000},  # month later
            },
            '2021-01-01T16:30:00+0000',
        ),
        # not create reason with lookup_extra
        (
            'not_create',
            {
                '_type': 'later',
                'created': 1609518600,  # == now
                'request': {
                    'due': 1612197000,  # month later
                    'lookup_extra': {'intent': ''},
                },
            },
            '2021-01-01T16:31:00+0000',
        ),
    ],
)
@pytest.mark.config(
    LOOKUP_FORCED_PERFORMER_SETTINGS={
        '__default__': {
            'fallback_not_satisfied': False,
            'whitelisted_filters': ['infra/class', 'infra/route_info'],
            'fallback_events': [],
            'restart_delay': 60,
        },
    },
)
async def test_stq_eta(taxi_lookup, mockserver, reason, order, eta):
    @mockserver.json_handler(
        r'/stq-agent/queues/api/add/(?P<queue_name>\w+)', regex=True,
    )
    def _stq_agent_queue(request, queue_name):
        body = request.json
        assert queue_name == 'lookup_contractor'
        assert body['eta'] == eta
        assert body['kwargs']['order_id'] == 'some_order_id'
        return {}

    request_body = {
        'order_id': 'some_order_id',
        'event_id': 'some_event_id',
        'reason': reason,
        'order': {'order': order},
    }
    response = await taxi_lookup.post('order-event', json=request_body)
    assert response.status_code == 200
