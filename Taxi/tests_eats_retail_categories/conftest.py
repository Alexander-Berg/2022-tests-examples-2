# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=no-member
import dataclasses
from typing import Any
from typing import List
from typing import Optional
from typing import Set

import pytest

from eats_retail_categories_plugins import *  # noqa: F403 F401


from tests_eats_retail_categories import builders
from tests_eats_retail_categories import utils


@pytest.fixture(name='get_cursor')
def _get_cursor(pgsql):
    def get_cursor():
        return pgsql['eats_retail_categories'].cursor()

    return get_cursor


@pytest.fixture(name='pg_add_brand')
def pg_add_brand(get_cursor):
    def _pg_add_brand(
            brand_id=utils.BRAND_ID,
            slug='brand1',
            picture_scale='aspect_fit',
            is_enabled=True,
            updated_at='2020-06-15T10:00:00Z',
    ):
        cursor = get_cursor()
        cursor.execute(
            """
            INSERT INTO eats_retail_categories.brands
                (id, slug, picture_scale, is_enabled, updated_at)
            VALUES (%s, %s, %s, %s, %s);
            """,
            (brand_id, slug, picture_scale, is_enabled, updated_at),
        )

    return _pg_add_brand


@pytest.fixture(name='pg_add_place')
def _pg_add_place(get_cursor):
    def pg_add_place(
            place_id=utils.PLACE_ID,
            place_slug=utils.PLACE_SLUG,
            brand_id=utils.BRAND_ID,
            is_enabled=True,
            updated_at='2021-02-02T12:30:00+0300',
    ):
        cursor = get_cursor()
        cursor.execute(
            f"""
                INSERT INTO eats_retail_categories.places (
                    id, slug, brand_id, is_enabled, updated_at
                ) VALUES
                (%s, %s, %s, %s, %s);
                """,
            (place_id, place_slug, brand_id, is_enabled, updated_at),
        )

    return pg_add_place


@pytest.fixture(name='pg_add_user_orders_updates')
def _pg_add_user_orders_updates(get_cursor):
    def pg_add_user_orders_updates(
            eater_id=utils.EATER_ID, updated_at='2021-02-02T12:30:00+0300',
    ):
        cursor = get_cursor()
        cursor.execute(
            f"""
                INSERT INTO eats_retail_categories.user_orders_updates_log (
                    eater_id, updated_at
                ) VALUES
                (%s, %s);
                """,
            (eater_id, updated_at),
        )

    return pg_add_user_orders_updates


@pytest.fixture(name='pg_select_user_orders_updates')
def _pg_select_user_orders_updates(get_cursor):
    def pg_select_user_orders_updates(eater_id=utils.EATER_ID):
        cursor = get_cursor()
        cursor.execute(
            """
            SELECT eater_id, updated_at
            FROM eats_retail_categories.user_orders_updates_log
            WHERE eater_id = %s
            """,
            (eater_id,),
        )
        return [
            {'eater_id': eater[0], 'updated_at': eater[1]} for eater in cursor
        ]

    return pg_select_user_orders_updates


@pytest.fixture(name='pg_add_user_ordered_product')
def _pg_add_user_ordered_product(get_cursor):
    def pg_add_user_ordered_product(
            eater_id=utils.EATER_ID,
            brand_id=utils.BRAND_ID,
            public_id=utils.PUBLIC_IDS[0],
            orders_count=1,
    ):
        cursor = get_cursor()
        cursor.execute(
            f"""
                INSERT INTO eats_retail_categories.user_ordered_products (
                    eater_id, brand_id, public_id, orders_count
                ) VALUES
                (%s, %s, %s, %s);
                """,
            (eater_id, brand_id, public_id, orders_count),
        )

    return pg_add_user_ordered_product


@pytest.fixture(name='pg_select_user_brand_products')
def _pg_select_user_brand_products(get_cursor):
    def pg_select_user_brand_products(
            eater_id=utils.EATER_ID, with_updated_at=False,
    ):
        def make_selected_products(db_values, with_updated_at):
            def make_product(value, with_updated_at):
                product = {
                    'eater_id': value[0],
                    'brand_id': value[1],
                    'public_id': value[2],
                    'orders_count': value[3],
                }
                if with_updated_at:
                    product['updated_at'] = value[4]
                return product

            return [
                make_product(value, with_updated_at) for value in db_values
            ]

        cursor = get_cursor()
        cursor.execute(
            """
            SELECT eater_id, brand_id, public_id, orders_count, updated_at
            FROM eats_retail_categories.user_ordered_products
            WHERE eater_id = %s
            """,
            (eater_id,),
        )
        return utils.sort_by_public_id(
            make_selected_products(cursor, with_updated_at),
        )

    return pg_select_user_brand_products


