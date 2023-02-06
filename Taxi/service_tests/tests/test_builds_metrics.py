import functools
import os
import re
import requests
import typing

import pandas as pd
import ujson

from autotests_metrics import run_teamcity_tests_metrics

NUMBER_OF_BUILDS = 50

PG_QUERY = (
    'SELECT build_number, test_count::int, test_failed::int, '
    'agent_name, build_id::int, duration::int, test_duration::int, '
    'sandbox_duration::int, finish_date::int, start_date::int, status, '
    'status_text, branch_name FROM {table};'
)


def select_from_postgres(client, table_name):
    with client.cursor() as cursor:
        cursor.execute(PG_QUERY.format(table=table_name))
        table = cursor.fetchall()
    return pd.DataFrame(table).sort_values(
        'build_id', ignore_index=True,
    )


def test_builds_stats_stored_successfully(
        responses,
        monkeypatch,
        pg_client,
        teamcity_builds_data,
        expected_builds_table,
):
    def teamcity_cb(request: requests.Request, builds_data: typing.Sequence):
        # assert request.params['fields'] == 'build'
        headers = {}
        return (
            200,
            headers,
            ujson.dumps({'build': builds_data[:NUMBER_OF_BUILDS]}),
        )

    responses.add_callback(
        'GET',
        re.compile(
            'http://teamcity.taxi.yandex-team.ru/app/rest/builds.*?'
            'buildType%3AYandexTaxiProjects_Eda_BackendServiceCore_PullRequests_TestsTestsuite.*?',
        ),
        callback=functools.partial(
            teamcity_cb, builds_data=teamcity_builds_data,
        ),
    )

    monkeypatch.chdir('../autotests_metrics/')
    run_teamcity_tests_metrics.main()

    pg_table = os.getenv('TESTS_TASK_ID')
    pg_builds_table = select_from_postgres(pg_client, pg_table)

    pd.testing.assert_frame_equal(
        pg_builds_table, expected_builds_table(NUMBER_OF_BUILDS),
    )


def test_mobile_builds_stats_stored(
        responses,
        monkeypatch,
        pg_client,
        teamcity_mobile_builds,
        expected_mobile_builds_table,
):
    build_type = 'Mobile_Eda_Android_UI_Tests'

    def teamcity_callback(
            request: requests.Request,
            builds_data: typing.Sequence,
    ):
        headers = {}
        return 200, headers, builds_data

    responses.add_callback(
        'GET',
        re.compile(
            'http://teamcity.taxi.yandex-team.ru/app/rest/builds.*?'
            f'buildType%3A{build_type}.*?',
        ),
        callback=functools.partial(
            teamcity_callback, builds_data=teamcity_mobile_builds,
        ),
    )

    monkeypatch.chdir('../autotests_metrics/')
    monkeypatch.setenv('TESTS_TASK_ID', build_type)

    run_teamcity_tests_metrics.main()

    pg_table = os.getenv('TESTS_TASK_ID')
    pg_builds_table = select_from_postgres(pg_client, pg_table)

    pd.testing.assert_frame_equal(
        pg_builds_table, expected_mobile_builds_table,
    )
