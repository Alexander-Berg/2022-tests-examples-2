# pylint: disable=too-many-function-args, protected-access
import datetime

import bson

from replication.foundation import map_doc_classes as core
from replication.targets.yt.rows_validators import schema as schema_validation


def test_validate_schema():
    schema = [
        {'name': 'int_column', 'type': 'int64'},
        {'name': 'uint_column', 'type': 'uint64'},
        {'name': 'double_column', 'type': 'double'},
        {'name': 'string_column', 'type': 'string'},
        {'name': 'any_column', 'type': 'any'},
    ]
    rows = [
        core.MapDocInfo(
            0,
            {'int_column': 1.0, 'double_column': 1.0, 'string_column': 1},
            '0',
        ),
        core.MapDocInfo(
            1,
            {'int_column': 1, 'double_column': 1, 'string_column': '1'},
            '1',
        ),
        core.MapDocInfo(2, {'uint_column': -1, 'extra_column': 1}, '2'),
        core.MapDocInfo(
            3,
            {
                'any_column': {
                    'ts': datetime.datetime(2019, 1, 1),
                    'list_with_ts': [0, datetime.datetime(2019, 1, 1)],
                    'object_id_field': bson.ObjectId(
                        '5a15b62c30996c7bf4797000',
                    ),
                },
            },
            '3',
        ),
        core.MapDocInfo(
            4,
            {'int_column': 1, 'double_column': 1.0, 'string_column': '1'},
            '4',
        ),
    ]
    schema_validator = schema_validation._validate_schema
    validation_result = schema_validator(rows, schema)
    good_rows = validation_result.good_rows
    bad_docs = validation_result.bad_rows
    assert not validation_result.skip_rows
    errors_messages = [
        (item.doc.doc_id, [error['message'] for error in item.errors])
        for item in bad_docs
    ]
    assert errors_messages == [
        (
            '0',
            [
                'column int_column, value 1.0, error: expected int64, '
                'but got value of type '
                '<class \'yt.yson.yson_types.YsonDouble\'>',
                'column string_column, value 1, error: expected string, '
                'but got value of type '
                '<class \'yt.yson.yson_types.YsonInt64\'>',
            ],
        ),
        (
            '1',
            [
                'column double_column, value 1, error: expected double, '
                'but got value of type '
                '<class \'yt.yson.yson_types.YsonInt64\'>',
            ],
        ),
        (
            '2',
            [
                'column uint_column, value -1, error: expected uint64, '
                'but got value not in [0, 2**64)',
                'column extra_column, value 1, error: not in schema',
            ],
        ),
        (
            '3',
            [
                'column any_column, value {'
                '\'ts\': FakeDatetime(2019, 1, 1, 0, 0), '
                '\'list_with_ts\': [0, FakeDatetime(2019, 1, 1, 0, 0)], '
                '\'object_id_field\': ObjectId(\'5a15b62c30996c7bf4797000\')},'
                ' error: there is datetime value at list_with_ts.1',
                'column any_column, value {'
                '\'ts\': FakeDatetime(2019, 1, 1, 0, 0), '
                '\'list_with_ts\': [0, FakeDatetime(2019, 1, 1, 0, 0)], '
                '\'object_id_field\': ObjectId(\'5a15b62c30996c7bf4797000\')},'
                ' error: there is ObjectId value at object_id_field',
                'column any_column, value {'
                '\'ts\': FakeDatetime(2019, 1, 1, 0, 0), '
                '\'list_with_ts\': [0, FakeDatetime(2019, 1, 1, 0, 0)], '
                '\'object_id_field\': ObjectId(\'5a15b62c30996c7bf4797000\')},'
                ' error: there is datetime value at ts',
            ],
        ),
    ]
    assert [row.doc_id for row in good_rows] == ['4']
