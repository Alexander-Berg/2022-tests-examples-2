# pylint: disable=C0302
import datetime
from typing import Any
from typing import Optional

# pylint: disable=redefined-outer-name
import pytest
# pylint: disable=import-error
from yandex.taxi.tags.index import Response

from tests_tags.tags import constants
from tests_tags.tags import tags_tools


_CONTENT_TYPE = 'application/x-flatbuffers'

_PROVIDER_ACTIVE = 'active_provider'
_PROVIDER_DISABLED = 'disabled_provider'
_PROVIDER_UNSTABLE = 'unstable_provider'

_CLEAN_UPDATE = None

_EXISTING_TAGS = ['tag0', 'tag1', 'tag2']
_EXISTING_ENTITIES = ['PARK_CAR0', 'PARK_CAR1', 'PARK_CAR2', 'udid3', 'udid4']

_INITIAL_INDEX = {
    'park_car_id': {
        'PARK_CAR0': {'tag0'},
        'PARK_CAR1': {'tag0'},
        'PARK_CAR2': {'tag2'},
    },
    'udid': {},
    'car_number': {},
}

_INITIAL_INDEX_PARK_CAR_ID = {
    'park_car_id': {
        'PARK_CAR0': {'tag0'},
        'PARK_CAR1': {'tag0'},
        'PARK_CAR2': {'tag2'},
    },
}
_EMPTY_INDEX_PARK_CAR_ID: dict = {'park_car_id': {}}

_INITIAL_INDEX_TOPIC = {
    'park_car_id': {
        'PARK_CAR0': {'tag0'},
        'PARK_CAR1': {'tag0'},
        'PARK_CAR2': set(),
    },
    'udid': {},
    'car_number': {},
}
_EMPTY_INITIAL_INDEX_ = {
    'park_car_id': {
        'PARK_CAR0': set(),
        'PARK_CAR1': set(),
        'PARK_CAR2': set(),
    },
    'udid': {},
    'car_number': {},
}
_INITIAL_INDEX_PARK_CAR_ID_TOPIC = {
    'park_car_id': {
        'PARK_CAR0': {'tag0'},
        'PARK_CAR1': {'tag0'},
        'PARK_CAR2': set(),
    },
}

_UNLIMITED = 1024

_DEFAULT_QUERIES: Any = [
    tags_tools.insert_tag_names(
        [
            tags_tools.TagName(2000, 'programmer'),
            tags_tools.TagName(2001, 'manager'),
        ],
    ),
    tags_tools.insert_topics(
        [
            tags_tools.Topic(4000, 'topic0', False),
            tags_tools.Topic(4001, 'topic1', False),
        ],
    ),
    tags_tools.insert_relations([tags_tools.Relation(2000, 4000)]),
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
            tags_tools.Entity(3000, 'PARK_CAR', 'park_car_id'),
            # programmer, manager tags
            tags_tools.Entity(3001, 'CAR_NUMBER', 'car_number'),
            # programmer tag
            tags_tools.Entity(3002, 'PARK_ID', 'park'),
        ],
    ),
    tags_tools.insert_tags(
        [
            # outdated programmer tag for PARK_CAR entity
            tags_tools.Tag(
                2000,
                1000,
                3000,
                ttl=datetime.datetime(2018, 1, 1, 10, 0, 0),
                entity_type='park_car_id',
            ),
            # programmer tag for PARK_CAR entity (disabled provider)
            tags_tools.Tag(2000, 1001, 3000, entity_type='park_car_id'),
            # programmer tag for CAR_NUMBER entity
            tags_tools.Tag(2000, 1000, 3001, entity_type='car_number'),
            # programmer tag for CAR_NUMBER entity (disabled provider)
            tags_tools.Tag(2000, 1001, 3001, entity_type='car_number'),
            # programmer tag for CAR_NUMBER entity
            tags_tools.Tag(2000, 1002, 3001, entity_type='car_number'),
            # programmer tag for PARK_ID entity
            tags_tools.Tag(2000, 1000, 3002, entity_type='park'),
            # manager tag for CAR_NUMBER entity
            tags_tools.Tag(2001, 1000, 3001, entity_type='car_number'),
        ],
    ),
]


@pytest.fixture(scope='session')
def regenerate_config_hooks(regenerate_stat_client_config):
    return [regenerate_stat_client_config]


