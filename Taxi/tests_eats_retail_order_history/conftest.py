# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=too-many-lines
import collections
import copy
import datetime
import json
from typing import Dict
from typing import Optional
from typing import Tuple

import psycopg2.extras
import pytest
import pytz

from eats_retail_order_history_plugins import *  # noqa: F403 F401

from . import utils


@pytest.fixture(name='environment')
def _environment(mockserver, mocked_time, set_order_claim_fixture):
    class Environment:
        def __init__(self):
            self.user_orders = collections.defaultdict(dict)
            self.order_revisions = {}
            self.order_revisions_tags = {}
            self.place_assortment = {}
            self.place_info = {}
            self.picker_orders = {}
            self.order_diff = {}
            self.claims = {}
            self.order_claims = {}
            self.notifications_count = 0
            self.order_confirmation_timers = collections.defaultdict(dict)
            self._build_mocks()

        def set_default(self):
            revision_ids = ['aaa', 'bbb', 'ccc', 'ddd']
            self.add_user_order(status='delivered')
            self.add_order_customer_service(
                revision_id=revision_ids[0],
                customer_service_id='retail-product',
                customer_service_name='Расходы на исполнение '
                'поручений по заказу',
                cost_for_customer='780.00',
                type_='retail',
                composition_products=[
                    self.make_composition_product(
                        id_='item_000-0',
                        name='Макароны',
                        cost_for_customer='50.00',
                        origin_id='item-0',
                    ),
                    self.make_composition_product(
                        id_='item_111-1',
                        name='Дырка от бублика',
                        cost_for_customer='150.00',
                        origin_id='item-1',
                    ),
                    self.make_composition_product(
                        id_='item_111-2',
                        name='Дырка от бублика',
                        cost_for_customer='150.00',
                        origin_id='item-1',
                    ),
                    self.make_composition_product(
                        id_='item_222-1',
                        name='Виноград',
                        cost_for_customer='100.00',
                        weight=500,
                        origin_id='item-2',
                    ),
                    self.make_composition_product(
                        id_='item_333-1',
                        name='Малина',
                        cost_for_customer='120.00',
                        weight=600,
                        origin_id='item-3',
                    ),
                    self.make_composition_product(
                        id_='item_444-1',
                        name='Сыр',
                        cost_for_customer='200.00',
                        weight=200,
                        origin_id='item-4',
                    ),
                    self.make_composition_product(
                        id_='item_777-1',
                        name='Спички',
                        cost_for_customer='10.00',
                        origin_id='item-7',
                    ),
                ],
            )
            for revision_id in revision_ids[1:3]:
                self.add_order_customer_service(
                    revision_id=revision_id,
                    customer_service_id='retail-product',
                    customer_service_name='Расходы на исполнение '
                    'поручений по заказу',
                    cost_for_customer='777.00',
                    type_='retail',
                    composition_products=[
                        self.make_composition_product(
                            id_='item_000-0',
                            name='Макароны',
                            cost_for_customer='50.00',
                            origin_id='item-0',
                        ),
                        self.make_composition_product(
                            id_='item_111-1',
                            name='Дырка от бублика',
                            cost_for_customer='160.00',
                            origin_id='item-1',
                        ),
                        self.make_composition_product(
                            id_='item_111-2',
                            name='Дырка от бублика',
                            cost_for_customer='160.00',
                            origin_id='item-1',
                        ),
                        self.make_composition_product(
                            id_='item_555-1',
                            name='Сливы',
                            cost_for_customer='120.00',
                            weight=500,
                            origin_id='item-5',
                        ),
                        self.make_composition_product(
                            id_='item_666-1',
                            name='Клубника',
                            cost_for_customer='87.00',
                            weight=580,
                            origin_id='item-6',
                        ),
                        self.make_composition_product(
                            id_='item_444-1',
                            name='Сыр',
                            cost_for_customer='200.00',
                            weight=200,
                            origin_id='item-4',
                        ),
                    ],
                )
            self.add_order_customer_service(
                revision_id=revision_ids[2],
                customer_service_id='assembly',
                customer_service_name='Стоимость сборки',
                cost_for_customer='110.00',
                type_='assembly',
            )
            self.add_order_customer_service(
                revision_id=revision_ids[2],
                customer_service_id='delivery',
                customer_service_name='Стоимость доставки',
                cost_for_customer='100.00',
                type_='delivery',
            )
            self.add_order_customer_service(
                revision_id=revision_ids[3],
                customer_service_id='retail-product',
                customer_service_name='Расходы на исполнение '
                'поручений по заказу',
                cost_for_customer='617.00',
                refunded_amount='260.00',
                type_='retail',
                composition_products=[
                    self.make_composition_product(
                        id_='item_000-0',
                        name='Макароны',
                        cost_for_customer='50.00',
                        origin_id='item-0',
                    ),
                    self.make_composition_product(
                        id_='item_111-1',
                        name='Дырка от бублика',
                        cost_for_customer='60.00',
                        origin_id='item-1',
                    ),
                    self.make_composition_product(
                        id_='item_111-2',
                        name='Дырка от бублика',
                        cost_for_customer='0.00',
                        origin_id='item-1',
                    ),
                    self.make_composition_product(
                        id_='item_555-1',
                        name='Сливы',
                        cost_for_customer='120.00',
                        weight=500,
                        origin_id='item-5',
                    ),
                    self.make_composition_product(
                        id_='item_666-1',
                        name='Клубника',
                        cost_for_customer='87.00',
                        weight=580,
                        origin_id='item-6',
                    ),
                    self.make_composition_product(
                        id_='item_444-1',
                        name='Сыр',
                        cost_for_customer='200.00',
                        weight=200,
                        origin_id='item-4',
                    ),
                ],
                refunds=[
                    {
                        'refund_revision_id': revision_ids[3],
                        'refund_products': [
                            {'id': 'item_111-1', 'refunded_amount': '100.00'},
                            {'id': 'item_111-2', 'refunded_amount': '160.00'},
                        ],
                    },
                ],
            )
            self.add_order_customer_service(
                revision_id=revision_ids[3],
                customer_service_id='assembly',
                customer_service_name='Стоимость сборки',
                cost_for_customer='60.00',
                refunded_amount='50.00',
                type_='assembly',
            )
            self.add_order_customer_service(
                revision_id=revision_ids[3],
                customer_service_id='delivery',
                customer_service_name='Стоимость доставки',
                cost_for_customer='50.00',
                refunded_amount='50.00',
                type_='delivery',
            )
            self.add_order_customer_service(
                revision_id=revision_ids[3],
                customer_service_id='tips',
                customer_service_name='Чаевые курьеру',
                cost_for_customer='40.00',
                refunded_amount='40.00',
                type_='tips',
            )
            self.add_order_customer_service(
                revision_id=revision_ids[3],
                customer_service_id='restaurant_tips',
                customer_service_name='Чаевые ресторану',
                cost_for_customer='60.00',
                refunded_amount='60.00',
                type_='restaurant_tips',
            )
            for i in range(8):
                self.add_place_product(
                    origin_id=f'item-{i}',
                    image_urls=[f'https://yandex.ru/item-{i}.jpg'],
                )
            self.add_place_info(our_picking=True, business='shop')
            self.add_picker_order(picking_status='complete')
            self.add_order_diff(
                add=[
                    self.make_picker_item(
                        id_='item-5',
                        is_catch_weight=True,
                        quantity=0.5,
                        # цены намеренно проставлены не совпадающими
                        # с ценами из данных ревизий
                        price='100.00',
                        measure_value=1000,
                        measure_quantum=100,
                        quantum_quantity=5,
                        quantum_price='10.00',
                        name='Сливы',
                    ),
                ],
                remove=[
                    self.make_picker_item(
                        id_='item-2',
                        is_catch_weight=True,
                        quantity=0.5,
                        price='100.00',
                        measure_value=1000,
                        measure_quantum=500,
                        quantum_quantity=1,
                        quantum_price='50.00',
                        name='Виноград',
                    ),
                ],
                update=[
                    {
                        'from_item': self.make_picker_item(
                            id_='item-1',
                            is_catch_weight=False,
                            quantity=2,
                            price='100.00',
                            measure_quantum=500,
                            quantum_quantity=4,
                            quantum_price='50.00',
                            name='Дырка от бублика',
                        ),
                        'to_item': self.make_picker_item(
                            id_='item-1',
                            is_catch_weight=False,
                            quantity=2,
                            price='110.00',
                            measure_quantum=1000,
                            quantum_quantity=2,
                            quantum_price='110.00',
                            name='Дырка от бублика',
                            price_updated_at=mocked_time.now()
                            .replace(tzinfo=pytz.utc)
                            .isoformat(),
                        ),
                    },
                ],
                replace=[
                    {
                        'from_item': self.make_picker_item(
                            id_='item-3',
                            is_catch_weight=True,
                            quantity=1.2,
                            price='100.00',
                            measure_value=500,
                            measure_quantum=250,
                            quantum_quantity=2.4,
                            quantum_price='50.00',
                            name='Малина',
                        ),
                        'to_item': self.make_picker_item(
                            id_='item-4',
                            is_catch_weight=True,
                            quantity=2,
                            price='100.00',
                            measure_value=100,
                            measure_quantum=50,
                            quantum_quantity=4,
                            quantum_price='50.00',
                            name='Сыр',
                        ),
                    },
                    {
                        'from_item': self.make_picker_item(
                            id_='item-4',
                            is_catch_weight=True,
                            quantity=2,
                            price='100.00',
                            measure_value=100,
                            measure_quantum=50,
                            quantum_quantity=4,
                            quantum_price='50.00',
                            name='Сыр',
                        ),
                        'to_item': self.make_picker_item(
                            id_='item-6',
                            is_catch_weight=True,
                            quantity=0.58,
                            price='100.00',
                            measure_value=1000,
                            measure_quantum=290,
                            quantum_quantity=2,
                            quantum_price='29.00',
                            name='Клубника',
                        ),
                    },
                ],
                soft_delete=[
                    self.make_picker_item(
                        id_='item-7',
                        is_catch_weight=False,
                        quantity=1,
                        price='10.00',
                        measure_value=20,
                        measure_quantum=1,
                        quantum_quantity=1,
                        quantum_price='10.00',
                        name='Спички',
                    ),
                ],
                picked_items=[
                    'item-0',
                    'item-1',
                    'item-4',
                    'item-5',
                    'item-6',
                ],
            )

        @staticmethod
        def make_composition_product(
                id_: str,
                name: str,
                cost_for_customer: str,
                type_: str = 'product',
                parent_id: Optional[str] = None,
                origin_id: Optional[str] = None,
                weight: Optional[float] = None,
                measure_unit: Optional[str] = 'GRM',
                discounts: Optional[list] = None,
        ):
            composition_product: dict = dict(
                id=id_,
                name=name,
                cost_for_customer=cost_for_customer,
                type=type_,
                parent_id=parent_id,
                origin_id=origin_id,
            )
            if discounts is not None:
                composition_product['discounts'] = discounts
            if weight is not None and measure_unit is not None:
                composition_product['weight'] = {
                    'value': weight,
                    'measure_unit': measure_unit,
                }
            return composition_product

        def add_user_order(
                self,
                status: str,
                yandex_uid: str = utils.YANDEX_UID,
                order_id: str = utils.ORDER_ID,
                destinations: Tuple[dict] = (
                    {
                        'short_text': 'ул. Пушкина, д. Колотушкина',
                        'point': [30.33811, 59.93507],
                    },
                ),
                created_at=mocked_time.now(),
                **kwargs,
        ):
            order = dict(
                order_id=order_id,
                service='eats',
                title='Магнит',
                created_at=utils.datetime_to_string(created_at),
                status=status,
                calculation={
                    'addends': [],
                    'final_cost': '',
                    'discount': '',
                    'refund': '',
                    'currency_code': '',
                    'final_cost_decimal': '',
                },
                legal_entities=[],
                destinations=destinations,
                meta_info=None,
                **kwargs,
            )
            self.user_orders[yandex_uid][order_id] = order

        def add_order_customer_service(
                self,
                revision_id: str,
                customer_service_id: str,
                customer_service_name: str,
                cost_for_customer: str,
                type_: str,
                order_id: str = utils.ORDER_ID,
                place_id: str = utils.PLACE_ID,
                composition_products: Optional[list] = None,
                currency: str = 'RUB',
                refunds: Optional[list] = None,
                refunded_amount: Optional[str] = None,
                discounts: Optional[list] = None,
        ):
            order_revisions = self.order_revisions.setdefault(
                order_id, collections.defaultdict(dict),
            )
            customer_services = order_revisions[revision_id].setdefault(
                'customer_services', [],
            )
            customer_service = dict(
                id=customer_service_id,
                name=customer_service_name,
                cost_for_customer=cost_for_customer,
                currency=currency,
                type=type_,
                trust_product_id='eda_133158084',
                place_id=place_id,
                details={
                    'composition_products': composition_products,
                    'discriminator_type': 'composition_products_details',
                    # элементы refunds - словари с полями id и refunded_amount
                    'refunds': refunds,
                },
            )
            if refunded_amount is not None:
                customer_service['refunded_amount'] = refunded_amount
            if discounts is not None:
                order_revisions[revision_id]['discounts'] = discounts
            customer_services.append(customer_service)

        def add_place_product(
                self,
                origin_id: str,
                image_urls: list,
                place_id: str = utils.PLACE_ID,
                name: str = 'Название продукта',
                description: str = 'Описание продукта',
                price: float = 25.25,
                adult: bool = False,
                shipping_type: str = 'pickup',
        ):
            place_assortment = self.place_assortment.setdefault(place_id, {})
            place_assortment[origin_id] = dict(
                origin_id=origin_id,
                name=name,
                description=description,
                price=price,
                adult=adult,
                shipping_type=shipping_type,
                images=[{'url': image_url} for image_url in image_urls],
            )

        def add_place_info(
                self,
                our_picking: bool,
                place_id: str = utils.PLACE_ID,
                place_slug: str = utils.PLACE_SLUG,
                brand_id: str = utils.BRAND_ID,
                brand_slug: str = utils.BRAND_SLUG,
                brand_name: str = utils.BRAND_NAME,
                business: str = 'shop',
                is_marketplace: bool = True,
                name: str = utils.PLACE_NAME,
                city: str = utils.CITY,
                address: str = utils.PLACE_ADDRESS,
                region_id: int = utils.REGION_ID_RU,
        ):
            self.place_info[place_id] = dict(
                id=int(place_id),
                revision_id=1,
                updated_at=utils.datetime_to_string(mocked_time.now()),
                slug=place_slug,
                business=business,
                brand={
                    'id': int(brand_id),
                    'name': brand_name,
                    'slug': brand_slug,
                    'picture_scale_type': 'aspect_fit',
                },
                features={
                    'ignore_surge': False,
                    'supports_preordering': False,
                    'fast_food': False,
                    'shop_picking_type': (
                        'our_picking' if our_picking else 'shop_picking'
                    ),
                },
                name=name,
                type=('marketplace' if is_marketplace else 'native'),
                address={'city': city, 'short': address},
                region={
                    'id': region_id,
                    'geobase_ids': [],
                    'time_zone': 'UTC',
                },
            )

        def add_picker_order(
                self,
                picking_status: str,
                order_nr: str = utils.ORDER_ID,
                courier_id: str = utils.COURIER_ID,
                picker_id: str = utils.PICKER_ID,
                courier_phone_id: str = utils.COURIER_PHONE_ID,
                picker_phone_id: str = utils.PICKER_PHONE_ID,
                spent: str = None,
        ):
            self.picker_orders[order_nr] = dict(
                id='1',
                eats_id=order_nr,
                status=picking_status,
                flow_type='picking_packing',
                place_id=1,
                categories=[],
                picker_items=[],
                courier_id=courier_id,
                picker_id=picker_id,
                courier_phone_id=courier_phone_id,
                picker_phone_id=picker_phone_id,
                currency={'code': 'RUB', 'sign': '₽'},
                spent=spent,
                ordered_total='100.00',
                pickedup_total='100.00',
                total_weight=100,
                require_approval=False,
                created_at='2021-01-01T12:00:00+00:00',
                updated_at='2021-01-01T12:00:00+00:00',
                status_updated_at='2021-01-01T12:00:00+00:00',
            )

        def change_order_status(
                self, yandex_uid: str, order_id: str, status: str,
        ):
            self.user_orders[yandex_uid][order_id]['status'] = status

        @staticmethod
        def make_picker_item(
                id_: str,
                is_catch_weight: bool,
                quantity: float,
                price: str = '25.25',
                measure_value: int = 1000,
                measure_unit: str = 'GRM',
                measure_quantum: Optional[int] = None,
                quantum_quantity: Optional[float] = None,
                quantum_price: Optional[str] = None,
                name: str = 'Яблоки',
                barcodes: Tuple[str] = ('123454321',),
                weight_barcode_type: Optional[str] = None,
                vendor_code: str = '12345-54321',
                goods_check_text: Optional[str] = None,
                max_overweight: Optional[int] = None,
                category_id: str = '42',
                images: tuple = tuple(),
                location: Optional[str] = None,
                price_updated_at=None,
        ):
            if not images:
                images = (
                    {
                        'url': f'https://yandex.ru/{id_}.jpg',
                        'resized_url_pattern': (
                            f'https://yandex.ru/{id_}-{{w}}x{{h}}.jpg'
                        ),
                    },
                )
            picker_item: Dict = dict(
                id=id_,
                name=name,
                barcodes=list(barcodes),
                weight_barcode_type=weight_barcode_type,
                is_catch_weight=is_catch_weight,
                vendor_code=vendor_code,
                measure={'value': measure_value, 'unit': measure_unit},
                price=price,
                goods_check_text=goods_check_text,
                max_overweight=max_overweight,
                category_id=category_id,
                images=images,
                location=location,
                price_updated_at=price_updated_at,
            )
            if is_catch_weight:
                measure = picker_item['measure']
                measure['quantum'] = measure_value
                measure['value'] = int(measure_value * quantity)
            else:
                picker_item['count'] = int(quantity)
            if (
                    measure_quantum is not None
                    and quantum_quantity is not None
                    and quantum_price is not None
            ):
                picker_item['measure_v2'] = dict(
                    value=measure_value,
                    quantum=measure_quantum,
                    quantum_quantity=quantum_quantity,
                    absolute_quantity=int(quantum_quantity * measure_quantum),
                    quantum_price=quantum_price,
                    unit=measure_unit,
                )
            return picker_item

        def add_order_diff(
                self,
                add: list,
                replace: list,
                update: list,
                remove: list,
                soft_delete: list,
                picked_items: list,
                order_id: str = utils.ORDER_ID,
        ):
            self.order_diff[order_id] = {
                'add': add,
                'replace': replace,
                'update': update,
                'remove': remove,
                'soft_delete': soft_delete,
                'picked_items': picked_items,
            }

        def add_claim(
                self,
                order_nr: str,
                claim_id: str,
                phone: dict = None,
                created_ts: str = None,
        ):
            claim = {'id': claim_id, 'phone': phone, 'created_ts': created_ts}
            self.claims[claim_id] = claim
            current_claim = self.order_claims.get(order_nr)
            if (current_claim is None) or (
                    (claim['id'], claim['created_ts'])
                    > (current_claim['id'], current_claim['created_ts'])
            ):
                self.order_claims[order_nr] = claim
                set_order_claim_fixture(order_nr, claim_id, 1)

        def _build_mocks(self):
            @mockserver.json_handler(
                '/eats-core-orders-retrieve/orders/retrieve',
            )
            def _eats_core_orders_retrieve(request):
                assert request.method == 'POST'
                assert request.json['services'] == ['eats']
                assert not request.json['user_identity']['bound_yandex_uids']
                assert request.json['user_identity']['include_eater_orders']
                assert request.json['range']['results'] == 1
                user_orders = self.user_orders[
                    request.json['user_identity']['yandex_uid']
                ]
                order_id = request.json['range'].get('order_id', None)
                response = {'orders': []}
                if order_id in user_orders:
                    response['orders'].append(user_orders[order_id])
                return response

            self.mock_orders_retrieve = _eats_core_orders_retrieve

            @mockserver.json_handler('/eats-order-revision/v1/revision/list')
            def _eats_order_revision_list(request):
                assert request.method == 'GET'
                order_id = request.query['order_id']
                if order_id not in self.order_revisions:
                    return mockserver.make_response(status=404)
                order_revisions = self.order_revisions[order_id]
                return {
                    'order_id': order_id,
                    'revisions': [
                        {
                            'origin_revision_id': revision_id,
                            'tags': self.order_revisions_tags.get(revision_id),
                        }
                        for revision_id in order_revisions.keys()
                    ],
                }

            self.mock_order_revision_list = _eats_order_revision_list

            @mockserver.json_handler(
                '/eats-order-revision/v1/order-revision/customer-services'
                '/details',
            )
            def _eats_order_revision_details(request):
                assert request.method == 'POST'
                order_id = request.json['order_id']
                revision_id = request.json['origin_revision_id']
                if revision_id not in self.order_revisions.get(order_id, {}):
                    return mockserver.make_response(status=404)
                revision = self.order_revisions[order_id][revision_id]
                response = {
                    'origin_revision_id': revision_id,
                    'customer_services': revision['customer_services'],
                    'created_at': (
                        mocked_time.now().replace(tzinfo=pytz.utc).isoformat()
                    ),
                }
                if 'discounts' in revision:
                    response['discounts'] = revision['discounts']
                return response

            self.mock_order_revision_details = _eats_order_revision_details

            @mockserver.json_handler(
                '/eats-products/api/v2/place/assortment/details',
            )
            def _eats_products_place_assortment_details(request):
                assert request.method == 'POST'
                place_id = request.json['place_id']
                origin_ids = request.json['origin_ids']
                if place_id not in self.place_assortment:
                    return mockserver.make_response(
                        status=404,
                        json={
                            'error': 'not_found_place',
                            'message': 'Магазин не найден',
                        },
                    )
                place_assortment = self.place_assortment[place_id]
                return {
                    'products': [
                        place_assortment[origin_id]
                        for origin_id in origin_ids
                        if origin_id in place_assortment
                    ],
                    'categories': [],
                }

            self.mock_place_assortment_details = (
                _eats_products_place_assortment_details
            )

            @mockserver.json_handler(
                '/eats-catalog-storage/internal/eats-catalog-storage'
                '/v1/places/retrieve-by-ids',
            )
            def _eats_catalog_storage_retrieve_places(request):
                assert request.method == 'POST'
                place_ids = request.json['place_ids']
                assert len(place_ids) == 1
                assert set(request.json['projection']) == {
                    'brand',
                    'business',
                    'features',
                    'slug',
                    'address',
                    'name',
                    'type',
                    'region',
                }
                place_id = str(place_ids[0])
                if place_id not in self.place_info:
                    return {
                        'places': [],
                        'not_found_place_ids': [int(place_id)],
                    }
                return {
                    'places': [self.place_info[place_id]],
                    'not_found_place_ids': [],
                }

            self.mock_retrieve_places = _eats_catalog_storage_retrieve_places

            @mockserver.json_handler('/eats-picker-orders/api/v1/order')
            def _eats_picker_orders_get_order(request):
                assert request.method == 'GET'
                order_id = request.query['eats_id']
                if order_id not in self.picker_orders:
                    return mockserver.make_response(
                        status=404,
                        json={
                            'code': 'not_found',
                            'message': 'Заказ не найден',
                        },
                    )
                return {'payload': self.picker_orders[order_id], 'meta': {}}

            self.mock_get_picker_order = _eats_picker_orders_get_order

            @mockserver.json_handler(
                '/eats-picker-orders/api/v1/order/cart/diff',
            )
            def _eats_picker_orders_cart_diff(request):
                assert request.method == 'GET'
                order_id = request.query['eats_id']
                if order_id not in self.order_diff:
                    return mockserver.make_response(
                        status=404,
                        json={
                            'code': 'not_found',
                            'message': 'Заказ не найден',
                        },
                    )
                status = None
                if order_id in self.picker_orders:
                    status = self.picker_orders[order_id]['status']
                diff = dict(self.order_diff[order_id])
                if not status or status in [
                        'paid',
                        'packing',
                        'handing',
                        'cancelled',
                        'complete',
                ]:
                    diff['remove'] += diff['soft_delete']
                    diff['soft_delete'] = []
                else:
                    diff['remove'] = []
                return {'cart_diff': diff}

            self.mock_cart_diff = _eats_picker_orders_cart_diff

            @mockserver.json_handler('/eda-candidates/list-by-ids')
            def _eda_candidates_list_by_ids(request):
                known_positions = {utils.PICKER_ID: [43.412297, 39.965948]}
                result = []
                for courier_id in request.json['ids']:
                    pos = known_positions.get(courier_id)
                    if pos:
                        result.append({'id': courier_id, 'position': pos})
                return {'candidates': result}

            self.mock_eda_candidates_list = _eda_candidates_list_by_ids

            @mockserver.json_handler('/eats-core/v1/supply/performer-location')
            def _eats_core_performer_location(request):
                known_positions = {
                    utils.COURIER_ID: {
                        'longitude': 43.401854,
                        'latitude': 39.971893,
                        'is_precise': True,
                    },
                }

                courier_id = request.query.get('performer_id')
                assert courier_id
                position = known_positions.get(courier_id)
                if position:
                    return {'performer_position': position}
                return mockserver.make_response(
                    status=404,
                    json={
                        'isSuccess': False,
                        'statusCode': 404,
                        'type': f'Position not found for courier {courier_id}',
                    },
                )

            self.mock_performer_location = _eats_core_performer_location

            @mockserver.json_handler('/vgw-api/v1/forwardings')
            def _vgw_api_forwardings(request):
                known_conversions = {
                    utils.COURIER_PHONE_ID: {
                        'phone': '+7(111)1111111',
                        'ext': '1111',
                    },
                    utils.PICKER_PHONE_ID: {
                        'phone': '+7(222)2222222',
                        'ext': '2222',
                    },
                }
                assert request.method == 'POST'
                if len(request.json.get('call_location', [])) != 2:
                    return mockserver.make_response(
                        json.dumps(
                            {
                                'code': 'PartnerUnableToHandle',
                                'error': {
                                    'code': 'PartnerUnableToHandle',
                                    'message': (
                                        'call_location is invalid '
                                        'in the request'
                                    ),
                                },
                            },
                        ),
                        400,
                    )
                phone_id = request.json.get('callee_phone_id')
                assert phone_id

                if known_conversions.get(phone_id):
                    response = copy.deepcopy(known_conversions[phone_id])
                    response['expires_at'] = (
                        mocked_time.now()
                        + datetime.timedelta(seconds=request.json['new_ttl'])
                    ).strftime('%Y-%m-%dT%H:%M:%S+0000')
                    return response
                return mockserver.make_response(
                    json.dumps(
                        {
                            'code': 'BadCallee',
                            'error': {
                                'code': 'BadCallee',
                                'message': (
                                    f'No forwarding found for id {phone_id}'
                                ),
                            },
                        },
                    ),
                    400,
                )

            self.mock_vgw_api_forwardings = _vgw_api_forwardings

            @mockserver.json_handler(
                '/b2b-taxi/b2b/cargo/integration/v1/driver-voiceforwarding',
            )
            def _cargo_driver_voiceforwarding(request):
                assert request.method == 'POST'
                claim = self.claims.get(request.json['claim_id'])

                if not claim or not claim['phone']:
                    return mockserver.make_response(
                        status=404,
                        json={
                            'code': 'not_found',
                            'message': 'claim not found',
                        },
                    )

                phone = claim['phone']

                return mockserver.make_response(
                    status=200,
                    json={
                        'phone': phone['phone'],
                        'ext': phone['ext'],
                        'ttl_seconds': phone['ttl_seconds'],
                    },
                )

            self.mock_cargo_voiceforwarding = _cargo_driver_voiceforwarding

            @mockserver.json_handler('/eats-notifications/v1/notification')
            def _eats_notifications_notify(request):
                assert request.method == 'POST'
                self.notifications_count += 1
                return {
                    'token': (
                        f'notification_token_{self.notifications_count - 1}'
                    ),
                }

            self.mock_eats_notification_notify = _eats_notifications_notify

            @mockserver.json_handler('/eats-picker-timers/api/v1/timer')
            def _eats_picker_timers_get_timer(request):
                assert request.method == 'GET'
                eats_id = request.query['eats_id']
                timer_type = request.query['timer_type']
                order_timers = self.order_confirmation_timers.get(eats_id)
                if (
                        order_timers is None
                        or timer_type not in order_timers
                        or order_timers[timer_type] is None
                ):
                    return mockserver.make_response(
                        status=404,
                        json={
                            'code': 'TIMER_NOT_FOUND',
                            'message': 'Timer not found',
                        },
                    )
                timer = order_timers[timer_type]
                return mockserver.make_response(
                    status=200,
                    json=dict(
                        {
                            'timer_id': 0,
                            'eats_id': eats_id,
                            'picker_id': utils.PICKER_ID,
                            'timer_type': timer_type,
                            'duration': 300,
                            'started_at': (
                                mocked_time.now()
                                .replace(tzinfo=pytz.utc)
                                .isoformat()
                            ),
                            'updated_at': (
                                mocked_time.now()
                                .replace(tzinfo=pytz.utc)
                                .isoformat()
                            ),
                        },
                        **timer,
                    ),
                )

            self.mock_eats_picker_timers_timer = _eats_picker_timers_get_timer

    return Environment()


