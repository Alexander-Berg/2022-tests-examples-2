from collections import OrderedDict
from unittest.mock import Mock

from requests import RequestException

import pytest
from metrika.pylib.structures.dotdict import DotDict


def test_create_tables_local_exists(restorer):
    restorer.donors_ch.tables_info = {
        'db1': dict(
            table1={
                'create_table_query': 'create table1',
                'engine': 'Table'
            },
            table2={
                'create_table_query': 'create table2',
                'engine': 'Table'
            },
            view1={
                'create_table_query': 'create view1',
                'engine': 'View'
            },
            mat_view1={
                'create_table_query': 'create mat_view1',
                'engine': 'MaterializedView'
            },
            view2={
                'create_table_query': 'create view2',
                'engine': 'View'
            }
        )
    }

    restorer.clickhouse.tables_info = {
        'db1': dict(
            table1={
                'create_table_query': 'create table1',
                'engine': 'Table'
            },
            view1={
                'create_table_query': 'create view1',
                'engine': 'View'
            }
        )
    }

    restorer.create_tables_and_views()
    assert restorer.clickhouse.created_databases == {}
    assert restorer.clickhouse.created_tables == ['create table2', 'create mat_view1', 'create view2']


def test_create_tables_local_differs(restorer):
    restorer.donors_ch.tables_info = {
        'db1': dict(
            table1={
                'create_table_query': 'create table1',
                'engine': 'Table'
            }
        )
    }

    restorer.clickhouse.tables_info = {
        'db1': dict(
            table1={
                'create_table_query': 'create mytable1',
                'engine': 'Table'
            }
        )
    }

    with pytest.raises(Exception, match='Table db1.table1 already exists, but with different create query'):
        restorer.create_tables_and_views()


def test_create_tables_local_empty(restorer):
    restorer.donors_ch.tables_info = {
        'db1': OrderedDict(
            table1={
                'create_table_query': 'create table1',
                'engine': 'Table'
            },
            table2={
                'create_table_query': 'create table2',
                'engine': 'Table'
            },
            view1={
                'create_table_query': 'create view1',
                'engine': 'View'
            },
            mat_view1={
                'create_table_query': 'create mat_view1',
                'engine': 'MaterializedView'
            },
            view2={
                'create_table_query': 'create view2',
                'engine': 'View'
            }
        )
    }

    restorer.create_tables_and_views()
    assert restorer.clickhouse.created_databases == {'db1': 'Ordinary'}
    assert restorer.clickhouse.created_tables == ['create table1', 'create table2', 'create mat_view1', 'create view1', 'create view2']


def test_create_databases_local_differs(restorer):
    restorer.donors_ch.tables_info = {
        'db1': dict(
            table1={
                'create_table_query': 'create table1',
                'engine': 'Table'
            }
        )
    }
    restorer.donors_ch.db_engines = {'db1': 'Atomic'}

    restorer.clickhouse.tables_info = {
        'db1': dict(
            table1={
                'create_table_query': 'create mytable1',
                'engine': 'Table'
            }
        )
    }
    restorer.clickhouse.db_engines = {'db1': 'Ordinary'}

    with pytest.raises(Exception, match='Database db1 already exists, but with different engine'):
        restorer.create_tables_and_views()


def test_create_table_ch_exception(restorer):
    response = DotDict()
    response.headers = {'x-clickhouse-exception-code': '254'}
    restorer.clickhouse.create_table = Mock(side_effect=RequestException(response=response))
    with pytest.raises(RequestException):
        restorer._create_table('kek')


def test_create_table_regexp_doesnt_match(restorer):
    response = DotDict()
    response.headers = {'x-clickhouse-exception-code': '253'}
    response.text = 'Error'
    restorer.clickhouse.create_table = Mock(side_effect=RequestException(response=response))
    with pytest.raises(RequestException):
        restorer._create_table('create kek')


def test_create_table_node_exists(restorer):
    response = DotDict()
    response.headers = {'x-clickhouse-exception-code': '253'}
    response.text = 'Replica kek already exists'
    restorer.clickhouse.create_table = Mock(side_effect=[RequestException(response=response), None])
    restorer._create_table('create kek')
    assert restorer.clickhouse.create_table.call_count == 2
    assert restorer.zk.delete.call_args[0][0] == 'kek'
