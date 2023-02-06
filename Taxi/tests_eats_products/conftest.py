# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=too-many-lines
import dataclasses
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Set

import pytest

from eats_products_plugins import *  # noqa: F403 F401

from tests_eats_products import eats_upsell_recommendations
from tests_eats_products import utils
from tests_eats_products.helpers import request_checker


# pylint: disable=too-many-lines


@pytest.fixture(name='mock_eats_tags', autouse=True)
def _mock_eats_tagse(mockserver):
    @mockserver.json_handler('/eats-tags/v2/match_single')
    def eats_tags(json_request):
        assert json_request.json.get('match', [])
        assert [
            item.get('type') in ['user_id', 'personal_phone_id']
            for item in json_request.json['match']
        ]
        return mockserver.make_response(
            status=200, json={'tags': ['tag1', '2tag', '3tag3', '1234']},
        )

    return eats_tags


@pytest.fixture(name='eats_order_stats', autouse=True)
def eats_order_stats(mockserver, request):
    @mockserver.json_handler(
        '/eats-order-stats/internal/eats-order-stats/v1/orders',
    )
    def _mock_eats_order_stats(json_request):
        identity = json_request.json['identities'][0]
        counters = [
            {
                'first_order_at': '2021-05-28T10:12:00+0000',
                'last_order_at': '2021-05-29T11:33:00+0000',
                'properties': [
                    {'name': 'brand_id', 'value': '1'},
                    {'name': 'place_id', 'value': '1'},
                    {'name': 'business_type', 'value': 'shop'},
                ],
                'value': 5,
            },
        ]
        return {'data': [{'counters': counters, 'identity': identity}]}

    return _mock_eats_order_stats


@pytest.fixture(name='cache_add_discount_product')
def cache_add_discount_product(pgsql):
    def _sql_add_discount_product(origin_id, place_id=1):
        cursor = pgsql['eats_products'].cursor()
        cursor.execute(
            f"""
            INSERT INTO eats_products.discount_product (
                place_id, nomenclature_id, updated_at
            ) VALUES
            (%s, %s, '2020-06-15T11:00:00Z');
            """,
            (place_id, origin_id),
        )

    return _sql_add_discount_product


@pytest.fixture(name='sql_add_brand')
def sql_add_brand(pgsql):
    def _sql_add_brand(
            brand_id=utils.BRAND_ID,
            brand_slug=utils.BRAND_SLUG,
            is_enabled=True,
    ):
        cursor = pgsql['eats_products'].cursor()
        cursor.execute(
            f"""
                INSERT INTO eats_products.brand (
                    brand_id, slug, picture_scale, is_enabled
                ) VALUES
                (%s, %s, 'aspect_fit', %s);
                """,
            (brand_id, brand_slug, is_enabled),
        )

    return _sql_add_brand


@pytest.fixture(name='sql_add_place')
def sql_add_place(pgsql):
    def _sql_add_place(
            place_id=utils.PLACE_ID,
            place_slug=utils.PLACE_SLUG,
            brand_id=utils.BRAND_ID,
            is_enabled=True,
            currency_code=None,
            currency_sign=None,
    ):
        cursor = pgsql['eats_products'].cursor()
        cursor.execute(
            f"""
                INSERT INTO eats_products.place (
                    place_id,
                    slug,
                    brand_id,
                    is_enabled,
                    currency_code,
                    currency_sign
                ) VALUES
                (%s, %s, %s, %s, %s, %s);
                """,
            (
                place_id,
                place_slug,
                brand_id,
                is_enabled,
                currency_code,
                currency_sign,
            ),
        )

    return _sql_add_place


@pytest.fixture(name='sql_set_place_currency')
def sql_set_place_currency(pgsql):
    def _sql_set_place_currency(place_id=utils.PLACE_ID, code='RUB', sign='₽'):
        cursor = pgsql['eats_products'].cursor()
        cursor.execute(
            f"""
                UPDATE eats_products.place SET
                    currency_code = %s,
                    currency_sign = %s
                WHERE place_id = %s;
                """,
            (code, sign, place_id),
        )

    return _sql_set_place_currency


@dataclasses.dataclass
class ProductMapping:
    origin_id: str
    core_id: Optional[int] = None
    public_id: Optional[str] = None


@pytest.fixture(name='add_place_products_mapping')
def _add_place_products_mapping(pgsql):
    def add_mapping(
            mapping: List[ProductMapping],
            place_id=utils.PLACE_ID,
            brand_id=utils.BRAND_ID,
    ):
        cursor = pgsql['eats_products'].cursor()
        for row in mapping:
            cursor.execute(
                f"""
                INSERT INTO eats_products.place_products (
                    origin_id, core_id, public_id, place_id,
                    brand_id, updated_at
                ) VALUES
                (%s, %s, %s, %s, %s, '2020-06-15T11:00:00Z');
                """,
                (
                    row.origin_id,
                    row.core_id,
                    row.public_id,
                    place_id,
                    brand_id,
                ),
            )

    return add_mapping


@pytest.fixture(name='make_public_by_sku_id_response')
def _make_public_by_sku_id_response():
    def make_public_by_sku_id_response(request, place_sku_to_public_ids):
        products = []
        sku_to_public_ids = place_sku_to_public_ids[request.query['place_id']]
        for sku_id, public_ids in sku_to_public_ids.items():
            if sku_id in request.json['sku_ids']:
                products.append({'sku_id': sku_id, 'ids': public_ids})
        return {'products': products}

    return make_public_by_sku_id_response


@pytest.fixture(name='add_default_product_mapping')
def add_default_product_mapping(pgsql, add_place_products_mapping):
    def _insert_mapping(place_id=utils.PLACE_ID, start_id=1, end_id=9):
        mapping = []
        for i in range(start_id, end_id + 1):
            origin_id = f'item_id_{i}'
            public_id = f'bb231b95-1ff2-4bc4-b78d-dcaa1f69b00{i}'
            mapping.append(ProductMapping(origin_id, i, public_id))
        add_place_products_mapping(mapping, place_id)

    return _insert_mapping


@pytest.fixture(name='nomenclature_categories_mock')
def nomenclature_categories_mock(mockserver):
    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PRODUCT_CATEGORIES)
    def _mock_eats_nomenclature_categories(request):
        return {'categories': [], 'products': []}

    return _mock_eats_nomenclature_categories


class V1NomenclatureContext:
    def __init__(self):
        self.response = {}
        self.status = 200

    def set_response(self, response, status=200):
        self.response = response
        self.status = status

    def set_error(self, status=500):
        self.response = dict(code=str(status), message='error')
        self.status = status


@pytest.fixture(name='mock_v1_nomenclature', autouse=True)
def mock_v1_nomenclature(mockserver):
    context = V1NomenclatureContext()

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE)
    def _mock_eats_nomenclature(request):
        return mockserver.make_response(
            json=context.response, status=context.status,
        )

    return context


@pytest.fixture(name='mock_nomenclature_v2_details')
def _mock_nomenclature_v2_details(mockserver, load_json):
    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_ASSORTMENT)
    def _mock_eats_nomenclature_v2_details(request):
        return load_json('v2_place_assortment_details_response.json')

    return _mock_eats_nomenclature_v2_details


@dataclasses.dataclass
class CashbackProduct:
    id_: str
    cashback_value: Optional[dict] = None


@dataclasses.dataclass
class CatalogOverrides:
    logo: Optional[dict] = dataclasses.field(default_factory=dict)
    color: Optional[dict] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class CatalogPlace:
    place_id: str
    place_slug: str
    brand_id: str
    brand_slug: str
    brand_name: str
    overrides: CatalogOverrides

    def build(self):
        return {
            'id': self.place_id,
            'slug': self.place_slug,
            'brand': {
                'id': self.brand_id,
                'slug': self.brand_slug,
                'business': 'shop',
                'name': self.brand_name,
                'logo': self.overrides.logo,
                'color': self.overrides.color,
            },
        }


@dataclasses.dataclass
class DiscountProduct:
    id_: str
    money_value: Optional[dict] = None
    product_value: Optional[dict] = None
    discount_meta: Optional[dict] = None


