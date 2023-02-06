import datetime
import json

import pytest

from tests_tags.tags import tags_select
from tests_tags.tags import tags_tools
from tests_tags.tags import yql_tools

_NOW = datetime.datetime(2021, 11, 9, 10, 54, 9)
_HOUR = datetime.timedelta(hours=1)

_QUERY = 'query0'
_PROVIDER_ID = 0
_PROVIDER = 'provider0'
_OPERATION_ID = 'operation_id_0'
_BASIC_QUERY = '[_INSERT_HERE_]'


@pytest.mark.config(UTAGS_YQL_WORKER_ENABLED=True)
@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_providers(
            [tags_tools.Provider(_PROVIDER_ID, _PROVIDER, '', True)],
        ),
        yql_tools.insert_queries(
            [
                yql_tools.Query(
                    _QUERY,
                    _PROVIDER_ID,
                    ['tag0'],
                    _NOW,
                    _NOW,
                    _BASIC_QUERY,
                    period=3599,
                    yql_processing_method='yt_merge',
                    entity_type='dbid_uuid',
                ),
            ],
        ),
        yql_tools.insert_operation(
            'operation_id_last',
            _PROVIDER_ID,
            'udid',
            'completed',
            _NOW - _HOUR,
        ),
        yql_tools.insert_yt_download_tasks(
            [
                yql_tools.YtDownloadTask(
                    _PROVIDER_ID,
                    'snapshot_path_last',
                    append_path='append_path_last',
                    remove_info=('remove_path_last', 'udid'),
                    tag_names_path='tag_names_last',
                    entity_types_path='entity_types_path_last',
                    status='finished',
                ),
            ],
        ),
        yql_tools.insert_snapshot(
            yql_tools.YtSnapshot(
                _PROVIDER_ID,
                'snapshot_path_last',
                _NOW - _HOUR,
                'fully_applied',
                'udid',
            ),
        ),
    ],
)
@pytest.mark.now(_NOW.isoformat(timespec='seconds'))
async def test_update_entity_type_flow(
        taxi_tags, pgsql, mockserver, mocked_time,
):
    # there is case:
    #  - yql-query is full completed and applied;
    #  - user updated entity type and ran yql-query;
    #  - the new execution was failed;
    #  - and all related snapshots were enqueued for delete;
    #  - also next generated yql-query is the same.
    # Make sure that deleted snapshots are not related for previous execution.
    # Note: related snapshots for previous execution should be in enqueued
    #       already, (they should be enqueued by execution),
    #       but for test purpose they are absent.
    @mockserver.json_handler('/yql/api/v2/operations')
    def _yql_operations(request):
        requested_data = json.loads(request.get_data())
        query = yql_tools.remove_uuid(requested_data['content'])
        expected_query = yql_tools.gen_transformed_yql_query(
            _BASIC_QUERY, _PROVIDER, 'dbid_uuid', 'snapshot_path_last',
        ) + yql_tools.gen_yql_merge_query(_PROVIDER, 'snapshot_path_last')
        assert query == expected_query

        response = {'id': _OPERATION_ID, 'status': 'IDLE'}
        return mockserver.make_response(json.dumps(response), 200)

    @mockserver.json_handler(
        '/yql/api/v2/operations/%s/results' % _OPERATION_ID,
    )
    def _yql_results_operations(_):
        response = {'id': _OPERATION_ID, 'status': 'ERROR'}
        return mockserver.make_response(json.dumps(response), 200)

    await tags_tools.activate_task(taxi_tags, 'yql-executer')
    assert _yql_operations.times_called == 1

    await tags_tools.activate_task(taxi_tags, 'yql-fsm')
    assert _yql_results_operations.times_called == 1

    # make sure that yt-tables of failed operation are in queue for delete
    yt_tables_in_delete_queue = tags_select.select_table_named(
        'service.yt_tables_delete_queue', 'yt_table_path', pgsql['tags'],
    )
    yt_table_paths = [
        yql_tools.remove_uuid(row['yt_table_path'])
        for row in yt_tables_in_delete_queue
    ]
    assert yt_table_paths == [
        yql_tools.gen_append_path(_PROVIDER),
        yql_tools.gen_entity_types_path(_PROVIDER),
        yql_tools.gen_remove_path(_PROVIDER),
        yql_tools.gen_tag_names_path(_PROVIDER),
        yql_tools.gen_tmp_path(_PROVIDER),
    ]

    # make sure that next generated yql-query is the same:
    # yt-table 'snapshot_path_last' is used
    mocked_time.sleep(3601)
    await tags_tools.activate_task(taxi_tags, 'yql-executer')
    assert _yql_operations.times_called == 2
