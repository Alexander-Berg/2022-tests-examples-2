import datetime

import pytest

from tests_tags.tags import tags_tools


_NOW = datetime.datetime(2019, 11, 8, 12, 45, 32)
_HOUR_AFTER = _NOW + datetime.timedelta(hours=1)
_MINUTE_AGO = _NOW - datetime.timedelta(minutes=1)


@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_tag_names(
            [
                tags_tools.TagName(0, 'tag0'),
                tags_tools.TagName(1, 'tag1'),
                tags_tools.TagName(2, 'unused_tag'),
            ],
        ),
        tags_tools.insert_providers(
            [
                tags_tools.Provider(0, 'provider0', '', True),
                tags_tools.Provider(1, 'provider1', '', True),
                tags_tools.Provider(2, 'disabled_provider2', '', False),
            ],
        ),
        tags_tools.insert_entities(
            [
                tags_tools.Entity(0, 'udid0', entity_type='udid'),
                tags_tools.Entity(1, 'udid1', entity_type='udid'),
                tags_tools.Entity(2, 'park2', entity_type='park'),
                tags_tools.Entity(3, 'car_number3', entity_type='car_number'),
            ],
        ),
        tags_tools.insert_tags(
            [
                tags_tools.Tag(0, 0, 0, entity_type='udid'),
                tags_tools.Tag(0, 0, 3, entity_type='car_number'),
                tags_tools.Tag(0, 1, 1, entity_type='udid'),
                tags_tools.Tag(
                    0, 1, 3, ttl=_MINUTE_AGO, entity_type='car_number',
                ),
                tags_tools.Tag(
                    0, 2, 2, entity_type='park',
                ),  # disabled provider
                tags_tools.Tag(1, 0, 1, entity_type='udid'),
                tags_tools.Tag(1, 0, 3, entity_type='car_number'),
                tags_tools.Tag(1, 1, 2, ttl=_HOUR_AFTER, entity_type='park'),
                tags_tools.Tag(
                    1, 1, 3, ttl=_MINUTE_AGO, entity_type='car_number',
                ),
                tags_tools.Tag(
                    1, 2, 0, entity_type='udid',
                ),  # disabled provider
            ],
        ),
        tags_tools.insert_topics([tags_tools.Topic(1000, 'topic0', True)]),
        tags_tools.insert_relations([tags_tools.Relation(0, 1000)]),
    ],
)
@pytest.mark.parametrize(
    'filters, columns, expected_code, expected_data',
    [
        (None, {'tag_name': 'Название тега'}, 400, None),
        ({}, None, 400, None),
        ({}, {}, 400, None),
        ({}, {'tag_name': ''}, 400, None),
        (
            {'entity_types': ['bad_type']},
            {'tag_name': 'Название тега'},
            400,
            None,
        ),
        (
            {'provider': 'not_existing'},
            {'tag_name': 'Название тега', 'provider': 'Поставщик'},
            200,
            ['Название тега,Поставщик'],
        ),
        (
            {'tag_name': 'not_existing'},
            {'tag_name': 'Название тега'},
            200,
            ['Название тега'],
        ),
        (
            {'entity_types': ['dbid_uuid']},
            {'tag_name': 'Название тега'},
            200,
            ['Название тега'],
        ),
        (
            {'entity': 'not_existing'},
            {'tag_name': 'Название тега'},
            200,
            ['Название тега'],
        ),
        (
            {'topic': 'not_existing'},
            {'tag_name': 'Название тега'},
            200,
            ['Название тега'],
        ),
        (
            {},
            {'tag_name': 'Название тега'},
            200,
            ['Название тега', 'tag0', 'tag1'],
        ),
        (
            {'entity_types': ['dbid_uuid']},
            {'tag_name': 'Some custom column name'},
            200,
            ['Some custom column name'],
        ),
        (
            {},
            {'tag_name': 'Название тега', 'entity_type': 'Тип'},
            200,
            [
                'Название тега,Тип',
                'tag0,udid',
                'tag0,car_number',
                'tag1,udid',
                'tag1,car_number',
                'tag1,park',
            ],
        ),
        (
            {},
            {
                'tag_name': 'Название',
                'entity_type': 'Тип',
                'entity': 'Значение',
                'provider': 'Поставщик',
                'ttl': 'Время жизни',
            },
            200,
            [
                'Название,Тип,Значение,Поставщик,Время жизни',
                'tag0,udid,udid0,provider0,infinity',
                'tag0,car_number,car_number3,provider0,infinity',
                'tag0,udid,udid1,provider1,infinity',
                'tag1,udid,udid1,provider0,infinity',
                'tag1,car_number,car_number3,provider0,infinity',
                'tag1,park,park2,provider1,' + _HOUR_AFTER.isoformat(),
            ],
        ),
        (
            {},
            {'tag_name': 'Название', 'entity_type': 'Тип'},
            200,
            [
                'Название,Тип',
                'tag0,udid',
                'tag0,car_number',
                'tag1,udid',
                'tag1,car_number',
                'tag1,park',
            ],
        ),
        (
            {},
            {'tag_name': 'Название', 'provider': 'Поставщик'},
            200,
            [
                'Название,Поставщик',
                'tag0,provider0',
                'tag0,provider1',
                'tag1,provider0',
                'tag1,provider1',
            ],
        ),
        (
            {'provider': 'provider0', 'entity_types': ['udid']},
            {
                'tag_name': 'Название',
                'entity_type': 'Тип',
                'provider': 'Поставщик',
                'ttl': 'Время жизни',
            },
            200,
            [
                'Название,Тип,Поставщик,Время жизни',
                'tag0,udid,provider0,infinity',
                'tag1,udid,provider0,infinity',
            ],
        ),
        (
            {
                'provider': 'provider0',
                'entity_types': ['udid'],
                'tag_name': 'tag0',
                'entity': 'udid0',
                'topic': 'topic0',
            },
            {
                'tag_name': 'Название',
                'entity_type': 'Тип',
                'entity': 'Значение',
                'provider': 'Поставщик',
                'ttl': 'Время жизни',
            },
            200,
            [
                'Название,Тип,Значение,Поставщик,Время жизни',
                'tag0,udid,udid0,provider0,infinity',
            ],
        ),
    ],
)
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.pgsql('tags', queries=[])
@pytest.mark.nofilldb()
async def test_tags_snapshot(
        taxi_tags, filters, columns, expected_code, expected_data,
):
    data = {}
    if filters is not None:
        data['filters'] = filters
    if columns is not None:
        data['columns'] = columns

    response = await taxi_tags.post('v1/admin/tags/csv', data)
    assert response.status_code == expected_code
    if expected_code == 200:
        rows = response.content.decode('utf-8').split('\n')
        assert len(rows) == len(expected_data)
        assert rows[0] == expected_data[0]
        if len(rows) > 1:
            assert rows[1:].sort() == expected_data[1:].sort()
