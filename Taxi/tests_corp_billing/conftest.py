# pylint: disable=wildcard-import, unused-wildcard-import, import-error

import datetime
import uuid

import pytest

from corp_billing_plugins import *  # noqa: F403 F401 I100 I202

from tests_corp_billing import billing_events_service
from tests_corp_billing import billing_replication_service
from tests_corp_billing import billing_reports_service
from tests_corp_billing import util


@pytest.fixture(autouse=True, name='tvm_config')
def tvm_config_fixture(taxi_config):
    taxi_config.set(
        TVM_SERVICES={
            'billing-replication': 999,
            'billing-reports': 555,
            'corp-billing': 123,
            'billing_orders': 456,
            'corp-billing-events': 789,
            'corp-discounts': 111,
            'statistics': 777,
            'agglomerations': 888,
            'corp-integration-api': 1000005,
            'stq-agent': 222,
        },
    )


@pytest.fixture
def billing_replication_config(taxi_config):
    taxi_config.set(
        CORP_BILLING_SERVICES_IDS={
            'eats': [668],
            'drive': [123],
            'claim': [555],
            'tanker': [636],
        },
        CORP_COUNTRIES_SUPPORTED={
            'kaz': {
                'country_code': 'KZ',
                'currency': 'KZT',
                'currency_sign': '₸',
                'deactivate_threshold': 500,
                'default_language': 'ru',
                'default_phone_code': '+7',
                'new_user_sms_tanker_key': 'sms.create_user_kaz',
                'utc_offset': '+06:00',
                'vat': 0.12,
                'web_ui_languages': ['kk', 'ru', 'en'],
            },
            'rus': {
                'country_code': 'RU',
                'currency': 'RUB',
                'currency_sign': '₽',
                'deactivate_threshold': 100,
                'default_language': 'ru',
                'default_phone_code': '+7',
                'new_user_sms_tanker_key': 'sms.create_user',
                'show_tariffs': True,
                'utc_offset': '+03:00',
                'vat': 0.2,
                'web_ui_languages': ['ru', 'en', 'he'],
            },
        },
    )


@pytest.fixture
def request_get_clients(taxi_corp_billing):
    async def _wrapper(external_refs):
        body = {'clients': [{'external_ref': ref for ref in external_refs}]}
        response = await taxi_corp_billing.post('/v1/clients/find', json=body)
        return response

    return _wrapper


@pytest.fixture
async def request_create_client(taxi_corp_billing):
    async def _wrapper(external_ref, payment_method_name):
        body = {
            'external_ref': external_ref,
            'payment_method_name': payment_method_name,
        }
        response = await taxi_corp_billing.post(
            '/v1/clients/create', json=body,
        )
        return response

    return _wrapper


@pytest.fixture
async def request_update_client(taxi_corp_billing):
    async def _wrapper(client):
        response = await taxi_corp_billing.post(
            '/v1/clients/update', json=client,
        )
        return response

    return _wrapper


@pytest.fixture
def request_create_employee(taxi_corp_billing):
    async def _wrapper(employee):
        body = {
            'client_external_ref': employee['client_external_ref'],
            'external_ref': employee['external_ref'],
        }
        response = await taxi_corp_billing.post(
            '/v1/employees/create', json=body,
        )
        return response

    return _wrapper


@pytest.fixture
def request_update_employee(taxi_corp_billing):
    async def _wrapper(employee):
        response = await taxi_corp_billing.post(
            '/v1/employees/update', json=employee,
        )
        return response

    return _wrapper


@pytest.fixture
def request_find_employees(taxi_corp_billing):
    async def _wrapper(external_refs):
        body = {'employees': [{'external_ref': ref for ref in external_refs}]}
        response = await taxi_corp_billing.post(
            '/v1/employees/find', json=body,
        )
        return response

    return _wrapper


@pytest.fixture
def request_billing_orders(taxi_corp_billing):
    async def _wrapper(topic):
        response = await taxi_corp_billing.post(
            '/v1/billing-orders', json=topic,
        )
        return response

    return _wrapper


@pytest.fixture
def request_payment_methods_eats(taxi_corp_billing):
    async def _wrapper(is_phonish=True, **request_body):
        request_body.update(is_phonish=is_phonish)
        response = await taxi_corp_billing.post(
            '/v1/payment-methods/availability/eats', json=request_body,
        )
        return response

    return _wrapper