# pylint: disable=no-member
@dataclasses.dataclass
class MatchDiscountContext:
    cashback_products: List[CashbackProduct] = dataclasses.field(
        default_factory=list,
    )
    discount_products: List[DiscountProduct] = dataclasses.field(
        default_factory=list,
    )
    handler: Any = None
    match_experiments: List[str] = dataclasses.field(default_factory=list)
    use_tags: bool = False

    DEFAULT_DISCOUNT_META = {
        'promo': {
            'name': 'Название акции',
            'description': 'Описание',
            'picture_uri': 'some_uri',
        },
    }

    def add_discount_product(
            self,
            id_,
            value_type=None,
            value=None,
            discount_meta=None,
            promo_product=False,
    ):
        discount_meta = discount_meta or self.DEFAULT_DISCOUNT_META
        self.discount_products.append(
            DiscountProduct(
                id_,
                {'value_type': value_type, 'value': str(value)}
                if not promo_product
                else None,
                {'discount_value': '100.0', 'bundle': 2}
                if promo_product
                else None,
                discount_meta,
            ),
        )

    def add_cashback_product(self, id_, value_type, value):
        self.cashback_products.append(
            CashbackProduct(
                id_, {'value_type': value_type, 'value': str(value)},
            ),
        )

    def add_match_experiments(self, exp):
        self.match_experiments.append(exp)

    def set_use_tags(self, use: bool):
        self.use_tags = use


@pytest.fixture(name='mock_v2_match_discounts_context')
def _mock_v2_match_discounts_context(mockserver):
    context = MatchDiscountContext()

    def mock_match_discounts(context, request):
        if context.match_experiments:
            assert set(context.match_experiments) == set(
                request.json['common_conditions']['conditions']['experiment'],
            )
        if context.use_tags:
            assert request.json['common_conditions']['conditions']['tag']

        assert request.json['common_conditions']['conditions']['country']

        discount_id = 0

        discounts_resp = {
            'hierarchy_name': 'menu_discounts',
            'discounts': [],
            'subquery_results': ([]),
        }
        for product in context.discount_products:
            discount_id += 1

            discount = {
                'discount_id': str(discount_id),
                'discount_meta': product.discount_meta,
            }

            if product.money_value is not None:
                discount['money_value'] = {'menu_value': product.money_value}
            elif product.product_value is not None:
                discount['product_value'] = product.product_value

            discounts_resp['discounts'].append(discount)
            discounts_resp['subquery_results'].append(
                {'id': product.id_, 'discount_id': str(discount_id)},
            )

        cashback_resp = {
            'hierarchy_name': 'place_menu_cashback',
            'discounts': [],
            'subquery_results': ([]),
        }
        for product in context.cashback_products:
            discount_id += 1
            cashback_resp['discounts'].append(
                {
                    'discount_id': str(discount_id),
                    'discount_meta': {'name': 'some name'},
                    'cashback_value': {'menu_value': product.cashback_value},
                },
            )
            cashback_resp['subquery_results'].append(
                {'id': product.id_, 'discount_id': str(discount_id)},
            )
        resp = {'match_results': []}
        if context.discount_products:
            resp['match_results'].append(discounts_resp)
        if context.cashback_products:
            resp['match_results'].append(cashback_resp)

        return resp

    @mockserver.json_handler(utils.Handlers.MATCH_DISCOUNTS)
    def _mock_match_discounts(request):
        return mock_match_discounts(context, request)

    context.handler = _mock_match_discounts

    return context


@pytest.fixture(name='mock_eats_catalog_storage', autouse=True)
def _mock_eats_catalog_storage(mockserver):
    @mockserver.json_handler(
        '/eats-catalog-storage/internal/eats-catalog-storage'
        '/v1/places/retrieve-by-ids',
    )
    def _mock_retrieve_by_ids(request):
        return utils.DEFAULT_EATS_CATALOG_RESPONSE

    return _mock_retrieve_by_ids


@dataclasses.dataclass
class OrdershistoryProduct:
    place_id: int
    core_id: int
    quantity: int


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
class NomenclatureProduct:
    public_id: str
    price: int
    promo_price: Optional[int] = None
    nom_id: Optional[str] = None
    is_available: bool = True
    description: Optional[str] = None
    is_catch_weight: Optional[bool] = True
    measure: Optional[dict] = None
    in_stock: Optional[int] = None
    shipping_type: Optional[str] = None
    name: Optional[str] = None

    DEFAULT_MEASURE = {'unit': 'KGRM', 'value': 1}

    def build(self, use_v2=True):
        price = self.price
        old_price = None
        if self.promo_price:
            price = self.promo_price
            old_price = self.price
        measure = (
            self.measure or self.DEFAULT_MEASURE
            if self.is_catch_weight
            else None
        )
        if use_v2:
            return utils.build_nomenclature_product(
                self.public_id,
                self.description or 'ghi',
                price,
                old_price,
                self.is_available,
                self.is_catch_weight,
                measure,
                self.in_stock,
                self.shipping_type or 'delivery',
                self.name or 'item_4',
            )
        return utils.build_v1_nomenclature_product(
            self.public_id,
            price,
            old_price,
            self.nom_id,
            self.is_available,
            self.is_catch_weight,
            measure,
            self.name or 'Яблоки',
            self.description or 'Описание Яблоки',
            self.in_stock,
        )


@dataclasses.dataclass
class NomenclatureProductBySkuId:
    place_id: int
    product_id: str
    price: str
    old_price: Optional[str] = None

    def build(self):
        result = {
            'place_id': self.place_id,
            'product_id': self.product_id,
            'price': self.price,
            'old_price': self.old_price,
        }
        return result


@dataclasses.dataclass
class NomenclatureV1ProductsInfoProduct:
    id_: str
    carbohydrates: Optional[str] = None
    proteins: Optional[str] = None
    fats: Optional[str] = None
    calories_value: Optional[str] = None
    calories_unit: Optional[str] = None
    description_general: Optional[str] = None
    is_catch_weight: Optional[bool] = True
    measure: Optional[dict] = None
    sku_id: Optional[str] = None
    name: Optional[str] = None
    images: Any = None
    shipping_type: Optional[str] = None
    expiration_info_value: Optional[str] = None
    expiration_info_unit: Optional[str] = None
    composition: Optional[str] = None
    storage_requirements: Optional[str] = None
    vendor_name: Optional[str] = None
    vendor_country: Optional[str] = None
    is_alcohol: Optional[bool] = None
    brand: Optional[str] = None
    alco_grape_cultivar: Optional[str] = None
    alco_flavour: Optional[str] = None
    alco_aroma: Optional[str] = None
    alco_pairing: Optional[str] = None

    DEFAULT_MEASURE = {'unit': 'GRM', 'value': 180}

    def build(self):
        measure = (
            self.measure or self.DEFAULT_MEASURE
            if self.is_catch_weight
            else None
        )
        return utils.build_v1_products_static_info(
            self.id_,
            self.carbohydrates,
            self.proteins,
            self.fats,
            self.calories_value,
            self.calories_unit,
            self.description_general,
            self.is_catch_weight,
            measure,
            self.sku_id,
            self.name,
            self.images,
            self.shipping_type,
            self.expiration_info_value,
            self.expiration_info_unit,
            self.composition,
            self.storage_requirements,
            self.vendor_name,
            self.vendor_country,
            is_alcohol=self.is_alcohol,
            brand=self.brand,
            alco_grape_cultivar=self.alco_grape_cultivar,
            alco_flavour=self.alco_flavour,
            alco_aroma=self.alco_aroma,
            alco_pairing=self.alco_pairing,
        )


@dataclasses.dataclass
class NomenclatureV1PlaceProductsInfoProduct:
    id_: str
    price: str
    is_available: bool
    parent_category_ids: List[str]
    old_price: Optional[str] = None
    origin_id: Optional[str] = None
    in_stock: Optional[int] = None

    def build(self):
        return utils.build_v1_products_dynamic_info(
            self.id_,
            self.price,
            self.is_available,
            self.old_price,
            self.origin_id,
            self.parent_category_ids,
            self.in_stock,
        )


@dataclasses.dataclass
class NomenclatureFilteredProduct:
    public_id: str
    name: str
    price: str = '100.00'
    is_catch_weight: bool = False
    adult: bool = False
    sort_order: int = 0
    images: List[dict] = dataclasses.field(default_factory=list)
    description: Dict[str, str] = dataclasses.field(default_factory=dict)
    shipping_type: str = 'delivery'
    in_stock: Optional[int] = None
    old_price: Optional[str] = None
    measure: Optional[dict] = None

    def build(self):
        return utils.build_filtered_product(
            self.public_id,
            self.name,
            self.price,
            self.is_catch_weight,
            self.adult,
            self.sort_order,
            self.images,
            self.description,
            self.shipping_type,
            self.in_stock,
            self.old_price,
            self.measure,
        )


@dataclasses.dataclass
class NomenclatureCategoryFilterValue:
    value: str
    items_count: int
    sort_order: int = 0

    def build(self):
        return {
            'value': self.value,
            'items_count': self.items_count,
            'sort_order': self.sort_order,
        }


