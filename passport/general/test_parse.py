from io import StringIO

from passport.backend.tools.metrics.file_parsers import (
    re_log_parser,
    table_log_parser,
    tskv_log_parser,
)
import pytest


@pytest.fixture
def parser_re():
    return re_log_parser(r'^(?P<col1>.+)\t(?P<col2>.+)$')


@pytest.fixture
def parser_csv():
    return table_log_parser(['col1', 'col2'], ' ', True)


@pytest.fixture
def parser_tskv():
    return tskv_log_parser()


def test_tskv_ok(parser_tskv):
    sample_log = StringIO(
        '\n'.join([
            'key1=value1',
            'foo bar zar',
            'key1=value1\tkey2=value2',
            'key1=value1\tkey2=value2\t',
        ]),
    )

    actual_data = list(parser_tskv(sample_log))

    expected_data = [
        # одна пара ключ-значение - ок
        {
            'key1': 'value1',
        },
        # foo bar zar возвращает пустую строку
        {},
        # несколько пар ключ-значение - ок
        {
            'key1': 'value1',
            'key2': 'value2',
        },
        # висящий \t в конце строки ничем не мешает
        {
            'key1': 'value1',
            'key2': 'value2',
        },
    ]

    assert actual_data == expected_data


def test_re_ok(parser_re):
    sample_log = StringIO(
        '\n'.join([
            'value1\tvalue2',
            'foo bar zar',
            'value3\tvalue4',
            'value5\tvalue6',
        ]),
    )

    actual_data = list(parser_re(sample_log))

    expected_data = [
        {
            'col1': 'value1',
            'col2': 'value2',
        },
        {
            'col1': None,
            'col2': None,
        },
        {
            'col1': 'value3',
            'col2': 'value4',
        },
        {
            'col1': 'value5',
            'col2': 'value6',
        },
    ]

    assert actual_data == expected_data


def test_csv_ok(parser_csv):
    sample_log = StringIO(
        '\n'.join([
            'value1 value2',
            'value3 "foo bar zar"',
            '  value5     value6  ',
            '',
            'one_column',
            'x y z',
        ]),
    )

    actual_data = list(parser_csv(sample_log))

    expected_data = [
        {
            'col1': 'value1',
            'col2': 'value2',
        },
        {
            'col1': 'value3',
            'col2': 'foo bar zar',
        },
        {
            'col1': 'value5',
            'col2': 'value6',
        },
        {
            'col1': None,
            'col2': None,
        },
        {
            'col1': 'one_column',
            'col2': None,
        },
        {
            'col1': 'x',
            'col2': 'y',
        },
    ]

    assert actual_data == expected_data
