import datetime
import socket

import pytest

from tests_tags.tags import tags_tools
from tests_tags.tags import yql_tools


_APPEND_POLICY = 'append'

_ENTITY_PARK = 'park'

_TEST_TAG_NAME = tags_tools.TagName(1000, 'tag_0')
_TEST_PROVIDER = tags_tools.Provider.from_id(1000, True)
_TEST_ENTITIES = [
    tags_tools.Entity(1000, 'park_0', entity_type=_ENTITY_PARK),
    tags_tools.Entity(1001, 'park_1', entity_type=_ENTITY_PARK),
]

_SNAPSHOTS_PATH = 'home/taxi/testsuite/features/tags/snapshots'

_NOW = datetime.datetime(2018, 10, 12, 16, 5, 00, 0)
_MINUTE_AGO = _NOW - datetime.timedelta(minutes=1)
_TWO_MINUTES_AGO = _NOW - datetime.timedelta(minutes=2)
_HALF_AN_HOUR_AGO = _NOW - datetime.timedelta(minutes=30)
_TWO_HOURS_AGO = _NOW - datetime.timedelta(hours=2)

_HOST = socket.gethostname()


@pytest.mark.now('2018-10-12T16:05:00+0000')
@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_tag_names(
            [
                tags_tools.TagName(2000, 'programmer'),
                tags_tools.TagName(2001, 'manager'),
            ],
        ),
        tags_tools.insert_providers(
            [
                tags_tools.Provider.from_id(1000, True),
                tags_tools.Provider.from_id(1001, False),
                tags_tools.Provider.from_id(1002, True),
            ],
        ),
        tags_tools.insert_entities(
            [
                # No tags
                tags_tools.Entity(3000, 'LICENSE', 'driver_license'),
                # programmer, manager tags
                tags_tools.Entity(3001, 'CAR_NUMBER', 'car_number'),
                # programmer tag
                tags_tools.Entity(3002, 'PARK_ID', 'park'),
            ],
        ),
        tags_tools.insert_tags(
            [
                # outdated programmer tag for LICENSE entity
                tags_tools.Tag(
                    2000,
                    1000,
                    3000,
                    ttl=datetime.datetime(2018, 1, 1, 10, 0, 0),
                ),
                # programmer tag for LICENSE entity (disabled provider)
                tags_tools.Tag(2000, 1001, 3000),
                # programmer tag for CAR_NUMBER entity
                tags_tools.Tag(2000, 1000, 3001),
                # programmer tag for CAR_NUMBER entity (disabled provider)
                tags_tools.Tag(2000, 1001, 3001),
                # programmer tag for CAR_NUMBER entity
                tags_tools.Tag(2000, 1002, 3001),
                # programmer tag for PARK_ID entity
                tags_tools.Tag(2000, 1000, 3002),
                # manager tag for CAR_NUMBER entity
                tags_tools.Tag(2001, 1000, 3001),
            ],
        ),
    ],
)
async def test_tags_count_monitor(taxi_tags, taxi_tags_monitor):
    await tags_tools.activate_task(taxi_tags, 'tags-count-monitor@' + _HOST)

    metrics = await taxi_tags_monitor.get_metrics()
    assert metrics['tags-count-by-providers'] == {
        'name_1000': 3,
        'name_1002': 1,
    }
    assert metrics['entities-count-by-types'] == {'car_number': 1, 'park': 1}


@pytest.mark.now('2018-10-12T16:05:00+0000')
@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_providers([_TEST_PROVIDER]),
        tags_tools.insert_service_providers(
            [(_TEST_PROVIDER.provider_id, ['reposition'], 'base')],
        ),
    ],
)
async def test_queue_size_monitor(taxi_tags, taxi_tags_monitor):
    query = (
        f'v1/upload?provider_id={_TEST_PROVIDER.name}&'
        f'confirmation_token=token_0'
    )
    tags = [
        tags_tools.Tag.get_data(_TEST_TAG_NAME.name, _TEST_ENTITIES[0].value),
        tags_tools.Tag.get_data(_TEST_TAG_NAME.name, _TEST_ENTITIES[1].value),
    ]
    data = {
        'merge_policy': _APPEND_POLICY,
        'entity_type': _ENTITY_PARK,
        'tags': tags,
    }

    response = await taxi_tags.post(query, data)
    assert response.status_code == 200

    await tags_tools.activate_task(taxi_tags, 'customs-monitor@' + _HOST)

    metrics = await taxi_tags_monitor.get_metrics()
    assert metrics['customs_queue_size']['size'] == 2


