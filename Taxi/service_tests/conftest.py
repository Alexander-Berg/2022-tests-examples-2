import datetime as dt
import os
import sys

import pandas as pd
import pytest
import psycopg2
from psycopg2.extras import RealDictCursor
import ujson

sys.path.append(os.path.join(os.path.dirname(__file__), '../'))  # noqa
sys.path.append(
    os.path.join(os.path.dirname(__file__), '../autotests_metrics'),
)  # noqa


def str_to_utc_timestamp(date: str) -> int:
    date_obj = dt.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%f%z')
    return int(date_obj.replace(tzinfo=dt.timezone.utc).timestamp())


def convert_datetime(date: str) -> int:
    date_obj = dt.datetime.strptime(date, '%Y%m%dT%H%M%S%z')
    return int(date_obj.timestamp())


@pytest.fixture(scope='session')
def pg_client():
    args = dict(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        dbname=os.getenv('POSTGRES_DBNAME'),
        cursor_factory=RealDictCursor,
    )
    with psycopg2.connect(**args) as pg_conn:
        pg_conn.autocommit = True
        yield pg_conn


@pytest.fixture(scope='function')
def teamcity_builds_data():
    with open('mocks/tc_response.json') as json_file:
        content = ujson.load(json_file)
    return content.get('build')


@pytest.fixture(scope='function')
def teamcity_mobile_builds():
    with open('mocks/mobile_builds.json') as json_file:
        return json_file.read()


@pytest.fixture(scope='function')
def teamcity_api_coverage_data():
    with open('mocks/teamcity_coverage_builds.json') as json_file:
        content = ujson.load(json_file)
    return content


@pytest.fixture(scope='function')
def teamcity_artifacts_data():
    with open('mocks/teamcity_artifacts.json') as json_file:
        content = ujson.load(json_file)
    return content


@pytest.fixture(scope='function')
def startrek_issues_data():
    with open('mocks/st_tasks.json', 'rb') as json_obj:
        return json_obj.read()


@pytest.fixture(scope='function')
def startrek_fields_data():
    with open('mocks/st_fields.json') as json_file:
        return json_file.read()


@pytest.fixture(scope='function')
def startrek_components_data():
    with open('mocks/st_components.json') as json_file:
        return json_file.read()


@pytest.fixture(scope='function')
def definition_data():
    with open('mocks/testpalm_definitions.json', 'rb') as json_obj:
        return json_obj.read()


@pytest.fixture(scope='function')
def testcases_data():
    with open('mocks/testpalm_testcases.json', 'rb') as json_obj:
        return json_obj.read()


@pytest.fixture(scope='function')
def expected_bugs_table() -> pd.DataFrame:
    with open('mocks/st_tasks.json', 'r') as json_obj:
        tasks = ujson.load(json_obj)
    result_table = []
    for task in tasks:
        result_table.append(
            {
                'created': str_to_utc_timestamp(task['createdAt']),
                'key': task['key'],
                'queue': task['queue']['key'],
                'stage': task['stage'],
                'type': task['type']['key'],
            },
        )
    table = pd.DataFrame(result_table)
    return table.sort_values('created', ignore_index=True)


@pytest.fixture(scope='function')
def expected_coverage_table() -> pd.DataFrame:
    with open('mocks/teamcity_coverage_builds.json') as json_file:
        with open('mocks/teamcity_artifacts.json') as json_obj:
            builds = ujson.load(json_file)
            artifacts = ujson.load(json_obj)
    result_table = []
    for index in range(0, len(builds)):
        build = builds[index]
        artifact_set = artifacts[index]
        result_table.append(
            {
                'build_id': build.get('id'),
                'start_date': convert_datetime((build.get('startDate'))),
                'coverage_ratio': artifact_set.get('coverage_ratio'),
                'endpoints_usage_stat_len': artifact_set.get(
                    'endpoints_usage_stat',
                ).get('_len'),
            },
        )
    return pd.DataFrame(result_table)


