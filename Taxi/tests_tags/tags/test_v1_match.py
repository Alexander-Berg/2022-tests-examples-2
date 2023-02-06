import datetime


import pytest

from tests_tags.tags import tags_tools


@pytest.mark.parametrize(
    'expected_code, data',
    [
        # No entities specified
        (400, {}),
        # Unknown entity type
        (400, {'entities': [{'type': 'unkown_type', 'id': 'abc'}]}),
        # No entities at all
        (200, {'entities': []}),
        # Valid entity
        (200, {'entities': [{'type': 'car_number', 'id': 'abc'}]}),
        (200, {'entities': [{'type': 'udid', 'id': 'abc'}]}),
    ],
)
@pytest.mark.pgsql('tags')
@pytest.mark.nofilldb()
async def test_request_data(taxi_tags, expected_code, data):
    response = await taxi_tags.post('v1/match', data)
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
                tags_tools.Entity(3000, 'LICENSE', 'driver_license'),
                tags_tools.Entity(3001, 'CAR_NUMBER', 'car_number'),
                # same entity id as driver license
                tags_tools.Entity(3002, 'LICENSE', 'park'),
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
                # Tag from deactivated provider
                tags_tools.Tag(2000, 1001, 3000),
                # Active tag
                tags_tools.Tag(2000, 1000, 3001),
                # Same tag as previous but from deactivated provider
                tags_tools.Tag(2000, 1001, 3001),
                # Same active tag as previous
                tags_tools.Tag(2000, 1002, 3001),
                tags_tools.Tag(2000, 1000, 3002),
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'requested_entities, expected_entities',
    [
        ([], []),
        (
            [{'id': 'LICENSE', 'type': 'driver_license'}],
            [{'id': 'LICENSE', 'type': 'driver_license', 'tags': []}],
        ),
        (
            [
                {'id': 'LICENSE', 'type': 'driver_license'},
                {'id': 'LICENSE', 'type': 'park'},
            ],
            [
                {'id': 'LICENSE', 'type': 'driver_license', 'tags': []},
                {'id': 'LICENSE', 'type': 'park', 'tags': ['programmer']},
            ],
        ),
        (
            [{'id': 'LICENSE', 'type': 'driver_license'}],
            [{'id': 'LICENSE', 'type': 'driver_license', 'tags': []}],
        ),
        (
            [{'id': 'CAR_NUMBER', 'type': 'car_number'}],
            [
                {
                    'id': 'CAR_NUMBER',
                    'type': 'car_number',
                    'tags': ['programmer'],
                },
            ],
        ),
    ],
)
@pytest.mark.nofilldb()
async def test_match(taxi_tags, requested_entities, expected_entities):
    data = {'entities': requested_entities or []}

    await taxi_tags.invalidate_caches()

    response = await taxi_tags.post('v1/match', data)
    assert response.status_code == 200
    response = response.json()
    assert 'entities' in response
    assert response['entities'] == expected_entities


_TEST_FIRST_PROVIDER_ID = 1000
_TEST_PROVIDERS = [
    tags_tools.Provider.from_id(_TEST_FIRST_PROVIDER_ID, True),
    tags_tools.Provider.from_id(_TEST_FIRST_PROVIDER_ID + 1, True),
    tags_tools.Provider.from_id(_TEST_FIRST_PROVIDER_ID + 2, False),
]


def _prepare_tags_data(tags):
    result = []
    for entity, tags_list in tags.items():
        for tag in tags_list:
            result.append({'name': tag, 'match': {'id': entity}})
    return result


def _parse_entities_response(entities, expected_items):
    result = {entity: set() for entity in expected_items}
    for entity in entities:
        entity_name = entity.get('id')
        tags = entity.get('tags')
        for tag in tags:
            result[entity_name].add(tag)
    return result


async def _upload_request(taxi_tags, provider, i, tags, entity_type='udid'):
    query = (
        'v1/upload?provider_id={provider}'
        '&confirmation_token=token_{i}'.format(provider=provider.name, i=i)
    )
    data = {
        'tags': tags,
        'merge_policy': 'replace',
        'entity_type': entity_type,
    }
    return await taxi_tags.post(query, data)


async def _match_request(taxi_tags, entities):
    query = 'v1/match'
    data = {'entities': [{'id': id, 'type': 'udid'} for id in entities]}
    return await taxi_tags.post(query, data)


@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_providers([_TEST_PROVIDERS[0]]),
        tags_tools.insert_service_providers(
            [(_TEST_PROVIDERS[0].provider_id, ['reposition'], 'base')],
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
    ],
)
@pytest.mark.nofilldb()
async def test_cache(taxi_tags, tags_uploads):
    for i, tags_upload in enumerate(tags_uploads):
        tags_data = _prepare_tags_data(tags_upload)
        upload_response = await _upload_request(
            taxi_tags, _TEST_PROVIDERS[0], i, tags_data,
        )
        assert upload_response.status_code == 200

        await tags_tools.activate_task(taxi_tags, 'customs-officer')
        await taxi_tags.invalidate_caches()

        entities_list = ['entity_0', 'entity_1', 'entity_2']

        match_response = await _match_request(taxi_tags, entities_list)
        assert match_response.status_code == 200

        entities = match_response.json().get('entities')
        parsed = _parse_entities_response(entities, entities_list)
        assert set(parsed.keys()) == set(entities_list)

        requested = {entity: set() for entity in entities_list}
        for entity, tags in tags_upload.items():
            requested[entity] = set(tags)
        assert parsed == requested
