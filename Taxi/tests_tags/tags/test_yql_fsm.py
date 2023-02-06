# pylint: disable=C0302, C5521, C1801, W0612, W0621
import datetime
from typing import Dict
from typing import List
from typing import Tuple

import pytest

from tests_tags.tags import tags_select
from tests_tags.tags import tags_tools
from tests_tags.tags import yql_services_fixture
from tests_tags.tags import yql_tools
from tests_tags.tags.yql_services_fixture import (  # noqa: F401
    local_yql_services,
)

_NOW = datetime.datetime.now()
_TAG_NAMES_PATH = 'tag_names'
_TMP_PATH_PART = '_tmp_'
_SNAPSHOT_DIR = 'home/taxi/testsuite/features/tags/snapshots/'
_TASK_TICKET = 'TASKTICKET-1234'

_INIT_QUERIES = [
    tags_tools.insert_providers([tags_tools.Provider.from_id(0)]),
    yql_tools.insert_queries(
        [
            yql_tools.Query(
                'query',
                0,
                ['tag'],
                _NOW,
                _NOW,
                'query',
                yql_processing_method='yt_merge',
                tags_limit=100,
            ),
        ],
    ),
    yql_tools.insert_operation(
        yql_services_fixture.DEFAULT_OPERATION_ID,
        0,
        'dbid_uuid',
        'running',
        _NOW,
        retry_number=0,
    ),
    yql_tools.insert_yt_download_tasks(
        [
            yql_tools.YtDownloadTask(
                0,
                'snapshot',
                'append',
                ('remove', 'dbid_uuid'),
                tag_names_path=_TAG_NAMES_PATH,
            ),
        ],
    ),
    yql_tools.insert_subscriptions(
        [
            yql_tools.Subscription(
                0, 'd-captain', yql_tools.SUBSCRIPTION_TYPES,
            ),
            yql_tools.Subscription(0, 'loginef', yql_tools.SUBSCRIPTION_TYPES),
        ],
    ),
]


def _verify_yql_operation_status(db, provider_id: int, status: str):
    rows = tags_select.select_table_named(
        'service.yql_operations', 'provider_id', db,
    )
    assert len(rows) == 1
    assert rows[0]['provider_id'] == provider_id
    assert rows[0]['status'] == status


def _verify_yql_operation_empty_counters(db, provider_id: int):
    rows = tags_select.select_table_named(
        'service.yql_operations', 'provider_id', db,
    )
    assert len(rows) == 1
    assert rows[0]['provider_id'] == provider_id
    assert rows[0]['total_count'] is None
    assert rows[0]['added_count'] is None
    assert rows[0]['removed_count'] is None
    assert rows[0]['malformed_count'] is None


def _verify_yql_operation_counters(
        db, provider_id: int, counters: Dict[str, int],
):
    rows = tags_select.select_table_named(
        'service.yql_operations', 'provider_id', db,
    )
    assert len(rows) == 1
    assert rows[0]['provider_id'] == provider_id

    for counter_name, expected_value in counters.items():
        assert rows[0][counter_name] == expected_value, str(rows[0])


def _verify_download_tasks_empty(db):
    rows = tags_select.select_table_named(
        'service.yt_download_tasks', 'provider_id', db,
    )
    assert len(rows) == 0


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


def _set_yt_download_task_status(db, provider_id: int, status: str):
    cursor = db.cursor()
    cursor.execute(
        'UPDATE service.yt_download_tasks '
        'SET status=\'{}\' WHERE provider_id={}'.format(status, provider_id),
    )


def _clear_yql_operations(db):
    cursor = db.cursor()
    cursor.execute('DELETE FROM service.yql_operations')


def _extract_uuid(string: str):
    return string[-32:]


