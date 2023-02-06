import datetime
from typing import List

import pytest

from tests_tags.tags import tags_tools as tools


_CUSTOM_OFFICER = 'customs-officer'

_ENTITY_DRIVER_LICENSE = 'driver_license'
_ENTITY_UDID = 'udid'

_TEST_PROVIDERS = [
    tools.Provider.from_id(1000, True),
    tools.Provider.from_id(1001, False),
    tools.Provider.from_id(1002, True),
]

_TEST_ENTITIES = [
    tools.Entity(1000, 'driver_license_0', entity_type=_ENTITY_DRIVER_LICENSE),
    tools.Entity(1001, 'driver_license_1', entity_type=_ENTITY_DRIVER_LICENSE),
    tools.Entity(1002, 'udid_0', entity_type=_ENTITY_UDID),
]

_TEST_TAG_NAMES = [
    tools.TagName(1000, 'tag_0'),
    tools.TagName(1001, 'tag_1'),
    tools.TagName(1002, 'tag_2'),
]

_TEST_TOPICS = [
    tools.Topic(2000, 'topic_0', False),
    tools.Topic(2001, 'topic_1', True),
    tools.Topic(2002, 'topic_2', False),
]

_PROVIDER_IDS = [1000, 1001, 1002]

_INFINITY = 'infinity'
_NOW = datetime.datetime(2019, 8, 29, 10, 54, 9)
_TAG_LIFETIME = datetime.timedelta(days=1)
_TAG_OUTDATED = _NOW - _TAG_LIFETIME
#  Test tag livetime in seconds
_TEST_DURATION = 3600
#  Expected tag ttl
_TEST_TTL = _NOW + datetime.timedelta(seconds=_TEST_DURATION)


def _tag(
        name_index: int,
        provider_index: int,
        entity_index: int,
        updated: datetime.datetime = None,
        ttl: datetime.datetime = None,
        entity_type: str = None,
):
    return tools.Tag(
        name_id=_TEST_TAG_NAMES[name_index].tag_name_id,
        provider_id=_TEST_PROVIDERS[provider_index].provider_id,
        entity_id=_TEST_ENTITIES[entity_index].entity_id,
        updated=updated,
        ttl=ttl or _INFINITY,
        entity_type=entity_type,
    )


_TEST_TAGS = [
    _tag(0, 0, 0, _NOW, entity_type=_ENTITY_DRIVER_LICENSE),
    _tag(1, 0, 0, _NOW, entity_type=_ENTITY_DRIVER_LICENSE),
    _tag(2, 0, 0, _NOW, entity_type=_ENTITY_DRIVER_LICENSE),
    _tag(0, 0, 1, _NOW, entity_type=_ENTITY_DRIVER_LICENSE),
    _tag(1, 0, 1, _NOW, entity_type=_ENTITY_DRIVER_LICENSE),
    _tag(2, 0, 1, _NOW, entity_type=_ENTITY_DRIVER_LICENSE),
    _tag(0, 1, 0, _NOW, entity_type=_ENTITY_DRIVER_LICENSE),
    _tag(1, 1, 0, _NOW, entity_type=_ENTITY_DRIVER_LICENSE),
    _tag(2, 1, 0, _NOW, entity_type=_ENTITY_DRIVER_LICENSE),
    _tag(0, 1, 1, _NOW, entity_type=_ENTITY_DRIVER_LICENSE),
    _tag(1, 1, 1, _NOW, entity_type=_ENTITY_DRIVER_LICENSE),
    _tag(2, 1, 1, _NOW, entity_type=_ENTITY_DRIVER_LICENSE),
    _tag(0, 2, 0, _NOW, entity_type=_ENTITY_DRIVER_LICENSE),
    _tag(1, 2, 0, _NOW, entity_type=_ENTITY_DRIVER_LICENSE),
    _tag(2, 2, 0, _NOW, entity_type=_ENTITY_DRIVER_LICENSE),
    _tag(0, 2, 1, _NOW, entity_type=_ENTITY_DRIVER_LICENSE),
    _tag(1, 2, 1, _NOW, entity_type=_ENTITY_DRIVER_LICENSE),
    _tag(2, 2, 1, _NOW, entity_type=_ENTITY_DRIVER_LICENSE),
    _tag(0, 0, 2, _NOW, entity_type=_ENTITY_UDID),
    _tag(1, 0, 2, _NOW, entity_type=_ENTITY_UDID),
    _tag(2, 0, 2, _NOW, entity_type=_ENTITY_UDID),
    _tag(0, 1, 2, _NOW, entity_type=_ENTITY_UDID),
    _tag(1, 1, 2, _NOW, entity_type=_ENTITY_UDID),
    _tag(2, 1, 2, _NOW, entity_type=_ENTITY_UDID),
    _tag(0, 2, 2, _NOW, entity_type=_ENTITY_UDID),
    _tag(1, 2, 2, _NOW, entity_type=_ENTITY_UDID),
    _tag(2, 2, 2, _NOW, entity_type=_ENTITY_UDID),
]


