import datetime

import pytest

from tests_tags.tags import tags_tools
from tests_tags.tags import yql_tools

_NOW = datetime.datetime.now()
_HOUR = datetime.timedelta(hours=1)
_FOUR_DAYS_AGO = _NOW - datetime.timedelta(days=4)
_TWO_WEEKS_AGO = _NOW - datetime.timedelta(weeks=2)
_HOUR_AGO = _NOW - _HOUR


_YQL_TTLS = {'successful_queries_ttl': 3, 'failed_queries_ttl': 7}


def _verify_has_queries(query_ids, db):
    cursor = db.cursor()
    cursor.execute('SELECT operation_id FROM service.yql_operations;')
    rows = list(row[0] for row in cursor)
    assert sorted(query_ids) == sorted(rows)


@pytest.mark.config(
    TAGS_YQL_QUERIES_HISTORY_TTL=_YQL_TTLS,
    UTAGS_GARBAGE_CRON_SETTINGS={
        '__default__': {
            '__default__': {
                'enabled': True,
                'execute_timeout': 1000,
                'execution_count': 1,
                'limit': 4,
                'statement_timeout': 1000,
                'wait_time': 60,
            },
        },
    },
)
@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_entities([tags_tools.Entity(0, 'park', 'park')]),
        tags_tools.insert_providers([tags_tools.Provider.from_id(0)]),
        yql_tools.insert_queries([yql_tools.Query('query0', 0, ['tag0'])]),
        yql_tools.insert_operation(
            '0', 0, 'driver_license', 'failed', _TWO_WEEKS_AGO,
        ),
        yql_tools.insert_operation(
            '1', 0, 'driver_license', 'failed', _HOUR_AGO,
        ),
        yql_tools.insert_operation(
            '20', 0, 'driver_license', 'completed', _FOUR_DAYS_AGO,
        ),
        yql_tools.insert_operation(
            '21', 0, 'driver_license', 'completed', _FOUR_DAYS_AGO - _HOUR,
        ),
        yql_tools.insert_operation(
            '3', 0, 'driver_license', 'completed', _HOUR_AGO,
        ),
        yql_tools.insert_operation(
            '4', 0, 'driver_license', 'running', _TWO_WEEKS_AGO,
        ),
        yql_tools.insert_operation(
            '5', 0, 'driver_license', 'running', _HOUR_AGO,
        ),
    ],
)
async def test_yql_queries_deletion(taxi_tags, pgsql):
    await tags_tools.activate_task(taxi_tags, 'garbage-collector')
    _verify_has_queries(['1', '20', '3', '4', '5'], pgsql['tags'])