@pytest.mark.pgsql('tags', queries=_INIT_QUERIES)
@pytest.mark.config(
    UTAGS_YQL_WORKER_ENABLED=True,
    TAGS_YQL_NOTIFICATION_TEMPLATES_V2={
        'message_sender_name': {
            '__default__': 'yandex-taxi-passenger-tags service',
            'tags': 'yandex-taxi-tags service',
        },
        'templates_by_event': {
            'failure': {
                'subject': {
                    '__default__': 'Subject',
                    'tags': 'YQL query failed',
                },
                'body': {
                    '__default__': 'Body',
                    'tags': (
                        'YQL query \"query\" failed.\n'
                        'https://tariff-editor.taxi.yandex-team.ru/tag-queries'
                        '/{service_unit}/edit/{url_query_name}/history\n'
                        'Error description:\n{failure_description}'
                    ),
                },
            },
            'upcoming_query_expiration': {
                'subject': {
                    '__default__': 'Subject',
                    'tags': 'YQL query failed',
                },
                'body': {'__default__': 'Body'},
            },
            'query_expiration': {
                'subject': {
                    '__default__': 'Subject',
                    'tags': 'YQL query failed',
                },
                'body': {'__default__': 'Body'},
            },
        },
    },
)
@pytest.mark.parametrize(
    'maximum_retries, send_failed', [(0, None), (1, False), (1, True)],
)
async def test_yql_fail(
        taxi_tags,
        mockserver,
        testpoint,
        local_yql_services,  # noqa: F811
        pgsql,
        taxi_config,
        maximum_retries,
        send_failed,
):
    taxi_config.set_values(
        dict(
            UTAGS_YQL_QUERIES_RETRIES={
                'defaults': {'sqlv1': maximum_retries, 'chyt': 0},
                'customs': {},
            },
        ),
    )

    @mockserver.json_handler('/sticker/send-internal/')
    def _send_internal(request):
        return mockserver.make_response('{}', 500 if send_failed else 200)

    @testpoint('send_email_notification_finished')
    def _send_email_finished(data):
        pass

    local_yql_services.add_results_response(
        {
            'id': yql_services_fixture.DEFAULT_OPERATION_ID,
            'status': 'ERROR',
            'issues': [
                {
                    'code': 1030,
                    'column': 0,
                    'file': '<main>',
                    'issues': [
                        {
                            'code': 0,
                            'column': 1,
                            'file': '<main>',
                            'issues': [
                                {
                                    'code': 3004,
                                    'column': 1,
                                    'file': '<main>',
                                    'issues': [],
                                    'message': (
                                        'Root cause error: '
                                        'last token was <append=false>'
                                    ),
                                    'row': 3,
                                    'severity': 'S_ERROR',
                                },
                            ],
                            'message': 'Error message',
                            'row': 3,
                            'severity': 'S_ERROR',
                        },
                    ],
                    'message': 'Error message',
                },
            ],
        },
    )

    await tags_tools.activate_task(taxi_tags, 'yql-fsm')

    db = pgsql['tags']
    _verify_yql_operation_status(db, 0, 'failed')
    _verify_yql_operation_empty_counters(db, 0)
    _verify_download_tasks_empty(db)

    if maximum_retries == 0:
        await _send_email_finished.wait_call(5)
        assert _send_internal.has_calls
        send_internal_request = _send_internal.next_call()['request']
        assert sorted(send_internal_request.json['send_to'].split(',')) == [
            'd-captain@yandex-team.ru',
            'loginef@yandex-team.ru',
        ]
        assert (
            send_internal_request.json['body']
            == '<?xml version="1.0"?><mails><mail>'
            '<from>yandex-taxi-tags service &lt;no-reply@yandex-team.ru&gt;'
            '</from><subject>YQL query failed</subject>'
            '<body>YQL query \"query\" failed.\n'
            'https://tariff-editor.taxi.yandex-team.ru/tag-queries/tags/edit/'
            'query/history\n'
            'Error description:\n'
            'operation status: ERROR; message: Root cause error: '
            'last token was &lt;append=false&gt;</body></mail></mails>'
        )


