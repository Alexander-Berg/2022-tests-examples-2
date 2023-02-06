import datetime
import json

import pytest

from taxi.clients import stq_agent
from taxi.stq import async_worker_ng
from taxi.util import dates

from taxi_adjust.stq import success_shuttle_order

NOW = datetime.datetime(2020, 4, 17, 17, 13, 52, 792663)

APP_NAME = 'android'
APP_TOKEN = '55ug2ntb3uzf'
SFO_EVENT_TOKEN = '71r5ks'
ORDER_EVENT_TOKEN = '71s4rs'
ORDER_ID = '2bb18ae954d84ba18e1a69dacf688fd5'
TAXI_USER_ID = 'user'
YANDEX_UID = '4046737833'
PHONE_ID = '123456789012345678901234'
DEVICE_ID = '5cef2bd4-aeb2-482a-8d6e-c38b8943aae0'


def mock_user_statistics(mockserver, order_count, counter_brand='yataxi'):
    @mockserver.json_handler('user-statistics/v1/orders')
    def _user_statistics_mock(request):
        assert request.json == {
            'identities': [
                {'type': 'phone_id', 'value': '123456789012345678901234'},
            ],
            'filters': [
                {'name': 'brand', 'values': [counter_brand]},
                {'name': 'tariff_class', 'values': ['shuttle']},
            ],
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


def _ok_adjust_mock(adjust_user_id, event_token):
    created_at = NOW

    def mock(params):
        callback_params = {
            'order_id': ORDER_ID,
            'yandex_uid': YANDEX_UID,
            'user_id': adjust_user_id,
        }

        expected_params = {
            'created_at': created_at.replace(
                tzinfo=datetime.timezone.utc,
            ).strftime('%Y-%m-%dT%H:%M:%S%z'),
            'android_id': DEVICE_ID,
            'app_token': APP_TOKEN,
            'event_token': event_token,
            's2s': '1',
            'environment': 'sandbox',
        }

        expected_params['callback_params'] = json.dumps(callback_params)

        assert params == expected_params
        return {'status': 'ok'}

    return mock


def _adjust_server_error_mock(params):
    return {}


@pytest.mark.now(NOW.strftime('%Y-%m-%dT%H:%M:%S%z'))
@pytest.mark.config(ADJUST_RESCHEDULE_COUNTER=3)
@pytest.mark.config(
    ADJUST_EVENT_TOKENS={
        'android': {
            'app_token': APP_TOKEN,
            'sfo_shuttle': SFO_EVENT_TOKEN,
            'order_shuttle': ORDER_EVENT_TOKEN,
        },
    },
)
@pytest.mark.parametrize(
    [
        'adjust_user_id',
        'adjust',
        'expected_reschedule',
        'adjust_times_called',
        'status',
        'reason',
        'order_count',
        'event_token',
    ],
    [
        pytest.param(
            'user',
            _ok_adjust_mock('user', SFO_EVENT_TOKEN),
            0,
            1,
            'sent',
            'none',
            0,
            SFO_EVENT_TOKEN,
            id='ok',
        ),
        pytest.param(
            'user',
            _ok_adjust_mock('user', ORDER_EVENT_TOKEN),
            0,
            1,
            'sent',
            'none',
            2,
            ORDER_EVENT_TOKEN,
            id='ok',
        ),
        pytest.param(
            'non_existing_user',
            _ok_adjust_mock('non_existing_user', ORDER_EVENT_TOKEN),
            1,
            0,
            'rescheduled',
            'user_not_found',
            2,
            ORDER_EVENT_TOKEN,
            id='non_existing_user',
        ),
        pytest.param(
            'user',
            _adjust_server_error_mock,
            1,
            1,
            'rescheduled',
            'adjust_request_error',
            2,
            ORDER_EVENT_TOKEN,
            id='client_error',
        ),
    ],
)
async def test_shuttle_adjust(
        stq3_context,
        get_stats_by_label_values,
        stq_runner,
        mongodb,
        adjust_user_id,
        adjust,
        expected_reschedule,
        adjust_times_called,
        status,
        reason,
        order_count,
        event_token,
        response_mock,
        mockserver,
):
    @mockserver.json_handler('adjust')
    def _adjust_mock(request):
        return adjust(dict(request.query))

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    async def _stq_reschedule(request):
        eta = dates.utcnow() + datetime.timedelta(seconds=20)

        assert request.json == {
            'queue_name': 'success_shuttle_order_adjust_events',
            'eta': eta.strftime(stq_agent.ETA_FORMAT),
            'task_id': 'task_id',
        }

        return {}

    user_statistics_mock = mock_user_statistics(mockserver, order_count)

    await stq_runner.success_shuttle_order_adjust_events.call(
        task_id='task_id',
        args=(),
        kwargs=dict(
            user_id=adjust_user_id,
            app_name=APP_NAME,
            created_at=NOW.strftime('%Y-%m-%dT%H:%M:%S%z'),
            order_id=ORDER_ID,
            yandex_uid=YANDEX_UID,
            phone_id=PHONE_ID,
        ),
    )

    assert _adjust_mock.times_called == adjust_times_called
    assert _stq_reschedule.times_called == expected_reschedule
    assert user_statistics_mock.times_called == 1

    task_info = async_worker_ng.TaskInfo(
        id='task_id',
        exec_tries=0,
        reschedule_counter=0,
        queue='success_shuttle_order_adjust_events',
    )
    await success_shuttle_order.task(
        context=stq3_context,
        task_meta_info=task_info,
        order_id=ORDER_ID,
        user_id=adjust_user_id,
        phone_id=PHONE_ID,
        yandex_uid=YANDEX_UID,
        app_name=APP_NAME,
        created_at=NOW.strftime('%Y-%m-%dT%H:%M:%S%z'),
    )
    stats = get_stats_by_label_values(
        stq3_context, {'sensor': 'taxi_adjust_stq_tasks'},
    )
    assert stats == [
        {
            'kind': 'IGAUGE',
            'labels': {
                'service_name': 'shuttle',
                'application_name': APP_NAME,
                'app_token': APP_TOKEN,
                'event_token': event_token,
                'status': status,
                'reason': reason,
                'sensor': 'taxi_adjust_stq_tasks',
            },
            'timestamp': None,
            'value': 1,
        },
    ]
