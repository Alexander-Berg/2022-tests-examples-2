import functools
import re
import typing

import requests
import pandas as pd
import ujson

from autotests_metrics import run_coverage_metrics


def test_coverage_stored_successfully(
        responses,
        monkeypatch,
        pg_client,
        teamcity_api_coverage_data,
        teamcity_artifacts_data,
        expected_coverage_table,
):
    def teamcity_api_coverage_cb(
            request: requests.Request, builds: typing.Sequence,
    ):
        headers = {}
        return 200, headers, ujson.dumps({'build': builds})

    def teamcity_artifacts_cb(
            request: requests.Request, artifact_data: typing.Dict,
    ):
        headers = {}
        return 200, headers, ujson.dumps(artifact_data)

    responses.add_callback(
        'GET',
        re.compile(
            'http://teamcity.taxi.yandex-team.ru/app/rest/builds.*?'
            'buildType%3AYandexTaxiProjects_Eda_BackendServiceCore_Internal_APICoverage.*?',
        ),
        callback=functools.partial(
            teamcity_api_coverage_cb, builds=teamcity_api_coverage_data,
        ),
    )

    for artifacts in teamcity_artifacts_data:
        responses.add_callback(
            'GET',
            re.compile(
                'http://teamcity.taxi.yandex-team.ru/app/rest/builds/'
                'id:\d+/artifacts/files//report.json/report.json',
            ),
            callback=functools.partial(
                teamcity_artifacts_cb, artifact_data=artifacts,
            ),
        )

    monkeypatch.chdir('../autotests_metrics/')
    run_coverage_metrics.main()

    pg_query = (
        'SELECT build_id::int, start_date::int , coverage_ratio::float, '
        'endpoints_usage_stat_len::int FROM  coverage_core_testsuite_builds;'
    )

    ydb_query = (
        'SELECT build_id, start_date, coverage_ratio, '
        'endpoints_usage_stat_len FROM  coverage_core_testsuite_builds;'
    )

    with pg_client.cursor() as cursor:
        cursor.execute(pg_query)
        table = cursor.fetchall()

    pg_coverage_table = pd.DataFrame(table)
    pd.testing.assert_frame_equal(pg_coverage_table, expected_coverage_table)
