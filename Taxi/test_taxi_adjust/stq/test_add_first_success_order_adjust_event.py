import datetime

import bson
import pytest

from taxi.clients import stq_agent

NOW = datetime.datetime(2020, 4, 17, 17, 13, 52, tzinfo=datetime.timezone.utc)
DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S%z'


def get_default_task_kwargs(created_at, application='app', user_agent=None):
    default_task_kwargs = dict(
        phone_id=bson.ObjectId('123456789012345678901234'),
        user_id='user_id',
        yandex_uid='yandex_uid',
        order_id='order_id',
        zone='zone',
        cost=5.0,
        currency='currency',
        application=application,
        created_at=created_at.strftime(DATETIME_FORMAT),
    )

    if user_agent is not None:
        default_task_kwargs['user_agent'] = user_agent

    return default_task_kwargs


def mock_user_statistics(mockserver, order_count, counter_brand='yataxi'):
    @mockserver.json_handler('user-statistics/v1/orders')
    def _user_statistics_mock(request):
        assert request.json == {
            'identities': [
                {'type': 'phone_id', 'value': '123456789012345678901234'},
            ],
            'filters': [{'name': 'brand', 'values': [counter_brand]}],
            'group_by': [],
        }

        counters = [
            {
                'counted_from': '2019-05-17T12:47:45+0000',
                'counted_to': NOW.strftime('%Y-%m-%dT%H:%M:%S%z'),
                'properties': [{'name': 'brand', 'value': counter_brand}],
                'value': order_count,
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

    return _user_statistics_mock


def mock_stq_reschedule(mockserver, created_at):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    async def _stq_reschedule(request):
        eta = created_at + datetime.timedelta(minutes=5)

        assert request.json == {
            'queue_name': 'add_first_success_order_adjust_event',
            'eta': eta.strftime(stq_agent.ETA_FORMAT),
            'task_id': 'user',
        }

        return {}

    return _stq_reschedule


def mock_add_event_queue(mockserver, created_at, application='app'):
    @mockserver.json_handler('/stq-agent/queues/api/add/add_adjust_event')
    def _queue(request):
        assert request.json['args'] == []
        expected_kwargs = dict(
            event_type='success_first_order',
            phone_id='123456789012345678901234',
            user_id='user_id',
            yandex_uid='yandex_uid',
            order_id='order_id',
            zone='zone',
            application=application,
            revenue=5,
            currency='currency',
            created_at=created_at.strftime('%Y-%m-%dT%H:%M:%S%z'),
        )
        assert request.json['kwargs'] == expected_kwargs
        assert request.json['task_id'] == 'user_id'

    return _queue


@pytest.mark.now(NOW.strftime('%Y-%m-%dT%H:%M:%S%z'))
@pytest.mark.config(
    ADJUST_APPLICATIONS=['app'], ADJUST_CONFIG={'__default__': True},
)
@pytest.mark.parametrize(
    ['event_age', 'expected_reschedule'],
    [
        pytest.param(2, True, id='rescheduling'),
        pytest.param(6, False, id='not_rescheduling'),
    ],
)
async def test_add_first_success_order_adjust_event(
        stq_runner, mockserver, event_age, expected_reschedule,
):
    created_at = NOW - datetime.timedelta(minutes=event_age)

    user_statistics_mock = mock_user_statistics(mockserver, 0)
    stq_reschedule_mock = mock_stq_reschedule(mockserver, created_at)
    add_event_queue_mock = mock_add_event_queue(mockserver, created_at)

    await stq_runner.add_first_success_order_adjust_event.call(
        task_id='user',
        args=(),
        kwargs=get_default_task_kwargs(created_at=created_at),
    )

    if expected_reschedule:
        assert add_event_queue_mock.times_called == 0
        assert user_statistics_mock.times_called == 0
        assert stq_reschedule_mock.times_called == 1
    else:
        assert add_event_queue_mock.times_called == 1
        assert user_statistics_mock.times_called == 1
        assert stq_reschedule_mock.times_called == 0


@pytest.mark.now(NOW.strftime('%Y-%m-%dT%H:%M:%S%z'))
@pytest.mark.config(
    ADJUST_APPLICATIONS=['app'], ADJUST_CONFIG={'__default__': True},
)
@pytest.mark.parametrize(
    'order_count, expected_to_add_event',
    [
        pytest.param(0, True, id='No orders'),
        pytest.param(1, True, id='One order'),
        pytest.param(2, False, id='Two orders'),
        pytest.param(9001, False, id='A lot of orders'),
    ],
)
async def test_has_orders(
        stq_runner, mockserver, order_count, expected_to_add_event,
):
    event_age = 6
    created_at = NOW - datetime.timedelta(minutes=event_age)

    user_statistics_mock = mock_user_statistics(mockserver, order_count)
    stq_reschedule_mock = mock_stq_reschedule(mockserver, created_at)
    add_event_queue_mock = mock_add_event_queue(mockserver, created_at)

    await stq_runner.add_first_success_order_adjust_event.call(
        task_id='user',
        args=(),
        kwargs=get_default_task_kwargs(created_at=created_at),
    )

    assert user_statistics_mock.times_called == 1
    assert stq_reschedule_mock.times_called == 0
    assert add_event_queue_mock.times_called == (
        1 if expected_to_add_event else 0
    )


@pytest.mark.now(NOW.strftime('%Y-%m-%dT%H:%M:%S%z'))
@pytest.mark.config(
    ADJUST_APPLICATIONS=['android'], ADJUST_CONFIG={'__default__': True},
)
async def test_cargo_app(stq_runner, mockserver):
    event_age = 6
    created_at = NOW - datetime.timedelta(minutes=event_age)
    user_agent = 'yandex-taxi/4.91.0.88955 Android/11 (Xiaomi; Mi A3)'

    user_statistics_mock = mock_user_statistics(mockserver, 1)
    stq_reschedule_mock = mock_stq_reschedule(mockserver, created_at)
    add_event_queue_mock = mock_add_event_queue(
        mockserver, created_at, application='android',
    )

    await stq_runner.add_first_success_order_adjust_event.call(
        task_id='user',
        args=(),
        kwargs=get_default_task_kwargs(
            created_at=created_at, application='cargo', user_agent=user_agent,
        ),
    )

    assert user_statistics_mock.times_called == 1
    assert stq_reschedule_mock.times_called == 0
    assert add_event_queue_mock.times_called == 1
