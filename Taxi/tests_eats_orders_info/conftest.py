# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=too-many-lines
import collections
from typing import Dict
from typing import Optional

from psycopg2 import extras
import pytest

from eats_orders_info_plugins import *  # noqa: F403 F401

from tests_eats_orders_info import bdu_orders_utils
from tests_eats_orders_info import utils


@pytest.fixture(name='local_services')
def _local_services(mockserver, mocked_time, load_json):
    class Context:
        orders = None
        exp_order_ids = []
        brands_response = None
        superapp_response = None
        retail_response = None
        core_order_info_response = None
        mock_core_orders = None
        mock_ride_donations = None
        mock_superapp_orders = None
        mock_retail_orders = None
        mock_core_order_info = None
        exp_superapp_request_body = {}
        core_response_code = 200
        persey_response_code = 200
        core_headers = {}
        superapp_response_code = 200
        retail_response_code = 200
        retail_response_headers = None
        core_order_info_response_code = 200
        feedbacks = None
        feedbacks_response_code = 200
        mock_feedbacks = None
        receipts_data = None
        receipts_code = 200
        mock_receipts = None
        user_orders = collections.defaultdict(dict)
        place_assortment = collections.defaultdict(list)
        order_revisions = {}
        place_info = {}
        mock_core_revision_list = None
        mock_core_revision_details = None
        mock_service_revision_details = None
        mock_catalog_retrieve_places = None
        mock_place_assortment_details = None
        mock_place_history_details = None
        mock_tracking_claims = None
        mock_cargo_driver_vfwd = None

        claims = {}
        order_claims = collections.defaultdict(list)

        def set_default(self, status='finished', bus_type='restaurant'):
            revision_ids = ['aaa', 'bbb', 'ccc', 'ddd']
            self.add_user_order(status=status, bus_type=bus_type)
            self.add_order_customer_service(
                revision_id=revision_ids[0],
                customer_service_id='restaurant-product',
                customer_service_name='Расходы на исполнение '
                'поручений по заказу',
                cost_for_customer='780.00',
                type_='composition_products',
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
                    customer_service_id='rest-product',
                    customer_service_name='Расходы на исполнение '
                    'поручений по заказу',
                    cost_for_customer='707.00',
                    type_='composition_products',
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
                customer_service_id='delivery',
                customer_service_name='Стоимость доставки',
                cost_for_customer='100.00',
                type_='delivery',
            )
            self.add_order_customer_service(
                revision_id=revision_ids[3],
                customer_service_id='rest-product',
                customer_service_name='Расходы на исполнение '
                'поручений по заказу',
                cost_for_customer='607.00',
                refunded_amount='150.00',
                type_='composition_products',
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
                            {'id': 'item_111-2', 'refunded_amount': '150.00'},
                        ],
                    },
                ],
            )
            self.add_order_customer_service(
                revision_id=revision_ids[3],
                customer_service_id='delivery',
                customer_service_name='Стоимость доставки',
                cost_for_customer='50.00',
                type_='delivery',
            )
            self.add_order_customer_service(
                revision_id=revision_ids[3],
                customer_service_id='tips',
                customer_service_name='Чаевые курьеру',
                cost_for_customer='40.00',
                type_='tips',
            )
            self.add_order_customer_service(
                revision_id=revision_ids[3],
                customer_service_id='restaurant_tips',
                customer_service_name='Чаевые ресторану',
                cost_for_customer='60.00',
                type_='restaurant_tips',
            )
            for i in range(8):
                self.add_place_product(
                    origin_id=f'item-{i}',
                    image_urls=[f'https://yandex.ru/item-{i}.jpg'],
                )
            self.add_place_info(business='restaurant')
            self.add_claim(phone=utils.COURIER_PHONE)

        @staticmethod
        def make_composition_product(
                id_: str,
                name: str,
                cost_for_customer: str,
                type_: str = 'product',
                parent_id: Optional[str] = None,
                origin_id: Optional[str] = None,
                stand_alone_item_parent_id: Optional[str] = None,
                weight: Optional[float] = None,
                measure_unit: Optional[str] = 'GRM',
        ):
            composition_product: dict = dict(
                id=id_,
                name=name,
                cost_for_customer=cost_for_customer,
                type=type_,
                parent_id=parent_id,
                origin_id=origin_id,
                stand_alone_item_parent_id=stand_alone_item_parent_id,
            )
            if weight is not None and measure_unit is not None:
                composition_product['weight'] = {
                    'value': weight,
                    'measure_unit': measure_unit,
                }
            return composition_product

        @staticmethod
        def make_order_item(
                id_: str,
                order_id: str = utils.ORDER_NR_ID,
                origin_id: str = '123',
                name: str = 'Яблоки',
                cost_for_customer: float = 123.0,
                count: int = 1,
                weight: int = 1,
                images: tuple = tuple(),
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
            order_item: Dict = dict(
                id=id_,
                order_id=order_id,
                origin_id=origin_id,
                name=name,
                cost_for_customer=cost_for_customer,
                count=count,
                weight=weight,
                images=images,
            )
            return order_item

        def add_user_order(
                self,
                status: str,
                order_id: str = utils.ORDER_NR_ID,
                lon: float = 30.33811,
                lat: float = 59.93507,
                city: str = 'д. Колотушкина',
                street: str = 'ул. Пушкина',
                created_at=utils.SAMPLE_TIME_CONVERTED,
                bus_type: str = 'restaurant',
                **kwargs,
        ):
            order = dict(
                order_id=order_id,
                created_at=created_at,
                status=status,
                lon=lon,
                lat=lat,
                city=city,
                street=street,
                bus_type=utils.core_type(bus_type),
                **kwargs,
            )
            self.user_orders[order_id] = order

        def add_place_product(
                self,
                origin_id: str,
                image_urls: list,
                name: str = 'Название продукта',
                price: float = 25.25,
                place_id: str = utils.PLACE_ID,
        ):
            self.place_assortment[place_id].append(
                dict(
                    id=origin_id,
                    name=name,
                    price=price,
                    available=True,
                    categoryId='categoryId',
                    images=[{'url': image_url} for image_url in image_urls],
                ),
            )

        def add_place_info(
                self,
                place_id: str = utils.PLACE_ID,
                place_slug: str = utils.PLACE_SLUG,
                brand_id: str = utils.BRAND_ID,
                brand_slug: str = utils.BRAND_SLUG,
                brand_name: str = utils.BRAND_NAME,
                business: str = 'restaurant',
                is_marketplace: bool = False,
                name: str = utils.PLACE_NAME,
                city: str = utils.CITY,
                address: str = utils.PLACE_ADDRESS,
        ):
            self.place_info[place_id] = dict(
                id=int(place_id),
                revision_id=1,
                updated_at=utils.SAMPLE_TIME_CONVERTED,
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
                },
                name=name,
                type=('marketplace' if is_marketplace else 'native'),
                address={'city': city, 'short': address},
            )

        def add_order_customer_service(
                self,
                revision_id: str,
                customer_service_id: str,
                customer_service_name: str,
                cost_for_customer: str,
                type_: str,
                order_id: str = utils.ORDER_NR_ID,
                place_id: str = utils.PLACE_ID,
                composition_products: Optional[list] = None,
                currency: str = 'RUB',
                refunds: Optional[list] = None,
                refunded_amount: Optional[str] = None,
        ):
            order_revisions = self.order_revisions.setdefault(order_id, {})
            revision = order_revisions.setdefault(revision_id, [])
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
            revision.append(customer_service)

        def add_claim(
                self,
                order_nr: str = utils.ORDER_NR_ID,
                claim_id: str = utils.CLAIM_ID,
                phone: dict = None,
        ):
            claim = {'id': claim_id, 'phone': phone}
            self.claims[claim_id] = claim
            self.order_claims[order_nr].append(claim)

    context = Context()

    @mockserver.json_handler('eats-core-orders/api/v1/orders')
    def core_orders(request):
        assert 'limit' in request.query
        assert 'offset' in request.query
        for key, value in context.core_headers.items():
            assert key in request.headers
            assert value == request.headers[key]
        return mockserver.make_response(
            status=context.core_response_code, json=context.orders,
        )

    @mockserver.json_handler(
        'eats-core-orders-superapp/internal-api/v1/orders/retrieve',
    )
    def superapp_orders(request):
        assert context.exp_superapp_request_body == request.json
        return mockserver.make_response(
            status=context.superapp_response_code,
            json=context.superapp_response,
        )

    @mockserver.json_handler(
        'eats-retail-order-history/eats/v1/'
        + 'retail-order-history/customer/order/history',
    )
    def retail_orders(request):
        assert 'order_nr' in request.query
        return mockserver.make_response(
            status=context.retail_response_code,
            json=context.retail_response,
            headers=context.retail_response_headers,
        )

    @mockserver.json_handler(
        'persey-payments/internal/v1/charity/multibrand/ride_donations',
    )
    def ride_donations(request):
        if context.persey_response_code != 200:
            return mockserver.make_response(
                status=context.persey_response_code,
            )
        assert (
            context.core_response_code == 200
        )  # TODO: add more for every service we get orders from
        persey_brands = ['eats', 'lavka']
        assert 'brands' in request.json
        assert len(request.json['brands']) == 2
        for brand_id in range(2):
            assert (
                request.json['brands'][brand_id]['brand']
                == persey_brands[brand_id]
            )
            assert 'order_ids' in request.json['brands'][brand_id]
            assert (
                context.exp_order_ids[brand_id]
                == request.json['brands'][brand_id]['order_ids']
            )
        return mockserver.make_response(
            status=context.persey_response_code,
            json={'brands': context.brands_response},
        )

    @mockserver.json_handler(
        'eats-feedback/internal/eats-feedback/v1/'
        'get-feedbacks-for-orders-history',
    )
    def feedbacks(request):
        return mockserver.make_response(
            status=context.feedbacks_response_code,
            json={'feedbacks': context.feedbacks},
        )

    @mockserver.json_handler('eats-receipts/api/v1/receipts')
    def receipts(request):
        return mockserver.make_response(
            status=context.receipts_code,
            json={'receipts': context.receipts_data},
        )

    @mockserver.json_handler(
        f'eats-core-orders/internal-api/v1/order/{utils.ORDER_NR_ID}/metainfo',
    )
    def core_order_info(request):
        order = context.user_orders.get(utils.ORDER_NR_ID)
        response_body = {
            'order_nr': utils.ORDER_NR_ID,
            'location_latitude': order['lat'],
            'location_longitude': order['lon'],
            'business_type': order['bus_type'],
            'city': order['city'],
            'street': order['street'],
            'is_asap': True,
            'status': order['status'],
            'place_id': utils.PLACE_ID,
            'region_id': '1',
            'place_delivery_zone_id': '1',
            'app': 'web',
            'order_status_history': {
                'created_at': utils.SAMPLE_TIME_CONVERTED,
            },
            'order_user_information': {'eater_id': '21'},
        }
        return mockserver.make_response(status=200, json=response_body)

    @mockserver.json_handler(
        '/eats-core-order-revision/internal-api/v1/order-revision/list',
    )
    def mock_core_revision_list(request):
        assert request.method == 'GET'
        order_id = request.query['order_id']
        if order_id not in context.order_revisions:
            return mockserver.make_response(status=404)
        order_revisions = context.order_revisions[order_id]
        return mockserver.make_response(
            status=200,
            json={
                'order_id': order_id,
                'revisions': [
                    {'revision_id': revision_id}
                    for revision_id in order_revisions.keys()
                ],
            },
        )

    @mockserver.json_handler(
        '/eats-core-order-revision/internal-api/v1'
        '/order-revision/customer-services/details',
    )
    def mock_core_revision_details(request):
        assert request.method == 'POST'
        order_id = request.json['order_id']
        revision_id = request.json['revision_id']
        if revision_id not in context.order_revisions.get(order_id, {}):
            return mockserver.make_response(status=404)
        return mockserver.make_response(
            status=200,
            json={
                'revision_id': revision_id,
                'customer_services': context.order_revisions[order_id][
                    revision_id
                ],
                'created_at': utils.SAMPLE_TIME_CONVERTED,
            },
        )

    @mockserver.json_handler(
        '/eats-order-revision/v1/revision/latest/customer-services/details',
    )
    def mock_service_revision_details(request):
        assert request.method == 'POST'
        order_id = request.json['order_id']
        # last default revision
        list_ids = list(context.order_revisions[order_id])
        last_revision_id = list_ids[-1]
        return mockserver.make_response(
            status=200,
            json={
                'origin_revision_id': last_revision_id,
                'customer_services': context.order_revisions[order_id][
                    last_revision_id
                ],
                'created_at': utils.SAMPLE_TIME_CONVERTED,
            },
        )

    @mockserver.json_handler(
        '/eats-catalog-storage/internal/eats-catalog-storage'
        '/v1/places/retrieve-by-ids',
    )
    def mock_catalog_retrieve_places(request):
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
        }
        place_id = str(place_ids[0])
        if place_id not in context.place_info:
            return mockserver.make_response(
                status=200,
                json={'places': [], 'not_found_place_ids': [int(place_id)]},
            )
        return mockserver.make_response(
            status=200,
            json={
                'places': [context.place_info[place_id]],
                'not_found_place_ids': [],
            },
        )

    @mockserver.json_handler(
        '/eats-core-restapp/v1/eats-restapp-menu/place-menu',
    )
    def mock_place_assortment_details(request):
        assert request.method == 'GET'
        place_id = request.query['place_id']
        if place_id not in context.place_assortment:
            return mockserver.make_response(
                status=404,
                json={
                    'isSuccess': False,
                    'statusCode': 404,
                    'type': 'not_found',
                },
            )
        place_assortment = context.place_assortment[place_id]
        return mockserver.make_response(
            status=200,
            json={
                'is_success': True,
                'payload': {
                    'menu': {'categories': [], 'items': place_assortment},
                },
            },
        )

    @mockserver.json_handler(
        '/eats-orders-tracking/internal/'
        'eats-orders-tracking/v1/get-claim-by-order-nr',
    )
    def mock_tracking_claims(request):
        assert request.method == 'GET'
        order_nr = request.query['order_nr']
        return mockserver.make_response(
            status=200,
            json={
                'order_nr': order_nr,
                'claim_id': utils.CLAIM_ID,
                'claim_alias': '124',
            },
        )

    @mockserver.json_handler(
        '/cargo-claims/api/integration/v1/driver-voiceforwarding',
    )
    def mock_cargo_driver_vfwd(request):
        assert request.method == 'POST'
        claim = context.claims.get(request.json['claim_id'])

        if not claim or not claim['phone']:
            return mockserver.make_response(
                status=404,
                json={'code': 'not_found', 'message': 'claim not found'},
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

    @mockserver.json_handler(bdu_orders_utils.RESTAPP_URL)
    def mock_place_history_details(request):
        assert request.method == 'POST'
        place_id = request.json['places'][0]['place_id']
        if place_id not in context.place_assortment:
            return mockserver.make_response(
                status=404,
                json={
                    'isSuccess': False,
                    'statusCode': 400,
                    'type': 'bad_request',
                    'context': 'some_context',
                },
            )
        place_assortment = []
        for item in context.place_assortment[place_id]:
            result_item = {
                'origin_id': item['id'],
                'name': item['name'],
                'images': [],
            }
            for image in item['images']:
                result_item['images'].append(image['url'])
            place_assortment.append(result_item)

        return mockserver.make_response(
            status=200,
            json={
                'places_items': [
                    {'place_id': place_id, 'items': place_assortment},
                ],
            },
        )

    context.mock_core_orders = core_orders
    context.mock_ride_donations = ride_donations
    context.mock_superapp_orders = superapp_orders
    context.mock_retail_orders = retail_orders
    context.mock_core_order_info = core_order_info
    context.mock_feedbacks = feedbacks
    context.mock_receipts = receipts
    context.mock_core_revision_list = mock_core_revision_list
    context.mock_core_revision_details = mock_core_revision_details
    context.mock_service_revision_details = mock_service_revision_details
    context.mock_catalog_retrieve_places = mock_catalog_retrieve_places
    context.mock_place_assortment_details = mock_place_assortment_details
    context.mock_place_history_details = mock_place_history_details
    context.mock_cargo_driver_vfwd = mock_cargo_driver_vfwd
    context.mock_tracking_claims = mock_tracking_claims
    return context


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


@pytest.fixture(name='assert_response_body')
def _assert_response_body():
    def do_assert_response_body(actual_response, expected_response):
        courier_phone = expected_response.get('forwarded_courier_phone')
        status_for_customer = expected_response.get('status_for_customer')
        if courier_phone and status_for_customer:
            status_for_customer = utils.StatusForCustomer[status_for_customer]
            if status_for_customer not in [
                    utils.StatusForCustomer.in_delivery,
                    utils.StatusForCustomer.arrived_to_customer,
            ]:
                del expected_response['forwarded_courier_phone']
        assert utils.format_response(actual_response) == expected_response

    return do_assert_response_body


@pytest.fixture(name='assert_response')
def _assert_response(taxi_eats_orders_info, assert_response_body):
    async def do_assert_response(expected_status, expected_response=None):
        response = await taxi_eats_orders_info.get(
            '/eats/v1/orders-info/v1/order',
            params={'order_nr': utils.ORDER_NR_ID},
            headers=utils.get_auth_headers(),
        )
        assert response.status_code == expected_status
        if expected_response is not None:
            assert_response_body(response.json(), expected_response)
        return response

    return do_assert_response


@pytest.fixture()
def assert_mocks(local_services):
    def do_assert_mocks(
            core_orders_retrieve_called,
            core_revision_list_called,
            core_revision_details_called,
            place_assortment_details_called,
            catalog_retrieve_places_called,
            tracking_claims_called,
            cargo_driver_vfwd_called,
    ):
        assert (
            local_services.mock_core_order_info.times_called
            == core_orders_retrieve_called
        )
        assert (
            local_services.mock_core_revision_list.times_called
            == core_revision_list_called
        )
        assert (
            local_services.mock_core_revision_details.times_called
            == core_revision_details_called
        )
        assert (
            local_services.mock_place_history_details.times_called
            == place_assortment_details_called
        )
        assert (
            local_services.mock_catalog_retrieve_places.times_called
            == catalog_retrieve_places_called
        )
        assert (
            local_services.mock_tracking_claims.times_called
            == tracking_claims_called
        )
        assert (
            local_services.mock_cargo_driver_vfwd.times_called
            == cargo_driver_vfwd_called
        )

    return do_assert_mocks


@pytest.fixture(name='mock_catalog_storage_dummy')
def _mock_catalog_dummy(mockserver):
    @mockserver.json_handler(bdu_orders_utils.CATALOG_STORAGE_URL)
    def mock(request):
        return mockserver.make_response(
            json=bdu_orders_utils.generate_catalog_info(
                [
                    {
                        'id': bdu_orders_utils.PLACE_ID,
                        'name': bdu_orders_utils.PLACE_NAME,
                    },
                ],
                [],
            ),
            status=200,
        )

    return mock


@pytest.fixture(name='mock_metainfo_dummy')
def _mock_metainfo_dummy(mockserver):
    @mockserver.json_handler(bdu_orders_utils.METAINFO_URL)
    def mock(request):
        return mockserver.make_response(
            json=bdu_orders_utils.generate_metainfo_orders(
                [
                    {
                        'order_nr': bdu_orders_utils.DEFAULT_ORDER_NR,
                        'bus_type': 'restaurant',
                        'status': 'confirmed',
                        'shipping_type': 'pickup',
                    },
                ],
            ),
            status=200,
        )

    return mock


@pytest.fixture(name='mock_orders_tracking_dummy')
def _mock_orders_tracking_dummy(mockserver):
    @mockserver.json_handler(bdu_orders_utils.TRACKING_URL)
    def mock(request):
        return mockserver.make_response(status=200, json={'orders': []})

    return mock


@pytest.fixture(name='mock_feedback_dummy')
def _mock_feedback_dummy(mockserver):
    @mockserver.json_handler(bdu_orders_utils.FEEDBACK_URL)
    def mock(request):
        return mockserver.make_response(
            status=200,
            json={
                'feedbacks': [
                    {
                        'has_feedback': True,
                        'status': 'noshow',
                        'order_nr': bdu_orders_utils.DEFAULT_ORDER_NR,
                        'is_feedback_needed': False,
                    },
                ],
            },
        )

    return mock


@pytest.fixture(name='mock_restapp_dummy')
def _mock_restapp_dummy(mockserver):
    @mockserver.json_handler(bdu_orders_utils.RESTAPP_URL)
    def mock(request):
        assert request.method == 'POST'
        return mockserver.make_response(
            status=200,
            json={
                'places_items': [
                    {
                        'place_id': bdu_orders_utils.PLACE_ID,
                        'items': [
                            {
                                'origin_id': bdu_orders_utils.ORIGIN_ID,
                                'name': 'name',
                                'images': [
                                    {'url': 'image_url_front'},
                                    {'url': 'image_url_back'},
                                ],
                            },
                        ],
                    },
                ],
            },
        )

    return mock


@pytest.fixture(name='mock_retail_update_dummy')
def _mock_retail_update_dummy(mockserver):
    @mockserver.json_handler(bdu_orders_utils.RETAIL_UPDATE_URL)
    def mock(request):
        assert request.method == 'POST'
        assert 'order_nrs' in request.json
        return mockserver.make_response(
            status=200,
            json={
                'orders': [
                    {
                        'order_nr': bdu_orders_utils.DEFAULT_ORDER_NR,
                        'total_amount': '384',
                        'items': [
                            {
                                'origin_id': (
                                    bdu_orders_utils.ORIGIN_ID_WITH_CHANGES
                                ),
                                'name': 'name',
                                'images_url_template': [
                                    'image_url_front',
                                    'image_url_back',
                                ],
                            },
                        ],
                    },
                ],
            },
        )

    return mock


@pytest.fixture(name='mock_last_revisions_dummy')
def _mock_last_revisions_dummy(mockserver, load_json):
    @mockserver.json_handler(bdu_orders_utils.REVISIONS_URL)
    def mock(request):
        assert request.method == 'POST'
        assert 'order_id' in request.json
        return mockserver.make_response(
            status=200, json=load_json('customer_service.json'),
        )

    return mock


@pytest.fixture(name='mock_donations_bdu_orders')
def _mock_donations_bdu_orders(mockserver):
    @mockserver.json_handler(
        'persey-payments/internal/v1/charity/multibrand/ride_donations',
    )
    def ride_donations(request):
        return mockserver.make_response(
            status=200,
            json={
                'brands': [
                    {
                        'brand': 'eats',
                        'orders': [
                            {
                                'order_id': 'finished_donation',
                                'donation': {
                                    'status': 'finished',
                                    'amount_info': {
                                        'amount': '5',
                                        'currency_code': 'RUB',
                                        'currency_sign': '₽',
                                    },
                                },
                            },
                            {
                                'order_id': 'unauthorized_donation',
                                'donation': {
                                    'status': 'unauthorized',
                                    'amount_info': {
                                        'amount': '5',
                                        'currency_code': 'RUB',
                                        'currency_sign': '₽',
                                    },
                                },
                            },
                        ],
                    },
                    {
                        'brand': 'lavka',
                        'orders': [
                            {
                                'order_id': 'finished_donation_grocery',
                                'donation': {
                                    'status': 'finished',
                                    'amount_info': {
                                        'amount': '3',
                                        'currency_code': 'RUB',
                                        'currency_sign': '₽',
                                    },
                                },
                            },
                            {
                                'order_id': 'unauthorized_donation_grocery',
                                'donation': {
                                    'status': 'unauthorized',
                                    'amount_info': {
                                        'amount': '3',
                                        'currency_code': 'RUB',
                                        'currency_sign': '₽',
                                    },
                                },
                            },
                        ],
                    },
                ],
            },
        )

    return ride_donations


@pytest.fixture
def pg_cursor(pgsql):
    return pgsql['eats_orders_info'].cursor()


@pytest.fixture
def pg_realdict_cursor(pgsql):
    return pgsql['eats_orders_info'].cursor(
        cursor_factory=extras.RealDictCursor,
    )
