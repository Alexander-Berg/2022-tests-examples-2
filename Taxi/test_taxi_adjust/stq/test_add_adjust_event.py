import datetime
import json

import pytest

from taxi.clients import stq_agent
from taxi.stq import async_worker_ng
from taxi.util import dates

from taxi_adjust.generated.stq3 import stq_context
from taxi_adjust.stq import add_adjust_event

NOW = datetime.datetime(
    2020, 4, 17, 17, 13, 52, 792663, tzinfo=datetime.timezone.utc,
)


@pytest.fixture(name='add_adjust_event_task')
def add_adjust_event_task_fixture(
        stq3_context: stq_context.Context, mockserver, patch,
):
    async def _add_adjust_event_task_fixture(
            user_id: str = 'user',
            created_at: str = NOW.strftime('%Y-%m-%dT%H:%M:%S%z'),
    ):
        task_info = async_worker_ng.TaskInfo(
            id='some_order',
            exec_tries=0,
            reschedule_counter=0,
            queue='add_adjust_event',
        )
        await add_adjust_event.task(
            context=stq3_context,
            task_meta_info=task_info,
            user_id=user_id,
            phone_id='phone_id',
            yandex_uid='yandex_uid',
            order_id='order_id',
            created_at=created_at,
            zone='zone',
            event_type='event_type',
            revenue=5,
            currency='currency',
            application='application',
        )

    return _add_adjust_event_task_fixture


def _ok_adjust_mock(user_id='user', with_device_id=True, with_adjust_id=False):
    def mock(params):
        assert 'created_at' in params
        del params['created_at']

        expected_params = {
            'app_token': 'application_token',
            'event_token': 'event_token',
            's2s': '1',
            'revenue': '5',
            'currency': 'currency',
            'environment': 'sandbox',
            'callback_params': json.dumps(
                {
                    'order_id': 'order_id',
                    'phone_id': 'phone_id',
                    'user_id': user_id,
                    'yandex_uid': 'yandex_uid',
                    'test_adjust': 'group_id',
                },
            ),
            'partner_params': json.dumps({'test_adjust': 'group_id'}),
        }
        if with_device_id:
            expected_params[
                'android_id'
            ] = '5cef2bd4-aeb2-482a-8d6e-c38b8943aae0'

        if with_adjust_id:
            expected_params['adid'] = '763adba1737ec7e865d4ce35da88c0a2'

        assert params == expected_params
        return {'status': 'ok'}

    return mock


def _adjust_server_error_mock(params):
    return {}


@pytest.mark.now(NOW.strftime('%Y-%m-%dT%H:%M:%S%z'))
@pytest.mark.client_experiments3(
    consumer='adjust_sender',
    experiment_name='test_adjust',
    args=[{'name': 'phone_id', 'type': 'string', 'value': 'phone_id'}],
    value={'group_id': 'group_id'},
)
@pytest.mark.config(
    ADJUST_EVENT_TOKENS={
        'application': {
            'app_token': 'application_token',
            'event_type': 'event_token',
        },
    },
    ADJUST_CONFIG={'enabled': True},
)
@pytest.mark.parametrize(
    [
        'user_id',
        'adjust',
        'adjust_times_called',
        'expected_stats',
        'expected_reschedule',
        'status',
        'reason',
    ],
    [
        pytest.param(
            'user',
            _ok_adjust_mock(with_device_id=True),
            1,
            {'_id': 'requests', 'success': 1, 'not_patched': 0, 'not_sent': 0},
            0,
            'sent',
            'none',
            id='ok',
        ),
        pytest.param(
            'user2',
            None,
            0,
            {'_id': 'requests', 'success': 0, 'not_patched': 0, 'not_sent': 1},
            0,
            'not_sent',
            'not_sent_without_device_id',
            id='without_device_id_no_adjust_request',
        ),
        pytest.param(
            'user2',
            _ok_adjust_mock('user2', False, True),
            1,
            {'_id': 'requests', 'success': 1, 'not_patched': 0, 'not_sent': 0},
            0,
            'sent',
            'none',
            id='without_device_id_adjust_request',
            marks=pytest.mark.config(ADJUST_SEND_WITHOUT_DEVICE_ID=True),
        ),
        pytest.param(
            'invalid_user',
            None,
            0,
            {'_id': 'requests', 'success': 0, 'not_patched': 1, 'not_sent': 0},
            1,
            'rescheduled',
            'user_not_found',
            id='user_not_in_adjust_users',
        ),
        pytest.param(
            'user',
            _adjust_server_error_mock,
            1,
            {'_id': 'requests', 'success': 0, 'not_patched': 0, 'not_sent': 1},
            1,
            'rescheduled',
            'adjust_request_error',
            id='client_error',
        ),
        pytest.param(
            'user_no_ids',
            None,
            0,
            {'_id': 'requests', 'success': 0, 'not_patched': 0, 'not_sent': 1},
            0,
            'not_sent',
            'not_sent_without_both_ids',
            id='without_device_id_and_adjust_id',
        ),
    ],
)
async def test_add_adjust_event(
        add_adjust_event_task,
        stq3_context,
        get_stats_by_label_values,
        stq_runner,
        mongodb,
        user_id,
        adjust,
        adjust_times_called,
        expected_stats,
        expected_reschedule,
        status,
        reason,
        response_mock,
        mockserver,
):
    @mockserver.json_handler('adjust')
    def _adjust_mock(request):
        return adjust(dict(request.query))

    @mockserver.json_handler('/taxi-tariffs/v1/tariff_zones')
    def _taxi_tariffs_mock(request):
        assert request.query['locale'] == 'ru'
        return {
            'zones': [
                {
                    'name': 'zone',
                    # XXX: check tz in created_at?
                    'time_zone': 'Asia/Novosibirsk',
                    'country': 'Russia',
                },
            ],
        }

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    async def _stq_reschedule(request):
        eta = dates.utcnow() + datetime.timedelta(seconds=20)

        assert request.json == {
            'queue_name': 'add_adjust_event',
            'eta': eta.strftime(stq_agent.ETA_FORMAT),
            'task_id': 'some_order',
        }

        return {}

    await stq_runner.add_adjust_event.call(
        task_id='some_order',
        args=(),
        kwargs=dict(
            user_id=user_id,
            created_at=NOW.strftime('%Y-%m-%dT%H:%M:%S%z'),
            zone='zone',
            event_type='event_type',
            revenue=5,
            currency='currency',
            application='application',
            phone_id='phone_id',
            yandex_uid='yandex_uid',
            order_id='order_id',
        ),
    )

    assert _adjust_mock.times_called == adjust_times_called
    new_stats = mongodb.adjust_stats.find_one({'_id': 'requests'})
    assert new_stats == expected_stats
    assert _stq_reschedule.times_called == expected_reschedule

    await add_adjust_event_task(
        user_id=user_id, created_at=NOW.strftime('%Y-%m-%dT%H:%M:%S%z'),
    )
    stats = get_stats_by_label_values(
        stq3_context, {'sensor': 'taxi_adjust_stq_tasks'},
    )
    assert stats == [
        {
            'kind': 'IGAUGE',
            'labels': {
                'service_name': 'taxi',
                'application_name': 'application',
                'event_type': 'event_type',
                'status': status,
                'reason': reason,
                'sensor': 'taxi_adjust_stq_tasks',
            },
            'timestamp': None,
            'value': 1,
        },
    ]