@pytest.fixture(name='get_cursor')
def _get_cursor(pgsql):
    def create_cursor():
        cursor = pgsql['eats_retail_order_history'].dict_cursor()
        psycopg2.extras.register_composite(
            'eats_retail_order_history.point', cursor,
        )
        psycopg2.extras.register_composite(
            'eats_retail_order_history.expiring_phone', cursor,
        )
        psycopg2.extras.register_composite(
            'eats_retail_order_history.weight', cursor,
        )
        psycopg2.extras.register_composite(
            'eats_retail_order_history.discount_info_v1', cursor,
        )
        psycopg2.extras.register_composite(
            'eats_retail_order_history.discount_v1', cursor,
        )
        psycopg2.extras.register_composite(
            'eats_retail_order_history.item_discount_v1', cursor,
        )
        return cursor

    return create_cursor


@pytest.fixture(name='create_order')
def _create_order(get_cursor, mocked_time):
    def do_create_order(
            yandex_uid=utils.YANDEX_UID,
            order_nr=utils.ORDER_ID,
            customer_id=utils.CUSTOMER_ID,
            taxi_user_id=utils.TAXI_USER_ID,
            place_id=None,
            place_slug=None,
            place_name=None,
            is_marketplace=None,
            application=utils.APPLICATION,
            city=None,
            place_address=None,
            place_business=None,
            status_for_customer=None,
            picking_status=None,
            currency_code=None,
            cost_for_place=None,
            original_cost_for_customer=None,
            original_cost_without_discounts=None,
            final_cost_for_customer=None,
            final_cost_without_discounts=None,
            refund_amount=None,
            delivery_cost_for_customer=None,
            picking_cost_for_customer=None,
            tips=None,
            restaurant_tips=None,
            our_picking=None,
            brand_id=None,
            brand_slug=None,
            brand_name=None,
            delivery_address=None,
            delivery_point=None,
            courier_id=None,
            picker_id=None,
            courier_phone_id=None,
            picker_phone_id=None,
            courier_phone=None,
            picker_phone=None,
            diff=None,
            cart_diff=None,
            order_created_at=datetime.datetime.now(pytz.utc),
            status_updated_at=datetime.datetime.now(pytz.utc),
            updated_at=datetime.datetime.now(pytz.utc),
            last_revision_id=None,
            service_fee=None,
            region_id=None,
            personal_phone_id=None,
            claim_id=None,
            claim_id_attempt=None,
    ):
        if isinstance(delivery_point, dict):
            delivery_point = (
                delivery_point['latitude'],
                delivery_point['longitude'],
            )
        if isinstance(diff, dict):
            diff = json.dumps(diff)
        if isinstance(cart_diff, dict):
            cart_diff = json.dumps(cart_diff)
        if isinstance(courier_phone, dict):
            courier_phone = (
                courier_phone['forwarded_phone'],
                courier_phone['expires_at'],
            )
        if isinstance(picker_phone, dict):
            picker_phone = (
                picker_phone['forwarded_phone'],
                picker_phone['expires_at'],
            )
        if original_cost_without_discounts is None:
            original_cost_without_discounts = original_cost_for_customer
        cursor = get_cursor()
        cursor.execute(
            'INSERT INTO eats_retail_order_history.order_history ('
            'yandex_uid, order_nr, customer_id, taxi_user_id, place_id, '
            'place_slug, place_name, is_marketplace, application, city, '
            'place_address, place_business, status_for_customer, '
            'picking_status, currency_code, cost_for_place, '
            'original_cost_for_customer, original_cost_without_discounts, '
            'final_cost_for_customer, final_cost_without_discounts, '
            'refund_amount, delivery_cost_for_customer, '
            'picking_cost_for_customer, tips, restaurant_tips, our_picking, '
            'brand_id, brand_slug, brand_name, delivery_address, '
            'delivery_point, courier_id, picker_id, courier_phone_id, '
            'picker_phone_id, courier_phone, picker_phone, diff, cart_diff, '
            'order_created_at, status_updated_at, updated_at, '
            'last_revision_id, service_fee, region_id, personal_phone_id, '
            'claim_id, claim_id_attempt)'
            'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '
            '%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '
            '%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '
            '%s, %s) '
            'RETURNING id',
            [
                yandex_uid,
                order_nr,
                customer_id,
                taxi_user_id,
                place_id,
                place_slug,
                place_name,
                is_marketplace,
                application,
                city,
                place_address,
                place_business,
                status_for_customer,
                picking_status,
                currency_code,
                cost_for_place,
                original_cost_for_customer,
                original_cost_without_discounts,
                final_cost_for_customer,
                final_cost_without_discounts,
                refund_amount,
                delivery_cost_for_customer,
                picking_cost_for_customer,
                tips,
                restaurant_tips,
                our_picking,
                brand_id,
                brand_slug,
                brand_name,
                delivery_address,
                delivery_point,
                courier_id,
                picker_id,
                courier_phone_id,
                picker_phone_id,
                courier_phone,
                picker_phone,
                diff,
                cart_diff,
                order_created_at,
                status_updated_at,
                updated_at,
                last_revision_id,
                service_fee,
                region_id,
                personal_phone_id,
                claim_id,
                claim_id_attempt,
            ],
        )
        return cursor.fetchone()[0]

    return do_create_order


