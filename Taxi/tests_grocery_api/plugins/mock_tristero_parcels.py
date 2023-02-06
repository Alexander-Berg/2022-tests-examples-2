from typing import Any
from typing import Dict

import pytest


class Order:
    def __init__(
            self,
            order_id: str,
            customer_address: str = None,
            customer_location: list = None,
            ref_order: str = '',
            token: str = '',
            vendor: str = '',
            depot_id: str = '',
            status: str = '',
            delivery_date: str = '',
            image_url_order_with_groceries: str = '',
            uid: str = '',
            timeslot_start: str = None,
            timeslot_end: str = None,
            alternative_timeslots: list = None,
    ):
        timeslot = None
        if (timeslot_start is not None) and (timeslot_end is not None):
            timeslot = {'start': timeslot_start, 'end': timeslot_end}
        self._data: Dict[str, Any] = {
            'order_id': order_id,
            'customer_address': customer_address,
            'customer_location': customer_location,
            'ref_order': ref_order,
            'token': token,
            'vendor': vendor,
            'depot_id': depot_id,
            'status': status,
            'delivery_date': delivery_date,
            'image_url_order_with_groceries': image_url_order_with_groceries,
            'parcels': [],
            'uid': uid,
            'timeslot': timeslot,
            'alternative_timeslots': alternative_timeslots,
        }

    def add_parcel(
            self,
            parcel_id: str,
            status: str = '',
            description: str = '',
            title_tanker_key: str = '',
            title: str = '',
            image_url_template: str = '',
            quantity_limit: str = '1',
            can_left_at_door: bool = True,
            state_meta: dict = None,
    ):
        self._data['parcels'].append(
            {
                'parcel_id': parcel_id,
                'status': status,
                'description': description,
                'title_tanker_key': title_tanker_key,
                'title': title,
                'image_url_template': image_url_template,
                'quantity_limit': quantity_limit,
                'can_left_at_door': can_left_at_door,
                'state_meta': state_meta if state_meta is not None else {},
            },
        )

    @property
    def data(self):
        return self._data


class Category:
    def __init__(
            self,
            category_id: str,
            title_tanker_key: str = '',
            image_url_template: str = '',
    ):
        self._data: Dict[str, Any] = {
            'category_id': category_id,
            'title_tanker_key': title_tanker_key,
            'image_url_template': image_url_template,
        }

    @property
    def data(self):
        return self._data