@pytest.fixture(scope='function')
def expected_builds_table() -> pytest.fixture:
    with open('mocks/tc_response.json') as json_file:
        builds_data = ujson.load(json_file).get('build')
    results_table = []

    for build in builds_data:
        results_table.append(
            {
                'build_number': build['number'],
                'test_count': build.get('testOccurrences', {}).get('count', 0),
                'test_failed': build.get('testOccurrences', {}).get(
                    'failed', 0,
                ),
                'agent_name': build['agent']['name'],
                'build_id': int(build['id']),
                'duration': (
                    convert_datetime(build['finishDate'])
                    - convert_datetime(build['startDate'])
                ),
                'test_duration': sum(
                    [
                        test.get('duration', 0)
                        for test in build.get('testOccurrences', {}).get(
                            'testOccurrence', [],
                        )
                    ],
                ),
                'sandbox_duration': (
                    int(build['sandbox_duration'])
                    if build.get('sandbox_duration') else None
                ),
                'finish_date': convert_datetime(build['finishDate']),
                'start_date': convert_datetime(build['startDate']),
                'status': build['status'],
                'status_text': build['statusText'],
                'branch_name': build['branchName'],
            },
        )

    def _get_expected_builds_table(number_of_builds: int):
        return pd.DataFrame(results_table[:number_of_builds]).sort_values(
            'build_id', ignore_index=True,
        )

    return _get_expected_builds_table


@pytest.fixture(scope='function')
def expected_testcase_table() -> pd.DataFrame:
    with open('mocks/testpalm_testcases.json') as json_obj:
        with open('mocks/testpalm_definitions.json') as json_file:
            testcases = ujson.load(json_obj)
            definitions = ujson.load(json_file)
            automation_status_id = next(
                (
                    entry['id']
                    for entry in definitions
                    if entry['title'] == 'Automation Status'
                ),
            )
            priority_id = next(
                (
                    entry['id']
                    for entry in definitions
                    if entry['title'] == 'Priority'
                ),
            )

    results_table = []
    for case in testcases:
        attributes = case.get('attributes')
        assert (
            attributes is not None
        ), f'Не найдены атрибуты тест кейса \'{case.get("name")}\''
        results_table.append(
            {
                'testcase_id': case['id'],
                'created_time': case['createdTime'],
                'status': case['status'],
                'is_autotest': case['isAutotest'],
                'automation_status': attributes.get(
                    automation_status_id, [None],
                )[0],
                'priority': (
                    None
                    if not len(attributes.get(priority_id))
                    else attributes.get(priority_id, [None])[0]
                ),
            },
        )
    return pd.DataFrame(results_table)


@pytest.fixture(scope='function')
def expected_mobile_builds_table() -> pd.DataFrame:
    with open('mocks/mobile_builds.json') as json_file:
        builds_data = ujson.load(json_file).get('build')

    results_table = []
    for build in builds_data:
        build_stats = build.get('statistics', {}).get('property', [])
        sandbox_duration = next(
            (
                int(item['value'])
                for item in build_stats
                if item['name'] == 'sandbox.build_duration'
            ),
            None,
        )
        results_table.append(
            {
                'build_number': build['number'],
                'test_count': build.get('testOccurrences', {}).get('count', 0),
                'test_failed': build.get('testOccurrences', {}).get(
                    'failed', 0,
                ),
                'agent_name': build['agent']['name'],
                'build_id': int(build['id']),
                'duration': (
                    convert_datetime(build['finishDate'])
                    - convert_datetime(build['startDate'])
                ),
                'test_duration': sum(
                    [
                        test.get('duration', 0)
                        for test in build.get('testOccurrences', {}).get(
                            'testOccurrence', [],
                        )
                    ],
                ),
                'sandbox_duration': sandbox_duration,
                'finish_date': convert_datetime(build['finishDate']),
                'start_date': convert_datetime(build['startDate']),
                'status': build['status'],
                'status_text': build['statusText'],
                'branch_name': build['branchName'],
            },
        )
    return pd.DataFrame(results_table[::-1])
