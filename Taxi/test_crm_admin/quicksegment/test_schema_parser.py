# pylint: disable=invalid-name

import io

import pytest
import yaml

from crm_admin.quicksegment import error
from crm_admin.quicksegment.schema_parser import (
    parse_schema,
)  # pylint: disable-all


def test_parse_string(tmpdir):
    schema = """
        tables:
          - name: base
            path:
            select: [id]
            schema_hints:
                col1: string
                col2: integer
          - name: properties
            path:
          - name: filter
            path:
            is_partitioned: True
          - name: filter-with-default-hist-depth
            path:
            is_partitioned: True
            history_depth_days: 20
          - name: filter_properties
            path:
            condition: col = true
            groupby: col
            is_optional: true
            prefix: prop_

        root_table: base

        graph:
          - how: left_outer
            left: base
            right: properties
            keys: id
            is_optional: True

          - how: left_semi
            left: base
            right: filter
            keys: secondary_key

          - how: left_outer
            left: filter
            right: filter_properties
            keys: {id: prop_id}
    """
    schema = yaml.load(
        io.StringIO(schema), Loader=getattr(yaml, 'CLoader', yaml.Loader),
    )

    g = parse_schema(schema)
    assert len(list(g.iter_tables())) == len(schema['tables'])
    assert len(list(g.iter_relations())) == len(schema['graph'])

    assert g.table('base').is_partitioned is False
    assert g.table('base').condition is None
    assert g.table('base').projection
    assert g.table('base').is_optional is False
    assert g.table('base').prefix is None
    assert g.table('base').schema_hints
    assert g.table('filter').is_partitioned is True
    assert not g.table('filter').schema_hints
    assert g.table('filter-with-default-hist-depth').is_partitioned is True
    assert g.table('filter-with-default-hist-depth').history_depth_days == 20
    assert g.table('filter_properties').condition is not None
    assert g.table('filter_properties').groupby == ['col']
    assert g.table('filter_properties').is_optional is True
    assert g.table('filter_properties').prefix == 'prop_'

    assert g.relation('base', 'properties').is_optional
    assert g.relation('base', 'filter').is_optional
    assert not g.relation('filter', 'filter_properties').is_optional


def test_parse_empty_schema():
    with pytest.raises(error.ValidationError):
        parse_schema({})


def test_missing_relations():
    schema = {'tables': [{'name': 'base', 'path': None}], 'root_table': 'base'}

    g = parse_schema(schema)
    assert g.graph.number_of_nodes() == 1
    assert g.graph.number_of_edges() == 0


def test_missing_root_table():
    schema = {
        'tables': [
            {'name': 'base', 'path': None},
            {'name': 'properties', 'path': None},
        ],
        'graph': [
            {
                'how': 'left_outer',
                'left': 'base',
                'right': 'properties',
                'keys': 'id',
            },
        ],
    }

    with pytest.raises(error.ValidationError):
        parse_schema(schema)


@pytest.mark.parametrize('missing_key', ['name', 'path'])
def test_missing_required_fields_in_tables(missing_key):
    schema = {'tables': [{'name': 'base', 'path': None}], 'graph': []}
    del schema['tables'][0][missing_key]

    with pytest.raises(error.ParseError):
        parse_schema(schema)


@pytest.mark.parametrize('missing_key', ['left', 'right', 'on', 'how'])
def test_missing_required_fields_in_graph(missing_key):
    schema = {
        'tables': [{'name': 'a', 'path': None}, {'name': 'b', 'path': None}],
        'graph': [{'left': 'a', 'right': 'b', 'how': 'inner', 'on': 'key'}],
    }
    del schema['graph'][0][missing_key]

    with pytest.raises(error.ParseError):
        parse_schema(schema)


def test_table_environ():
    schema = {
        'tables': [
            {'name': 'a', 'path': {'production': None, 'testing': None}},
        ],
        'graph': [],
        'root_table': 'a',
    }

    g = parse_schema(schema)
    assert g.table('a').path == schema['tables'][0]['path']


def test_ids():
    schema = """
        tables:
          - name: base
            path:
            select: "*"
          - name: table_a
            path:
          - name: table_b
            path:
          - name: table_c
            path:
          - name: table_d
            path:

        root_table: base

        graph:
          - how: inner
            left: base
            right: table_a
            keys: id

          - how: inner
            left: base
            right: table_b
            keys: key_b

          - how: inner
            left: base
            right: table_c
            keys: key_c

          - how: inner
            left: table_c
            right: table_d
            keys: key_d
    """
    schema = yaml.load(
        io.StringIO(schema), Loader=getattr(yaml, 'CLoader', yaml.Loader),
    )

    g = parse_schema(schema)

    assert g.node_id('base') == 0
    assert g.node_id('table_a') == 1
    assert g.node_id('table_b') == 2
    assert g.node_id('table_c') == 3
    assert g.node_id('table_d') == 4
    assert g.edge_id('base', 'table_a') == 0
    assert g.edge_id('base', 'table_b') == 1
    assert g.edge_id('base', 'table_c') == 2
    assert g.edge_id('table_c', 'table_d') == 3


def test_join_keys():
    schema = """
        tables:
          - name: base
            path:
            select: "*"
          - name: table_a
            path:
          - name: table_b
            path:
          - name: table_c
            path:
          - name: table_d
            path:

        root_table: base

        graph:
          - how: inner
            left: base
            right: table_a
            keys: key1

          - how: inner
            left: base
            right: table_b
            keys: {base.key2: table_b.key2}

          - how: inner
            left: base
            right: table_c
            keys: {table_b.key3: table_c.key3}
    """
    schema = yaml.load(
        io.StringIO(schema), Loader=getattr(yaml, 'CLoader', yaml.Loader),
    )

    g = parse_schema(schema)

    assert g.table('base').keys == set()
    assert g.table('table_a').keys == {'key1'}
    assert g.table('table_b').keys == {'key2', 'key3'}
    assert g.table('table_c').keys == {'key3'}

    g = parse_schema(schema, include_left_keys=True)

    assert g.table('base').keys == {'key1', 'key2', 'table_b.key3'}
    assert g.table('table_a').keys == {'key1'}
    assert g.table('table_b').keys == {'key2', 'key3'}
    assert g.table('table_c').keys == {'key3'}
