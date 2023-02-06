# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=wrong-import-order
import datetime
import json

import bson
from debts_plugins import *  # noqa: F403 F401

import pytest  # noqa: I202


class DebtsClient:
    def __init__(self, taxi_debts):
        self.taxi_debts = taxi_debts

    async def get_limit(self, data=None):
        response = await self.taxi_debts.post(
            'v1/overdraft/limit', json=data or self.make_request(),
        )
        return response.json()

    async def get_payment_availability(self, **kwargs):
        params = dict(**kwargs)
        response = await self.taxi_debts.get(
            '/internal/payment_availability', params=params,
        )
        return response.json(), response.status_code

    async def get_payment_filters(self, phone_id, brand='yataxi'):
        params = dict(phone_id=phone_id, brand=brand)
        response = await self.taxi_debts.get(
            '/internal/launch/payment_filters', params=params,
        )
        return response.json(), response.status_code

    async def get_debts_list(self, yandex_uid, phone_id, application):
        params = dict(
            yandex_uid=yandex_uid, application=application, phone_id=phone_id,
        )
        response = await self.taxi_debts.get(
            '/internal/debts/list', params=params,
        )
        return response.json(), response.status_code

    async def admin_get_debts(
            self, order_id=None, yandex_uid=None, phone_id=None,
    ):
        params = dict(
            order_id=order_id, yandex_uid=yandex_uid, phone_id=phone_id,
        )
        params = {k: v for k, v in params.items() if v is not None}
        response = await self.taxi_debts.get(
            '/internal/admin/orders', params=params,
        )
        return response.json(), response.status_code

    async def admin_release_debt(self, order_id):
        params = dict(order_id=order_id)
        response = await self.taxi_debts.post(
            '/internal/admin/orders/release', params=params,
        )
        return response.json(), response.status_code

    async def unset_debt_hard(self, order_id):
        params = dict(order_id=order_id)
        response = await self.taxi_debts.post(
            '/internal/admin/orders/release/hard', params=params,
        )
        return response.status_code

    async def send_patch(self, order_id=None, data=None, headers=None):
        data = data or self.make_patch()
        params = {'order_id': order_id or 'order_id'}
        return await self.taxi_debts.patch(
            'v1/debts', json=data, params=params, headers=headers,
        )

    async def get_admin_orders_list(self, yandex_uid=None, phone_id=None):
        params = dict(yandex_uid=yandex_uid, phone_id=phone_id)
        response = await self.taxi_debts.get(
            'internal/admin/orders/list', params=params,
        )
        return response.json(), response.status_code

    async def admin_make_debt(self, order_id):
        params = dict(order_id=order_id)
        response = await self.taxi_debts.post(
            '/internal/admin/orders/make_debt', params=params,
        )
        return response.status_code

    async def get_admin_detail_order(self, order_id):
        params = dict(order_id=order_id)
        response = await self.taxi_debts.get(
            'internal/admin/orders/detail', params=params,
        )
        return response.json(), response.status_code

    async def unset_debt_light(self, order_id):
        params = dict(order_id=order_id)
        response = await self.taxi_debts.post(
            '/internal/admin/orders/release/light', params=params,
        )
        return response.status_code

    async def get_debstatuses(
            self,
            yandex_uid=None,
            phone_id=None,
            is_cash_available=None,
            is_plus_enabled=None,
            available_user_payment_methods=None,
    ):
        headers = {
            'X-Yandex-UID': yandex_uid,
            'X-AppMetrica-UUID': 'appmetrica-uuid',
            'X-AppMetrica-DeviceId': 'appmetrica-device-id',
        }
        if phone_id is not None:
            headers['X-YaTaxi-PhoneId'] = phone_id
        body = {}
        if is_cash_available is not None:
            body['is_cash_available'] = is_cash_available
        if is_plus_enabled is not None:
            body['is_plus_enabled'] = is_plus_enabled
        if available_user_payment_methods is not None:
            body[
                'available_user_payment_methods'
            ] = available_user_payment_methods
        response = await self.taxi_debts.post(
            '/4.0/debtstatuses', headers=headers, json=body,
        )
        return response.json(), response.status_code

    @staticmethod
    def make_patch(**kwargs):
        patch = {
            'patch_time': kwargs.get('patch_time', '2019-01-01T00:00:00.0Z'),
            'action': kwargs.get('action', 'set_debt'),
            'order_info': kwargs.get('order_info', {}),
            'yandex_uid': kwargs.get('yandex_uid', 'yandex_uid_1'),
            'phone_id': kwargs.get('phone_id', 'phone_id_1'),
            'created_at': kwargs.get('created_at', '2018-01-01T00:00:00.0Z'),
            'brand': kwargs.get('brand', 'yataxi'),
        }
        if 'value' in kwargs:
            patch['value'] = kwargs.get('value')
        if 'currency' in kwargs:
            patch['currency'] = kwargs.get('currency')
        if 'reason_code' in kwargs:
            patch['reason_code'] = kwargs.get('reason_code')
        return patch

    @staticmethod
    def make_request(
            phone_id=None, yandex_uid=None, personal_phone_id=None, brand=None,
    ):
        return {
            'brand': brand or 'yataxi',
            'personal_phone_id': personal_phone_id or 'personal-phone-id',
            'phone_id': phone_id or '58d10af0b008444444444444',
            'yandex_uid': yandex_uid or 'yandex-uid',
        }


