from typing import Any
from typing import Dict
from typing import List

# pylint: disable=import-error
from fbs.tags.handlers.v1_entity_index import Response
import pytest

from tests_tags.tags import tags_tools


_CONTENT_TYPE = 'application/x-flatbuffers'


def _decode_response(response):
    assert response.status_code == 200
    assert response.headers['Content-Type'] == _CONTENT_TYPE

    data = response.content
    root = Response.Response.GetRootAsResponse(data, 0)

    entities = []
    for index in range(root.EntitiesLength()):
        entity_info = root.Entities(index)
        entities.append(
            {
                'type': entity_info.Type().decode('utf-8'),
                'name': entity_info.Name().decode('utf-8'),
                'revision': entity_info.Revision(),
                'updated': entity_info.Updated(),
            },
        )

    return {
        'entities': entities,
        'last_processed_revision': root.LastProcessedRevision(),
        'has_more': root.HasMore(),
    }


@pytest.mark.parametrize(
    'newer_than, limit, entity_types, expected_code',
    [
        (-1, 1, ['user_phone_id'], 400),
        (1, 0, ['user_phone_id'], 400),
        (0, 10, [], 400),
        (1, 10, ['bad_entity_type'], 400),
    ],
)
@pytest.mark.nofilldb()
async def test_bad_request(
        taxi_tags, newer_than, limit, entity_types, expected_code,
):
    response = await taxi_tags.post(
        'v1/entity_index',
        {
            'range': {'newer_than': newer_than, 'limit': limit},
            'entity_types': entity_types,
        },
    )

    assert response.status_code == expected_code


@pytest.mark.pgsql('tags', files=['pg_tags_initial.sql'])
@pytest.mark.parametrize(
    'newer_than, limit, entity_types, '
    'expected_entities, expected_revision, expected_has_more',
    [
        pytest.param(
            0,
            1,
            ['user_phone_id'],
            [
                {
                    'type': 'user_phone_id',
                    'name': 'user_phone_id_0',
                    'revision': 1,
                    'updated': 1577836800000,
                },
            ],
            1,
            True,
            id='limit_1',
        ),
        pytest.param(
            0,
            10,
            ['user_phone_id'],
            [
                {
                    'type': 'user_phone_id',
                    'name': 'user_phone_id_0',
                    'revision': 1,
                    'updated': 1577836800000,
                },
            ],
            10,
            True,
            id='sparse_limit_10_truncates',
        ),
        pytest.param(
            0,
            20,
            ['user_phone_id'],
            [
                {
                    'type': 'user_phone_id',
                    'name': 'user_phone_id_0',
                    'revision': 11,
                    'updated': 1578384000000,
                },
            ],
            12,
            False,
            id='sparse_limit_20',
        ),
        pytest.param(
            0,
            30,
            ['car_number', 'dbid_uuid', 'udid', 'park_car_id'],
            [
                {
                    'type': 'car_number',
                    'name': 'car_number_0',
                    'revision': 12,
                    'updated': 1578294000000,
                },
                {
                    'type': 'udid',
                    'name': 'udid_0',
                    'revision': 4,
                    'updated': 1604458800000,
                },
                {
                    'type': 'dbid_uuid',
                    'name': 'dbid_uuid_0',
                    'revision': 5,
                    'updated': 1604548800000,
                },
                {
                    'type': 'park_car_id',
                    'name': 'park_car_id_0',
                    'revision': 9,
                    'updated': 1604908800000,
                },
                {
                    'type': 'park_car_id',
                    'name': 'park_car_id_1',
                    'revision': 10,
                    'updated': 1604826000000,
                },
            ],
            12,
            False,
            id='driver_limit_30',
        ),
        pytest.param(
            0,
            10,
            ['car_number', 'dbid_uuid', 'udid', 'park_car_id'],
            [
                {
                    'type': 'car_number',
                    'name': 'car_number_0',
                    'revision': 3,
                    'updated': 1578016800000,
                },
                {
                    'type': 'udid',
                    'name': 'udid_0',
                    'revision': 4,
                    'updated': 1604458800000,
                },
                {
                    'type': 'dbid_uuid',
                    'name': 'dbid_uuid_0',
                    'revision': 5,
                    'updated': 1604548800000,
                },
                {
                    'type': 'park_car_id',
                    'name': 'park_car_id_0',
                    'revision': 9,
                    'updated': 1604908800000,
                },
                {
                    'type': 'park_car_id',
                    'name': 'park_car_id_1',
                    'revision': 10,
                    'updated': 1604826000000,
                },
            ],
            10,
            True,
            id='driver_limit_10_truncated',
        ),
        pytest.param(
            11, 10, ['user_phone_id'], [], 12, False, id='no_updates',
        ),
    ],
)
@pytest.mark.nofilldb()
async def test_request(
        taxi_tags,
        newer_than: int,
        limit: int,
        entity_types: List[str],
        expected_entities: List[Dict[str, Any]],
        expected_revision: int,
        expected_has_more: bool,
        pgsql,
):
    first_revision = tags_tools.get_first_revision(pgsql['tags'])
    response = await taxi_tags.post(
        'v1/entity_index',
        {
            'range': {
                'newer_than': newer_than + first_revision - 1,
                'limit': limit,
            },
            'entity_types': entity_types,
        },
    )

    assert response.status_code == 200
    result = _decode_response(response)
    entities = [
        {
            'type': entity['type'],
            'name': entity['name'],
            'revision': entity['revision'] - first_revision + 1,
            'updated': entity['updated'],
        }
        for entity in result['entities']
    ]
    assert entities == expected_entities
    expected_revision = expected_revision + first_revision - 1
    assert result['last_processed_revision'] == expected_revision
    assert result['has_more'] == expected_has_more