@pytest.fixture
def request_pay_order_eats(taxi_corp_billing):
    async def _wrapper(**request_body):
        response = await taxi_corp_billing.post(
            '/v1/pay-order/eats', json=request_body,
        )
        return response

    return _wrapper


@pytest.fixture
def events_topics_handler(mockserver):
    def _wrapper(response):
        @mockserver.json_handler('/corp-billing-events/v1/topics/compact')
        async def handler(request):
            if callable(response):
                return response(request)
            return response

        return handler

    return _wrapper


@pytest.fixture
def reports_balances_handler(mockserver):
    def _wrapper(response):
        @mockserver.json_handler('/billing-reports/v1/balances/select')
        async def handler(request):
            if callable(response):
                return response(request)
            return response

        return handler

    return _wrapper


@pytest.fixture
def events_push_handler(mockserver):
    @mockserver.json_handler('/corp-billing-events/v1/events')
    def handler(request):
        return {}

    return handler


@pytest.fixture
def get_billing_id_handler(
        mockserver, billing_replication,
):  # pylint: disable=W0621
    @mockserver.json_handler('/billing-replication/corp-client/')
    def handler(request):
        return billing_replication.get_billing_id()

    return handler


@pytest.fixture
def get_billing_active_contract(
        mockserver, billing_replication,
):  # pylint: disable=W0621
    @mockserver.json_handler('/billing-replication/v1/active-contracts/')
    def handler(request):
        services = [
            int(service) for service in request.args['service_id'].split(',')
        ]
        services = set(services)
        result = []
        for contract in billing_replication.get_contract():
            if services.intersection(set(contract['SERVICES'])):
                result.append(contract)
        return result

    return handler


@pytest.fixture
async def add_client_with_services(
        request_create_client, request_update_client,  # pylint: disable=W0621
):
    async def _wrapper(client):
        response = await request_create_client(
            client['external_ref'], client['payment_method_name'],
        )
        assert response.status_code == 200

        client['revision'] = response.json()['revision']
        response = await request_update_client(client)
        assert response.status_code == 200

        return response

    return _wrapper


@pytest.fixture
def normalize_order():
    def _wrapper(order):
        order['event_at'] = util.normalize_timestring(order['event_at'])
        if order['data'].get('entries'):
            # ConvertibleToPayout
            entries = order['data']['entries']
            for entry in entries:
                entry['amount'] = util.normalize_money(entry['amount'])
            entries.sort(key=util.account_to_tuple)
        else:
            # ArbitraryPayout
            entries = order['data']['template_entries']
            for entry in entries:
                entry['context']['amount'] = util.normalize_money(
                    entry['context']['amount'],
                )
                entries.sort(
                    key=lambda obj: util.account_to_tuple(obj['context']),
                )
        return order

    return _wrapper


@pytest.fixture
def sync_with_corp_cabinet(
        load_json,
        add_client_with_services,  # pylint: disable=W0621
        request_create_employee,  # pylint: disable=W0621
        request_update_employee,  # pylint: disable=W0621
):
    async def _wrapper(*static_files):
        if not static_files:
            static_files = [
                'client_yataxi_rus.json',
                'client_yataxi_kaz.json',
                'client_yastation_rus.json',
            ]
        for filename in static_files:
            data = load_json(filename)

            await add_client_with_services(data['client'])

            for employee in data['employees']:
                response = await request_create_employee(employee)
                assert response.status_code == 200
                employee['revision'] = response.json()['revision']
                response = await request_update_employee(employee)
                assert response.status_code == 200

    return _wrapper


@pytest.fixture
def build_eats_order(load_json, mocked_time):
    def _wrapper(
            transaction_created_at=None, order_external_ref=None, **kwargs,
    ):
        if transaction_created_at is None:
            transaction_created_at = mocked_time.now()
        if order_external_ref is None:
            order_external_ref = uuid.uuid4().hex
        order = load_json('eats_order_template.json')
        order.update(kwargs)
        order['transaction_created_at'] = util.to_timestring(
            transaction_created_at,
        )
        order['order']['external_ref'] = order_external_ref

        return order

    return _wrapper


@pytest.fixture
def billing_reports():
    return billing_reports_service.Service()


