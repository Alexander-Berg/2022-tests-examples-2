# pylint: disable=redefined-outer-name, unused-variable
import datetime

import pytest

from taxi.maintenance import run
from taxi.util import dates

from eats_automation_statistics.crontasks import collect_bug_history_metrics
from eats_automation_statistics.generated.cron import run_cron


@pytest.fixture
async def startrack_mock(mockserver, load_json):
    @mockserver.json_handler('/startrek/issues/_search')
    def bugs():
        return mockserver.make_response(json=load_json('st_open_bugs.json'))


async def test_bugs_stored_successfully(startrack_mock, load_json, pgsql):
    await run_cron.main(
        [
            'eats_automation_statistics.crontasks.collect_bug_history_metrics',
            '-t',
            '0',
        ],
    )
    cursor = pgsql['eats_automation_statistics'].cursor()
    cursor.execute(
        'SELECT id, key, snapshot_time::int, '
        'status, status_changed::int, weight::int, priority, '
        'created_at::int, queue, stage, '
        'type, stream, components, tags, summary '
        'FROM eats_automation_statistics.eats_bug_history '
        'WHERE id=\'6266d0c59082c901649b6bb9\';',
    )
    result = [list(row) for row in cursor]
    snapshot_time = (
        datetime.datetime.today()
        .replace(hour=0, minute=0, second=0, microsecond=0)
        .timestamp()
    )
    assert result == [
        [
            '6266d0c59082c901649b6bb9',
            'EDAFRONT-10005',
            snapshot_time,
            'open',
            1650905442,
            None,
            'normal',
            1650905284,
            'EDAFRONT',
            'Production',
            'bug',
            'Рост',
            ['iOSClient'],
            None,
            '[iOS] Некорректно отображается '
            'картинка без текста в бейдже акции',
        ],
    ]
    cursor.execute(
        'SELECT count(*) ' 'FROM eats_automation_statistics.eats_bug_history;',
    )
    assert cursor.fetchone()[0] == 4


async def test_solomon(
        startrack_mock,
        loop,
        cron_context,
        get_stats_by_label_values,
        load_json,
):

    stuff_context = run.StuffContext(
        lock=None,
        task_id='some-id',
        start_time=dates.utcnow(),
        data=cron_context,
    )
    await collect_bug_history_metrics.do_stuff(stuff_context, loop)

    stats = get_stats_by_label_values(
        cron_context, {'sensor': 'startrack_metrics.collected_bugs'},
    )
    assert stats == [
        {
            'value': 4,
            'kind': 'IGAUGE',
            'timestamp': None,
            'labels': {
                'sensor': 'startrack_metrics.collected_bugs',
                'table': 'eats_bug_history',
            },
        },
        {
            'value': 0,
            'kind': 'IGAUGE',
            'timestamp': None,
            'labels': {
                'sensor': 'startrack_metrics.collected_bugs',
                'table': 'eats_bugs',
            },
        },
        {
            'value': 0,
            'kind': 'IGAUGE',
            'timestamp': None,
            'labels': {
                'sensor': 'startrack_metrics.collected_bugs',
                'table': 'edaduty_events',
            },
        },
        {
            'value': 0,
            'kind': 'IGAUGE',
            'timestamp': None,
            'labels': {
                'sensor': 'startrack_metrics.collected_bugs',
                'table': 'edabugreport_events',
            },
        },
        {
            'value': 0,
            'kind': 'IGAUGE',
            'timestamp': None,
            'labels': {
                'sensor': 'startrack_metrics.collected_bugs',
                'table': 'eats_bugs_sla',
            },
        },
    ]
