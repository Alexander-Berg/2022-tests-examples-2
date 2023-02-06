# pylint: disable=C0302
import typing

import pytest
# pylint: disable=import-error
from yandex.taxi.tags.snapshot import Response


_CONTENT_TYPE = 'application/x-flatbuffers'

_INITIAL_INDEX = {
    'park_car_id::PARK_CAR0': {'tag0'},
    'park_car_id::PARK_CAR1': {'tag0'},
    'park_car_id::PARK_CAR2': {'tag2'},
}

_INITIAL_INDEX_TOPIC = {
    'park_car_id::PARK_CAR0': {'tag0'},
    'park_car_id::PARK_CAR1': {'tag0'},
}


# Returns cache revision and entities tags
def _decode_response(
        response,
) -> typing.Tuple[int, typing.Dict[str, typing.Set[str]]]:
    assert response.status_code == 200
    assert response.headers['Content-Type'] == _CONTENT_TYPE

    data = response.content
    root = Response.Response.GetRootAsResponse(data, 0)
    revision: int = root.Revision()

    entities_tags: typing.Dict[str, typing.Set[str]] = dict()
    if root.EntitiesTagsLength():
        for entity_it in range(0, root.EntitiesTagsLength()):
            entity_tags = root.EntitiesTags(entity_it)
            entity_type = entity_tags.Type().decode('utf-8')
            entity_name = entity_tags.Name().decode('utf-8')
            tags: typing.Set[str] = set()
            assert entity_tags.TagsLength() > 0
            for tag_it in range(0, entity_tags.TagsLength()):
                tags.add(entity_tags.Tags(tag_it).decode('utf-8'))

            # Just to store results into a dictionary
            entity_id = f'{entity_type}::{entity_name}'
            assert entity_id not in entities_tags
            entities_tags[entity_id] = tags

    return revision, entities_tags


async def _perform_snapshot_request(
        taxi_tags,
        entity_types: typing.List[str],
        topics: typing.Optional[typing.List[str]],
        parts: int,
        part_no: int,
        consumer: str = 'testsuite',
):
    data = {'entity_types': entity_types, 'parts': parts, 'part': part_no}
    if topics is not None:
        data['topics'] = topics

    return await taxi_tags.post(f'/v1/snapshot?consumer={consumer}', data)


# Acquires full tags snapshot using sequential calls to /v1/snapshot
async def _acquire_full_snapshot(
        taxi_tags,
        entity_types: typing.List[str],
        topics: typing.Optional[typing.List[str]],
        parts: int,
        consumer: str = 'testsuite',
):
    revision = None
    entities_tags = dict()

    for part_no in range(0, parts):
        chunk_response = await _perform_snapshot_request(
            taxi_tags=taxi_tags,
            entity_types=entity_types,
            topics=topics,
            parts=parts,
            part_no=part_no,
            consumer=consumer,
        )
        chunk_revision, chunk_data = _decode_response(chunk_response)

        if revision is None:
            revision = chunk_revision
        else:
            # Should not change between the calls to the same service instance
            assert revision == chunk_revision

        for entity_id in chunk_data:
            # Should not be any duplicates between different parts
            assert entity_id not in entities_tags

            entities_tags[entity_id] = chunk_data[entity_id]

    return revision, entities_tags


@pytest.mark.pgsql('tags', files=['pg_tags_initial.sql'])
@pytest.mark.parametrize(
    'parts_count, entity_types, topics, expected_entities',
    [
        pytest.param(
            1,
            ['park_car_id', 'udid', 'car_number'],
            None,
            _INITIAL_INDEX,
            id='one-chunk',
        ),
        pytest.param(
            2,
            ['park_car_id', 'udid', 'car_number'],
            None,
            _INITIAL_INDEX,
            id='two-chunks',
        ),
        pytest.param(
            17,
            ['park_car_id', 'udid', 'car_number'],
            None,
            _INITIAL_INDEX,
            id='17-chunks',
        ),
        pytest.param(
            3,
            ['park_car_id'],
            ['topic0'],
            _INITIAL_INDEX_TOPIC,
            id='filtered-by-topic',
        ),
    ],
)
@pytest.mark.nofilldb()
async def test_full_snapshot(
        taxi_tags,
        parts_count: int,
        entity_types: typing.List[str],
        topics: typing.Optional[typing.List[str]],
        expected_entities,
):
    revision, entities_tags = await _acquire_full_snapshot(
        taxi_tags, entity_types=entity_types, topics=topics, parts=parts_count,
    )

    assert revision > 0
    assert entities_tags == expected_entities
