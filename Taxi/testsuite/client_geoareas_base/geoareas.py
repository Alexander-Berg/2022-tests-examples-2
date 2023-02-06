import datetime

import pytest


class Geoareas:
    def __init__(self):
        self.items = {
            'geoareas': {},
            'subvention_geoareas': {},
            'typed_geoareas': {},
        }

    def add_one(self, item, db_format=False, collection_name='geoareas'):
        if db_format:
            item['id'] = item['_id']
            del item['_id']
            if 't' in item:
                item['object_type'] = item['t']
                del item['t']
            if 'created' in item:
                if isinstance(item['created'], datetime.datetime):
                    item['created'] = item['created'].strftime(
                        '%Y-%m-%dT%H:%M:%SZ',
                    )
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
        if 'tg_filename' in marker.kwargs:
            self.add_many(
                load_json(marker.kwargs['tg_filename']),
                db_format=db_format,
                collection_name='typed_geoareas',
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
    for marker in request.node.iter_markers('geoareas'):
        data.add_by_marker(marker, load_json)
    return data


def pytest_configure(config):
    config.addinivalue_line('markers', 'geoareas: geoareas')
