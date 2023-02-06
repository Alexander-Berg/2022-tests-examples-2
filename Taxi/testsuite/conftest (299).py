# pylint: disable=too-many-lines
import copy
import typing

from psycopg2 import extras
import pytest

# noqa: F403 F401
from tests_eats_retail_market_integration.eats_catalog_internals import storage

# root conftest for service eats-retail-market-integration
pytest_plugins = ['eats_retail_market_integration_plugins.pytest_plugins']


@pytest.fixture
def pg_realdict_cursor(pgsql):
    return pgsql['eats_retail_market_integration'].cursor(
        cursor_factory=extras.RealDictCursor,
    )


@pytest.fixture
def pg_cursor(pgsql):
    return pgsql['eats_retail_market_integration'].cursor()


@pytest.fixture
def update_taxi_config(taxi_config):
    """
    Updates only specified keys in the config, without touching other keys.
    E.g. if original config is `{ a: 1, b: 2}`, then value `{ b: 3, c: 4}`
    will set the config to `{ a: 1, b: 3, c: 4}`.
    """

    def _impl(config_name, config_value):
        updated_config = copy.deepcopy(taxi_config.get(config_name))
        updated_config.update(config_value)
        taxi_config.set(**{config_name: updated_config})

    return _impl


@pytest.fixture(name='mock_eats_core_couriers_stats', autouse=True)
def coriers_stats(mockserver, load_json):
    response = load_json('couriers_stats_expected_response.json')

    @mockserver.json_handler('/eats-core/v1/export/settings/couriers-stats')
    def eats_core(request):
        return response

    return eats_core


@pytest.fixture(name='regions_settings', autouse=True)
def regions_settings(request, mockserver, load_json):

    ResponseType = typing.Optional[typing.Dict]

    class Context:
        def __init__(self):
            self._response: ResponseType = None

        def set_response(self, response: ResponseType):
            self._response = response

        @property
        def response(self) -> ResponseType:
            return self._response

    ctx = Context()

    marker = request.node.get_closest_marker('regions_settings')
    if marker:
        if 'file' in marker.kwargs:
            ctx.set_response(load_json(marker.kwargs['file']))
        elif marker.args:
            ctx.set_response(marker.args[0])

    @mockserver.json_handler('/eats-core/v1/export/settings/regions-settings')
    def _eats_core(_):
        response = ctx.response
        if response is None:
            return mockserver.make_response(status=500)
        return response

    return ctx


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


@pytest.fixture(autouse=True, name='eats_catalog_storage')
def eats_catalog_storage(mockserver, load_json, eats_catalog_storage_cache):
    delivery_zone_projection = {
        'archived',
        'couriers_type',
        'delivery_conditions',
        'enabled',
        'features',
        'name',
        'place_id',
        'polygon',
        'shipping_type',
        'source_info',
        'timing',
        'working_intervals',
    }

    place_projection = {
        'address',
        'archived',
        'assembly_cost',
        'brand',
        'business',
        'categories',
        'country',
        'enabled',
        'extra_info',
        'features',
        'gallery',
        'launched_at',
        'location',
        'name',
        'payment_methods',
        'price_category',
        'quick_filters',
        'region',
        'slug',
        'sorting',
        'timing',
        'type',
        'new_rating',
        'working_intervals',
        'allowed_couriers_types',
        'tags',
    }

    class Context:
        def __init__(self):
            self.__revision = 1
            self.__places = []
            self.__zones = []
            self.by_slug = {}
            self.by_brand_slug = {}
            self.index = {}
            self.search = None

        def add_place(self, place: storage.Place):
            self.__revision = self.__revision + 1

            place['revision_id'] = self.__revision
            place['updated_at'] = '1991-01-20T02:00:00+03:00'

            self.__places.append(place)

            place_id = place['id']
            if place_id not in self.index:
                self.index[place_id] = []

            self.by_slug[place['slug']] = place_id

            place_brand_slug = place['brand']['slug']
            if place_brand_slug not in self.by_brand_slug:
                self.by_brand_slug[place_brand_slug] = [place_id]
            else:
                self.by_brand_slug[place_brand_slug].append(place_id)

        def add_place_from_file(self, filename: str):
            self.add_place(load_json(filename))

        def add_zone(self, zone: storage.Zone):
            self.__revision = self.__revision + 1

            zone['revision_id'] = self.__revision
            zone['updated_at'] = '1991-01-20T02:00:00+03:00'
            self.__zones.append(zone)

            if zone['place_id'] not in self.index:
                self.index[zone['place_id']] = []

            self.index[zone['place_id']].append(zone['id'])

        def add_zones_from_file(self, filename: str):
            data = load_json(filename)
            for zone in data['zones']:
                self.add_zone(zone)

        def get_places(self) -> typing.List[storage.Place]:
            places = self.__places
            self.__places = []
            return places

        def get_zones(self) -> typing.List[storage.Zone]:
            zones = self.__zones
            self.__zones = []
            return zones

        def overide_search(self, func):
            self.search = func

        def get_revision(self):
            return self.__revision

        @property
        def search_times_called(self) -> int:
            return search_places_zones.times_called

        @property
        def search_bbox_times_called(self) -> int:
            return search_places_within_bbox.times_called

    ctx = Context()

    prefix: str = '/eats-catalog-storage/internal/eats-catalog-storage/v1/'

    @mockserver.json_handler(prefix + 'places/retrieve-by-revision-ids')
    def _place_by_revisions(_):
        return {'places': []}

    @mockserver.json_handler(
        prefix + 'delivery_zones/retrieve-by-revision-ids',
    )
    def _delivery_zones_by_revisions(_):
        return {'delivery_zones': []}

    @mockserver.json_handler(prefix + 'places/updates')
    def _place_updates(request):
        projection = request.json['projection']
        projection.sort()

        assert (
            set(projection) == place_projection
        ), 'unexpected place projection'
        return {
            'places': ctx.get_places(),
            'last_known_revision': ctx.get_revision(),
        }

    @mockserver.json_handler(prefix + 'delivery_zones/updates')
    def _delivery_zones_updates(request):
        projection = request.json['projection']
        projection.sort()

        assert (
            set(projection) == delivery_zone_projection
        ), 'unexpected delivery zone projection'
        return {
            'delivery_zones': ctx.get_zones(),
            'last_known_revision': ctx.get_revision(),
        }

    @mockserver.json_handler(prefix + 'search/places-zones-ids')
    def search_places_zones(request):
        if ctx.search is not None:
            return ctx.search(request)

        ids = []

        if 'place_slug' in request.json:
            slug = request.json['place_slug']
            if slug in ctx.by_slug:
                place_id = ctx.by_slug[slug]
                ids.append(
                    {'place_id': place_id, 'zone_ids': ctx.index[place_id]},
                )

        elif 'brand_slug' in request.json:
            place_brand_slug = request.json['brand_slug']
            if place_brand_slug in ctx.by_brand_slug:
                place_ids = ctx.by_brand_slug[place_brand_slug]
                for place_id in place_ids:
                    ids.append(
                        {
                            'place_id': place_id,
                            'zone_ids': ctx.index[place_id],
                        },
                    )
        else:
            for place_id in ctx.index:
                ids.append(
                    {'place_id': place_id, 'zone_ids': ctx.index[place_id]},
                )

        return {'ids': ids}

    @mockserver.json_handler(prefix + 'search/places-within-bbox')
    def search_places_within_bbox(request):
        if ctx.search is not None:
            return ctx.search(request)

        return {
            'places': [
                {'id': place_id, 'zone_ids': zones}
                for place_id, zones in ctx.index.items()
            ],
        }

    return ctx
