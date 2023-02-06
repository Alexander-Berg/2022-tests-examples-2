import pytest

from tests_cargo_crm import const
from tests_cargo_crm.plugins.mocks.basic.basic_mock import BasicMock


@pytest.fixture(name='mocked_cargo_tasks')
async def _mocked_cargo_tasks(mockserver):
    class Context:
        def __init__(self):
            self.upsert_client = BasicMock()
            self.create_association = BasicMock()
            self.upsert_person = BasicMock()
            self.upsert_person_simulate = BasicMock()
            self.create_offer = BasicMock()
            self.create_contract = BasicMock()
            self.find_client = BasicMock()
            self.find_person = BasicMock()
            self.find_offer = BasicMock()

        @property
        def upsert_client_times_called(self):
            return _upsert_client.times_called

        @property
        def create_association_times_called(self):
            return _create_association.times_called

        @property
        def upsert_person_times_called(self):
            return _upsert_person.times_called

        @property
        def upsert_person_smt_times_called(self):
            return _upsert_person_simulate.times_called

        @property
        def create_offer_times_called(self):
            return _create_offer.times_called

    context = Context()

    @mockserver.json_handler('/cargo-tasks/v1/billing/client/upsert')
    async def _upsert_client(request):
        expected_data = context.upsert_client.get_expected_data()
        assert request.json['operator_uid'] == const.UID
        assert request.json['params'] == expected_data

        response = context.upsert_client.get_response()
        return mockserver.make_response(
            status=response['code'], json=response['json'],
        )

    @mockserver.json_handler('/cargo-tasks/v1/billing/association/create')
    async def _create_association(request):
        assert request.json['operator_uid'] == const.UID
        assert request.json['params']['customer_uid'] == const.ANOTHER_UID
        assert request.json['params']['client_id'] == const.BILLING_CLIENT_ID

        response = context.create_association.get_response()
        return mockserver.make_response(
            status=response['code'], json=response['json'],
        )

    @mockserver.json_handler('/cargo-tasks/v1/billing/person/upsert')
    async def _upsert_person(request):
        expected_data = context.upsert_person.get_expected_data()
        assert request.json['operator_uid'] == const.UID
        assert request.json['params'] == expected_data

        response = context.upsert_person.get_response()
        return mockserver.make_response(
            status=response['code'], json=response['json'],
        )

    @mockserver.json_handler('/cargo-tasks/v1/billing/person/upsert-simulate')
    async def _upsert_person_simulate(request):
        expected_data = context.upsert_person_simulate.get_expected_data()
        assert request.json['operator_uid'] == const.UID
        assert request.json['params'] == expected_data

        response = context.upsert_person_simulate.get_response()
        return mockserver.make_response(
            status=response['code'], json=response['json'],
        )

    @mockserver.json_handler('/cargo-tasks/v1/billing/offer/create')
    async def _create_offer(request):
        expected_data = context.create_offer.get_expected_data()
        assert request.json['operator_uid'] == const.UID
        assert request.json['params'] == expected_data

        response = context.create_offer.get_response()
        return mockserver.make_response(
            status=response['code'], json=response['json'],
        )

    @mockserver.json_handler('/cargo-tasks/v1/billing/contract/create')
    async def _create_contract(request):
        expected_data = context.create_contract.get_expected_data()
        assert request.json['operator_uid'] == const.UID
        assert request.json['params'] == expected_data

        response = context.create_contract.get_response()
        return mockserver.make_response(
            status=response['code'], json=response['json'],
        )

    @mockserver.json_handler('/cargo-tasks/v1/billing/client/find')
    async def _find_client(request):
        assert request.query['uid'] == const.ANOTHER_UID

        response = context.find_client.get_response()
        return mockserver.make_response(
            status=response['code'], json=response['json'],
        )

    @mockserver.json_handler('/cargo-tasks/v1/billing/client/person/list')
    async def _find_person(request):
        assert request.query['client_id'] == const.BILLING_CLIENT_ID

        response = context.find_person.get_response()
        return mockserver.make_response(
            status=response['code'], json=response['json'],
        )

    @mockserver.json_handler('/cargo-tasks/v1/billing/offer/list')
    async def _find_offer(request):
        assert request.query['client_id'] == const.BILLING_CLIENT_ID

        response = context.find_offer.get_response()
        return mockserver.make_response(
            status=response['code'], json=response['json'],
        )

    return context
