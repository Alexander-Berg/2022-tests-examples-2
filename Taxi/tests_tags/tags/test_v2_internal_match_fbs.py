import datetime
import operator

# pylint: disable=import-error
from fbs.tags.handlers.v2_internal_match_fbs import Response
import pytest

from tests_tags.tags import tags_tools


_NOW = datetime.datetime(2019, 12, 27, 11, 22, 32, 0)
_MINUTE = datetime.timedelta(minutes=1)
_HOUR = datetime.timedelta(hours=1)
_DAY = datetime.timedelta(days=1)
_INFINITY = datetime.datetime(9999, 12, 31, 23, 59, 59, 999999)


def _unpack_v2_internal_match_fbs_response(data):
    root = Response.Response.GetRootAsResponse(data, 0)
    return sorted(
        [
            {
                'id': root.Entities(i).Id().decode('utf-8'),
                'type': root.Entities(i).Type().decode('utf-8'),
                'topic': root.Entities(i).Topic().decode('utf-8'),
                'tags': sorted(
                    [
                        root.Entities(i).Tags(j).decode('utf-8')
                        for j in range(root.Entities(i).TagsLength())
                    ],
                ),
            }
            for i in range(root.EntitiesLength())
        ],
        key=operator.itemgetter('id'),
    )


@pytest.mark.parametrize(
    'expected_code, data',
    [
        # 0. Missing topics & match
        (400, {}),
        # 1. Empty topics
        (
            400,
            {
                'topics': [],
                'match': {
                    'park': [],
                    'dbid_uuid': [],
                    'park_car_id': [],
                    'udid': [],
                },
            },
        ),
        # 2. Missing match type park
        (
            400,
            {
                'topics': ['sample'],
                'match': {'dbid_uuid': [], 'park_car_id': [], 'udid': []},
            },
        ),
        # 3. Missing match type dbid_uuid
        (
            400,
            {
                'topics': ['sample'],
                'match': {'park': [], 'park_car_id': [], 'udid': []},
            },
        ),
        # 4. Missing match type park_car_id
        (
            400,
            {
                'topics': ['sample'],
                'match': {'park': [], 'dbid_uuid': [], 'udid': []},
            },
        ),
        # 5. Missing match type udid
        (
            400,
            {
                'topics': ['sample'],
                'match': {'park': [], 'dbid_uuid': [], 'park_car_id': []},
            },
        ),
        # 6. Extra types
        (
            400,
            {
                'topics': [],
                'match': {
                    'park': [],
                    'dbid_uuid': [],
                    'park_car_id': [],
                    'udid': [],
                },
            },
        ),
        # 7. Correct request
        (
            200,
            {
                'topics': ['sample'],
                'match': {
                    'park': [],
                    'dbid_uuid': [],
                    'park_car_id': [],
                    'udid': [],
                },
            },
        ),
    ],
)
@pytest.mark.pgsql('tags')
@pytest.mark.nofilldb()
async def test_request_data(taxi_tags, expected_code: int, data):
    response = await taxi_tags.post('v2/internal/match_fbs', data)
    assert response.status_code == expected_code


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_tag_names(
            [
                tags_tools.TagName(2000, 'tag0'),
                tags_tools.TagName(2001, 'tag1'),
                tags_tools.TagName(2002, 'tag2'),
                tags_tools.TagName(2003, 'tag3'),
            ],
        ),
        tags_tools.insert_topics(
            [
                tags_tools.Topic(1500, 'topic0', False),
                tags_tools.Topic(1501, 'topic1', True),
            ],
        ),
        tags_tools.insert_relations(
            [
                tags_tools.Relation(2000, 1500),  # tag0 topic0
                tags_tools.Relation(2001, 1501),  # tag1 topic1
                tags_tools.Relation(2002, 1501),  # tag2 topic1
                tags_tools.Relation(2003, 1501),  # tag3 topic1
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
                # has tags
                tags_tools.Entity(3000, 'dbid1', 'park'),
                tags_tools.Entity(3001, 'dbid1_uuid1', 'dbid_uuid'),
                tags_tools.Entity(3002, 'dbid1_car1', 'park_car_id'),
                tags_tools.Entity(3003, 'udid1', 'udid'),
                # no tags
                tags_tools.Entity(4000, 'dbid2', 'park'),
                tags_tools.Entity(4001, 'dbid2_uuid2', 'dbid_uuid'),
                tags_tools.Entity(4002, 'dbid2_car2', 'park_car_id'),
                tags_tools.Entity(4003, 'udid2', 'udid'),
            ],
        ),
        tags_tools.insert_tags(
            [
                # outdated tag unwanted topic disabled provider
                tags_tools.Tag(2000, 1001, 3001, ttl=_NOW - _HOUR),
                # outdated tag wanted topic disabled provider
                tags_tools.Tag(2001, 1001, 3001, ttl=_NOW - _HOUR),
                # outdated tag wanted topic enabled provider
                tags_tools.Tag(2001, 1000, 3002, ttl=_NOW - _HOUR),
                # unwanted topic disabled provider
                tags_tools.Tag(2000, 1001, 3002, ttl=_NOW + _HOUR),
                # wanted topic disabled provider
                tags_tools.Tag(2001, 1001, 3003, ttl=_NOW + _HOUR),
                # wanted topic enabled provider
                tags_tools.Tag(2001, 1000, 3000, ttl=_NOW + _HOUR),
                tags_tools.Tag(2002, 1000, 3001, ttl=_NOW + _HOUR),
                tags_tools.Tag(2003, 1000, 3002, ttl=_NOW + _HOUR),
                # wanted topic enabled provider no ttl
                tags_tools.Tag(2003, 1000, 3003),
            ],
            _NOW,
        ),
    ],
)
async def test_match(taxi_tags):
    data = {
        'topics': ['topic1'],
        'match': {
            'park': ['dbid1', 'dbid2'],
            'dbid_uuid': ['dbid1_uuid1', 'dbid2_uuid2'],
            'park_car_id': ['dbid1_car1', 'dbid2_car2'],
            'udid': ['udid1', 'udid2'],
        },
    }
    response = await taxi_tags.post('v2/internal/match_fbs', data)
    assert response.status_code == 200
    assert _unpack_v2_internal_match_fbs_response(response.content) == [
        {'id': 'dbid1', 'tags': ['tag1'], 'topic': 'topic1', 'type': 'park'},
        {
            'id': 'dbid1_car1',
            'tags': ['tag3'],
            'topic': 'topic1',
            'type': 'park_car_id',
        },
        {
            'id': 'dbid1_uuid1',
            'tags': ['tag2'],
            'topic': 'topic1',
            'type': 'dbid_uuid',
        },
        {'id': 'udid1', 'tags': ['tag3'], 'topic': 'topic1', 'type': 'udid'},
    ]
