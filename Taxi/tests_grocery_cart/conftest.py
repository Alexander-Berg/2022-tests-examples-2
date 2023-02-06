# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=redefined-outer-name
import dataclasses
import datetime
import decimal
import typing

from grocery_cart_plugins import *  # noqa: F403 F401
import pytest
import pytz

from tests_grocery_cart import common
from tests_grocery_cart import models
from tests_grocery_cart.plugins import keys


class CartControl:
    HttpError = common.CartHttpError

    def __init__(
            self,
            *,
            cart_id=None,
            cart_version=None,
            offer_id='some_offer_id',
            headers=None,
            child_cart_id=None,
            taxi_grocery_cart,
            overlord_catalog,
            fetch_cart,
            update_cart_db,
            fetch_items,
            upsert_items,
            set_items_pricing,
            additional_data=None,
    ):
        self._taxi_grocery_cart = taxi_grocery_cart
        self._overlord_catalog = overlord_catalog
        self._fetch_cart = fetch_cart
        self._update_cart_db = update_cart_db
        self._fetch_items = fetch_items
        self._upsert_items = upsert_items
        self._set_items_pricing = set_items_pricing
        self.cart_id = cart_id
        self.cart_version = cart_version
        self.offer_id = offer_id
        self.position = keys.DEFAULT_POSITION
        self.child_cart_id = child_cart_id
        if headers is not None:
            self._base_headers = headers
        else:
            self._base_headers = common.TAXI_HEADERS
        self.additional_data = keys.DEFAULT_ADDITIONAL_DATA

    def fetch_db(self, cart_id=None):
        assert self.cart_id is not None or cart_id is not None
        return self._fetch_cart(
            cart_id if cart_id is not None else self.cart_id,
        )

    def fetch_items(self, cart_id=None):
        return self._fetch_items(self.cart_id or cart_id)

    def upsert_items(self, items: typing.List[models.CartItem]):
        self._upsert_items(self.cart_id, items)

    def set_items_pricing(self, items_pricing):
        self._set_items_pricing(self.cart_id, items_pricing)

    def unsubscribe(self):
        self.cart_id = None
        self.cart_version = None

    def update_db(self, cart_id=None, **kwargs):
        if cart_id is None:
            cart_id = self.cart_id

        assert cart_id is not None

        return self._update_cart_db(cart_id=cart_id, **kwargs)

    async def init(
            self,
            products,
            currency='RUB',
            delivery_type=None,
            headers=None,
            legal_restrictions=None,
    ):
        assert self.cart_version is None

        items = self._get_cart_items(products, currency=currency)

        for item in items:
            self._overlord_catalog.add_product(
                product_id=item['id'],
                price=item['price'],
                legal_restrictions=legal_restrictions,
            )

        return await self._modify_impl(items, delivery_type, headers)

    async def retrieve(
            self,
            *,
            headers=None,
            allow_checked_out=False,
            disable_migration=None,
    ):
        request = self._build_request()
        if allow_checked_out:
            request['allow_checked_out'] = allow_checked_out
        if disable_migration is not None:
            request['disable_migration'] = disable_migration
        response = await self._taxi_grocery_cart.post(
            '/lavka/v1/cart/v1/retrieve',
            json=request,
            headers=self._build_headers(headers),
        )
        return self._handle_response(response)

    async def internal_retrieve_raw(self, *, headers=None):
        response = await self._taxi_grocery_cart.post(
            '/internal/v1/cart/retrieve/raw',
            json={'cart_id': self.cart_id, 'source': 'SQL'},
            headers=headers,
        )
        return self._handle_response(response)

    async def modify(
            self, products, currency='RUB', delivery_type=None, headers=None,
    ):
        items = self._get_cart_items(products, currency=currency)
        return await self._modify_impl(items, delivery_type, headers)

    async def create_shared(self, cart_id=None, status_code=200):
        if cart_id is None:
            cart_id = self.cart_id
        response = await self._taxi_grocery_cart.post(
            '/lavka/v1/cart/v1/shared/create', json={'cart_id': cart_id},
        )
        assert response.status_code == status_code
        return response.json()

    async def checkout(
            self,
            *,
            headers=None,
            required_status_code=200,
            cashback_to_pay=None,
            grocery_flow_version=None,
            order_flow_version=None,
            payment_method=None,
            service_fee=None,
            tips_payment_flow=None,
            cart_id=None,
            cart_version=None,
    ):
        if headers is None:
            headers = common.TAXI_HEADERS
        json = {
            'position': keys.DEFAULT_POSITION,
            'cart_id': cart_id or self.cart_id,
            'cart_version': cart_version or self.cart_version,
            'offer_id': self.offer_id,
            'cashback_to_pay': cashback_to_pay,
            'grocery_flow_version': grocery_flow_version,
            'order_flow_version': order_flow_version,
            'payment_method': payment_method,
            'service_fee': service_fee,
            'tips_payment_flow': tips_payment_flow,
        }
        response = await self._taxi_grocery_cart.post(
            '/internal/v2/cart/checkout', headers=headers, json=json,
        )
        assert response.status_code == required_status_code
        return response.json()

    async def apply_promocode(
            self, promocode, *, headers=None, additional_data=None,
    ):
        if additional_data is None:
            additional_data = self.additional_data
        response = await self._taxi_grocery_cart.post(
            '/lavka/v1/cart/v1/apply-promocode',
            json=self._build_request(
                promocode=promocode, additional_data=additional_data,
            ),
            headers=self._build_headers(
                headers,
                extra={
                    'X-Idempotency-Token': (
                        common.APPLY_PROMOCODE_IDEMPOTENCY_TOKEN
                    ),
                    'User-Agent': keys.DEFAULT_USER_AGENT,
                },
            ),
        )
        return self._handle_response(response)

    async def apply_promocode_v2(
            self,
            promocode,
            *,
            headers=None,
            position=None,
            cart_version=None,
            additional_data=None,
    ):
        if position is None:
            position = self.position
        if cart_version is None:
            cart_version = self.cart_version
        if additional_data is None:
            additional_data = self.additional_data
        response = await self._taxi_grocery_cart.post(
            '/lavka/v1/cart/v2/apply-promocode',
            json=self._build_request(
                promocode=promocode,
                position=position,
                cart_version=cart_version,
                additional_data=additional_data,
            ),
            headers=self._build_headers(
                headers,
                extra={
                    'X-Idempotency-Token': (
                        common.APPLY_PROMOCODE_IDEMPOTENCY_TOKEN
                    ),
                    'User-Agent': keys.DEFAULT_USER_AGENT,
                },
            ),
        )
        return self._handle_response(response)

    async def promocodes_list(
            self,
            *,
            headers=None,
            required_status=200,
            include_cart_info=True,
            additional_data=None,
    ):
        request = {'position': self.position, 'offer_id': self.offer_id}
        if self.cart_id is not None and include_cart_info:
            assert self.cart_version is not None
            request['cart_id'] = self.cart_id
            request['cart_version'] = self.cart_version
        if additional_data is None:
            additional_data = self.additional_data
        request['additional_data'] = additional_data

        response = await self._taxi_grocery_cart.post(
            '/lavka/v1/cart/v1/promocodes-list',
            json=request,
            headers=self._build_headers(
                headers,
                extra={
                    'X-Idempotency-Token': (
                        common.PROMOCODES_LIST_IDEMPOTENCY_TOKEN
                    ),
                    'User-Agent': keys.DEFAULT_USER_AGENT,
                },
            ),
        )
        assert response.status_code == required_status

        return response.json()

    async def set_payment(
            self,
            payment_type,
            payment_id=None,
            payment_meta=None,
            headers=None,
    ):
        if headers is None:
            headers = common.TAXI_HEADERS
        response = await self._taxi_grocery_cart.post(
            '/lavka/v1/cart/v1/set-payment',
            json={
                'position': keys.DEFAULT_POSITION,
                'cart_id': self.cart_id,
                'offer_id': self.offer_id,
                'payment_method': {
                    'type': payment_type,
                    'id': payment_id,
                    'meta': payment_meta,
                },
                'cart_version': self.cart_version,
            },
            headers=headers,
        )
        return self._handle_response(response)

    async def set_cashback_flow(self, flow, headers=None):
        if headers is None:
            headers = common.TAXI_HEADERS
        response = await self._taxi_grocery_cart.post(
            '/lavka/v1/cart/v1/set-cashback-flow',
            json={
                'position': keys.DEFAULT_POSITION,
                'cart_id': self.cart_id,
                'offer_id': self.offer_id,
                'cashback_flow': flow,
                'cart_version': self.cart_version,
            },
            headers=headers,
        )
        return self._handle_response(response)

    async def set_order_id(self, order_id):
        response = await self._taxi_grocery_cart.post(
            '/internal/v1/cart/set-order-id',
            json={'cart_id': self.cart_id, 'order_id': order_id},
        )
        if response.status_code != 200:
            raise common.CartHttpError(response)
        return response

    async def set_tips(self, tips, headers=None):
        if headers is None:
            headers = common.TAXI_HEADERS
        response = await self._taxi_grocery_cart.post(
            '/lavka/v1/cart/v1/set-tips',
            json={
                'cart_id': self.cart_id,
                'cart_version': self.cart_version,
                'tips': tips,
            },
            headers=headers,
        )
        return self._handle_response(response)

    async def set_tips_v2(
            self,
            tips,
            cart_id=None,
            cart_version=None,
            additional_data=None,
            headers=None,
            status_code=200,
    ):
        if headers is None:
            headers = {
                **common.TAXI_HEADERS,
                'User-Agent': keys.DEFAULT_USER_AGENT,
            }
        if cart_version is None:
            cart_version = self.cart_version
        if cart_id is None:
            cart_id = self.cart_id
        if additional_data is None:
            additional_data = self.additional_data

        response = await self._taxi_grocery_cart.post(
            '/lavka/v1/cart/v2/set-tips',
            json={
                'position': keys.DEFAULT_POSITION,
                'cart_id': cart_id,
                'cart_version': cart_version,
                'tips': tips,
                'additional_data': additional_data,
            },
            headers=headers,
        )

        if 'cart_version' in response.json():
            self.cart_version = response.json()['cart_version']

        assert response.status_code == status_code
        return response.json()

    async def accept_delivery_cost(self, delivery_cost, headers=None):
        if headers is None:
            headers = common.TAXI_HEADERS
        response = await self._taxi_grocery_cart.post(
            '/lavka/v1/cart/v1/accept-delivery-cost',
            headers=headers,
            json=self._build_request(delivery_cost=delivery_cost),
        )
        self._check_status_code(response)
        self.cart_version += 1

    async def takeout_load_ids(self, yandex_uid, till_dt, headers=None):
        response = await self._taxi_grocery_cart.post(
            '/internal/v1/cart/takeout/load-ids',
            json={'yandex_uid': yandex_uid, 'till_dt': till_dt},
            headers=headers,
        )
        self._check_status_code(response)
        return response.json()

    async def takeout_load(self, cart_id, status_code=200, headers=None):
        response = await self._taxi_grocery_cart.post(
            '/internal/v1/cart/takeout/load',
            json={'cart_id': cart_id},
            headers=headers,
        )

        assert response.status_code == status_code
        return response.json()

    async def takeout_delete(
            self, cart_id, anonym_id, status_code=200, headers=None,
    ):
        response = await self._taxi_grocery_cart.post(
            '/internal/v1/cart/takeout/delete',
            json={'cart_id': cart_id, 'anonym_id': anonym_id},
            headers=headers,
        )

        assert response.status_code == status_code

    async def takeout_status(self, yandex_uids, till_dt, headers=None):
        response = await self._taxi_grocery_cart.post(
            '/internal/v1/cart/takeout/status',
            json={'yandex_uids': yandex_uids, 'till_dt': till_dt},
            headers=headers,
        )
        self._check_status_code(response)
        return response.json()

    async def invalidate_caches(self):
        await self._taxi_grocery_cart.invalidate_caches()

    @staticmethod
    def _get_cart_items(products, currency):
        if isinstance(products, list):
            products = {product_key: {} for product_key in products}
        result = []
        for product_key, params in products.items():
            item = {
                'id': product_key,
                'price': str(
                    params.get('p', params.get('price', keys.DEFAULT_PRICE)),
                ),
                'quantity': str(
                    params.get(
                        'q', params.get('quantity', common.DEFAULT_QUANTITY),
                    ),
                ),
                'currency': currency,
            }
            cashback = params.get('c', params.get('cashback', None))
            if cashback is not None:
                item['cashback'] = str(cashback)
            result.append(item)
        return result

    async def _modify_impl(self, items, delivery_type, headers):
        params = {}
        if delivery_type is not None:
            params['delivery_type'] = delivery_type
        response = await self._taxi_grocery_cart.post(
            '/lavka/v1/cart/v1/update',
            json=self._build_request(items=items, **params),
            headers=self._build_headers(headers),
        )
        return self._handle_response(response)

    def _build_headers(self, headers, extra=None):
        return {**self._base_headers, **(extra or {}), **(headers or {})}

    def _build_request(self, **extra):
        request = {'position': self.position, 'offer_id': self.offer_id}
        if self.cart_id is not None:
            assert self.cart_version is not None
            request['cart_id'] = self.cart_id
            request['cart_version'] = self.cart_version
        print('request: ', {**request, **extra})
        return {**request, **extra}

    def _handle_response(self, response):
        self._check_status_code(response)
        response_json = response.json()
        self.cart_id = response_json['cart_id']
        self.cart_version = response_json['cart_version']
        return response_json

    @staticmethod
    def _check_status_code(response):
        if response.status_code != 200:
            raise common.CartHttpError(response)


