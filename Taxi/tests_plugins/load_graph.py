import pytest


class MockGraphContext:
    def __init__(self):
        self.filename = 'graph.json'


@pytest.fixture
def load_graph(testpoint, load_json):
    context = MockGraphContext()

    @testpoint('testpoint::load_graph')
    def _handler(data_json):
        return load_json(context.filename)

    return context