@pytest.mark.pgsql('tags', queries=_INIT_QUERIES)
@pytest.mark.config(
    UTAGS_YQL_WORKER_ENABLED=True,
    TAGS_YQL_NOTIFICATION_SETTINGS={
        'failure': {'is_enabled': False, 'auto_subscribe_query_author': False},
        'upcoming_query_expiration': {
            'is_enabled': False,
            'auto_subscribe_query_author': False,
            'notification_schedule': [{'hours': 1}],
        },
        'query_expiration': {
            'is_enabled': False,
            'auto_subscribe_query_author': False,
        },
    },
)
async def test_yt_fail(
        taxi_tags, local_yql_services, yt_client, pgsql,  # noqa: F811
):
    local_yql_services.add_status_response('COMPLETED')
    local_yql_services.add_results_response(
        {
            'id': yql_services_fixture.DEFAULT_OPERATION_ID,
            'status': 'COMPLETED',
            'data': [{'Write': [{}]}],
            'updatedAt': '2019-06-18T07:04:50.528Z',
        },
    )

    yt_client.write_table('//' + _TAG_NAMES_PATH, [])
    await tags_tools.activate_task(taxi_tags, 'yql-fsm')

    db = pgsql['tags']
    yql_tools.verify_yt_download_task(
        db, 0, 'in_progress', check_status_only=True,
    )
    _verify_yql_operation_status(db, 0, 'downloading')

    # as if yt failed
    _set_yt_download_task_status(db, 0, 'failed')
    await tags_tools.activate_task(taxi_tags, 'yql-fsm')
    _verify_yql_operation_status(db, 0, 'failed')
    _verify_yql_operation_empty_counters(db, 0)
    _verify_download_tasks_empty(db)


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.config(
    TAGS_YT_DOWNLOADER_CHUNK_SIZE=4096,
    UTAGS_YQL_WORKER_ENABLED=True,
    TAGS_YT_SKIP_MALFORMED_ROWS=True,
)
async def test_flow(
        taxi_tags,
        local_yql_services,  # noqa: F811
        yt_client,
        pgsql,
        mocked_time,
):
    db = pgsql['tags']
    data = yql_tools.generate_and_insert_tags(
        db,
        local_yql_services,
        tags_count=5,
        tags_to_insert=0,
        entity_type='dbid_uuid',
    )

    # create query
    response = await yql_tools.edit_request(
        taxi_tags,
        'create',
        login='nagibator777',
        query_name='query_name',
        query='[_INSERT_HERE_] SELECT \'A777MP\' '
        'as dbid_uuid, \'tag_0\' as tag',
        tags=['tag_0'],
        ticket=_TASK_TICKET,
        tags_limit=100,
        enabled=True,
        period=1800,
    )
    assert response.status_code == 200

    provider_id = 1

    # prepare query
    local_yql_services.add_status_response('IDLE')
    await tags_tools.activate_task(taxi_tags, 'yql-executer')
    _verify_yql_operation_status(db, provider_id, 'prepared')
    _verify_yql_operation_empty_counters(db, provider_id)

    # execute query for the first time
    local_yql_services.set_operation_id(
        yql_services_fixture.DEFAULT_OPERATION_ID,
    )
    local_yql_services.add_results_response(
        {'id': yql_services_fixture.DEFAULT_OPERATION_ID, 'status': 'IDLE'},
    )
    await tags_tools.activate_task(taxi_tags, 'yql-fsm')
    assert local_yql_services.times_called['action'] == 1
    _verify_yql_operation_status(db, provider_id, 'running')
    _verify_yql_operation_empty_counters(db, provider_id)

    (
        snapshot,
        append,
        remove,
        tag_names,
        entity_types,
    ) = _get_download_task_paths(db)

    yql_tools.verify_yt_download_task(
        db, provider_id, 'description', 0, append, remove, 0,
    )

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
    yt_client.write_table(
        '//' + tag_names, [{'tag': 'tag_0'}], force_create=True,
    )
    yt_client.write_table(
        '//' + entity_types, [{'entity_type': 'dbid_uuid'}], force_create=True,
    )
    yt_client.write_table('//' + snapshot, data[:4], force_create=True)

    local_yql_services.add_results_response(
        {
            'id': yql_services_fixture.DEFAULT_OPERATION_ID,
            'status': 'COMPLETED',
            'data': [{'Write': [{}]}],
        },
    )
    await tags_tools.activate_task(taxi_tags, 'yql-fsm')
    yql_tools.verify_yt_download_task(
        db, provider_id, 'in_progress', check_status_only=True,
    )
    _verify_yql_operation_status(db, provider_id, 'downloading')

    expected_counters = {
        'total_count': 4,
        'added_count': 4,
        'removed_count': None,
    }
    _verify_yql_operation_counters(db, provider_id, expected_counters)

    assert append is not None and snapshot == append and remove is None

    yql_tools.verify_snapshot(db, snapshot, 'description')

    # look at append path
    await tags_tools.activate_task(taxi_tags, 'yt-downloader')
    # look at remove path
    await tags_tools.activate_task(taxi_tags, 'yt-downloader')
    yql_tools.verify_yt_download_task(
        db, provider_id, 'finished', 0, None, None, 0,
    )

    await tags_tools.activate_task(taxi_tags, 'yql-fsm')
    _verify_yql_operation_status(db, provider_id, 'completed')
    _verify_yql_operation_counters(db, provider_id, expected_counters)

    assert _extract_uuid(tag_names) == _extract_uuid(entity_types)
    yt_tables_for_remove = [
        tag_names,
        entity_types,
        _SNAPSHOT_DIR
        + 'query_name'
        + _TMP_PATH_PART
        + _extract_uuid(tag_names),
    ]

    await tags_tools.activate_task(taxi_tags, 'customs-officer')
    tags_tools.verify_active_tags(
        db,
        yql_tools.gen_tags(
            provider_id, 0, range(0, 4), entity_type='dbid_uuid',
        ),
    )

    # can't have two operations with the same name, so delete previous one
    _clear_yql_operations(db)
    mocked_time.set(datetime.datetime.now() + datetime.timedelta(minutes=1))
    await taxi_tags.tests_control()

    # execute query for the second time, incremental update
    local_yql_services.add_status_response('IDLE')
    await tags_tools.activate_task(taxi_tags, 'yql-executer')

    local_yql_services.add_results_response(
        {'id': yql_services_fixture.DEFAULT_OPERATION_ID, 'status': 'IDLE'},
    )
    await tags_tools.activate_task(taxi_tags, 'yql-fsm')
    assert local_yql_services.times_called['action'] == 2
    _verify_yql_operation_status(db, provider_id, 'running')
    _verify_yql_operation_empty_counters(db, provider_id)

    (
        snapshot,
        append,
        remove,
        tag_names,
        entity_types,
    ) = _get_download_task_paths(db)

    yql_tools.verify_yt_download_task(
        db, provider_id, 'description', 0, append, remove, 0,
    )

    assert (
        append is not None
        and remove is not None
        and snapshot != append
        and snapshot != remove
    )

    malformed_example = {
        'tag': None,
        'entity_type': 'dbid_uuid',
        'entity_value': f'entity0',
        'ttl': 'infinity',
    }

    yt_client.write_table('//' + entity_types, [{'entity_type': 'dbid_uuid'}])
    yt_client.write_table('//' + snapshot, data[1:] + [malformed_example])
    yt_client.write_table('//' + append, [data[4]] + [malformed_example])
    yt_client.write_table('//' + remove, [data[0]])
    yt_client.write_table('//' + tag_names, [{'tag': 'tag_0'}])

    local_yql_services.add_results_response(
        {
            'id': yql_services_fixture.DEFAULT_OPERATION_ID,
            'status': 'COMPLETED',
            'data': [{'Write': [{}]}],
            'updatedAt': '2019-06-18T07:04:50.528Z',
        },
    )
    await tags_tools.activate_task(taxi_tags, 'yql-fsm')
    yql_tools.verify_yt_download_task(
        db, provider_id, 'in_progress', check_status_only=True,
    )
    _verify_yql_operation_status(db, provider_id, 'downloading')

    expected_counters = {
        'total_count': 5,
        'added_count': 2,
        'removed_count': 1,
    }
    _verify_yql_operation_counters(db, provider_id, expected_counters)

    # look at append path
    await tags_tools.activate_task(taxi_tags, 'yt-downloader')
    # look at remove path
    await tags_tools.activate_task(taxi_tags, 'yt-downloader')
    yql_tools.verify_yt_download_task(
        db, provider_id, 'finished', 0, None, None, 1,
    )

    await tags_tools.activate_task(taxi_tags, 'yql-fsm')
    _verify_yql_operation_status(db, provider_id, 'completed')

    expected_counters['malformed_count'] = 1
    _verify_yql_operation_counters(db, provider_id, expected_counters)

    # yt-tables relations were added
    yt_tables_for_remove.extend(
        [
            append,
            remove,
            tag_names,
            entity_types,
            _SNAPSHOT_DIR
            + 'query_name'
            + _TMP_PATH_PART
            + _extract_uuid(tag_names),
        ],
    )
    yt_tables = tags_select.select_table_named(
        'service.yt_tables_delete_queue', 'yt_table_path', db,
    )
    assert [item['yt_table_path'] for item in yt_tables] == sorted(
        yt_tables_for_remove,
    )

    await tags_tools.activate_task(taxi_tags, 'customs-officer')
    tags_tools.verify_active_tags(
        db,
        yql_tools.gen_tags(
            provider_id, 0, range(1, 5), entity_type='dbid_uuid',
        ),
    )


