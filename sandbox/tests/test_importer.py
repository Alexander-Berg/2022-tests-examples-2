import networkx as nx
import pytest

from sandbox.projects.yabs.qa.utils.general import get_json_md5
from sandbox.projects.yabs.qa.utils.importer import (
    CSDataError,
    build_importer_graph,
    get_bases_importers,
    get_bases_importers_with_dependencies,
    get_importers_with_dependencies,
    get_importer_bases,
    get_importer_output_tables,
    get_importers_after,
    get_importers_before,
    get_importer_mkdb_info_version,
    is_mysql_importer,
)


@pytest.fixture(scope='module')
def importer_graph():
    graph = nx.DiGraph()
    graph.add_node('8')
    graph.add_edges_from([
        ('1', '2'),
        ('1', '3'),
        ('2', '4'),
        ('3', '4'),
        ('3', '5'),
        ('6', '7'),
    ])
    return graph


def test_build_importer_graph(importer_graph):
    dependencies = {
        '1': [],
        '2': ['1'],
        '3': ['1'],
        '4': ['2', '3'],
        '5': ['3'],
        '6': ['7'],
        '8': [],
    }
    actual_graph = build_importer_graph(dependencies)

    assert nx.is_isomorphic(importer_graph, actual_graph)


@pytest.mark.parametrize(('importer', 'dependents'), [
    ('1', ['2', '3', '4', '5']),
    ('2', ['4']),
    ('3', ['4', '5']),
    ('4', []),
    ('5', []),
    ('6', ['7']),
    ('7', []),
    ('8', []),
])
def test_get_importers_after(importer, dependents, importer_graph):
    assert set(dependents) == set(get_importers_after(importer, importer_graph))


@pytest.mark.parametrize(('importer',), [
    ('9',),
])
def test_get_importers_after_raises(importer, importer_graph):
    with pytest.raises(CSDataError):
        get_importers_after(importer, importer_graph)


@pytest.mark.parametrize(('importer', 'dependencies'), [
    ('1', []),
    ('2', ['1']),
    ('3', ['1']),
    ('4', ['1', '2', '3']),
    ('5', ['1', '3']),
    ('6', []),
    ('7', ['6']),
    ('8', []),
])
def test_get_importers_before(importer, dependencies, importer_graph):
    assert set(dependencies) == set(get_importers_before(importer, importer_graph))


@pytest.mark.parametrize(('importer',), [
    ('9',),
])
def test_get_importers_before_raises(importer, importer_graph):
    with pytest.raises(CSDataError):
        get_importers_before(importer, importer_graph)


@pytest.mark.parametrize(('importer_info', 'mkdb_info', 'expected_bases'), [
    (
        {
            'outputs': [
                {'excluded_base_groups': [], 'mkdb_queries': ['a', 'b']},
                {'excluded_base_groups': [], 'mkdb_queries': ['b', 'c', 'd']},
                {'excluded_base_groups': None, 'mkdb_queries': []},
            ],
        },
        {
            'A': {"Queries": [{"Name": "0"}, {"Name": "a"}]},
            'B': {"Queries": [{"Name": "0"}, {"Name": "b"}, {"Name": "a"}]},
            'C': {"Queries": [{"Name": "0"}, {"Name": "c"}]},
            'D': {"Queries": [{"Name": "0"}, {"Name": "d"}]},
            'E': {"Queries": [{"Name": "0"}, {"Name": "e"}]},
        },
        {'A', 'B', 'C', 'D'},
    ),
    (
        {'outputs': [{'excluded_base_groups': [], 'mkdb_queries': ['a']}]},
        {
            'A': {"Queries": [{"Name": "a"}]},
            'A_0': {"Queries": [{"Name": "a"}]},
            'A001': {"Queries": [{"Name": "a"}]},
            'A_001': {"Queries": [{"Name": "a"}]},
            'B': {"Queries": [{"Name": "a"}]},
            'B_0': {"Queries": [{"Name": "a"}]},
            'B001': {"Queries": [{"Name": "a"}]},
            'B_001': {"Queries": [{"Name": "a"}]},
            'C': {"Queries": [{"Name": "c"}]},
        },
        {'A', 'A_0', 'A001', 'A_001', 'B', 'B_0', 'B001', 'B_001'},
    ),
    (
        {'outputs': [{'excluded_base_groups': ['A_0', 'B'], 'mkdb_queries': ['a']}]},
        {
            'A': {"Queries": [{"Name": "a"}]},
            'A_0': {"Queries": [{"Name": "a"}]},
            'A001': {"Queries": [{"Name": "a"}]},
            'A_001': {"Queries": [{"Name": "a"}]},
            'B': {"Queries": [{"Name": "a"}]},
            'B_0': {"Queries": [{"Name": "a"}]},
            'B001': {"Queries": [{"Name": "a"}]},
            'B_001': {"Queries": [{"Name": "a"}]},
            'C': {"Queries": [{"Name": "c"}]},
        },
        {'A', 'A001', 'A_001', 'B_0'},
    ),
])
def test_get_importer_bases(importer_info, mkdb_info, expected_bases):
    assert expected_bases == get_importer_bases(importer_info, mkdb_info)


