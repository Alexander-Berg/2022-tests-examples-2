# pylint: disable=redefined-outer-name

import copy
import datetime as dt
import json
import re
import uuid

from lxml import etree
import pytest

from taxi.clients import stq_agent
from taxi.util import dates

import persey_payments.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['persey_payments.generated.service.pytest_plugins']


def remove_spaces(text):
    return re.sub(r'[\n\t\s]*', '', text)


@pytest.fixture
def mock_balance(mockserver, load):
    def _do_mock(method_response):
        @mockserver.handler('/balance/xmlrpctvm')
        def _handler(request):
            parser = etree.XMLParser(resolve_entities=False)
            root = etree.fromstring(request.get_data(), parser)
            method_name = root.xpath('//methodName[1]')[0].text

            if method_name in method_response:
                fname = method_response[method_name]
                expected_request = remove_spaces(load(f'expected_{fname}'))
                response_body = load(fname)
            else:
                raise ValueError(method_name)

            assert (
                remove_spaces(request.get_data().decode('ascii'))
                == expected_request
            ), method_name

            return mockserver.make_response(response_body, 200)

        return _handler

    return _do_mock


@pytest.fixture
def mock_trust_check_basket(mockserver):
    def _do_mock(response_update=None, token='trust-basket-token'):
        @mockserver.json_handler(f'/trust-payments/v2/payments/{token}/')
        def _handler(request):
            resp_body = {
                'status': 'success',
                'purchase_token': 'trust-basket-token',
                'trust_payment_id': 'trust-payment-id',
            }

            if response_update is not None:
                if isinstance(response_update, list):
                    update = response_update.pop()
                else:
                    update = response_update

                resp_body.update(update)

            return mockserver.make_response(status=200, json=resp_body)

        return _handler

    return _do_mock


@pytest.fixture
def fill_service_orders_success(mockserver, load_json):
    def _do_mock(expected_request):
        @mockserver.json_handler('/trust-payments/v2/orders/')
        def _handler(request):
            assert expected_request is None or request.json in load_json(
                expected_request,
            )

            resp_body = {
                'status': 'success',
                'status_code': 'created',
                'order_id': 'some_service_order_id',
            }
            return mockserver.make_response(status=200, json=resp_body)

        return _handler

    return _do_mock


@pytest.fixture
def trust_create_basket_success(mockserver, load_json):
    def _do_mock(expected_request):
        @mockserver.json_handler('/trust-payments/v2/payments/')
        def _handler(request):
            assert expected_request is None or request.json == load_json(
                expected_request,
            )

            resp_body = {
                'status': 'success',
                'purchase_token': 'trust-basket-token',
            }
            return mockserver.make_response(status=200, json=resp_body)

        return _handler

    return _do_mock


@pytest.fixture
def trust_pay_basket_success(mockserver):
    def _do_mock(amount=None):
        @mockserver.json_handler(
            '/trust-payments/v2/payments/trust-basket-token/start/',
        )
        def _handler(request):
            resp_body = {
                'status': 'success',
                'purchase_token': 'trust-basket-token',
                'payment_status': 'started',
                'payment_url': 'trust-payment-url',
                'amount': amount,
            }
            return mockserver.make_response(status=200, json=resp_body)

        return _handler

    return _do_mock


@pytest.fixture
def trust_clear_pending_success(mockserver):
    def _do_mock():
        @mockserver.json_handler(
            '/trust-payments/v2/payments/trust-basket-token/',
        )
        def _handler(request):
            resp_body = {
                'status': 'success',
                'purchase_token': 'trust-basket-token',
                'payment_status': 'cleared',
            }
            return mockserver.make_response(status=200, json=resp_body)

        return _handler

    return _do_mock


@pytest.fixture
def trust_clear_init_success(mockserver):
    def _do_mock():
        @mockserver.json_handler(
            '/trust-payments/v2/payments/trust-basket-token/clear/',
        )
        def _handler(request):
            resp_body = {
                'status': 'success',
                'purchase_token': 'trust-basket-token',
                'payment_status': 'authorized',
            }
            return mockserver.make_response(status=200, json=resp_body)

        return _handler

    return _do_mock


