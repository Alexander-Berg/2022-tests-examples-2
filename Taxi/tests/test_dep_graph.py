import pytest

from taxi_buildagent import dep_graph


def add_dep_node(graph, name):
    node = dep_graph.DependencyNode(
        project_name=name, link_targets=[], project_path=None, link_sources=[],
    )
    graph.node_by_name[name] = node
    return node


class Params:
    def __init__(self, project_name, expected_output):
        self.project_name = project_name
        self.expected_output = expected_output


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(project_name='A', expected_output='ABCD'),
            id='starting from A node',
        ),
        pytest.param(
            Params(project_name='B', expected_output='B'),
            id='starting from B node',
        ),
        pytest.param(
            Params(project_name='C', expected_output='CDB'),
            id='starting from C node',
        ),
        pytest.param(
            Params(project_name='D', expected_output='DB'),
            id='starting from D node',
        ),
    ],
)
def test_dep_graph(params):
    graph = dep_graph.DependencyGraph(node_by_name={})
    a_node = add_dep_node(graph, 'A')
    b_node = add_dep_node(graph, 'B')
    c_node = add_dep_node(graph, 'C')
    d_node = add_dep_node(graph, 'D')
    a_node.link_sources.append(b_node.project_name)
    a_node.link_sources.append(c_node.project_name)
    c_node.link_sources.append(d_node.project_name)
    d_node.link_sources.append(b_node.project_name)

    start_node = graph.node_by_name.get(params.project_name)
    nodes_names = []
    for node in dep_graph.iterate_link_source_nodes(start_node, graph):
        nodes_names.append(node.project_name)
    assert ''.join(nodes_names) == params.expected_output
