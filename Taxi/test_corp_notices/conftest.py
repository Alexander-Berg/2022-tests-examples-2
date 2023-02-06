# pylint: disable=redefined-outer-name
import dataclasses
import typing

import pytest

import corp_notices.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['corp_notices.generated.service.pytest_plugins']


@pytest.fixture
def mock_corp_clients(mockserver):
    class MockCorpClients:
        @dataclasses.dataclass
        class CorpClientsData:
            get_contracts_response: dict
            get_client_response: typing.Optional[dict]
            client_attendance_response: list
            get_service_taxi_response: typing.Optional[dict]

        data = CorpClientsData(
            get_contracts_response={},
            get_client_response=None,
            client_attendance_response=[],
            get_service_taxi_response=None,
        )

        @staticmethod
        @mockserver.json_handler('/corp-clients/v1/contracts')
        async def get_contracts(request):
            return mockserver.make_response(
                json=MockCorpClients.data.get_contracts_response, status=200,
            )

        @staticmethod
        @mockserver.json_handler('/corp-clients/v1/clients')
        async def get_client(request):
            if MockCorpClients.data.get_client_response:
                return mockserver.make_response(
                    json=MockCorpClients.data.get_client_response, status=200,
                )
            return mockserver.make_response(
                json={'message': 'Not Found'}, status=404,
            )

        @staticmethod
        @mockserver.json_handler('/corp-clients/v1/services/taxi')
        async def service_taxi_get(request):
            if MockCorpClients.data.get_service_taxi_response:
                return mockserver.make_response(
                    json=MockCorpClients.data.get_service_taxi_response,
                    status=200,
                )
            return mockserver.make_response(
                json={'message': 'Not Found'}, status=404,
            )

        @staticmethod
        @mockserver.json_handler('/corp-clients/v1/clients/attendance')
        async def clients_attendance(request):
            return mockserver.make_response(
                json=MockCorpClients.data.client_attendance_response,
                status=200,
            )

    return MockCorpClients()


@pytest.fixture
def mock_corp_requests(mockserver):
    class MockCorpRequests:
        @dataclasses.dataclass
        class CorpRequestsData:
            get_client_request_response: dict
            get_request_draft_response: dict
            get_manager_request_response: dict
            man_requests_byclientids: list

        data = CorpRequestsData(
            get_client_request_response={},
            get_request_draft_response={},
            get_manager_request_response={},
            man_requests_byclientids=[],
        )

        @staticmethod
        @mockserver.json_handler('/corp-requests/v1/client-requests')
        async def get_client_request(request):
            if MockCorpRequests.data.get_client_request_response:
                return mockserver.make_response(
                    json=MockCorpRequests.data.get_client_request_response,
                    status=200,
                )
            return mockserver.make_response(
                json={'message': 'Not Found'}, status=404,
            )

        @staticmethod
        @mockserver.json_handler('/corp-requests/v1/client-request-draft')
        async def get_client_request_draft(request):
            if MockCorpRequests.data.get_request_draft_response:
                return mockserver.make_response(
                    json=MockCorpRequests.data.get_request_draft_response,
                    status=200,
                )
            return mockserver.make_response(
                json={'message': 'Not Found'}, status=404,
            )

        @staticmethod
        @mockserver.json_handler('/corp-requests/v1/manager-requests')
        async def get_manager_request(request):
            if MockCorpRequests.data.get_manager_request_response:
                return mockserver.make_response(
                    json=MockCorpRequests.data.get_manager_request_response,
                    status=200,
                )
            return mockserver.make_response(
                json={'message': 'Not Found'}, status=404,
            )

        @staticmethod
        @mockserver.json_handler(
            '/corp-requests/v1/manager-requests/by-client-ids',
        )
        async def get_man_requests_by_client_ids(request):
            resp = {
                'manager_requests': [
                    x
                    for x in MockCorpRequests.data.man_requests_byclientids
                    if x['client_id'] in request.json['client_ids']
                ],
            }
            return mockserver.make_response(json=resp, status=200)

        @staticmethod
        @mockserver.json_handler(
            '/corp-requests/v1/manager-requests/activation_email_sent',
        )
        async def post_activation_email_sent(request):
            return mockserver.make_response(json={}, status=200)

    return MockCorpRequests()


@pytest.fixture
def mock_staff(mockserver):
    class MockStaff:
        @dataclasses.dataclass
        class StaffData:
            get_persons_response: dict

        data = StaffData(get_persons_response={})

        @staticmethod
        @mockserver.json_handler('/staff/v3/persons')
        async def get_persons(request):
            return mockserver.make_response(
                json=MockStaff.data.get_persons_response, status=200,
            )

    return MockStaff()


@pytest.fixture
def mock_sender(mockserver):
    class MockSender:
        @staticmethod
        @mockserver.json_handler(
            r'/sender/api/0/taxi/transactional/(?P<slug>\w+)/send', regex=True,
        )
        async def send_transactional(request, slug):
            return mockserver.make_response(json={}, status=200)

    return MockSender()
