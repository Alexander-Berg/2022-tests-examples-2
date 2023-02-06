import datetime

import pytest

from taxi.clients import stq_agent
from taxi.stq import async_worker_ng
from taxi.util import dates

from taxi_adjust.generated.stq3 import stq_context
from taxi_adjust.stq import rida_adjust_events


NOW = datetime.datetime(2020, 2, 26, 13, 50, tzinfo=datetime.timezone.utc)

APPLICATION = 'rida_android'
APP_TOKEN = '1234567890abc'
USER_GUID = 'some_user_guid'
EVENT_TOKEN = 'order_complete'
OFFER_GUID = 'some_offer_guid'


@pytest.fixture(name='rida_adjust_events_task')
def rida_adjust_events_fixture(stq3_context: stq_context.Context):
    async def _rida_adjust_events_fixture(
            reschedule_counter: int = 0, user_guid: str = USER_GUID,
    ):
        task_info = async_worker_ng.TaskInfo(
            id='task_id',
            exec_tries=0,
            reschedule_counter=reschedule_counter,
            queue='rida_adjust_events',
        )
        await rida_adjust_events.task(
            context=stq3_context,
            task_meta_info=task_info,
            application=APPLICATION,
            app_token=APP_TOKEN,
            user_guid=user_guid,
            event_token=EVENT_TOKEN,
            created_at=NOW,
            offer_guid=OFFER_GUID,
        )

    return _rida_adjust_events_fixture


@pytest.fixture(name='check_stq_metric')
def check_stq_metric_fixture(stq3_context, get_stats_by_label_values):
    def _check_stq_metric(
            expected_status: str, expected_reason: str = 'none',
    ) -> None:
        stats = get_stats_by_label_values(
            stq3_context, {'sensor': 'taxi_adjust_stq_tasks'},
        )
        assert stats == [
            {
                'kind': 'IGAUGE',
                'labels': {
                    'service_name': 'rida',
                    'application_name': APPLICATION,
                    'app_token': APP_TOKEN,
                    'event_token': EVENT_TOKEN,
                    'status': expected_status,
                    'reason': expected_reason,
                    'sensor': 'taxi_adjust_stq_tasks',
                },
                'timestamp': None,
                'value': 1,
            },
        ]

    return _check_stq_metric


@pytest.mark.now(NOW.isoformat())
async def test_rida_adjust_events(
        mockserver, rida_adjust_events_task, check_stq_metric,
):
    @mockserver.json_handler('adjust')
    def _adjust_mock(request):
        params = dict(request.query)
        expected_params = {
            'app_token': APP_TOKEN,
            'callback_params': '{}',
            'created_at': NOW.strftime('%Y-%m-%dT%H:%M:%S%z'),
            'environment': 'sandbox',
            'event_token': EVENT_TOKEN,
            'iphone_id': '5cef2bd4-aeb2-482a-8d6e-c38b8943aae0',
            's2s': '1',
        }
        assert params == expected_params
        return {'status': 'ok'}

    await rida_adjust_events_task()
    check_stq_metric(expected_status='sent')


@pytest.mark.config(ADJUST_EVENT_TIMEOUT_MINUTES=10)
@pytest.mark.now((NOW + datetime.timedelta(minutes=11)).isoformat())
async def test_metric_too_old(rida_adjust_events_task, check_stq_metric):
    await rida_adjust_events_task()
    check_stq_metric(expected_status='not_sent', expected_reason='too_old')


@pytest.mark.config(ADJUST_RESCHEDULE_COUNTER=2)
@pytest.mark.parametrize(
    ['current_reschedule_count', 'expected_is_rescheduled'],
    [
        pytest.param(0, True, id='no_reschedules_yet'),
        pytest.param(1, True, id='reschedules_below_config_value'),
        pytest.param(2, False, id='reschedules_match_config_value'),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_user_not_found(
        mockserver,
        rida_adjust_events_task,
        check_stq_metric,
        current_reschedule_count: int,
        expected_is_rescheduled: bool,
):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    async def _stq_reschedule(request):
        eta = dates.utcnow() + datetime.timedelta(seconds=20)
        assert request.json == {
            'queue_name': 'rida_adjust_events',
            'eta': eta.strftime(stq_agent.ETA_FORMAT),
            'task_id': 'task_id',
        }
        return {}

    await rida_adjust_events_task(
        reschedule_counter=current_reschedule_count, user_guid='nonexistent',
    )
    if expected_is_rescheduled:
        assert _stq_reschedule.times_called == 1
        check_stq_metric(
            expected_status='rescheduled', expected_reason='user_not_found',
        )
    else:
        assert _stq_reschedule.times_called == 0
        check_stq_metric(
            expected_status='not_sent', expected_reason='user_not_found',
        )


@pytest.mark.now(NOW.isoformat())
async def test_adjust_error(
        mockserver, rida_adjust_events_task, check_stq_metric,
):
    @mockserver.json_handler('adjust')
    def _adjust_mock(request):
        params = dict(request.query)
        expected_params = {
            'app_token': APP_TOKEN,
            'callback_params': '{}',
            'created_at': NOW.strftime('%Y-%m-%dT%H:%M:%S%z'),
            'environment': 'sandbox',
            'event_token': EVENT_TOKEN,
            'iphone_id': '5cef2bd4-aeb2-482a-8d6e-c38b8943aae0',
            's2s': '1',
        }
        assert params == expected_params
        return {'error': 'device not found'}

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    async def _stq_reschedule(request):
        eta = dates.utcnow() + datetime.timedelta(seconds=20)
        assert request.json == {
            'queue_name': 'rida_adjust_events',
            'eta': eta.strftime(stq_agent.ETA_FORMAT),
            'task_id': 'task_id',
        }
        return {}

    await rida_adjust_events_task()
    assert _stq_reschedule.times_called == 1
    check_stq_metric(
        expected_status='rescheduled', expected_reason='invalid_data',
    )


@pytest.mark.now(NOW.isoformat())
async def test_adjust_unique_event_error(
        mockserver, rida_adjust_events_task, check_stq_metric,
):
    @mockserver.json_handler('adjust')
    def _adjust_mock(request):
        return {
            'error': (
                'Event request failed (Ignoring event, '
                'earlier unique event tracked)'
            ),
        }

    await rida_adjust_events_task()
    check_stq_metric(expected_status='sent')
