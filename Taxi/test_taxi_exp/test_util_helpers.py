# pylint: disable=protected-access
import pytest

from taxi.util import dates

from taxi_exp.util import exceptions
from taxi_exp.util import request_checks
from taxi_exp.util import values


@pytest.mark.parametrize(
    'clauses,schema,is_valid',
    [
        (
            [
                {
                    'title': 'test',
                    'value': {
                        'property1': 'hello everybody',
                        'property2': 12345,
                    },
                },
            ],
            """
description: test value
type: object
additionalProperties: false
required:
-   property1
-   property2
properties:
    property1:
        type: string
    property2:
        type: integer
            """,
            True,
        ),
        (
            [{'title': 'test', 'value': {'property1': 'hello everybody'}}],
            """
description: test value
type: object
additionalProperties: false
required:
-   property1
-   property2
properties:
    property1:
        type: string
    property2:
        type: integer
            """,
            False,
        ),
        (
            [
                {
                    'title': 'test',
                    'value': {
                        'property1': 'hello everybody',
                        'property2': 12345,
                    },
                },
            ],
            """
type: unknown
            """,
            False,
        ),
        (
            [
                {
                    'title': '1',
                    'value': {
                        'another_key': 321,
                        'deep_key': {'other_inner_key': 'aaaaaa'},
                        'array': [1, 2, 3],
                    },
                    'extension_method': 'extend',
                },
                {
                    'title': '2',
                    'value': {
                        'another_key': 321,
                        'deep_key': {'other_inner_key': 'aaaaaa'},
                        'array': [1, 2, 3],
                    },
                    'extension_method': 'deep_extend',
                },
                {
                    'title': '3',
                    'value': {'different_key': 'bbbbb'},
                    'extension_method': 'replace',
                },
                {
                    'title': '4',
                    'value': {'array': [1, 2, 3]},
                    'extension_method': 'extend',
                },
                {
                    'title': 'default',
                    'value': {
                        'key': 123,
                        'deep_key': {'inner_key': 'vvvvvv'},
                        'array': [99, 67, 56],
                    },
                    'predicate': {'type': 'TRUE'},
                },
            ],
            """
description: test value
type: object
additionalProperties: false
default:
  any_of:
  - key: 1
  - different_key: ""
properties:
  key:
    type: integer
  different_key:
    type: string
  another_key:
    type: integer
  deep_key:
    type: object
  array:
    type: array
  other_inner_key:
    type: string
            """,
            True,
        ),
    ],
)
async def test_check_clauses(clauses, schema, is_valid, taxi_exp_client):
    taxi_exp_app = taxi_exp_client.app
    try:
        processor = values.ValuesProcessor.from_context(
            context=taxi_exp_app, schema=schema, clauses=clauses,
        )
        processor.check_schema()
        processor.check_and_extend_clauses()
        assert is_valid
    except exceptions.RequestError:
        assert not is_valid


@pytest.mark.parametrize(
    'default,right,expected,is_deep,is_raise',
    [
        (
            {'a': {'b': {'c': [1, 2, 3]}, 'e': [6, 7, 7]}},
            {'a': {'d': {1: 100}, 'e': [9, 10]}},
            {'a': {'b': {'c': [1, 2, 3]}, 'e': [9, 10], 'd': {1: 100}}},
            True,
            False,
        ),
        (
            {
                'key': 123,
                'deep_key': {'inner_key': 'vvvvvv'},
                'array': [99, 67, 56],
            },
            {
                'another_key': 321,
                'deep_key': {'other_inner_key': 'aaaaaa'},
                'array': [1, 2, 3],
            },
            {
                'key': 123,
                'another_key': 321,
                'deep_key': {
                    'inner_key': 'vvvvvv',
                    'other_inner_key': 'aaaaaa',
                },
                'array': [1, 2, 3],
            },
            True,
            False,
        ),
        (
            {
                'key': 123,
                'deep_key': {'inner_key': 'vvvvvv'},
                'array': [99, 67, 56],
            },
            {
                'another_key': 321,
                'deep_key': {'other_inner_key': 'aaaaaa'},
                'array': [1, 2, 3],
            },
            {
                'key': 123,
                'another_key': 321,
                'deep_key': {'other_inner_key': 'aaaaaa'},
                'array': [1, 2, 3],
            },
            False,
            False,
        ),
        (
            {'key': {'deep_key': 'vvvvvv'}},
            {'key': {'deep_key': 'aaaaaa'}},
            {'key': {'deep_key': 'aaaaaa'}},
            True,
            False,
        ),
        ([1, 2, 3], [4, 5, 6], None, False, True),
    ],
)
def test_merge(default, right, expected, is_deep, is_raise):
    if is_raise:
        with pytest.raises(AttributeError):
            values.merge(default, right, deep=is_deep)
    else:
        merged = values.merge(default, right, deep=is_deep)

        assert merged == expected


def test_checking_lifetime():
    with pytest.raises(exceptions.RequestError400):
        request_checks.check_lifetime('2099-01-12T12:30:00Z')

    now_date = '{}-12-31T23:59:59Z'.format(dates.localize().year)
    request_checks.check_lifetime(now_date)


def test_check_names():
    request_checks.check_file_name('aa_cc_aaa-bbbb.txt')
    request_checks.check_app_name('aaaaa-bbbb_txt')
    request_checks.check_consumer_name('api-proxy/3.0/taxiontheway')
