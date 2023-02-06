import copy
import datetime
import json
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import pytest

from tests_tags.tags import tags_select
from tests_tags.tags import tags_tools
from tests_tags.tags import yql_tools

_NOW = datetime.datetime(2077, 1, 18, 10, 54, 9)
_HOUR_AGO = _NOW - datetime.timedelta(hours=1)
_PROVIDER = 'provider0'

_OLD_SNAPSHOT_PATH = 'some/old/path/0/old_snapshot'
_NOW_PATH = yql_tools.gen_snapshot_path(_PROVIDER)
_APPEND_PATH = yql_tools.gen_append_path(_PROVIDER)
_REMOVE_PATH = yql_tools.gen_remove_path(_PROVIDER)
_TAG_NAMES_PATH = yql_tools.gen_tag_names_path(_PROVIDER)
_ENTITY_TYPES_PATH = yql_tools.gen_entity_types_path(_PROVIDER)
_TMP_PATH = yql_tools.gen_tmp_path(_PROVIDER)

_COMMENT_GENERATED = '-- THIS CODE WAS GENERATED BY TAGS SERVICE\n'
_COMMENT_SECTION = '--------------------------------------------------------\n'

_BASIC_QUERY = (
    'DIFFICULT SELECTS FROM [_LAST_RUN_RESULT_] AND JOINS [_INSERT_HERE_] '
    'SELECT "tag", "dbid_uuid" FROM [_LAST_RUN_RESULT_];'
)

_QUERY = yql_tools.Query(
    'query0',
    0,
    ['tag0'],
    '2018-08-30T12:34:56.0',
    '2018-08-30T12:34:56.0',
    _BASIC_QUERY,
    yql_processing_method='yt_merge',
)


def _get_basic_yql_transformed_query(
        entity_type: Optional[str], last_snapshot_path: Optional[str],
) -> str:
    return yql_tools.gen_transformed_yql_query(
        user_query=_BASIC_QUERY,
        provider=_PROVIDER,
        entity_type=entity_type,
        last_snapshot_path=last_snapshot_path,
    )


def _get_yql_merge_query(
        entity_type: Optional[str], last_snapshot_path: str,
) -> str:
    return yql_tools.gen_yql_merge_query(
        provider=_PROVIDER, last_snapshot_path=last_snapshot_path,
    )


def _string_to_path(path: str, truncate: bool) -> str:
    if truncate:
        return f'"<append=false>//{path}"'
    return f'"//{path}"'


def _get_basic_chyt_transformed_query(
        snapshot_path: str, tag_names_path: str, last_snapshot_path: str,
):
    return (
        'DIFFICULT SELECTS FROM '
        + last_snapshot_path
        + ' AND JOINS '
        + '\n'
        + '\n'
        + _COMMENT_SECTION
        + _COMMENT_GENERATED
        + ' INSERT INTO '
        + _string_to_path(snapshot_path, True)
        + '\n'
        + _COMMENT_SECTION
        + '\n\n'
        + ' SELECT "tag", "dbid_uuid" FROM '
        + last_snapshot_path
        + ';\n\n\n'
        + _COMMENT_SECTION
        + _COMMENT_GENERATED
        + ';\n\n\n'
        'INSERT INTO '
        + _string_to_path(tag_names_path, True)
        + ' SELECT DISTINCT tag FROM '
        + _string_to_path(snapshot_path, False)
        + ';\n'
    )


