# pylint: disable=redefined-outer-name, unused-variable
import pytest

from taxi.maintenance import run
from taxi.util import dates

from eats_automation_statistics.crontasks import collect_testpalm_metrics
from eats_automation_statistics.generated.cron import run_cron


@pytest.fixture
async def testpalm_mock(mockserver, load_json):
    @mockserver.json_handler('/testpalm/definition/ios-client')
    def definitions():
        return mockserver.make_response(
            json=load_json('testpalm_definitions.json'),
        )

    @mockserver.json_handler('/testpalm/testcases/ios-client')
    def testcases():
        return mockserver.make_response(
            json=load_json('testpalm_testcases.json'),
        )


@pytest.mark.config(TESTPALM_PROJECTS=['ios-client'])
async def test_testpalm_metrics(testpalm_mock, load_json, pgsql):

    await run_cron.main(
        [
            'eats_automation_statistics.crontasks.collect_testpalm_metrics',
            '-t',
            '0',
        ],
    )
    cursor = pgsql['eats_automation_statistics'].cursor()
    cursor.execute(
        'SELECT testcase_id, created_time, status, '
        'is_autotest, automation_status, priority, case_group FROM '
        'eats_automation_statistics.iosclient '
        'ORDER BY created_time;',
    )
    expected = load_json('testpalm_expected.json')
    result = [list(row) for row in cursor]
    assert result == expected


@pytest.mark.config(TESTPALM_PROJECTS=['ios-client'])
async def test_solomon(
        testpalm_mock,
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
    await collect_testpalm_metrics.do_stuff(stuff_context, loop)

    stats = get_stats_by_label_values(
        cron_context, {'sensor': 'testpalm_metrics.collected_testcases'},
    )
    assert stats == [
        {
            'value': 0,
            'kind': 'IGAUGE',
            'timestamp': None,
            'labels': {
                'sensor': 'testpalm_metrics.collected_testcases',
                'table': 'newtests',
            },
        },
        {
            'value': 10,
            'kind': 'IGAUGE',
            'timestamp': None,
            'labels': {
                'sensor': 'testpalm_metrics.collected_testcases',
                'table': 'iosclient',
            },
        },
    ]
