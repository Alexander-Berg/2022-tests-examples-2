import pytest


@pytest.fixture(name='eats_catalog_storage_cache', autouse=True)
def service_cache(mockserver, request, load_json):
    data = []

    marker = request.node.get_closest_marker('eats_catalog_storage_cache')
    if marker:
        if 'file' in marker.kwargs:
            data = load_json(marker.kwargs['file'])
        elif marker.args:
            data = marker.args[0]

    class ServiceCache:
        def __init__(self, data):
            self.data = data if data else []

        def updates(self, last_revision=None):
            if not last_revision:
                return self.data
            return [x for x in self.data if x['revision_id'] > last_revision]

        def retrieve_by_revision_ids(self, revision_ids=None):
            if not revision_ids:
                return []
            return [x for x in self.data if x['revision_id'] in revision_ids]

    eats_catalog_storage_cache = ServiceCache(data)

    @mockserver.json_handler(
        'eats-catalog-storage'
        '/internal/eats-catalog-storage/v1/places/updates',
    )
    def _mock_updates(json_request):
        revision = json_request.json['last_known_revision']
        places = eats_catalog_storage_cache.updates(revision)
        if places:
            return {
                'places': places,
                'last_known_revision': places[-1]['revision_id'],
            }

        return {'places': [], 'last_known_revision': 0}

    @mockserver.json_handler(
        'eats-catalog-storage'
        '/internal/eats-catalog-storage/v1/places/retrieve-by-revision-ids',
    )
    def _mock_retrieve_by_revision_ids(json_request):
        revision_ids = json_request.json['revision_ids']
        places = eats_catalog_storage_cache.retrieve_by_revision_ids(
            revision_ids,
        )
        return {'places': places}