def _get_chyt_transformed_query(
        entity_type: Optional[str],
        last_snapshot_path: Optional[str],
        clique: str = 'robot-tags-alias',
):
    assert entity_type and last_snapshot_path
    return (
        _COMMENT_GENERATED + f'use chyt.hahn/{clique};\n'
        'PRAGMA yql.DisableParallelExecution = true;\n'
        + _create_table(_TMP_PATH, False)
        + '\n'
        + _create_table(_NOW_PATH, True)
        + '\n'
        + _create_table(_TAG_NAMES_PATH, False, None)
        + '\n'
        + _COMMENT_SECTION
        + '\n'
        + '\n'
        # modified query
        + _get_basic_chyt_transformed_query(
            _TMP_PATH,
            _TAG_NAMES_PATH,
            _string_to_path(last_snapshot_path, False),
        )
        # sort _tmp_path into snapshot path
        + 'INSERT INTO '
        + _string_to_path(_NOW_PATH, True)
        + ' SELECT tag, dbid_uuid FROM '
        + _string_to_path(_TMP_PATH, False)
        + ' ORDER BY (tag, dbid_uuid);\n'
        # clear tmp path
        + 'DROP TABLE ' + _string_to_path(_TMP_PATH, False) + ';\n'
        # create append
        + _create_table(_APPEND_PATH, False) + '\n'
        # create remove
        + _create_table(_REMOVE_PATH, False) + '\n'
        # join to fill remove
        + 'INSERT INTO '
        + _string_to_path(_REMOVE_PATH, True)
        + ' SELECT a.tag, a.dbid_uuid FROM '
        # 0-th snapshot, 0 is added in _insert_previous_results
        + _string_to_path(_OLD_SNAPSHOT_PATH + '0', False)
        + ' a LEFT JOIN '
        + _string_to_path(_NOW_PATH, False)
        + ' b ON a.tag = b.tag AND a.dbid_uuid = b.dbid_uuid'
        + ' WHERE b.tag = \'\';\n'
        # join to fill append
        + 'INSERT INTO '
        + _string_to_path(_APPEND_PATH, True)
        + ' SELECT a.tag, a.dbid_uuid FROM '
        + _string_to_path(_NOW_PATH, False)
        + ' a LEFT JOIN '
        + _string_to_path(_OLD_SNAPSHOT_PATH + '0', False)
        + ' b ON a.tag = b.tag AND a.dbid_uuid = b.dbid_uuid'
        + ' WHERE b.tag = \'\';\n'
    )


def _get_chyt_builder(clique: str):
    def builder(entity_type, last_snapshot_path):
        clique_name = clique
        return _get_chyt_transformed_query(
            entity_type, last_snapshot_path, clique_name,
        )

    return builder


def _verify_queries_entry(db, provider_id):
    rows = tags_select.select_table_named('service.queries', 'provider_id', db)
    assert len(rows) == 1
    row = rows[0]
    assert row['provider_id'] == provider_id
    assert row['yql_processing_method'] == 'yt_merge'


def _verify_yql_operation(
        db_row,
        operation_id: str,
        provider_id: int,
        entity_type: Optional[str],
        status: str,
        started: datetime.datetime,
        failure_description: Optional[str],
        failure_type: Optional[str],
        retry_number: Optional[int],
):
    assert db_row['operation_id'] == operation_id
    assert db_row['provider_id'] == provider_id
    assert db_row['entity_type'] == entity_type
    assert db_row['status'] == status
    assert db_row['started'] == started
    assert db_row['failure_description'] == failure_description
    assert db_row['failure_type'] == failure_type
    assert db_row['retry_number'] == retry_number


def _verify_yql_operations(db, operations):
    rows = tags_select.select_table_named(
        'service.yql_operations', 'operation_id', db,
    )
    assert len(rows) == len(operations)
    for index, row in enumerate(rows):
        _verify_yql_operation(row, **operations[index])


def _verify_yt_download_task(
        db,
        provider_id: int,
        snapshot_path: str,
        append_path: str,
        remove_path: Optional[str],
        tag_names_path: str,
        entity_types_path: Optional[str],
):
    rows = tags_select.select_table_named(
        'service.yt_download_tasks', 'provider_id', db,
    )
    assert len(rows) == 1
    row = rows[0]
    assert row['provider_id'] == provider_id
    assert yql_tools.remove_uuid(row['snapshot_path']) == snapshot_path
    assert yql_tools.remove_uuid(row['append_path']) == append_path
    assert yql_tools.remove_uuid(row['remove_path']) == remove_path
    assert yql_tools.remove_uuid(row['tag_names_path']) == tag_names_path
    assert yql_tools.remove_uuid(row['entity_types_path']) == entity_types_path
    assert row['current_row'] == 0
    assert row['status'] == 'description'