@pytest.fixture(name='pg_add_user_crossbrand_product')
def _pg_add_user_crossbrand_product(get_cursor):
    def pg_add_user_crossbrand_product(
            eater_id=utils.EATER_ID, sku_id=utils.SKU_IDS[0], orders_count=1,
    ):
        cursor = get_cursor()
        cursor.execute(
            f"""
                INSERT INTO
                eats_retail_categories.user_cross_brand_ordered_products
                (eater_id, sku_id, orders_count) VALUES
                (%s, %s, %s);
                """,
            (eater_id, sku_id, orders_count),
        )

    return pg_add_user_crossbrand_product


@pytest.fixture(name='pg_select_crossbrand_products')
def _pg_select_crossbrand_products(get_cursor):
    def pg_select_crossbrand_products(
            eater_id=utils.EATER_ID, with_updated_at=False,
    ):
        def make_selected_products(db_values, with_updated_at):
            def make_product(value, with_updated_at):
                product = {
                    'eater_id': value[0],
                    'sku_id': value[1],
                    'orders_count': value[2],
                }
                if with_updated_at:
                    product['updated_at'] = value[3]
                return product

            return [
                make_product(value, with_updated_at) for value in db_values
            ]

        cursor = get_cursor()
        cursor.execute(
            """
            SELECT eater_id, sku_id, orders_count, updated_at
            FROM eats_retail_categories.user_cross_brand_ordered_products
            WHERE eater_id = %s
            """,
            (eater_id,),
        )
        return utils.sort_by_sku_id(
            make_selected_products(cursor, with_updated_at),
        )

    return pg_select_crossbrand_products


@dataclasses.dataclass
class ContextWithStatusAndErrors:
    # List of codes, that will be returned with each call of the handler
    status_codes: List[int] = dataclasses.field(default_factory=lambda: [200])
    network_error: bool = False
    timeout_error: bool = False
    calls_limit: int = 0
    times_called: int = 0

    def set_status(self, status_code: int):
        self.status_codes = [status_code]

    def set_statuses(self, status_codes: List[int]):
        self.status_codes = status_codes

    def get_status_code(self):
        # if handler called more times than amount of status_code, the last
        # one will be returned. otherwise corresponding to handler times_called
        # will be returned
        status_code = self.status_codes[len(self.status_codes) - 1]
        if self.times_called < len(self.status_codes):
            status_code = self.status_codes[self.times_called]
        self.times_called += 1
        return status_code

    def set_network_error(self, network_error: bool, calls_limit: int = 0):
        self.network_error = network_error
        self.calls_limit = calls_limit

    def set_timeout_error(self, timeout_error: bool, calls_limit: int = 0):
        self.timeout_error = timeout_error
        self.calls_limit = calls_limit

    def process_errors(self, mockserver):
        if self.network_error and self.calls_limit == 0:
            raise mockserver.NetworkError()

        if self.timeout_error and self.calls_limit == 0:
            raise mockserver.TimeoutError()

        if self.calls_limit != 0:
            self.calls_limit -= 1


@dataclasses.dataclass
class OrdershistoryProduct:
    origin_id: str
    core_id: int
    place_id: int
    quantity: int


@dataclasses.dataclass
class OrderhistoryContext(ContextWithStatusAndErrors):
    products: List[OrdershistoryProduct] = dataclasses.field(
        default_factory=list,
    )
    handler: Any = None

    def add_product(
            self, origin_id, core_id=1, place_id=utils.PLACE_ID, quantity=1,
    ):
        self.products.append(
            OrdershistoryProduct(origin_id, core_id, place_id, quantity),
        )


@pytest.fixture(name='mock_ordershistory_context')
def _mock_ordershistory_context(mockserver):

    context = OrderhistoryContext()

    def mock_orders(context, request):
        status_code = context.get_status_code()
        if status_code != 200:
            return mockserver.make_response(status=status_code)

        orders = []

        for product in context.products:
            cart = {
                'name': 'Товар 1',
                'place_menu_item_id': product.core_id,
                'origin_id': product.origin_id,
                'product_id': 'product-id-1',
                'quantity': product.quantity,
            }
            order = {
                'cart': [cart],
                'created_at': '2020-01-28T12:00:00+03:00',
                'delivery_location': {'lat': 32.07, 'lon': 34.77},
                'is_asap': True,
                'order_id': 'oid-1',
                'place_id': product.place_id,
                'source': 'eda',
                'status': 'delivered',
                'total_amount': '2222',
            }
            orders.append(order)

        return {'orders': orders}

    @mockserver.json_handler(utils.Handlers.ORDERSHISTORY_ORDERS)
    def _mock_orders(request):
        return mock_orders(context, request)

    context.handler = _mock_orders

    return context


