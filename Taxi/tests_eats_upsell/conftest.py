# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import typing

import pytest

from eats_upsell_plugins import *  # noqa: F403 F401

from . import eats_catalog_storage
from . import eats_discounts
from . import eats_products
from . import eats_rest_menu_storage as rest_menu_storage
from . import umlaas_eats


def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        'smart_prices_cache: [smart_prices_cache] ' 'fixture fo service cache',
    )
    config.addinivalue_line(
        'markers',
        'smart_prices_items: [smart_prices_items] ' 'fixture fo service cache',
    )


@pytest.fixture(name='eats_catalog_storage_service')
def eats_catalog_storage_service(mockserver):
    class Context:
        def __init__(self):
            self.business = eats_catalog_storage.Business.RESTAURANT
            self.places_by_ids = {}
            self.places_by_slugs = {}

        def add_place(self, place: eats_catalog_storage.StoragePlace):
            self.places_by_ids[place.place_id] = place
            self.places_by_slugs[place.place_slug] = place

        def get_place_by_slug(
                self, slug: str,
        ) -> typing.Optional[eats_catalog_storage.StoragePlace]:
            return self.places_by_slugs.get(slug, None)

        def get_place_by_id(
                self, place_id: int,
        ) -> typing.Optional[eats_catalog_storage.StoragePlace]:
            return self.places_by_ids.get(place_id, None)

        @property
        def times_called(self) -> int:
            return search_places_list.times_called

    ctx = Context()

    @mockserver.json_handler(
        '/eats-catalog-storage/internal/eats-catalog-storage'
        '/v1/search/places/list',
    )
    def search_places_list(request):
        assert 'place_ids' in request.json or 'place_slugs' in request.json

        places = []
        if 'place_ids' in request.json:
            assert request.json['place_ids']
            for place_id in request.json['place_ids']:
                place = ctx.get_place_by_id(place_id)
                if place:
                    places.append(place)

        elif 'place_slugs' in request.json:
            assert request.json['place_slugs']
            for place_slug in request.json['place_slugs']:
                place = ctx.get_place_by_slug(place_slug)
                if place:
                    places.append(place)

        return {'places': places}

    return ctx


@pytest.fixture(name='umlaas_suggest')
def umlaas_service(mockserver):
    class Context:
        def __init__(self):
            self.items = []
            self.expected_request = None

        def set_expected_request(self, request: umlaas_eats.SuggestRequest):
            self.expected_request = request

        def add_item(self, item: umlaas_eats.SuggestItem):
            self.items.append(item)

        def add_items(self, items: typing.List[umlaas_eats.SuggestItem]):
            if not items:
                return
            self.items.extend(items)

        @property
        def times_called(self) -> int:
            return suggest.times_called

    ctx = Context()

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/eats-suggest')
    def suggest(request):
        assert 'request_id' in request.query
        if ctx.expected_request:
            assert ctx.expected_request == request.json

        return {
            'items': ctx.items,
            'exp_list': [],
            'request_id': request.query['request_id'],
        }

    return ctx


@pytest.fixture(name='core_menu_items')
def eats_core_service(mockserver):
    class Context:
        def __init__(self):
            self.items = None

        def set_items(self, items: list):
            self.items = items

        def add_item(self, item):
            if not self.items:
                self.set_items([])

            self.items.append(item)

        @property
        def times_called(self) -> int:
            return get_items.times_called

    ctx = Context()

    @mockserver.json_handler(
        '/eats-core-place-menu/internal-api/v1/place/menu/get-items',
    )
    def get_items(request):
        if not ctx.items:
            return mockserver.make_response('no items info', status=500)

        return {
            'place_id': '1',
            'place_slug': 'place_1',
            'place_brand_business_type': 'restaurant',
            'place_menu_items': ctx.items,
        }

    return ctx


@pytest.fixture(name='products_menu_items')
def eats_products_service(mockserver):
    class Context:
        def __init__(self):
            self.items = None

        def set_items(self, items: typing.List[eats_products.RetailItem]):
            self.items = items

        def add_item(self, item: eats_products.RetailItem):
            if not self.items:
                self.set_items([])

            self.items.append(item)

        @property
        def times_called(self) -> int:
            return get_items.times_called

    ctx = Context()

    @mockserver.json_handler('/eats-products/api/v2/menu/get-items')
    def get_items(request):
        if not ctx.items:
            return mockserver.make_response('no items info', status=500)

        return {
            'place_id': 2,
            'place_slug': 'place_2',
            'place_brand_business_type': 'shop',
            'place_menu_items': ctx.items,
        }

    return ctx