def _insert_previous_results(
        db,
        previous_results: List[str],
        provider_id,
        query_syntax: str,
        entity_type: Optional[str],
):
    cursor = db.cursor()
    for i, previous_result in enumerate(previous_results):
        cursor.execute(
            yql_tools.insert_snapshot(
                yql_tools.YtSnapshot(
                    provider_id,
                    _OLD_SNAPSHOT_PATH + str(i),
                    _NOW - datetime.timedelta(minutes=i + 1),
                    previous_result,
                    query_syntax=query_syntax,
                    entity_type=entity_type,
                ),
            ),
        )


def _create_table(
        path: str, ordered: bool, entity_type: Optional[str] = 'dbid_uuid',
) -> str:
    columns_schema = 'tag String'
    order_by = 'tag'
    if entity_type is not None:
        columns_schema += f', {entity_type} String'
        order_by += f', {entity_type}'
    ans = (
        f'CREATE TABLE IF NOT EXISTS {_string_to_path(path, False)}'
        f'({columns_schema}) ENGINE = YtTable()'
    )

    if ordered:
        ans += f' ORDER BY ({order_by})'
    return ans + ';'


@pytest.mark.config(UTAGS_YQL_WORKER_ENABLED=True)
@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_providers(
            [tags_tools.Provider(0, 'provider0', '', True)],
        ),
    ],
)
@pytest.mark.parametrize('use_dynamic_entity_types', [False, True])
@pytest.mark.parametrize(
    'previous_execution_results, query_builders,'
    'full_update_expected, query_syntax',
    [
        ([], [_get_basic_yql_transformed_query], True, 'SQLv1'),
        (['description'], [_get_basic_yql_transformed_query], True, 'SQLv1'),
        (
            ['description', 'outdated'],
            [_get_basic_yql_transformed_query],
            True,
            'SQLv1',
        ),
        (
            ['description', 'description', 'fully_applied', 'description'],
            [_get_basic_yql_transformed_query, _get_yql_merge_query],
            False,
            'SQLv1',
        ),
        pytest.param(
            ['fully_applied'],
            # create tables
            [_get_chyt_builder(clique='robot-tags-alias')],
            False,
            'CLICKHOUSE',
        ),
        pytest.param(
            ['fully_applied'],
            # create tables
            [_get_chyt_builder(clique='robot-tags-custom-alias')],
            False,
            'CLICKHOUSE',
            marks=[
                pytest.mark.config(
                    UTAGS_CLIQUE_NAME={
                        '__default__': {
                            '__default__': 'robot-tags-default-alias',
                            '__yql_executer': 'robot-tags-custom-alias',
                            '__yql_experimental': (
                                'robot-tags-experimental-alias'
                            ),
                        },
                    },
                ),
            ],
        ),
        pytest.param(
            ['fully_applied'],
            # create tables
            [_get_chyt_builder(clique='robot-tags-alias')],
            False,
            'CLICKHOUSE',
            marks=[
                pytest.mark.config(
                    UTAGS_CLIQUE_NAME={
                        '__default__': {
                            '__default__': 'robot-tags-default-alias',
                            '__yql_executer': 'robot-tags-alias',
                            '__yql_experimental': (
                                'robot-tags-experimental-alias'
                            ),
                        },
                    },
                    TAGS_EXPERIMENTAL_CLIQUE_SETTINGS={
                        'is_enabled': False,
                        'queries': [_QUERY.name],
                    },
                ),
            ],
        ),
        pytest.param(
            ['fully_applied'],
            # create tables
            [_get_chyt_builder(clique='robot-tags-alias')],
            False,
            'CLICKHOUSE',
            marks=[
                pytest.mark.config(
                    UTAGS_CLIQUE_NAME={
                        '__default__': {
                            '__default__': 'robot-tags-default-alias',
                            '__yql_executer': 'robot-tags-alias',
                            '__yql_experimental': (
                                'robot-tags-experimental-alias'
                            ),
                        },
                    },
                    TAGS_EXPERIMENTAL_CLIQUE_SETTINGS={
                        'is_enabled': True,
                        'queries': ['unknown_name'],
                    },
                ),
            ],
        ),
        pytest.param(
            ['fully_applied'],
            # create tables
            [_get_chyt_builder(clique='robot-tags-experimental-alias')],
            False,
            'CLICKHOUSE',
            marks=[
                pytest.mark.config(
                    UTAGS_CLIQUE_NAME={
                        '__default__': {
                            '__default__': 'robot-tags-default-alias',
                            '__yql_executer': 'robot-tags-alias',
                            '__yql_experimental': (
                                'robot-tags-experimental-alias'
                            ),
                        },
                    },
                    TAGS_EXPERIMENTAL_CLIQUE_SETTINGS={
                        'is_enabled': True,
                        'queries': [_QUERY.name],
                    },
                ),
            ],
        ),
    ],
)
@pytest.mark.now(_NOW.isoformat(timespec='seconds'))
async def test_basic(
        taxi_tags,
        use_dynamic_entity_types: bool,
        previous_execution_results: List[str],
        query_builders: List[Any],
        full_update_expected: bool,
        query_syntax: str,
        yt_client,
        pgsql,
        mockserver,
):
    db = pgsql['tags']

    cursor = db.cursor()
    query = copy.deepcopy(_QUERY)
    query.syntax = query_syntax
    if use_dynamic_entity_types and query_syntax == 'SQLv1':
        query.entity_type = None
    cursor.execute(yql_tools.insert_queries([query]))

    _insert_previous_results(
        db, previous_execution_results, 0, query_syntax, query.entity_type,
    )

    last_snapshot = None
    if 'fully_applied' in previous_execution_results:
        last_snapshot = _OLD_SNAPSHOT_PATH + str(
            previous_execution_results.index('fully_applied'),
        )

    expected_query = ''.join(
        builder(query.entity_type, last_snapshot) for builder in query_builders
    )

    @mockserver.json_handler('/yql/api/v2/operations')
    def handler(request):
        assert request.args == {}

        requested_data = json.loads(request.get_data())
        assert requested_data['type'] == query_syntax
        assert (
            yql_tools.remove_uuid(requested_data['content']) == expected_query
        )
        assert requested_data.get('acl', None) == {
            'canRead': ['test_maintainer', 'petya', 'vasya'],
            'canUpdate': ['test_maintainer', 'petya', 'vasya'],
        }

        response_yql = (
            '{{"id": "operation_id_{}", "status":' '"IDLE"}}'
        ).format(handler.times_called)
        return mockserver.make_response(response_yql, 200)

    await tags_tools.activate_task(taxi_tags, 'yql-executer')
    assert handler.has_calls

    yt_tables = [_TAG_NAMES_PATH, _TMP_PATH]
    if query_syntax == 'SQLv1':
        yt_tables.append(_ENTITY_TYPES_PATH)

    snapshot_path = _NOW_PATH

    if full_update_expected:
        append_path = snapshot_path
        remove_path = None
    else:
        append_path = _APPEND_PATH
        remove_path = _REMOVE_PATH
        yt_tables.extend([_APPEND_PATH, _REMOVE_PATH])

    _verify_yt_download_task(
        db,
        0,
        snapshot_path,
        append_path,
        remove_path,
        _TAG_NAMES_PATH,
        _ENTITY_TYPES_PATH if query_syntax == 'SQLv1' else None,
    )

    yt_tables_in_delete_queue = tags_select.select_table_named(
        'service.yt_tables_delete_queue', 'yt_table_path', db,
    )
    assert [
        yql_tools.remove_uuid(item['yt_table_path'])
        for item in yt_tables_in_delete_queue
    ] == sorted(yt_tables)


