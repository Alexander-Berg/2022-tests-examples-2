import collections
import enum

import pytest


class UpsaleRequestSource(enum.Enum):
    cart_page = 'cart-page'
    cart_page_v2 = 'cart-page-v2'
    item_page = 'item-page'
    menu_page = 'menu-page'
    tableware = 'tableware'


@pytest.fixture(name='empty_upsale')
def mock_upsale(mockserver):
    @mockserver.json_handler('/grocery-upsale/internal/upsale/v1/match')
    def mock_upsale_match(data):
        return {'items': []}

    class Context:
        @property
        def times_called(self):
            return mock_upsale_match.times_called

    context = Context()
    return context


@pytest.fixture(name='grocery_upsale', autouse=True)
def mock_grocery_upsale(mockserver):
    class Context:
        def __init__(self):
            self._upsale_ids = []
            self._upsale_ids_by_source = collections.defaultdict(list)
            self._product_ids = None
            self._cart_items = None
            self._request_source = None
            self._throw_error = False
            self._throw_error_on_source = {}
            self._substitutions = []

        def add_product(self, product_id: str):
            self._upsale_ids.append(product_id)

        def add_product_with_source(
                self, product_id: str, request_source: UpsaleRequestSource,
        ):
            self._upsale_ids_by_source[request_source.value].append(product_id)

        def add_products(self, products: list):
            self._upsale_ids.extend(products)

        def add_product_substitutions(self, products: list):
            self._substitutions.extend(products)

        def set_request_check(
                self,
                *,
                product_ids=None,
                cart_items=None,
                request_source=None,
        ):
            self._product_ids = product_ids
            self._cart_items = cart_items
            if request_source == UpsaleRequestSource.cart_page:
                self._request_source = {
                    UpsaleRequestSource.cart_page.value,
                    UpsaleRequestSource.cart_page_v2.value,
                    UpsaleRequestSource.tableware.value,
                }
            else:
                self._request_source = {request_source.value}

        def set_response_type(self, *, is_error=None, error_on_source=None):
            self._throw_error = is_error
            self._throw_error_on_source = (
                {item.value for item in error_on_source}
                if error_on_source
                else {}
            )

        @property
        def upsale_ids(self):
            return self._upsale_ids

        @property
        def upsale_ids_by_source(self):
            return self._upsale_ids_by_source

        @property
        def substitutions(self):
            return self._substitutions

        @property
        def request_ids(self):
            return self._product_ids

        @property
        def request_cart(self):
            return self._cart_items

        @property
        def request_source(self):
            return self._request_source

        @property
        def throw_error(self):
            return self._throw_error

        @property
        def throw_error_on_source(self):
            return self._throw_error_on_source

        @property
        def times_called(self):
            return upsale_handler.times_called

        @property
        def umlaas_called(self):
            return umlaas_handler.times_called

    context = Context()

    @mockserver.json_handler('/grocery-upsale/internal/upsale/v1/match')
    def upsale_handler(request):
        if context.request_ids is not None:
            assert request.json['context']['items'] == [
                {'product_id': item_id} for item_id in context.request_ids
            ]
        if context.request_cart is not None:
            assert request.json['context']['cart'] == [
                {'product_id': cart_item_id, 'quantity': 1}
                for cart_item_id in context.request_cart
            ]
        if context.request_source is not None:
            assert request.args['request_source'] in context.request_source
        return {
            'items': [
                {'product_id': upsale_id} for upsale_id in context.upsale_ids
            ],
        }

    def _assert_request(request):
        if context.request_ids is not None:
            assert request.json['context']['items'] == [
                {'product_id': item_id} for item_id in context.request_ids
            ]
        if context.request_cart is not None:
            assert request.json['context']['cart'] == [
                {'product_id': cart_item_id, 'quantity': 1}
                for cart_item_id in context.request_cart
            ]
        if context.request_source is not None:
            assert request.args['request_source'] in context.request_source
        assert request.args['suggest_type'] in [
            'complement-items',
            'substitute-items',
        ]
        assert request.args['service_name'] in ['grocery-api', 'grocery-cart']

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/grocery-suggest')
    def umlaas_handler(request):
        _assert_request(request)
        if context.throw_error:
            return mockserver.make_response('Error 500', status=500)
        if request.args['request_source'] in context.throw_error_on_source:
            return mockserver.make_response('Error 500', status=500)

        upsale_ids = context.upsale_ids
        if request.args['suggest_type'] == 'substitute-items':
            upsale_ids = context.substitutions

        return {
            'exp_list': [],
            'request_id': request.args['request_id'],
            'items': [
                {'product_id': upsale_id}
                for upsale_id in upsale_ids
                + context.upsale_ids_by_source[request.args['request_source']]
            ],
        }

    return context
