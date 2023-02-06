import datetime as dt
import json

import pytest

from tests_driver_mode_subscription import mode_rules

# sha256sum mydbid_myuuiddifferent_profile_usage
_SHA256_TASK_ID = (
    'c223c3100dba5b01a54656973187883c31e9264696411ea1a369597b77420416'
)

_ONLINE_EVENTS_TOPIC = (
    '/taxi/contractor-events-producer/testing/contractor-online-events'
)


def _make_logbroker_testpoint(testpoint):
    @testpoint('logbroker_commit')
    def logbroker_commit_testpoint(cookie):
        assert cookie == 'my_cookie'

    return logbroker_commit_testpoint


def _make_raw_event(dbid: str, uuid: str, status: str, timestamp: str):
    event = {
        'park_id': dbid,
        'driver_id': uuid,
        'status': status,
        'updated_at': timestamp,
    }

    return json.dumps(event)


@pytest.mark.now('2021-02-01T05:00:00+00:00')
@pytest.mark.mode_rules(
    rules=mode_rules.patched([mode_rules.Patch(rule_name='prev_work_mode')]),
)
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_ONLINE_EVENTS_CONSUMER_SETTINGS={
        'unsubscribe_on_different_profile_online': True,
        'max_pipeline_size': 1000,
        'outdate_interval_min': 1440,
        'processing_retry_interval_ms': 100,
    },
)
@pytest.mark.parametrize(
    'online_status, online_status_timestamp, expect_sync_call',
    [
        pytest.param(
            'online', '2021-01-31T23:59:59.0+00:00', True, id='online event',
        ),
        pytest.param(
            'bad_status',
            '2021-01-31T23:59:59.0+00:00',
            False,
            id='unparseable event',
        ),
        pytest.param(
            'offline',
            '2021-01-31T23:59:59.0+00:00',
            False,
            id='offline event',
        ),
        pytest.param(
            'online',
            '2021-01-29T23:59:59.0+00:00',
            False,
            id='outdated event',
        ),
        pytest.param(
            'online',
            '2021-01-31T23:59:59.0+00:00',
            False,
            id='unsubscribe disabled',
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_ONLINE_EVENTS_CONSUMER_SETTINGS={
                        'unsubscribe_on_different_profile_online': False,
                        'max_pipeline_size': 1000,
                        'outdate_interval_min': 1440,
                        'processing_retry_interval_ms': 100,
                    },
                ),
            ],
        ),
    ],
)
async def test_start_subscription_sync(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mocked_time,
        stq,
        testpoint,
        online_status: str,
        online_status_timestamp: str,
        expect_sync_call: bool,
):
    logbroker_testpoint = _make_logbroker_testpoint(testpoint)

    response = await taxi_driver_mode_subscription.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'contractor-online-events-consumer',
                'data': _make_raw_event(
                    'mydbid', 'myuuid', online_status, online_status_timestamp,
                ),
                'topic': _ONLINE_EVENTS_TOPIC,
                'cookie': 'my_cookie',
            },
        ),
    )

    assert response.status_code == 200

    await logbroker_testpoint.wait_call()

    if expect_sync_call:
        assert stq.subscription_sync.times_called == 1

        stq_data = stq.subscription_sync.next_call()
        assert stq_data['queue'] == 'subscription_sync'
        assert stq_data['id'] == _SHA256_TASK_ID
        assert stq_data['eta'] == dt.datetime(2021, 2, 1, 5, 0)

        stq_kwargs = stq_data['kwargs']
        del stq_kwargs['log_extra']
        assert stq_kwargs == {
            'park_driver_id': 'mydbid_myuuid',
            'unsubscribe_reason': 'different_profile_usage',
        }
    else:
        assert stq.subscription_sync.times_called == 0