def _verify_table_empty(db, table_name):
    rows = tags_select.select_table_named(table_name, 'provider_id', db)
    assert not rows


@pytest.mark.config(UTAGS_YQL_WORKER_ENABLED=True)
@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_providers(
            [tags_tools.Provider(0, 'provider0', '', True)],
        ),
        yql_tools.insert_queries(
            [
                yql_tools.Query(
                    'query0',
                    0,
                    ['tag0'],
                    '2018-08-30T12:34:56.0',
                    '2018-08-30T12:34:56.0',
                    _BASIC_QUERY,
                    yql_processing_method='yt_merge',
                ),
            ],
        ),
        yql_tools.insert_snapshot(
            yql_tools.YtSnapshot(
                0, _OLD_SNAPSHOT_PATH, _HOUR_AGO, 'partially_applied',
            ),
        ),
    ],
)
async def test_execute_with_last_partially_applied(taxi_tags, pgsql):
    await tags_tools.activate_task(taxi_tags, 'yql-executer')
    db = pgsql['tags']
    # verify task has not been started
    _verify_table_empty(db, 'service.yt_download_tasks')
    _verify_table_empty(db, 'service.yql_operations')


@pytest.mark.now(_NOW.isoformat(timespec='seconds'))
@pytest.mark.config(UTAGS_YQL_WORKER_ENABLED=True)
@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_providers(
            [tags_tools.Provider(0, 'provider0', '', True)],
        ),
        yql_tools.insert_queries(
            [
                yql_tools.Query(
                    'query0',
                    0,
                    ['tag0'],
                    '2018-08-30T12:34:56.0',
                    '2018-08-30T12:34:56.0',
                    _BASIC_QUERY,
                    period=86400,
                    yql_processing_method='yt_merge',
                    entity_type='udid',
                    last_operation_id='operation_id_0',
                ),
            ],
        ),
        yql_tools.insert_operation(
            'operation_id_0',
            0,
            'udid',
            'failed',
            _HOUR_AGO,
            failure_type='execution_failed',
            retry_number=0,
        ),
    ],
)
@pytest.mark.parametrize('maximum_retries', [0, 1])
async def test_query_retry(
        taxi_tags, pgsql, mockserver, taxi_config, maximum_retries,
):
    taxi_config.set_values(
        dict(
            UTAGS_YQL_QUERIES_RETRIES={
                'defaults': {'sqlv1': 0, 'chyt': 0},
                'customs': {'query0': maximum_retries},
            },
        ),
    )

    @mockserver.json_handler('/yql/api/v2/operations')
    def handler(request):
        response_yql = (
            '{{"id": "operation_id_{}", "status":' '"IDLE"}}'
        ).format(handler.times_called + 1)
        return mockserver.make_response(response_yql, 200)

    await tags_tools.activate_task(taxi_tags, 'yql-executer')
    assert handler.has_calls is bool(maximum_retries)

    # check service.yt_download_tasks table
    if maximum_retries:
        _verify_yt_download_task(
            pgsql['tags'],
            0,
            _NOW_PATH,
            _NOW_PATH,
            None,
            _TAG_NAMES_PATH,
            _ENTITY_TYPES_PATH,
        )
    else:
        _verify_table_empty(pgsql['tags'], 'service.yt_download_tasks')

    # check service.yql_operations table
    expected_operations = [
        {
            'operation_id': 'operation_id_0',
            'provider_id': 0,
            'entity_type': 'udid',
            'status': 'failed',
            'started': _HOUR_AGO,
            'failure_description': None,
            'failure_type': 'execution_failed',
            'retry_number': 0,
        },
    ]
    if maximum_retries:
        expected_operations.append(
            {
                'operation_id': 'operation_id_1',
                'provider_id': 0,
                'entity_type': 'udid',
                'status': 'prepared',
                'started': _NOW,
                'failure_description': None,
                'failure_type': None,
                'retry_number': 1,
            },
        )
    _verify_yql_operations(pgsql['tags'], expected_operations)


