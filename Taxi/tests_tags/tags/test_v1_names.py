import datetime
from typing import Any
from typing import Dict
from typing import List

import pytest

from tests_tags.tags import tags_tools

_1DAY = datetime.timedelta(days=1)
_1SEC = datetime.timedelta(seconds=1)
_NOW = datetime.datetime.now()

list_answers: dict = {'names': []}


@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_tag_names(
            [
                tags_tools.TagName(0, 'programmer'),
                tags_tools.TagName(1, 'manager'),
                tags_tools.TagName(2, 'analyst'),
                tags_tools.TagName(3, 'engineer'),
                tags_tools.TagName(4, 'teamlead'),
            ],
        ),
        tags_tools.insert_providers(
            [
                tags_tools.Provider.from_id(10, True),
                tags_tools.Provider.from_id(11, False),
                tags_tools.Provider.from_id(12, True),
                tags_tools.Provider.from_id(13, True),
            ],
        ),
        tags_tools.insert_entities(
            [
                tags_tools.Entity(200, 'DBID_UUID', 'dbid_uuid'),
                tags_tools.Entity(201, 'CAR_NUMBER', 'car_number'),
                tags_tools.Entity(202, 'UDID', 'udid'),
                tags_tools.Entity(203, 'PHONE HASH', 'phone_hash_id'),
                tags_tools.Entity(204, 'PARK', 'park'),
            ],
        ),
        tags_tools.insert_tags(
            [
                tags_tools.Tag(0, 10, 200, entity_type='dbid_uuid'),
                tags_tools.Tag(
                    0, 10, 204, entity_type='park', ttl=_NOW - _1DAY,
                ),
                tags_tools.Tag(1, 12, 201, entity_type='car_number'),
                tags_tools.Tag(2, 11, 202, entity_type='udid'),
                tags_tools.Tag(2, 11, 201, entity_type='car_number'),
                tags_tools.Tag(2, 12, 202, entity_type='udid'),
                tags_tools.Tag(3, 11, 203, entity_type='phone_hash_id'),
                tags_tools.Tag(3, 12, 203, entity_type='phone_hash_id'),
                tags_tools.Tag(3, 13, 203, entity_type='phone_hash_id'),
                tags_tools.Tag(4, 11, 204, entity_type='park'),
                tags_tools.Tag(4, 12, 204, entity_type='park'),
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'data, status_code, expected_names',
    [
        ({'entity_types': ['bad_type']}, 400, []),
        ({'entity_types': ['']}, 400, ['empty entity types']),
        ({'entity_types': ['park']}, 200, ['teamlead']),
        ({'entity_types': ['car_number']}, 200, ['manager']),
        ({'entity_types': ['phone_hash_id']}, 200, ['engineer']),
        (
            {
                'entity_types': [
                    'personal_phone_id',
                    'user_id',
                    'user_phone_id',
                ],
            },
            200,
            [],
        ),
        ({'entity_types': ['dbid_uuid']}, 200, ['programmer']),
        ({'entity_types': ['udid']}, 200, ['analyst']),
        (
            {'entity_types': ['dbid_uuid', 'car_number', 'park', 'udid']},
            200,
            ['analyst', 'manager', 'programmer', 'teamlead'],
        ),
    ],
)
@pytest.mark.nofilldb()
async def test_names(
        taxi_tags,
        data: Dict[str, Any],
        status_code: int,
        expected_names: List[str],
):
    names_response = await taxi_tags.post('v1/names', data)
    assert names_response.status_code == status_code
    if status_code == 200:
        response = names_response.json()
        assert response['names'] == expected_names


@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_tag_names(
            [
                tags_tools.TagName(0, 'programmer_on_topic_and_entity'),
                tags_tools.TagName(1, 'manager_on_topic'),
                tags_tools.TagName(2, 'analyst_on_topic_and_entity'),
                tags_tools.TagName(3, 'engineer_on_entity'),
                tags_tools.TagName(4, 'teamlead_on_topic_and_entity'),
                tags_tools.TagName(5, 'used_on_entity'),
                tags_tools.TagName(6, 'used_on_topic'),
                tags_tools.TagName(7, 'unused'),
            ],
        ),
        tags_tools.insert_providers(
            [
                tags_tools.Provider.from_id(10, True),
                tags_tools.Provider.from_id(11, False),
                tags_tools.Provider.from_id(12, True),
                tags_tools.Provider.from_id(13, True),
            ],
        ),
        tags_tools.insert_topics(
            [
                tags_tools.Topic(2000, 'simple_topic', False),
                tags_tools.Topic(2001, 'finance_topic', True),
                tags_tools.Topic(2002, 'base_topic', False),
            ],
        ),
        tags_tools.insert_relations(
            [
                tags_tools.Relation(0, 2001),
                tags_tools.Relation(1, 2001),
                tags_tools.Relation(2, 2000),
                tags_tools.Relation(4, 2002),
                tags_tools.Relation(6, 2000),
            ],
        ),
        tags_tools.insert_entities(
            [
                tags_tools.Entity(200, 'DBID_UUID', 'dbid_uuid'),
                tags_tools.Entity(201, 'CAR_NUMBER', 'car_number'),
                tags_tools.Entity(202, 'UDID', 'udid'),
                tags_tools.Entity(203, 'PHONE HASH', 'phone_hash_id'),
                tags_tools.Entity(204, 'PARK', 'park'),
            ],
        ),
        tags_tools.insert_tags(
            [
                tags_tools.Tag(0, 10, 200, ttl=_NOW - _1SEC),
                tags_tools.Tag(0, 10, 204, ttl=_NOW - _1DAY),
                tags_tools.Tag(2, 11, 202),
                tags_tools.Tag(2, 11, 201),
                tags_tools.Tag(2, 11, 204),
                tags_tools.Tag(3, 11, 203),
                tags_tools.Tag(3, 12, 203),
                tags_tools.Tag(3, 13, 203),
                tags_tools.Tag(4, 10, 204),
                tags_tools.Tag(4, 12, 204),
                tags_tools.Tag(5, 12, 200),
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'query, status_code, expected_names',
    [
        ('limit=0', 400, None),
        ('offset=-1', 400, None),
        (
            '',
            200,
            [
                'analyst_on_topic_and_entity',
                'engineer_on_entity',
                'programmer_on_topic_and_entity',
                'teamlead_on_topic_and_entity',
                'used_on_entity',
            ],
        ),
        (
            'tag_contains=am',
            200,
            ['programmer_on_topic_and_entity', 'teamlead_on_topic_and_entity'],
        ),
        (
            'tag_contains=am&include_topic_related=false',
            200,
            ['programmer_on_topic_and_entity', 'teamlead_on_topic_and_entity'],
        ),
        (
            'tag_contains=am&include_topic_related=true',
            200,
            ['programmer_on_topic_and_entity', 'teamlead_on_topic_and_entity'],
        ),
        (
            'include_topic_related=false',
            200,
            [
                'analyst_on_topic_and_entity',
                'engineer_on_entity',
                'programmer_on_topic_and_entity',
                'teamlead_on_topic_and_entity',
                'used_on_entity',
            ],
        ),
        (
            'include_topic_related=true',
            200,
            [
                'analyst_on_topic_and_entity',
                'engineer_on_entity',
                'manager_on_topic',
                'programmer_on_topic_and_entity',
                'teamlead_on_topic_and_entity',
                'used_on_entity',
                'used_on_topic',
            ],
        ),
        ('tag_contains=un', 200, []),
        ('tag_contains=un&include_topic_related=true', 200, []),
        (
            'offset=0&limit=2',
            200,
            ['analyst_on_topic_and_entity', 'engineer_on_entity'],
        ),
        ('offset=1&limit=1', 200, ['engineer_on_entity']),
        ('offset=3&limit=1', 200, ['teamlead_on_topic_and_entity']),
        (
            'include_topic_related=true&offset=5&limit=3',
            200,
            ['used_on_entity', 'used_on_topic'],
        ),
        (
            'tag_contains=am&include_topic_related=true&limit=1',
            200,
            ['programmer_on_topic_and_entity'],
        ),
        (
            'tag_contains=am&include_topic_related=true&offset=1&limit=1',
            200,
            ['teamlead_on_topic_and_entity'],
        ),
        (
            'include_inactive=false',
            200,
            [
                'analyst_on_topic_and_entity',
                'engineer_on_entity',
                'programmer_on_topic_and_entity',
                'teamlead_on_topic_and_entity',
                'used_on_entity',
            ],
        ),
        (
            'include_inactive=true',
            200,
            [
                'analyst_on_topic_and_entity',
                'engineer_on_entity',
                'manager_on_topic',
                'programmer_on_topic_and_entity',
                'teamlead_on_topic_and_entity',
                'unused',
                'used_on_entity',
                'used_on_topic',
            ],
        ),
        (
            'tag_contains=us&include_inactive=true',
            200,
            ['unused', 'used_on_entity', 'used_on_topic'],
        ),
        (
            'tag_contains=us&include_inactive=true&offset=2&limit=1',
            200,
            ['used_on_topic'],
        ),
        (
            'topic=simple_topic&tag_contains=us&include_inactive=true',
            200,
            ['used_on_topic'],
        ),
        (
            'topic=finance_topic&tag_contains=topic&include_inactive=true',
            200,
            ['manager_on_topic', 'programmer_on_topic_and_entity'],
        ),
        (
            'topic=finance_topic&tag_contains=topic&include_inactive=true'
            '&include_topic_related=true',
            200,
            ['manager_on_topic', 'programmer_on_topic_and_entity'],
        ),
        (
            'topic=finance_topic&tag_contains=topic&include_inactive=true'
            '&include_topic_related=true&limit=1',
            200,
            ['manager_on_topic'],
        ),
        (
            'topic=finance_topic&tag_contains=topic&include_inactive=true'
            '&include_topic_related=true&offset=1',
            200,
            ['programmer_on_topic_and_entity'],
        ),
        (
            'topic=finance_topic&tag_contains=mm&include_inactive=true',
            200,
            ['programmer_on_topic_and_entity'],
        ),
        ('topic=simple_topic&tag_contains=mm', 200, []),
        ('topic=base_topic', 200, ['teamlead_on_topic_and_entity']),
        ('topic=not_existed', 200, []),
        ('topic=\'--SELECT;--', 200, []),
    ],
)
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.nofilldb()
async def test_suggest_names(
        taxi_tags, query: str, status_code: int, expected_names: List[str],
):
    names_response = await taxi_tags.get('v1/suggest_names?' + query)
    assert names_response.status_code == status_code
    if expected_names is not None:
        response = names_response.json()
        assert response['names'] == expected_names
