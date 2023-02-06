import datetime
import json

import pytest

from tests_contractor_statistics_view import pg_helpers as pgh

ONLINE_EVENTS_TOPIC = (
    '/taxi/contractor-events-producer/testing/contractor-online-events'
)


def _make_logbroker_testpoint(testpoint):
    @testpoint('logbroker_commit')
    def logbroker_commit_testpoint(cookie):
        assert cookie == 'my_cookie'

    return logbroker_commit_testpoint


@pytest.mark.parametrize(
    'dpid,pid,online_status,call_stq,enabled,idx',
    [
        pytest.param(
            'dpid0', 'pid0', 'offline', False, True, 0, id='offline event',
        ),
        pytest.param(
            'dpid1',
            'pid1',
            'bad_status',
            False,
            True,
            1,
            id='unparseable event',
        ),
        pytest.param(
            'dpid0', 'pid0', 'online', True, True, 2, id='online event',
        ),
        pytest.param(
            'dpid1',
            'pid1',
            'online',
            False,
            False,
            3,
            id='config not enabled',
        ),
    ],
)
async def test_stq_task_creation(
        taxi_contractor_statistics_view,
        stq,
        testpoint,
        taxi_config,
        dpid,
        pid,
        online_status,
        call_stq,
        idx,
        enabled,
):
    taxi_config.set(
        CONTRACTOR_STATISTICS_VIEW_ONLINE_EVENTS_HANDLING_ENABLED=enabled,
    )

    online_status_timestamp = '202{}-03-20T11:22:33.44+0000'.format(idx)
    logbroker_testpoint = _make_logbroker_testpoint(testpoint)

    response = await taxi_contractor_statistics_view.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'contractor-online-events',
                'data': json.dumps(
                    {
                        'park_id': pid,
                        'driver_id': dpid,
                        'status': online_status,
                        'updated_at': online_status_timestamp,
                    },
                ),
                'topic': ONLINE_EVENTS_TOPIC,
                'cookie': 'my_cookie',
            },
        ),
    )

    assert response.status_code == 200

    await logbroker_testpoint.wait_call()

    assert (
        stq.contractor_statistics_view_handle_online_event.times_called
        == int(call_stq)
    )
    if call_stq:
        kwargs = (
            stq.contractor_statistics_view_handle_online_event.next_call()[
                'kwargs'
            ]
        )
        assert kwargs['driver_profile_id'] == dpid
        assert kwargs['park_id'] == pid
        assert kwargs[
            'last_online_time'
        ] == '202{}-03-20T11:22:33.44+00:00'.format(idx)


@pytest.mark.parametrize(
    'dpid,pid,update_last_online_time,idx',
    [
        pytest.param('bad_dpid', 'pid1', False, 0, id='bad driver_profile_id'),
        pytest.param('dpid0', 'pid0', True, 1, id='no last_online_time id db'),
        pytest.param(
            'dpid1', 'pid1', True, 2, id='there is last_online_time id db',
        ),
    ],
)
@pytest.mark.pgsql(
    'contractor_statistics_view', files=['insert_in_contractors.sql'],
)
async def test_stq_task_execution(
        stq, stq_runner, pgsql, dpid, pid, update_last_online_time, idx,
):
    online_status_timestamp = '202{}-03-20T11:22:33.44+00:00'.format(idx)

    await stq_runner.contractor_statistics_view_handle_online_event.call(
        task_id='task_id',
        args=[],
        kwargs={
            'driver_profile_id': dpid,
            'park_id': pid,
            'last_online_time': online_status_timestamp,
        },
        expect_fail=False,
    )

    query = f"""
    SELECT
        last_online_time, updated_at
    FROM contractor_statistics_view.contractors
    WHERE driver_profile_id = '{dpid}' and park_id = '{pid}';
    """

    cursor = pgsql['contractor_statistics_view'].cursor()
    cursor.execute(query)
    rows = cursor.fetchall()

    time_now = pgh.datetime_from_timestamp(
        str(datetime.datetime.now()), fmt='%Y-%m-%d %H:%M:%S.%f',
    )

    if update_last_online_time:
        assert rows[0][0] == pgh.datetime_from_timestamp(
            online_status_timestamp,
        )
        assert (time_now - rows[0][1]).total_seconds() <= 1
    else:
        assert rows == []
