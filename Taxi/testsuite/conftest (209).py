# pylint: disable=too-many-lines

# root conftest for service eats-catalog
import copy
import json
import typing

import pytest
# from eats_regions_cache import eats_regions_cache  # noqa: F403 F401
from tests_eats_catalog.eats_catalog import adverts
from tests_eats_catalog.eats_catalog import storage
from tests_eats_catalog.eats_catalog import surge_utils
from tests_eats_catalog.eats_catalog import umlaas

pytest_plugins = ['eats_catalog_plugins.pytest_plugins']


def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        'eats_regions_cache: [eats_regions_cache] '
        'fixture for regions cache',
    )
    config.addinivalue_line(
        'markers',
        'regions_settings: [regions_settings] ' 'fixture for regions settings',
    )


@pytest.fixture(autouse=True)
def eats_discounts_applicator(mockserver):
    class Context:
        class Hierarchy:
            binds: 'dict[str, list[str]]' = None
            discounts: list = None

            def __init__(self) -> None:
                self.binds = {}
                self.discounts = []

        mock_eats_order_stats = None
        mock_eats_catalog_storage = None
        mock_eats_discounts = None
        hierarchies: 'dict[str, Hierarchy]' = {}
        mock_eats_discounts_matches_exp = None
        mock_eats_tags = None
        expected_retail_orders_count = None
        expected_restaurant_orders_count = None
        mock_delivery_method = None
        mock_shipping_type_array = set()

        # NOTE(beluc): 'extra' field is used for additional
        # fields that are returned depending on the hierarchy
        def add_discount(
                self,
                discount_id,
                hierarchy_name='menu_discounts',
                name='name',
                description='description',
                picture_uri='picture_uri',
                promo_type=None,
                extra=None,
        ):
            if hierarchy_name not in self.hierarchies.keys():
                self.hierarchies[hierarchy_name] = Context.Hierarchy()
            self.hierarchies[hierarchy_name].discounts.append(
                {
                    'id': discount_id,
                    'name': name,
                    'description': description,
                    'picture_uri': picture_uri,
                    'promo_type': promo_type,
                    'extra': extra or {},
                },
            )

        def bind_discount(
                self,
                place_id: str,
                discount_id: str,
                hierarchy_name: str = 'menu_discounts',
        ):
            assert hierarchy_name in self.hierarchies.keys()
            binds = self.hierarchies[hierarchy_name].binds
            if place_id not in binds.keys():
                binds[place_id] = []
            binds[place_id].append(discount_id)

    context = Context()

    @mockserver.json_handler('/eats-tags/v2/match_single')
    def _eats_tags(request):
        assert request.json.get('match', [])
        assert [
            item.get('type') in ['user_id', 'personal_phone_id']
            for item in request.json['match']
        ]
        tags = context.mock_eats_tags if context.mock_eats_tags else []
        return mockserver.make_response(status=200, json={'tags': tags})

    @mockserver.json_handler(
        '/eats-order-stats/internal/eats-order-stats/v1/orders',
    )
    def _eats_order_stats(_):
        return {
            'data': [
                {
                    'identity': {'type': 'eater_id', 'value': '1'},
                    'counters': [],
                },
            ],
        }

    @mockserver.json_handler(
        '/eats-catalog-storage/internal/eats-catalog-storage'
        '/v1/places/retrieve-by-ids',
    )
    def _eats_catalog_storage(_):
        # catalog send full info about place
        assert False

    @mockserver.json_handler('/eats-discounts/v3/fetch-discounts')
    def _eats_discounts(request):
        if context.mock_eats_discounts_matches_exp:
            assert set(context.mock_eats_discounts_matches_exp) == set(
                request.json['user_conditions']['experiments'],
            )

        if context.mock_eats_tags:
            assert set(context.mock_eats_tags) == set(
                request.json['user_conditions']['tags'],
            )
        assert 'country' in request.json
        assert 'orders_count' in request.json['user_conditions']
        assert 'restaurant_orders_count' in request.json['user_conditions']
        assert 'retail_orders_count' in request.json['user_conditions']

        if context.expected_retail_orders_count:
            assert (
                request.json['user_conditions']['retail_orders_count']
                == context.expected_retail_orders_count
            )
        if context.expected_restaurant_orders_count:
            assert (
                request.json['user_conditions']['restaurant_orders_count']
                == context.expected_restaurant_orders_count
            )
        if context.mock_delivery_method:
            for region in request.json['regions']:
                for brand in region['brands']:
                    for place in brand['places']:
                        assert (
                            place['delivery_method']
                            == context.mock_delivery_method
                        )

        context.mock_shipping_type_array.add(
            request.json['user_conditions']['shipping_type'],
        )

        return {
            'fetch_results': [
                {
                    'fetched_data': {
                        'discounts': [
                            {
                                'discount_id': discount['id'],
                                'discount_meta': {
                                    'text': discount['name'],
                                    'promo': {
                                        'description': discount['description'],
                                        'name': discount['name'],
                                        'picture_uri': discount['picture_uri'],
                                        'promo_type': discount['promo_type'],
                                    },
                                },
                                'product_value': {
                                    'bundle': 2,
                                    'discount_value': '1.5',
                                },
                                **discount['extra'],
                            }
                            for discount in hierarchy.discounts
                        ],
                        'hierarchy_name': hierarchy_name,
                    },
                    'fetched_parameters': [
                        {'products': {'is_excluded': False, 'values': []}},
                    ],
                    'places_fetch_results': [
                        {
                            'data': [
                                {'discount_id': discount_id, 'items_index': 0}
                                for discount_id in discounts
                            ],
                            'id': int(place_id),
                        }
                        for place_id, discounts in hierarchy.binds.items()
                    ],
                }
                for hierarchy_name, hierarchy in context.hierarchies.items()
            ],
        }

    context.mock_eats_order_stats = _eats_order_stats
    context.mock_eats_catalog_storage = _eats_catalog_storage
    context.mock_eats_discounts = _eats_discounts
    return context