@pytest.fixture
def billing_replication(billing_replication_config):  # pylint: disable=W0621
    return billing_replication_service.ReplicationService()


@pytest.fixture
def spend_money(billing_reports, mocked_time):  # pylint: disable=W0621
    def _wrapper(
            client_external_ref,
            employee_external_ref,
            amount,
            currency,
            service_type,
            from_dt,
            month_timestamp=None,
            event_at=None,
    ):
        now = mocked_time.now()
        if month_timestamp is None:
            month_timestamp = now
        if event_at is None:
            event_at = now - datetime.timedelta(seconds=5)
        entity = 'corp/client_employee/%s/%s' % (
            client_external_ref,
            employee_external_ref,
        )
        service = service_type.split('/')[0]
        account = {
            'entity': entity,
            'agreement': f'{service}/orders/limit',
            'currency': currency,
            'sub_account': 'payment',
        }
        billing_reports.set_balance_at(account, event_at, amount)

    return _wrapper


@pytest.fixture
def balances_handler(mockserver, billing_reports):  # pylint: disable=W0621
    @mockserver.json_handler('/billing-reports/v1/balances/select')
    def handler(request):
        response = billing_reports.get_balances(request.json)
        return response

    return handler


@pytest.fixture
def success_int_api_checks_mock(
        mockserver, billing_replication, load_json,
):  # pylint: disable=W0621
    @mockserver.json_handler('/taxi-corp-integration/v1/payment-methods/eats')
    def handler(request):
        assert request.json == {
            'currency': 'RUB',
            'order_id': '111111-222222',
            'order_sum': '1650',
        }
        return load_json('pm_eats_response.json')

    return handler


@pytest.fixture
def int_api_tanker_checks_mock(
        mockserver, billing_replication, load_json,
):  # pylint: disable=W0621
    @mockserver.json_handler(
        '/taxi-corp-integration/v1/payment-methods/tanker',
    )
    def handler(request):
        assert request.json == {
            'currency': 'RUB',
            'order_id': '111111-222222',
            'order_sum': '1400',
            'fuel_type': 'a95',
        }
        return load_json('pm_tanker_response.json')

    return handler


@pytest.fixture
def build_pa_headers():
    def _wrapper(headers):
        default = {
            'X-YaTaxi-UserId': 'user_id',
            'X-Yandex-UID': 'uid',
            'X-YaTaxi-Bound-Uids': 'uid1,uid2',
            'X-Yandex-Login': 'login',
            'X-YaTaxi-Pass-Flags': 'portal,ya-plus',
            'X-Request-Language': 'ru_RU',
            'X-Request-Application': 'app=iphone',
            'X-YaTaxi-User': 'personal_phone_id=some_personal_phone_id',
        }
        default.update(headers)
        return default

    return _wrapper


@pytest.fixture
def _events_service():
    return billing_events_service.EventsService()


@pytest.fixture
async def mocks(
        balances_handler,
        mockserver,
        _events_service,
        get_billing_id_handler,
        get_billing_active_contract,
):  # pylint: disable=W0621
    class Mocks:
        balances = balances_handler
        events_service = _events_service

        @staticmethod
        @mockserver.json_handler('/corp-billing-events/v1/events')
        def events_post(request):
            _events_service.push(request.json['events'])
            return {}

        @staticmethod
        @mockserver.json_handler('/corp-billing-events/v1/topics/compact')
        def events_topics(request):
            return _events_service.compacted(request.json['topics'])

    return Mocks()


@pytest.fixture
async def pay_order_request(taxi_corp_billing):
    async def _wrapper(order):
        url = '/v1/pay-order/eats'
        response = await taxi_corp_billing.post(url, json=order)
        return response

    return _wrapper


@pytest.fixture
async def pay_cargo_request(taxi_corp_billing):
    async def _wrapper(order):
        url = '/v1/pay-order/cargo'
        response = await taxi_corp_billing.post(url, json=order)
        return response

    return _wrapper


@pytest.fixture
async def pay_order_tanker_request(taxi_corp_billing):
    async def _wrapper(order):
        url = '/v1/pay-order/tanker'
        response = await taxi_corp_billing.post(url, json=order)
        return response

    return _wrapper


@pytest.fixture
def cursor(pgsql):
    return pgsql['corp_billing'].cursor()
