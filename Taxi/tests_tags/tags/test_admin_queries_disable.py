# pylint: disable=C1801, W0612
import datetime

import pytest

from tests_tags.tags import tags_select
from tests_tags.tags import tags_tools
from tests_tags.tags import yql_tools


_USERNAME = 'ivanov'
_TMP_PATH = 'tmp/' + _USERNAME + '/88f63051-d0da20b8-370e8722-d51dc23a'
_OPERATION_ID = 'operation_id'
_NOW = datetime.datetime.now()
_MINUTES_AFTER = _NOW + datetime.timedelta(minutes=3)
_HOUR_BEFORE = _NOW - datetime.timedelta(hours=1)
_HOUR_AFTER = _NOW + datetime.timedelta(hours=1)
_TWO_HOURS_AFTER = _HOUR_AFTER + datetime.timedelta(hours=1)
_INFINITY = datetime.datetime(9999, 12, 31, 23, 59, 59, 999999)
_SNAPSHOT_DIR = '//home/taxi/testsuite/features/tags/snapshots/name_1'
_TASK_TICKET = 'TASKTICKET-1234'

_LOGIN = 'science-intensive'
_QUERIES = [
    yql_tools.Query(
        'yql1',
        1,
        ['tag1'],
        _HOUR_BEFORE,
        _HOUR_BEFORE,
        period=1000000,
        ticket=_TASK_TICKET,
    ),
    yql_tools.Query(
        'yql2',
        2,
        ['tag2'],
        _HOUR_BEFORE,
        _HOUR_BEFORE,
        period=1000000,
        ticket=_TASK_TICKET,
    ),
    yql_tools.Query(
        _OPERATION_ID,
        1,
        ['tag1'],
        _HOUR_BEFORE,
        _HOUR_BEFORE,
        ticket=_TASK_TICKET,
        tags_limit=100,
    ),
    yql_tools.Query(
        'yql4',
        1,
        ['tag1'],
        _HOUR_BEFORE,
        _HOUR_BEFORE,
        yql_processing_method='yt_merge',
        ticket=_TASK_TICKET,
    ),
]


def _verify_tags_empty(db):
    cursor = db.cursor()
    cursor.execute('SELECT COUNT(*) FROM state.tags')

    rows = list(row for row in cursor)
    assert rows[0][0] == 0


def _verify_tag_doesnt_have_infinity_ttl(db):
    rows = tags_select.select_table_named('state.tags', 'revision', db)
    assert len(rows) == 1
    assert rows[0]['ttl'] != _INFINITY


def _verify_tag_has_infinity_ttl(db):
    rows = tags_select.select_table_named('state.tags', 'revision', db)
    assert len(rows) == 1
    assert rows[0]['ttl'] == _INFINITY


def _get_snapshot_path(db, snapshot_name):
    rows = tags_select.select_table_named(
        'service.yt_download_tasks', 'snapshot_path', db,
    )
    assert len(rows) == 1
    return rows[0][snapshot_name]


def _verify_operation_status(db, operation_name, status):
    cursor = db.cursor()
    cursor.execute(
        'SELECT status FROM service.yql_operations'
        ' WHERE operation_id=\'{}\''.format(operation_name),
    )

    rows = list(row for row in cursor)
    assert rows[0][0] == status


@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_entities([tags_tools.Entity(1, 'e1', 'dbid_uuid')]),
        tags_tools.insert_providers(
            [tags_tools.Provider.from_id(1), tags_tools.Provider.from_id(2)],
        ),
        tags_tools.insert_tag_names(
            [tags_tools.TagName(1, 'tag1'), tags_tools.TagName(2, 'tag2')],
        ),
        yql_tools.insert_queries([_QUERIES[0], _QUERIES[1]]),
        yql_tools.insert_operation('op1', 1, 'udid', 'completed', _NOW),
        yql_tools.insert_operation('op2', 2, 'udid', 'running', _NOW),
        tags_tools.insert_tags(
            [tags_tools.Tag(1, 1, 1, entity_type='dbid_uuid')],
        ),
    ],
)
async def test_disable_query(taxi_tags, mocked_time, pgsql, mockserver):
    @mockserver.json_handler('/yql/api/v2/operations/op2')
    def yql_operations_handler(request):
        response = '{"id": "%s", "username": "%s", "status": "%s"}' % (
            'op2',
            _USERNAME,
            'ABORTING',
        )
        return mockserver.make_response(response, 200)

    await yql_tools.change_query_active_state(
        taxi_tags, _QUERIES[0], _LOGIN, False,
    )
    await yql_tools.change_query_active_state(
        taxi_tags, _QUERIES[1], _LOGIN, False,
    )
    await tags_tools.activate_task(taxi_tags, 'tags-updater')
    await tags_tools.activate_task(taxi_tags, 'tags-updater')
    await tags_tools.activate_task(taxi_tags, 'customs-officer')
    # make garbage collector remove tags
    mocked_time.set(_TWO_HOURS_AFTER)
    await tags_tools.activate_task(taxi_tags, 'garbage-collector')
    db = pgsql['tags']
    _verify_tags_empty(db)
    _verify_operation_status(db, 'op1', 'completed')
    _verify_operation_status(db, 'op2', 'aborted')

    handler_request = await yql_operations_handler.wait_call()
    assert handler_request['request'].json['action'] == 'ABORT'