@pytest.fixture(autouse=True, name='offers')
def eats_offers(mockserver):
    class Context:
        def __init__(self):
            self.match_expected_request = None
            self.match = mockserver.make_response(
                status=404, json={'code': 'NOT_FOUND', 'message': 'not_found'},
            )

            self.set_expected_request = None
            self.set = mockserver.make_response(
                status=500,
                json={'code': 'NOT_SET', 'message': 'mock is empty'},
            )

        def match_response(self, status: int, body: dict) -> None:
            self.match = mockserver.make_response(status=status, json=body)

        def match_request(self, body: typing.Optional[dict]) -> None:
            self.match_expected_request = body

        @property
        def match_times_called(self):
            return eats_offers_match.times_called

        def set_response(self, status: int, body: dict) -> None:
            self.set = mockserver.make_response(status=status, json=body)

        def set_request(self, body: typing.Optional[dict]) -> None:
            self.set_expected_request = body

        @property
        def set_times_called(self):
            return eats_offers_set.times_called

    ctx = Context()

    @mockserver.json_handler('/eats-offers/v1/offer/match')
    def eats_offers_match(request):
        if ctx.match_expected_request is not None:
            assert request.json == ctx.match_expected_request
        return ctx.match

    @mockserver.json_handler('/eats-offers/v1/offer/set')
    def eats_offers_set(request):
        if ctx.set_expected_request is not None:
            assert request.json == ctx.set_expected_request
        return ctx.set

    return ctx


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
    # response = load_json('regions_settings.json')

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


@pytest.fixture(autouse=True)
def quick_filters(mockserver, load_json):
    response = load_json('quick_filters.json')

    @mockserver.json_handler('/eats-core/v1/export/quick-filters')
    def eats_core(_):
        return response

    return eats_core


@pytest.fixture(autouse=True)
def eta_service_default(mockserver):
    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/eta')
    def _(_):
        return mockserver.make_response(
            status=500,
            response=json.dumps(
                {
                    'code': 'DEFAULT_MOCK',
                    'message': 'this is fatal error from default mock',
                },
            ),
        )