@pytest.mark.parametrize(('base_tags', 'importers_info', 'mkdb_info', 'expected_importers'), [
    (
        ('A', 'yabs_B'),
        {
            '1': {
                'outputs': [
                    {'excluded_base_groups': [], 'mkdb_queries': ['a', 'b']},
                    {'excluded_base_groups': [], 'mkdb_queries': ['b', 'c', 'd']},
                    {'excluded_base_groups': None, 'mkdb_queries': []},
                ],
                'dependencies': ['2'],
            },
            '2': {
                'outputs': [
                    {'excluded_base_groups': None, 'mkdb_queries': []},
                ],
                'dependencies': ['3'],
            },
            '3': {
                'outputs': [
                    {'excluded_base_groups': None, 'mkdb_queries': []},
                ],
            },
            '4': {
                'outputs': [
                    {'excluded_base_groups': [], 'mkdb_queries': ['b', 'c', 'd']},
                ],
            },
            '5': {
                'outputs': [
                    {'excluded_base_groups': [], 'mkdb_queries': ['c']},
                    {'excluded_base_groups': [], 'mkdb_queries': ['e']},
                    {'excluded_base_groups': None, 'mkdb_queries': []},
                ],
                'dependencies': ['1'],
            },
        },
        {
            'A': {"Queries": [{"Name": "0"}, {"Name": "a"}]},
            'B': {"Queries": [{"Name": "0"}, {"Name": "b"}, {"Name": "a"}]},
            'C': {"Queries": [{"Name": "0"}, {"Name": "c"}]},
            'D': {"Queries": [{"Name": "0"}, {"Name": "d"}]},
            'E': {"Queries": [{"Name": "0"}, {"Name": "e"}]},
        },
        ['1', '4'],
    ),
])
def test_get_bases_importers(base_tags, importers_info, mkdb_info, expected_importers):
    assert expected_importers == sorted(get_bases_importers(base_tags, importers_info, mkdb_info))


@pytest.mark.parametrize(('base_tags', 'importers_info', 'mkdb_info', 'expected_importers'), [
    (
        ('A', 'yabs_B'),
        {
            '1': {
                'outputs': [
                    {'excluded_base_groups': [], 'mkdb_queries': ['a', 'b']},
                    {'excluded_base_groups': [], 'mkdb_queries': ['b', 'c', 'd']},
                    {'excluded_base_groups': None, 'mkdb_queries': []},
                ],
                'dependencies': ['2'],
            },
            '2': {
                'outputs': [
                    {'excluded_base_groups': None, 'mkdb_queries': []},
                ],
                'dependencies': ['3'],
            },
            '3': {
                'outputs': [
                    {'excluded_base_groups': None, 'mkdb_queries': []},
                ],
                'dependencies': [],
            },
            '4': {
                'outputs': [
                    {'excluded_base_groups': [], 'mkdb_queries': ['b', 'c', 'd']},
                ],
                'dependencies': [],
            },
            '5': {
                'outputs': [
                    {'excluded_base_groups': [], 'mkdb_queries': ['c']},
                    {'excluded_base_groups': [], 'mkdb_queries': ['e']},
                    {'excluded_base_groups': None, 'mkdb_queries': []},
                ],
                'dependencies': ['1'],
            },
        },
        {
            'A': {"Queries": [{"Name": "0"}, {"Name": "a"}]},
            'B': {"Queries": [{"Name": "0"}, {"Name": "b"}, {"Name": "a"}]},
            'C': {"Queries": [{"Name": "0"}, {"Name": "c"}]},
            'D': {"Queries": [{"Name": "0"}, {"Name": "d"}]},
            'E': {"Queries": [{"Name": "0"}, {"Name": "e"}]},
        },
        ['1', '2', '3', '4'],
    ),
])
def test_get_bases_importers_with_dependencies(base_tags, importers_info, mkdb_info, expected_importers):
    assert expected_importers == sorted(get_bases_importers_with_dependencies(base_tags, importers_info, mkdb_info))