@pytest.mark.config(UTAGS_YQL_WORKER_ENABLED=True)
@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_providers(
            [tags_tools.Provider(0, 'provider0', '', True)],
        ),
        yql_tools.insert_queries(
            [
                yql_tools.Query(
                    'query0',
                    0,
                    ['tag0'],
                    '2018-08-30T12:34:56.0',
                    '2018-08-30T12:34:56.0',
                    _BASIC_QUERY,
                    yql_processing_method='yt_merge',
                    entity_type='udid',
                ),
            ],
        ),
        yql_tools.insert_snapshot(
            yql_tools.YtSnapshot(
                0,
                _OLD_SNAPSHOT_PATH,
                _HOUR_AGO,
                'fully_applied',
                entity_type='dbid_uuid',
            ),
        ),
    ],
)
@pytest.mark.now(_NOW.isoformat(timespec='seconds'))
async def test_change_query_entity_type(taxi_tags, pgsql, mockserver):
    @mockserver.json_handler('/yql/api/v2/operations')
    def handler(request):
        assert request.args == {}

        expected_query = (
            yql_tools.gen_transformed_yql_query(
                user_query=_BASIC_QUERY,
                provider=_PROVIDER,
                entity_type='udid',
                last_snapshot_path=_OLD_SNAPSHOT_PATH,
            )
            + yql_tools.gen_yql_merge_query(
                provider=_PROVIDER, last_snapshot_path=_OLD_SNAPSHOT_PATH,
            )
        )
        requested_data = json.loads(request.get_data())
        assert requested_data['type'] == 'SQLv1'
        assert (
            yql_tools.remove_uuid(requested_data['content']) == expected_query
        )
        response_yql = (
            '{{"id": "operation_id_{}", "status":' '"IDLE"}}'
        ).format(handler.times_called)
        return mockserver.make_response(response_yql, 200)

    await tags_tools.activate_task(taxi_tags, 'yql-executer')

    assert handler.has_calls

    _verify_yt_download_task(
        pgsql['tags'],
        0,
        _NOW_PATH,
        _APPEND_PATH,
        _REMOVE_PATH,
        _TAG_NAMES_PATH,
        _ENTITY_TYPES_PATH,
    )