def _decode_response(response):
    assert response.status_code == 200
    assert response.headers['Content-Type'] == _CONTENT_TYPE

    data = response.content
    root = Response.Response.GetRootAsResponse(data, 0)

    indexes = dict()
    for en_it in range(0, root.EntitiesLength()):
        entities = root.Entities(en_it)
        entity_type = entities.EntityType().decode('utf-8')
        assert entity_type not in indexes

        items = dict()
        for item_it in range(0, entities.ItemsLength()):
            entity_tags = entities.Items(item_it)
            name = entity_tags.Name().decode('utf-8')
            tags = set()
            for tag_it in range(0, entity_tags.TagsLength()):
                tags.add(entity_tags.Tags(tag_it).decode('utf-8'))
            items[name] = tags

        indexes[entity_type] = items

    return indexes, root.Revision(), root.HasMoreTags(), root.PollingDelayMs()


async def _perform_index_request(
        taxi_tags,
        revision_from: int,
        entity_types: list,
        limit: int,
        topics: Optional[list] = None,
):
    data = {
        'range': {'newer_than': revision_from, 'limit': limit},
        'entity_types': list(entity_types),
    }
    if topics is not None:
        data['topics'] = topics

    return await taxi_tags.post('v2/index', data)


async def _call_provider_activation_status(taxi_tags, provider, activate):
    query = 'v1/providers/activation_status?id=%s' % provider
    response = await taxi_tags.put(query, {'activate': activate})
    assert response.status_code == 200
    await tags_tools.activate_task(taxi_tags, 'tags-updater')
    await tags_tools.activate_task(taxi_tags, 'customs-officer')


async def _perform_v1_upload(taxi_tags, provider, upload_data):
    query = 'v1/upload?provider_id={0}&confirmation_token=token_{0}'.format(
        provider,
    )
    response = await taxi_tags.post(query, upload_data)
    assert response.status_code == 200
    await tags_tools.activate_task(taxi_tags, 'customs-officer')


@pytest.mark.pgsql('tags', files=['pg_tags_initial.sql'])
@pytest.mark.parametrize(
    'revision_from, entity_types, limit, expected_code, expected_entities',
    [
        (0, ['park_car_id', 'udid', 'car_number'], 10, 200, _INITIAL_INDEX),
        (1, ['park_car_id', 'udid', 'car_number'], 10, 200, _INITIAL_INDEX),
        # negative limit
        (1, ['park_car_id', 'udid', 'car_number'], -10, 400, None),
        # unknown entity type
        (1, ['udid', 'unknown'], 10, 400, None),
        # limit is zero
        (1, ['park_car_id', 'udid', 'car_number'], 0, 400, None),
    ],
)
@pytest.mark.nofilldb()
async def test_request(
        taxi_tags,
        revision_from,
        entity_types,
        limit,
        expected_code,
        expected_entities,
):
    response = await _perform_index_request(
        taxi_tags, revision_from, entity_types, limit,
    )

    assert response.status_code == expected_code
    if expected_code == 200:
        entities, revision, has_more_tags, _ = _decode_response(response)
        assert revision > 0
        assert not has_more_tags
        assert entities == expected_entities


@pytest.mark.pgsql('tags', files=['pg_tags_initial.sql'])
@pytest.mark.parametrize(
    'revision_from, topics, expected_code, expected_entities',
    [
        (0, ['topic0', 'topic1'], 200, _INITIAL_INDEX),
        (0, ['topic0'], 200, _INITIAL_INDEX_TOPIC),
        (0, ['topic2'], 200, _EMPTY_INITIAL_INDEX_),
        (0, ['unknown'], 200, _EMPTY_INITIAL_INDEX_),
        pytest.param(0, [], 400, None, id='empty_topics_list_error'),
        pytest.param(1, None, 200, _INITIAL_INDEX, id='next_revision'),
        pytest.param(0, ['non_cached'], 400, None, id='non_cached_error'),
        pytest.param(0, ['topic0', 'non_cached'], 400, None, id='mixed_cache'),
    ],
)
@pytest.mark.config(
    TAGS_TOPICS_POLICY={'__default__': 'cached', 'non_cached': 'non_cached'},
)
@pytest.mark.nofilldb()
async def test_request_topics(
        taxi_tags, revision_from, topics, expected_code, expected_entities,
):
    response = await _perform_index_request(
        taxi_tags,
        revision_from=revision_from,
        entity_types=['park_car_id', 'udid', 'car_number'],
        limit=10,
        topics=topics,
    )

    assert response.status_code == expected_code
    if expected_code == 200:
        entities, revision, has_more_tags, _ = _decode_response(response)
        assert revision > 0
        assert not has_more_tags
        assert entities == expected_entities


