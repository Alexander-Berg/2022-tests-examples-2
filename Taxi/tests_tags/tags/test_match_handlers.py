import datetime

# pylint: disable=import-error
from fbs.tags.handlers.v2_match_fbs import Entity
from fbs.tags.handlers.v2_match_fbs import Match
from fbs.tags.handlers.v2_match_fbs import Request
from fbs.tags.handlers.v2_match_fbs import Response
import flatbuffers
import pytest

from tests_tags.tags import tags_select
from tests_tags.tags import tags_tools


_NOW = datetime.datetime(2019, 12, 27, 11, 22, 32, 0)
_MINUTE = datetime.timedelta(minutes=1)
_HOUR = datetime.timedelta(hours=1)
_DAY = datetime.timedelta(days=1)
_INFINITY = datetime.datetime(9999, 12, 31, 23, 59, 59, 999999)

_FBS_HEADER = {'Content-Type': 'application/x-flatbuffers'}


def _pack_v2_match_fbs_request(request_json):
    builder = flatbuffers.Builder(0)

    topics = request_json['topics'] if 'topics' in request_json else []
    fbs_topics = [builder.CreateString(topic) for topic in topics]
    Request.RequestStartTopicsVector(builder, len(fbs_topics))
    for fbs_topic in reversed(fbs_topics):
        builder.PrependUOffsetTRelative(fbs_topic)
    fbs_topics = builder.EndVector(len(fbs_topics))

    entities = request_json['entities'] if 'entities' in request_json else []
    fbs_entities = []
    for entity in entities:
        fbs_matches = []
        for match in entity['match']:
            fbs_type = builder.CreateString(match['type'])
            fbs_value = builder.CreateString(match['value'])
            Match.MatchStart(builder)
            Match.MatchAddType(builder, fbs_type)
            Match.MatchAddValue(builder, fbs_value)
            fbs_matches.append(Match.MatchEnd(builder))
        Entity.EntityStartMatchVector(builder, len(fbs_matches))
        for fbs_match in reversed(fbs_matches):
            builder.PrependUOffsetTRelative(fbs_match)
        fbs_matches = builder.EndVector(len(fbs_matches))

        fbs_id = builder.CreateString(entity['id'])
        Entity.EntityStart(builder)
        Entity.EntityAddId(builder, fbs_id)
        Entity.EntityAddMatch(builder, fbs_matches)
        fbs_entities.append(Entity.EntityEnd(builder))

    Request.RequestStartEntitiesVector(builder, len(fbs_entities))
    for fbs_entity in reversed(fbs_entities):
        builder.PrependUOffsetTRelative(fbs_entity)
    fbs_entities = builder.EndVector(len(fbs_entities))

    Request.RequestStart(builder)
    Request.RequestAddTopics(builder, fbs_topics)
    Request.RequestAddEntities(builder, fbs_entities)
    request_fbs = Request.RequestEnd(builder)
    builder.Finish(request_fbs)
    return builder.Output()


def _unpack_v2_match_fbs_response(data):
    root = Response.Response.GetRootAsResponse(data, 0)
    entities = []
    for i in range(root.EntitiesLength()):
        entity = root.Entities(i)
        tags = [
            entity.Tags(j).decode('utf-8') for j in range(entity.TagsLength())
        ]
        entities.append({'id': entity.Id().decode('utf-8'), 'tags': tags})
    return {'entities': entities}


@pytest.mark.parametrize(
    'expected_code, expected_fbs_code, data',
    [
        # No entities specified
        (400, 200, {}),
        # No entities at all
        (200, 200, {'entities': []}),
        # Valid entity
        (
            200,
            200,
            {
                'entities': [
                    {'id': 'a', 'match': [{'type': 'udid', 'value': 'abc'}]},
                ],
            },
        ),
        # Duplicate group ids found
        (
            200,
            200,
            {
                'entities': [
                    {'id': 'a', 'match': [{'type': 'udid', 'value': 'abc'}]},
                    {
                        'id': 'a',
                        'match': [{'type': 'driver_license', 'value': 'cda'}],
                    },
                ],
            },
        ),
        # Duplicate group ids found
        (
            200,
            200,
            {
                'entities': [
                    {'id': 'a', 'match': [{'type': 'udid', 'value': 'abc'}]},
                    {'id': 'a', 'match': [{'type': 'udid', 'value': 'abc'}]},
                ],
            },
        ),
        # Unknown entity type
        (
            400,
            400,
            {
                'entities': [
                    {
                        'id': 'a',
                        'match': [{'type': 'unkown_type', 'value': 'abc'}],
                    },
                ],
            },
        ),
        # Entity without any match
        (200, 200, {'entities': [{'id': 'a', 'match': []}]}),
    ],
)
@pytest.mark.pgsql('tags')
@pytest.mark.nofilldb()
async def test_request_data(
        taxi_tags, expected_code: int, expected_fbs_code: int, data,
):
    response = await taxi_tags.post('v2/match', data)
    assert response.status_code == expected_code

    for url in ['v2/match_fbs', 'v1/internal/match_fbs']:
        request = _pack_v2_match_fbs_request(data)
        response = await taxi_tags.post(url, headers=_FBS_HEADER, data=request)
        assert response.status_code == expected_fbs_code


