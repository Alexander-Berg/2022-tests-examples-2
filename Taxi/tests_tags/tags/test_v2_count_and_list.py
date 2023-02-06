import datetime
from typing import Any
from typing import Dict
from typing import List

import pytest


from tests_tags.tags import constants
from tests_tags.tags import tags_tools


_1DAY = datetime.timedelta(days=1)
_2DAYS = datetime.timedelta(days=2)
_3DAYS = datetime.timedelta(days=3)
_NOW = datetime.datetime.now()
_TTL = datetime.datetime(2018, 1, 1, 10, 0, 0)

list_answers: dict = {
    'name_10': [
        {
            'name': 'programmer',
            'entity_type': 'car_number',
            'entity_name': 'CAR_NUMBER',
            'ttl': 'infinity',
            'provider_name': 'name_10',
            'topics': ['topic0', 'topic2'],
        },
    ],
    'name_11': [
        {
            'name': 'manager',
            'entity_type': 'phone_hash_id',
            'entity_name': 'PARK',
            'ttl': datetime.datetime.isoformat(
                _NOW + _1DAY, timespec='seconds',
            ),
            'provider_name': 'name_11',
            'topics': ['topic1'],
        },
        {
            'name': 'programmer',
            'entity_type': 'car_number',
            'entity_name': 'CAR_NUMBER',
            'ttl': datetime.datetime.isoformat(
                _NOW + _2DAYS, timespec='seconds',
            ),
            'provider_name': 'name_11',
            'topics': ['topic0', 'topic2'],
        },
        {
            'name': 'programmer',
            'entity_type': 'park',
            'entity_name': 'PARK',
            'ttl': datetime.datetime.isoformat(
                _NOW + _3DAYS, timespec='seconds',
            ),
            'provider_name': 'name_11',
            'topics': ['topic0', 'topic2'],
        },
    ],
    'name_12': [
        {
            'name': 'programmer',
            'entity_type': 'car_number',
            'entity_name': 'CAR_NUMBER',
            'ttl': 'infinity',
            'provider_name': 'name_12',
            'topics': ['topic0', 'topic2'],
        },
        {
            'name': 'analyst',
            'entity_type': 'car_number',
            'entity_name': 'CAR_NUMBER2',
            'ttl': 'infinity',
            'provider_name': 'name_12',
            'topics': [],
        },
    ],
    'name_13': [
        {
            'name': 'manager',
            'entity_type': 'phone_hash_id',
            'entity_name': 'PARK',
            'ttl': 'infinity',
            'provider_name': 'name_13',
            'topics': ['topic1'],
        },
        {
            'name': 'analyst',
            'entity_type': 'car_number',
            'entity_name': 'CAR_NUMBER2',
            'ttl': 'infinity',
            'provider_name': 'name_13',
            'topics': [],
        },
        {
            'name': 'teamlead',
            'entity_type': 'park',
            'entity_name': 'PARK',
            'ttl': 'infinity',
            'provider_name': 'name_13',
            'topics': [],
        },
    ],
}


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
                tags_tools.Provider.from_id(11, True),
                tags_tools.Provider.from_id(12, True),
                tags_tools.Provider.from_id(13, False),
            ],
        ),
        tags_tools.insert_entities(
            [
                tags_tools.Entity(200, 'PARK', 'phone_hash_id'),
                tags_tools.Entity(201, 'CAR_NUMBER', 'car_number'),
                tags_tools.Entity(202, 'LICENSE2', 'driver_license'),
                tags_tools.Entity(203, 'CAR_NUMBER2', 'car_number'),
                tags_tools.Entity(204, 'PARK', 'park'),
            ],
        ),
        tags_tools.insert_tags(
            [
                tags_tools.Tag(
                    0, 10, 200, ttl=_TTL, entity_type='phone_hash_id',
                ),
                tags_tools.Tag(
                    1, 11, 200, ttl=_NOW + _1DAY, entity_type='phone_hash_id',
                ),
                tags_tools.Tag(1, 13, 200, entity_type='phone_hash_id'),
                tags_tools.Tag(0, 10, 201, entity_type='car_number'),
                tags_tools.Tag(
                    0, 11, 201, ttl=_NOW + _2DAYS, entity_type='car_number',
                ),
                tags_tools.Tag(2, 13, 203, entity_type='car_number'),
                tags_tools.Tag(2, 12, 203, entity_type='car_number'),
                tags_tools.Tag(0, 12, 201, entity_type='car_number'),
                tags_tools.Tag(
                    0, 11, 204, ttl=_NOW + _3DAYS, entity_type='park',
                ),
                tags_tools.Tag(4, 13, 204, entity_type='park'),
            ],
        ),
        tags_tools.insert_topics(
            [
                tags_tools.Topic(1000, 'topic0', False),
                tags_tools.Topic(1001, 'topic1', True),
                tags_tools.Topic(1002, 'topic2', True),
            ],
        ),
        tags_tools.insert_relations(
            [
                tags_tools.Relation(0, 1000),
                tags_tools.Relation(0, 1002),
                tags_tools.Relation(1, 1001),
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'data, expected_tags',
    [
        ({'filters': {'provider': 'name_10'}}, list_answers['name_10']),
        ({'filters': {'provider': 'name_11'}}, list_answers['name_11']),
        ({'filters': {'provider': 'name_12'}}, list_answers['name_12']),
        ({'filters': {'provider': 'name_13'}}, []),
        ({'filters': {'provider': 'name_13'}, 'show_inactive': False}, []),
        (
            {'filters': {'provider': 'name_13'}, 'show_inactive': True},
            list_answers['name_13'],
        ),
        (
            {'filters': {'entity_types': ['car_number']}},
            list_answers['name_11'][1:2]
            + list_answers['name_10']
            + list_answers['name_12'],
        ),
        (
            {'filters': {'provider': 'name_11', 'tag_name': 'programmer'}},
            list_answers['name_11'][1:],
        ),
        (
            {'filters': {'provider': 'name_11', 'tag_name': 'manager'}},
            list_answers['name_11'][:1],
        ),
        (
            {'filters': {'provider': 'name_11', 'entity': 'PARK'}},
            list_answers['name_11'][:1] + list_answers['name_11'][2:],
        ),
        (
            {'filters': {'provider': 'name_11', 'entity_types': ['park']}},
            list_answers['name_11'][2:],
        ),
        (
            {'filters': {'topic': 'topic0', 'entity_types': ['park', 'park']}},
            list_answers['name_11'][2:],
        ),
        (
            {'filters': {'topic': 'topic0'}},
            list_answers['name_10']
            + list_answers['name_11'][1:]
            + list_answers['name_12'][0:1],
        ),
        (
            {'filters': {'topic': 'topic1'}, 'show_inactive': True},
            list_answers['name_11'][:1] + list_answers['name_13'][:1],
        ),
        (
            {
                'filters': {
                    'entity_types': [
                        'user_phone_id',
                        'udid',
                        'dbid_uuid',
                        'personal_phone_id',
                    ],
                },
            },
            [],
        ),
        (
            {
                'filters': {
                    'entity_types': ['car_number', 'park', 'phone_hash_id'],
                },
            },
            list_answers['name_10']
            + list_answers['name_11']
            + list_answers['name_12'],
        ),
        (
            {'filters': {'entity_types': []}, 'show_inactive': True},
            list(tag for tags in list_answers.values() for tag in tags),
        ),
        ({'filters': {'tag_name': 'programmer', 'topic': 'topic1'}}, []),
        (
            {'filters': {'tag_name': 'manager', 'topic': 'topic1'}},
            list_answers['name_11'][:1],
        ),
        (
            {
                'filters': {'tag_name': 'manager', 'topic': 'topic1'},
                'show_inactive': True,
            },
            list_answers['name_11'][:1] + list_answers['name_13'][:1],
        ),
        (
            {
                'filters': {
                    'provider': 'name_10',
                    'tag_name': 'programmer',
                    'entity_types': ['car_number'],
                    'entity': 'CAR_NUMBER',
                    'topic': 'topic2',
                },
            },
            list_answers['name_10'],
        ),
    ],
)
@pytest.mark.nofilldb()
async def test_list(
        taxi_tags, data: Dict[str, Any], expected_tags: List[Dict[str, Any]],
):
    await taxi_tags.invalidate_caches()

    list_response = await taxi_tags.post('v2/list', data)
    assert list_response.status_code == 200
    response = list_response.json()
    tags = response['tags']
    start_pos = data.get('offset', 0)
    end_pos = start_pos + data.get('limit', len(expected_tags))

    checked_tags = 0
    for tag_data in tags:
        checked_tags += 1
        assert tag_data in expected_tags[start_pos:end_pos]
    assert checked_tags == len(expected_tags[start_pos:end_pos])

    if 'limit' in data:
        del data['limit']
    if 'offset' in data:
        del data['offset']

    count_response = await taxi_tags.post('v2/count', data)
    assert count_response.status_code == 200
    count = count_response.json()['count']
    assert count == len(expected_tags)


@pytest.mark.parametrize(
    'data',
    [
        ({'limit': 'not integer'}),
        ({'offset': 'not integer'}),
        ({'limit': -1}),
        ({'filters': {'entity_types': {'object': 'should be list'}}}),
        ({'filters': {'entity_types': ['bad_entity_type']}}),
        ({'filters': {'tag_name': 1234}}),
    ],
)
@pytest.mark.nofilldb()
async def test_list_bad_requests(taxi_tags, data: Dict[str, Any]):
    await taxi_tags.invalidate_caches()

    filter_response = await taxi_tags.post('v2/list', data)
    assert filter_response.status_code == 400


@pytest.mark.parametrize(
    'tvm_enabled, tvm_header', [(False, False), (False, True), (True, True)],
)
@pytest.mark.config(
    TVM_RULES=[{'src': 'reposition', 'dst': constants.TAGS_TVM_NAME}],
)
@pytest.mark.nofilldb()
async def test_with_tvm(
        taxi_tags, taxi_config, load, tvm_enabled: bool, tvm_header: bool,
):
    taxi_config.set_values(dict(TVM_ENABLED=tvm_enabled))

    header_data: Dict[str, Any] = {}
    if tvm_header:
        header_data = {
            'X-Ya-Service-Ticket': load(
                f'tvm2_ticket_18_{constants.TAGS_TVM_ID}',
            ),
        }

    data = {'filters': {'provider': 'non_existing_name'}}
    empty_answer: Dict[str, List[str]] = {'tags': []}

    response = await taxi_tags.post('/v2/list', data, headers=header_data)
    assert response.status_code == 200
    assert response.json() == empty_answer


@pytest.mark.config(
    TVM_RULES=[{'src': 'driver_protocol', 'dst': constants.TAGS_TVM_NAME}],
)
@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.parametrize(
    'header_data, error_text',
    [
        ({}, 'missing or empty X-Ya-Service-Ticket header'),
        (
            {'X-Ya-Service-Ticket': ''},
            'missing or empty X-Ya-Service-Ticket header',
        ),
        (
            {'X-Ya-Service-Ticket': 'INVALID-TOKEN-VALUE'},
            'Bad tvm2 service ticket',
        ),
    ],
)
@pytest.mark.nofilldb()
async def test_check_tvm2(
        taxi_tags, header_data: Dict[str, str], error_text: str,
):
    data = {'filters': {'provider': 'non_existing_name'}}

    response = await taxi_tags.post('v2/list', data, headers=header_data)
    assert response.status_code == 401
    assert response.json() == {'code': '401', 'message': error_text}


@pytest.mark.config(
    TVM_RULES=[{'src': 'driver_protocol', 'dst': constants.TAGS_TVM_NAME}],
)
@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.nofilldb()
async def test_check_tvm2_unknown_source(taxi_tags, load):
    data = {'filters': {'provider': 'non_existing_name'}}

    header_data = {
        'X-Ya-Service-Ticket': load(
            f'tvm2_ticket_999_{constants.TAGS_TVM_ID}',
        ),
    }
    response = await taxi_tags.post('v2/list', data, headers=header_data)
    assert response.status_code == 403
    assert response.json() == {
        'code': '403',
        'message': 'No rule found for source from tvm2 ticket',
    }