@pytest.fixture
def trust_create_partner_success(mockserver, load_json):
    def _do_mock(expected_request):
        @mockserver.json_handler('/trust-payments/v2/partners/')
        def _handler(request):
            data = load_json(expected_request)
            assert request.json == data['request']

            return {'status': 'success', 'partner_id': data['partner_id']}

        return _handler

    return _do_mock


@pytest.fixture
def trust_create_product_success(mockserver, load_json):
    def _do_mock(expected_request):
        @mockserver.json_handler('/trust-payments/v2/products/')
        def _handler(request):
            assert request.json in load_json(expected_request)

            return {'status': 'success'}

        return _handler

    return _do_mock


@pytest.fixture
def mock_uuid(patch):
    def _do_mock(period, start=-1):
        uuids = [
            uuid.UUID('2104653b-dac3-43e3-9ac5-7869d0bd738d'),
            uuid.UUID('26ea1098-0141-44a9-9b8e-2ea3307ab562'),
            uuid.UUID('28d83a4e-36d9-462f-8963-3fffe82d7f0d'),
            uuid.UUID('50d4a367-c219-4ce0-982c-c59b66d472e3'),
            uuid.UUID('55712909-27bd-4166-85bd-7822faba425c'),
        ]

        @patch('uuid.uuid4')
        def uuid4():
            uuid4.index += 1

            return uuids[uuid4.index % period]

        uuid4.index = start

    return _do_mock


@pytest.fixture
def trust_create_refund_success(mockserver):
    def _do_mock(expected_request=None):
        @mockserver.json_handler('/trust-payments/v2/refunds/')
        def _handler(request):
            if expected_request is not None:
                assert request.json == expected_request

            resp_body = {
                'status': 'success',
                'trust_refund_id': 'trust-refund-id',
            }
            return mockserver.make_response(status=200, json=resp_body)

        return _handler

    return _do_mock


@pytest.fixture
def mock_do_refund(mockserver):
    def _do_mock(status):
        @mockserver.json_handler(
            '/trust-payments/v2/refunds/trust-refund-id/start/',
        )
        def _handler(request):
            resp_body = {
                'status': status,
                'trust_refund_id': 'trust-refund-id',
            }
            return mockserver.make_response(status=200, json=resp_body)

        return _handler

    return _do_mock


@pytest.fixture
def mock_check_refund(mockserver):
    def _do_mock(status):
        @mockserver.json_handler('/trust-payments/v2/refunds/trust-refund-id/')
        def _handler(request):
            resp_body = {
                'status': status,
                'trust_refund_id': 'trust-refund-id',
            }
            return mockserver.make_response(status=200, json=resp_body)

        return _handler

    return _do_mock


@pytest.fixture
def mock_check_subs(mockserver, load_json):
    def _do_mock(fname):
        @mockserver.json_handler(
            '/trust-payments/v2/subscriptions/some_order_id/',
        )
        def _handler(request):
            return load_json(fname)

        return _handler

    return _do_mock


@pytest.fixture
def mock_blackbox(mockserver):
    def _do_mock(response_json, fail=False):
        @mockserver.json_handler('/blackbox/blackbox')
        def _handler(request):
            if fail:
                return mockserver.make_response(status=500)

            return response_json

        return _handler

    return _do_mock


@pytest.fixture
def mock_send_raw(mockserver, load_json):
    def _do_mock(fname):
        @mockserver.json_handler('/sticker/send-raw/')
        def _handle(request):
            req_json = request.json

            subject_match = re.search(
                r'<subject encoding="yes">(.*)</subject>', req_json['body'],
            )
            body_match = re.search(r'<!\[CDATA\[(.*)\]\]>', req_json['body'])

            req_json['subject'] = subject_match.group(1)
            req_json['body'] = body_match.group(1)

            assert req_json == load_json(fname)

            return {}

        return _handle

    return _do_mock


@pytest.fixture
def mock_payment_methods(mockserver, load_json):
    def _do_mock(fname):
        @mockserver.json_handler('/trust-payments/v2/payment_methods/')
        def _handler(request):
            return load_json(fname)

        return _handler

    return _do_mock


@pytest.fixture
def mock_set_payment_method(mockserver):
    def _do_mock(expected_request, response):
        @mockserver.json_handler(
            '/trust-payments/v2/subscriptions/some_order_id/',
        )
        def _handler(request):
            assert expected_request == request.json

            return response

        return _handler

    return _do_mock


