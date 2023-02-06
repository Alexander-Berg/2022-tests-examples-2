# pylint: disable=protected-access

import datetime

import pytest

from mia.crontasks import filters
from mia.generated.service.swagger.models import api


FIELD_NAME = 'field'


@pytest.mark.parametrize(
    'field, expected', [('field', 'value'), ('', {'field': 'value'})],
)
def test_extract_field(field, expected):
    table_record = {'field': 'value'}
    assert filters._extract_field(table_record, field) == expected


@pytest.mark.parametrize(
    'reference_value, expected', [('value', True), ('not_value', False)],
)
def test_exact_match_filter(reference_value, expected):
    table_record = {'field': 'value'}
    filter_ = filters.ExactMatchFilter(FIELD_NAME, reference_value)
    assert filter_(table_record) == expected


@pytest.mark.parametrize(
    'reference_value, expected',
    [('value', False), ('not_value_1', True), ('not_value_2', True)],
)
def test_not_equal_filter(reference_value, expected):
    table_record = {'field': 'value'}
    filter_ = filters.NotEqualFilter(FIELD_NAME, reference_value)
    assert filter_(table_record) == expected


def test_normalized_filter_normalize():
    field_value = (
        'АВСЕНКМОРТХУ авсенкмортху 1234567890 ABCEHKMOPTXY abcehkmoptxy'
    )
    expected = 'ABCEHKMOPTXYABCEHKMOPTXY1234567890ABCEHKMOPTXYABCEHKMOPTXY'
    result = filters.NormalizedFilter._normalize(field_value)
    assert result == expected


@pytest.mark.parametrize(
    'reference_value, expected',
    [('ABу 1 2 3 Yв C', True), ('AbY 1 3 3 ув С', False)],
)
def test_normalized_filter(reference_value, expected):
    table_record = {'field': 'Аву 123 УbС'}
    filter_ = filters.NormalizedFilter(FIELD_NAME, reference_value)
    assert filter_(table_record) == expected


@pytest.mark.parametrize(
    'reference_value, expected',
    [('.o..t..n.*reet.34', True), ('.o..t..c.*reet.34', False)],
)
def test_regex_filter(reference_value, expected):
    table_record = {'field': 'location 12, street 34'}
    filter_ = filters.RegexFilter(FIELD_NAME, reference_value)
    assert filter_(table_record) == expected


@pytest.mark.parametrize(
    'reference_value, expected',
    [
        (
            api.Period(
                datetime.datetime(2019, 10, 1, 4, 48, 27),
                datetime.datetime(2019, 10, 1, 4, 48, 29),
            ),
            True,
        ),
        (
            api.Period(
                datetime.datetime(2019, 10, 1, 4, 48, 26),
                datetime.datetime(2019, 10, 1, 4, 48, 27),
            ),
            False,
        ),
    ],
)
def test_period_filter(reference_value, expected):
    table_record = {'field': 1569905308}
    filter_ = filters.PeriodFilter(FIELD_NAME, reference_value)
    assert filter_(table_record) == expected


@pytest.mark.parametrize(
    'reference_value, expected',
    [
        (filters.ExactMatchFilter('', 'abac'), True),
        (filters.ExactMatchFilter('', 'baca'), False),
    ],
)
def test_any_of_array_filter(reference_value, expected):
    table_record = {'field': ['aba', 'caba', 'abacaba', 'abac', 'cabac']}
    filter_ = filters.AnyOfArrayFilter(FIELD_NAME, reference_value)
    assert filter_(table_record) == expected


@pytest.mark.parametrize(
    'reference_value, expected',
    [
        (filters.ExactMatchFilter('', 'cabac'), True),
        (filters.ExactMatchFilter('', 'abac'), False),
        (filters.ExactMatchFilter('', 'babac'), False),
    ],
)
def test_last_of_array_filter(reference_value, expected):
    table_record = {'field': ['aba', 'caba', 'abacaba', 'abac', 'cabac']}
    filter_ = filters.LastOfArrayFilter(FIELD_NAME, reference_value)
    assert filter_(table_record) == expected


@pytest.mark.parametrize(
    'reference_value, expected',
    [(filters.ExactMatchFilter('', 'cabac'), False), (None, False)],
)
def test_last_of_array_filter_empty(reference_value, expected):
    table_record = {'field': []}
    filter_ = filters.LastOfArrayFilter(FIELD_NAME, reference_value)
    assert filter_(table_record) == expected