@dataclasses.dataclass
class NomenclatureCategoryFilter:
    id_: str
    name: str
    type: str
    sort_order: int = 0
    image: Optional[str] = None
    values: Optional[list] = None

    def build(self):
        result = {
            'id': self.id_,
            'name': self.name,
            'type': self.type,
            'sort_order': self.sort_order,
        }

        if self.image is not None:
            result['image'] = {'url': self.image}

        if self.values is not None:
            # pylint: disable=not-an-iterable
            result['values'] = [value.build() for value in self.values]

        return result


@dataclasses.dataclass
class NomenclatureFilteredCategory:
    public_id: str
    name: str
    origin_id: str
    type: str = 'custom_base'
    sort_order: int = 0
    parent_public_id: Optional[str] = None
    products: List[NomenclatureFilteredProduct] = dataclasses.field(
        default_factory=list,
    )
    images: List[dict] = dataclasses.field(default_factory=list)
    child_ids: List[str] = dataclasses.field(default_factory=list)
    filters: List[dict] = dataclasses.field(default_factory=list)
    tags: Optional[List[str]] = None

    def add_product(self, *args, **kwargs):
        """
        Позволяем добавлять товар как через передачу объекта
        NomenclatureProduct, так и через кварги
        """
        args_len = len(args)
        if args_len > 0 and isinstance(args[0], NomenclatureFilteredProduct):
            product = args[0]
        else:
            product = NomenclatureFilteredProduct(**kwargs)
        self.products.append(product)


@dataclasses.dataclass
class NomenclatureProductContext:
    products: List[NomenclatureProduct] = dataclasses.field(
        default_factory=list,
    )
    handler: Any = None
    status_code: int = 200

    def add_product(
            self,
            id_,
            price=100,
            promo_price=None,
            description=None,
            is_catch_weight=True,
            measure=None,
            is_available=True,
            in_stock=None,
            shipping_type=None,
    ):
        self.products.append(
            NomenclatureProduct(
                id_,
                price,
                promo_price,
                description=description,
                is_catch_weight=is_catch_weight,
                measure=measure,
                is_available=is_available,
                in_stock=in_stock,
                shipping_type=shipping_type,
            ),
        )

    def set_status(self, status_code):
        self.status_code = status_code


@dataclasses.dataclass
class NomenclatureProductBySkuIdContext(ContextWithStatusAndErrors):
    products: List[NomenclatureProductBySkuId] = dataclasses.field(
        default_factory=list,
    )
    handler: Any = None
    expected_request: Optional[dict] = None
    stored_requests: List[dict] = dataclasses.field(default_factory=list)

    def add_product(self, place_id, product_id, price='100', old_price=None):
        self.products.append(
            NomenclatureProductBySkuId(
                place_id=place_id,
                product_id=product_id,
                price=price,
                old_price=old_price,
            ),
        )


@dataclasses.dataclass
class CatalogPlacesContext(ContextWithStatusAndErrors):
    places: List[CatalogPlace] = dataclasses.field(default_factory=list)
    handler: Any = None
    expected_request: Any = None
    block_name: Optional[str] = 'kShopPlacesBlockId'
    logo = {
        'light': [
            {'size': 'large', 'logo_url': 'logo_url'},
            {'size': 'small', 'logo_url': 'logo_url'},
        ],
        'dark': [
            {'size': 'large', 'logo_url': 'logo_url'},
            {'size': 'small', 'logo_url': 'logo_url'},
        ],
    }
    color = {'light': '#111111', 'dark': '#ffffff'}

    def add_place(
            self,
            place_id='1',
            place_slug='slug',
            brand_id='1',
            brand_slug='brand1',
            brand_name='test_brand_name',
    ):
        self.places.append(
            CatalogPlace(
                place_id=place_id,
                place_slug=place_slug,
                brand_id=brand_id,
                brand_slug=brand_slug,
                brand_name=brand_name,
                overrides=CatalogOverrides(logo=self.logo, color=self.color),
            ),
        )

    def build_places(self):
        if self.block_name is None:
            return {'blocks': []}
        return {
            'blocks': [
                {
                    'id': self.block_name,
                    # pylint: disable=not-an-iterable
                    'list': [place.build() for place in self.places],
                    'stats': {'places_count': len(self.places)},
                },
            ],
        }


@dataclasses.dataclass
class GeneralizedStaticInfo:
    id_: str = ''
    name: str = ''
    sku_id: Optional[str] = None


@dataclasses.dataclass
class GeneralizedDynamicInfo:
    price: str = ''
    parent_category_ids: List[str] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class NomenclatureV1ProductsInfoContext(ContextWithStatusAndErrors):
    products: List[NomenclatureV1ProductsInfoProduct] = dataclasses.field(
        default_factory=list,
    )
    handler: Any = None
    request_ids: Optional[Set[str]] = None

    def add_product(
            self,
            id_,
            carbohydrates=None,
            proteins=None,
            fats=None,
            calories_value=None,
            calories_unit=None,
            description_general=None,
            is_catch_weight=True,
            measure=None,
            sku_id=None,
            name=None,
            images=None,
            shipping_type='all',
            expiration_info_value=None,
            expiration_info_unit=None,
            composition=None,
            storage_requirements=None,
            vendor_name=None,
            vendor_country=None,
            is_alcohol=False,
            brand=None,
            alco_grape_cultivar=None,
            alco_flavour=None,
            alco_aroma=None,
            alco_pairing=None,
    ):
        self.products.append(
            NomenclatureV1ProductsInfoProduct(
                id_,
                carbohydrates,
                proteins,
                fats,
                calories_value,
                calories_unit,
                description_general,
                is_catch_weight,
                measure,
                sku_id,
                name,
                images,
                shipping_type,
                expiration_info_value,
                expiration_info_unit,
                composition,
                storage_requirements,
                vendor_name,
                vendor_country,
                is_alcohol,
                brand,
                alco_grape_cultivar,
                alco_flavour,
                alco_aroma,
                alco_pairing,
            ),
        )


@dataclasses.dataclass
class GeneralizedProductContext(ContextWithStatusAndErrors):
    static_data: Optional[GeneralizedStaticInfo] = None
    dynamic_data: Optional[GeneralizedDynamicInfo] = None
    handler: Any = None

    def set_generalized_info(
            self, id_, name, price, parent_category_ids, sku_id=None,
    ):
        self.static_data = GeneralizedStaticInfo(id_, name, sku_id)
        self.dynamic_data = GeneralizedDynamicInfo(price, parent_category_ids)


@dataclasses.dataclass
class NomenclatureV1PlaceProductsInfoContext(ContextWithStatusAndErrors):
    products: List[NomenclatureV1PlaceProductsInfoProduct] = dataclasses.field(
        default_factory=list,
    )
    handler: Any = None
    expected_request: Any = None

    def add_product(
            self,
            id_,
            price=10,
            is_available=True,
            old_price=None,
            origin_id='origin_id_101',
            parent_category_ids=None,
            in_stock=None,
    ):
        if parent_category_ids is None:
            parent_category_ids = ['1']

        self.products.append(
            NomenclatureV1PlaceProductsInfoProduct(
                id_,
                price,
                is_available,
                parent_category_ids,
                old_price,
                origin_id,
                in_stock,
            ),
        )


