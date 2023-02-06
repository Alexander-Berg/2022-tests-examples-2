# pylint: disable=invalid-name

import json

import pytest
import yaml

from crm_admin.quicksegment import error
from crm_admin.quicksegment import tools


def test_read_file_yaml(tmpdir):
    data = {'key': 'value'}
    with open(tmpdir / 'config.yaml', 'wt') as f:
        yaml.dump(data, f)
    assert tools.read_file(tmpdir / 'config.yaml') == data


def test_read_file_json(tmpdir):
    data = {'key': 'value'}
    with open(tmpdir / 'config.json', 'wt') as f:
        json.dump(data, f)
    assert tools.read_file(tmpdir / 'config.json') == data


def test_read_file_other(tmpdir):
    with open(tmpdir / 'config.txt', 'wt') as f:
        f.write('{"key": "value"}')
    with pytest.raises(error.ParseError):
        tools.read_file(tmpdir / 'config.txt')


@pytest.mark.parametrize('ext', ['yaml', 'json'])
def test_read_malformed_file(tmpdir, ext):
    with open(tmpdir / f'config.{ext}', 'wt') as f:
        f.write('{{}')
    with pytest.raises(error.ParseError):
        tools.read_file(tmpdir / f'config.{ext}')


@pytest.mark.parametrize(
    'colname, is_qualified', [('col', False), ('table.col', True)],
)
def test_is_qualified_colname(colname, is_qualified):
    assert tools.is_qualified_colname(colname) == is_qualified


def test_table_name():
    assert tools.table_name('table.column') == 'table'
    with pytest.raises(ValueError):
        tools.table_name('column')


def test_split_col():
    assert tools.split_col('table.column') == ('table', 'column')
    with pytest.raises(ValueError):
        tools.split_col('column')


def test_drop_table_name():
    assert tools.drop_table_name('table.column') == 'column'
    assert tools.drop_table_name('column') == 'column'
