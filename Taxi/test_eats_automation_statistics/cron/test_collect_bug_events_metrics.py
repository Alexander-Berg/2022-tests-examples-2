# pylint: disable=redefined-outer-name, unused-variable
import pytest

from taxi.maintenance import run
from taxi.util import dates

from eats_automation_statistics.crontasks import collect_bug_events_metrics
from eats_automation_statistics.generated.cron import run_cron


@pytest.fixture
async def startrack_mock(mockserver, load_json):
    @mockserver.json_handler('/startrek/issues/_search')
    def bugs():
        return mockserver.make_response(json=load_json('st_bugs.json'))

    @mockserver.json_handler(
        '/startrek/issues/60b89ab1f3e0663aba09f5b3/changelog',
    )
    def changelog_1():
        return mockserver.make_response(json=load_json('st_changelog_1.json'))

    @mockserver.json_handler(
        '/startrek/issues/62987bbb5bff652e704e9429/changelog',
    )
    def changelog_2():
        return mockserver.make_response(json=load_json('st_changelog_2.json'))


@pytest.mark.config(
    EATS_AUTOMATION_STATISTICS_STARTRACK_FILTERS={
        'edabugreport_events': 'Queue: EDABUGREPORT AND Updated: today()',
        'edaduty_events': 'Queue: EDADUTY AND Updated: today()',
    },
)
async def test_events_stored_successfully(startrack_mock, load_json, pgsql):
    await run_cron.main(
        [
            'eats_automation_statistics.crontasks.collect_bug_events_metrics',
            '-t',
            '0',
        ],
    )
    expected = load_json('expected_events.json')
    cursor = pgsql['eats_automation_statistics'].cursor()
    cursor.execute(
        'SELECT id, bug_id, event_author, event_time::int, '
        'old_status, new_status '
        'FROM eats_automation_statistics.edabugreport_events;',
    )
    result = [list(row) for row in cursor]
    assert result == expected
    cursor.execute(
        'SELECT id, bug_id, event_author, event_time::int, '
        'old_status, new_status '
        'FROM eats_automation_statistics.edaduty_events;',
    )
    result = [list(row) for row in cursor]
    assert result == expected


@pytest.mark.config(
    EATS_AUTOMATION_STATISTICS_STARTRACK_FILTERS={
        'edabugreport_events': 'Queue: EDABUGREPORT AND Updated: today()',
        'edaduty_events': 'Queue: EDADUTY AND Updated: today()',
    },
)
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
    await collect_bug_events_metrics.do_stuff(stuff_context, loop)

    stats = get_stats_by_label_values(
        cron_context, {'sensor': 'startrack_metrics.collected_bugs'},
    )
    assert stats == [
        {
            'value': 0,
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
            'value': 9,
            'kind': 'IGAUGE',
            'timestamp': None,
            'labels': {
                'sensor': 'startrack_metrics.collected_bugs',
                'table': 'edaduty_events',
            },
        },
        {
            'value': 9,
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