@pytest.fixture
def mock_cancel_subs(mockserver):
    def _do_mock():
        @mockserver.json_handler(
            '/trust-payments/v2/subscriptions/some_order_id/',
        )
        def _handler(request):
            assert 'finish_ts' in request.json

            return {'status': 'success'}

        return _handler

    return _do_mock


@pytest.fixture
def get_ride_subs(pgsql):
    def _do_get(*fields):
        fields_expr = ''
        if fields:
            fields_expr = ', ' + ', '.join(fields)

        db = pgsql['persey_payments']

        cursor = db.cursor()
        cursor.execute(
            'SELECT yandex_uid, phone_id, brand, fund_id, mod, city, '
            'category, partner_name, parent_ride_subs_id, locale, '
            f'hidden_at IS NOT NULL{fields_expr} '
            'FROM persey_payments.ride_subs '
            'ORDER BY yandex_uid, brand, id',
        )

        return list(map(list, cursor))

    return _do_get


@pytest.fixture
def get_active_ride_subs(pgsql):
    def _do_get():
        db = pgsql['persey_payments']

        cursor = db.cursor()
        cursor.execute(
            'SELECT ride_subs_id, yandex_uid, brand '
            'FROM persey_payments.active_ride_subs ORDER BY ride_subs_id',
        )

        return list(map(list, cursor))

    return _do_get


@pytest.fixture
def get_seen_bound_uids(pgsql):
    def _do_get():
        db = pgsql['persey_payments']

        cursor = db.cursor()
        cursor.execute(
            'SELECT portal_yandex_uid, phonish_yandex_uid '
            'FROM persey_payments.bound_uids '
            'ORDER BY portal_yandex_uid, phonish_yandex_uid',
        )

        return list(map(list, cursor))

    return _do_get


@pytest.fixture
def check_ride_subs_events(pgsql, load_json):
    def _do_check(exp_fname):
        db = pgsql['persey_payments']

        cursor = db.cursor()
        cursor.execute(
            'SELECT ride_subs_id, type, payload '
            'FROM persey_payments.ride_subs_event '
            'ORDER BY ride_subs_id',
        )

        db_events = set()
        for event in cursor:
            db_events.add(
                json.dumps(
                    {'type': event[1], 'payload': json.loads(event[2])},
                    sort_keys=True,
                ),
            )

        exp_events = {
            json.dumps(e, sort_keys=True) for e in load_json(exp_fname)
        }

        assert db_events == exp_events

    return _do_check


@pytest.fixture
def mock_invoice_create(mockserver, load_json):
    def _do_mock(expected_request):
        @mockserver.json_handler('/transactions-persey/v2/invoice/create')
        def _handler(request):
            assert request.json == load_json(expected_request)

            return {}

        return _handler

    return _do_mock


@pytest.fixture
def mock_invoice_update(mockserver, load_json):
    def _do_mock(expected_request, not_found=False):
        @mockserver.json_handler('/transactions-persey/v2/invoice/update')
        def _handler(request):
            assert request.json == load_json(expected_request)

            if not_found:
                return mockserver.make_response(
                    status=404, json={'code': 'code', 'message': 'message'},
                )

            return {}

        return _handler

    return _do_mock


@pytest.fixture
def mock_invoice_retrieve(mockserver, load_json):
    def _do_mock(order_id, response_json):
        @mockserver.json_handler('/transactions/v2/invoice/retrieve')
        def _handler(request):
            assert request.json['id'] == order_id

            return load_json(response_json)

        return _handler

    return _do_mock


def _get_eta(date, shift_sec):
    return (date + dt.timedelta(seconds=shift_sec)).strftime(
        stq_agent.ETA_FORMAT,
    )


@pytest.fixture
def mock_stq_reschedule(mockserver):
    def _do_mock(queue_name, shift_sec):
        @mockserver.json_handler('/stq-agent/queues/api/reschedule')
        def _stq_reschedule(request):
            assert request.json == {
                'queue_name': queue_name,
                'eta': _get_eta(dates.utcnow(), shift_sec),
                'task_id': '1',
            }
            return {}

        return _stq_reschedule

    return _do_mock