@pytest.mark.pgsql('tags')
@pytest.mark.parametrize(
    'revision_from, entity_types, expected_code',
    [(0, ['udid'], 200), (1000, ['car_number', 'personal_phone_id'], 200)],
)
@pytest.mark.nofilldb()
async def test_empty_cache(
        taxi_tags, revision_from, entity_types, expected_code,
):
    response = await _perform_index_request(
        taxi_tags, revision_from, entity_types, 1,
    )

    assert response.status_code == expected_code
    #  this doesn't work since knows about json only
    entities, revision, has_more_tags, _ = _decode_response(response)

    assert revision >= revision_from
    assert not has_more_tags
    assert entities == {entity_type: {} for entity_type in entity_types}


@pytest.mark.pgsql('tags', queries=_DEFAULT_QUERIES)
@pytest.mark.parametrize(
    'entity_types, newer_than_delta, limit, expected_entities',
    [
        # No tags for udid in data
        (['udid'], _CLEAN_UPDATE, _UNLIMITED, {'udid': {}}),
        (
            ['udid', 'park'],
            _CLEAN_UPDATE,
            _UNLIMITED,
            {
                'park': {'PARK_ID': {'programmer'}},
                'udid': {},  # Empty tags for the type
            },
        ),
        # All existing tags - clean
        (
            ['park_car_id', 'car_number', 'park'],
            _CLEAN_UPDATE,
            _UNLIMITED,
            {
                'car_number': {'CAR_NUMBER': {'manager', 'programmer'}},
                'park_car_id': {
                    # this would never be sent in v1/match
                    'PARK_CAR': set(),
                },
                'park': {'PARK_ID': {'programmer'}},
            },
        ),
        # All existing tags - partial
        (
            ['park_car_id', 'car_number', 'park'],
            -100500,  # Since the beginning
            _UNLIMITED,
            {
                'car_number': {'CAR_NUMBER': {'manager', 'programmer'}},
                'park_car_id': {
                    # this would never be send in v1/index
                    'PARK_CAR': set(),
                },
                'park': {'PARK_ID': {'programmer'}},
            },
        ),
        # Recent updates - partial
        (
            ['park_car_id', 'car_number', 'park'],
            0,  # Recent updates (nothing)
            _UNLIMITED,
            {'car_number': {}, 'park_car_id': {}, 'park': {}},
        ),
        (
            ['park_car_id', 'car_number'],
            _CLEAN_UPDATE,
            1,
            {'car_number': {}, 'park_car_id': {'PARK_CAR': set()}},
        ),
        (
            ['park_car_id', 'car_number'],
            _CLEAN_UPDATE,
            3,
            {
                'car_number': {'CAR_NUMBER': {'manager', 'programmer'}},
                'park_car_id': {
                    # this would never be sent in v1/match
                    'PARK_CAR': set(),
                },
            },
        ),
    ],
)
@pytest.mark.nofilldb()
async def test_clean_update(
        taxi_tags,
        entity_types,
        newer_than_delta,
        limit,
        expected_entities,
        pgsql,
):
    latest_revision = tags_tools.get_latest_revision(pgsql['tags'])
    newer_than = (
        0
        if newer_than_delta is None
        else max(latest_revision + newer_than_delta, 0)
    )
    response = await _perform_index_request(
        taxi_tags, newer_than, entity_types, limit,
    )
    entities, revision, has_more_tags, _ = _decode_response(response)
    assert entities == expected_entities
    assert revision >= newer_than
    assert has_more_tags == (revision < latest_revision)


