import datetime
import json
from typing import Optional

import pytest

from tests_tags.tags import tags_select
from tests_tags.tags import tags_tools
from tests_tags.tags import yql_tools


_NOW = datetime.datetime(2077, 1, 18, 10, 54, 9)
_QUERY_NAME = 'query0'
_SNAPSHOTS_PATH = 'home/taxi/testsuite/features/passenger-tags/snapshots'
_SNAPSHOT_PATH = _SNAPSHOTS_PATH + '/' + _QUERY_NAME + '_snapshot'
_OLD_SNAPSHOT_PATH = 'some/old/path/0/old_snapshot'
_APPEND_PATH = _SNAPSHOTS_PATH + '/' + _QUERY_NAME + '_append'
_REMOVE_PATH = _SNAPSHOTS_PATH + '/' + _QUERY_NAME + '_remove'
_TAG_NAMES_PATH = _SNAPSHOTS_PATH + '/' + _QUERY_NAME + '_tag_names'
_ENTITY_TYPES_PATH = _SNAPSHOTS_PATH + '/' + _QUERY_NAME + '_entity_types'
_QUERY = yql_tools.Query(
    _QUERY_NAME,
    0,
    ['tag0'],
    '2018-08-30T12:34:56.0',
    '2018-08-30T12:34:56.0',
    '[_INSERT_HERE_] SELECT * FROM X',
    entity_type='yandex_uid',
    yql_processing_method='yt_merge',
    tags_limit=1000,
)


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


@pytest.mark.config(UTAGS_YQL_WORKER_ENABLED=True)
@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_providers(
            [tags_tools.Provider(0, _QUERY_NAME, '', True)],
        ),
        yql_tools.insert_snapshot(
            yql_tools.YtSnapshot(
                0,
                _OLD_SNAPSHOT_PATH + '0',
                _NOW - datetime.timedelta(minutes=1),
                'fully_applied',
                query_syntax=_QUERY.syntax,
                entity_type=_QUERY.entity_type,
            ),
        ),
        yql_tools.insert_queries([_QUERY]),
    ],
)
@pytest.mark.now(_NOW.isoformat(timespec='seconds'))
async def test_basic(taxi_passenger_tags, yt_client, pgsql, mockserver):
    @mockserver.json_handler('/yql/api/v2/operations')
    def handler(request):
        assert request.args == {}

        requested_data = json.loads(request.get_data())
        assert requested_data['type'] == _QUERY.syntax
        # note: query text from \'content\' key is not checked

        response_yql = (
            '{{"id": "operation_id_{}", "status":' '"IDLE"}}'
        ).format(handler.times_called)
        return mockserver.make_response(response_yql, 200)

    await tags_tools.activate_task(taxi_passenger_tags, 'yql-executer')
    assert handler.has_calls

    _verify_yt_download_task(
        pgsql['tags'],
        0,
        _SNAPSHOT_PATH,
        _APPEND_PATH,
        _REMOVE_PATH,
        _TAG_NAMES_PATH,
        _ENTITY_TYPES_PATH,
    )