@pytest.fixture(name='create_order_item')
def _create_order_item(get_cursor, mocked_time):
    def do_create_order_item(
            order_id,
            origin_id,
            name,
            cost_for_customer,
            count=None,
            weight=None,
            images=None,
    ):
        if isinstance(weight, dict):
            weight = (weight['value'], weight['measure_unit'])
        cursor = get_cursor()
        cursor.execute(
            'INSERT INTO eats_retail_order_history.original_order_items ('
            'order_id, origin_id, name, cost_for_customer, count, weight, '
            'images) '
            'VALUES (%s, %s, %s, %s, %s, %s, %s) '
            'RETURNING id',
            [
                order_id,
                origin_id,
                name,
                cost_for_customer,
                count,
                weight,
                images,
            ],
        )
        return cursor.fetchone()[0]

    return do_create_order_item


@pytest.fixture()
def create_customer_notification(get_cursor, mocked_time):
    def do_create_customer_notification(
            order_nr=utils.ORDER_ID,
            idempotency_token='idempotency_token_0',
            notification_type=None,
            notification_type_v2='first_retail_order_changes',
            status_for_customer='cooking',
            picking_status='complete',
            customer_id=utils.CUSTOMER_ID,
            application=utils.APPLICATION,
            events=None,
            notification_key='eats',
            project='eats',
            token='notification_token',
            created_at=mocked_time.now(),
    ):
        if events is None:
            events = []
        cursor = get_cursor()
        cursor.execute(
            'INSERT INTO eats_retail_order_history.customer_notifications ('
            'order_nr, idempotency_token, notification_type, '
            'notification_type_v2, status_for_customer, picking_status, '
            'events, customer_id, notification_key, project, application, '
            'token, created_at) '
            'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) '
            'RETURNING id',
            [
                order_nr,
                idempotency_token,
                notification_type,
                notification_type_v2,
                status_for_customer,
                picking_status,
                events,
                customer_id,
                notification_key,
                project,
                application,
                token,
                created_at,
            ],
        )
        return cursor.fetchone()[0]

    return do_create_customer_notification


