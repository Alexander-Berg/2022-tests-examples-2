# pylint: disable=redefined-outer-name
import json
import os

from psycopg2 import extras
import pytest

from taxi.util import dates

import eats_corp_orders.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301
from eats_corp_orders.generated.service.swagger.models import api
from eats_corp_orders.internal import types

pytest_plugins = ['eats_corp_orders.generated.service.pytest_plugins']

skip_teamcity_old_redis = pytest.mark.skipif(  # pylint: disable=invalid-name
    os.getenv('IS_TEAMCITY'), reason='Teamcity does not support redis 6.2.0',
)


@pytest.fixture
def user_id():
    return 177043222


@pytest.fixture
def qr_code():
    return 'YNDX17bd2a3c7db44373822cc291d09b86bc'


@pytest.fixture
def user_code():
    return '111111'


@pytest.fixture
def order_id():
    return 'order_id'


@pytest.fixture
def order_nr():
    return '00000-00000'


@pytest.fixture
def terminal_id():
    return 'terminal_id'


@pytest.fixture
def balance_client_id():
    return 'balance_client_id'


@pytest.fixture
def place_id():
    return '146'


@pytest.fixture
def terminal_token():
    return 'secret_token'


@pytest.fixture
def idempotency_key():
    return 'idempotency_key'


@pytest.fixture
def cancel_token():
    return 'cancel_token'


@pytest.fixture
def yandex_uid():
    return '4087169916'


@pytest.fixture
def phone_id():
    return '3f59131b38cb45629e70320a116df7cf'


@pytest.fixture
def email_id():
    return 'email_id'


@pytest.fixture
def eats_user(user_id, phone_id, email_id):
    return (
        f'user_id={user_id},'
        f'personal_phone_id={phone_id},'
        f'personal_email_id={email_id}'
    )


@pytest.fixture
def x_request_language():
    return 'ru'


@pytest.fixture
def x_device_id():
    return 'l11vff1l-2fqcfs0hg02-lbv5gojuvea-rw18h4vwvne'


@pytest.fixture
def user_agent():
    return 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'


@pytest.fixture
def x_platform():
    return 'desktop_web'


@pytest.fixture
def x_app_version():
    return '15.50.1'


@pytest.fixture
def x_remote_ip():
    return '127.0.0.1'


@pytest.fixture
def items():
    return [
        {
            'price': '1.0',
            'quantity': '2.0',
            'vat': 'nds_0',
            'title': 'Бюджетное мороженое',
            'tin': '',
        },
        {
            'price': '10.0',
            'quantity': '1.5',
            'vat': 'nds_20',
            'title': 'Дорогое мороженое',
            'tin': '',
        },
        {
            'price': '0.5',
            'quantity': '1.0',
            'vat': 'nds_20',
            'title': '',
            'tin': '',
        },
    ]


@pytest.fixture
def proper_headers_code_get(
        eats_user,
        yandex_uid,
        x_device_id,
        x_platform,
        user_agent,
        x_request_language,
        x_app_version,
        x_remote_ip,
):
    return {
        'X-Eats-User': eats_user,
        'X-Yandex-UID': yandex_uid,
        'X-Device-Id': x_device_id,
        'X-Platform': x_platform,
        'User-Agent': user_agent,
        'X-Request-Language': x_request_language,
        'X-App-Version': x_app_version,
        'X-Remote-Ip': x_remote_ip,
    }


@pytest.fixture
def eats_authproxy_headers(eats_user):
    return {'X-Eats-User': eats_user}


@pytest.fixture
async def notify_about_order(
        web_context,
        web_app_client,
        proper_headers_code_get,
        user_id,
        items,
        order_id,
        order_nr,
):
    async def wrapper():
        return await web_context.long_polling.notify_about_order(
            user_id,
            types.ItemsForUser(
                items=[
                    api.ItemForUser(
                        price=item['price'],
                        quantity=item['quantity'],
                        title=item['title'],
                    )
                    for item in items
                ],
                order_id=order_id,
                order_nr=order_nr,
                is_confirmation_required=False,
            ),
        )

    return wrapper


