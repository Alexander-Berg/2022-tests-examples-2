# pylint: disable=C5521, W0621, W0612
import datetime
from typing import List

import pytest

from tests_tags.tags import tags_select
from tests_tags.tags import tags_tools
from tests_tags.tags import yql_services_fixture
from tests_tags.tags import yql_tools
from tests_tags.tags.yql_services_fixture import (  # noqa: F401
    local_yql_services,
)

_REFERENCE_TIME = datetime.datetime.now()
_HOUR_AFTER = _REFERENCE_TIME + datetime.timedelta(hours=1)
_HOUR_BEFORE = _REFERENCE_TIME - datetime.timedelta(hours=1)
_HUGE_DELAY = datetime.timedelta(minutes=20)
_SMALL_DELAY = datetime.timedelta(minutes=5)
_REALLY_SMALL_DELAY = datetime.timedelta(minutes=1)

_PROVIDER_ID = 1000

_NEW_OPERATION_ID_1 = f'{yql_services_fixture.DEFAULT_OPERATION_ID}_1'
_NEW_OPERATION_ID_2 = f'{yql_services_fixture.DEFAULT_OPERATION_ID}_2'

_PROVIDER_QUERY = [
    tags_tools.insert_providers(
        [tags_tools.Provider(1000, 'provider1000', '', True)],
    ),
]
_DEFAULT_QUERIES = _PROVIDER_QUERY + [
    yql_tools.insert_queries(
        [
            yql_tools.Query(
                'query1000',
                _PROVIDER_ID,
                ['tag0'],
                '2018-08-30T12:34:56.0',
                '2018-08-30T12:34:56.0',
                period=3600,  # 1 hour
            ),
        ],
    ),
]


def _verify_yql_operation_status(db, operation_id: int, status: str):
    rows = tags_select.select_table_named(
        'service.yql_operations', 'provider_id', db,
    )

    assert rows[-1]['operation_id'] == operation_id
    assert rows[-1]['status'] == status


def _get_operations(db):
    return tags_select.select_table_named(
        'service.yql_operations', 'started', db,
    )


def _get_download_task_paths(db):
    rows = tags_select.select_table_named(
        'service.yt_download_tasks', 'provider_id', db,
    )
    assert len(rows) == 1
    row = rows[0]
    return (
        row['snapshot_path'],
        row['append_path'],
        row['remove_path'],
        row['tag_names_path'],
        row['entity_types_path'],
    )


# Copied from test_yql_fsm.py
async def _operation_full_process(
        db, taxi_tags, local_yql_services, yt_client,  # noqa: F811
):
    action_times_called_before = local_yql_services.times_called['action']
    await tags_tools.activate_task(taxi_tags, 'yql-fsm')
    assert (
        local_yql_services.times_called['action']
        == action_times_called_before + 1
    )

    _verify_yql_operation_status(
        db, local_yql_services.operation_id, 'running',
    )

    (
        snapshot,
        append,
        remove,
        tag_names,
        entity_types,
    ) = _get_download_task_paths(db)

    yt_client.create_table(
        '//' + tag_names,
        recursive=True,
        attributes={'schema': [{'name': 'tag', 'type': 'string'}]},
    )
    yt_client.create_table(
        '//' + entity_types,
        recursive=True,
        attributes={'schema': [{'name': 'entity_type', 'type': 'string'}]},
    )
    yt_client.create_table(
        '//' + snapshot,
        recursive=True,
        attributes={
            'schema': [
                {'name': 'entity_value', 'type': 'string'},
                {'name': 'entity_type', 'type': 'string'},
                {'name': 'tag', 'type': 'string'},
                {'name': 'ttl', 'type': 'string'},
            ],
        },
    )
    yt_client.write_table('//' + tag_names, [], force_create=True)
    yt_client.write_table('//' + entity_types, [], force_create=True)
    yt_client.write_table('//' + snapshot, [], force_create=True)

    yql_tools.verify_yt_download_task(
        db, _PROVIDER_ID, 'description', 0, append, remove, 0,
    )

    local_yql_services.add_results_response(
        {
            'id': _NEW_OPERATION_ID_1,
            'status': 'COMPLETED',
            'data': [{'Write': [{}]}],
        },
    )
    await tags_tools.activate_task(taxi_tags, 'yql-fsm')
    yql_tools.verify_yt_download_task(
        db, _PROVIDER_ID, 'in_progress', check_status_only=True,
    )

    _verify_yql_operation_status(
        db, local_yql_services.operation_id, 'downloading',
    )

    # look at append path
    await tags_tools.activate_task(taxi_tags, 'yt-downloader')
    # look at remove path
    await tags_tools.activate_task(taxi_tags, 'yt-downloader')
    yql_tools.verify_yt_download_task(
        db, _PROVIDER_ID, 'finished', 0, None, None, 0,
    )

    await tags_tools.activate_task(taxi_tags, 'yql-fsm')
    _verify_yql_operation_status(
        db, local_yql_services.operation_id, 'completed',
    )


