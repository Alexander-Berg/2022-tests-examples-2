import datetime
import json

import pytest

from taxi.clients import stq_agent
from taxi.stq import async_worker_ng
from taxi.util import dates

from taxi_adjust.generated.stq3 import stq_context
from taxi_adjust.stq import grocery_adjust_events

NOW = datetime.datetime(2020, 4, 17, 17, 13, 52, 792663)

APP_NAME = 'android'
APP_TOKEN = '55ug2ntb3uzf'
EVENT_TOKEN = '71r5ks'
ORDER_ID = '2bb18ae954d84ba18e1a69dacf688fd5-grocery'
TAXI_USER_ID = 'user'
YANDEX_UID = '4046737833'
PERSONAL_PHONE_ID = '46baa0fc4e0a4d0795f50664795863b1'
PHONE_ID = '5f0460ae7c6d769bd937ea8d'
EATS_USER_ID = '176998609'
APPMETRICA_DEVICE_ID = 'CE1B0542-109A-4DB3-BF67-A321A780E8D9'
TOTAL_ORDERS_COUNT = 20
DEVICE_ID = '5cef2bd4-aeb2-482a-8d6e-c38b8943aae0'

CALLBACK_PARAMS: dict = {
    'total_orders_count': TOTAL_ORDERS_COUNT,
    'phone_id': PHONE_ID,
    'personal_phone_id': PERSONAL_PHONE_ID,
    'yandex_uid': YANDEX_UID,
    'order_id': ORDER_ID,
    'eats_user_id': EATS_USER_ID,
    'appmetrica_device_id': APPMETRICA_DEVICE_ID,
    'app_name': APP_NAME,
}


@pytest.fixture(name='grocery_adjust_events_task')
def grocery_adjust_events_fixture(
        stq3_context: stq_context.Context, mockserver, patch,
):
    async def _grocery_adjust_events_fixture(
            user_id: str = 'user',
            created_at: datetime.datetime = NOW,
            partner_params=None,
    ):
        task_info = async_worker_ng.TaskInfo(
            id='task_id',
            exec_tries=0,
            reschedule_counter=0,
            queue='grocery_adjust_events',
        )
        await grocery_adjust_events.task(
            context=stq3_context,
            task_meta_info=task_info,
            adjust_user_id=user_id,
            app_name=APP_NAME,
            app_token=APP_TOKEN,
            event_token=EVENT_TOKEN,
            created_at=created_at,
            callback_params={
                'user_id': user_id,
                'taxi_user_id': user_id,
                **CALLBACK_PARAMS,
            },
            partner_params=partner_params if partner_params else {},
        )

    return _grocery_adjust_events_fixture


def _ok_adjust_mock(
        adjust_user_id=TAXI_USER_ID,
        partner_params=None,
        upd_callback=None,
        created_at=NOW,
):
    def mock(params):
        callback_params = {
            'user_id': adjust_user_id,
            'taxi_user_id': adjust_user_id,
            **CALLBACK_PARAMS,
        }

        expected_params = {
            'created_at': created_at.replace(
                tzinfo=datetime.timezone.utc,
            ).strftime('%Y-%m-%dT%H:%M:%S%z'),
            'android_id': DEVICE_ID,
            'app_token': APP_TOKEN,
            'event_token': EVENT_TOKEN,
            's2s': '1',
            'environment': 'sandbox',
        }

        if partner_params:
            expected_params['partner_params'] = json.dumps(partner_params)

        if upd_callback:
            callback_params.update(upd_callback)

        expected_params['callback_params'] = json.dumps(callback_params)

        assert params == expected_params
        return {'status': 'ok'}

    return mock


def _adjust_server_error_mock(params):
    return {}


