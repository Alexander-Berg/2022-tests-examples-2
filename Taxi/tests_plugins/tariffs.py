import pytest


class Tariffs:
    def __init__(self):
        self.items = {}

    def add_one(self, item):
        self.items[item['home_zone']] = item

    def add_many(self, items):
        for item in items:
            self.add_one(item)

    def add_by_marker(self, marker, load_json):
        if 'filename' in marker.kwargs:
            self.add_many(load_json(marker.kwargs['filename']))
        if 'items' in marker.kwargs:
            self.add_many(marker.kwargs['items'])

    def get_dict(self):
        return self.items

    def get_list(self):
        return list(self.items.values())


def pytest_configure(config):
    config.addinivalue_line('markers', 'tariffs: tariffs')


@pytest.fixture
def tariffs(request, load_json):
    data = Tariffs()

    for marker in request.node.iter_markers('tariffs'):
        data.add_by_marker(marker, load_json)

    return data