@pytest.fixture()
def get_order(get_cursor):
    def do_get_order(order_id):
        cursor = get_cursor()
        cursor.execute(
            'SELECT * FROM eats_retail_order_history.order_history '
            'WHERE id = %s',
            [order_id],
        )
        return cursor.fetchone()

    return do_get_order


@pytest.fixture()
def get_order_by_order_nr(get_cursor):
    def do_get_order(order_nr):
        cursor = get_cursor()
        cursor.execute(
            'SELECT * FROM eats_retail_order_history.order_history '
            'WHERE order_nr = %s',
            [order_nr],
        )
        return cursor.fetchone()

    return do_get_order


@pytest.fixture()
def get_order_items(get_cursor):
    def do_get_order_items(order_id):
        cursor = get_cursor()
        cursor.execute(
            'SELECT * FROM eats_retail_order_history.original_order_items '
            'WHERE order_id = %s '
            'ORDER BY origin_id',
            [order_id],
        )
        return cursor.fetchall()

    return do_get_order_items


@pytest.fixture()
def get_notification(get_cursor):
    def do_get_notification(idempotency_token):
        cursor = get_cursor()
        cursor.execute(
            'SELECT * FROM eats_retail_order_history.customer_notifications '
            'WHERE idempotency_token = %s '
            'ORDER BY created_at DESC '
            'LIMIT 1',
            [idempotency_token],
        )
        return cursor.fetchone()

    return do_get_notification