@pytest.fixture
def update_cart_db(pgsql):
    def _update_cart_db(cart_id, **kwargs):
        cursor = pgsql['grocery_cart'].cursor()
        for cart_property, value in kwargs.items():
            if value is not None:
                cursor.execute(
                    common.SET_CART_PROPERTY.format(cart_property),
                    (value, cart_id),
                )

    return _update_cart_db


@pytest.fixture
def fetch_cart(pgsql):
    def _fetch_cart(cart_id):
        cursor = pgsql['grocery_cart'].cursor()
        cursor.execute(common.SELECT_CART_SQL, (cart_id,))
        row = cursor.fetchone()
        if row is None:
            raise RuntimeError(f'Cart {cart_id} not found')
        cart = models.Cart(
            cart_id=row[0],
            cart_version=row[1],
            updated=row[3].astimezone(pytz.UTC).replace(tzinfo=None),
            idempotency_token=row[4],
            promocode=row[5],
            user_type=row[6],
            user_id=row[7],
            session=row[8],
            payment_method_type=row[9],
            payment_method_id=row[10],
            payment_method_meta=row[11],
            status=row[12],
            delivery_type=row[13],
            cashback_flow=row[14],
            delivery_cost=row[15],
            child_cart_id=row[16],
            tips_amount=row[17],
            tips_amount_type=row[18],
            depot_id=row[19],
            timeslot_start=row[20],
            timeslot_end=row[21],
            timeslot_request_kind=row[22],
            personal_phone_id=row[23],
            yandex_uid=row[24],
            bound_uids=row[25],
            bound_sessions=row[26],
            anonym_id=row[27],
        )
        cursor.execute(common.SELECT_CHECKOUT_DATA_SQL, (cart_id,))
        row = cursor.fetchone()
        if row is None:
            return cart
        cart.promocode_discount = row[1]
        cart.calculation_log = row[2]
        cart.items_pricing = row[3]
        cart.cashback_to_pay = row[4]
        cart.service_fee = row[5]
        return cart

    return _fetch_cart


