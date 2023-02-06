from copy import deepcopy
import json
import os
import pytest

import yatest.common as yc

import sandbox.projects.devtools.CacheTestGraphCompare.compare as compare

FILES = [
    compare.BENCHMARK_UNMATCHED_NODES_FILE_NAME,
    compare.TEST_UNMATCHED_NODES_FILE_NAME,
    compare.UID_ONLY_CHANGES_FILE_NAME,
    compare.SIGNIFICANT_BUT_NO_UID_CHANGES_FILE_NAME,
    compare.SIGNIFICANT_CHANGES_FILE_NAME,
    compare.UID_AND_DEPS_CHANGES_ONLY_FILE_NAME,
    compare.INSIGNIFICANT_CHANGES_FILE_NAME,
]

GRAPH = {
    'context': {
        'dummy': 'value',
    },
    'results': [
        'uid_result'
    ],
    'graph': [
        {
            'uid': 'uid_1',
            'stats_uid': 'stats_uid_1',
            'deps': [
                'uid_2',
                'uid_3',
            ],
            'inputs': [
                'input1',
                'input2',
            ],
            'changeme': 'changeme'
        },
        {
            'uid': 'uid_2',
            'stats_uid': 'stats_uid_2',
            'deps': [
            ],
            'inputs': [
                'input3',
                'input4',
            ],
        },
        {
            'uid': 'uid_3',
            'stats_uid': 'stats_uid_3',
            'deps': [
            ],
            'inputs': [
                'input5',
                'input6',
            ],
        },
    ],
}


def _read_file(file_path):
    with open(file_path) as f:
        return f.read()


def _dump_graphs_and_compare(bm_graph, tst_graph):
    bm_graph_path = yc.test_output_path('bm-graph.json')
    tst_graph_path = yc.test_output_path('tst-graph.json')
    result_dir = yc.test_output_path('cmp-results')
    os.mkdir(result_dir)
    with open(bm_graph_path, 'w') as f:
        json.dump(bm_graph, f)
    with open(tst_graph_path, 'w') as f:
        json.dump(tst_graph, f)
    stat = compare.compare_graphs(bm_graph_path, tst_graph_path, result_dir)

    result = '=== STAT:\n{}\n'.format(stat)
    for fn in FILES:
        result += '=== ' + fn + ':\n'
        result += _read_file(os.path.join(result_dir, fn))
    return result


def _prepare_graphs():
    return deepcopy(GRAPH), deepcopy(GRAPH)


def test_identical_graphs():
    bm_graph, tst_graph = _prepare_graphs()
    return _dump_graphs_and_compare(bm_graph, tst_graph)


# Не нашлось соответствия по stats_uid
def test_unmatched_nodes():
    bm_graph, tst_graph = _prepare_graphs()
    tst_graph['graph'][1]['stats_uid'] = 'changed_stats_uid'
    return _dump_graphs_and_compare(bm_graph, tst_graph)


# Поменялся только uid, но ничего больше не поменялось
def test_changed_uid_only():
    bm_graph, tst_graph = _prepare_graphs()
    tst_graph['graph'][0]['uid'] = 'changed_uid'
    return _dump_graphs_and_compare(bm_graph, tst_graph)


# Поменялись значимые поля ноды, но uid не поменялся
def test_significant_but_no_uid_changes():
    bm_graph, tst_graph = _prepare_graphs()
    tst_graph['graph'][0]['deps'] = ['uid_2']
    return _dump_graphs_and_compare(bm_graph, tst_graph)


# Поменялись значимые поля ноды и uid тоже. Изменение deps тестируется отдельно
@pytest.mark.parametrize('field', ['cmds', 'outputs', 'env', 'platform', 'requirements', 'tags', 'target_properties'])
def test_significant_changes(field):
    bm_graph, tst_graph = _prepare_graphs()
    tst_graph['graph'][0]['uid'] = 'changed_uid'
    tst_graph['graph'][0][field] = {'siginificant_field_value': None}
    return _dump_graphs_and_compare(bm_graph, tst_graph)


# Переменные окружения, начинающиеся на 'YA_' игнорируются
def test_unimportant_env_changes():
    bm_graph, tst_graph = _prepare_graphs()
    bm_graph['graph'][0]['env'] = {'YA_KEY': 'value1'}
    tst_graph['graph'][0]['env'] = {'YA_KEY': 'value2'}
    return _dump_graphs_and_compare(bm_graph, tst_graph)


# В одной из нод поменялись только uid и deps
def test_deps_and_uid_changes():
    bm_graph, tst_graph = _prepare_graphs()
    tst_graph['graph'][0]['deps'] = ['uid_2']
    tst_graph['graph'][0]['uid'] = 'changed_uid'
    return _dump_graphs_and_compare(bm_graph, tst_graph)


# Поменялись незначимые поля ноды
def test_insignificant_changes():
    bm_graph, tst_graph = _prepare_graphs()
    tst_graph['graph'][0]['changeme'] = 'changed'
    return _dump_graphs_and_compare(bm_graph, tst_graph)