@dataclasses.dataclass
class NomenclatureCategoriesFilteredContext(ContextWithStatusAndErrors):
    categories: List[NomenclatureFilteredCategory] = dataclasses.field(
        default_factory=list,
    )
    handler: Any = None
    expected_request: Any = None

    def add_category(self, category: NomenclatureFilteredCategory):
        self.categories.append(category)

    def make_expected_response(self, shipping_type='delivery'):
        goods_count = 0

        def rounded(string):
            return int(float(string))

        def build_product(product):
            result = {
                'id': int(product.public_id[-1]),
                'public_id': product.public_id,
                'name': product.name,
                'description': (
                    product.description['general']
                    if 'general' in product.description
                    else ''
                ),
                'available': True,
                'inStock': product.in_stock,
                'price': (
                    rounded(product.price)
                    if product.old_price is None
                    else rounded(product.old_price)
                ),
                'decimalPrice': (
                    product.price
                    if product.old_price is None
                    else product.old_price
                ),
                'promoPrice': (
                    None
                    if product.old_price is None
                    else rounded(product.price)
                ),
                'decimalPromoPrice': (
                    None if product.old_price is None else product.price
                ),
                'promoTypes': [],
                'shippingType': product.shipping_type,
                'sortOrder': product.sort_order,
                'optionGroups': [],
                'picture': (
                    None
                    if not product.images
                    else {
                        'scale': 'aspect_fit',
                        'url': (
                            product.images[len(product.images) - 1]['url']
                            + '/{w}x{h}'
                        ),
                    }
                ),
                'adult': product.adult,
            }

            if product.measure is not None:
                value = product.measure['value']
                result['weight'] = f'{value} кг'

            nonlocal goods_count
            goods_count += 1

            return result

        def build_category(category):
            result = {
                'id': int(category.public_id),
                'uid': category.public_id,
                'parentId': (
                    None
                    if category.parent_public_id is None
                    else int(category.parent_public_id)
                ),
                'schedule': None,
                'available': True,
                'gallery': [
                    {'type': 'tile', 'url': image['url'] + '/{w}x{h}'}
                    for image in category.images[-1:]
                ],
                'show_in': ['categories_carousel'],
                'name': category.name,
                'items': [
                    build_product(product)
                    for product in category.products
                    if product.shipping_type in ('all', shipping_type)
                ],
            }
            if category.parent_public_id is not None:
                result['parent_uid'] = category.parent_public_id
            return result

        categories = sorted(self.categories, key=lambda item: item.sort_order)
        for category in categories:
            category.images.sort(key=lambda item: item['sort_order'])
            category.products.sort(key=lambda item: item.sort_order)
            for product in category.products:
                product.images.sort(key=lambda item: item['sort_order'])

        categories_result = [
            build_category(category) for category in categories
        ]

        return {
            'meta': None,
            'payload': {
                'categories': categories_result,
                'goods_count': goods_count,
            },
        }


@dataclasses.dataclass
class NomenclatureCategory:
    id_: str
    name: str
    public_id: int
    parent_id: Optional[str] = None
    parent_public_id: Optional[int] = None
    products: List[NomenclatureProduct] = dataclasses.field(
        default_factory=list,
    )
    is_custom: Optional[bool] = None
    is_base: Optional[bool] = None
    is_restaurant: Optional[bool] = None
    sort_order: Optional[int] = None
    images: List[dict] = dataclasses.field(default_factory=list)

    def add_product(self, *args, **kwargs):
        """
        Позволяем добавлять товар как через передачу объекта
        NomenclatureProduct, так и через кварги
        """
        args_len = len(args)
        if args_len > 0 and isinstance(args[0], NomenclatureProduct):
            product = args[0]
        else:
            product = NomenclatureProduct(**kwargs)
        self.products.append(product)


@dataclasses.dataclass
class NomenclatureCategoryContext:
    categories: List[NomenclatureCategory] = dataclasses.field(
        default_factory=list,
    )
    handler: Any = None

    def add_category(self, category):
        self.categories.append(category)


@pytest.fixture(name='mock_nomenclature_v2_details_context')
def _mock_nomenclature_v2_details_context(mockserver):
    context = NomenclatureProductContext()

    def mock_nomenclature_v2_details(context, request):
        if context.status_code != 200:
            return mockserver.make_response(status=context.status_code)

        request_checker.RequestChecker().add(
            request_checker.ProductsWithIdsChecker(),
        ).check(request)

        products = [
            product.build()
            for product in context.products
            if product.public_id in request.json['products']
        ]
        return {'categories': [], 'products': products}

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_ASSORTMENT)
    def _mock_nomenclature_v2_details(request):
        return mock_nomenclature_v2_details(context, request)

    context.handler = _mock_nomenclature_v2_details

    return context


@dataclasses.dataclass
class NomenclatureV1ProductCategory:
    public_id: int
    name: str
    parent_public_id: Optional[int] = None

    def build(self):
        return utils.build_v1_product_category(
            self.public_id, self.name, self.parent_public_id,
        )


@dataclasses.dataclass
class NomenclatureV1ProductCategoryContext(ContextWithStatusAndErrors):
    categories: List[NomenclatureV1ProductCategory] = dataclasses.field(
        default_factory=list,
    )
    handler: Any = None

    def add_category(self, public_id, name, parent_public_id=None):
        self.categories.append(
            NomenclatureV1ProductCategory(public_id, name, parent_public_id),
        )


@pytest.fixture(name='mock_nomenclature_v1_categories_context')
def _mock_nomenclature_v1_categories_context(mockserver):
    context = NomenclatureV1ProductCategoryContext()

    def mock_nomenclature_v1_categories(context, request):
        status_code = context.get_status_code()
        if status_code != 200:
            return mockserver.make_response(status=status_code)

        context.process_errors(mockserver)

        utils.REQUEST_WITH_PLACE_AND_ORIGIN_IDS.check(request)

        categories = [category.build() for category in context.categories]
        return {'categories': categories, 'products': []}

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PRODUCT_CATEGORIES)
    def _mock_nomenclature_v1_categories(request):
        return mock_nomenclature_v1_categories(context, request)

    context.handler = _mock_nomenclature_v1_categories

    return context


@pytest.fixture(name='mock_v1_nomenclature_context')
def _mock_v1_nomenclature_context(mockserver):
    context = NomenclatureCategoryContext()

    def mock_v1_nomenclature_handler(context, request):
        category_id = None
        if 'category_id' in request.query:
            category_id = request.query['category_id']

        response = {'categories': []}
        for category in context.categories:
            # mapping_updater ходит с public_id
            if (
                    category_id is not None
                    and category_id != category.id_
                    and category_id != str(category.public_id)
                    and category_id != category.parent_id
                    and category_id != str(category.parent_public_id)
            ):
                continue

            resp_cat = {
                'available': True,
                'id': category.id_,
                'images': category.images,
                'items': [],
                'name': category.name,
                'public_id': category.public_id,
                'sort_order': (
                    category.sort_order if category.sort_order else 1
                ),
                'is_custom': category.is_custom,
                'is_base': category.is_base,
                'is_restaurant': category.is_restaurant,
            }

            if category.parent_id and category.parent_public_id:
                resp_cat['parent_id'] = category.parent_id
                resp_cat['parent_public_id'] = category.parent_public_id

            if category_id is not None:
                for product in category.products:
                    resp_cat['items'].append(product.build(use_v2=False))

            response['categories'].append(resp_cat)

        return response

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE)
    def _mock_v1_nomenclature_handler(request):
        return mock_v1_nomenclature_handler(context, request)

    context.handler = _mock_v1_nomenclature_handler

    return context


@pytest.fixture(name='mock_v2_fetch_discounts_context')
def _mock_v2_fetch_discounts_context(mockserver):
    context = MatchDiscountContext()

    def mock_fetch_discounts(context, request):
        response = {}
        requested_hierarchies = request.json['hierarchies_fetch_parameters']
        discount_id = 0

        if context.match_experiments:
            assert set(context.match_experiments) == set(
                requested_hierarchies['menu_discounts']['conditions'][
                    'experiment'
                ],
            )

        if context.use_tags:
            assert (
                requested_hierarchies.get('menu_discounts', {})
                .get('conditions', {})
                .get('tag', [])
                or requested_hierarchies.get('yandex_menu_cashback', {})
                .get('conditions', {})
                .get('tag', [])
            )

        if 'menu_discounts' in requested_hierarchies:
            total_count = 0
            discounts = []
            for product in context.discount_products:
                discount_id += 1
                total_count += 1
                discounts.append(
                    {
                        'products': {
                            'values': [product.id_],
                            'is_excluded': False,
                        },
                        'discount': {
                            'discount_id': str(discount_id),
                            'discount_meta': product.discount_meta,
                            'money_value': {'menu_value': product.money_value},
                        },
                    },
                )
            response['menu_discounts'] = {
                'total_count': total_count,
                'discounts': discounts,
            }
        if (
                'place_menu_cashback' in requested_hierarchies
                or 'yandex_menu_cashback' in requested_hierarchies
        ):
            total_count = 0
            cashbacks = []
            for product in context.cashback_products:
                discount_id += 1
                total_count += 1
                cashbacks.append(
                    {
                        'products': {
                            'values': [product.id_],
                            'is_excluded': False,
                        },
                        'discount': {
                            'discount_id': str(discount_id),
                            'discount_meta': {'name': 'some name'},
                            'cashback_value': {
                                'menu_value': product.cashback_value,
                            },
                        },
                    },
                )
            response['place_menu_cashback'] = {
                'total_count': total_count,
                'discounts': cashbacks,
            }

        return response

    @mockserver.json_handler(utils.Handlers.FETCH_DISCOUNTS)
    def _mock_fetch_discounts(request):
        return mock_fetch_discounts(context, request)

    context.handler = _mock_fetch_discounts

    return context


