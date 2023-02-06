import dataclasses
import logging

import pytest

import corp_reports.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['corp_reports.generated.service.pytest_plugins']

logger = logging.getLogger(__name__)

REPORT_ANSWER_EMPTY: dict = {'orders': []}


@pytest.fixture
def mock_personal(mockserver):
    @mockserver.json_handler('/personal/v1/yandex_logins/store')
    async def _yandex_logins_store(request):
        value = request.json['value']
        return {'id': value + '_pd_id', 'value': value}

    @mockserver.json_handler('/personal/v1/yandex_logins/retrieve')
    async def _yandex_logins_retrieve(request):
        pd_id = request.json['id']
        value = pd_id[0 : pd_id.find('_pd_id')]
        return {'id': pd_id, 'value': value}


@pytest.fixture
def mock_corp_clients(mockserver):
    class MockCorpClients:
        @dataclasses.dataclass
        class CorpClientsData:
            get_client_response: dict
            get_contracts_response: dict

        data = CorpClientsData(
            get_client_response={}, get_contracts_response={},
        )

        @staticmethod
        @mockserver.json_handler('/corp-clients/v1/clients')
        async def clients(request):
            if request.method == 'GET':
                if MockCorpClients.data.get_client_response:
                    return mockserver.make_response(
                        json=MockCorpClients.data.get_client_response,
                        status=200,
                    )
                return mockserver.make_response(json={}, status=404)
            if request.method == 'PATCH':
                return mockserver.make_response(json={}, status=200)

        @staticmethod
        @mockserver.json_handler('/corp-clients/v1/contracts')
        async def contracts(request):
            if request.method == 'GET':
                if MockCorpClients.data.get_contracts_response:
                    return mockserver.make_response(
                        json=MockCorpClients.data.get_contracts_response,
                        status=200,
                    )
            return mockserver.make_response(json={}, status=404)

    return MockCorpClients()


@pytest.fixture
def mock_corp_discounts(mockserver):
    class MockCorpDiscounts:
        @dataclasses.dataclass
        class CorpDiscountsData:
            get_client_links_response: dict

        data = CorpDiscountsData(get_client_links_response={'items': []})

        @staticmethod
        @mockserver.json_handler('/corp-discounts/v1/admin/client/links/list')
        async def clint_links(request):
            if request.method == 'GET':
                if MockCorpDiscounts.data.get_client_links_response:
                    return mockserver.make_response(
                        json=MockCorpDiscounts.data.get_client_links_response,
                        status=200,
                    )
                return mockserver.make_response(json={}, status=404)
            if request.method == 'PATCH':
                return mockserver.make_response(json={}, status=404)

    return MockCorpDiscounts()


@pytest.fixture
def mock_corp_orders(mockserver):
    class MockCorpOrders:
        @dataclasses.dataclass
        class CorpOrdersData:
            orders_eats_response: dict
            eats_must_be_error: bool
            offset_eat: int
            eats_orders_count: int
            orders_drive_response: dict
            drive_must_be_error: bool
            offset_drive: int
            drive_orders_count: int
            orders_tanker_response: dict
            tanker_must_be_error: bool
            offset_tanker: int
            tanker_orders_count: int

        data = CorpOrdersData(
            orders_eats_response={},
            offset_eat=0,
            eats_must_be_error=False,
            eats_orders_count=0,
            orders_drive_response={},
            offset_drive=0,
            drive_orders_count=0,
            drive_must_be_error=False,
            orders_tanker_response={},
            offset_tanker=0,
            tanker_must_be_error=False,
            tanker_orders_count=0,
        )

        @staticmethod
        @mockserver.json_handler('/corp-orders/v1/orders/eats/find')
        async def orders_eats_find(request):
            if request.method == 'GET':
                if MockCorpOrders.data.eats_must_be_error:
                    return mockserver.make_response(json={}, status=400)
                MockCorpOrders.data.eats_orders_count += 1
                if MockCorpOrders.data.offset_eat > 0:
                    return mockserver.make_response(
                        json=REPORT_ANSWER_EMPTY, status=200,
                    )
                if MockCorpOrders.data.orders_eats_response:
                    if MockCorpOrders.data.orders_eats_response['orders']:
                        MockCorpOrders.data.offset_eat += len(
                            MockCorpOrders.data.orders_eats_response['orders'],
                        )
                    return mockserver.make_response(
                        json=MockCorpOrders.data.orders_eats_response,
                        status=200,
                    )
                return mockserver.make_response(json={}, status=404)
            if request.method == 'PATCH':
                return mockserver.make_response(json={}, status=404)

        @staticmethod
        @mockserver.json_handler('/corp-orders/v1/orders/drive/find')
        async def orders_drive_find(request):
            if request.method == 'GET':
                if MockCorpOrders.data.drive_must_be_error:
                    return mockserver.make_response(json={}, status=400)
                MockCorpOrders.data.drive_orders_count += 1
                if MockCorpOrders.data.offset_drive > 0:
                    return mockserver.make_response(
                        json=REPORT_ANSWER_EMPTY, status=200,
                    )
                if MockCorpOrders.data.orders_drive_response:
                    if MockCorpOrders.data.orders_drive_response['orders']:
                        MockCorpOrders.data.offset_drive += len(
                            MockCorpOrders.data.orders_drive_response[
                                'orders'
                            ],
                        )
                    return mockserver.make_response(
                        json=MockCorpOrders.data.orders_drive_response,
                        status=200,
                    )
                return mockserver.make_response(json={}, status=404)
            if request.method == 'PATCH':
                return mockserver.make_response(json={}, status=404)

        @staticmethod
        @mockserver.json_handler('/corp-orders/v1/orders/tanker/find')
        async def orders_tanker_find(request):
            if request.method == 'GET':
                if MockCorpOrders.data.tanker_must_be_error:
                    return mockserver.make_response(json={}, status=400)
                MockCorpOrders.data.tanker_orders_count += 1
                if MockCorpOrders.data.offset_tanker > 0:
                    return mockserver.make_response(
                        json=REPORT_ANSWER_EMPTY, status=200,
                    )
                if MockCorpOrders.data.orders_tanker_response:
                    if MockCorpOrders.data.orders_tanker_response['orders']:
                        MockCorpOrders.data.offset_tanker += len(
                            MockCorpOrders.data.orders_tanker_response[
                                'orders'
                            ],
                        )
                    return mockserver.make_response(
                        json=MockCorpOrders.data.orders_tanker_response,
                        status=200,
                    )
                return mockserver.make_response(json={}, status=404)
            if request.method == 'PATCH':
                return mockserver.make_response(json={}, status=404)

    return MockCorpOrders()


@pytest.fixture
def mock_user_api(mockserver):
    @mockserver.json_handler('/user_api-api/user_phones/get_bulk')
    def _get_user_phones_bulk(request):
        def hex_to_phone(hex_phone):
            phone = hex_phone.strip('a')
            if not phone.startswith('+'):
                phone = '+' + phone
            return phone

        logger.error(request.json)
        return {
            'items': [
                {'id': _id, 'phone': hex_to_phone(_id)}
                for _id in request.json['ids']
            ],
        }


@pytest.fixture()
def autotranslations(monkeypatch):
    def _get_string(self, key, language, num=None):
        items = [key]
        if language != 'ru':
            items.append(language)
        if num is not None:
            items.append(num)
        return ' '.join(items)

    monkeypatch.setattr(
        'taxi.translations.TranslationBlock.get_string', _get_string,
    )
