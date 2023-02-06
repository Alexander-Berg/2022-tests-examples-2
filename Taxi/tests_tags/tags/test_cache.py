import datetime

import pytest

from testsuite.utils import ordered_object

from tests_tags.tags import tags_tools

_NOW = datetime.datetime(2019, 8, 29, 10, 54, 9)

_ENTITY_USER_PHONE = 'user_phone_id'
_ENTITY_CAR_NUMBER = 'car_number'
_ENTITY_PARK = 'park'

_TEST_TAG_NAMES = [
    tags_tools.TagName(1000, 'tag_0'),
    tags_tools.TagName(1001, 'tag_1'),
    tags_tools.TagName(1002, 'tag_2'),
]

_TEST_PROVIDERS = [
    tags_tools.Provider.from_id(1000, True),
    tags_tools.Provider.from_id(1001, False),
    tags_tools.Provider.from_id(1, True),
]

_TEST_ENTITIES = [
    tags_tools.Entity(1000, 'phone_0', entity_type=_ENTITY_USER_PHONE),
    tags_tools.Entity(1001, 'phone_1', entity_type=_ENTITY_USER_PHONE),
    tags_tools.Entity(1002, 'phone_2', entity_type=_ENTITY_USER_PHONE),
    tags_tools.Entity(1, 'phone_3', entity_type=_ENTITY_USER_PHONE),
    tags_tools.Entity(1003, 'phone_0', entity_type=_ENTITY_PARK),
    tags_tools.Entity(1004, 'park_1', entity_type=_ENTITY_PARK),
]


def _tag(
        name_index: int,
        provider_index: int,
        entity_index: int,
        updated=None,
        ttl=None,
        entity_type=None,
):
    return tags_tools.Tag(
        name_id=_TEST_TAG_NAMES[name_index].tag_name_id,
        provider_id=_TEST_PROVIDERS[provider_index].provider_id,
        entity_id=_TEST_ENTITIES[entity_index].entity_id,
        updated=updated,
        ttl=ttl or 'infinity',
        entity_type=entity_type or 'udid',
    )


def _delete_tags(revision: int):
    return 'DELETE FROM state.tags WHERE revision <= {revision};'.format(
        revision=revision,
    )


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.pgsql(
    'tags', queries=['select setval(\'state.tags_revision\', 1000000000000);'],
)
@pytest.mark.nofilldb()
async def test_match_tags_cache(taxi_tags, pgsql):
    data = {
        'entities': [
            {'id': item.value, 'type': item.type} for item in _TEST_ENTITIES
        ],
    }

    queries = [
        tags_tools.insert_tag_names(_TEST_TAG_NAMES[:2]),
        tags_tools.insert_providers(_TEST_PROVIDERS[:2]),
        tags_tools.insert_entities(_TEST_ENTITIES[:3]),
        tags_tools.insert_tags(
            [
                _tag(0, 0, 0, _NOW),
                _tag(1, 0, 1, _NOW),
                _tag(0, 1, 2, _NOW),
                _tag(1, 1, 1, _NOW),
            ],
        ),
    ]
    tags_tools.apply_queries(pgsql['tags'], queries)

    expected_tags = [[0], [1], [], [], [], []]
    expected_result = {
        'entities': [
            {
                'id': item.value,
                'type': item.type,
                'tags': [
                    _TEST_TAG_NAMES[i].name for i in expected_tags[index]
                ],
            }
            for index, item in enumerate(_TEST_ENTITIES)
        ],
    }

    await taxi_tags.invalidate_caches()
    response = await taxi_tags.post('v1/match', data)
    assert response.status_code == 200
    response_data = response.json()
    ordered_object.assert_eq(response_data, expected_result, ['entities.tags'])

    setup_revision = tags_tools.get_latest_revision(pgsql['tags'])
    queries = [
        tags_tools.insert_tag_names(_TEST_TAG_NAMES[2:]),
        tags_tools.insert_providers(_TEST_PROVIDERS[2:]),
        tags_tools.insert_entities(_TEST_ENTITIES[3:]),
        tags_tools.insert_tags(
            [
                _tag(2, 0, 4, _NOW),
                _tag(2, 0, 0, _NOW),
                _tag(1, 2, 3, _NOW),
                _tag(1, 2, 5, _NOW),
                _tag(2, 2, 5, _NOW),
            ],
        ),
        # delete previous tags to make sure that partial-update works
        _delete_tags(setup_revision),
    ]
    tags_tools.apply_queries(pgsql['tags'], queries)

    expected_tags = [[0, 2], [1], [], [1], [2], [2, 1]]
    expected_result = {
        'entities': [
            {
                'id': item.value,
                'type': item.type,
                'tags': [
                    _TEST_TAG_NAMES[i].name for i in expected_tags[index]
                ],
            }
            for index, item in enumerate(_TEST_ENTITIES)
        ],
    }

    await taxi_tags.invalidate_caches(clean_update=False)
    response = await taxi_tags.post('v1/match', data)
    assert response.status_code == 200
    response_data = response.json()
    ordered_object.assert_eq(response_data, expected_result, ['entities.tags'])
