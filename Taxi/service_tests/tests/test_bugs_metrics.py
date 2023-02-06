import functools
import re

import requests
import pandas as pd
from autotests_metrics import run_bugs_metrics


def test_bugs_stored_successfully(
        responses,
        monkeypatch,
        pg_client,
        startrek_issues_data,
        startrek_fields_data,
        startrek_components_data,
        expected_bugs_table,
):
    def startrek_cb(request: requests.Request, issues: bytes):
        assert (
            request.headers['Authorization'] == 'OAuth xxx-xxx'
        ), 'The script has sent the unexpected token'

        headers = {
            'Content-Language': 'ru',
            'Content-Type': 'application/json;charset=utf-8',
            'X-Total-Count': '3',
            'X-Total-Pages': '1',
        }
        return 200, headers, issues

    def startrek_fields_cb(request: requests.Request, fields_data: bytes):
        headers = {
            'Content-Language': 'ru',
            'Content-Type': 'application/json;charset=utf-8',
            'Transfer-Encoding': 'chunked',
        }
        return 200, headers, fields_data

    def startrek_components_404(request: requests.Request, components_data: bytes):
        headers = {
            'Content-Language': 'ru',
            'Content-Type': 'application/json;charset=utf-8',
            'Transfer-Encoding': 'chunked',
        }
        return 404, headers, components_data

    responses.add_callback(
        'POST',
        'https://st-api.yandex-team.ru/v2/issues/_search?scrollType=unsorted',
        callback=functools.partial(startrek_cb, issues=startrek_issues_data),
    )

    responses.add_callback(
        'GET',
        'https://st-api.yandex-team.ru/v2/fields/',
        callback=functools.partial(
            startrek_fields_cb, fields_data=startrek_fields_data,
        ),
    )

    responses.add_callback(
        'GET',
        re.compile(r'https://st-api.yandex-team.ru/v2/components/\d+'),
        callback=functools.partial(
            startrek_components_404, components_data=startrek_components_data,
        ),
    )

    monkeypatch.setenv('AUTOTEST_ROBOT_ST_TOKEN', 'xxx-xxx')
    monkeypatch.chdir('../autotests_metrics/')
    run_bugs_metrics.main()

    pg_query = (
        'SELECT created::int, key, queue, stage, type FROM bugs '
        'ORDER BY created;'
    )

    with pg_client.cursor() as cursor:
        cursor.execute(pg_query)
        table = cursor.fetchall()

    pg_bugs_table = pd.DataFrame(table)

    pd.testing.assert_frame_equal(pg_bugs_table, expected_bugs_table)