@pytest.mark.pgsql('tags', queries=_DEFAULT_QUERIES)
@pytest.mark.parametrize(
    'topics, expected_entities',
    [
        (
            ['topic0', 'topic1'],
            {
                'car_number': {'CAR_NUMBER': {'programmer'}},
                'park_car_id': {
                    # this would never be sent in v1/match
                    'PARK_CAR': set(),
                },
                'park': {'PARK_ID': {'programmer'}},
            },
        ),
        (
            ['topic1'],
            {
                'car_number': {'CAR_NUMBER': set()},
                'park_car_id': {
                    # this would never be sent in v1/match
                    'PARK_CAR': set(),
                },
                'park': {'PARK_ID': set()},
            },
        ),
    ],
)
@pytest.mark.nofilldb()
async def test_clean_update_topics(taxi_tags, topics, expected_entities):
    response = await _perform_index_request(
        taxi_tags,
        revision_from=0,
        entity_types=['park_car_id', 'car_number', 'park'],
        limit=_UNLIMITED,
        topics=topics,
    )

    entities, revision, has_more_tags, _ = _decode_response(response)
    assert entities == expected_entities
    assert revision > 0
    assert has_more_tags is False


@pytest.mark.pgsql('tags', files=['pg_tags_initial.sql'])
@pytest.mark.parametrize(
    'entity_types, newer_than_delta, expected_before, expected_after',
    [
        (
            ['car_number'],
            -100500,
            {
                #  Unstable provider doesn't affect car_number entities at all
                'car_number': {},
            },
            None,
        ),
        (
            ['park_car_id'],
            _CLEAN_UPDATE,
            _INITIAL_INDEX_PARK_CAR_ID,
            {
                # phone2 entity lost it's tags and we do shot it
                # in v1/index we wouldn't
                'park_car_id': {
                    'PARK_CAR0': {'tag0'},
                    'PARK_CAR1': {'tag0'},
                    'PARK_CAR2': set(),
                },
            },
        ),
        (
            ['park_car_id'],
            -100500,
            _INITIAL_INDEX_PARK_CAR_ID,
            {
                # partial update show the fact that
                # phone2 entity lost all tags
                'park_car_id': {
                    'PARK_CAR0': {'tag0'},
                    'PARK_CAR1': {'tag0'},
                    'PARK_CAR2': set(),
                },
            },
        ),
        (
            ['park_car_id'],
            0,
            {
                'park_car_id': {
                    # There is no changes since last minute before deactivating
                },
            },
            {
                'park_car_id': {
                    # After deactivating provider this entity got no tags
                    'PARK_CAR2': set(),
                },
            },
        ),
    ],
)
@pytest.mark.nofilldb()
async def test_deactivate_provider(
        taxi_tags,
        entity_types,
        newer_than_delta,
        expected_before,
        expected_after,
        pgsql,
):
    revision_before = tags_tools.get_latest_revision(pgsql['tags'])
    newer_than = (
        0
        if newer_than_delta is None
        else max(revision_before + newer_than_delta, 1)
    )

    await taxi_tags.invalidate_caches()
    response = await _perform_index_request(
        taxi_tags, newer_than, entity_types, 1024,
    )
    entities, revision, has_more_tags, _ = _decode_response(response)
    assert entities == expected_before
    assert revision == revision_before
    assert not has_more_tags

    await _call_provider_activation_status(
        taxi_tags, _PROVIDER_UNSTABLE, False,
    )

    await taxi_tags.invalidate_caches()
    response = await _perform_index_request(
        taxi_tags, newer_than, entity_types, 1024,
    )
    entities, revision, has_more_tags, _ = _decode_response(response)
    if expected_after is None:
        expected_after = expected_before
    assert entities == expected_after
    assert revision > revision_before
    assert not has_more_tags


