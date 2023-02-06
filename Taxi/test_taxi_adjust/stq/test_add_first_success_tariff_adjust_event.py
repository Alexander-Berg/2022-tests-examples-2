import datetime

from aiohttp import web
import bson
import pytest

from taxi.clients import stq_agent

NOW = datetime.datetime(2020, 4, 17, 17, 13, 52, tzinfo=datetime.timezone.utc)
SERVER_ERROR_RESPONSE = web.json_response(status=500)
EMPTY_DATA_RESPONSE: dict = {'data': []}
TASK_KWARGS = {
    'user_id': 'user_id',
    'phone_id': bson.ObjectId('123456789012345678901234'),
    'yandex_uid': 'yandex_uid',
    'order_id': 'order_id',
    'application': 'app',
    'tariff': 'econom',
    'zone': 'zone',
    'cost': 5.0,
    'currency': 'currency',
}


@pytest.fixture(name='stq_agent_queue_mock')
def _stq_agent_queue_mock(mockserver):
    def _mock(created_at):
        @mockserver.json_handler('/stq-agent/queues/api/add/add_adjust_event')
        def _queue(request):
            assert request.json['args'] == []
            expected_kwargs = dict(
                application='app',
                created_at=created_at.strftime('%Y-%m-%dT%H:%M:%S%z'),
                currency='currency',
                event_type='success_first_econom_order',
                revenue=5,
                user_id='user_id',
                phone_id='123456789012345678901234',
                yandex_uid='yandex_uid',
                order_id='order_id',
                zone='zone',
            )
            assert request.json['kwargs'] == expected_kwargs
            assert request.json['task_id'] == 'user_id_econom'

        return _queue

    return _mock


@pytest.mark.now(NOW.strftime('%Y-%m-%dT%H:%M:%S%z'))
@pytest.mark.config(
    ADJUST_APPLICATIONS=['app'], ADJUST_CONFIG={'__default__': True},
)
@pytest.mark.parametrize(
    [
        'event_age',
        'expected_reschedule',
        'completed_orders',
        'queue_times_called',
    ],
    [
        pytest.param(2, True, 0, 0, id='rescheduling'),
        pytest.param(6, False, 0, 1, id='no_completed_orders'),
        pytest.param(6, False, 1, 1, id='one_completed_order'),
        pytest.param(6, False, 5, 0, id='not_sent'),
    ],
)
async def test_ok(
        stq_runner,
        mockserver,
        stq_agent_queue_mock,
        event_age,
        expected_reschedule,
        completed_orders,
        queue_times_called,
):
    created_at = NOW - datetime.timedelta(minutes=event_age)

    @mockserver.json_handler('user-statistics/v1/orders')
    def _user_statistics_mock(request):
        assert request.json == {
            'identities': [
                {'type': 'phone_id', 'value': '123456789012345678901234'},
            ],
            'filters': [
                {'name': 'brand', 'values': ['yataxi']},
                {'name': 'tariff_class', 'values': ['econom']},
            ],
            'group_by': [],
        }

        if not completed_orders:
            counters = []
        else:
            counters = [
                {
                    'counted_from': '2019-05-17T12:47:45+0000',
                    'counted_to': NOW.strftime('%Y-%m-%dT%H:%M:%S%z'),
                    'properties': [
                        {'name': 'brand', 'value': 'yataxi'},
                        {'name': 'tariff_class', 'value': 'econom'},
                    ],
                    'value': completed_orders,
                },
            ]

        return {
            'data': [
                {
                    'counters': counters,
                    'identity': {
                        'type': 'phone_id',
                        'value': '123456789012345678901234',
                    },
                },
            ],
        }

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    async def _stq_reschedule(request):
        eta = created_at + datetime.timedelta(minutes=5)

        assert request.json == {
            'queue_name': 'add_first_success_tariff_adjust_event',
            'eta': eta.strftime(stq_agent.ETA_FORMAT),
            'task_id': 'user_tariff',
        }

        return {}

    mock_stq_agent_queue = stq_agent_queue_mock(created_at)

    await stq_runner.add_first_success_tariff_adjust_event.call(
        task_id='user_tariff',
        args=(),
        kwargs=dict(
            **TASK_KWARGS,
            created_at=created_at.strftime('%Y-%m-%dT%H:%M:%S%z'),
        ),
    )

    if expected_reschedule:
        assert _user_statistics_mock.times_called == 0
        assert _stq_reschedule.times_called == 1
    else:
        assert _user_statistics_mock.times_called == 1
        assert _stq_reschedule.times_called == 0

    assert mock_stq_agent_queue.times_called == queue_times_called