@pytest.fixture(name='mock_internal_v1_places_context')
def _mock_internal_v1_places_context(mockserver):
    context = CatalogPlacesContext()

    def _prepare_error_reponse(status_code):
        return mockserver.make_response(
            json={'status': status_code, 'message': 'message'},
            status=status_code,
        )

    @mockserver.json_handler(utils.Handlers.CATALOG_INTERNAL_V1_PLACES)
    def _mock_internal_v1_places_context(request):
        if context.expected_request is not None:
            assert context.expected_request == request.json
        status_code = context.get_status_code()
        context.process_errors(mockserver)
        if status_code != 200:
            return _prepare_error_reponse(status_code)
        return context.build_places()

    context.handler = _mock_internal_v1_places_context

    return context


@pytest.fixture(name='mock_nomenclature_static_info_context')
def _mock_nomenclature_v1_products_info_context(mockserver):
    context = NomenclatureV1ProductsInfoContext()

    def mock_products_static_info(context, request):
        if context.request_ids is not None:
            assert set(request.json['product_ids']) == context.request_ids

        context.process_errors(mockserver)
        status_code = context.get_status_code()
        if status_code != 200:
            return mockserver.make_response(status=status_code)
        products = [
            product.build()
            for product in context.products
            if product.id_ in request.json['product_ids']
        ]
        return {'products': products}

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PRODUCTS_INFO)
    def _mock_nomenclature_v1_products_info_context(request):
        assert 'use_sku' not in request.query
        return mock_products_static_info(context, request)

    context.handler = _mock_nomenclature_v1_products_info_context

    return context


@pytest.fixture(name='mock_nomenclature_dynamic_info_context')
def _mock_nomenclature_v1_place_products_info_context(mockserver):
    context = NomenclatureV1PlaceProductsInfoContext()

    def mock_products_dynamic_info(context, request):
        context.process_errors(mockserver)
        status_code = context.get_status_code()
        if status_code != 200:
            return mockserver.make_response(status=status_code)

        utils.REQUEST_WITH_PLACE_AND_PRODUCT_IDS.check(request)

        if context.expected_request is not None:
            request.json['product_ids'].sort()
            context.expected_request['product_ids'].sort()
            assert request.json == context.expected_request

        products = [
            product.build()
            for product in context.products
            if product.id_ in request.json['product_ids']
        ]
        return {'products': products}

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PLACE_PRODUCTS_INFO)
    def _mock_nomenclature_v1_place_products_info_context(request):
        return mock_products_dynamic_info(context, request)

    context.handler = _mock_nomenclature_v1_place_products_info_context

    return context


@pytest.fixture(name='mock_nomenclature_categories_filtered_context')
def _mock_nomenclature_categories_filtered_context(mockserver):

    context = NomenclatureCategoriesFilteredContext()

    def _mock_nomenclature_categories(context, request):
        context.process_errors(mockserver)
        status_code = context.get_status_code()

        if context.expected_request is not None:
            assert request.json == context.expected_request

        if status_code != 200:
            return mockserver.make_response(
                status=status_code,
                json={'status': status_code, 'message': 'message'},
            )

        categories = [
            {
                'id': category.public_id,
                'origin_id': category.origin_id,
                'name': category.name,
                'child_ids': category.child_ids,
                'sort_order': category.sort_order,
                'type': category.type,
                'images': category.images,
                'filters': [filter.build() for filter in category.filters],
                'products': [product.build() for product in category.products],
                'parent_id': category.parent_public_id,
                'tags': category.tags,
            }
            for category in context.categories
        ]

        return {'categories': categories}

    @mockserver.json_handler(
        utils.Handlers.NOMENCLATURE_CATEGORY_PRODUCTS_FILTERED,
    )
    def _mock_nomenclature_categories_filtered_context(request):
        return _mock_nomenclature_categories(context, request)

    context.handler = _mock_nomenclature_categories_filtered_context

    return context


@pytest.fixture(name='mock_upsell_recommendations')
def _mock_upsell_recommendations(mockserver):
    @dataclasses.dataclass
    class Context:
        raise_error: bool = False
        status_code: int = 200
        recommendations: List[
            eats_upsell_recommendations.Recommendation
        ] = dataclasses.field(default_factory=list)
        request_item_categories: Optional[List[str]] = None

        def set_raise_error(self, raise_error: bool):
            self.raise_error = raise_error

        def set_expected_item_categories(self, categories: List[str]):
            self.request_item_categories = categories

        def add_recommendation(
                self,
                recommendation: eats_upsell_recommendations.Recommendation,
        ):
            self.recommendations.append(recommendation)

        def add_recommendations(
                self,
                recommendations: List[
                    eats_upsell_recommendations.Recommendation
                ],
        ):
            self.recommendations.extend(recommendations)

        @property
        def times_called(self) -> int:
            return recommendations.times_called

    ctx = Context()

    @mockserver.json_handler(utils.Handlers.UPSELL_RECOMMENDATIONS)
    def recommendations(request):
        assert request.json['place_slug'] != ''
        item = request.json['item']
        if ctx.request_item_categories is not None:
            assert 'public_category_ids' in item
            assert sorted(item['public_category_ids']) == sorted(
                ctx.request_item_categories,
            )

        if ctx.raise_error:
            raise mockserver.NetworkError()

        return mockserver.make_response(
            status=ctx.status_code,
            json={
                'recommendations': [
                    # pylint: disable=not-an-iterable
                    recommendation.asdict()
                    for recommendation in ctx.recommendations
                ],
            },
        )

    return ctx


@dataclasses.dataclass
class NomenclatureV1PlaceCategoriesGetParent:
    id_: str
    name: str
    parent_id: Optional[str] = None
    sort_order: Optional[int] = None
    type_: Optional[str] = None
    tags: Optional[List[str]] = None

    def build(self):
        return utils.build_v1_categories_get_parent(
            self.id_,
            self.name,
            self.parent_id,
            self.sort_order or 1,
            self.type_ or 'partner',
            self.tags,
        )


@dataclasses.dataclass
class NomenclatureV1PlaceCategoriesGetParentContext(
        ContextWithStatusAndErrors,
):
    categories: List[
        NomenclatureV1PlaceCategoriesGetParent
    ] = dataclasses.field(default_factory=list)
    handler: Any = None

    def add_category(
            self,
            id_,
            name='default',
            parent_id=None,
            sort_order=None,
            type_=None,
            tags=None,
    ):
        self.categories.append(
            NomenclatureV1PlaceCategoriesGetParent(
                id_, name, parent_id, sort_order, type_, tags,
            ),
        )


@dataclasses.dataclass
class OrdersHistoryProduct:
    public_id: str
    orders_count: int
    sku_id: Optional[str] = None


