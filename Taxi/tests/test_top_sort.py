import collections

import pytest

from codegen import utils


@pytest.mark.parametrize(
    'edges, cycle',
    [
        ([(0, 1), (0, 2), (1, 2)], None),
        ([(0, 1), (1, 2), (2, 0)], [0, 1, 2, 0]),
        (
            [
                (0, 1),
                (0, 2),
                (1, 2),
                (1, 3),
                (2, 4),
                (3, 2),
                (4, 5),
                (5, 3),
                (10, 11),
                (11, 12),
                (12, 13),
                (10, 14),
                (13, 14),
            ],
            [2, 4, 5, 3, 2],
        ),
        (
            [
                (0, 1),
                (1, 2),
                (0, 3),
                (1, 3),
                (3, 2),
                (1, 4),
                (2, 4),
                (3, 4),
                (0, 5),
                (5, 1),
                (5, 4),
                (10, 11),
                (11, 12),
            ],
            None,
        ),
    ],
)
def test_dependencies_graph_sort(edges, cycle):
    graph = collections.OrderedDict()
    for edge in edges:
        first, second = edge
        graph.setdefault(first, []).append(second)
        graph.setdefault(second, [])
    if cycle:
        with pytest.raises(utils.CycleFound) as exc_info:
            utils.top_sort_nodes(graph)
        assert cycle == exc_info.value.args[0]
    else:
        index = {}
        for i, second in enumerate(utils.top_sort_nodes(graph)):
            index[second] = i
        for edge in edges:
            first, second = edge
            assert index[first] > index[second]