@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_providers(
            [
                tags_tools.Provider(0, 'provider0', '', True),
                tags_tools.Provider(1, 'provider1', '', True),
                tags_tools.Provider(2, 'provider2', '', True),
                tags_tools.Provider(3, 'provider3', '', False),
                tags_tools.Provider(4, 'provider4', '', False),
            ],
        ),
        yql_tools.insert_queries(
            [
                yql_tools.Query(
                    'query0', 0, ['tag0'], _NOW, _NOW, 'text', period=3600,
                ),
                yql_tools.Query(
                    'query1', 1, ['tag0'], _NOW, _NOW, 'text', period=3600,
                ),
                yql_tools.Query(
                    'query2', 2, ['tag0'], _NOW, _NOW, 'text', period=300,
                ),
                yql_tools.Query(
                    'query3', 3, ['tag0'], _NOW, _NOW, 'text', period=300,
                ),
                yql_tools.Query(
                    'query4', 4, ['tag0'], _NOW, _NOW, 'text', period=3600,
                ),
            ],
        ),
        yql_tools.insert_operation(
            'operation0_0', 0, 'dbid_uuid', 'completed', _TWO_MINUTES_AGO,
        ),
        yql_tools.insert_operation(
            'operation0_1', 0, 'dbid_uuid', 'failed', _MINUTE_AGO,
        ),
        yql_tools.insert_operation(
            'operation0_2', 0, 'dbid_uuid', 'running', _NOW,
        ),
        yql_tools.insert_operation(
            'operation1_0', 1, 'dbid_uuid', 'completed', _MINUTE_AGO,
        ),
        yql_tools.insert_operation(
            'operation1_1', 1, 'dbid_uuid', 'completed', _NOW,
        ),
        # last query start was too long ago
        # (period = 5 minutes, last execution was 30 minutes ago)
        yql_tools.insert_operation(
            'operation2_0', 2, 'dbid_uuid', 'completed', _HALF_AN_HOUR_AGO,
        ),
        # provider is disabled, so result is not considered
        yql_tools.insert_operation(
            'operation3_0', 3, 'dbid_uuid', 'failed', _HALF_AN_HOUR_AGO,
        ),
        # operation executed too long ago, result is not considered
        yql_tools.insert_operation(
            'operation4_0', 4, 'dbid_uuid', 'failed', _TWO_HOURS_AGO,
        ),
    ],
)
@pytest.mark.now(_NOW.isoformat())
async def test_yql_monitor(taxi_tags, taxi_tags_monitor):
    await tags_tools.activate_task(taxi_tags, 'yql-monitor@' + _HOST)

    metrics = await taxi_tags_monitor.get_metrics()
    assert metrics['queries_status'] == {
        'running': 1,
        'completed': 2,
        'failed': 1,
        'aborted': 0,
        'downloading': 0,
        'prepared': 0,
    }
    assert metrics['queries_delay'] == {'provider2': 25}
    assert metrics['max_query_delay'] == {'size': 25}


@pytest.mark.yt(
    schemas=[
        {
            'path': f'//{_SNAPSHOTS_PATH}/yt_table_{index}',
            'attributes': {'schema': [{'name': 'id', 'type': 'string'}]},
        }
        for index in range(7)
    ],
)
async def test_yt_monitor(
        taxi_tags, taxi_tags_monitor, yt_client, yt_apply_force,
):
    await tags_tools.activate_task(taxi_tags, 'yt-monitor@' + _HOST)

    metrics = await taxi_tags_monitor.get_metrics()
    assert metrics['yt_tables_count'] == {'yt_tables_count': 7}
