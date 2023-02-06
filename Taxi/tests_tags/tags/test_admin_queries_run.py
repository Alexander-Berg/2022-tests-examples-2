# pylint: disable=W0612
import datetime
from typing import Dict

import pytest

from tests_tags.tags import tags_select
from tests_tags.tags import tags_tools

_NOW = datetime.datetime.fromisoformat('2020-11-02 12:23:00+00:00')


def _get_custom_execution_time_query(query_name: str):
    return (
        'SELECT custom_execution_time AT TIME ZONE \'UTC\' '
        'as custom_execution_time '
        f'FROM service.queries WHERE name = \'{query_name}\''
    )


def _get_query_operation_status_query(query_name: str):
    return (
        'SELECT DISTINCT ON (queries.provider_id) status FROM service.queries '
        'JOIN service.yql_operations '
        'ON queries.last_operation_id = yql_operations.operation_id '
        f'WHERE queries.name = \'{query_name}\' '
        'ORDER BY queries.provider_id, started DESC'
    )


def _get_custom_execution_time(pgsql, query_name: str):
    rows = tags_select.select_named(
        _get_custom_execution_time_query(query_name), pgsql['tags'],
    )
    assert len(rows) == 1
    return rows[0]['custom_execution_time']


def _verify_query_operation_status(pgsql, query_name: str, status: str):
    rows = tags_select.select_named(
        _get_query_operation_status_query(query_name), pgsql['tags'],
    )
    assert len(rows) == 1
    assert rows[0]['status'] == status


@pytest.mark.nofilldb()
@pytest.mark.pgsql('tags', files=['queries_run_initial.sql'])
@pytest.mark.parametrize(
    'query_name, expected_code, expected_response',
    [
        pytest.param('ordinary_query', 200, {'status': 'ok'}, id='completed'),
        pytest.param(
            'disabled_query',
            400,
            {'code': 'INVALID_ARGUMENT', 'message': 'Query is disabled'},
            id='disabled',
        ),
        pytest.param('running_query', 200, {'status': 'ok'}, id='running'),
        pytest.param(
            'missing_query',
            404,
            {'code': 'NOT_FOUND', 'message': 'Query not found'},
            id='missing_query',
        ),
        pytest.param(
            'scheduled_query', 200, {'status': 'ok'}, id='already_scheduled',
        ),
    ],
)
@pytest.mark.now(_NOW.isoformat())
async def test_query_run_once(
        taxi_tags,
        pgsql,
        query_name: str,
        expected_code: int,
        expected_response: Dict[str, str],
):
    data = {'query_name': query_name}
    response = await taxi_tags.post('v1/admin/queries/run_once', data)
    assert response.status_code == expected_code
    assert response.json() == expected_response

    if expected_code != 404:
        scheduled_time = _get_custom_execution_time(pgsql, query_name)
        if expected_code == 200:
            assert scheduled_time == _NOW
        else:
            assert scheduled_time is None


@pytest.mark.nofilldb()
@pytest.mark.pgsql('tags', files=['queries_run_initial.sql'])
@pytest.mark.config(UTAGS_YQL_WORKER_ENABLED=True)
@pytest.mark.now(_NOW.isoformat())
async def test_running_query_restart(taxi_tags, pgsql, mockserver, yt_client):
    query_name = 'running_query'
    data = {'query_name': query_name}

    response = await taxi_tags.post('v1/admin/queries/run_once', data)
    assert response.status_code == 200
    scheduled_time = _get_custom_execution_time(pgsql, query_name)
    assert scheduled_time == _NOW

    @mockserver.json_handler(
        '/yql/api/v2/operations/(?P<operation_id>\\w+)/results', regex=True,
    )
    def status_handler(request, operation_id):
        response = (
            f'{{"id": "{operation_id}", "username": "loginef", '
            '"status": "COMPLETED"}'
        )
        return mockserver.make_response(response, 200)

    # run yql-fsm to fail running operation
    await tags_tools.activate_task(taxi_tags, 'yql-fsm')
    _verify_query_operation_status(pgsql, query_name, 'failed')

    @mockserver.json_handler('/yql/api/v2/operations')
    def operation_handler(request):
        response = (
            f'{{"id": "operation_id{operation_handler.times_called}",'
            ' "username": "loginef", "status": "COMPLETED"}'
        )
        return mockserver.make_response(response, 200)

    # run yql-executer to check that operation starts
    await tags_tools.activate_task(taxi_tags, 'yql-executer')
    scheduled_time = _get_custom_execution_time(pgsql, query_name)
    assert scheduled_time is None
    _verify_query_operation_status(pgsql, query_name, 'prepared')