@pytest.mark.pgsql('tags', files=['pg_tags_initial.sql'])
@pytest.mark.parametrize(
    'entity_types, newer_than_delta, expected_before, expected_after',
    [
        (
            ['car_number', 'udid'],
            -100500,
            {'car_number': {}, 'udid': {}},
            None,
        ),
        (
            ['park_car_id'],
            _CLEAN_UPDATE,
            _INITIAL_INDEX_PARK_CAR_ID,
            {
                # phone1 received 'tag1
                'park_car_id': {
                    'PARK_CAR0': {'tag0'},
                    'PARK_CAR1': {'tag0', 'tag1'},
                    'PARK_CAR2': {'tag2'},
                },
            },
        ),
        (
            ['park_car_id'],
            -100500,
            _INITIAL_INDEX_PARK_CAR_ID,
            {
                'park_car_id': {
                    'PARK_CAR0': {'tag0'},
                    'PARK_CAR1': {'tag0', 'tag1'},
                    'PARK_CAR2': {'tag2'},
                },
            },
        ),
        (
            ['park_car_id'],
            0,
            {'park_car_id': {}},
            {
                'park_car_id': {
                    #  After activating this entity got tag1
                    'PARK_CAR1': {'tag0', 'tag1'},
                },
            },
        ),
    ],
)
@pytest.mark.nofilldb()
async def test_activate_provider(
        taxi_tags,
        pgsql,
        entity_types,
        newer_than_delta,
        expected_before,
        expected_after,
):
    revision_before = tags_tools.get_latest_revision(pgsql['tags'])
    newer_than = (
        0
        if newer_than_delta is None
        else max(revision_before + newer_than_delta, 1)
    )

    await taxi_tags.invalidate_caches()
    response = await _perform_index_request(
        taxi_tags, newer_than, entity_types, 1024,
    )
    entities, revision, has_more_tags, _ = _decode_response(response)
    assert entities == expected_before
    assert revision == revision_before
    assert not has_more_tags

    await _call_provider_activation_status(taxi_tags, _PROVIDER_DISABLED, True)

    await taxi_tags.invalidate_caches()
    response = await _perform_index_request(
        taxi_tags, newer_than, entity_types, 1024,
    )
    entities, revision, has_more_tags, _ = _decode_response(response)
    if expected_after is None:
        expected_after = expected_before
    assert entities == expected_after
    assert revision > revision_before
    assert not has_more_tags


@pytest.mark.pgsql('tags', files=['pg_tags_initial.sql'])
@pytest.mark.parametrize(
    'topic, tags, add_relation, update_num, revision_inc, expected_steps',
    [
        # add exist relation
        (
            'topic1',
            ['tag0'],
            True,
            1,
            0,
            [
                {
                    'entity_types': ['park_car_id'],
                    'topics': None,
                    'expected': {'park_car_id': {}},
                },
            ],
        ),
        # add new relation
        (
            'topic2',
            ['tag0', 'tag1'],
            True,
            2,
            3,
            [
                {
                    'entity_types': ['park_car_id'],
                    'topics': None,
                    'expected': {
                        'park_car_id': {
                            'PARK_CAR0': {'tag0'},
                            'PARK_CAR1': {'tag0'},
                        },
                    },
                },
                {
                    'entity_types': ['park_car_id'],
                    'topics': ['topic2'],
                    'expected': {
                        'park_car_id': {
                            'PARK_CAR0': {'tag0'},
                            'PARK_CAR1': {'tag0'},
                        },
                    },
                },
                {
                    'entity_types': ['park_car_id'],
                    'topics': ['topic1'],
                    'expected': {
                        'park_car_id': {
                            'PARK_CAR0': {'tag0'},
                            'PARK_CAR1': {'tag0'},
                        },
                    },
                },
            ],
        ),
        # add mix (exist & new) relations
        (
            'topic1',
            ['tag0', 'tag1'],
            True,
            1,
            1,
            [
                {
                    'entity_types': ['park_car_id'],
                    'topics': None,
                    'expected': {'park_car_id': {'PARK_CAR1': {'tag0'}}},
                },
            ],
        ),
        # remove exist relations
        (
            'topic1',
            ['tag0', 'tag2'],
            False,
            2,
            3,
            [
                {
                    'entity_types': ['park_car_id'],
                    'topics': None,
                    'expected': {
                        'park_car_id': {
                            'PARK_CAR0': {'tag0'},
                            'PARK_CAR1': {'tag0'},
                            'PARK_CAR2': {'tag2'},
                        },
                    },
                },
                {
                    'entity_types': ['park_car_id'],
                    'topics': ['topic1'],
                    'expected': {
                        'park_car_id': {
                            'PARK_CAR0': set(),
                            'PARK_CAR1': set(),
                            'PARK_CAR2': set(),
                        },
                    },
                },
            ],
        ),
        # remove non-exist relation
        (
            'topic2',
            ['tag0', 'tag1'],
            False,
            1,
            0,
            [
                {
                    'entity_types': ['park_car_id'],
                    'topics': None,
                    'expected': {'park_car_id': {}},
                },
            ],
        ),
        # remove mix (exist & non-exist) relations
        (
            'topic0',
            ['tag0', 'tag1'],
            False,
            1,
            2,
            [
                {
                    'entity_types': ['park_car_id'],
                    'topics': None,
                    'expected': {
                        'park_car_id': {
                            'PARK_CAR0': {'tag0'},
                            'PARK_CAR1': {'tag0'},
                        },
                    },
                },
                {
                    'entity_types': ['park_car_id'],
                    'topics': ['topic1'],
                    'expected': {
                        'park_car_id': {
                            'PARK_CAR0': {'tag0'},
                            'PARK_CAR1': {'tag0'},
                        },
                    },
                },
            ],
        ),
    ],
)
@pytest.mark.nofilldb()
async def test_edit_topic_relation(
        taxi_tags,
        topic,
        tags,
        add_relation,
        update_num,
        revision_inc,
        expected_steps,
        pgsql,
):
    revision_before = tags_tools.get_latest_revision(pgsql['tags'])

    query = (
        'v2/admin/topics/items'
        if add_relation
        else 'v2/admin/topics/delete_items'
    )
    response = await taxi_tags.post(
        query,
        {'topic': topic, 'tags': tags},
        headers=constants.TEST_LOGIN_HEADER,
    )
    assert response.status_code == 200

    for _ in range(update_num):
        await tags_tools.activate_task(taxi_tags, 'tags-updater')
    await tags_tools.activate_task(taxi_tags, 'customs-officer')
    await taxi_tags.invalidate_caches()

    for expected_step in expected_steps:
        entity_types = expected_step['entity_types']
        topics = expected_step['topics']
        expected = expected_step['expected']
        response = await _perform_index_request(
            taxi_tags, revision_before, entity_types, 1024, topics,
        )
        entities, revision, has_more_tags, _ = _decode_response(response)
        assert entities == expected
        assert revision == revision_before + revision_inc
        assert not has_more_tags


