import datetime
import json

import pytest

from tests_tags.tags import tags_tools
from tests_tags.tags import yql_tools

_NOW = datetime.datetime(2077, 1, 18, 10, 54, 9)
_HOUR_AGO = _NOW - datetime.timedelta(hours=1)
_DIRECTORY_PATH = 'home/taxi/testsuite/features/tags/snapshots/provider0'
_NOW_PATH = _DIRECTORY_PATH + '/' + _NOW.isoformat(timespec='seconds')
_OLD_SNAPSHOT_PATH = 'some/old/path/0/' + _HOUR_AGO.isoformat(
    timespec='seconds',
)
_BASIC_QUERY = (
    'DIFFICULT SELECTS AND JOINS [_INSERT_HERE_] '
    'SELECT "tag", "dbid_uuid" FROM NOWHERE;'
)


@pytest.mark.config(
    UTAGS_YQL_WORKER_ENABLED=True,
    TAGS_YT_RESOURCE_RESTRICTIONS={
        '__default__': {'user_slots': 100, 'pool_name': 'tags'},
        'query1': {'user_slots': 200},
    },
)
@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_providers(
            [
                tags_tools.Provider(0, 'provider0', '', True),
                tags_tools.Provider(1, 'provider1', '', True),
            ],
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
                    syntax='SQLv1',
                ),
                yql_tools.Query(
                    'query1',
                    1,
                    ['tag0'],
                    '2018-08-30T12:34:56.0',
                    '2018-08-30T12:34:56.0',
                    _BASIC_QUERY,
                    yql_processing_method='yt_merge',
                    syntax='SQLv1',
                ),
            ],
        ),
        yql_tools.insert_snapshot(
            yql_tools.YtSnapshot(
                0,
                _OLD_SNAPSHOT_PATH,
                _HOUR_AGO,
                'fully_applied',
                query_syntax='SQLv1',
            ),
        ),
        yql_tools.insert_snapshot(
            yql_tools.YtSnapshot(
                1,
                _OLD_SNAPSHOT_PATH + '/',
                _HOUR_AGO,
                'fully_applied',
                query_syntax='SQLv1',
            ),
        ),
    ],
)
async def test_pragma(taxi_tags, mockserver):
    @mockserver.json_handler('/yql/api/v2/operations')
    def handler(request):
        assert request.args == {}

        requested_data = json.loads(request.get_data())
        query = requested_data['content']
        is_first_query = 'provider0' in query
        cpu_pragma = (
            f'PRAGMA yt.UserSlots = \"{100 if is_first_query else 200}\";\n'
        )
        assert cpu_pragma in query

        pool_pragma = 'PRAGMA yt.Pool = "tags"'
        assert pool_pragma in query

        response_yql = (
            '{{"id": "operation_id_{}", "status":' '"RUNNING"}}'
        ).format(handler.times_called)
        return mockserver.make_response(response_yql, 200)

    await tags_tools.activate_task(taxi_tags, 'yql-executer')

    assert handler.has_calls