@pytest.fixture(name='tristero_parcels', autouse=True)
def mock_tristero_parcels(mockserver):
    class Context:
        def __init__(self):
            self._orders = []
            self._category = None
            self._yandex_uid = None
            self._check_request_data = {}

        def add_order(
                self,
                order_id: str,
                customer_address: str = None,
                customer_location: list = None,
                ref_order: str = '',
                token: str = '',
                vendor: str = '',
                depot_id: str = '',
                status: str = '',
                delivery_date: str = '',
                image_url_order_with_groceries: str = '',
                uid: str = '',
                timeslot_start: str = None,
                timeslot_end: str = None,
                alternative_timeslots: list = None,
        ):
            order = Order(
                order_id=order_id,
                customer_address=customer_address,
                customer_location=customer_location,
                ref_order=ref_order,
                token=token,
                vendor=vendor,
                depot_id=depot_id,
                status=status,
                delivery_date=delivery_date,
                image_url_order_with_groceries=image_url_order_with_groceries,
                uid=uid,
                timeslot_start=timeslot_start,
                timeslot_end=timeslot_end,
                alternative_timeslots=alternative_timeslots,
            )
            self._orders.append(order)
            return order

        @property
        def orders(self):
            return self._orders

        def set_category(
                self,
                category_id: str,
                title_tanker_key: str = '',
                image_url_template: str = '',
        ):
            self._category = Category(
                category_id=category_id,
                title_tanker_key=title_tanker_key,
                image_url_template=image_url_template,
            )

        @property
        def category(self):
            return self._category

        def set_yandex_uid(self, yandex_uid: str):
            self._yandex_uid = yandex_uid

        @property
        def yandex_uid(self):
            return self._yandex_uid

        @property
        def check_request_data(self):
            return self._check_request_data

        def check_request(self, *, handler, json, params, headers):
            self._check_request_data[handler] = {
                'json': json,
                'params': params,
                'headers': headers,
            }

        @property
        def retrieve_orders_times_called(self):
            return retrieve_orders.times_called

        @property
        def retrieve_orders_v2_times_called(self):
            return _retrieve_orders_v2.times_called

        @property
        def retrieve_times_called(self):
            return retrieve.times_called

        @property
        def order_info_times_called(self):
            return order_info.times_called

        @property
        def order_make_times_called(self):
            return order_make.times_called

        @property
        def order_make_has_calls(self):
            return order_make.has_calls

        @property
        def order_track_times_called(self):
            return order_track.times_called

        @property
        def order_track_has_calls(self):
            return order_track.has_calls

    @mockserver.json_handler(
        '/tristero-parcels/internal/v1/parcels/v2/retrieve-orders',
    )
    def _retrieve_orders_v2(request):
        retrieve_orders = {'orders': []}

        # necessary fields except 'parcels'/'items'
        order_fields = {
            'order_id',
            'ref_order',
            'token',
            'vendor',
            'depot_id',
            'status',
            'delivery_date',
            'customer_address',
            'customer_location',
            'image_url_order_with_groceries',
            'timeslot',
            'alternative_timeslots',
        }
        parcel_fields = {
            'parcel_id',
            'depot_id',
            'status',
            'title',
            'quantity_limit',
            'can_left_at_door',
            'state_meta',
        }

        for full_order in context.orders:
            order_data = full_order.data
            known_order = next(
                filter(
                    lambda order, od=order_data: order['ref_order']
                    == od['ref_order']
                    and order['vendor'] == od['vendor'],
                    request.json['known_orders'],
                ),
                None,
            )
            if known_order:
                if 'token' in known_order:
                    if order_data['token'] != known_order['token']:
                        continue
                elif 'X-Yandex-UID' in request.headers:
                    if order_data['uid'] != request.headers['X-Yandex-UID']:
                        continue
                else:
                    continue
                order_info = {
                    k: v
                    for (k, v) in order_data.items()
                    if (k in order_fields)
                }

                # rename 'status' to 'state'
                order_info['state'] = order_info.pop('status')

                parcels = []
                for parcel_data in order_data['parcels']:
                    parcel = {
                        k: v
                        for (k, v) in parcel_data.items()
                        if (k in parcel_fields)
                    }
                    # rename 'status' to 'state'
                    parcel['state'] = parcel.pop('status')
                    # add extra fields
                    parcel['depot_id'] = order_info['depot_id']

                    parcels.append(parcel)
                order_info['items'] = parcels

                retrieve_orders['orders'].append(order_info)

            if 'depot_id' in request.json:
                retrieve_orders['depot_id'] = request.json['depot_id']
            elif retrieve_orders['orders'] and all(
                [
                    o['depot_id'] == retrieve_orders['orders'][0]['depot_id']
                    for o in retrieve_orders['orders']
                ],
            ):
                retrieve_orders['depot_id'] = retrieve_orders['orders'][0][
                    'depot_id'
                ]

        for full_order in context.orders:
            order_data = full_order.data
            if 'X-Yandex-UID' in request.headers:
                if order_data['uid'] != request.headers['X-Yandex-UID']:
                    continue
            else:
                return retrieve_orders

            order = {
                k: v for (k, v) in order_data.items() if (k in order_fields)
            }
            if order['order_id'] in [
                    order['order_id'] for order in retrieve_orders['orders']
            ]:
                continue
            order['state'] = order.pop('status')
            parcels = []
            for parcel_data in order_data['parcels']:
                parcel = {
                    k: v
                    for (k, v) in parcel_data.items()
                    if (k in parcel_fields)
                }
                # rename 'status' to 'state'
                parcel['state'] = parcel.pop('status')
                # add extra fields
                parcel['depot_id'] = order['depot_id']

                parcels.append(parcel)
            order['items'] = parcels

            retrieve_orders['orders'].append(order)

        return retrieve_orders

    @mockserver.json_handler(
        '/tristero-parcels/internal/v1/parcels/v1/retrieve-orders',
    )
    def retrieve_orders(request):
        if context.yandex_uid:
            assert request.headers['X-Yandex-UID'] == context.yandex_uid

        response = {}

        # necessary fields except 'parcels'/'items'
        order_fields = {
            'order_id',
            'ref_order',
            'token',
            'vendor',
            'status',
            'depot_id',
            'customer_address',
            'customer_location',
            'customer_meta',
            'timeslot',
            'alternative_timeslots',
        }
        parcel_fields = {
            'parcel_id',
            'status',
            'description',
            'title',
            'image_url_template',
            'can_left_at_door',
            'quantity_limit',
        }

        response['orders'] = []
        for full_order in context.orders:
            order_data = full_order.data
            if 'X-Yandex-UID' in request.headers:
                if order_data['uid'] != request.headers['X-Yandex-UID']:
                    continue

            order = {
                k: v for (k, v) in order_data.items() if (k in order_fields)
            }

            parcels = []
            for parcel_data in order_data['parcels']:
                parcel = {
                    k: v
                    for (k, v) in parcel_data.items()
                    if (k in parcel_fields)
                }
                parcels.append(parcel)
            order['parcels'] = parcels

            response['orders'].append(order)

        return response

    @mockserver.json_handler(
        '/tristero-parcels/internal/v1/parcels/v1/retrieve',
    )
    def retrieve(request):
        if context.yandex_uid:
            assert request.headers['X-Yandex-UID'] == context.yandex_uid

        response = {}

        parcel_fields = {
            'parcel_id',
            'description',
            'title_tanker_key',
            'image_url_template',
            'can_left_at_door',
        }
        response['parcels'] = []
        for order in context.orders:
            for parcel_data in order.data['parcels']:
                parcel = {
                    k: v
                    for k, v in parcel_data.items()
                    if (k in parcel_fields)
                }
                response['parcels'].append(parcel)

        response['category'] = context.category.data

        return response

    @mockserver.json_handler(
        '/tristero-parcels/internal/v1/parcels/v1/order-info',
    )
    def order_info(request):
        order_info = {}

        # necessary fields except 'parcels'/'items'
        order_fields = {
            'order_id',
            'ref_order',
            'token',
            'vendor',
            'depot_id',
            'status',
            'delivery_date',
            'customer_address',
            'customer_location',
            'image_url_order_with_groceries',
            'timeslot',
            'alternative_timeslots',
        }
        parcel_fields = {
            'parcel_id',
            'depot_id',
            'status',
            'title',
            'quantity_limit',
            'can_left_at_door',
            'state_meta',
        }

        for full_order in context.orders:
            order_data = full_order.data
            if (
                    order_data['ref_order'] == request.args['ref_order']
                    and order_data['vendor'] == request.args['vendor']
            ):
                if 'token' in request.args:
                    if order_data['token'] != request.args['token']:
                        return mockserver.make_response(status=403)
                elif 'X-Yandex-UID' in request.headers:
                    if order_data['uid'] != request.headers['X-Yandex-UID']:
                        return mockserver.make_response(status=403)
                else:
                    return mockserver.make_response(status=403)

                order_info = {
                    k: v
                    for (k, v) in order_data.items()
                    if (k in order_fields)
                }

                # rename 'status' to 'state'
                order_info['state'] = order_info.pop('status')

                parcels = []
                for parcel_data in order_data['parcels']:
                    parcel = {
                        k: v
                        for (k, v) in parcel_data.items()
                        if (k in parcel_fields)
                    }
                    # rename 'status' to 'state'
                    parcel['state'] = parcel.pop('status')
                    # add extra fields
                    parcel['depot_id'] = order_info['depot_id']

                    parcels.append(parcel)
                order_info['items'] = parcels

                return order_info

        return mockserver.make_response(status=404)

    @mockserver.json_handler(
        '/tristero-parcels/internal/v1/parcels/v1/order/make',
    )
    def order_make(request):
        if request.url in context.check_request_data:
            check_request_data = context.check_request_data[request.url]
            assert request.json == check_request_data['json']
            assert request.args == check_request_data['params']
            assert request.headers == check_request_data['headers']

        ref_order = request.json['ref_order']
        token = request.json['token']
        vendor = request.json['vendor']
        for order in context.orders:
            order_data = order.data
            if (
                    order_data['ref_order'] == ref_order
                    and order_data['vendor'] == vendor
                    and order_data['token'] == token
            ):
                if order_data['status'] != 'received':
                    return mockserver.make_response(
                        json={
                            'code': 'ORDER_WRONG_STATE',
                            'message': 'Order is in wrong state',
                        },
                        status=400,
                    )
                for parcel in order_data['parcels']:
                    if parcel['status'] not in ['in_depot', 'order_cancelled']:
                        return mockserver.make_response(
                            json={
                                'code': 'PARCEL_WRONG_STATE',
                                'message': 'Parcel is in wrong state',
                            },
                            status=400,
                        )
                return {'grocery_order_id': '123456-grocery'}

        return mockserver.make_response(
            json={'code': 'ORDER_NOT_FOUND', 'message': 'Order not found'},
            status=404,
        )

    @mockserver.json_handler(
        '/tristero-parcels/internal/v1/parcels/v1/order/track',
    )
    def order_track(request):
        ref_order = request.json['ref_order']
        token = request.json['token']
        vendor = request.json['vendor']
        order_fields = {
            'order_id',
            'ref_order',
            'token',
            'vendor',
            'depot_id',
            'status',
            'delivery_date',
            'customer_address',
            'customer_location',
            'image_url_order_with_groceries',
        }
        parcel_fields = {
            'parcel_id',
            'depot_id',
            'status',
            'title',
            'quantity_limit',
            'can_left_at_door',
        }
        for order in context.orders:
            order_data = order.data
            if (
                    order_data['ref_order'] == ref_order
                    and order_data['vendor'] == vendor
                    and order_data['token'] == token
            ):
                # TODO: get order info and parcels
                order_info = {
                    k: v
                    for (k, v) in order_data.items()
                    if (k in order_fields)
                }
                # rename 'status' to 'state'
                order_info['state'] = order_info.pop('status')

                parcels = []
                for parcel_data in order_data['parcels']:
                    parcel = {
                        k: v
                        for (k, v) in parcel_data.items()
                        if (k in parcel_fields)
                    }
                    # rename 'status' to 'state'
                    parcel['state'] = parcel.pop('status')
                    # add extra fields
                    parcel['depot_id'] = order_info['depot_id']
                    parcel['state_meta'] = {}

                    parcels.append(parcel)
                order_info['items'] = parcels

                track_response = {'order_data': {'order': order_info}}
                order_data = track_response['order_data']

                order_data[
                    'grocery_order_id'
                ] = '4fe795ed-afd8-41d2-9f73-bb4333437bb5'
                order_data['short_order_id'] = '280920-a-2254655'
                order_data['status'] = 'assembled'
                order_data['delivery_eta_min'] = 3
                order_data['client_price_template'] = '1000$SIGN$$CURRENCY$'
                order_data['location'] = [10.0, 20.0]
                order_data['address'] = {
                    'country': 'order_country',
                    'city': 'order_city',
                    'street': 'order_street',
                    'house': 'order_building',
                    'floor': 'order_floor',
                    'flat': 'order_flat',
                    'doorcode': 'order_doorcode',
                    'place_id': 'place-id',
                }
                order_data['depot_location'] = [13.0, 37.0]
                order_data['promise_max'] = '2020-05-25T15:38:45+00:00'
                order_data['localized_promise'] = 'Заказ приедет к ~ 18:38'
                order_data['courier_info'] = {
                    'name': 'Ivan',
                    'transport_type': 'car',
                }
                order_data['tracking_info'] = {
                    'title': 'Ещё примерно 56 минут',
                }
                order_data['actions'] = [{'type': 'call_courier'}]
                return track_response
        return {}

    context = Context()
    return context


@pytest.fixture(name='tristero_parcels_500')
def mock_tristero_parcels_500(mockserver):
    class Context:
        @property
        def retrieve_orders_times_called(self):
            return retrieve_orders.times_called

        @property
        def retrieve_times_called(self):
            return retrieve.times_called

        @property
        def order_info_times_called(self):
            return order_info.times_called

    @mockserver.json_handler(
        '/tristero-parcels/internal/v1/parcels/v1/retrieve-orders',
    )
    def retrieve_orders(request):
        return mockserver.make_response(status=500)

    @mockserver.json_handler(
        '/tristero-parcels/internal/v1/parcels/v1/retrieve',
    )
    def retrieve(request):
        return mockserver.make_response(status=500)

    @mockserver.json_handler(
        '/tristero-parcels/internal/v1/parcels/v1/order-info',
    )
    def order_info(request):
        return mockserver.make_response(status=500)

    context = Context()
    return context