@pytest.mark.pgsql('tags', files=['pg_tags_initial.sql'])
@pytest.mark.parametrize(
    'provider, upload_data, expected_steps',
    [
        (
            # Append already existing tag
            _PROVIDER_ACTIVE,
            {
                'merge_policy': 'append',
                'entity_type': 'park_car_id',
                'tags': [
                    tags_tools.Tag.get_data(
                        _EXISTING_TAGS[0], _EXISTING_ENTITIES[0],
                    ),
                ],
            },
            [
                {
                    # Same as clean update (without changes)
                    'newer_than_delta': None,
                    'entity_types': ['park_car_id'],
                    'topics': None,
                    'expected': _INITIAL_INDEX_PARK_CAR_ID,
                },
                {
                    'newer_than_delta': None,
                    'entity_types': ['park_car_id'],
                    'topics': ['topic0'],
                    'expected': _INITIAL_INDEX_PARK_CAR_ID_TOPIC,
                },
                {
                    'newer_than_delta': None,
                    'entity_types': ['park_car_id'],
                    'topics': ['topic2'],
                    'expected': {
                        'park_car_id': {
                            'PARK_CAR0': set(),
                            'PARK_CAR1': set(),
                            'PARK_CAR2': set(),
                        },
                    },
                },
                {
                    'newer_than_delta': None,
                    'entity_types': ['park_car_id'],
                    'topics': ['unknown'],
                    'expected': {
                        'park_car_id': {
                            'PARK_CAR0': set(),
                            'PARK_CAR1': set(),
                            'PARK_CAR2': set(),
                        },
                    },
                },
                {
                    # Clean update without changes
                    'newer_than_delta': _CLEAN_UPDATE,
                    'entity_types': ['park_car_id'],
                    'topics': None,
                    'expected': _INITIAL_INDEX_PARK_CAR_ID,
                },
                {
                    'newer_than_delta': _CLEAN_UPDATE,
                    'entity_types': ['park_car_id'],
                    'topics': ['topic0'],
                    'expected': _INITIAL_INDEX_PARK_CAR_ID_TOPIC,
                },
                {
                    # No tags were affected by v1/upload
                    'newer_than_delta': 0,
                    'entity_types': ['park_car_id'],
                    'topics': None,
                    'expected': _EMPTY_INDEX_PARK_CAR_ID,
                },
            ],
        ),
        (
            # Append new tag for disabled provider
            _PROVIDER_DISABLED,
            {
                'merge_policy': 'append',
                'entity_type': 'park_car_id',
                'tags': [
                    tags_tools.Tag.get_data(
                        _EXISTING_TAGS[1], _EXISTING_ENTITIES[2],
                    ),
                ],
            },
            [
                {
                    # Same as clean update (without changes)
                    'newer_than_delta': -100500,
                    'entity_types': ['park_car_id'],
                    'topics': None,
                    'expected': _INITIAL_INDEX_PARK_CAR_ID,
                },
                {
                    'newer_than_delta': -100500,
                    'entity_types': ['park_car_id'],
                    'topics': ['topic0'],
                    'expected': _INITIAL_INDEX_PARK_CAR_ID_TOPIC,
                },
                {
                    # Clean update without changes
                    'newer_than_delta': _CLEAN_UPDATE,
                    'entity_types': ['park_car_id'],
                    'topics': None,
                    'expected': _INITIAL_INDEX_PARK_CAR_ID,
                },
                {
                    # No tags were affected by v1/upload, but phone2 was
                    # under the subject to be updated
                    # through it's tags remain unchanged
                    'newer_than_delta': 0,
                    'entity_types': ['park_car_id'],
                    'topics': None,
                    'expected': {'park_car_id': {'PARK_CAR2': {'tag2'}}},
                },
                {
                    # Partial update in future
                    'newer_than_delta': 100500,
                    'entity_types': ['park_car_id'],
                    'topics': None,
                    'expected': _EMPTY_INDEX_PARK_CAR_ID,
                },
            ],
        ),
        (
            # Replace active provider's tags, effectively appending
            # tags for PARK_CAR1 and PARK_CAR2 and removing last tag from
            # PARK_CAR0
            _PROVIDER_ACTIVE,
            {
                'merge_policy': 'replace',
                'entity_type': 'park_car_id',
                'tags': [
                    tags_tools.Tag.get_data(
                        _EXISTING_TAGS[2], _EXISTING_ENTITIES[1],
                    ),
                    tags_tools.Tag.get_data(
                        _EXISTING_TAGS[2], _EXISTING_ENTITIES[2],
                    ),
                ],
            },
            [
                {
                    # Partial update from epoch should return all entities
                    'newer_than_delta': -100500,
                    'entity_types': ['park_car_id'],
                    'topics': None,
                    'expected': {
                        'park_car_id': {
                            'PARK_CAR0': set(),
                            'PARK_CAR1': {'tag2'},
                            'PARK_CAR2': {'tag2'},
                        },
                    },
                },
                {
                    'newer_than_delta': -100500,
                    'entity_types': ['park_car_id'],
                    'topics': ['topic0', 'topic1', 'topic2'],
                    'expected': {
                        'park_car_id': {
                            'PARK_CAR0': set(),
                            'PARK_CAR1': {'tag2'},
                            'PARK_CAR2': {'tag2'},
                        },
                    },
                },
                {
                    # v2/index always shows all entities tags, even if empty
                    'newer_than_delta': _CLEAN_UPDATE,
                    'entity_types': ['park_car_id'],
                    'topics': None,
                    'expected': {
                        'park_car_id': {
                            # v1/index with clean update won't send that
                            'PARK_CAR0': set(),
                            'PARK_CAR1': {'tag2'},
                            'PARK_CAR2': {'tag2'},
                        },
                    },
                },
                {
                    # These entities were affected in last minute by v1/upload
                    'newer_than_delta': 0,
                    'entity_types': ['park_car_id'],
                    'topics': None,
                    'expected': {
                        'park_car_id': {
                            'PARK_CAR0': set(),
                            'PARK_CAR1': {'tag2'},
                            'PARK_CAR2': {'tag2'},
                        },
                    },
                },
                {
                    # Partial update in future
                    'newer_than_delta': +100500,
                    'entity_types': ['park_car_id'],
                    'topics': None,
                    'expected': _EMPTY_INDEX_PARK_CAR_ID,
                },
            ],
        ),
        (
            # Removes active provider's single tag from PHONEe0
            _PROVIDER_ACTIVE,
            {
                'merge_policy': 'remove',
                'entity_type': 'park_car_id',
                'tags': [
                    tags_tools.Tag.get_data(
                        _EXISTING_TAGS[0], _EXISTING_ENTITIES[0],
                    ),
                ],
            },
            [
                {
                    # Partial update from epoch should return all entities
                    'newer_than_delta': -100500,
                    'entity_types': ['park_car_id'],
                    'topics': None,
                    'expected': {
                        'park_car_id': {
                            'PARK_CAR0': set(),
                            'PARK_CAR1': {'tag0'},
                            'PARK_CAR2': {'tag2'},
                        },
                    },
                },
                {
                    # Partial update from epoch should return all entities
                    'newer_than_delta': -100500,
                    'entity_types': ['park_car_id'],
                    'topics': ['topic0'],
                    'expected': {
                        'park_car_id': {
                            'PARK_CAR0': set(),
                            'PARK_CAR1': {'tag0'},
                            'PARK_CAR2': set(),
                        },
                    },
                },
                {
                    # There is no clean update mode in v2/index
                    'newer_than_delta': _CLEAN_UPDATE,
                    'entity_types': ['park_car_id'],
                    'topics': None,
                    'expected': {
                        'park_car_id': {
                            # v1/index wouldn't send that
                            'PARK_CAR0': set(),
                            'PARK_CAR1': {'tag0'},
                            'PARK_CAR2': {'tag2'},
                        },
                    },
                },
                {
                    'newer_than_delta': 0,
                    'entity_types': ['park_car_id'],
                    'topics': None,
                    'expected': {
                        'park_car_id': {
                            # Only this entity was affected
                            'PARK_CAR0': set(),
                        },
                    },
                },
                {
                    # Partial update in future
                    'newer_than_delta': +1,
                    'entity_types': ['park_car_id'],
                    'topics': None,
                    'expected': _EMPTY_INDEX_PARK_CAR_ID,
                },
            ],
        ),
    ],
)
@pytest.mark.nofilldb()
async def test_upload(taxi_tags, provider, upload_data, expected_steps, pgsql):
    revision_before = tags_tools.get_latest_revision(pgsql['tags'])

    await _perform_v1_upload(taxi_tags, provider, upload_data)

    revision_after = tags_tools.get_latest_revision(pgsql['tags'])

    await taxi_tags.invalidate_caches()

    for step in expected_steps:
        entity_types = step['entity_types']
        topics = step['topics']
        newer_than_delta = step['newer_than_delta']
        newer_than = (
            0
            if newer_than_delta is None
            else max(revision_before + newer_than_delta, 1)
        )
        expected = step['expected']

        response = await _perform_index_request(
            taxi_tags, newer_than, entity_types, 1024, topics,
        )
        entities, revision, has_more_tags, _ = _decode_response(response)

        assert entities == expected
        assert revision == max(revision_after, newer_than or 1)
        assert has_more_tags == (revision < revision_after)