@dataclasses.dataclass
class RetailCategoriesBrandOrdersHistoryContext(ContextWithStatusAndErrors):
    brand_products: Dict[int, List[OrdersHistoryProduct]] = dataclasses.field(
        default_factory=dict,
    )
    handler: Any = None
    expected_request: Any = None

    def add_brand_product(
            self,
            brand_id: int,
            public_id: str,
            orders_count: int,
            sku_id: Optional[str] = None,
    ):
        # pylint: disable=E1135, E1137, E1136
        # Reason: dataclasses breaks linter type detection when used with dict,
        # which causes false-positive errors
        if brand_id not in self.brand_products:
            self.brand_products[brand_id] = []
        self.brand_products[brand_id].append(
            OrdersHistoryProduct(public_id, orders_count, sku_id),
        )

    def add_default_products(self):
        self.add_brand_product(1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001', 2)
        self.add_brand_product(1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002', 5)
        self.add_brand_product(1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003', 3)
        self.add_brand_product(1, 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b004', 1)


@dataclasses.dataclass
class RetailCategoriesCrossBrandOrdersHistoryContext(
        ContextWithStatusAndErrors,
):
    place_products: Dict[int, List[OrdersHistoryProduct]] = dataclasses.field(
        default_factory=dict,
    )
    handler: Any = None
    expected_request: Any = None

    def add_product(
            self,
            place_id: int,
            public_id: str,
            orders_count: int,
            sku_id: Optional[str] = None,
    ):
        # pylint: disable=E1135, E1137, E1136
        # Reason: dataclasses breaks linter type detection when used with dict,
        # which causes false-positive errors
        if place_id not in self.place_products:
            self.place_products[place_id] = []
        self.place_products[place_id].append(
            OrdersHistoryProduct(public_id, orders_count, sku_id),
        )


@pytest.fixture(name='mock_nomenclature_get_parent_context')
def _mock_nomenclature_get_parent_context(mockserver):
    context = NomenclatureV1PlaceCategoriesGetParentContext()

    def mock_get_parent_context(context, request):
        status_code = context.get_status_code()
        if status_code != 200:
            return mockserver.make_response(status=status_code)

        context.process_errors(mockserver)

        utils.REQUEST_WITH_PLACE_AND_CATEGORY_IDS.check(request)
        categories = [category.build() for category in context.categories]
        return {'categories': categories}

    @mockserver.json_handler(
        utils.Handlers.NOMENCLATURE_PLACE_CATEGORIES_GET_PARENT,
    )
    def _mock_nomenclature_get_parent_context(request):
        return mock_get_parent_context(context, request)

    context.handler = _mock_nomenclature_get_parent_context

    return context


@dataclasses.dataclass
class ProductMenuGoods:
    public_id: str
    origin_id: str
    name: str
    description: str = ''
    barcodes: List[str] = dataclasses.field(default_factory=list)
    is_choosable: bool = True
    measure: Optional[tuple] = None
    volume: Optional[tuple] = None
    is_catch_weight: bool = False
    adult: bool = False
    shipping_type: str = 'pickup'
    images: List[tuple] = dataclasses.field(default_factory=list)
    vendor_name: Optional[str] = None
    vendor_country: Optional[str] = None
    product_brand: Optional[str] = None
    processing_type: Optional[str] = None
    is_sku: bool = False
    carbohydrates: Optional[str] = None
    proteins: Optional[str] = None
    fats: Optional[str] = None
    calories: Optional[str] = None
    storage_requirements: Optional[str] = None
    expiration_info: Optional[str] = None
    in_stock: Optional[int] = None
    is_available: bool = True
    price: float = 1
    old_price: Optional[float] = None
    vat: Optional[str] = None
    vendor_code: Optional[str] = None
    location: Optional[str] = None

    # Filled by category
    parent_categories: List['CategoryMenuGoods'] = dataclasses.field(
        default_factory=list, init=False,
    )


@dataclasses.dataclass
class CategoryMenuGoods:
    public_id: str
    name: str
    origin_id: Optional[str] = None
    products: List[ProductMenuGoods] = dataclasses.field(default_factory=list)
    is_available: bool = True
    sort_order: int = 0
    category_type: str = 'partner'
    images: List[tuple] = dataclasses.field(default_factory=list)

    # Filled by methods
    product_id_to_sort_order: Dict[str, int] = dataclasses.field(
        default_factory=dict, init=False,
    )
    parent_category: Optional['CategoryMenuGoods'] = dataclasses.field(
        default=None, init=False,
    )
    child_categories: List['CategoryMenuGoods'] = dataclasses.field(
        default_factory=list, init=False,
    )

    def add_product(self, product: ProductMenuGoods, sort_order: int = 0):
        self.products.append(product)
        # pylint: disable=E1137
        # Reason: dataclasses breaks linter type detection when used with dict,
        # which causes false-positive errors
        self.product_id_to_sort_order[product.public_id] = sort_order
        product.parent_categories.append(self)

    def add_child_category(self, category: 'CategoryMenuGoods'):
        self.child_categories.append(category)
        category.parent_category = self


@dataclasses.dataclass
class PlaceMenuGoods:
    place_id: int
    slug: str
    brand_id: int

    root_categories: List[CategoryMenuGoods] = dataclasses.field(
        default_factory=list, init=False,
    )
    category_public_id_to_data: Dict[
        str, 'CategoryMenuGoods',
    ] = dataclasses.field(default_factory=dict, init=False)
    product_public_id_to_data: Dict[
        str, 'ProductMenuGoods',
    ] = dataclasses.field(default_factory=dict, init=False)

    def _add_category(self, category: CategoryMenuGoods):
        category_public_id = category.public_id

        # pylint: disable=E1135
        # Reason: dataclasses breaks linter type detection when used with dict,
        # which causes false-positive errors
        assert category_public_id not in self.category_public_id_to_data
        # pylint: disable=E1137
        # Reason: dataclasses breaks linter type detection when used with dict,
        # which causes false-positive errors
        self.category_public_id_to_data[category_public_id] = category

    def _add_category_products(self, category: CategoryMenuGoods):
        for product in category.products:
            product_public_id = product.public_id
            # pylint: disable=E1135
            # Reason: dataclasses breaks linter type detection
            # when used with dict, which causes false-positive errors
            if product_public_id not in self.product_public_id_to_data:
                self.add_product(product)

    def _add_categories_recursive(self, category: CategoryMenuGoods):
        self._add_category(category)
        self._add_category_products(category)
        for child_category in category.child_categories:
            self._add_categories_recursive(child_category)

    def add_root_category(self, category: CategoryMenuGoods):
        self.root_categories.append(category)
        self._add_categories_recursive(category)

    def add_product(self, product: ProductMenuGoods):
        product_public_id = product.public_id
        # pylint: disable=E1135
        # Reason: dataclasses breaks linter type detection when used with dict,
        # which causes false-positive errors
        assert product_public_id not in self.product_public_id_to_data

        # pylint: disable=E1137
        # Reason: dataclasses breaks linter type detection when used with dict,
        # which causes false-positive errors
        self.product_public_id_to_data[product_public_id] = product


class NomenclatureMenuGoodsContext(ContextWithStatusAndErrors):
    _taxi_config = None
    _taxi_eats_products = None
    _v1_nomenclature = None
    _v1_place_categories = None
    _v1_places_categories = None
    _v1_products_info = None
    _v1_places_products_info = None
    _v1_place_products_filtered = None

    _place: Optional[PlaceMenuGoods] = None

    def handle_v1_nomenclature(self, request):
        # TODO: add depth check somewhere

        assert request.query['slug'] == self._place.slug
        requested_category_id = request.query.get('category_id', None)
        if requested_category_id:
            assert len(self._place.root_categories) == 1
            assert (
                requested_category_id
                == self._place.root_categories[0].public_id
            )

        return {
            'categories': [
                {
                    'name': category.name,
                    'available': category.is_available,
                    'id': category.origin_id,
                    'public_id': int(category.public_id),
                    'sort_order': category.sort_order,
                    'parent_id': (
                        category.parent_category.origin_id
                        or category.parent_category.public_id
                        if category.parent_category
                        else None
                    ),
                    'parent_public_id': (
                        int(category.parent_category.public_id)
                        if category.parent_category
                        else None
                    ),
                    'images': [
                        {'url': url, 'hash': url, 'sort_order': sort_order}
                        for url, sort_order in category.images
                    ],
                    'is_custom': category.category_type != 'partner',
                    'is_base': category.category_type == 'custom_base',
                    'is_restaurant': (
                        category.category_type == 'custom_restaurant'
                    ),
                    'items': [
                        {
                            'adult': product.adult,
                            'description': {'general': product.description},
                            'id': product.origin_id,
                            'images': [
                                {'sort_order': sort_order, 'url': url}
                                for url, sort_order in product.images
                            ],
                            'is_available': product.is_available,
                            'in_stock': product.in_stock,
                            'is_catch_weight': product.is_catch_weight,
                            'is_choosable': product.is_choosable,
                            'measure': (
                                {
                                    'value': product.measure[0],
                                    'unit': product.measure[1],
                                }
                                if product.measure
                                else None
                            ),
                            'volume': (
                                {
                                    'value': product.volume[0],
                                    'unit': product.volume[1],
                                }
                                if product.volume
                                else None
                            ),
                            'name': product.name,
                            'old_price': product.old_price,
                            'price': product.price,
                            'public_id': product.public_id,
                            'shipping_type': product.shipping_type,
                            'sort_order': category.product_id_to_sort_order[
                                product.public_id
                            ],
                        }
                        for product in category.products
                    ],
                }
                for category in self._place.category_public_id_to_data.values()
            ],
        }

    def handle_v1_place_categories(self, request):
        # TODO: add depth check somewhere

        assert request.query['place_id'] == str(self._place.place_id)
        j = request.json

        requested_category_ids = j['category_ids']
        if requested_category_ids:
            assert len(self._place.root_categories) == 1
            assert (
                requested_category_ids[0]
                == self._place.root_categories['public_id']
            )

        return {
            'categories': [
                {
                    'id': category.public_id,
                    'images': [
                        {'url': url, 'sort_order': sort_order}
                        for url, sort_order in category.images
                    ],
                    'name': category.name,
                    'origin_id': category.origin_id,
                    'child_ids': [
                        child_cat.public_id
                        for child_cat in category.child_categories
                    ],
                    'parent_id': (
                        category.parent_category.public_id
                        if category.parent_category
                        else None
                    ),
                    'products': [
                        {
                            'id': product.public_id,
                            'sort_order': category.product_id_to_sort_order[
                                product.public_id
                            ],
                        }
                        for product in category.products
                    ],
                    'sort_order': category.sort_order,
                    'type': category.category_type,
                }
                for category in self._place.category_public_id_to_data.values()
            ],
        }

    def handle_v1_places_categories(self, request):
        j = request.json

        assert len(j['places_categories']) == 1

        place_categories = j['places_categories'][0]
        assert place_categories['place_id'] == self._place.place_id

        assert set(place_categories['categories']) == set(
            self._place.category_public_id_to_data.keys(),
        )

        return {
            'places_categories': [
                {
                    'categories': [
                        category.public_id
                        for category in self._place.category_public_id_to_data.values()  # noqa: E501
                        if category.is_available
                    ],
                    'place_id': self._place.place_id,
                },
            ],
        }

    def handle_v1_products_info(self, request):
        j = request.json

        assert set(j['product_ids']) == set(
            self._place.product_public_id_to_data.keys(),
        )

        return {
            'products': [
                {
                    'adult': product.adult,
                    'barcodes': [],
                    'description': {'general': product.description},
                    'id': product.public_id,
                    'images': [
                        {'url': url, 'sort_order': sort_order}
                        for url, sort_order in product.images
                    ],
                    'is_catch_weight': product.is_catch_weight,
                    'is_choosable': product.is_choosable,
                    'is_sku': product.is_sku,
                    'measure': (
                        {
                            'value': product.measure[0],
                            'unit': product.measure[1],
                        }
                        if product.measure
                        else None
                    ),
                    'volume': (
                        {'value': product.volume[0], 'unit': product.volume[1]}
                        if product.volume
                        else None
                    ),
                    'name': product.name,
                    'origin_id': product.origin_id,
                    'place_brand_id': str(self._place.brand_id),
                    'shipping_type': product.shipping_type,
                }
                for product in self._place.product_public_id_to_data.values()
            ],
        }

    def handle_v1_place_products_info(self, request):
        j = request.json

        assert request.query['place_id'] == str(self._place.place_id)
        assert set(j['product_ids']) == set(
            self._place.product_public_id_to_data.keys(),
        )

        return {
            'products': [
                {
                    'id': product.public_id,
                    'in_stock': product.in_stock,
                    'is_available': product.is_available,
                    'origin_id': product.origin_id,
                    'parent_category_ids': [
                        category.public_id
                        for category in product.parent_categories
                    ],
                    'price': product.price,
                    'old_price': product.old_price,
                }
                for product in self._place.product_public_id_to_data.values()
            ],
        }

    def handle_v1_category_filtered(self, request):
        assert request.query['place_id'] == str(self._place.place_id)
        requested_category_id = request.query['category_id']
        assert len(self._place.root_categories) == 1
        assert (
            requested_category_id == self._place.root_categories[0].public_id
        )

        return {
            'categories': [
                {
                    'id': category.public_id,
                    'origin_id': category.origin_id,
                    'name': category.name,
                    'child_ids': [],
                    'sort_order': category.sort_order,
                    'type': category.category_type,
                    'images': [
                        {'url': url, 'hash': url, 'sort_order': sort_order}
                        for url, sort_order in category.images
                    ],
                    'filters': [],
                    'products': [
                        {
                            'id': product.public_id,
                            'name': product.name,
                            'price': str(product.price),
                            'is_catch_weight': product.is_catch_weight,
                            'adult': product.adult,
                            'sort_order': category.product_id_to_sort_order[
                                product.public_id
                            ],
                            'images': [
                                {'url': url, 'sort_order': sort_order}
                                for url, sort_order in product.images
                            ],
                            'description': {'general': product.description},
                            'shipping_type': product.shipping_type,
                            'in_stock': product.in_stock,
                            'old_price': (
                                None
                                if product.old_price is None
                                else str(product.old_price)
                            ),
                            'measure': (
                                {
                                    'value': product.measure[0],
                                    'unit': product.measure[1],
                                }
                                if product.measure
                                else None
                            ),
                        }
                        for product in category.products
                        if product.is_available
                    ],
                    'parent_id': (
                        category.parent_category.public_id
                        if category.parent_category
                        else None
                    ),
                }
                for category in self._place.category_public_id_to_data.values()
                if category.is_available
            ],
        }

    def set_globals(self, taxi_config, taxi_eats_products):
        self._taxi_config = taxi_config
        self._taxi_eats_products = taxi_eats_products

    def set_mock_handlers(
            self,
            v1_nomenclature,
            v1_place_categories,
            v1_places_categories,
            v1_products_info,
            v1_places_products_info,
            v1_place_products_filtered,
    ):
        self._v1_nomenclature = v1_nomenclature
        self._v1_place_categories = v1_place_categories
        self._v1_places_categories = v1_places_categories
        self._v1_products_info = v1_products_info
        self._v1_places_products_info = v1_places_products_info
        self._v1_place_products_filtered = v1_place_products_filtered

    def set_place(self, place: PlaceMenuGoods):
        self._place = place

    def verify_mock_data_with_request(
            self, menu_goods_request_json, nmn_category_public_id=None,
    ):
        assert self._place.slug == menu_goods_request_json['slug']
        if 'category_id' in menu_goods_request_json:
            assert len(self._place.root_categories) == 1
            assert nmn_category_public_id
            assert (
                nmn_category_public_id
                == self._place.root_categories[0].public_id
            )

    def get_mock_times_called(self):
        return {
            'v1_nomenclature': self._v1_nomenclature.times_called,
            'v1_place_categories': self._v1_place_categories.times_called,
            'v1_places_categories': self._v1_places_categories.times_called,
            'v1_products_info': self._v1_products_info.times_called,
            'v1_places_products_info': (
                self._v1_places_products_info.times_called
            ),
            'v1_place_products_filtered': (
                self._v1_place_products_filtered.times_called
            ),
        }

    async def invoke_menu_goods_basic(
            self,
            request,
            integration_version,
            category_public_id=None,
            headers=None,
            use_version_for_all=True,
    ):
        if use_version_for_all:
            self._taxi_config.set_values(
                dict(
                    EATS_PRODUCTS_NOMENCLATURE_REQUEST_SETTINGS={
                        'get_items_categories_version': integration_version,
                        'repeat_category_handlers_version': (
                            integration_version
                        ),
                        'get_items_handlers_version': integration_version,
                        'menu_goods_category_products_version': (
                            integration_version
                        ),
                    },
                ),
            )
        self.verify_mock_data_with_request(request, category_public_id)

        response = await self._taxi_eats_products.post(
            utils.Handlers.MENU_GOODS, json=request, headers=headers,
        )
        if response.status_code != 200:
            return response

        times_called = self.get_mock_times_called()
        if integration_version == 'v1':
            assert times_called == {
                'v1_nomenclature': 1,
                'v1_place_categories': 0,
                'v1_places_categories': 0,
                'v1_products_info': 0,
                'v1_places_products_info': 0,
                'v1_place_products_filtered': 0,
            }
        elif 'category' in request or 'category_uid' in request:
            assert times_called == {
                'v1_nomenclature': 0,
                'v1_place_categories': 0,
                'v1_places_categories': 0,
                'v1_products_info': 0,
                'v1_places_products_info': 0,
                'v1_place_products_filtered': 1,
            }
        else:
            assert times_called == {
                'v1_nomenclature': 0,
                'v1_place_categories': 1,
                'v1_places_categories': 1,
                'v1_products_info': 0,
                'v1_places_products_info': 0,
                'v1_place_products_filtered': 0,
            }

        return response


@pytest.fixture(name='mock_nomenclature_info_by_skuid')
def _mock_nomenclature_info_by_skuid(mockserver):
    context = NomenclatureProductBySkuIdContext()

    def _prepare_error_reponse(status_code):
        return mockserver.make_response(
            json={'status': status_code, 'message': 'message'},
            status=status_code,
        )

    def mock_nomenclature_info_by_skuid(context, request):
        status_code = context.get_status_code()
        context.process_errors(mockserver)
        if status_code != 200:
            return _prepare_error_reponse(status_code)
        if not request.json['place_ids']:
            return _prepare_error_reponse(404)
        if not request.json['sku_id']:
            return _prepare_error_reponse(404)
        if context.expected_request is not None:
            assert context.expected_request == request.json
        context.stored_requests.append(request.json)
        return {'places_products': [item.build() for item in context.products]}

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_INFO_BY_SKU_ID)
    def _mock_nomenclature_info_by_skuid_context(request):
        return mock_nomenclature_info_by_skuid(context, request)

    context.handler = _mock_nomenclature_info_by_skuid_context

    return context


@pytest.fixture(name='mock_generalized_info_context')
def _mock_generalized_info(mockserver):
    context = GeneralizedProductContext()

    def _prepare_error_reponse(status_code):
        message = 'Unknown error'
        if status_code == 404:
            message = 'Product not found'
        if status_code == 500:
            message = 'Internal server error'

        return mockserver.make_response(
            json={'status': status_code, 'message': message},
            status=status_code,
        )

    def mock_products_generalized_info(context, request):
        status_code = context.get_status_code()
        if status_code != 200:
            return _prepare_error_reponse(status_code)
        context.process_errors(mockserver)

        if (
                context.static_data is None
                or context.dynamic_data is None
                or context.static_data.id_ is None
                or request.query['product_id'] != context.static_data.id_
        ):
            return _prepare_error_reponse(404)

        return {
            'product': {
                'static_data': {
                    'id': context.static_data.id_,
                    'origin_id': 'origin_id',
                    'place_brand_id': 'place_brand_id',
                    'name': context.static_data.name,
                    'description': 'some description',
                    'barcodes': [{'value': 'barcodes'}],
                    'is_choosable': True,
                    'measure': {'unit': 'KGRM', 'value': 1},
                    'is_catch_weight': False,
                    'is_adult': False,
                    'shipping_type': 'pickup',
                    'images': [],
                    'vendor_name': 'vendor',
                    'vendor_country': 'China',
                    'brand': 'brand',
                    'is_alcohol': False,
                    'is_fresh': False,
                    'sku_id': context.static_data.sku_id,
                },
                'dynamic_data': {
                    'price': context.dynamic_data.price,
                    'parent_category_ids': (
                        context.dynamic_data.parent_category_ids
                    ),
                },
                'id': context.static_data.id_,
            },
        }

    @mockserver.json_handler(utils.Handlers.RETAIL_SEO_GENERALIZED_INFO)
    def _mock_products_generalized_info_context(request):
        return mock_products_generalized_info(context, request)

    context.handler = _mock_products_generalized_info_context

    return context


@pytest.fixture(name='mock_nomenclature_for_v2_menu_goods')
def _mock_nomenclature_for_v2_menu_goods(
        mockserver, taxi_config, taxi_eats_products,
):
    context = NomenclatureMenuGoodsContext()

    @mockserver.json_handler('eats-nomenclature/v1/nomenclature')
    def _mock_nmn_nomenclature(request):
        status_code = context.get_status_code()
        if status_code != 200:
            return mockserver.make_response(status=status_code)
        return context.handle_v1_nomenclature(request)

    @mockserver.json_handler(
        utils.Handlers.NOMENCLATURE_PLACE_CATEGORIES_GET_CHILDREN,
    )
    def _mock_nmn_categories(request):
        status_code = context.get_status_code()
        if status_code != 200:
            return mockserver.make_response(status=status_code)
        return context.handle_v1_place_categories(request)

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PLACES_CATEGORIES)
    def _mock_nmn_places_categories(request):
        return context.handle_v1_places_categories(request)

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PRODUCTS_INFO)
    def _mock_nmn_products(request):
        return context.handle_v1_products_info(request)

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE_PLACE_PRODUCTS_INFO)
    def _mock_nmn_place_products(request):
        return context.handle_v1_place_products_info(request)

    @mockserver.json_handler(
        utils.Handlers.NOMENCLATURE_CATEGORY_PRODUCTS_FILTERED,
    )
    def _mock_nmn_place_products_filtered(request):
        status_code = context.get_status_code()
        if status_code != 200:
            return mockserver.make_response(status=status_code)
        return context.handle_v1_category_filtered(request)

    context.set_globals(taxi_config, taxi_eats_products)
    context.set_mock_handlers(
        _mock_nmn_nomenclature,
        _mock_nmn_categories,
        _mock_nmn_places_categories,
        _mock_nmn_products,
        _mock_nmn_place_products,
        _mock_nmn_place_products_filtered,
    )

    return context


