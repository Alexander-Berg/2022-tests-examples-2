import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from eats_catalog_storage_plugins import *  # noqa: F403 F401

from tests_eats_catalog_storage import sql


def pytest_configure(config):
    config.addinivalue_line(
        'markers', 'place_tags: [place_tags] ' 'fixture for eats-tags',
    )


@pytest.fixture(name='database')
def database(pgsql):
    class Context:
        def __init__(self, cluster):
            self.db = cluster

        def insert_place(self, place: sql.Place):
            sql.insert_place(self.db, place)

        def insert_zone(self, zone: sql.DeliverZone):
            sql.insert_delivery_zone(self.db, zone)

    return Context(pgsql['eats_catalog_storage'])


@pytest.fixture(name='place_tags', autouse=True)
def place_tags(mockserver, request):
    class Context:
        def __init__(self):
            self.tags = set()

        def add(self, tag: str):
            self.tags.add(tag)

    ctx = Context()

    marker = request.node.get_closest_marker('place_tags')
    if marker:
        for tag in marker.args:
            if isinstance(tag, str):
                ctx.add(tag)

    @mockserver.json_handler('/eats-tags/v2/match')
    def _eats_tags_match(request):
        entities = request.json['entities']
        if not entities:
            return {'entities': []}

        assert len(entities) == 1

        entity = entities[0]

        types = {item['type'] for item in entity['match']}
        assert types == set(['brand_id', 'place_id'])

        for item in entity['match']:
            assert item['value'].isnumeric()

        if not ctx.tags:
            return {'entities': []}

        return {'entities': [{'id': entity['id'], 'tags': list(ctx.tags)}]}

    return ctx