@pytest.fixture(autouse=True)
def init_currencies(experiments3):
    experiments3.add_experiment3_from_marker(utils.currencies_config3(), None)


@pytest.fixture(autouse=True)
def init_measure_units(get_cursor):
    cursor = get_cursor()
    cursor.execute(
        'INSERT INTO eats_retail_order_history.measure_units '
        '(okei_code, okei_name, okei_sign_ru, okei_sign) '
        'VALUES '
        '(163, \'GRM\', \'г\', \'g\'), '
        '(111, \'MLT\', \'мл\', \'ml\'), '
        '(111, \'CMQ\', \'см3\', \'cm3\'), '
        '(112, \'DMQ\', \'дм3\', \'dm3\')',
    )


@pytest.fixture()
def create_order_from_json(create_order, create_order_item):
    def do_create_order_from_json(order_data):
        order = order_data['order']
        order_id = create_order(**order)
        for item in order_data['original_items']:
            item['order_id'] = order_id
            create_order_item(**item)
        return order_id

    return do_create_order_from_json


@pytest.fixture()
def get_order_claim(get_cursor):
    def do_get_order_claim(order_nr):
        cursor = get_cursor()
        cursor.execute(
            'SELECT claim_id, claim_id_attempt '
            'FROM eats_retail_order_history.order_history '
            'WHERE order_nr = %s',
            [order_nr],
        )
        return cursor.fetchone()

    return do_get_order_claim