@pytest.fixture
def mock_zalogin(mockserver, load_json):
    def _do_mock(expected_yandex_uid, response_json, no_uid=False):
        @mockserver.json_handler('/zalogin/v2/internal/uid-info')
        def _handler(request):
            assert request.query['yandex_uid'] == expected_yandex_uid

            if no_uid:
                return mockserver.make_response(
                    status=409,
                    json={'code': 'uid_not_found', 'message': 'message'},
                )

            return load_json(response_json)

        return _handler

    return _do_mock


@pytest.fixture
def get_ride_subs_cache(pgsql):
    def _do_get():
        db = pgsql['persey_payments']
        result = {}

        for key, query in [
                (
                    'cache',
                    'SELECT order_id, mod '
                    'FROM persey_payments.ride_subs_order_cache '
                    'ORDER BY order_id',
                ),
                (
                    'user',
                    'SELECT yandex_uid, brand, order_id '
                    'FROM persey_payments.ride_subs_order_user '
                    'ORDER BY yandex_uid, brand, order_id',
                ),
                (
                    'paid_order',
                    'SELECT order_id, CAST(amount AS VARCHAR) '
                    'FROM persey_payments.ride_subs_paid_order '
                    'ORDER BY order_id',
                ),
        ]:
            cursor = db.cursor()
            cursor.execute(query)
            result[key] = list(map(list, cursor))

        return result

    return _do_get


@pytest.fixture
def get_subs_events(pgsql):
    def _do_get():
        db = pgsql['persey_payments']
        cursor = db.cursor()
        cursor.execute('SELECT type FROM persey_payments.subs_event')

        return list(cursor)

    return _do_get


PERSEY_PAYMENTS_RIDE_SUBS_BASE = {
    'from_string': 'Помощь рядом &lt;donation@yandex-team.ru&gt;',
    'tariff_zone_mods': {'default': {'default_index': 1, 'options': [21, 12]}},
    'email_limiter_settings': {'event_delay_m': 5, 'email_delay_m': 60},
    'static_response': {
        'menu': {'icon_image_tag': 'class_econom_icon'},
        'main_screen': {
            'common': {
                'contribution_image_tag': 'class_econom_icon',
                'details': {'link': 'https://google.com'},
            },
            'subscribed': {
                'share': {
                    'og_tags': {
                        'image': (
                            'https://yastatic.net/iconostasis/'
                            '_/wT9gfGZZ80sP0VsoR6dgDyXJf2Y.png'
                        ),
                        'url': 'https://google.com',
                    },
                },
            },
        },
        'profile_screen': {'icon_image_tag': 'class_econom_icon'},
        'on_subs_dialog': {'icon_image_tag': 'class_econom_icon'},
    },
    'default_fund_id': 'friends',
    'need_accept_polling_period_s': 900,
    'order_cache': {
        'cache_ttl_s': 7500,
        'user_ttl_s': 7500,
        'update_batch_size': 20000,
        'delete_batch_size': 20000,
    },
    'donation_stats_enabled': True,
    'pay_ride_screen_static': {
        'entry': {'icon_image_tag': 'class_econom_icon'},
        'confirmation_dialog': {'icon_image_tag': 'class_econom_icon'},
    },
    'thank_ride_screen_static': {
        'entry': {'icon_image_tag': 'class_econom_icon'},
    },
}


def ride_subs_config(config_update=None, callback=None):
    config = copy.deepcopy(PERSEY_PAYMENTS_RIDE_SUBS_BASE)

    if callback is not None:
        callback(config)

    config.update(config_update or {})

    return pytest.mark.config(PERSEY_PAYMENTS_RIDE_SUBS=config)


ZONE_COUNTRY = {'moscow': 'rus', 'baku': 'aze'}


@pytest.fixture
def mock_tariffs(mockserver):
    def _do_mock(expected_zone_name):
        @mockserver.json_handler('/tariffs/v1/tariff_zones', prefix=True)
        def _handler(request):
            assert request.query['zone_names'] == expected_zone_name

            country_code = ZONE_COUNTRY.get(request.query['zone_names'])

            if country_code is None:
                zones = []
            else:
                zones = [
                    {
                        'name': 'name',
                        'time_zone': 'time_zone',
                        'country': country_code,
                    },
                ]

            return {'zones': zones}

        return _handler

    return _do_mock