@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_providers([tags_tools.Provider.from_id(0)]),
        yql_tools.insert_queries(
            [
                yql_tools.Query(
                    name='query_name',
                    provider_id=0,
                    tags=['tag_0'],
                    changed=_NOW,
                    created=_NOW,
                    tags_limit=100,
                ),
            ],
        ),
    ],
)
@pytest.mark.config(UTAGS_YQL_WORKER_ENABLED=True)
async def test_tags_not_from_list(
        taxi_tags, yt_client, pgsql, local_yql_services,  # noqa: F811
):
    local_yql_services.add_status_response('IDLE')

    await tags_tools.activate_task(taxi_tags, 'yql-executer', 200)  # prepare
    local_yql_services.add_status_response('COMPLETED')

    db = pgsql['tags']
    (
        snapshot,
        append,
        remove,
        tag_names,
        entity_types,
    ) = _get_download_task_paths(db)
    await tags_tools.activate_task(taxi_tags, 'yql-fsm', 200)  # run
    yt_client.write_table(
        '//' + tag_names, [{'tag': 'tag_0'}, {'tag': 'tag_1'}],
    )
    yt_client.write_table('//' + entity_types, [{'entity_type': 'dbid_uuid'}])

    await tags_tools.activate_task(taxi_tags, 'yql-fsm', 200)
    _verify_yql_operation_status(db, 0, 'failed')


