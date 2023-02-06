import functools

import pandas as pd
import pytest
import requests

from autotests_metrics import run_testpalm_metrics

PROJECT_NAME = 'TEST_PROJECT'


@pytest.fixture(scope='function')
def clean_table(pg_client):
    yield
    with pg_client.cursor() as cursor:
        cursor.execute(f'TRUNCATE TABLE {PROJECT_NAME.lower()};')


def test_testpalm_metrics_stored_successfully(
        responses,
        monkeypatch,
        pg_client,
        definition_data,
        testcases_data,
        expected_testcase_table,
        clean_table,
):
    def testpalm_definitions_cb(request: requests.Request, definitions: bytes):
        assert (
            request.headers['Authorization'] == 'OAuth xxx-yyy'
        ), 'The script has sent the unexpected token'

        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'Access-Control-Allow-Credentials': 'true',
        }

        return 200, headers, definitions

    def testpalm_testcases_cb(request: requests.Request, testcases: bytes):
        assert (
            request.headers['Authorization'] == 'OAuth xxx-yyy'
        ), 'The script has sent the unexpected token'

        headers = {'Content-Type': 'application/json; charset=utf-8'}

        return 200, headers, testcases

    responses.add_callback(
        'GET',
        f'https://testpalm-api.yandex-team.ru/definition/{PROJECT_NAME}',
        callback=functools.partial(
            testpalm_definitions_cb, definitions=definition_data,
        ),
    )

    responses.add_callback(
        'GET',
        f'https://testpalm-api.yandex-team.ru/testcases/{PROJECT_NAME}',
        callback=functools.partial(
            testpalm_testcases_cb, testcases=testcases_data,
        ),
    )

    monkeypatch.chdir('../autotests_metrics/')
    monkeypatch.setenv('TESTPALM_PROJECT_ID', PROJECT_NAME)
    monkeypatch.setenv('TESTPALM_TOKEN', 'xxx-yyy')
    run_testpalm_metrics.main()

    pg_query = (
        'SELECT testcase_id::int, created_time::bigint, status, is_autotest::Bool, '
        f'automation_status, priority FROM {PROJECT_NAME.lower()};'
    )

    with pg_client.cursor() as cursor:
        cursor.execute(pg_query)
        table = cursor.fetchall()

    pg_testcases_table = pd.DataFrame(table)

    pd.testing.assert_frame_equal(pg_testcases_table, expected_testcase_table)