@pytest.mark.config(UTAGS_YQL_WORKER_ENABLED=True)
@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_entities([tags_tools.Entity(1, 'e1', 'dbid_uuid')]),
        tags_tools.insert_providers([tags_tools.Provider.from_id(1)]),
        tags_tools.insert_tag_names([tags_tools.TagName(1, 'tag1')]),
        yql_tools.insert_queries([_QUERIES[2]]),
        tags_tools.insert_tags(
            [tags_tools.Tag(1, 1, 1, entity_type='dbid_uuid')],
        ),
        # snapshot is needed, because if it exists,
        # yql-executer doesn't go to YT
        yql_tools.insert_snapshot(
            yql_tools.YtSnapshot(1, 's', _NOW, 'fully_applied'),
        ),
    ],
)
@pytest.mark.now(_NOW.isoformat())
# first disable provider and set its tags' ttls = updated
# then enable provider and verify that ttls again are infinity
async def test_disable_enable_frequently_run_query(
        taxi_tags, pgsql, mocked_time, mockserver, yt_client,
):
    @mockserver.json_handler('/yql/api/v2/operations')
    def handler(_):
        response = '{{"id": "{}", "status": "IDLE"}}'.format(_OPERATION_ID)
        return mockserver.make_response(response, 200)

    @mockserver.json_handler(
        '/yql/api/v2/operations/%s/results' % _OPERATION_ID,
    )
    def status_handler(_):
        response = '{"id": "%s", "username": "%s", "status": "%s"}' % (
            _OPERATION_ID,
            _USERNAME,
            'COMPLETED',
        )
        return mockserver.make_response(response, 200)

    @mockserver.json_handler(
        '/yql/api/v2/operations/%s/results_data' % _OPERATION_ID,
    )
    def results_data_handler(_):
        results_data = 'tag,dbid_uuid\r\ntag1,e1\r\n'
        return mockserver.make_response(results_data, 200)

    @mockserver.json_handler(
        '/yql/api/v2/operations/%s/results' % _OPERATION_ID,
    )
    def results_handler(_):
        return {
            'id': _OPERATION_ID,
            'status': 'COMPLETED',
            'data': [{'Write': [{}]}],
            'updatedAt': '2019-06-18T07:04:50.528Z',
        }

    # set ttl of tag1 to now
    await yql_tools.change_query_active_state(
        taxi_tags, _QUERIES[2], _LOGIN, False,
    )
    await tags_tools.activate_task(taxi_tags, 'tags-updater')
    await tags_tools.activate_task(taxi_tags, 'customs-officer')
    _verify_tag_doesnt_have_infinity_ttl(pgsql['tags'])
    await yql_tools.change_query_active_state(
        taxi_tags, _QUERIES[2], _LOGIN, True,
    )
    # yql query should be executed because of period
    mocked_time.set(_MINUTES_AFTER)
    await taxi_tags.tests_control()
    await tags_tools.activate_task(taxi_tags, 'yql-executer')

    yt_client.create_table(
        '//' + _get_snapshot_path(pgsql['tags'], 'snapshot_path'),
        recursive=True,
        attributes={
            'schema': [
                {'name': 'entity_value', 'type': 'string'},
                {'name': 'entity_type', 'type': 'string'},
                {'name': 'tag', 'type': 'string'},
                {'name': 'ttl', 'type': 'string'},
                {'name': 'dbid_uuid', 'type': 'string'},
            ],
        },
    )
    yt_client.write_table(
        '//' + _get_snapshot_path(pgsql['tags'], 'snapshot_path'),
        [
            {
                'entity_type': 'dbid_uuid',
                'entity_value': 'e1',
                'tag': 'tag1',
                'ttl': 'infinity',
                'dbid_uuid': 'e1',
            },
        ],
    )
    yt_client.write_table(
        '//' + _get_snapshot_path(pgsql['tags'], 'tag_names_path'),
        [{'tag': 'tag1'}],
    )
    yt_client.write_table(
        '//' + _get_snapshot_path(pgsql['tags'], 'entity_types_path'),
        [{'entity_type': 'dbid_uuid'}],
    )

    await tags_tools.activate_task(taxi_tags, 'yql-fsm')  # run
    await tags_tools.activate_task(taxi_tags, 'yql-fsm')  # complete
    await tags_tools.activate_task(taxi_tags, 'yt-downloader')
    await tags_tools.activate_task(taxi_tags, 'customs-officer')
    _verify_tag_has_infinity_ttl(pgsql['tags'])


def _verify_yt_download_tasks_empty(db):
    rows = tags_select.select_table_named(
        'service.yt_download_tasks', 'provider_id', db,
    )
    assert len(rows) == 0


@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_providers([tags_tools.Provider.from_id(1)]),
        yql_tools.insert_queries([_QUERIES[3]]),
        yql_tools.insert_yt_download_tasks(
            [
                yql_tools.YtDownloadTask(
                    1,
                    'snapshot',
                    'append',
                    ('remove', 'dbid_uuid'),
                    0,
                    'in_progress',
                ),
            ],
        ),
        yql_tools.insert_snapshot(
            yql_tools.YtSnapshot(1, 'snapshot', _NOW, 'partially_applied'),
        ),
    ],
)
async def test_disable_downloading_query(taxi_tags, pgsql):
    await yql_tools.change_query_active_state(
        taxi_tags, _QUERIES[3], _LOGIN, False,
    )
    db = pgsql['tags']
    yql_tools.verify_snapshot_status(db, 'outdated')
    _verify_yt_download_tasks_empty(db)
