import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Set

import pytest

from tests_tags.tags import tags_tools


@pytest.mark.parametrize(
    'expected_code, data',
    [
        # No entities specified
        (400, {}),
        (400, {'entity_type': 'car_number'}),
        # Unknown entity type
        (400, {'entity_type': 'unknown_type', 'entities': ['abc']}),
        # tags_tools.Entity type was not specified
        (400, {'entities': ['abc']}),
        # No entities at all
        (200, {'entity_type': 'driver_license', 'entities': []}),
        # Valid entity
        (200, {'entity_type': 'car_number', 'entities': ['abc']}),
    ],
)
@pytest.mark.pgsql('tags')
@pytest.mark.nofilldb()
async def test_request_data(
        taxi_tags, expected_code: int, data: Dict[str, Any],
):
    response = await taxi_tags.post('v1/bulk_match', data)
    assert response.status_code == expected_code


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
                tags_tools.Entity(3000, 'PARK', 'park'),
                tags_tools.Entity(3001, 'CAR_NUMBER', 'car_number'),
                tags_tools.Entity(
                    3002, 'PARK', 'park_car_id',
                ),  # same entity id as park
                tags_tools.Entity(3003, 'USER ID', 'user_id'),
            ],
        ),
        tags_tools.insert_tags(
            [
                # Deleted tag
                tags_tools.Tag(
                    2000,
                    1000,
                    3000,
                    ttl=datetime.datetime(2018, 1, 1, 10, 0, 0),
                ),
                # tags_tools.Tag from deactivated provider
                tags_tools.Tag(2000, 1001, 3000),
                # Active tag
                tags_tools.Tag(2000, 1000, 3001),
                # Same tag as previous but from deactivated provider
                tags_tools.Tag(2000, 1001, 3001),
                # Same active tag as previous
                tags_tools.Tag(2000, 1002, 3001),
                tags_tools.Tag(2000, 1000, 3002),
                tags_tools.Tag(2001, 1000, 3003),
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'entity_type, requested_entities, expected_entities',
    [
        ('park', [], []),
        ('park', ['PARK'], []),
        (
            'park_car_id',
            ['CAR_NUMBER', 'PARK'],
            [{'id': 'PARK', 'tags': ['programmer']}],
        ),
        (
            'car_number',
            ['CAR_NUMBER'],
            [{'id': 'CAR_NUMBER', 'tags': ['programmer']}],
        ),
        ('park', [], []),
        ('user_id', ['USER ID'], [{'id': 'USER ID', 'tags': ['manager']}]),
    ],
)
@pytest.mark.nofilldb()
async def test_match(
        taxi_tags,
        entity_type: str,
        requested_entities: List[str],
        expected_entities: List[str],
):
    data = {'entity_type': entity_type, 'entities': requested_entities or []}

    await taxi_tags.invalidate_caches()

    response = await taxi_tags.post('v1/bulk_match', data)
    assert response.status_code == 200
    response = response.json()
    assert response['entities'] == expected_entities


_TEST_FIRST_PROVIDER_ID = 1000
_TEST_PROVIDERS = [
    tags_tools.Provider.from_id(_TEST_FIRST_PROVIDER_ID, True),
    tags_tools.Provider.from_id(_TEST_FIRST_PROVIDER_ID + 1, True),
    tags_tools.Provider.from_id(_TEST_FIRST_PROVIDER_ID + 2, False),
]


def _prepare_tags_data(tags: Dict[str, List[str]]):
    result = []
    for entity, tags_list in tags.items():
        for tag in tags_list:
            result.append({'name': tag, 'match': {'id': entity}})
    return result


def _parse_entities_response(
        entities: List[Dict[str, Any]], expected_items: List[str],
):
    result: Dict[str, Set[str]] = {entity: set() for entity in expected_items}
    for entity in entities:
        entity_name = entity.get('id') or ''
        tags = entity.get('tags') or set()
        for tag in tags:
            result[entity_name].add(tag)
    return result


def _upload_request(taxi_tags, provider, i, tags, entity_type='park'):
    query = (
        'v1/upload?provider_id={provider}'
        '&confirmation_token=token_{i}'.format(provider=provider.name, i=i)
    )
    data = {
        'tags': tags,
        'merge_policy': 'replace',
        'entity_type': entity_type,
    }
    return taxi_tags.post(query, data)


def _match_request(taxi_tags, entities_list: List[str]):
    query = 'v1/bulk_match'
    data = {'entity_type': 'park', 'entities': entities_list}
    return taxi_tags.post(query, data)


@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_providers([_TEST_PROVIDERS[0]]),
        tags_tools.insert_service_providers(
            [(_TEST_PROVIDERS[0].provider_id, ['service'], 'base')],
        ),
    ],
)
@pytest.mark.parametrize(
    'tags_uploads',
    [
        (
            [
                {'entity_0': ['tag_0', 'tag_1', 'tag_2']},
                {'entity_1': ['tag_0', 'tag_1', 'tag_2'], 'entity_0': []},
                {'entity_1': [], 'entity_0': ['tag_0']},
                {'entity_2': []},
            ]
        ),
        (
            [
                {},
                {'entity_0': []},
                {
                    'entity_0': ['tag_0', 'tag_1'],
                    'entity_1': ['tag_3', 'tag_4'],
                },
                {'entity_0': ['tag_4', 'tag_5'], 'entity_2': []},
            ]
        ),
        (
            [
                {
                    'entity_0': ['bonus_20', 'bonus_40'],
                    'entity_1': ['bonus_40', 'bonus_20_correction'],
                    'entity_2': ['bonus_20_correction', 'bonus_40'],
                },
                {
                    'entity_0': ['bonus_20_correction', 'bonus_40_correction'],
                    'entity_1': ['bonus_40_correction', 'bonus_20'],
                    'entity_2': ['bonus_20', 'bonus_40_correction'],
                },
                {
                    'entity_0': ['bonus_20', 'bonus_40'],
                    'entity_1': ['bonus_40', 'bonus_20_correction'],
                    'entity_2': ['bonus_20_correction', 'bonus_40'],
                },
            ]
        ),
    ],
)
@pytest.mark.nofilldb()
async def test_cache(taxi_tags, tags_uploads: List[Dict[str, List[str]]]):
    for i, tags_upload in enumerate(tags_uploads):
        tags_data = _prepare_tags_data(tags_upload)
        upload_response = await _upload_request(
            taxi_tags, _TEST_PROVIDERS[0], i, tags_data,
        )
        assert upload_response.status_code == 200

        await tags_tools.activate_task(taxi_tags, 'customs-officer')
        await taxi_tags.invalidate_caches()

        entities_list = ['entity_0', 'entity_1', 'entity_2']
        entities_expected = []
        for entity in entities_list:
            if entity in tags_upload and tags_upload.get(entity, []):
                entities_expected.append(entity)

        match_response = await _match_request(taxi_tags, entities_list)
        assert match_response.status_code == 200

        entities = match_response.json().get('entities')
        parsed = _parse_entities_response(entities, entities_expected)
        assert set(parsed.keys()) == set(entities_expected)

        requested: Dict[str, Set[str]] = {
            entity: set() for entity in entities_expected
        }
        for entity, tags in tags_upload.items():
            if tags:
                requested[entity] = set(tags)
        assert parsed == requested


@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_providers([_TEST_PROVIDERS[0]]),
        tags_tools.insert_service_providers(
            [(_TEST_PROVIDERS[0].provider_id, ['service'], 'base')],
        ),
    ],
)
@pytest.mark.nofilldb()
async def test_bulk_match(taxi_tags):
    bulk_size = 100

    entities = ['entity_%s' % i for i in range(bulk_size)]
    tags = ['tag0', 'tag1', 'tag2']
    tags_data = _prepare_tags_data({entity: tags for entity in entities})
    upload_response = await _upload_request(
        taxi_tags, _TEST_PROVIDERS[0], 'test_confirmation_token', tags_data,
    )
    assert upload_response.status_code == 200

    await tags_tools.activate_task(taxi_tags, 'customs-officer')
    await taxi_tags.invalidate_caches()

    match_response = await _match_request(taxi_tags, entities)
    assert match_response.status_code == 200
    match_response = match_response.json()
    matched_entities = match_response['entities']
    assert len(matched_entities) == bulk_size

    for entity in matched_entities:
        entity['tags'] = set(entity['tags'])

    expected_entities = [
        {'id': 'entity_%s' % i, 'tags': set(tags)} for i in range(bulk_size)
    ]
    assert matched_entities == expected_entities
