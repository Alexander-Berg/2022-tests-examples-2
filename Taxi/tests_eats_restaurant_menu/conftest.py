# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import typing

import pytest

from eats_restaurant_menu_plugins import *  # noqa: F403 F401

from . import rest_menu_storage


def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        'eats_catalog_storage_cache: [eats_catalog_storage_cache] '
        'fixture fo service cache',
    )
    config.addinivalue_line(
        'markers',
        'smart_prices_cache: [smart_prices_cache] ' 'fixture fo service cache',
    )
    config.addinivalue_line(
        'markers',
        'smart_prices_items: [smart_prices_items] ' 'fixture fo service cache',
    )


@pytest.fixture(autouse=True)
def eats_discounts_applicator(mockserver):
    class Context:
        mock_eats_order_stats = None
        mock_eats_catalog_storage = None
        mock_match_discounts = None
        mock_eats_tags = None
        menu_discount = []
        restaurant_menu_discounts = []
        product_discount = []

        def add_menu_discount(
                self,
                item_id,
                discount_id,
                value,
                value_type='absolute',
                name='name',
                description='description',
                picture_uri='picture_uri',
        ):
            self.menu_discount.append(
                {
                    'id': item_id,
                    'discount_id': discount_id,
                    'value': value,
                    'value_type': value_type,
                    'name': name,
                    'description': description,
                    'picture_uri': picture_uri,
                },
            )

        def add_restaurant_menu_discounts(
                self,
                item_id,
                discount_id,
                value,
                value_type='absolute',
                name='name',
                description='description',
                picture_uri='picture_uri',
        ):
            self.restaurant_menu_discounts.append(
                {
                    'id': item_id,
                    'discount_id': discount_id,
                    'value': value,
                    'value_type': value_type,
                    'name': name,
                    'description': description,
                    'picture_uri': picture_uri,
                },
            )

        def add_product_discount(
                self,
                item_id,
                discount_id,
                bundle,
                value,
                name='name',
                description='description',
                picture_uri='picture_uri',
        ):
            self.product_discount.append(
                {
                    'id': item_id,
                    'discount_id': discount_id,
                    'value': value,
                    'bundle': bundle,
                    'name': name,
                    'description': description,
                    'picture_uri': picture_uri,
                },
            )

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

    @mockserver.json_handler('/eats-discounts/v2/match-discounts')
    def _match_discounts(request):
        if context.mock_eats_tags:
            assert set(context.mock_eats_tags) == set(
                request.json['common_conditions']['conditions']['tag'],
            )
        assert (
            'shipping_types' in request.json['common_conditions']['conditions']
        )

        items_id = set()
        for item in request.json['subqueries']['subqueries']:
            items_id.add(item['id'])
        assert len(request.json['subqueries']['subqueries']) == len(items_id)
        result = {'match_results': []}
        for discount in context.menu_discount:
            result['match_results'].append(
                {
                    'hierarchy_name': 'menu_discounts',
                    'discounts': [
                        {
                            'discount_id': discount['discount_id'],
                            'discount_meta': {
                                'promo': {
                                    'name': discount['name'],
                                    'description': discount['description'],
                                    'picture_uri': discount['picture_uri'],
                                },
                            },
                            'money_value': {
                                'menu_value': {
                                    'value_type': discount['value_type'],
                                    'value': discount['value'],
                                },
                            },
                        },
                    ],
                    'subquery_results': [
                        {
                            'id': discount['id'],
                            'discount_id': discount['discount_id'],
                        },
                    ],
                },
            )
        for discount in context.restaurant_menu_discounts:
            result['match_results'].append(
                {
                    'hierarchy_name': 'menu_discounts',
                    'discounts': [
                        {
                            'discount_id': discount['discount_id'],
                            'discount_meta': {
                                'promo': {
                                    'name': discount['name'],
                                    'description': discount['description'],
                                    'picture_uri': discount['picture_uri'],
                                },
                            },
                            'money_value': {
                                'menu_value': {
                                    'value_type': discount['value_type'],
                                    'value': discount['value'],
                                },
                            },
                        },
                    ],
                    'subquery_results': [
                        {
                            'id': discount['id'],
                            'discount_id': discount['discount_id'],
                        },
                    ],
                },
            )

        for discount in context.product_discount:
            result['match_results'].append(
                {
                    'hierarchy_name': 'menu_discounts',
                    'discounts': [
                        {
                            'discount_id': discount['discount_id'],
                            'discount_meta': {
                                'promo': {
                                    'name': discount['name'],
                                    'description': discount['description'],
                                    'picture_uri': discount['picture_uri'],
                                },
                            },
                            'product_value': {
                                'bundle': discount['bundle'],
                                'discount_value': discount['value'],
                            },
                        },
                    ],
                    'subquery_results': [
                        {
                            'id': discount['id'],
                            'discount_id': discount['discount_id'],
                        },
                    ],
                },
            )
        return result

    context.mock_eats_order_stats = _eats_order_stats
    context.mock_eats_catalog_storage = _eats_catalog_storage
    context.mock_match_discounts = _match_discounts
    return context


@pytest.fixture()
def eats_rest_menu_storage(mockserver):
    class Context:
        mock_menu_handler = None
        mock_get_items_handler = None

        def __init__(self):
            self.categories = []
            self.items = []
            self.request_assertion_cb = None
            self.place_id = '1'
            self.place_slug = 'test_slug'

        def add_category(
                self,
                category: rest_menu_storage.Category,
                items: typing.List[rest_menu_storage.Item],
        ):
            self.categories.append(category)
            self.add_items(items, category.id, category.legacy_id)

        def add_items(
                self,
                items: typing.List[rest_menu_storage.Item],
                category_id,
                category_legacy_id,
        ):
            for item in items:
                if item.categories_ids is None:
                    item.categories_ids = []
                item.categories_ids.append(
                    rest_menu_storage.CategoryIds(
                        id=category_id, legacy_id=category_legacy_id,
                    ),
                )
                self.items.append(item)

        def request_assertion(self, callback):
            self.request_assertion_cb = callback
            return callback

        @property
        def times_called_menu_handler(self):
            return _menu_handler.times_called

        @property
        def times_called_get_items_handler(self):
            return _get_items_handler.times_called

    ctx = Context()

    @mockserver.json_handler('/eats-rest-menu-storage/internal/v1/menu')
    def _menu_handler(request):
        if ctx.request_assertion_cb is not None:
            ctx.request_assertion_cb(request)
        menu = rest_menu_storage.Menu(
            categories=ctx.categories, items=ctx.items,
        )
        return menu.as_dict()

    @mockserver.json_handler('/eats-rest-menu-storage/internal/v1/get-items')
    def _get_items_handler(request):
        assert request.json['shipping_types'] == ['delivery']

        items = list()
        for elem in ctx.items:
            items.append(elem.as_dict())

        response = {
            'places': [
                {
                    'place_id': ctx.place_id,
                    'place_slug': ctx.place_slug,
                    'items': items,
                },
            ],
        }
        return response

    ctx.mock_menu_handler = _menu_handler
    ctx.mock_get_items_handler = _get_items_handler

    return ctx