@pytest.mark.parametrize(
    'filters_, expected',
    [
        (
            [
                filters.RegexFilter('field_1', '.o..t..n.*reet.34'),
                filters.ExactMatchFilter('field_2', 'value_1'),
                filters.LastOfArrayFilter(
                    'field_3', filters.ExactMatchFilter('', 'cabac'),
                ),
            ],
            True,
        ),
        (
            [
                filters.RegexFilter('field_1', '.o..t..c.*reet.34'),
                filters.ExactMatchFilter('field_2', 'value_2'),
                filters.LastOfArrayFilter(
                    'field_3', filters.ExactMatchFilter('', 'cabac'),
                ),
            ],
            False,
        ),
    ],
)
def test_all_of_filter(filters_, expected):
    table_record = {
        'field_1': 'location 12, street 34',
        'field_2': 'value_1',
        'field_3': ['aba', 'caba', 'abacaba', 'abac', 'cabac'],
    }
    filter_ = filters.AllOfFilter(filters_)
    assert filter_(table_record) == expected


def test_all_of_filter_exception():
    with pytest.raises(filters.EmptyFiltersList):
        filters.AnyOfFilter([])


@pytest.mark.parametrize(
    'filters_, expected',
    [
        (
            [
                filters.RegexFilter('field_1', '.o..t..n.*reet.34'),
                filters.ExactMatchFilter('field_2', 'value_2'),
                filters.LastOfArrayFilter(
                    'field_3', filters.ExactMatchFilter('', 'cabab'),
                ),
            ],
            True,
        ),
        (
            [
                filters.RegexFilter('field_1', '.o..t..c.*reet.34'),
                filters.ExactMatchFilter('field_2', 'value_2'),
                filters.LastOfArrayFilter(
                    'field_3', filters.ExactMatchFilter('', 'cabab'),
                ),
            ],
            False,
        ),
    ],
)
def test_any_of_filter(filters_, expected):
    table_record = {
        'field_1': 'location 12, street 34',
        'field_2': 'value_1',
        'field_3': ['aba', 'caba', 'abacaba', 'abac', 'cabac'],
    }
    filter_ = filters.AnyOfFilter(filters_)
    assert filter_(table_record) == expected


def test_any_of_filter_exception():
    with pytest.raises(filters.EmptyFiltersList):
        filters.AnyOfFilter([])


@pytest.mark.parametrize(
    'reference_value, expected',
    [
        (filters.ExactMatchFilter('driver_name', 'Name_2'), True),
        (filters.ExactMatchFilter('driver_name', 'Name_3'), False),
    ],
)
def test_performer_filter(reference_value, expected):
    table_record = {
        'performer_driver_id': 'id_2',
        'candidates': [
            {'driver_id': 'id_3', 'driver_name': 'Name_3'},
            {'driver_id': 'id_2', 'driver_name': 'Name_2'},
            {'driver_id': 'id_1', 'driver_name': 'Name_1'},
        ],
    }
    filter_ = filters.PerformerFilter(reference_value)
    assert filter_(table_record) == expected


@pytest.mark.parametrize(
    'test',
    [
        {
            'request': {
                'row_field_name': 'geopoint',
                'reference_value': api.Coordinates(
                    lon=55.734928, lat=37.642576, radius=1,
                ),
            },
            'expected': True,
        },
        {
            'request': {
                'row_field_name': 'geopoint',
                'reference_value': api.Coordinates(
                    lon=55.734273, lat=37.642492, radius=100,
                ),
            },
            'expected': True,
        },
        {
            'request': {
                'row_field_name': 'geopoint',
                'reference_value': api.Coordinates(
                    lon=55.733574, lat=37.641090, radius=100,
                ),
            },
            'expected': False,
        },
        {
            'request': {
                'row_field_name': 'geopoint',
                'reference_value': api.Coordinates(
                    lon=55.735221, lat=37.643300, radius=100,
                ),
            },
            'expected': True,
        },
        {
            'request': {
                'row_field_name': 'geopoint',
                'reference_value': api.Coordinates(
                    lon=55.736138, lat=37.642752, radius=100,
                ),
            },
            'expected': False,
        },
    ],
)
def test_coordinates_filter(test):
    request = test['request']
    expected = test['expected']

    table_record = {'geopoint': [55.734928, 37.642576]}

    filter_ = filters.CoordsFilter(**request)

    assert filter_(table_record) == expected