@pytest.fixture(name='set_order_claim_fixture')
def set_order_claim(get_cursor):
    def do_set_order_claim(order_nr, claim_id, attempt):
        cursor = get_cursor()
        cursor.execute(
            'UPDATE eats_retail_order_history.order_history '
            'SET claim_id=%s, claim_id_attempt=%s '
            'WHERE order_nr=%s',
            [claim_id, attempt, order_nr],
        )

    return do_set_order_claim


@pytest.fixture(name='assert_response_body')
def _assert_response_body():
    def do_assert_response_body(actual_response, expected_response):
        courier_phone = expected_response.get('forwarded_courier_phone')
        picker_phone = expected_response.get('forwarded_picker_phone')
        status_for_customer = expected_response.get('status_for_customer')
        picking_status = expected_response.get('picking_status')
        if courier_phone and status_for_customer:
            status_for_customer = utils.StatusForCustomer[status_for_customer]
            if status_for_customer not in [
                    utils.StatusForCustomer.in_delivery,
                    utils.StatusForCustomer.arrived_to_customer,
            ]:
                del expected_response['forwarded_courier_phone']
        if picker_phone and picking_status:
            picking_status = utils.PickingStatus[picking_status]
            if not (
                    utils.PickingStatus.picking
                    <= picking_status
                    < utils.PickingStatus.cancelled
            ):
                del expected_response['forwarded_picker_phone']
        assert utils.format_response(actual_response) == expected_response

    return do_assert_response_body


