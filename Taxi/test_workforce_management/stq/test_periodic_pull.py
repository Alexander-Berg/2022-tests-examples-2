import datetime

import pytest
import pytz

START = datetime.datetime(2020, 7, 26, 12, 0, 0, tzinfo=pytz.UTC)


@pytest.mark.pgsql(
    'workforce_management',
    files=[
        'simple_operators.sql',
        'simple_actual_events.sql',
        'simple_shifts.sql',
    ],
)
@pytest.mark.config(
    WORKFORCE_MANAGEMENT_PHONE_QUEUE_SKILL_MAPPING={
        'shift_skills': ['pokemon'],
        'phone_queues': ['pokemon'],
    },
)
@pytest.mark.parametrize(
    '',
    [
        pytest.param(id='simple'),
        pytest.param(
            id='shift_violations',
            marks=[
                pytest.mark.config(
                    WORKFORCE_MANAGEMENT_SHIFT_VIOLATIONS_ENABLED=True,
                ),
                pytest.mark.config(
                    WORKFORCE_MANAGEMENT_ACTUAL_SHIFTS_SETTINGS={
                        'min_flap_interval_sec': 60,
                    },
                ),
                pytest.mark.now(
                    (START + datetime.timedelta(minutes=15)).isoformat(),
                ),
            ],
        ),
    ],
)
async def test_base(stq_runner, mockserver, stq):
    @mockserver.json_handler('/callcenter-stats/v1/operators/history')
    async def _(*args, **kwargs):
        return {
            'next_cursor': 2,
            'operators': [
                {
                    'id': 0,
                    'yandex_uid': 'uid1',
                    'metaqueues': ['queue'],
                    'status': 'disconnected',
                    'created_at': (
                        START - datetime.timedelta(minutes=5)
                    ).isoformat(),
                },
                {
                    'id': 0,
                    'yandex_uid': 'uid1',
                    'metaqueues': ['queue'],
                    'status': 'connected',
                    'created_at': (
                        START + datetime.timedelta(minutes=5)
                    ).isoformat(),
                },
                {
                    'id': 0,
                    'yandex_uid': 'uid1',
                    'metaqueues': ['queue'],
                    'status': 'paused',
                    'created_at': (
                        START + datetime.timedelta(minutes=10)
                    ).isoformat(),
                },
                {
                    'id': 0,
                    'yandex_uid': 'uid2',
                    'metaqueues': ['queue'],
                    'status': 'connected',
                    'created_at': START.isoformat(),
                },
                {
                    'id': 0,
                    'yandex_uid': 'missing_uid',
                    'metaqueues': ['queue'],
                    'status': 'connected',
                    'created_at': START.isoformat(),
                },
            ],
        }

    await stq_runner.workforce_management_periodic_jobs.call(
        task_id='cc_stats_puller', args=(), kwargs={},
    )

    assert stq.workforce_management_setup_jobs.next_call()['kwargs'] == {
        'triggered_events': {'uid1': {'id': 7}},
        'job_type': 'actual_shifts_creator',
    }
    assert stq.workforce_management_periodic_jobs.next_call()