@pytest.fixture
def fetch_items(pgsql):
    def _fetch_items(cart_id):
        cursor = pgsql['grocery_cart'].cursor()
        cursor.execute(common.SELECT_ITEMS_SQL, (cart_id,))
        items_pg = cursor.fetchall()

        items = []
        for item_pg in items_pg:
            items.append(models.CartItem(*item_pg))

        return items

    return _fetch_items


@pytest.fixture
def upsert_items(pgsql):
    def _upsert_items(cart_id, items: typing.List[models.CartItem]):
        cursor = pgsql['grocery_cart'].cursor()
        for item in items:
            cursor.execute(
                common.UPSERT_ITEM_SQL,
                (
                    cart_id,
                    item.item_id,
                    item.price,
                    item.quantity,
                    item.currency,
                    item.reserved,
                ),
            )

    return _upsert_items


@pytest.fixture
def set_items_pricing(pgsql):
    def _set_items_pricing(cart_id, items_pricing):
        cursor = pgsql['grocery_cart'].cursor()
        cursor.execute(
            common.SET_ITEMS_PRICING_FIELD_SQL, (items_pricing, cart_id),
        )

    return _set_items_pricing


@pytest.fixture
def cart_factory(
        taxi_grocery_cart,
        overlord_catalog,
        fetch_cart,
        update_cart_db,
        fetch_items,
        upsert_items,
        set_items_pricing,
):
    def factory(**kwargs):
        return CartControl(
            taxi_grocery_cart=taxi_grocery_cart,
            overlord_catalog=overlord_catalog,
            fetch_cart=fetch_cart,
            update_cart_db=update_cart_db,
            fetch_items=fetch_items,
            upsert_items=upsert_items,
            set_items_pricing=set_items_pricing,
            **kwargs,
        )

    return factory