@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_providers([tags_tools.Provider.from_id(0)]),
        yql_tools.insert_queries(
            [
                yql_tools.Query(
                    name='query_name',
                    provider_id=0,
                    tags=['tag_0'],
                    changed=_NOW,
                    created=_NOW,
                    tags_limit=100,
                ),
            ],
        ),
    ],
)
@pytest.mark.config(UTAGS_YQL_WORKER_ENABLED=True)
@pytest.mark.parametrize(
    'entity_types', [['udid', 'user_phone_id'], ['not_entity_type']],
)
async def test_bad_entity_types(
        taxi_tags,
        yt_client,
        pgsql,
        local_yql_services,  # noqa: F811
        entity_types,
):
    local_yql_services.add_status_response('IDLE')

    await tags_tools.activate_task(taxi_tags, 'yql-executer', 200)  # prepare
    local_yql_services.add_status_response('COMPLETED')

    db = pgsql['tags']
    (
        snapshot,
        append,
        remove,
        tag_names,
        entity_types,
    ) = _get_download_task_paths(db)
    await tags_tools.activate_task(taxi_tags, 'yql-fsm', 200)  # run
    yt_client.write_table('//' + tag_names, [{'tag': 'tag_0'}])
    yt_client.write_table(
        '//' + entity_types,
        [{'entity_type': entity_type} for entity_type in entity_types],
    )

    await tags_tools.activate_task(taxi_tags, 'yql-fsm', 200)
    _verify_yql_operation_status(db, 0, 'failed')