@pytest.fixture(name='prediction')
def eta_service(mockserver):
    class Context:
        def __init__(self):
            self.expected_request = None
            # Словарь с предсказаниями времен которые нужно вернуть
            self.__places: dict = {}
            self.should_fail = True

        def set_place_time(
                self, place_id: int, min_minutes: int, max_minutes: int,
        ):
            self.should_fail = False
            self.__places[place_id] = {'min': min_minutes, 'max': max_minutes}

        def unset_place_time(self, place_id: int):
            del self.__places[place_id]
            self.should_fail = len(self.__places) == 0

        def get_place_time(self, place_id: int):
            if place_id in self.__places:
                return self.__places[place_id]
            return None

        @property
        def times_called(self) -> int:
            return cart_eta.times_called

    ctx = Context()

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/eta')
    def cart_eta(request):
        if ctx.expected_request is not None:
            assert (
                request.json == ctx.expected_request
            ), 'unexpected cart_eta request'

        if ctx.should_fail:
            return mockserver.make_response('error', status=500)

        predicted_times = []

        for requested_time in request.json['requested_times']:
            times = ctx.get_place_time(requested_time['place']['id'])
            if times is None:
                continue
            predicted_times.append(
                {
                    'id': requested_time['id'],
                    'times': {
                        'total_time': times['max'],
                        'cooking_time': times['max'] * 0.2,
                        'delivery_time': times['max'] * 0.8,
                        'boundaries': {
                            'min': times['min'],
                            'max': times['max'],
                        },
                    },
                },
            )

        return {
            'exp_list': [],
            'request_id': request.query['request_id'],
            'provider': 'testsuite',
            'predicted_times': predicted_times,
        }

    return ctx


@pytest.fixture(name='delivery_price', autouse=True)
def delivery_price_service(mockserver):
    class Context:
        def __init__(self):
            self.request_callback = None
            self.expected_request = None
            self.should_fail = True
            self.__delivery_conditions: typing.List[dict] = None
            self.__weight_conditions: typing.List[dict] = None
            self.__thresholds_info: typing.Optional[dict] = None
            self.__place_surge: dict = None
            self.surge_final_cost = None
            self.continuous_surge_range = None

        def request_assertion(self, callback):
            self.request_callback = callback
            return callback

        def update_should_fail(self):
            self.should_fail = (
                self.__delivery_conditions is None
                or self.__place_surge is None
            )

        def set_delivery_conditions(self, conditions: typing.List[dict]):
            self.__delivery_conditions = conditions
            self.update_should_fail()

        def set_weight_conditions(self, conditions: typing.List[dict]):
            self.__weight_conditions = conditions
            self.update_should_fail()

        def set_thresholds_info(self, thresholds_info: dict):
            self.__thresholds_info = thresholds_info
            self.update_should_fail()

        def get_delivery_conditions(self) -> typing.List[dict]:
            return self.__delivery_conditions

        def get_weight_conditions(self) -> typing.List[dict]:
            return self.__weight_conditions

        def get_thresholds_info(self) -> typing.Optional[dict]:
            return self.__thresholds_info

        def set_place_surge(self, surge: dict):
            self.__place_surge = surge
            self.update_should_fail()

        def set_surge_final_cost(self, cost: int):
            self.surge_final_cost = cost
            self.update_should_fail()

        def set_continuous_surge_range(self, min_value: int, max_value: int):
            self.continuous_surge_range = {
                'min': str(min_value),
                'max': str(max_value),
            }
            self.update_should_fail()

        def get_place_surge(self) -> dict:
            return self.__place_surge

        @property
        def times_called(self) -> int:
            return eda_delivery_price_surge.times_called

    ctx = Context()

    @mockserver.json_handler(
        '/eda-delivery-price/v1/calc-delivery-price-surge',
    )
    def eda_delivery_price_surge(request):
        if ctx.request_callback:
            ctx.request_callback(request)
        elif ctx.expected_request is not None:
            assert (
                request.json == ctx.expected_request
            ), 'unexpected eda-delivery-price-surge request'

        if ctx.should_fail:
            return mockserver.make_response('error', status=500)
        surge_extra = {}
        if ctx.surge_final_cost is not None:
            surge_extra['final_cost'] = ctx.surge_final_cost
        if ctx.continuous_surge_range is not None:
            surge_extra['continuous_surge_range'] = ctx.continuous_surge_range
        result = {
            'calculation_result': {
                'calculation_name': 'testsuite',
                'result': {
                    'fees': ctx.get_delivery_conditions(),
                    'weight_fees': ctx.get_weight_conditions(),
                    'is_fallback': False,
                    'extra': {},
                },
            },
            'experiment_results': [],
            'experiment_errors': [],
            'surge_result': ctx.get_place_surge(),
            'surge_extra': surge_extra,
            'meta': {},
            'service_fee': '49',
        }
        thresholds_info = ctx.get_thresholds_info()
        if thresholds_info:
            result.update({'thresholds_info': thresholds_info})
        return result

    @mockserver.json_handler('/eda-delivery-price/v1/user-promo')
    def _eda_delivery_price_user_promo(request):
        return mockserver.make_response('error', status=500)

    return ctx