@pytest.mark.pgsql('tags', queries=_DEFAULT_QUERIES)
@pytest.mark.nofilldb()
async def test_metric_calls(taxi_tags, statistics):
    async with statistics.capture(taxi_tags) as capture:
        await _perform_index_request(
            taxi_tags,
            revision_from=0,
            entity_types=['park_car_id', 'car_number', 'park'],
            limit=_UNLIMITED,
            topics=['topic0', 'topic2'],
        )

    assert capture.statistics == {
        'tags.v2_index.pg.get_topics_relations.success': 1,
        'tags.v2_index.pg.get_updated_entities_revision.success': 1,
    }


@pytest.mark.pgsql('tags', queries=_DEFAULT_QUERIES)
@pytest.mark.nofilldb()
async def test_polling_delay(taxi_tags, statistics):
    response = await _perform_index_request(
        taxi_tags,
        revision_from=0,
        entity_types=['park_car_id', 'car_number', 'park'],
        limit=_UNLIMITED,
        topics=['topic0', 'topic2'],
    )
    _, _, _, polling_delay_ms = _decode_response(response)
    assert 185 < polling_delay_ms < 215

    statistics.fallbacks = ['v2_index_degrade']
    await taxi_tags.invalidate_caches()

    response = await _perform_index_request(
        taxi_tags,
        revision_from=0,
        entity_types=['park_car_id', 'car_number', 'park'],
        limit=_UNLIMITED,
        topics=['topic0', 'topic2'],
    )
    _, _, _, polling_delay_ms = _decode_response(response)
    assert 485 < polling_delay_ms < 515