def verify_tags(expected_tags: List[tools.Tag], db):
    cursor = db.cursor()
    cursor.execute(
        'SELECT tag_name_id, provider_id, entity_id, '
        'updated, ttl, revision, entity_type FROM '
        'state.tags',
    )

    # Some time interval big enough to cover all the tests gone
    delta_time = datetime.timedelta(minutes=30)

    found_count = 0
    rows = list(row for row in cursor)
    for row in rows:
        parsed_tag = tools.Tag(
            name_id=row[0],
            provider_id=row[1],
            entity_id=row[2],
            updated=row[3],
            ttl=row[4],
            # 5 is a revision as for v17 scheme
            entity_type=row[6],
        )

        expected_tag = parsed_tag.find_in(expected_tags)
        if expected_tag:
            #  tools.Tag is still active (it was expected)
            found_count += 1
            if expected_tag.ttl == _INFINITY:
                assert parsed_tag.ttl == datetime.datetime(
                    9999, 12, 31, 23, 59, 59, 999999,
                )
            else:
                assert parsed_tag.ttl - expected_tag.ttl < delta_time
            assert parsed_tag.updated - expected_tag.updated < delta_time
            assert parsed_tag.entity_type == expected_tag.entity_type
        else:
            #  tools.Tag was removed (ttl set to now())
            assert parsed_tag.ttl - _NOW < delta_time
            assert parsed_tag.updated - _NOW < delta_time
    assert len(expected_tags) == found_count


@pytest.mark.nofilldb()
@pytest.mark.parametrize(
    'expected_code, tool_name, entity_type, providers, instance,'
    ' expected_tags',
    [
        pytest.param(
            200,
            'remove-tags-for-entity-type',
            'driver_license',
            _PROVIDER_IDS,
            'tags',
            _TEST_TAGS[18:],
            id='existing_entity_type',
        ),
        pytest.param(
            200,
            'remove-tags-for-entity-type',
            'clid_uuid',
            _PROVIDER_IDS,
            'tags',
            _TEST_TAGS,
            id='missing_entity_type',
        ),
        pytest.param(
            200,
            'remove-tags-for-entity-type',
            'driver_license',
            _PROVIDER_IDS[0:1],
            'tags',
            _TEST_TAGS[6:],
            id='specific_providers',
        ),
        pytest.param(
            400,
            'remove-tags-for-entity-type',
            'driver_license',
            _PROVIDER_IDS[0:1],
            'passenger-tags',
            _TEST_TAGS,
            id='missing_config',
        ),
        pytest.param(
            404,
            'remove-tags',
            'phone',
            _PROVIDER_IDS,
            'tags',
            _TEST_TAGS,
            id='missing_tool',
        ),
    ],
)
@pytest.mark.pgsql(
    'tags',
    queries=[
        tools.insert_providers(_TEST_PROVIDERS[:3]),
        tools.insert_tag_names(_TEST_TAG_NAMES[:3]),
        tools.insert_entities(_TEST_ENTITIES[:3]),
        tools.insert_tags(_TEST_TAGS),
        tools.insert_topics(_TEST_TOPICS),
    ],
)
@pytest.mark.now(_NOW.isoformat())
async def test_tool_remove_tags_for_entity_type(
        taxi_tags,
        pgsql,
        expected_code: int,
        expected_tags: List[tools.Tag],
        tool_name: str,
        taxi_config,
        entity_type,
        providers,
        instance,
):
    taxi_config.set_values(
        dict(
            TAGS_TOOLS_PARAMETERS={
                '__default__': {},
                instance: {
                    'remove_tags_for_entity_type': {
                        'entity_type': entity_type,
                        'providers': providers,
                        'chunk_size': 512,
                    },
                },
            },
        ),
    )
    query = f'v1/tools/{tool_name}'
    response = await taxi_tags.post(query)
    assert response.status_code == expected_code
    await tools.activate_task(taxi_tags, _CUSTOM_OFFICER)
    verify_tags(expected_tags, pgsql['tags'])