@pytest.fixture
def pgsql_conn(pgsql):
    conn = pgsql['eats_corp_orders'].conn
    conn.cursor_factory = extras.RealDictCursor
    return conn


@pytest.fixture
def check_codes_db(pgsql_conn):
    def _check_db_data(expected_data):
        with pgsql_conn.cursor() as cursor:
            cursor.execute('SELECT user_id, code, expires_at FROM user_codes')
            actual_data = [row for row in cursor]

        assert len(actual_data) == len(expected_data)

        for actual, expected in zip(actual_data, expected_data):
            assert actual['user_id'] == expected['user_id']
            assert actual['code'] == expected['code']
            assert (
                dates.localize(actual['expires_at']).isoformat()
                == expected['expires_at']
            )

    return _check_db_data


@pytest.fixture
def check_payment_methods_db(pgsql_conn):
    def _check_db_data(expected_data):
        with pgsql_conn.cursor() as cursor:
            cursor.execute(
                'SELECT id, type, user_id, meta FROM payment_methods',
            )
            actual_data = [row for row in cursor]

        assert len(actual_data) == len(expected_data)

        for i, elem in enumerate(expected_data):
            assert actual_data[i] == elem

    return _check_db_data


@pytest.fixture
def check_order_status_db(pgsql_conn):
    def _check(
            order_id,
            expected_status,
            expected_is_cancelling=None,
            error_code=None,
    ):
        with pgsql_conn.cursor() as cursor:
            cursor.execute(
                f'SELECT status, is_cancelling, error_code FROM orders '
                f'WHERE id=\'{order_id}\'',
            )
            actual_data = [row for row in cursor]

        assert len(actual_data) == 1
        assert actual_data[0]['status'] == expected_status
        if expected_is_cancelling is not None:
            assert actual_data[0]['is_cancelling'] == expected_is_cancelling
        if error_code is not None:
            assert actual_data[0]['error_code'] == error_code

    return _check


@pytest.fixture
def fill_db(pgsql_conn, load):
    def _fill(sql_file_name: str):
        with pgsql_conn.cursor() as cursor:
            sql = load(sql_file_name)
            cursor.execute(sql)

    return _fill


@pytest.fixture
def check_headers_redis(
        redis_store,
        user_agent,
        x_app_version,
        x_device_id,
        user_id,
        x_platform,
        x_request_language,
        yandex_uid,
        phone_id,
        email_id,
        x_remote_ip,
):
    def _check():
        actual_bytes = redis_store.get(f'user_headers_{user_id}')
        actual = json.loads(actual_bytes)
        expected = {
            'user_agent': user_agent,
            'x_app_metrica_device_id': None,
            'x_app_version': x_app_version,
            'x_device_id': x_device_id,
            'phone_id': phone_id,
            'email_id': email_id,
            'x_platform': x_platform,
            'x_request_language': x_request_language,
            'x_yandex_uid': yandex_uid,
            'x_remote_ip': x_remote_ip,
        }
        assert actual == expected

    return _check


@pytest.fixture
def check_redis_array(redis_store):
    def _check(key, value):
        actual_bytes = redis_store.lrange(key, 0, -1)
        actual = [json.loads(elem) for elem in actual_bytes]
        expected = value
        assert actual == expected

    return _check


@pytest.fixture
def payment_methods_provider(mock_eats_taxi_corp_integration):
    def _get(case):
        if case == 'corp':

            @mock_eats_taxi_corp_integration('/v1/payment-methods/eats')
            async def handler(request):
                # assert request.json == {}
                return {
                    'payment_methods': [
                        {
                            'id': 'corp:916880dd88914f3b836e1a289484c834:RUB',
                            'type': 'corp',
                            'name': 'corp-test',
                            'currency': 'RUB',
                            'availability': {
                                'available': True,
                                'disabled_reason': '',
                            },
                            'description': 'Осталось 9000 из 10000 ₽',
                            'client_id': 'beed2277ae71428db1029c07394e542c',
                            'user_id': '916880dd88914f3b836e1a289484c834',
                            'balance_left': '9000',
                        },
                    ],
                }

        elif case == 'corp_disabled':

            @mock_eats_taxi_corp_integration('/v1/payment-methods/eats')
            async def handler(request):
                return {
                    'payment_methods': [
                        {
                            'id': 'corp:916880dd88914f3b836e1a289484c834:RUB',
                            'type': 'corp',
                            'name': 'corp-test',
                            'currency': 'RUB',
                            'availability': {
                                'available': False,
                                'disabled_reason': 'Why to enable?',
                            },
                            'description': 'Осталось 9000 из 10000 ₽',
                            'client_id': 'beed2277ae71428db1029c07394e542c',
                            'user_id': '916880dd88914f3b836e1a289484c834',
                            'balance_left': '9000',
                        },
                    ],
                }

        elif case == 'corp_not_exists':

            @mock_eats_taxi_corp_integration('/v1/payment-methods/eats')
            async def handler(request):
                return {'payment_methods': []}

        else:
            raise NotImplementedError
        return handler

    return _get