@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_providers(
            [tags_tools.Provider.from_id(0), tags_tools.Provider.from_id(1)],
        ),
        yql_tools.insert_queries(
            [
                yql_tools.Query(
                    name='sql_query',
                    provider_id=0,
                    tags=['tag_0'],
                    changed=_NOW,
                    created=_NOW,
                    syntax='SQLv1',
                    tags_limit=100,
                ),
                yql_tools.Query(
                    name='chyt_query',
                    provider_id=1,
                    tags=['tag_0'],
                    changed=_NOW,
                    created=_NOW,
                    syntax='CLICKHOUSE',
                    tags_limit=100,
                ),
            ],
        ),
        yql_tools.insert_operation(
            'operation_id0',
            0,
            'dbid_uuid',
            'running',
            '2020-09-30 12:00:00+0000',
        ),
        yql_tools.insert_operation(
            'operation_id1',
            1,
            'dbid_uuid',
            'running',
            '2020-09-30 12:00:00+0000',
        ),
    ],
)
@pytest.mark.config(UTAGS_YQL_WORKER_ENABLED=True)
@pytest.mark.parametrize(
    'expected_operation_statuses',
    [
        pytest.param(
            [(0, 'running'), (1, 'running')],
            marks=[
                pytest.mark.config(
                    TAGS_YQL_QUERIES_TIMEOUTS_V2={
                        'defaults': {'sqlv1': 600, 'chyt': 600},
                        'custom': {},
                    },
                ),
            ],
            id='fit_in_default_timeouts',
        ),
        pytest.param(
            [(0, 'failed'), (1, 'running')],
            marks=[
                pytest.mark.config(
                    TAGS_YQL_QUERIES_TIMEOUTS_V2={
                        'defaults': {'sqlv1': 60, 'chyt': 600},
                        'custom': {},
                    },
                ),
            ],
            id='exceed_default_sql_timeout',
        ),
        pytest.param(
            [(0, 'running'), (1, 'failed')],
            marks=[
                pytest.mark.config(
                    TAGS_YQL_QUERIES_TIMEOUTS_V2={
                        'defaults': {'sqlv1': 600, 'chyt': 60},
                        'custom': {},
                    },
                ),
            ],
            id='exceed_default_chyt_timeout',
        ),
        pytest.param(
            [(0, 'failed'), (1, 'running')],
            marks=[
                pytest.mark.config(
                    TAGS_YQL_QUERIES_TIMEOUTS_V2={
                        'defaults': {'sqlv1': 600, 'chyt': 60},
                        'custom': {
                            'tags': {'sql_query': 60, 'chyt_query': 600},
                        },
                    },
                ),
            ],
            id='exceed_custom_sql_timeout',
        ),
        pytest.param(
            [(0, 'failed'), (1, 'failed')],
            marks=[
                pytest.mark.config(
                    TAGS_YQL_QUERIES_TIMEOUTS_V2={
                        'defaults': {'sqlv1': 600, 'chyt': 600},
                        'custom': {
                            'tags': {'sql_query': 60, 'chyt_query': 60},
                        },
                    },
                ),
            ],
            id='exceed_custom_timeouts',
        ),
        pytest.param(
            [(0, 'running'), (1, 'running')],
            marks=[
                pytest.mark.config(
                    TAGS_YQL_QUERIES_TIMEOUTS_V2={
                        'defaults': {'sqlv1': 60, 'chyt': 60},
                        'custom': {
                            'tags': {'sql_query': 600, 'chyt_query': 600},
                        },
                    },
                ),
            ],
            id='fit_in_custom_timeouts',
        ),
    ],
)
@pytest.mark.now('2020-09-30 12:05:00+0000')
async def test_yql_timeout(
        taxi_tags,
        pgsql,
        mockserver,
        expected_operation_statuses: List[Tuple[int, str]],
):
    is_yql_aborted = {}

    @mockserver.json_handler(
        '/yql/api/v2/operations/(?P<operation_id>\\w+)', regex=True,
    )
    def action_handler(request, operation_id):
        assert request.method == 'POST'
        assert request.json['action'] == 'ABORT'
        assert operation_id not in is_yql_aborted
        is_yql_aborted[operation_id] = True
        response = '{"id": "%s", "status": "%s"}' % (operation_id, 'RUNNING')
        return mockserver.make_response(response, 200)

    @mockserver.json_handler(
        '/yql/api/v2/operations/(?P<operation_id>\\w+)/results', regex=True,
    )
    def results_handler(request, operation_id):
        response = '{"id": "%s", "status": "%s"}' % (operation_id, 'RUNNING')
        assert operation_id not in is_yql_aborted
        is_yql_aborted[operation_id] = False
        return mockserver.make_response(response, 200)

    await tags_tools.activate_task(taxi_tags, 'yql-fsm')

    db_rows = tags_select.select_table_named(
        'service.yql_operations', 'provider_id', pgsql['tags'],
    )
    db_operations = list(
        map(lambda row: (row['provider_id'], row['status']), db_rows),
    )
    assert db_operations == expected_operation_statuses
    assert is_yql_aborted == {
        f'operation_id{id_}': status == 'failed'
        for id_, status in expected_operation_statuses
    }


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.pgsql(
    'tags',
    queries=_INIT_QUERIES
    + [
        yql_tools.insert_snapshots(
            [
                yql_tools.YtSnapshot(
                    0,
                    'prev_snapshot',
                    _NOW - datetime.timedelta(hours=1),
                    'fully_applied',
                ),
                yql_tools.YtSnapshot(
                    0,
                    'snapshot',
                    _NOW - datetime.timedelta(minutes=1),
                    'description',
                ),
            ],
        ),
    ],
)
@pytest.mark.config(
    UTAGS_YQL_WORKER_ENABLED=True,
    UTAGS_YQL_RECORDS_COUNTS_MISMATCH_ERROR={'__default__': True},
    TAGS_YQL_NOTIFICATION_SETTINGS={
        'failure': {'is_enabled': False, 'auto_subscribe_query_author': False},
        'upcoming_query_expiration': {
            'is_enabled': False,
            'auto_subscribe_query_author': False,
            'notification_schedule': [{'hours': 1}],
        },
        'query_expiration': {
            'is_enabled': False,
            'auto_subscribe_query_author': False,
        },
    },
)
@pytest.mark.parametrize('mismatch', [False, True])
async def test_tags_count_mismatch(
        taxi_tags,
        local_yql_services,  # noqa: F811
        yt_client,
        pgsql,
        mismatch,
):
    local_yql_services.add_results_response(
        {
            'id': yql_services_fixture.DEFAULT_OPERATION_ID,
            'status': 'COMPLETED',
            'data': [{'Write': [{}]}],
        },
    )

    db = pgsql['tags']
    data = yql_tools.generate_and_insert_tags(
        db,
        local_yql_services,
        tags_count=10,
        tags_to_insert=0,
        entity_type='dbid_uuid',
    )

    yt_client.write_table('//prev_snapshot', data[0:6])
    yt_client.write_table('//snapshot', data[5:10])
    yt_client.write_table('//' + _TAG_NAMES_PATH, [])

    if mismatch:
        yt_client.write_table('//remove', data[0:2])
        yt_client.write_table('//append', data[6:10])
    else:
        yt_client.write_table('//remove', data[0:5])
        yt_client.write_table('//append', data[6:10])

    await tags_tools.activate_task(taxi_tags, 'yql-fsm')

    if mismatch:
        _verify_yql_operation_status(db, 0, 'failed')
    else:
        _verify_yql_operation_status(db, 0, 'downloading')
        yql_tools.verify_yt_download_task(
            db, 0, 'in_progress', check_status_only=True,
        )


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.pgsql(
    'tags',
    queries=_INIT_QUERIES
    + [
        yql_tools.insert_snapshots(
            [
                yql_tools.YtSnapshot(
                    0,
                    'snapshot',
                    _NOW - datetime.timedelta(minutes=1),
                    'description',
                ),
            ],
        ),
    ],
)
@pytest.mark.config(
    UTAGS_YQL_WORKER_ENABLED=True,
    TAGS_YQL_NOTIFICATION_SETTINGS={
        'failure': {'is_enabled': False, 'auto_subscribe_query_author': False},
        'upcoming_query_expiration': {
            'is_enabled': False,
            'auto_subscribe_query_author': False,
            'notification_schedule': [{'hours': 1}],
        },
        'query_expiration': {
            'is_enabled': False,
            'auto_subscribe_query_author': False,
        },
    },
)
@pytest.mark.parametrize(
    'passed',
    [
        pytest.param(
            False,
            marks=[
                pytest.mark.config(
                    TAGS_YQL_COUNT_LIMITS={
                        '__default__': {'__default__': 100},
                    },
                ),
            ],
            id='exceeded by config value',
        ),
        pytest.param(
            False,
            marks=[
                pytest.mark.pgsql(
                    'tags',
                    queries=['UPDATE service.queries SET tags_limit=100'],
                ),
            ],
            id='exceeded by query data',
        ),
        pytest.param(
            False,
            marks=[
                pytest.mark.config(
                    TAGS_YQL_COUNT_LIMITS={
                        '__default__': {'__default__': 200, 'query': 100},
                    },
                ),
                pytest.mark.pgsql(
                    'tags',
                    queries=['UPDATE service.queries SET tags_limit=200'],
                ),
            ],
            id='specific config is more priority',
        ),
        pytest.param(
            True,
            marks=[
                pytest.mark.config(
                    TAGS_YQL_COUNT_LIMITS={
                        '__default__': {'__default__': 100},
                    },
                ),
                pytest.mark.pgsql(
                    'tags',
                    queries=['UPDATE service.queries SET tags_limit=110'],
                ),
            ],
            id='passed: query data is selected',
        ),
        pytest.param(
            True,
            marks=[
                pytest.mark.config(
                    TAGS_YQL_COUNT_LIMITS={
                        '__default__': {'__default__': 110},
                    },
                ),
                pytest.mark.pgsql(
                    'tags',
                    queries=['UPDATE service.queries SET tags_limit=110'],
                ),
            ],
            id='passed: limit is not exceeded',
        ),
    ],
)
async def test_tags_limit_exceeded(
        taxi_tags, local_yql_services, yt_client, pgsql, passed,  # noqa: F811
):
    local_yql_services.add_results_response(
        {
            'id': yql_services_fixture.DEFAULT_OPERATION_ID,
            'status': 'COMPLETED',
            'data': [{'Write': [{}]}],
        },
    )

    db = pgsql['tags']
    data = yql_tools.generate_and_insert_tags(
        db,
        local_yql_services,
        tags_count=101,
        tags_to_insert=0,
        entity_type='dbid_uuid',
    )

    yt_client.write_table('//snapshot', data)
    yt_client.write_table('//' + _TAG_NAMES_PATH, [])
    yt_client.write_table('//append', data)

    await tags_tools.activate_task(taxi_tags, 'yql-fsm')

    if passed:
        _verify_yql_operation_status(db, 0, 'downloading')
        yql_tools.verify_yt_download_task(
            db, 0, 'in_progress', check_status_only=True,
        )
    else:
        _verify_yql_operation_status(db, 0, 'failed')