@dataclasses.dataclass
class ProductMapping:
    origin_id: str
    public_id: Optional[str]
    place_id: int


@dataclasses.dataclass
class ProductsPublicIdByOriginIdContext(ContextWithStatusAndErrors):
    products: List[ProductMapping] = dataclasses.field(default_factory=list)
    handler: Any = None

    def add_product(self, origin_id, public_id=None, place_id=utils.PLACE_ID):
        self.products.append(ProductMapping(origin_id, public_id, place_id))


@pytest.fixture(name='mock_public_id_by_origin_id_context')
def _mock_public_id_by_origin_id_context(mockserver):

    context = ProductsPublicIdByOriginIdContext()

    def make_response(context, request):
        status_code = context.get_status_code()
        if status_code != 200:
            return mockserver.make_response(
                json={'code': 'place_not_found', 'message': 'bad response'},
                status=status_code,
            )
        mapping = []

        for product in context.products:
            if product.place_id == request.json['place_id']:
                mapping.append(
                    {
                        'origin_id': product.origin_id,
                        'public_id': product.public_id,
                    },
                )

        return {'products_ids': mapping}

    @mockserver.json_handler(utils.Handlers.PRODUCTS_PUBLIC_BY_ORIGIN_ID)
    def _mock_mapping(request):
        return make_response(context, request)

    context.handler = _mock_mapping

    return context


@dataclasses.dataclass
class SkuToPublicId:
    sku_id: str
    public_id: Optional[str]
    place_id: int


@dataclasses.dataclass
class NomenclaturePublicIdBySkuIdContext(ContextWithStatusAndErrors):
    products: List[SkuToPublicId] = dataclasses.field(default_factory=list)
    handler: Any = None

    def add_product(
            self,
            sku_id=utils.SKU_IDS[0],
            public_id=None,
            place_id=utils.PLACE_ID,
    ):
        # self.products[place_id] = PublicAndSkuId(sku_id, public_id)
        self.products.append(SkuToPublicId(sku_id, public_id, place_id))


@pytest.fixture(name='mock_public_id_by_sku_id_context')
def _mock_public_id_by_sku_id_context(mockserver):

    context = NomenclaturePublicIdBySkuIdContext()

    def make_response(context, request):
        status_code = context.get_status_code()
        if status_code != 200:
            return mockserver.make_response(
                json={'status': status_code, 'message': 'bad response'},
                status=status_code,
            )
        place_id = int(request.query['place_id'])
        products = []
        for product in context.products:
            if place_id != product.place_id:
                continue
            public_ids = (
                [] if product.public_id is None else [product.public_id]
            )
            products.append({'sku_id': product.sku_id, 'ids': public_ids})

        return {'products': products}

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PUBLIC_ID_BY_SKU_ID)
    def _mock_mapping(request):
        return make_response(context, request)

    context.handler = _mock_mapping

    return context


@dataclasses.dataclass
class NomenclatureV1ProductsInfoProduct:
    public_id: str
    name: Optional[str] = None
    shipping_type: Optional[str] = None
    sku_id: Optional[str] = None

    def build(self):
        return builders.product_static_info(
            self.public_id, self.name, self.shipping_type, self.sku_id,
        )


@dataclasses.dataclass
class NomenclatureV1ProductsInfoContext(ContextWithStatusAndErrors):
    products: List[NomenclatureV1ProductsInfoProduct] = dataclasses.field(
        default_factory=list,
    )
    handler: Any = None
    status_code: int = 200
    request_ids: Optional[Set[str]] = None

    def add_product(
            self,
            public_id,
            name='Масло сливочное',
            shipping_type='delivery',
            sku_id=None,
    ):
        self.products.append(
            NomenclatureV1ProductsInfoProduct(
                public_id, name, shipping_type, sku_id,
            ),
        )


@pytest.fixture(name='mock_nomenclature_static_info_context')
def _mock_nomenclature_v1_products_info_context(mockserver):

    context = NomenclatureV1ProductsInfoContext()

    def mock_products_static_info(context, request):
        if context.request_ids is not None:
            assert set(request.json['product_ids']) == context.request_ids
        status_code = context.get_status_code()
        if status_code != 200:
            return mockserver.make_response(status=status_code)
        products = [
            product.build()
            for product in context.products
            if product.public_id in request.json['product_ids']
        ]
        return {'products': products}

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PRODUCTS_INFO)
    def _mock_nomenclature_v1_products_info_context(request):
        assert 'use_sku' not in request.query
        return mock_products_static_info(context, request)

    context.handler = _mock_nomenclature_v1_products_info_context

    return context