@pytest.mark.now(NOW.strftime('%Y-%m-%dT%H:%M:%S%z'))
@pytest.mark.client_experiments3(
    consumer='adjust_sender',
    experiment_name='test_adjust',
    args=[{'name': 'phone_id', 'type': 'string', 'value': 'phone_id'}],
    value={'group_id': 'group_id'},
)
@pytest.mark.config(
    ADJUST_EVENT_TOKENS={
        'application': {
            'app_token': 'application_token',
            'event_type': 'event_token',
        },
    },
    ADJUST_CONFIG={'enabled': True},
    ADJUST_EVENT_TIMEOUT_MINUTES=10,
)
@pytest.mark.parametrize(
    ['age', 'expected_stats', 'adjust_times_called', 'status', 'reason'],
    [
        pytest.param(
            5,
            {'_id': 'requests', 'success': 1, 'not_patched': 0, 'not_sent': 0},
            1,
            'sent',
            'none',
            id='ok',
        ),
        pytest.param(
            15,
            {'_id': 'requests', 'success': 0, 'not_patched': 0, 'not_sent': 0},
            0,
            'not_sent',
            'too_old',
            id='timeout',
        ),
    ],
)
async def test_adjust_event_timeout(
        add_adjust_event_task,
        stq3_context,
        get_stats_by_label_values,
        stq_runner,
        mongodb,
        age,
        expected_stats,
        adjust_times_called,
        status,
        reason,
        response_mock,
        mockserver,
):
    @mockserver.json_handler('adjust')
    def _adjust_mock(request):
        return _ok_adjust_mock(with_device_id=True)(dict(request.query))

    @mockserver.json_handler('/taxi-tariffs/v1/tariff_zones')
    def _taxi_tariffs_mock(request):
        assert request.query['locale'] == 'ru'
        return {
            'zones': [
                {
                    'name': 'zone',
                    # XXX: check tz in created_at?
                    'time_zone': 'Asia/Novosibirsk',
                    'country': 'Russia',
                },
            ],
        }

    await stq_runner.add_adjust_event.call(
        task_id='some_order',
        args=(),
        kwargs=dict(
            user_id='user',
            created_at=(NOW - datetime.timedelta(minutes=age)).strftime(
                '%Y-%m-%dT%H:%M:%S%z',
            ),
            zone='zone',
            event_type='event_type',
            revenue=5,
            currency='currency',
            application='application',
            phone_id='phone_id',
            yandex_uid='yandex_uid',
            order_id='order_id',
        ),
    )

    assert _adjust_mock.times_called == adjust_times_called
    new_stats = mongodb.adjust_stats.find_one({'_id': 'requests'})
    assert new_stats == expected_stats

    await add_adjust_event_task(
        created_at=(NOW - datetime.timedelta(minutes=age)).strftime(
            '%Y-%m-%dT%H:%M:%S%z',
        ),
    )
    stats = get_stats_by_label_values(
        stq3_context, {'sensor': 'taxi_adjust_stq_tasks'},
    )
    assert stats == [
        {
            'kind': 'IGAUGE',
            'labels': {
                'service_name': 'taxi',
                'application_name': 'application',
                'event_type': 'event_type',
                'status': status,
                'reason': reason,
                'sensor': 'taxi_adjust_stq_tasks',
            },
            'timestamp': None,
            'value': 1,
        },
    ]