@pytest.mark.now(NOW.strftime('%Y-%m-%dT%H:%M:%S%z'))
@pytest.mark.config(
    ADJUST_APPLICATIONS=['app'], ADJUST_CONFIG={'__default__': True},
)
@pytest.mark.parametrize(
    ['user_statistics_response'],
    [
        pytest.param(SERVER_ERROR_RESPONSE, id='server_error'),
        pytest.param(EMPTY_DATA_RESPONSE, id='empty_data'),
    ],
)
async def test_task_fails(
        stq_runner, mockserver, stq_agent_queue_mock, user_statistics_response,
):
    created_at = NOW - datetime.timedelta(minutes=6)

    @mockserver.json_handler('user-statistics/v1/orders')
    def _user_statistics_mock(request):
        return user_statistics_response

    mock_stq_agent_queue = stq_agent_queue_mock(created_at)

    with pytest.raises(Exception):
        await stq_runner.add_first_success_tariff_adjust_event.call(
            task_id='user_tariff',
            args=(),
            kwargs=dict(
                **TASK_KWARGS,
                created_at=created_at.strftime('%Y-%m-%dT%H:%M:%S%z'),
            ),
        )

    assert _user_statistics_mock.times_called == 1
    assert mock_stq_agent_queue.times_called == 0


@pytest.mark.now(NOW.strftime('%Y-%m-%dT%H:%M:%S%z'))
@pytest.mark.config(
    ADJUST_APPLICATIONS=['app'], ADJUST_CONFIG={'__default__': True},
)
async def test_client_error(stq_runner, mockserver, stq_agent_queue_mock):
    created_at = NOW - datetime.timedelta(minutes=6)

    @mockserver.json_handler('user-statistics/v1/orders')
    def _user_statistics_mock(request):
        return {}

    mock_stq_agent_queue = stq_agent_queue_mock(created_at)

    await stq_runner.add_first_success_tariff_adjust_event.call(
        task_id='user_tariff',
        args=(),
        kwargs=dict(
            **TASK_KWARGS,
            created_at=created_at.strftime('%Y-%m-%dT%H:%M:%S%z'),
        ),
    )

    assert _user_statistics_mock.times_called == 1
    assert mock_stq_agent_queue.times_called == 1


@pytest.mark.now(NOW.strftime('%Y-%m-%dT%H:%M:%S%z'))
@pytest.mark.config(
    ADJUST_APPLICATIONS=['app'], ADJUST_CONFIG={'__default__': True},
)
async def test_too_many_requests_error(stq_runner, mockserver):
    created_at = NOW - datetime.timedelta(minutes=6)

    @mockserver.json_handler('user-statistics/v1/orders')
    def _user_statistics_mock(request):
        return web.json_response(status=429)

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    async def _stq_reschedule(request):
        eta = NOW + datetime.timedelta(seconds=20)

        assert request.json == {
            'queue_name': 'add_first_success_tariff_adjust_event',
            'eta': eta.strftime(stq_agent.ETA_FORMAT),
            'task_id': 'user_tariff',
        }

        return {}

    await stq_runner.add_first_success_tariff_adjust_event.call(
        task_id='user_tariff',
        args=(),
        kwargs=dict(
            **TASK_KWARGS,
            created_at=created_at.strftime('%Y-%m-%dT%H:%M:%S%z'),
        ),
    )

    assert _user_statistics_mock.times_called == 1
    assert _stq_reschedule.times_called == 1
