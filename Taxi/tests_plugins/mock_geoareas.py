import pytest


class Geoareas:
    def __init__(self):
        self.items = {'geoareas': {}, 'subvention_geoareas': {}}

    def add_one(self, item, db_format=False, collection_name='geoareas'):
        collection_items = self.items[collection_name]
        collection_items[item['name']] = item

    def add_many(self, items, db_format=False, collection_name='geoareas'):
        for item in items:
            self.add_one(
                item, db_format=db_format, collection_name=collection_name,
            )

    def add_by_marker(self, marker, load_json):
        db_format = False
        if 'db_format' in marker.kwargs and marker.kwargs['db_format']:
            db_format = True
        if 'filename' in marker.kwargs:
            self.add_many(
                load_json(marker.kwargs['filename']), db_format=db_format,
            )
        if 'sg_filename' in marker.kwargs:
            self.add_many(
                load_json(marker.kwargs['sg_filename']),
                db_format=db_format,
                collection_name='subvention_geoareas',
            )
        if 'items' in marker.kwargs:
            self.add_many(marker.kwargs['items'], db_format=db_format)

    def get_dict(self, collection_name='geoareas'):
        return self.items[collection_name]

    def get_list(self, collection_name='geoareas'):
        return list(self.items[collection_name].values())


@pytest.fixture
def geoareas(request, load_json):
    data = Geoareas()
    has_items = False
    for marker in request.node.iter_markers('geoareas'):
        has_items = True
        data.add_by_marker(marker, load_json)
    if not has_items:
        data.add_many(load_json('geoareas.json'))
    return data


@pytest.fixture(autouse=True)
def mock_geoareas(mockserver, geoareas):
    @mockserver.json_handler('/geoareas/geoareas/v1/tariff-areas')
    def _geoareas_handler(request):
        if 'updated_after' in request.args:
            return {'geoareas': [], 'removed_names': []}
        return {'geoareas': geoareas.get_list(), 'removed_names': []}

    return _geoareas_handler


def pytest_configure(config):
    config.addinivalue_line('markers', 'geoareas: geoareas')