@pytest.mark.now(NOW.strftime('%Y-%m-%dT%H:%M:%S%z'))
@pytest.mark.config(ADJUST_RESCHEDULE_COUNTER=3)
@pytest.mark.parametrize(
    [
        'adjust_user_id',
        'partner_params',
        'adjust',
        'expected_reschedule',
        'adjust_times_called',
        'status',
        'reason',
    ],
    [
        pytest.param(
            'user', {}, _ok_adjust_mock('user'), 0, 1, 'sent', 'none', id='ok',
        ),
        pytest.param(
            'user',
            {'partner_param': 'value'},
            _ok_adjust_mock(
                'user', {'partner_param': 'value'}, {'partner_param': 'value'},
            ),
            0,
            1,
            'sent',
            'none',
            id='non_empty_partner',
        ),
        pytest.param(
            'user',
            {'partner_param': 'value', 'total_orders_count': 30},
            _ok_adjust_mock(
                'user',
                {'partner_param': 'value', 'total_orders_count': 30},
                {'partner_param': 'value'},
            ),
            0,
            1,
            'sent',
            'none',
            id='overlapping_params',
        ),
        pytest.param(
            'non_existing_user',
            {},
            _ok_adjust_mock('non_existing_user'),
            1,
            0,
            'rescheduled',
            'user_not_found',
            id='user_not_in_adjust_users',
        ),
        pytest.param(
            'user3',
            {},
            _ok_adjust_mock('user3'),
            0,
            1,
            'sent',
            'none',
            id='ok_new_format',
        ),
        pytest.param(
            'user4',
            {},
            _ok_adjust_mock('user4'),
            0,
            1,
            'sent',
            'none',
            id='ok_old_user_after_migration',
        ),
        pytest.param(
            'user5',
            {},
            _ok_adjust_mock('user5'),
            0,
            1,
            'sent',
            'none',
            id='ok_new_format_without_app',
        ),
        pytest.param(
            'user',
            {},
            _adjust_server_error_mock,
            1,
            1,
            'rescheduled',
            'adjust_request_error',
            id='client_error',
        ),
    ],
)
async def test_grocery_adjust_events(
        grocery_adjust_events_task,
        stq3_context,
        get_stats_by_label_values,
        stq_runner,
        mongodb,
        adjust_user_id,
        partner_params,
        adjust,
        expected_reschedule,
        adjust_times_called,
        status,
        reason,
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
            'queue_name': 'grocery_adjust_events',
            'eta': eta.strftime(stq_agent.ETA_FORMAT),
            'task_id': 'task_id',
        }

        return {}

    await stq_runner.grocery_adjust_events.call(
        task_id='task_id',
        args=(),
        kwargs=dict(
            adjust_user_id=adjust_user_id,
            app_name=APP_NAME,
            app_token=APP_TOKEN,
            event_token=EVENT_TOKEN,
            created_at=NOW,
            callback_params={
                'user_id': adjust_user_id,
                'taxi_user_id': adjust_user_id,
                **CALLBACK_PARAMS,
            },
            partner_params=partner_params,
        ),
    )

    assert _adjust_mock.times_called == adjust_times_called
    assert _stq_reschedule.times_called == expected_reschedule

    await grocery_adjust_events_task(
        user_id=adjust_user_id, partner_params=partner_params,
    )
    stats = get_stats_by_label_values(
        stq3_context, {'sensor': 'taxi_adjust_stq_tasks'},
    )
    assert stats == [
        {
            'kind': 'IGAUGE',
            'labels': {
                'service_name': 'lavka',
                'application_name': APP_NAME,
                'app_token': APP_TOKEN,
                'event_token': EVENT_TOKEN,
                'status': status,
                'reason': reason,
                'sensor': 'taxi_adjust_stq_tasks',
            },
            'timestamp': None,
            'value': 1,
        },
    ]


@pytest.mark.now(NOW.strftime('%Y-%m-%dT%H:%M:%S%z'))
@pytest.mark.config(
    ADJUST_CONFIG={'enabled': True}, ADJUST_EVENT_TIMEOUT_MINUTES=10,
)
@pytest.mark.parametrize(
    ['age', 'adjust_times_called', 'status', 'reason'],
    [
        pytest.param(5, 1, 'sent', 'none', id='ok'),
        pytest.param(15, 0, 'not_sent', 'too_old', id='timeout'),
    ],
)
async def test_event_timeout(
        grocery_adjust_events_task,
        stq3_context,
        get_stats_by_label_values,
        stq_runner,
        mongodb,
        age,
        adjust_times_called,
        status,
        reason,
        response_mock,
        mockserver,
):
    @mockserver.json_handler('adjust')
    def _adjust_mock(request):
        return _ok_adjust_mock(
            created_at=(NOW - datetime.timedelta(minutes=age)),
        )(dict(request.query))

    await stq_runner.grocery_adjust_events.call(
        task_id='task_id',
        args=(),
        kwargs=dict(
            adjust_user_id='user',
            app_name=APP_NAME,
            app_token=APP_TOKEN,
            event_token=EVENT_TOKEN,
            created_at=NOW - datetime.timedelta(minutes=age),
            callback_params={
                'user_id': 'user',
                'taxi_user_id': 'user',
                **CALLBACK_PARAMS,
            },
            partner_params={},
        ),
    )

    assert _adjust_mock.times_called == adjust_times_called

    await grocery_adjust_events_task(
        created_at=NOW - datetime.timedelta(minutes=age),
    )
    stats = get_stats_by_label_values(
        stq3_context, {'sensor': 'taxi_adjust_stq_tasks'},
    )
    assert stats == [
        {
            'kind': 'IGAUGE',
            'labels': {
                'service_name': 'lavka',
                'application_name': APP_NAME,
                'app_token': APP_TOKEN,
                'event_token': EVENT_TOKEN,
                'status': status,
                'reason': reason,
                'sensor': 'taxi_adjust_stq_tasks',
            },
            'timestamp': None,
            'value': 1,
        },
    ]