@pytest.fixture(name='umlaas_eats_retail_suggest')
def umlaas_eats_retail_suggest(mockserver):
    class Context:
        def __init__(self):
            self.status_code = 200
            self.recommendations = []
            self.expected_request = None

        def set_status_code(self, status_code: int):
            self.status_code = status_code

        def set_expected_request(self, request: umlaas_eats.SuggestRequest):
            self.expected_request = request

        def add_recommendation(self, public_id: str):
            self.recommendations.append(public_id)

        def set_recommendations(self, public_ids: typing.List[str]):
            self.recommendations.extend(public_ids)

        @property
        def times_called(self) -> int:
            return suggest.times_called

    ctx = Context()

    @mockserver.json_handler(
        '/umlaas-eats/internal/umlaas-eats/v1/retail/suggest',
    )
    def suggest(request):
        if ctx.expected_request:
            assert ctx.expected_request == request.json
        return mockserver.make_response(
            status=ctx.status_code,
            json={
                'request_id': 'testsuite',
                'recommendations': ctx.recommendations,
                'experiments': [],
            },
        )

    return ctx


@pytest.fixture(name='products_id_mappings')
def eats_products_id_mappings(mockserver):
    class Context:
        def __init__(self):
            self.mappings = []

        def add_mapping(self, mapping: eats_products.Mapping):
            self.mappings.append(mapping)

        def add_mappings(self, mappings: typing.List[eats_products.Mapping]):
            self.mappings.extend(mappings)

        @property
        def times_called(self) -> int:
            return get_mappings.times_called

    ctx = Context()

    @mockserver.json_handler('/eats-products/internal/v2/products/public_id')
    def get_mappings(request):
        return {'products_ids': ctx.mappings}

    return ctx


@pytest.fixture()
def rest_menu_storage_get_items(mockserver):
    class Context:
        def __init__(self):
            self.places: typing.List[rest_menu_storage.Place] = []
            self.status_code: int = 200
            self.assert_callback: typing.Optional[typing.Callable] = None

        @property
        def times_called(self) -> int:
            return get_items.times_called

    ctx = Context()

    @mockserver.json_handler('/eats-rest-menu-storage/internal/v1/get-items')
    def get_items(request):
        if ctx.assert_callback:
            ctx.assert_callback(request)  # pylint: disable=not-callable
        response = rest_menu_storage.GetItemsResponse(places=ctx.places)
        return mockserver.make_response(
            json=response.as_dict(), status=ctx.status_code,
        )

    return ctx


@pytest.fixture()
def discounts_match_discounts(mockserver):
    class Context:
        def __init__(self):
            self.menu_discounts: typing.List[eats_discounts.MenuDiscount] = []
            self.restaurant_menu_discounts: typing.List[
                eats_discounts.RestaurantMenuDiscount
            ] = []
            self.status_code: int = 200
            self.assert_callback: typing.Optional[typing.Callable] = None

        def add_menu_discount(
                self, menu_discount: eats_discounts.MenuDiscount,
        ):
            self.menu_discounts.append(menu_discount)

        def add_restaurant_menu_discounts(
                self,
                restaurant_menu_discount: eats_discounts.RestaurantMenuDiscount,  # noqa: E501
        ):
            self.restaurant_menu_discounts.append(restaurant_menu_discount)

        @property
        def times_called(self) -> int:
            return match_discounts.times_called

    ctx = Context()

    @mockserver.json_handler('/eats-discounts/v2/match-discounts')
    def match_discounts(request):
        if ctx.assert_callback:
            ctx.assert_callback(request)  # pylint: disable=not-callable
        result = {'match_results': []}
        assert request.json['common_conditions']['conditions']['country']
        for menu_discount in ctx.menu_discounts:
            result['match_results'].append(
                {
                    'hierarchy_name': 'menu_discounts',
                    'discounts': [
                        {
                            'discount_id': menu_discount.discount_id,
                            'discount_meta': {
                                'promo': {
                                    'name': menu_discount.name,
                                    'description': menu_discount.description,
                                    'picture_uri': menu_discount.picture_uri,
                                    'promo_type': menu_discount.promo_type,
                                },
                            },
                            'money_value': {
                                'menu_value': {
                                    'value_type': menu_discount.value_type,
                                    'value': menu_discount.value,
                                },
                            },
                        },
                    ],
                    'subquery_results': [
                        {
                            'id': menu_discount.id,
                            'discount_id': menu_discount.discount_id,
                        },
                    ],
                },
            )
        for rest_menu_discount in ctx.restaurant_menu_discounts:
            result['match_results'].append(
                {
                    'hierarchy_name': 'restaurant_menu_discounts',
                    'discounts': [
                        {
                            'discount_id': rest_menu_discount.discount_id,
                            'discount_meta': {
                                'promo': {
                                    'name': rest_menu_discount.name,
                                    'description': (
                                        rest_menu_discount.description
                                    ),
                                    'picture_uri': (
                                        rest_menu_discount.picture_uri
                                    ),
                                },
                            },
                            'money_value': {
                                'menu_value': {
                                    'value_type': (
                                        rest_menu_discount.value_type
                                    ),
                                    'value': rest_menu_discount.value,
                                },
                            },
                        },
                    ],
                    'subquery_results': [
                        {
                            'id': rest_menu_discount.id,
                            'discount_id': rest_menu_discount.discount_id,
                        },
                    ],
                },
            )
        return mockserver.make_response(json=result, status=ctx.status_code)

    return ctx