@pytest.fixture
def epma_payment_methods_provider(mock_eats_payment_methods_availability):
    def _get(case):
        if case == 'corp':

            @mock_eats_payment_methods_availability(
                '/v1/payment-methods/availability',
            )
            async def handler(request):
                return {
                    'payment_methods': [
                        {
                            'id': 'corp:916880dd88914f3b836e1a289484c834:RUB',
                            'type': 'corp',
                            'name': 'corp-test',
                            'currency': 'RUB',
                            'availability': {
                                'available': True,
                                'disabled_reason': '',
                            },
                            'description': f'Осталось N из 1000 ₽',
                            'balance_left': '9000',
                        },
                    ],
                }

        elif case == 'card':

            @mock_eats_payment_methods_availability(
                '/v1/payment-methods/availability',
            )
            async def handler(request):
                return {
                    'payment_methods': [
                        {
                            'id': 'card:a45f93536c0a402c904dd458a8bd3a88:RUB',
                            'type': 'card',
                            'number': '553691****1234',
                            'currency': 'RUB',
                            'system': 'MasterCard',
                            'availability': {
                                'available': True,
                                'disabled_reason': '',
                            },
                            'bin': '0',
                            'name': '',
                            'short_title': '',
                            'service_token': '',
                        },
                    ],
                }

        elif case == 'corp+card':

            @mock_eats_payment_methods_availability(
                '/v1/payment-methods/availability',
            )
            async def handler(request):
                return {
                    'payment_methods': [
                        {
                            'id': 'corp:916880dd88914f3b836e1a289484c834:RUB',
                            'type': 'corp',
                            'name': 'corp-test',
                            'currency': 'RUB',
                            'availability': {
                                'available': True,
                                'disabled_reason': '',
                            },
                            'description': f'Осталось N из 1000 ₽',
                            'balance_left': '9000',
                        },
                        {
                            'id': 'card:a45f93536c0a402c904dd458a8bd3a88:RUB',
                            'type': 'card',
                            'number': '553691****1234',
                            'currency': 'RUB',
                            'system': 'MasterCard',
                            'availability': {
                                'available': True,
                                'disabled_reason': '',
                            },
                            'bin': '0',
                            'name': '',
                            'short_title': '',
                            'service_token': '',
                        },
                    ],
                }

        elif case == 'corp_disabled':

            @mock_eats_payment_methods_availability(
                '/v1/payment-methods/availability',
            )
            async def handler(request):
                return {
                    'payment_methods': [
                        {
                            'id': 'corp:916880dd88914f3b836e1a289484c834:RUB',
                            'type': 'corp',
                            'name': 'corp-test',
                            'currency': 'RUB',
                            'availability': {
                                'available': False,
                                'disabled_reason': '',
                            },
                            'description': f'Осталось N из 1000 ₽',
                            'balance_left': '9000',
                        },
                        {
                            'id': 'card:a45f93536c0a402c904dd458a8bd3a88:RUB',
                            'type': 'card',
                            'number': '553691****1234',
                            'currency': 'RUB',
                            'system': 'MasterCard',
                            'availability': {
                                'available': True,
                                'disabled_reason': '',
                            },
                            'bin': '0',
                            'name': '',
                            'short_title': '',
                            'service_token': '',
                        },
                    ],
                }

        else:
            raise NotImplementedError
        return handler

    return _get
