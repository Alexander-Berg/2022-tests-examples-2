# pylint: disable=redefined-outer-name, unused-variable
import pytest

from taxi.maintenance import run
from taxi.util import dates

from eats_automation_statistics.crontasks import collect_teamcity_metrics
from eats_automation_statistics.generated.cron import run_cron


@pytest.fixture
async def teamcity_mobile_mock(mockserver, load_json):
    @mockserver.json_handler('/teamcity/app/rest/builds')
    def builds():
        return mockserver.make_response(
            json=load_json('mobile_builds_response.json'),
        )


@pytest.fixture
async def teamcity_core_mock(mockserver, load_json):
    @mockserver.json_handler('/teamcity/app/rest/builds')
    def builds():
        return mockserver.make_response(
            json=load_json('core_builds_response.json'),
        )


@pytest.mark.config(
    TEAMCITY_BUILDS=[
        {
            'build_configuration_id': (
                'mobile_eda_android_pull_request_ui_tests'
            ),
            'tablename': 'mobile_eda_android_pull_request_ui_tests',
        },
    ],
)
async def test_mobile_builds(teamcity_mobile_mock, load_json, pgsql):
    await run_cron.main(
        [
            'eats_automation_statistics.crontasks.collect_teamcity_metrics',
            '-t',
            '0',
        ],
    )
    cursor = pgsql['eats_automation_statistics'].cursor()
    cursor.execute(
        'SELECT build_number, test_count::int, test_failed::int, '
        'agent_name, build_id::int, duration::int, test_duration::int, '
        'sandbox_duration::int, finish_date::int, start_date::int, status, '
        'status_text, branch_name FROM '
        'eats_automation_statistics.mobile_eda_android_pull_request_ui_tests '
        'ORDER BY build_number;',
    )
    expected = load_json('mobile_builds_expected.json')
    result = [list(row) for row in cursor]
    assert result == expected


@pytest.mark.config(
    TEAMCITY_BUILDS=[
        {
            'build_configuration_id': (
                'YandexTaxiProjects_Eda_'
                'BackendServiceCore_PullRequests_'
                'TestsTestsuite'
            ),
            'tablename': 'core_testsuite_builds',
        },
    ],
)
async def test_core_builds(teamcity_core_mock, load_json, pgsql):
    await run_cron.main(
        [
            'eats_automation_statistics.crontasks.collect_teamcity_metrics',
            '-t',
            '0',
        ],
    )

    cursor = pgsql['eats_automation_statistics'].cursor()
    cursor.execute(
        'SELECT build_number, test_count::int, test_failed::int, '
        'agent_name, build_id::int, duration::int, test_duration::int, '
        'sandbox_duration::int, finish_date::int, start_date::int, status, '
        'status_text, branch_name '
        'FROM eats_automation_statistics.core_testsuite_builds '
        'ORDER BY build_number;',
    )
    expected = load_json('core_builds_expected.json')
    result = [list(row) for row in cursor]
    assert result == expected


@pytest.mark.config(
    TEAMCITY_BUILDS=[
        {
            'build_configuration_id': (
                'mobile_eda_android_pull_request_ui_tests'
            ),
            'tablename': 'mobile_eda_android_pull_request_ui_tests',
        },
    ],
)
async def test_solomon_mobile_builds(
        teamcity_mobile_mock,
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
    await collect_teamcity_metrics.do_stuff(stuff_context, loop)

    stats = get_stats_by_label_values(
        cron_context, {'sensor': 'teamcity_metrics.collected_builds'},
    )
    assert stats == [
        {
            'value': 10,
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
            'value': 0,
            'kind': 'IGAUGE',
            'timestamp': None,
            'labels': {
                'sensor': 'teamcity_metrics.collected_builds',
                'table': 'coverage_core_testsuite_builds',
            },
        },
    ]


@pytest.mark.config(
    TEAMCITY_BUILDS=[
        {
            'build_configuration_id': (
                'YandexTaxiProjects_Eda_'
                'BackendServiceCore_PullRequests_'
                'TestsTestsuite'
            ),
            'tablename': 'core_testsuite_builds',
        },
    ],
)
async def test_solomon_core_builds(
        teamcity_core_mock,
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
    await collect_teamcity_metrics.do_stuff(stuff_context, loop)

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
            'value': 10,
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
            'value': 0,
            'kind': 'IGAUGE',
            'timestamp': None,
            'labels': {
                'sensor': 'teamcity_metrics.collected_builds',
                'table': 'coverage_core_testsuite_builds',
            },
        },
    ]
