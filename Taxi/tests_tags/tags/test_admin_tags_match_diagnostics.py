import datetime

import pytest

from tests_tags.tags import tags_tools
from tests_tags.tags import yql_tools


_NOW = datetime.datetime(2019, 11, 8, 12, 45, 32)
_HOUR_AFTER = _NOW + datetime.timedelta(hours=1)
_DAY_AFTER = _NOW + datetime.timedelta(days=1)


@pytest.mark.nofilldb()
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_tag_names(
            [
                tags_tools.TagName(1, 'tag1'),
                tags_tools.TagName(2, 'tag2'),
                tags_tools.TagName(3, 'tag3'),
            ],
        ),
        tags_tools.insert_topics(
            [
                tags_tools.Topic(10, 'topic1', False),
                tags_tools.Topic(20, 'topic2', False),
                tags_tools.Topic(30, 'topic3', False),
            ],
        ),
        tags_tools.insert_relations(
            [
                tags_tools.Relation(1, 10),
                tags_tools.Relation(2, 20),
                tags_tools.Relation(2, 30),
            ],
        ),
        tags_tools.insert_providers(
            [
                tags_tools.Provider(100, 'provider0', '', True),
                tags_tools.Provider(200, 'provider1', '', True),
                tags_tools.Provider(300, 'provider2', '', True),
            ],
        ),
        tags_tools.insert_service_providers([(100, ['base_service'], 'base')]),
        yql_tools.insert_queries(
            [
                yql_tools.Query(
                    'query', 200, ['tag1', 'tag2', 'tag3'], entity_type='udid',
                ),
            ],
        ),
        tags_tools.insert_entities(
            [
                tags_tools.Entity(1000, 'udid0', entity_type='udid'),
                tags_tools.Entity(2000, 'dbid_uuid0', entity_type='dbid_uuid'),
                tags_tools.Entity(3000, 'park0', entity_type='park'),
                tags_tools.Entity(
                    4000, 'car_number0', entity_type='car_number',
                ),
                tags_tools.Entity(
                    5000, 'park_car_id0', entity_type='park_car_id',
                ),
                tags_tools.Entity(6000, 'udid1', entity_type='udid'),
                tags_tools.Entity(7000, 'udid2', entity_type='udid'),
            ],
        ),
        tags_tools.insert_tags(
            [
                # single tags
                tags_tools.Tag(2, 200, 1000, ttl='infinity'),
                tags_tools.Tag(1, 100, 2000, ttl='infinity'),
                tags_tools.Tag(1, 300, 3000, ttl=_HOUR_AFTER),
                tags_tools.Tag(2, 300, 4000, ttl='infinity'),
                tags_tools.Tag(3, 100, 5000, ttl=_DAY_AFTER),
                # multi tags
                tags_tools.Tag(1, 300, 6000, ttl='infinity'),
                tags_tools.Tag(2, 300, 6000, ttl=_HOUR_AFTER),
                tags_tools.Tag(3, 300, 6000, ttl=_DAY_AFTER),
                # multi providers
                tags_tools.Tag(3, 100, 7000, ttl='infinity'),
                tags_tools.Tag(3, 200, 7000, ttl=_HOUR_AFTER),
                tags_tools.Tag(3, 300, 7000, ttl=_DAY_AFTER),
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'request_entities, response_tags',
    [
        pytest.param(
            [{'type': 'udid', 'value': 'not-existed'}], [{}], id='no tags',
        ),
        pytest.param(
            [{'type': 'udid', 'value': 'udid1'}],
            [
                {
                    'tag1': {
                        'topics': ['topic1'],
                        'entries': [
                            {
                                'provider': {
                                    'name': 'provider2',
                                    'type': 'manual',
                                },
                            },
                        ],
                    },
                    'tag2': {
                        'topics': ['topic2', 'topic3'],
                        'entries': [
                            {
                                'ttl': '2019-11-08T13:45:32+0000',
                                'provider': {
                                    'name': 'provider2',
                                    'type': 'manual',
                                },
                            },
                        ],
                    },
                    'tag3': {
                        'topics': [],
                        'entries': [
                            {
                                'ttl': '2019-11-09T12:45:32+0000',
                                'provider': {
                                    'name': 'provider2',
                                    'type': 'manual',
                                },
                            },
                        ],
                    },
                },
            ],
            id='multi tags',
        ),
        pytest.param(
            [{'type': 'udid', 'value': 'udid2'}],
            [
                {
                    'tag3': {
                        'topics': [],
                        'entries': [
                            {
                                'provider': {
                                    'name': 'provider0',
                                    'type': 'service',
                                },
                            },
                            {
                                'ttl': '2019-11-08T13:45:32+0000',
                                'provider': {
                                    'name': 'provider1',
                                    'type': 'yql',
                                },
                            },
                            {
                                'ttl': '2019-11-09T12:45:32+0000',
                                'provider': {
                                    'name': 'provider2',
                                    'type': 'manual',
                                },
                            },
                        ],
                    },
                },
            ],
            id='multi providers',
        ),
        pytest.param(
            [
                {'type': 'udid', 'value': 'udid0'},
                {'type': 'dbid_uuid', 'value': 'dbid_uuid0'},
                {'type': 'park', 'value': 'park0'},
                {'type': 'car_number', 'value': 'car_number0'},
                {'type': 'park_car_id', 'value': 'park_car_id0'},
            ],
            [
                {
                    'tag2': {
                        'topics': ['topic2', 'topic3'],
                        'entries': [
                            {'provider': {'name': 'provider1', 'type': 'yql'}},
                        ],
                    },
                },
                {
                    'tag1': {
                        'topics': ['topic1'],
                        'entries': [
                            {
                                'provider': {
                                    'name': 'provider0',
                                    'type': 'service',
                                },
                            },
                        ],
                    },
                },
                {
                    'tag1': {
                        'topics': ['topic1'],
                        'entries': [
                            {
                                'ttl': '2019-11-08T13:45:32+0000',
                                'provider': {
                                    'name': 'provider2',
                                    'type': 'manual',
                                },
                            },
                        ],
                    },
                },
                {
                    'tag2': {
                        'topics': ['topic2', 'topic3'],
                        'entries': [
                            {
                                'provider': {
                                    'name': 'provider2',
                                    'type': 'manual',
                                },
                            },
                        ],
                    },
                },
                {
                    'tag3': {
                        'topics': [],
                        'entries': [
                            {
                                'ttl': '2019-11-09T12:45:32+0000',
                                'provider': {
                                    'name': 'provider0',
                                    'type': 'service',
                                },
                            },
                        ],
                    },
                },
            ],
            id='multi entities',
        ),
    ],
)
@pytest.mark.pgsql('tags', queries=[])
async def test_tags_diagnostic(taxi_tags, request_entities, response_tags):
    body = {'entities': request_entities}
    response = await taxi_tags.post('v1/admin/tags/match_diagnostics', body)
    assert response.status_code == 200
    response_json = response.json()
    for entities in response_json['entities']:
        for _, tag in entities['tags'].items():
            tag['topics'].sort()
    assert response_json == {'entities': [{'tags': x} for x in response_tags]}
