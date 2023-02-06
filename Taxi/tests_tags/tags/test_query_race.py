# pylint: disable=C1801
import datetime

import pytest

from tests_tags.tags import tags_select
from tests_tags.tags import tags_tools
from tests_tags.tags import yql_tools

_NOW = datetime.datetime.now()
_TASK_TICKET = 'TASKTICKET-1234'

_QUERY = yql_tools.Query(
    'query',
    0,
    ['tag0'],
    _NOW,
    _NOW,
    '[_INSERT_HERE_] query',
    ticket=_TASK_TICKET,
    tags_limit=100,
)
_LOGIN = 'password'


def _check_yql_operations_empty(db):
    rows = tags_select.select_table_named(
        'service.yql_operations', 'provider_id', db,
    )
    assert len(rows) == 0


@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_tag_names([tags_tools.TagName(0, 'tag0')]),
        tags_tools.insert_providers(
            [tags_tools.Provider(0, 'provider0', '', True)],
        ),
        tags_tools.insert_entities(
            [
                tags_tools.Entity(0, 'license0'),
                tags_tools.Entity(1, 'license1'),
                tags_tools.Entity(2, 'license2'),
            ],
        ),
        tags_tools.insert_tags(
            [tags_tools.Tag(0, 0, 0), tags_tools.Tag(0, 0, 1)],
        ),
        yql_tools.insert_queries([_QUERY]),
    ],
)
@pytest.mark.config(UTAGS_YQL_WORKER_ENABLED=True)
async def test_race(taxi_tags, pgsql):
    await yql_tools.change_query_active_state(taxi_tags, _QUERY, _LOGIN, False)
    await yql_tools.change_query_active_state(taxi_tags, _QUERY, _LOGIN, True)

    await tags_tools.activate_task(taxi_tags, 'yql-executer')
    # verify, that operation has not been started
    _check_yql_operations_empty(pgsql['tags'])