@pytest.fixture(name='setup_nomenclature_handlers_v2')
def _setup_nomenclature_handlers_v2(
        mock_nomenclature_static_info_context,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_get_parent_context,
):
    def setup(
            expected_public_ids=None, extra_product=False, extra_discount=True,
    ):
        mock_nomenclature_static_info_context.add_product(
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
            name='item_1',
            description_general='abc',
            images=[
                {
                    'scale': 'aspect_fit',
                    'url': 'url_1/{w}x{h}',
                    'sort_order': 0,
                },
            ],
            is_catch_weight=False,
        )
        mock_nomenclature_static_info_context.add_product(
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
            name='item_2',
            description_general='def',
            images=[
                {
                    'scale': 'aspect_fit',
                    'url': 'url_2/{w}x{h}',
                    'sort_order': 0,
                },
            ],
            is_catch_weight=False,
            shipping_type='delivery',
        )
        mock_nomenclature_static_info_context.add_product(
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003',
            name='item_3',
            description_general='ghi',
            images=[],
            is_catch_weight=False,
            shipping_type='delivery',
        )

        mock_nomenclature_static_info_context.add_product(
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b007',
        )

        mock_nomenclature_dynamic_info_context.add_product(
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
            price=999.0,
            old_price=1999.0 if extra_discount else None,
            in_stock=20,
            parent_category_ids=['999105'],
        )
        mock_nomenclature_dynamic_info_context.add_product(
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
            price=990.0 if extra_discount else 999.0,
            old_price=1990.0 if extra_discount else 1000.0,
            in_stock=99,
            parent_category_ids=['999106'],
        )
        mock_nomenclature_dynamic_info_context.add_product(
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003',
            price=999.0 if extra_discount else 990.0,
            old_price=1000.0,
            parent_category_ids=['999106'],
        )
        mock_nomenclature_dynamic_info_context.add_product(
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b007',
            price=999,
            old_price=1000,
            is_available=False,
            in_stock=0,
        )

        if extra_product:
            mock_nomenclature_static_info_context.add_product(
                'bb231b95-1ff2-4bc4-b78d-dcaa1f69b004',
                description_general='ghi',
            )
            mock_nomenclature_dynamic_info_context.add_product(
                'bb231b95-1ff2-4bc4-b78d-dcaa1f69b004',
                price=990,
                old_price=1000,
                parent_category_ids=['333'],
            )

        if expected_public_ids is not None:
            mock_nomenclature_static_info_context.request_ids = (
                expected_public_ids
            )
            mock_nomenclature_dynamic_info_context.expected_request = {
                'product_ids': list(expected_public_ids),
            }

        mock_nomenclature_get_parent_context.add_category(
            '999106', 'Топ-левел категория 1',
        )
        mock_nomenclature_get_parent_context.add_category(
            '123', 'Топ-левел категория 2',
        )
        mock_nomenclature_get_parent_context.add_category(
            '333', 'Топ-левел категория 3',
        )
        mock_nomenclature_get_parent_context.add_category(
            '999105', 'Подкатегория 1', '123',
        )

    return setup