@pytest.fixture(name='surge', autouse=True)
def surge_service(mockserver):
    class PlaceInfo(typing.NamedTuple):
        surge: typing.Optional[dict]
        free_delivery: typing.Optional[dict]

    class Context:
        def __init__(self):
            self.expected_user: typing.Optional[dict] = None
            self.expected_location: typing.Optional[dict] = None
            self.expected_params = None
            self.places_info: dict = {}
            self.user_info: typing.Optional[dict] = None
            self.should_fail = True

        def set_place_info(
                self,
                place_id: int,
                surge: typing.Optional[dict] = None,
                free_delivery: typing.Optional[dict] = None,
        ):
            assert surge is not None or free_delivery is not None
            self.should_fail = False
            self.places_info[place_id] = PlaceInfo(
                surge=surge, free_delivery=free_delivery,
            )

        def unset_place_surge(self, place_id: int):
            del self.places_info[place_id]
            self.should_fail = (
                len(self.places_info) == 0 and self.user_info is None
            )

        def get_place_info(self, place_id: int):
            if place_id in self.places_info:
                return self.places_info[place_id]
            return None

        def set_expected(
                self,
                expected_params: typing.Optional[dict] = None,
                expected_user: typing.Optional[dict] = None,
                expected_location: typing.Optional[dict] = None,
        ):
            self.expected_params = expected_params
            self.expected_user = expected_user
            self.expected_location = expected_location

        def set_user_info(self, user_info: dict):
            self.should_fail = False
            self.user_info = user_info

        @property
        def times_called(self) -> int:
            return calc_surge_bulk.times_called

    ctx = Context()

    @mockserver.json_handler('/eda-delivery-price/v2/calc-surge-bulk')
    def calc_surge_bulk(request):
        if ctx.expected_user is not None:
            user_id = ctx.expected_user['user_id']
            personal_phone_id = ctx.expected_user['personal_phone_id']
            assert (
                set(
                    map(
                        lambda s: s.strip(),
                        request.headers['X-Eats-User'].split(','),
                    ),
                )
                == {
                    f'user_id={user_id}',
                    f'personal_phone_id={personal_phone_id}',
                }
            )
            device_id = ctx.expected_user['device_id']
            assert request.headers['X-Device-Id'] == device_id

        if ctx.expected_location is not None:
            region_id = ctx.expected_location['region_id']
            position = ctx.expected_location['position']
            assert request.json['region_id'] == region_id
            assert request.json['position'] == position
        if ctx.expected_params is not None:
            assert request.json == ctx.expected_params
        if ctx.should_fail:
            return mockserver.make_response('error', status=500)

        user_info = {
            'is_eda_new_user': False,
            'is_retail_new_user': False,
            'tags': [],
            'any_free_delivery': False,
        }
        if ctx.user_info is not None:
            user_info.update(ctx.user_info)

        places_info = []

        for place_id, place_info in ctx.places_info.items():
            if place_info.surge is not None:
                surge_data = copy.deepcopy(place_info.surge)
            else:
                surge_data = {}

            surge_data['placeId'] = place_id
            data = {'surge': surge_data}
            if place_info.free_delivery is not None:
                data['free_delivery'] = place_info.free_delivery
            places_info.append(data)

        return {'user_info': user_info, 'places_info': places_info}

    return ctx


@pytest.fixture(autouse=True)
def eats_core_promo(mockserver):
    @mockserver.json_handler('/eats-core-promo/server/api/v1/promo/active')
    def _active(_):
        return {'cursor': '', 'promos': []}


@pytest.fixture(autouse=True)
def eats_plus_404(mockserver):
    @mockserver.handler(
        '/eats-plus/internal/eats-plus/v1/presentation/cashback/place',
    )
    def _eats_plus(request):
        return mockserver.make_response(status=404)

    @mockserver.json_handler(
        '/eats-plus/internal/eats-plus/v1/presentation/cashback/places-list',
    )
    def _eats_plus_places_list(request):
        return {'cashback': []}


