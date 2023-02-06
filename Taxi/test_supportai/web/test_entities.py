import pytest


def check_entity_content(entity, ref_entity):
    assert entity['slug'] == ref_entity['slug']
    assert entity['title'] == ref_entity['title']
    assert entity['type'] == ref_entity['type']
    assert entity['extractor'] == ref_entity['extractor']


@pytest.mark.pgsql('supportai', files=['default.sql', 'sample_entities.sql'])
async def test_get_entities(web_app_client):
    all_features_response = await web_app_client.get(
        '/v1/entities?user_id=1&project_slug=ya_lavka',
    )
    assert all_features_response.status == 200
    assert len((await all_features_response.json())['entities']) == 3


@pytest.mark.pgsql('supportai', files=['default.sql'])
@pytest.mark.parametrize(
    'type_,extractor,valid',
    [
        (
            'int',
            {'type': 'regular_expression', 'regular_expression': '[0-9]+'},
            True,
        ),
        (
            'int',
            {'type': 'regular_expression', 'regular_expression': '[0-9'},
            False,
        ),
        (
            'str',
            {
                'type': 'choice_from_variants',
                'variants': [{'regular_expression': 'a|A', 'value': 'A'}],
            },
            True,
        ),
        (
            'str',
            {
                'type': 'choice_from_variants',
                'variants': [{'regular_expression': '[a', 'value': 'A'}],
            },
            False,
        ),
        ('str', {'type': 'custom', 'extractor_type': 'custom'}, True),
    ],
)
async def test_create_entity(web_app_client, type_, extractor, valid):
    ref_entity = {
        'id': '',
        'slug': 'new_entity',
        'title': 'New entity',
        'type': type_,
        'extractor': extractor,
    }

    entity_response = await web_app_client.post(
        '/v1/entities?user_id=1&project_slug=ya_market', json=ref_entity,
    )

    assert entity_response.status == (200 if valid else 400)

    if valid:
        new_entity = await entity_response.json()

        check_entity_content(new_entity, ref_entity)

        all_entities_response = await web_app_client.get(
            '/v1/entities?user_id=1&project_slug=ya_market',
        )

        all_entities_response = await all_entities_response.json()

        assert len(all_entities_response['entities']) == 1

        assert new_entity['id'] in [
            entity['id'] for entity in all_entities_response['entities']
        ]


@pytest.mark.pgsql('supportai', files=['default.sql', 'sample_entities.sql'])
async def test_update_entity(web_app_client):
    ref_entity = {
        'id': '1',
        'slug': 'entity1',
        'title': 'Entity 1 new name',
        'type': 'str',
        'extractor': {
            'type': 'choice_from_variants',
            'variants': [{'regular_expression': 'a|A', 'value': 'A'}],
        },
    }

    update_entity_response = await web_app_client.put(
        '/v1/entities/1?user_id=1&project_slug=ya_lavka', json=ref_entity,
    )

    assert update_entity_response.status == 200

    updated_entity = await update_entity_response.json()

    check_entity_content(updated_entity, ref_entity)

    all_entities_response = await web_app_client.get(
        '/v1/entities?user_id=1&project_slug=ya_lavka',
    )

    all_entities_response_json = await all_entities_response.json()

    for entity in all_entities_response_json['entities']:
        if entity['id'] == ref_entity['id']:
            check_entity_content(entity, ref_entity)
            break


@pytest.mark.pgsql('supportai', files=['default.sql', 'sample_entities.sql'])
async def test_delete_entity(web_app_client):

    remove_entity_response = await web_app_client.delete(
        '/v1/entities/1?user_id=1&project_slug=ya_lavka',
    )

    assert remove_entity_response.status == 200

    remove_entity_response = await web_app_client.delete(
        '/v1/entities/3?user_id=1&project_slug=ya_lavka',
    )

    assert remove_entity_response.status == 400


@pytest.mark.pgsql('supportai', files=['default.sql'])
async def test_entity_custom_extractors(web_app_client):

    response = await web_app_client.get(
        '/v1/entities/extractors/custom?user_id=1&project_slug=ya_lavka',
    )

    assert response.status == 200

    response_json = await response.json()

    assert len(response_json['extractors']) == 16


@pytest.mark.pgsql('supportai', files=['default.sql'])
async def test_post_entities_bulk(web_app_client):

    ref_entities = [
        {
            'id': '1',
            'slug': 'entity1',
            'title': 'Entity 1',
            'type': 'str',
            'extractor': {
                'type': 'choice_from_variants',
                'variants': [{'regular_expression': 'a|A', 'value': 'A'}],
            },
        },
        {
            'id': '2',
            'slug': 'entity2',
            'title': 'Entity 2',
            'type': 'int',
            'extractor': {
                'type': 'regular_expression',
                'regular_expression': '\\d+',
            },
        },
    ]

    entity_response = await web_app_client.post(
        '/supportai/v1/entities?user_id=1&project_slug=ya_lavka',
        json={'entities': ref_entities},
    )

    assert entity_response.status == 200

    new_entities = (await entity_response.json())['entities']

    assert len(new_entities) == 2

    for idx, ref_entity in enumerate(ref_entities):
        check_entity_content(new_entities[idx], ref_entity)
