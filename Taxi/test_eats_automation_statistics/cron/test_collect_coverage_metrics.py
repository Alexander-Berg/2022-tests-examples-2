# pylint: disable=redefined-outer-name, unused-variable
import pytest

from taxi.maintenance import run
from taxi.util import dates

from eats_automation_statistics.crontasks import collect_coverage_metrics
from eats_automation_statistics.generated.cron import run_cron


@pytest.fixture
async def coverage_mock(mockserver, load_json):
    @mockserver.json_handler('/teamcity/app/rest/builds')
    def builds():
        return mockserver.make_response(
            json=load_json('coverage_response.json'),
        )

    @mockserver.json_handler(
        '/teamcity/repository/download/YandexTaxiProjects_Eda_'
        'BackendServiceCore_Internal_APICoverage'
        '/7857761:id/report.json/report.json',
    )
    def artifacts200():
        return mockserver.make_response(
            json=load_json('coverage_artifact_response.json'),
        )

    @mockserver.json_handler(
        '/teamcity/repository/download/YandexTaxiProjects_Eda_'
        'BackendServiceCore_Internal_APICoverage'
        '/7859818:id/report.json/report.json',
    )
    def artifacts404():
        return mockserver.make_response(status=404)


async def test_coverage_builds(coverage_mock, load_json, pgsql):
    await run_cron.main(
        [
            'eats_automation_statistics.crontasks.collect_coverage_metrics',
            '-t',
            '0',
        ],
    )
    cursor = pgsql['eats_automation_statistics'].cursor()
    cursor.execute(
        'SELECT build_id, start_date, '
        'coverage_ratio, endpoints_usage_stat_len FROM '
        'eats_automation_statistics.coverage_core_testsuite_builds '
        'ORDER BY build_id;',
    )
    expected = load_json('coverage_expected.json')
    result = [list(row) for row in cursor]
    assert result == expected


async def test_solomon(
        coverage_mock, loop, cron_context, get_stats_by_label_values,
):
    stuff_context = run.StuffContext(
        lock=None,
        task_id='some-id',
        start_time=dates.utcnow(),
        data=cron_context,
    )

    await collect_coverage_metrics.do_stuff(stuff_context, loop)

    stats = get_stats_by_label_values(
        cron_context, {'sensor': 'teamcity_metrics.collected_builds'},
    )
    assert stats == [
        {
            'value': 0,
            'kind': 'IGAUGE',
            'timestamp': None,
            'labels': {
                'sensor': 'teamcity_metrics.collected_builds',
                'table': 'mobile_eda_android_pull_request_ui_tests',
            },
        },
        {
            'value': 0,
            'kind': 'IGAUGE',
            'timestamp': None,
            'labels': {
                'sensor': 'teamcity_metrics.collected_builds',
                'table': 'mobile_eda_android_ui_tests',
            },
        },
        {
            'value': 0,
            'kind': 'IGAUGE',
            'timestamp': None,
            'labels': {
                'sensor': 'teamcity_metrics.collected_builds',
                'table': 'core_testsuite_builds',
            },
        },
        {
            'value': 0,
            'kind': 'IGAUGE',
            'timestamp': None,
            'labels': {
                'sensor': 'teamcity_metrics.collected_builds',
                'table': 'ios_tests_builds',
            },
        },
        {
            'value': 1,
            'kind': 'IGAUGE',
            'timestamp': None,
            'labels': {
                'sensor': 'teamcity_metrics.collected_builds',
                'table': 'coverage_core_testsuite_builds',
            },
        },
    ]