@pytest.fixture
def get_donations(pgsql):
    def _do_get():
        db = pgsql['persey_payments']
        cursor = db.cursor()
        cursor.execute(
            'SELECT fund_id, yandex_uid, sum, user_name, user_email, '
            'purchase_token, trust_order_id, city, category, partner_name, '
            'subs_id, ride_subs_id, brand, order_id, status '
            'FROM persey_payments.donation',
        )

        return list(cursor)

    return _do_get


@pytest.fixture
def mock_cardstorage_card(mockserver, load_json):
    def _impl(expected_requests, response_fname, error=False):
        @mockserver.json_handler('/cardstorage/v1/card')
        def _mock_cardstorage(request):
            assert (
                request.json['yandex_uid'],
                request.json['card_id'],
            ) in expected_requests

            if error:
                return mockserver.make_response(status=500)

            resp = load_json(response_fname)
            resp['card_id'] = request.json['card_id']

            return resp

        return _mock_cardstorage

    return _impl


@pytest.fixture
def mock_cs_payment_methods(mockserver, load_json):
    def _impl(response_fname, error=False):
        @mockserver.json_handler('/cardstorage/v1/payment_methods')
        def _mock_cardstorage(request):
            if error:
                return mockserver.make_response(status=500)

            return load_json(response_fname)

        return _mock_cardstorage

    return _impl


@pytest.fixture
def mock_transactions_persey(mockserver, load_json):
    def _impl(responses_fname):
        responses = {
            order['id']: order for order in load_json(responses_fname)
        }

        @mockserver.json_handler('/transactions-persey/v2/invoice/retrieve')
        def _mock_v2_invoice_retrieve(request):
            order_id = request.json['id']

            doc = responses[order_id]

            return {
                'id': order_id,
                'invoice_due': '2020-04-15T18:29:03+0300',
                'created': '2020-04-15T18:29:03+0300',
                'currency': 'RUB',
                'status': 'cleared',
                'operation_info': {},
                'sum_to_pay': [],
                'held': [],
                'cleared': [],
                'debt': [],
                'transactions': [
                    {
                        'created': '2020-04-15T18:29:03+0300',
                        'updated': '2020-04-15T18:29:03+0300',
                        'sum': [],
                        'initial_sum': [],
                        'status': 'clear_success',
                        'refunds': [],
                        'external_payment_id': '',
                        'error_reason_code': doc.get('payment_resp_desc'),
                        'payment_method_id': doc.get('payment_method_id'),
                        'payment_type': doc.get('payment_type'),
                    },
                ],
                'yandex_uid': doc['yandex_uid'],
                'payment_types': [],
            }

        return _mock_v2_invoice_retrieve

    return _impl


@pytest.fixture
def mock_geo(mockserver):
    def _impl(country_code, status_code):
        @mockserver.json_handler('/persey-core/geo/position')
        def _mock_geo(request):
            assert request.query['position'] == '1.0,2.0'

            if status_code != 200:
                return mockserver.make_response(
                    status=status_code,
                    json={'code': 'code', 'message': 'message'},
                )

            return {'country_code': country_code}

        return _mock_geo

    return _impl


@pytest.fixture
def get_billing_events(pgsql):
    def _impl():
        db = pgsql['persey_payments']
        cursor = db.cursor()
        cursor.execute(
            'SELECT brand, order_id, event '
            'FROM persey_payments.billing_event '
            'ORDER BY brand, order_id, event',
        )

        return list(cursor)

    return _impl


@pytest.fixture
def get_donation_statuses(pgsql):
    def _impl():
        db = pgsql['persey_payments']
        cursor = db.cursor()
        cursor.execute(
            'SELECT brand, order_id, status FROM persey_payments.donation',
        )

        return {
            (brand, order_id): status for brand, order_id, status in cursor
        }

    return _impl


@pytest.fixture
def mock_participant_count(mockserver):
    @mockserver.json_handler('/persey-core/persey-core/participant-count')
    def _mock_participant_count(request):
        return {
            'overall': 1234,
            'by_brand': {'yataxi': 600, 'eats': 100, 'lavka': 2},
        }

    return _mock_participant_count