@pytest.mark.parametrize(('importers', 'importers_info', 'expected_importers'), [
    (['1'], {'1': {'dependencies': []}}, ['1']),
    (['1'], {
        '1': {'dependencies': ['2']},
        '2': {'dependencies': []},
    }, ['1', '2']),
    (['2'], {
        '1': {'dependencies': ['2']},
        '2': {'dependencies': []},
    }, ['2']),
    (['1', '2'], {
        '1': {'dependencies': ['3']},
        '2': {'dependencies': []},
        '3': {'dependencies': []},
    }, ['1', '2', '3']),
])
def test_get_importers_with_dependencies(importers, importers_info, expected_importers):
    assert expected_importers == sorted(get_importers_with_dependencies(importers, importers_info))


@pytest.mark.parametrize(('importers', 'importers_info'), [
    (['1'], {}),
    (['1'], {'1': {}}),
    (['1'], {'1': {'dependencies': None}}),
    (['1'], {'1': {'dependencies': '2'}}),
    (['2'], {
        '1': {'dependencies': ['2']},
        '2': {},
    }),
    (['1', '2'], {
        '1': {'dependencies': ['3']},
        '2': {'dependencies': []},
        '3': {},
    }),
])
def test_get_importers_with_dependencies_raises(importers, importers_info):
    with pytest.raises(CSDataError):
        get_importers_with_dependencies(importers, importers_info)


@pytest.mark.parametrize(('importer_info', 'mkdb_info', 'base_tags', 'output_tables'), [
    (
        {
            'outputs': [
                {'path': '1', 'excluded_base_groups': [], 'mkdb_queries': ['a', 'b']},
                {'path': '2', 'excluded_base_groups': [], 'mkdb_queries': ['b', 'c', 'd']},
                {'path': '3', 'excluded_base_groups': [], 'mkdb_queries': ['e']},
                {'path': '4', 'excluded_base_groups': None, 'mkdb_queries': []},
            ],
            'dependencies': ['0'],
        },
        {
            'A': {"Queries": [{"Name": "0"}, {"Name": "a"}]},
            'B': {"Queries": [{"Name": "0"}, {"Name": "b"}, {"Name": "a"}]},
            'C': {"Queries": [{"Name": "0"}, {"Name": "c"}]},
            'D': {"Queries": [{"Name": "0"}, {"Name": "d"}]},
            'E': {"Queries": [{"Name": "0"}, {"Name": "e"}]},
        },
        ['A', 'B', 'C'],
        ['1', '2', '4'],
    ),
])
def test_get_importer_output_tables(importer_info, mkdb_info, base_tags, output_tables):
    assert get_importer_output_tables(importer_info, mkdb_info, base_tags) == output_tables


@pytest.mark.parametrize(('importer_info', 'mkdb_info', 'expected'), [
    (
        {
            'outputs': [
                {'excluded_base_groups': [], 'mkdb_queries': ['a', 'b']},
                {'excluded_base_groups': [], 'mkdb_queries': ['b', 'c', 'd']},
                {'excluded_base_groups': None, 'mkdb_queries': []},
            ],
        },
        {
            'A': {"Queries": [{"Name": "0"}, {"Name": "a"}]},
            'B': {"Queries": [{"Name": "0"}, {"Name": "b"}, {"Name": "a"}]},
            'C': {"Queries": [{"Name": "0"}, {"Name": "c"}]},
            'D': {"Queries": [{"Name": "0"}, {"Name": "d"}]},
            'E': {"Queries": [{"Name": "0"}, {"Name": "e"}]},
        },
        get_json_md5({
            'A': {"Queries": [{"Name": "0"}, {"Name": "a"}]},
            'B': {"Queries": [{"Name": "0"}, {"Name": "b"}, {"Name": "a"}]},
            'C': {"Queries": [{"Name": "0"}, {"Name": "c"}]},
            'D': {"Queries": [{"Name": "0"}, {"Name": "d"}]},
        }),
    ),

])
def test_get_importer_mkdb_info_version(importer_info, mkdb_info, expected):
    assert get_importer_mkdb_info_version(importer_info, mkdb_info) == expected


@pytest.mark.parametrize(("importer_info", "is_mysql"), [
    ({"queries": [{"Name": "mysql_importer", "SQL": "select *", "Table": "table"}]}, True),
    ({"queries": []}, False),
])
def test_is_mysql_importer(importer_info, is_mysql):
    assert is_mysql_importer(importer_info) == is_mysql