def _verify_single_match(response, expected_tags):
    assert response.status_code == 200
    response = response.json()
    response['tags'].sort()

    assert response == {'tags': expected_tags}


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_tag_names(
            [
                tags_tools.TagName(2000, 'programmer'),
                tags_tools.TagName(2001, 'manager'),
                tags_tools.TagName(2002, 'engineer'),
            ],
        ),
        tags_tools.insert_topics(
            [
                tags_tools.Topic(1500, 'tech', False),
                tags_tools.Topic(1501, 'humanist', True),
            ],
        ),
        tags_tools.insert_relations(
            [
                # Tech programmer
                tags_tools.Relation(2000, 1500),
                # Humanist manager
                tags_tools.Relation(2001, 1501),
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
                tags_tools.Tag(2000, 1000, 3000, ttl=_NOW - _HOUR),
                # programmer tag for LICENSE entity (disabled provider)
                tags_tools.Tag(2000, 1001, 3000, ttl=_NOW + _MINUTE),
                # programmer tag for CAR_NUMBER entity
                tags_tools.Tag(2000, 1000, 3001, ttl=_NOW + _MINUTE),
                # programmer tag for CAR_NUMBER entity (disabled provider)
                tags_tools.Tag(2000, 1001, 3001),
                # programmer tag for CAR_NUMBER entity
                tags_tools.Tag(2000, 1002, 3001, ttl=_NOW + _HOUR),
                # programmer tag for PARK_ID entity
                tags_tools.Tag(2000, 1000, 3002),
                # manager tag for CAR_NUMBER entity
                tags_tools.Tag(2001, 1000, 3001, ttl=_NOW + _DAY),
                # engineer tag for CAR_NUMBER entity
                tags_tools.Tag(2002, 1000, 3001),
            ],
            _NOW,
        ),
    ],
)
@pytest.mark.parametrize(
    'requested_entities, topics, expected_entities, expected_fbs_entities',
    [
        ([], None, [], []),
        ([], [], [], []),
        # Entity without match specified
        ([{'id': 'a', 'match': []}], None, [], [{'id': 'a', 'tags': []}]),
        # No tags - no entities in response
        (
            [
                {
                    'id': 'a',
                    'match': [{'value': 'LICENSE', 'type': 'driver_license'}],
                },
            ],
            None,
            [],
            [{'id': 'a', 'tags': []}],
        ),
        (
            [
                {
                    'id': 'a',
                    'match': [{'value': 'LICENSE', 'type': 'driver_license'}],
                },
                {'id': 'b', 'match': [{'value': 'PARK_ID', 'type': 'park'}]},
            ],
            ['tech'],
            [{'id': 'b', 'tags': ['programmer']}],
            [{'id': 'a', 'tags': []}, {'id': 'b', 'tags': ['programmer']}],
        ),
        pytest.param(
            [
                {'id': 'b', 'match': [{'value': 'PARK_ID', 'type': 'park'}]},
                {'id': 'b', 'match': [{'value': 'PARK_ID', 'type': 'park'}]},
            ],
            ['tech', 'humanist', 'comissions'],
            [{'id': 'b', 'tags': ['programmer']}],
            [
                {'id': 'b', 'tags': ['programmer']},
                {'id': 'b', 'tags': ['programmer']},
            ],
            id='duplicate_entities',
        ),
        pytest.param(
            [
                {'id': 'c', 'match': [{'value': 'PARK_ID', 'type': 'park'}]},
                {'id': 'd', 'match': [{'value': 'PARK_ID', 'type': 'park'}]},
                {'id': 'b', 'match': [{'value': 'PARK_ID', 'type': 'park'}]},
            ],
            ['tech', 'humanist', 'comissions'],
            [
                {'id': 'c', 'tags': ['programmer']},
                {'id': 'd', 'tags': ['programmer']},
                {'id': 'b', 'tags': ['programmer']},
            ],
            [
                {'id': 'c', 'tags': ['programmer']},
                {'id': 'd', 'tags': ['programmer']},
                {'id': 'b', 'tags': ['programmer']},
            ],
            id='same_order_check',
        ),
        (
            [
                {
                    'id': 'a',
                    'match': [
                        {'value': 'LICENSE', 'type': 'driver_license'},
                        {'value': 'PARK_ID', 'type': 'park'},
                    ],
                },
            ],
            None,
            [{'id': 'a', 'tags': ['programmer']}],
            [{'id': 'a', 'tags': ['programmer']}],
        ),
        # Single tag
        (
            [
                {
                    'id': 'a',
                    'match': [{'value': 'CAR_NUMBER', 'type': 'car_number'}],
                },
            ],
            None,
            [{'id': 'a', 'tags': ['engineer', 'manager', 'programmer']}],
            [{'id': 'a', 'tags': ['engineer', 'manager', 'programmer']}],
        ),
        # Single tag, skip programmer tag because of topic
        (
            [
                {
                    'id': 'a',
                    'match': [{'value': 'CAR_NUMBER', 'type': 'car_number'}],
                },
            ],
            ['humanist'],
            [{'id': 'a', 'tags': ['manager']}],
            [{'id': 'a', 'tags': ['manager']}],
        ),
        # Two entities with programmer tag, one also possesses with manager tag
        (
            [
                {
                    'id': 'a',
                    'match': [
                        {'value': 'CAR_NUMBER', 'type': 'car_number'},
                        {'value': 'PARK_ID', 'type': 'park'},
                    ],
                },
            ],
            ['comissions', 'tech', 'humanist'],
            [{'id': 'a', 'tags': ['manager', 'programmer']}],
            [{'id': 'a', 'tags': ['manager', 'programmer']}],
        ),
        # Same entities in reverse order
        (
            [
                {
                    'id': 'a',
                    'match': [
                        {'value': 'PARK_ID', 'type': 'park'},
                        {'value': 'CAR_NUMBER', 'type': 'car_number'},
                    ],
                },
            ],
            ['humanist', 'tech', 'comissions'],
            [{'id': 'a', 'tags': ['manager', 'programmer']}],
            [{'id': 'a', 'tags': ['manager', 'programmer']}],
        ),
    ],
)
@pytest.mark.nofilldb()
async def test_match(
        taxi_tags,
        requested_entities,
        topics,
        expected_entities,
        expected_fbs_entities,
):
    tags_ttl = {
        'CAR_NUMBER': {
            'programmer': _NOW + _HOUR,
            'manager': _NOW + _DAY,
            'engineer': _INFINITY,
        },
        'LICENSE': {},
        'PARK_ID': {'programmer': _INFINITY},
    }
    tags_topics = {'programmer': ['tech'], 'manager': ['humanist']}

    data = {'entities': requested_entities or []}
    if topics is not None:
        data['topics'] = topics

    await taxi_tags.invalidate_caches()

    for url in ['v2/match']:
        response = await taxi_tags.post(url, data)
        assert response.status_code == 200
        response = response.json()
        assert 'entities' in response
        for entity_with_tags in response['entities']:
            entity_with_tags['tags'].sort()
        assert response['entities'] == expected_entities

    for url in ['v2/match_fbs', 'v1/internal/match_fbs']:
        request = _pack_v2_match_fbs_request(data)
        response = await taxi_tags.post(url, headers=_FBS_HEADER, data=request)
        assert response.status_code == 200
        response = _unpack_v2_match_fbs_response(response.content)
        assert 'entities' in response
        for entity_with_tags in response['entities']:
            entity_with_tags['tags'].sort()
        assert response['entities'] == expected_fbs_entities

    if len(requested_entities) == 1:
        match = requested_entities[0]['match']
        data = {'match': match}
        if topics is not None:
            data['topics'] = topics

        expected_tags = (
            expected_entities[0]['tags'] if expected_entities else []
        )
        response = await taxi_tags.post('v2/match_single', data)
        _verify_single_match(response, expected_tags)
        response = await taxi_tags.post('v2/match_urgent', data)
        _verify_single_match(response, expected_tags)

        response = await taxi_tags.post('v3/match_single', data)
        response = response.json()

        expected_tags_info = {}
        for tag in expected_tags:
            expected_tags_info[tag] = dict()

            entity_values = [match_item['value'] for match_item in match]
            ttl = max(
                [
                    tags_ttl[entity_value][tag]
                    for entity_value in entity_values
                    if tag in tags_ttl[entity_value]
                ],
            )
            if ttl is not _INFINITY:
                expected_tags_info[tag]['ttl'] = ttl.isoformat() + '+0000'
            if tag in tags_topics:
                expected_tags_info[tag]['topics'] = tags_topics[tag]

        assert response == {'tags': expected_tags_info}


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_tag_names(
            [
                tags_tools.TagName(2000, 'programmer'),
                tags_tools.TagName(2001, 'manager'),
            ],
        ),
        tags_tools.insert_topics([tags_tools.Topic(1500, 'tech', False)]),
        tags_tools.insert_relations(
            [tags_tools.Relation(2000, 1500), tags_tools.Relation(2001, 1500)],
        ),
        tags_tools.insert_providers([tags_tools.Provider.from_id(1000, True)]),
        tags_tools.insert_entities(
            [
                # car_number entity
                tags_tools.Entity(3000, 'CAR_NUMBER', 'car_number'),
            ],
        ),
        tags_tools.insert_tags(
            [
                # programmer tag for CAR_NUMBER entity
                tags_tools.Tag(2000, 1000, 3000, ttl=_NOW + _MINUTE),
            ],
            _NOW,
        ),
    ],
)
@pytest.mark.nofilldb()
async def test_match_cache(taxi_tags, pgsql, testpoint):
    await taxi_tags.invalidate_caches()

    queries = [
        tags_tools.insert_entities(
            [
                # park entity
                tags_tools.Entity(3001, 'PARK_ID', 'park'),
            ],
        ),
        tags_tools.insert_tags(
            [
                # manager tag for PARK_ID entity
                tags_tools.Tag(2001, 1000, 3001),
            ],
            _NOW,
        ),
    ]
    tags_tools.apply_queries(pgsql['tags'], queries)

    data = {
        'entities': [
            {
                'id': 'a',
                'match': [
                    {'value': 'CAR_NUMBER', 'type': 'car_number'},
                    {'value': 'PARK_ID', 'type': 'park'},
                ],
            },
        ],
        'topics': ['tech'],
    }

    response = await taxi_tags.post('v2/match', data)
    assert response.status_code == 200
    json = response.json()
    assert 'entities' in json
    for entity_with_tags in json['entities']:
        entity_with_tags['tags'].sort()
    expected = [{'id': 'a', 'tags': ['programmer']}]
    assert json['entities'] == expected

    # make sure that state.entities are not changed
    rows = tags_select.select_table_named(
        'state.entities', 'id', pgsql['tags'],
    )
    assert rows == [
        {'id': 3000, 'value': 'CAR_NUMBER', 'type': 'car_number'},
        {'id': 3001, 'value': 'PARK_ID', 'type': 'park'},
    ]

    latest_revision = tags_tools.get_latest_revision(pgsql['tags'])
    for url, expected_tags, required_revision, db_usage in [
            ('v2/match_fbs', ['programmer'], None, None),
            ('v1/internal/match_fbs', ['programmer'], 0, False),
            ('v1/internal/match_fbs', ['manager', 'programmer'], None, True),
            (
                'v1/internal/match_fbs',
                ['manager', 'programmer'],
                latest_revision,
                True,
            ),
    ]:

        @testpoint('fetch_tags_from_db')
        def _fetch_tags_from_db(arg):
            pass

        @testpoint('fetch_tags_from_cache')
        def _fetch_tags_from_cache(arg):
            pass

        if required_revision is not None:
            url += f'?required_revision={required_revision}'

        request = _pack_v2_match_fbs_request(data)
        response = await taxi_tags.post(url, headers=_FBS_HEADER, data=request)
        assert response.status_code == 200
        response = _unpack_v2_match_fbs_response(response.content)
        assert 'entities' in response
        for entity_with_tags in response['entities']:
            entity_with_tags['tags'].sort()
        expected = [{'id': 'a', 'tags': expected_tags}]
        assert response['entities'] == expected

        assert _fetch_tags_from_db.has_calls is (db_usage is True)
        assert _fetch_tags_from_cache.has_calls is (db_usage is False)

        # make sure that state.entities are not changed
        rows = tags_select.select_table_named(
            'state.entities', 'id', pgsql['tags'],
        )
        assert rows == [
            {'id': 3000, 'value': 'CAR_NUMBER', 'type': 'car_number'},
            {'id': 3001, 'value': 'PARK_ID', 'type': 'park'},
        ]


@pytest.mark.nofilldb()
async def test_metric_calls(taxi_tags, statistics):
    async with statistics.capture(taxi_tags) as capture:
        data = {
            'entities': [
                {
                    'id': 'a',
                    'match': [
                        {'value': 'CAR_NUMBER', 'type': 'car_number'},
                        {'value': 'PARK_ID', 'type': 'park'},
                    ],
                },
            ],
            'topics': ['tech'],
        }
        request = _pack_v2_match_fbs_request(data)
        await taxi_tags.post(
            'v1/internal/match_fbs', headers=_FBS_HEADER, data=request,
        )

    metric_prefix = 'tags.v1_internal_match_fbs.pg'
    assert capture.statistics == {
        f'{metric_prefix}.get_active_tag_names_by_entity_ids.success': 1,
        f'{metric_prefix}.get_entities_by_names.success': 2,
        f'{metric_prefix}.get_topics_relations.success': 1,
    }