@pytest.fixture(name='assert_response')
def _assert_response(taxi_eats_retail_order_history, assert_response_body):
    async def do_assert_response(expected_status, expected_response=None):
        response = await taxi_eats_retail_order_history.get(
            '/eats/v1/retail-order-history/customer/order/history',
            params={'order_nr': utils.ORDER_ID},
            headers={
                'X-Eats-User': f'user_id={utils.CUSTOMER_ID}',
                'X-Yandex-UID': utils.YANDEX_UID,
            },
        )
        assert response.status_code == expected_status
        if expected_response is not None:
            assert_response_body(response.json(), expected_response)
        return response

    return do_assert_response


@pytest.fixture()
def assert_mocks(environment):
    def do_assert_mocks(
            orders_retrieve_called=0,
            order_revision_list_called=0,
            order_revision_details_called=0,
            place_assortment_details_called=0,
            retrieve_places_called=0,
            get_picker_order_called=0,
            cart_diff_called=0,
            eda_candidates_list_called=0,
            performer_location_called=0,
            vgw_api_forwardings_called=0,
            cargo_driver_voiceforwardings_called=0,
    ):
        assert (
            environment.mock_orders_retrieve.times_called
            == orders_retrieve_called
        )
        assert (
            environment.mock_order_revision_list.times_called
            == order_revision_list_called
        )
        assert (
            environment.mock_order_revision_details.times_called
            == order_revision_details_called
        )
        assert (
            environment.mock_place_assortment_details.times_called
            == place_assortment_details_called
        )
        assert (
            environment.mock_retrieve_places.times_called
            == retrieve_places_called
        )
        assert (
            environment.mock_get_picker_order.times_called
            == get_picker_order_called
        )
        assert (
            environment.mock_eda_candidates_list.times_called
            == eda_candidates_list_called
        )
        assert (
            environment.mock_performer_location.times_called
            == performer_location_called
        )
        assert (
            environment.mock_vgw_api_forwardings.times_called
            == vgw_api_forwardings_called
        )
        assert (
            environment.mock_cargo_voiceforwarding.times_called
            == cargo_driver_voiceforwardings_called
        )
        assert environment.mock_cart_diff.times_called == cart_diff_called

    return do_assert_mocks


@pytest.fixture(name='mock_timers', autouse=True)
def _mock_timers(mockserver):
    @mockserver.json_handler('/eats-picker-timers/api/v1/timer')
    def _eats_picker_timers_get_timer(request):
        return mockserver.make_response(
            status=404,
            json={'code': 'TIMER_NOT_FOUND', 'message': 'Timer not found'},
        )
