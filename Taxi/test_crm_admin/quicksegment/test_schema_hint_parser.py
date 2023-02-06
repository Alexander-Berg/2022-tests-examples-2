# pylint: disable=invalid-name

import pytest

from crm_admin.quicksegment import schema_hint_parser as parser


@pytest.mark.parametrize(
    'expr, expected',
    [
        ('string', 'string'),
        (
            'array<integer>',
            {'type': 'array', 'elementType': 'integer', 'containsNull': True},
        ),
        (
            'map<string, integer>',
            {
                'type': 'map',
                'keyType': 'string',
                'valueType': 'integer',
                'valueContainsNull': True,
            },
        ),
        (
            'array<array<integer>>',
            {
                'type': 'array',
                'elementType': {
                    'type': 'array',
                    'elementType': 'integer',
                    'containsNull': True,
                },
                'containsNull': True,
            },
        ),
        (
            'struct[key: string, value: integer]',
            {
                'type': 'struct',
                'fields': [
                    {
                        'name': 'key',
                        'type': 'string',
                        'metadata': None,
                        'nullable': True,
                    },
                    {
                        'name': 'value',
                        'type': 'integer',
                        'metadata': None,
                        'nullable': True,
                    },
                ],
            },
        ),
    ],
)
def test_schema_hint_parsers(expr, expected):
    assert parser.parse(expr) == expected


#
# This fuction is a part of spark-jobs/segment.py, so we can not directly
# test it.
#
# from pyspark.sql import types
#
# def convert_schema_hint(schema):
#     def convert(dtype):
#         if isinstance(dtype, str):
#             raise RuntimeError(
#                 'atomic types are not currently supported'
#             )
#         elif dtype['type'] == 'array':
#             return types.ArrayType.fromJson(dtype)
#         elif dtype['type'] == 'map':
#             return types.MapType.fromJson(dtype)
#         else:
#             assert dtype['type'] == 'struct'
#             return types.StructType.fromJson(dtype)
#
#     return {col: convert(dtype) for col, dtype in schema.items()}
#
#
# def test_convert_schema_hint():
#     schema = {
#         # 'a': parser.parse('string'),
#         'b': parser.parse('array<string>'),
#         'c': parser.parse('map<string, array<string>>'),
#         'd': parser.parse('struct[key: string, value: integer]'),
#     }
#     converted = convert_schema_hint(schema)
#
#     print('>>>>>', converted)
#     assert isinstance(converted['b'], types.ArrayType)
#     assert isinstance(converted['c'], types.MapType)
#     assert isinstance(converted['d'], types.StructType)
