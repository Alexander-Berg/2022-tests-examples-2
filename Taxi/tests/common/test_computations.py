# coding: utf-8

from nile.contrib import cloudpickle
import pytest
import numpy as np

from taxi.ml.nirvana.common import computations


class CallsCounter:
    def __init__(self, base=0):
        self.calls_count = base

    def __call__(self, *args, **kwargs):
        self.calls_count += 1
        return self.calls_count


@pytest.fixture(scope='module')
def graph_1():
    graph = computations.Graph()

    graph.input('value_1')
    value_1 = graph['value_1']
    value_2 = graph.input('value_2')
    const_1 = graph.as_node(np.array([1, 2, 34]))
    const_1.sum(axis=0).output('n1')
    const_1.size.output('n2')

    calls_counter_1 = graph.global_node(CallsCounter)
    graph.global_node(CallsCounter, 1).with_name('calls_counter_2')
    calls_counter_3 = graph.global_node(CallsCounter, base=2)

    graph.auto_node(lambda func: func(), calls_counter_1).output('c1')
    graph.auto_node(lambda func: func(), graph['calls_counter_2']).output('c2')
    graph.auto_node(lambda func: func(), calls_counter_3).output('c3')

    summator = graph.as_node(lambda x, y: x + y)
    value_3 = (
        summator(value_1, value_2)
        .break_if(lambda x: x < 10)
        .with_name('value_3')
        .output('value_3')
    )

    graph['value_4'] = summator(x=graph['value_1'], y=value_3)
    graph['value_4'].output('value_4_1').output('value_4_2')

    value_5 = graph.node(lambda x: x, value_2).with_name('value_5')

    (value_1 + value_5).output('value_5_1')
    (value_1 - value_5).output('value_5_2')
    (value_1 * value_5).output('value_5_3')
    (value_1 / value_5).output('value_5_4')
    (value_1 // value_5).output('value_5_5')
    (value_1 + 1).output('value_5_6')
    (1 + value_1).output('value_5_7')
    (value_5 - 1).output('value_5_8')
    (1 - value_5).output('value_5_9')

    return graph


def test_pickle_graph_1(graph_1):
    cloudpickle.loads(cloudpickle.dumps(graph_1))


def test_pickle_graph_computer_1(graph_1):
    cloudpickle.loads(
        cloudpickle.dumps(computations.DefaultGraphComputer(graph_1)),
    )


@pytest.fixture(scope='module')
def prepared_computer_1(graph_1):
    computer = computations.DefaultGraphComputer(graph_1)
    computer.prepare()
    return computer


def test_graph_1(prepared_computer_1):
    computer = prepared_computer_1
    with pytest.raises(KeyError):
        assert computer(a=1, b=2)


def test_graph_2(prepared_computer_1):
    result = prepared_computer_1(value_1=1, value_2=4)
    assert result['n1'] == 37
    assert result['n2'] == 3
    assert result['c1'] == 1
    assert result['c2'] == 2
    assert result['c3'] == 3
    assert result['value_3'] == 5
    assert 'value_4_1' not in result
    assert 'value_4_2' not in result
    assert result['value_5_1'] == 5
    assert result['value_5_2'] == -3
    assert result['value_5_3'] == 4
    assert result['value_5_4'] == 0.25
    assert result['value_5_5'] == 0
    assert result['value_5_6'] == 2
    assert result['value_5_7'] == 2
    assert result['value_5_8'] == 3
    assert result['value_5_9'] == -3


def test_graph_3(prepared_computer_1):
    result = prepared_computer_1(value_1=1, value_2=11)
    assert result['c1'] == 1
    assert result['c2'] == 2
    assert result['c3'] == 3
    assert result['value_3'] == 12
    assert result['value_4_1'] == 13
    assert result['value_4_2'] == 13


def test_graph_4(prepared_computer_1):
    result = prepared_computer_1(value_3=11, value_1=2, value_5=2)
    assert result['c1'] == 1
    assert result['c2'] == 2
    assert result['c3'] == 3
    assert result['value_3'] == 11
    assert result['value_4_1'] == 13
    assert result['value_4_2'] == 13