@pytest.fixture(name='mock_retail_categories_brand_orders_history')
def _mock_retail_categories_brand_orders_history(mockserver):
    context = RetailCategoriesBrandOrdersHistoryContext()

    @mockserver.json_handler(utils.Handlers.BRAND_ORDERS_HISTORY)
    def _mock_get_brand_orders_history(request):
        status_code = context.get_status_code()
        if status_code != 200:
            return mockserver.make_response(status=status_code)
        context.process_errors(mockserver)
        if context.expected_request is not None:
            assert request == context.expected_request

        return {
            'products': [
                {
                    'public_id': product.public_id,
                    'orders_count': product.orders_count,
                    'sku_id': product.sku_id,
                }
                for product in context.brand_products.get(
                    request.json['brand_id'], [],
                )
            ],
        }

    context.handler = _mock_get_brand_orders_history

    return context


@pytest.fixture(name='mock_retail_categories_cross_brand_orders')
def _mock_retail_categories_cross_brand_orders(mockserver):
    context = RetailCategoriesCrossBrandOrdersHistoryContext()

    @mockserver.json_handler(utils.Handlers.CROSS_BRAND_ORDERS_HISTORY)
    def _mock_get_cross_brand_orders_history(request):
        if context.expected_request is not None:
            assert request == context.expected_request
        context.process_errors(mockserver)
        status_code = context.get_status_code()
        if status_code != 200:
            return mockserver.make_response(status=status_code)

        return {
            'products': [
                {
                    'public_id': product.public_id,
                    'orders_count': product.orders_count,
                    'sku_id': product.sku_id,
                }
                for product in context.place_products.get(
                    request.json['place_id'], [],
                )
            ],
        }

    context.handler = _mock_get_cross_brand_orders_history

    return context
