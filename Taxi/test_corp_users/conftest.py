# pylint: disable=redefined-outer-name
import dataclasses

import pytest

import corp_users.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['corp_users.generated.service.pytest_plugins']


@pytest.fixture
def mock_personal(request, load_json):
    marker = request.node.get_closest_marker('personal_data')
    if not marker:
        request.node.add_marker(
            pytest.mark.personal_data(load_json('personal_data.json')),
        )


@pytest.fixture
def mock_corp_clients(mockserver):
    class MockCorpClients:
        @dataclasses.dataclass
        class CorpClientsData:
            get_client_response: dict
            get_client_accurate_response: dict
            get_services_response: dict

        data = CorpClientsData(
            get_client_accurate_response={},
            get_client_response={},
            get_services_response={},
        )

        @staticmethod
        @mockserver.handler('/corp-clients/v1/clients/list/accurate')
        async def clients_list_accurate(request):
            return mockserver.make_response(
                json=MockCorpClients.data.get_client_accurate_response,
                status=200,
            )

        @staticmethod
        @mockserver.handler('/corp-clients/v1/clients')
        async def get_client(request):
            return mockserver.make_response(
                json=MockCorpClients.data.get_client_response, status=200,
            )

        @staticmethod
        @mockserver.handler('/corp-clients/v1/services')
        async def get_services(request):
            return mockserver.make_response(
                json=MockCorpClients.data.get_services_response, status=200,
            )

    return MockCorpClients()


@pytest.fixture
def mock_corp_int_api(mockserver):
    class MockCorpIntApi:
        @dataclasses.dataclass
        class CorpIntApiData:
            clients_can_order_eats: dict

        data = CorpIntApiData(clients_can_order_eats={})

        @staticmethod
        @mockserver.handler(
            '/taxi-corp-integration/v1/clients/can_order/eats2',
        )
        async def clients_can_order_eats(request):
            return mockserver.make_response(
                json=MockCorpIntApi.data.clients_can_order_eats, status=200,
            )

    return MockCorpIntApi()


@pytest.fixture
def mock_billing_reports(mockserver):
    class MockBillingReports:
        @dataclasses.dataclass
        class BillingReportsData:
            balances_select: dict

        data = BillingReportsData(balances_select={})

        @staticmethod
        @mockserver.handler('/billing-reports/v1/balances/select')
        async def balances_select(request):
            return mockserver.make_response(
                json=MockBillingReports.data.balances_select, status=200,
            )

    return MockBillingReports()


@pytest.fixture
def mock_drive(mockserver):
    class DriveMock:
        @dataclasses.dataclass
        class DriveData:
            drive_accounts_response: dict

        data = DriveData(drive_accounts_response={})

        @staticmethod
        @mockserver.json_handler('/drive/api/b2b/accounts')
        def fetch_drive_spending(request):
            return mockserver.make_response(
                json=DriveMock.data.drive_accounts_response, status=200,
            )

    return DriveMock()