@pytest.fixture(autouse=True)
def eats_user_reactions_400(mockserver):
    @mockserver.handler(
        '/eats-user-reactions/eats-user-reactions/v1/favourites/find-by-eater',
    )
    def _eats_user_reactions(request):
        return mockserver.make_response(status=400)


@pytest.fixture(autouse=True)
def umlaas_eats_empty(mockserver):
    @mockserver.handler('/umlaas-eats/umlaas-eats/v1/catalog')
    def _umlaas_eats(request):
        return mockserver.make_response(
            json={
                'exp_list': [],
                'request_id': '',
                'provider': '',
                'available_blocks': [],
                'result': [],
            },
        )


@pytest.fixture(autouse=True)
def umlaas_filters_ranking(mockserver):
    @mockserver.handler('/umlaas-eats/umlaas-eats/v1/filters')
    def _filters(request):
        return mockserver.make_response(status=502)


@pytest.fixture(autouse=True, name='eats_catalog_storage')
def eats_catalog_storage(mockserver, load_json, eats_catalog_storage_cache):
    delivery_zone_projection = {
        'archived',
        'couriers_type',
        'delivery_conditions',
        'enabled',
        'name',
        'place_id',
        'polygon',
        'shipping_type',
        'timing',
        'working_intervals',
        'source_info',
        'features',
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


@pytest.fixture(autouse=True)
def eats_tags(mockserver):
    @mockserver.handler('/eats-tags/v1/match')
    def _match(request):
        return mockserver.make_response(status=502)


@pytest.fixture(autouse=True)
def grocery_api(mockserver):
    @mockserver.json_handler(
        '/grocery-api/lavka/v1/api/v1/virtual-categories-availability',
    )
    def _virtual_categories_availability(_):
        return mockserver.make_response(status=500)


@pytest.fixture(name='catalog_for_layout')
def catalog_for_layout(taxi_eats_catalog):
    default_location = {'longitude': 37.591503, 'latitude': 55.802998}
    default_headers = {
        'x-device-id': 'test_simple',
        'x-request-id': 'hello',
        'x-platform': 'ios_app',
        'x-app-version': '6.1.0',
        'cookie': 'just a cookie',
        'x-yandex-uid': '12341212',
        'X-Eats-User': 'user_id=1234',
    }

    async def execute(
            blocks,
            condition=None,
            location=None,
            headers=None,
            delivery_time=None,
            time=None,
            filters=None,
            filters_v2=None,
            sort=None,
    ):
        if location is None:
            location = default_location
        if headers is None:
            headers = default_headers

        if time is not None:
            delivery_time = {'time': time, 'zone': 10800}

        return await taxi_eats_catalog.post(
            '/internal/v1/catalog-for-layout',
            headers=headers,
            json={
                'location': location,
                'blocks': blocks,
                'condition': condition,
                'delivery_time': delivery_time,
                'filters': filters,
                'filters_v2': filters_v2,
                'sort': sort,
            },
        )

    return execute


@pytest.fixture(name='catalog_for_wizard')
def catalog_for_wizard(taxi_eats_catalog):
    async def execute(
            lon: typing.Optional[float] = 37.591503,
            lat: typing.Optional[float] = 55.802998,
            quick_filter_id: typing.Optional[int] = None,
            region: typing.Optional[int] = None,
            limit: typing.Optional[int] = None,
            after: typing.Optional[str] = None,
    ):
        params = {
            'longitude': lon,
            'latitude': lat,
            'userRegion': region,
            'limit': limit,
            'after': after,
            'quickFilterId': quick_filter_id,
        }
        return await taxi_eats_catalog.get(
            '/internal/v1/catalog-for-wizard',
            params={
                key: value
                for key, value in params.items()
                if value is not None
            },
        )

    return execute


Query = typing.Dict[str, typing.Optional[typing.Union[str, float]]]
Headers = typing.Dict[str, str]


@pytest.fixture(name='brand_slug')
def brand_slug(taxi_eats_catalog):
    async def execute(
            slug: str,
            query: typing.Optional[Query] = None,
            headers: typing.Optional[Headers] = None,
    ):
        request_query: Query = {
            'latitude': 55.73442,
            'longitude': 37.583948,
            'regionId': 1,
        }
        if query is not None:
            request_query.update(query)

        request_headers: Headers = {
            'x-device-id': 'testuite',
            'x-platform': 'desktop_web',
            'x-app-version': '0.0.0',
        }

        if headers is not None:
            request_headers.update(headers)

        return await taxi_eats_catalog.get(
            f'/eats-catalog/v1/brand/{slug}',
            params={k: v for k, v in request_query.items() if v is not None},
            headers={
                k: v for k, v in request_headers.items() if v is not None
            },
        )

    return execute


@pytest.fixture(name='slug')
def slug_handler(taxi_eats_catalog):
    async def execute(
            slug: str,
            query: typing.Optional[Query] = None,
            headers: typing.Optional[Headers] = None,
    ):
        request_query: Query = {
            'latitude': 55.802998,
            'longitude': 37.591503,
            'regionId': 1,
        }
        if query is not None:
            request_query.update(query)

        request_headers: Headers = {
            'x-device-id': 'testsuite',
            'x-platform': 'ios_app',
            'x-app-version': '5.7.0',
        }

        if headers is not None:
            request_headers.update(headers)

        return await taxi_eats_catalog.get(
            f'/eats-catalog/v1/slug/{slug}',
            params={k: v for k, v in request_query.items() if v is not None},
            headers={
                k: v for k, v in request_headers.items() if v is not None
            },
        )

    return execute


@pytest.fixture(name='internal_place')
def internal_place(taxi_eats_catalog):
    default_location = [37.591503, 55.802998]
    default_headers = {
        'x-device-id': 'test_simple',
        'x-request-id': 'hello',
        'x-platform': 'ios_app',
        'x-app-version': '6.1.0',
    }

    async def execute(
            slug,
            position=None,
            delivery_time=None,
            headers=None,
            disable_pricing=False,
    ):
        if headers is None:
            headers = default_headers
        if position is None:
            position = default_location
        return await taxi_eats_catalog.post(
            '/internal/v1/place',
            headers=headers,
            json={
                'slug': slug,
                'position': position,
                'delivery_time': delivery_time,
                'disable_pricing': disable_pricing,
            },
        )

    return execute


@pytest.fixture(name='delivery_zones_resolve')
def delivery_zones_resolve(taxi_eats_catalog):
    default_location = [37.591503, 55.802998]

    async def execute(
            place_id,
            delivery_time=None,
            location=None,
            shipping_type='delivery',
            headers=None,
    ):
        if location is None:
            location = default_location

        return await taxi_eats_catalog.post(
            '/internal/v1/delivery-zones/resolve',
            headers=headers,
            json={
                'place_id': place_id,
                'delivery_time': delivery_time,
                'location': location,
                'shipping_type': str(shipping_type),
            },
        )

    return execute


@pytest.fixture(name='v2_delivery_zones_resolve')
def v2_delivery_zones_resolve(taxi_eats_catalog):
    default_location = [37.591503, 55.802998]

    async def execute(
            place_id,
            delivery_time=None,
            location=None,
            shipping_type='delivery',
            headers=None,
    ):
        if location is None:
            location = default_location

        return await taxi_eats_catalog.post(
            '/internal/v2/delivery-zones/resolve',
            headers=headers,
            json={
                'place_id': place_id,
                'delivery_time': delivery_time,
                'location': location,
                'shipping_type': str(shipping_type),
            },
        )

    return execute


@pytest.fixture(name='umlaas_eta')
def umlaas_eta(mockserver):
    class Context:
        def __init__(self):
            self._eta: typing.Dict[int, umlaas.UmlaasEta] = {}
            self._relevance: typing.Dict[int, float] = {}
            self._request_assert = None

        def set_eta(self, eta: umlaas.UmlaasEta):
            self._eta[eta.place_id] = eta

        def set_relevance(self, place_id: int, relevance: float):
            self._relevance[place_id] = relevance

        def set_request_assert(self, check_func):
            self._request_assert = check_func

        def request_assert(self, request):
            if self._request_assert is not None:
                self._request_assert(request)

        @property
        def all_etas(self):
            return self._eta.values()

        @property
        def relevance(self):
            return self._relevance

        @property
        def times_called(self) -> int:
            return umlaas_eats.times_called

    ctx = Context()

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/catalog')
    def umlaas_eats(request):
        ctx.request_assert(request)

        result: list = []
        for eta in ctx.all_etas:
            result.append(
                {
                    'id': eta.place_id,
                    'relevance': ctx.relevance.get(
                        eta.place_id, float(eta.place_id),
                    ),
                    'type': 'ranking',
                    'predicted_times': {
                        'min': eta.eta_min,
                        'max': eta.eta_max,
                    },
                    'blocks': [],
                },
            )
        return {
            'exp_list': [],
            'request_id': '',
            'provider': '',
            'available_blocks': [],
            'result': result,
        }

    return ctx


@pytest.fixture(name='internal_places')
def internal_places(taxi_eats_catalog):
    default_location = {'longitude': 37.591503, 'latitude': 55.802998}
    default_headers = {
        'x-device-id': 'test_simple',
        'x-request-id': 'hello',
        'x-platform': 'ios_app',
        'x-app-version': '6.1.0',
    }

    async def execute(
            blocks,
            headers=None,
            location=None,
            time=None,
            shipping_type=None,
            filters: typing.Optional[typing.List[str]] = None,
            filters_v2=None,
            enable_deduplication=None,
    ):
        if headers is None:
            headers = default_headers
        if location is None:
            location = default_location

        delivery_time = None
        if time is not None:
            delivery_time = {'time': time, 'zone': 10800}

        return await taxi_eats_catalog.post(
            '/internal/v1/places',
            headers=headers,
            json={
                'blocks': blocks,
                'location': location,
                'delivery_time': delivery_time,
                'shipping_type': shipping_type,
                'filters': filters,
                'filters_v2': filters_v2,
                'enable_deduplication': enable_deduplication,
            },
        )

    return execute


@pytest.fixture()
def surge_resolver(mockserver):
    def do_nothing(*args, **kwargs):
        pass

    class Context:
        def __init__(self):
            self.place_radius: typing.Dict[int, surge_utils.SurgeRadius] = {}
            self.request_assertion_callback = do_nothing

        def request_assertion(self, callback):
            self.request_assertion_callback = callback
            return callback

        @property
        def times_called(self):
            return surge_handler.times_called

    ctx = Context()

    @mockserver.json_handler('/eats-surge-resolver/api/v2/surge-level')
    def surge_handler(request):
        ctx.request_assertion_callback(request)

        result = []
        for place_id, radius in ctx.place_radius.items():
            native_info = {
                'deliveryFee': radius.additional_fee,
                'surgeLevel': radius.native_surge_level,
                'loadLevel': 0,
                'show_radius': radius.pedestrian,
            }
            taxi_info = {
                'deliveryFee': 0,
                'surgeLevel': 0,
                'loadLevel': 0,
                'show_radius': radius.taxi,
            }
            lavka_info = {
                'minimumOrder': radius.minimum_order,
                'surgeLevel': radius.lavka_surge_level,
                'loadLevel': 0,
            }
            result.append(
                {
                    'calculatorName': 'calc_surge_eats_2100m',
                    'nativeInfo': native_info,
                    'taxiInfo': taxi_info,
                    'lavkaInfo': lavka_info,
                    'zoneId': 0,
                    'placeId': place_id,
                },
            )
        return result

    return ctx


@pytest.fixture(name='place_stats_cache')
def place_stats_cache(taxi_eats_catalog, taxi_config, yt_client):
    class Cache:
        def __init__(self, taxi_eats_catalog, taxi_config, yt_client):
            self.taxi_eats_catalog = taxi_eats_catalog
            self.taxi_config = taxi_config
            self.yt_client = yt_client
            self.places_stats = list()
            self.table = adverts.PlaceStatsTable()

        def add_place_stats(self, place_stats: adverts.PlaceStats) -> None:
            self.places_stats.append(place_stats)

        def add_places_stats(
                self, places_stats: typing.List[adverts.PlaceStats],
        ) -> None:
            self.places_stats.extend(places_stats)

        def write_table(self) -> None:
            yt_path = self.table.get_yt_path()
            if not self.yt_client.exists(yt_path):
                self.yt_client.create(
                    'table',
                    yt_path,
                    recursive=True,
                    attributes=self.table.get_attributes(),
                )

            data = [place_stats.asdict() for place_stats in self.places_stats]
            self.yt_client.write_table(yt_path, data, format=None)

        async def flush(self):
            self.write_table()
            self.taxi_config.set_values(
                {
                    'EATS_CATALOG_ADVERT_PLACE_STATS_CACHE': {
                        'enabled': True,
                        'cluster': 'yt-local',
                        'batch_size': 10000,
                        'table': self.table.get_yt_path(),
                    },
                },
            )

            return await taxi_eats_catalog.invalidate_caches(
                clean_update=True, cache_names=['place-stats-cache'],
            )

    return Cache(taxi_eats_catalog, taxi_config, yt_client)


@pytest.fixture(name='yabs')
def yabs_mock(mockserver):
    def do_nothing(*args, **kwargs):
        pass

    class Context:
        def __init__(self):
            self.status_code = 200
            self.page_id = 1
            self.service_banners = []
            self.request_assertion_callback = do_nothing

        def set_status_code(self, status_code: int):
            self.status_code = status_code

        def set_page_id(self, page_id: int):
            self.page_id = page_id

        def add_banner(self, service_banner: adverts.YabsServiceBanner):
            self.service_banners.append(service_banner)

        def add_banners(
                self, service_banners: typing.List[adverts.YabsServiceBanner],
        ):
            self.service_banners.extend(service_banners)

        def request_assertion(self, callback):
            self.request_assertion_callback = callback
            return callback

        @property
        def times_called(self) -> int:
            return page.times_called

    ctx = Context()

    @mockserver.json_handler(f'/yabs/page/{ctx.page_id}')
    def page(request):
        assert request.query
        ctx.request_assertion_callback(request)

        service_banner: list = []
        for banner in ctx.service_banners:
            service_banner.append(banner.asdict())

        return mockserver.make_response(
            status=ctx.status_code, json={'service_banner': service_banner},
        )

    return ctx


@pytest.fixture(name='relevant_ads_data_cache')
def relevant_ads_data_cache(taxi_eats_catalog, taxi_config, yt_client):
    class Cache:
        def __init__(self, taxi_eats_catalog, taxi_config, yt_client):
            self.taxi_eats_catalog = taxi_eats_catalog
            self.taxi_config = taxi_config
            self.yt_client = yt_client
            self.places_relevance = list()
            self.table = adverts.PlacesRelevanceTable()

        def add_place_relevance_stats(
                self, places_relevances: adverts.RelevantPlaceStats,
        ) -> None:
            self.places_relevance += places_relevances

        def write_table(self) -> None:
            yt_path = self.table.get_yt_path()
            if not self.yt_client.exists(yt_path):
                self.yt_client.create(
                    'table',
                    yt_path,
                    recursive=True,
                    attributes=self.table.get_attributes(),
                )

            data = [
                place_relevance.asdict()
                for place_relevance in self.places_relevance
            ]
            self.yt_client.write_table(yt_path, data, format=None)

        async def flush(self):
            self.write_table()
            self.taxi_config.set_values(
                {
                    'EATS_CATALOG_RELEVANT_DATA_CACHE': {
                        'enabled': True,
                        'cluster': 'yt-local',
                        'batch_size': 10000,
                        'table': self.table.get_yt_path(),
                    },
                },
            )

            return await taxi_eats_catalog.invalidate_caches(
                clean_update=True, cache_names=['relevant-ads-data-cache'],
            )

    return Cache(taxi_eats_catalog, taxi_config, yt_client)


@pytest.fixture(name='internal_place_promo')
def internal_place_promo(taxi_eats_catalog):
    default_headers = {
        'x-device-id': 'test_simple',
        'x-request-id': 'hello',
        'x-platform': 'ios_app',
        'x-app-version': '6.1.0',
    }

    async def execute(
            slug: str,
            location: dict = None,
            headers: dict = None,
            time: str = None,
            shipping_type: str = 'delivery',
    ):
        if headers is None:
            headers = default_headers

        return await taxi_eats_catalog.post(
            '/internal/v1/place/promos',
            headers=headers,
            json={
                'slug': slug,
                'position': location,
                'delivery_time': time,
                'shipping_type': shipping_type,
            },
        )

    return execute


@pytest.fixture(name='metric')
def metric_fixture(taxi_eats_catalog_monitor):
    async def get_metric(name: str):
        return await taxi_eats_catalog_monitor.get_metric(name)

    return get_metric