@pytest.fixture(name='cart')
def mock_cart(cart_factory):
    return cart_factory()


@pytest.fixture
def fetch_promocode(pgsql):
    def _fetch_promocode(cart_id):
        cursor = pgsql['grocery_cart'].cursor()
        cursor.execute(common.SELECT_PROMOCODE_SQL, (cart_id,))
        row = cursor.fetchone()
        if row is None:
            return None

        promocode = models.CartPromocode(
            cart_id=row[0],
            promocode=row[1],
            currency=row[2],
            source=row[3],
            valid=row[4],
            discount=row[5],
            error_code=row[6],
            properties=row[7],
        )

        return promocode

    return _fetch_promocode


@pytest.fixture(name='grocery_dispatch', autouse=True)
def mock_grocery_dispatch(mockserver):
    @mockserver.json_handler(
        '/grocery-dispatch/internal/dispatch/v1/check-price',
    )
    def _mock_eta_prediction(request):
        return {'price': 123.56}


@pytest.fixture(name='grocery_depots', autouse=True)
def mock_grocery_depots(grocery_depots):
    grocery_depots.add_depot(
        int(keys.DEFAULT_LEGACY_DEPOT_ID),
        legacy_depot_id=keys.DEFAULT_LEGACY_DEPOT_ID,
        depot_id=keys.DEFAULT_WMS_DEPOT_ID,
        location=keys.DEFAULT_DEPOT_LOCATION_OBJ,
    )
    return grocery_depots