@pytest.fixture(name='debts_client')
def _debts_client(taxi_debts):
    return DebtsClient(taxi_debts)


@pytest.fixture(name='mock_antifraud_limit')
def _mock_antifraud_limit(mockserver):
    class Context:
        value = 50
        last_request = None

    context = Context()

    @mockserver.json_handler('/antifraud/v1/overdraft/limit')
    def _antifraud_limit(request):
        context.last_request = request.json
        return {'value': context.value}

    return context


@pytest.fixture(name='mock_transactions_invoice_retrieve')
def _mock_transactions_invoice_retrieve(mockserver, load_json):
    response = load_json('transactions/response_invoice_retrive.json')

    @mockserver.json_handler('/transactions/invoice/retrieve')
    def _transactions_invoice_retrieve(request):
        order_id = request.json['id']
        if order_id == 'invoice_id_1':
            response['fail_reason'] = {'code': 'payment_failed'}
            return mockserver.make_response(json.dumps(response), 200)
        if order_id == 'invoice_id_2':
            response['id'] = 'invoice_id_2'
            response['status'] = 'cleared'
            response['debt'] = {}
            return mockserver.make_response(json.dumps(response), 200)
        if order_id == 'not_debt_order':
            response['fail_reason'] = {'code': 'payment_failed'}
            response['id'] = 'not_debt_order'
            response['debt'] = {}
            return mockserver.make_response(json.dumps(response), 200)
        return mockserver.make_response('No invoice found', 404)


@pytest.fixture()
def mock_v1_debts(mockserver):
    def _inner(order_id='some_order', **kwargs):
        @mockserver.json_handler('/debts/v1/debts')
        def v1_debts(request):
            assert request.args['order_id'] == order_id
            return mockserver.make_response(status=200)

        return v1_debts

    return _inner


@pytest.fixture()
def mock_archive_order(mockserver):
    def _inner(order_id='order_id', is_owner=False, payment_type='card'):
        @mockserver.json_handler('archive-api/archive/order')
        def _archive_order(request):
            family = {'is_owner': is_owner}
            if not is_owner:
                family['owner_uid'] = 'family_owner_uid'
            order = dict(
                _id=order_id,
                created=datetime.datetime(2020, 2, 20),
                user_uid='1234567',
                user_phone_id=bson.ObjectId('123456781234567812345678'),
                user_id='123456781234567812345679',
                user_locale='ru',
                payment_tech=dict(
                    type=payment_type,
                    main_card_payment_id='card_id',
                    family=family,
                ),
                request={},
            )
            return mockserver.make_response(
                bson.BSON.encode({'doc': order}), 200,
            )

        return _archive_order

    return _inner


@pytest.fixture()
def mock_ucommunications_push(mockserver):
    def _inner(order_id='order_id', attempt=0):
        @mockserver.json_handler('/ucommunications/user/notification/push')
        def user_notification_push(request):
            assert (
                request.headers['X-Idempotency-Token']
                == f'debts_notification/{order_id}/{attempt}'
            )
            assert request.json == {
                'data': {
                    'payload': {},
                    'repack': {
                        'apns': {
                            'aps': {
                                'alert': {
                                    'body': 'Some subtitle',
                                    'title': 'Some title',
                                },
                                'content-available': 1,
                            },
                        },
                        'fcm': {
                            'notification': {
                                'body': 'Some subtitle',
                                'title': 'Some title',
                            },
                        },
                        'hms': {
                            'notification': {
                                'body': 'Some subtitle',
                                'title': 'Some title',
                            },
                        },
                    },
                },
                'intent': 'debts.notification',
                'user': '123456781234567812345679',
            }
            return {}

        return user_notification_push

    return _inner
