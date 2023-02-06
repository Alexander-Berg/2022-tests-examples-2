import datetime

import pytest

from replication.configuration.mapping import raw_loaders


@pytest.mark.parametrize(
    'source_type, doc, expected_doc',
    [
        (
            'mongo',
            {
                'data': {
                    '_id': 'id1',
                    'some_key': 'some_value',
                    '__raw_bson': (
                        b'+\x00\x00\x00\x02_id\x00\x04\x00\x00\x00id1'
                        b'\x00\x02some_key\x00\x0b\x00\x00\x00some_value'
                        b'\x00\x00'
                    ),
                },
            },
            {
                '__raw_bson': (
                    b'+\x00\x00\x00\x02_id\x00\x04\x00\x00'
                    b'\x00id1\x00\x02some_key\x00\x0b\x00\x00'
                    b'\x00some_value\x00\x00'
                ),
                '__raw_json': '{"_id": "id1", "some_key": "some_value"}',
                '_id': 'id1',
                'some_key': 'some_value',
            },
        ),
        (
            'api',
            {
                'data': {
                    '_id': 'id1',
                    'data': {
                        'updated': datetime.datetime(2022, 6, 24, 12, 0, 0),
                    },
                },
            },
            {
                '__raw_json': {
                    '_id': 'id1',
                    'data': {'updated': datetime.datetime(2022, 6, 24, 12, 0)},
                },
                '_id': 'id1',
                'data': {'updated': datetime.datetime(2022, 6, 24, 12, 0)},
            },
        ),
        (
            'postgres',
            {
                'data': {
                    '_id': 'id1',
                    '__raw_json': {
                        'updated': datetime.datetime(2022, 6, 24, 12, 0, 0),
                    },
                    'updated': datetime.datetime(2022, 6, 24, 12, 0, 0),
                },
            },
            {
                '__raw_json': (
                    '{"__raw_json": {"updated": {"$a": {"raw_type": '
                    '"datetime"}, "$v": "2022-06-24T12:00:00"}}, "_i'
                    'd": "id1", "updated": {"$a": {"raw_type": "date'
                    'time"}, "$v": "2022-06-24T12:00:00"}}'
                ),
                '_id': 'id1',
                'updated': datetime.datetime(2022, 6, 24, 12, 0),
            },
        ),
    ],
)
def test_pass_raw_json(replication_ctx, source_type, doc, expected_doc):
    source_definition = replication_ctx.pluggy_deps.source_definitions.data[
        source_type
    ]
    data_serializer = source_definition.get_data_serializer_to_queue()
    assert raw_loaders.pass_raw_json(doc, data_serializer) == expected_doc