@pytest.mark.config(UTAGS_YQL_WORKER_ENABLED=True)
@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_providers(
            [tags_tools.Provider(0, 'provider0', '', True)],
        ),
        yql_tools.insert_queries(
            [
                yql_tools.Query(
                    'query0',
                    0,
                    ['tag0'],
                    '2018-08-30T12:34:56.0',
                    '2018-08-30T12:34:56.0',
                    _BASIC_QUERY,
                    yql_processing_method='yt_merge',
                    entity_type='udid',
                ),
            ],
        ),
    ],
)
@pytest.mark.parametrize('failure_count', [5, 2])
@pytest.mark.now(_NOW.isoformat(timespec='seconds'))
async def test_retry_insert_operation(
        taxi_tags, pgsql, mockserver, testpoint, failure_count: int,
):
    @testpoint('yql-insert-operation')
    def testpoint_handler(data):
        return {
            'inject_failure': (testpoint_handler.times_called < failure_count),
        }

    @mockserver.json_handler('/yql/api/v2/operations')
    def yql_handler(request):
        response_yql = '{"id": "operation_id", "status": "IDLE"}'
        return mockserver.make_response(response_yql, 200)

    await tags_tools.activate_task(taxi_tags, 'yql-executer')

    assert yql_handler.has_calls
    assert testpoint_handler.times_called == 3

    yt_snapshots = tags_select.select_table_named(
        'service.yt_snapshots', 'provider_id', pgsql['tags'],
    )

    expected_operation: Dict[str, Any] = {
        'entity_type': 'udid',
        'failure_description': None,
        'failure_type': None,
        'operation_id': 'operation_id',
        'started': _NOW,
        'status': 'prepared',
        'provider_id': 0,
        'retry_number': 0,
    }
    _verify_yql_operations(pgsql['tags'], [expected_operation])

    assert yt_snapshots
    del yt_snapshots[0]['snapshot_path']
    assert yt_snapshots == [
        {
            'provider_id': 0,
            'status': 'description',
            'created': _NOW,
            'entity_type': 'udid',
            'query_syntax': 'SQLv1',
        },
    ]