def _prepare_yql_for_new_operation(
        local_yql_services, operation_id,  # noqa: F811
):
    local_yql_services.set_operation_id(operation_id)
    local_yql_services.add_status_response('IDLE')
    local_yql_services.add_results_response(
        {'id': operation_id, 'status': 'IDLE'},
    )


@pytest.mark.parametrize(
    'pg_queries',
    [
        pytest.param(
            _PROVIDER_QUERY
            + [
                yql_tools.insert_queries(
                    [
                        yql_tools.Query(
                            'query1000',
                            _PROVIDER_ID,
                            ['tag0'],
                            '2018-08-30T12:34:56.0',
                            '2018-08-30T12:34:56.0',
                            custom_execution_time=_REFERENCE_TIME.isoformat(),
                            period=3600,  # 1 hour
                        ),
                    ],
                ),
            ],
            id='schedule after run_once',
        ),
        pytest.param(
            _DEFAULT_QUERIES
            + [
                yql_tools.insert_operation(
                    yql_services_fixture.DEFAULT_OPERATION_ID,
                    _PROVIDER_ID,
                    'dbid_uuid',
                    'completed',
                    _HOUR_BEFORE + _HUGE_DELAY,
                    scheduled_at=_HOUR_BEFORE,
                ),
            ],
            id='regular schedule flow',
        ),
        pytest.param(
            _DEFAULT_QUERIES
            + [
                yql_tools.insert_operation(
                    yql_services_fixture.DEFAULT_OPERATION_ID,
                    _PROVIDER_ID,
                    'dbid_uuid',
                    'completed',
                    _HOUR_BEFORE,
                    # scheduled_at is NULL
                ),
            ],
            id='scheduling flow with null in scheduled_at',
        ),
    ],
)
@pytest.mark.config(UTAGS_YQL_WORKER_ENABLED=True)
@pytest.mark.now((_REFERENCE_TIME + _SMALL_DELAY).isoformat())
async def test_scheduling_flow(
        taxi_tags,
        pg_queries: List[str],
        pgsql,
        mocked_time,
        local_yql_services,  # noqa: F811
        yt_client,
):
    db = pgsql['tags']

    tags_tools.apply_queries(db, pg_queries)

    operations = _get_operations(db)
    operations_count_before_test = len(operations)

    _prepare_yql_for_new_operation(local_yql_services, _NEW_OPERATION_ID_1)

    await taxi_tags.tests_control()
    await tags_tools.activate_task(taxi_tags, 'yql-executer')

    operations = _get_operations(db)
    assert len(operations) == operations_count_before_test + 1
    last_operation = operations[-1]
    assert last_operation['scheduled_at'] == _REFERENCE_TIME

    await _operation_full_process(db, taxi_tags, local_yql_services, yt_client)

    mocked_time.set(_HOUR_AFTER + _REALLY_SMALL_DELAY)
    await taxi_tags.tests_control()

    _prepare_yql_for_new_operation(local_yql_services, _NEW_OPERATION_ID_2)
    await tags_tools.activate_task(taxi_tags, 'yql-executer')

    operations = _get_operations(db)

    assert len(operations) == operations_count_before_test + 2
    last_operation = operations[-1]
    assert last_operation['scheduled_at'] == _HOUR_AFTER
