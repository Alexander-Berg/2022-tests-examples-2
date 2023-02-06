# pylint: disable=C1801
import datetime

import pytest

from tests_tags.tags import tags_select
from tests_tags.tags import tags_tools
from tests_tags.tags import yql_tools

_NOW = datetime.datetime.now()
_HOUR_AFTER = _NOW + datetime.timedelta(hours=1)
_A_LITTLE_BIT_LATER_THAN_AN_HOUR_AFTER = _HOUR_AFTER + datetime.timedelta(
    minutes=1,
)
_A_LITTLE_BIT_EARLIER_THAN_AN_HOUR_AFTER = _HOUR_AFTER - datetime.timedelta(
    minutes=1,
)
_HOUR_BEFORE = _NOW - datetime.timedelta(hours=1)


def _get_operations(db):
    return tags_select.select_table_named(
        'service.yql_operations', 'operation_id', db,
    )


@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_providers(
            [
                #  basic
                tags_tools.Provider(1000, 'provider1000', '', True),
                #  disabled provider
                tags_tools.Provider(1001, 'provider1001', '', False),
                #  disabled query
                tags_tools.Provider(1002, 'provider1002', '', True),
            ],
        ),
        yql_tools.insert_queries(
            [
                yql_tools.Query(
                    'query1000',
                    1000,
                    ['tag0'],
                    '2018-08-30T12:34:56.0',
                    '2018-08-30T12:34:56.0',
                    custom_execution_time=_HOUR_AFTER.isoformat(),
                ),
                yql_tools.Query(
                    'query1001',
                    1001,
                    ['tag0'],
                    '2018-08-30T12:34:56.0',
                    '2018-08-30T12:34:56.0',
                    custom_execution_time=_HOUR_AFTER.isoformat(),
                ),
                yql_tools.Query(
                    'query1002',
                    1002,
                    ['tag0'],
                    '2018-08-30T12:34:56.0',
                    '2018-08-30T12:34:56.0',
                    enabled=False,
                    custom_execution_time=_HOUR_AFTER.isoformat(),
                ),
            ],
        ),
        # snapshots are needed, because if they exist,
        # yql-executer doesn't go to YT
        yql_tools.insert_snapshot(
            yql_tools.YtSnapshot(1000, 's0', _NOW, 'fully_applied'),
        ),
        yql_tools.insert_snapshot(
            yql_tools.YtSnapshot(1001, 's1', _NOW, 'fully_applied'),
        ),
        yql_tools.insert_snapshot(
            yql_tools.YtSnapshot(1002, 's2', _NOW, 'fully_applied'),
        ),
    ],
)
@pytest.mark.config(UTAGS_YQL_WORKER_ENABLED=True)
@pytest.mark.now(_NOW.isoformat())
async def test_basic(taxi_tags, pgsql, mocked_time, mockserver):
    @mockserver.json_handler('/yql/api/v2/operations')
    def handler(_):
        response = '{{"id": "operation_id_{}", "status": "IDLE"}}'.format(
            handler.times_called,
        )
        return mockserver.make_response(response, 200)

    db = pgsql['tags']

    mocked_time.set(_A_LITTLE_BIT_EARLIER_THAN_AN_HOUR_AFTER)
    await taxi_tags.tests_control()
    await tags_tools.activate_task(taxi_tags, 'yql-executer')
    assert len(_get_operations(db)) == 0

    mocked_time.set(_A_LITTLE_BIT_LATER_THAN_AN_HOUR_AFTER)
    await taxi_tags.tests_control()
    await tags_tools.activate_task(taxi_tags, 'yql-executer')
    operations = _get_operations(db)
    assert len(operations) == 1
    assert operations[0]['provider_id'] == 1000


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
                    'query',
                    0,
                    ['tag'],
                    _NOW,
                    _NOW,
                    'query',
                    custom_execution_time=_HOUR_BEFORE.isoformat(),
                ),
            ],
        ),
        yql_tools.insert_operation(
            'operation', 0, 'dbid_uuid', 'running', _NOW,
        ),
    ],
)
@pytest.mark.now(_NOW.isoformat())
async def test_custom_execution_time_while_running(taxi_tags, pgsql):
    await tags_tools.activate_task(taxi_tags, 'yql-executer')
    operations = _get_operations(pgsql['tags'])
    assert len(operations) == 1
    assert operations[0]['status'] == 'running'
