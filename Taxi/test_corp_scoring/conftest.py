# pylint: disable=redefined-outer-name
import dataclasses
import datetime

import pytest

import corp_scoring.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['corp_scoring.generated.service.pytest_plugins']
LONG_CONTRACT = '333/33aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
CONTRACTS = {
    '111/11': [
        {
            'contract_id': 1,
            'billing_client_id': 'billing_id_1',
            'billing_person_id': '10001',
            'payment_type': 'prepaid',
            'services': ['taxi'],
            'currency': 'RUB',
            'external_id': '111/11',
            'is_offer': True,
            'created': '2020-11-01T18:00:00+03:00',
        },
        {
            'contract_id': 2,
            'billing_client_id': 'billing_id_2',
            'billing_person_id': '10002',
            'payment_type': 'prepaid',
            'services': ['taxi'],
            'currency': 'RUB',
            'external_id': '111/11',
            'is_offer': True,
            'created': '2020-11-01T19:00:00+03:00',
        },
    ],
    LONG_CONTRACT: [
        {
            'contract_id': 3,
            'billing_client_id': 'billing_id_3',
            'billing_person_id': '10003',
            'payment_type': 'prepaid',
            'services': ['taxi'],
            'currency': 'RUB',
            'external_id': LONG_CONTRACT,
            'is_offer': True,
            'created': '2020-11-01T20:00:00+03:00',
        },
    ],
    '555/55': [
        {
            'contract_id': 5,
            'billing_client_id': 'billing_id_5',
            'billing_person_id': '10004',
            'payment_type': 'postpaid',
            'services': ['taxi'],
            'currency': 'RUB',
            'external_id': '555/55',
            'is_offer': False,
            'created': '2020-11-01T21:00:00+03:00',
        },
    ],
    '444/44': [
        {
            'contract_id': 4,
            'billing_client_id': 'billing_id_5',
            'billing_person_id': '10005',
            'payment_type': 'prepaid',
            'services': ['taxi'],
            'currency': 'RUB',
            'external_id': '444/44',
            'is_offer': True,
            'created': '2020-11-01T22:00:00+03:00',
        },
    ],
}

EXP_NAME = 'corp_welcome_overdraft_exp'


class ExpSimple:
    name = EXP_NAME


EXP_CONTRACTS = {2: [ExpSimple()], 3: [], 4: [ExpSimple()]}


@pytest.fixture
def mock_corp_clients(mockserver):
    class MockCorpClients:
        @dataclasses.dataclass
        class CorpClientsData:
            get_contracts_response: dict
            clients_list: dict

        data = CorpClientsData(
            get_contracts_response={},
            clients_list={
                'clients': [],
                'skip': 0,
                'limit': 50,
                'amount': 0,
                'sort_field': 'name',
                'sort_direction': 1,
                'search': 'corp_client_2',
            },
        )

        @staticmethod
        @mockserver.json_handler('/corp-clients/v1/contracts/by-external-ids')
        async def get_contracts(request):
            ext_contract_ids = request.json['contract_external_ids']
            contract_list = []
            for ext_contract_id in ext_contract_ids:
                contract_list.extend(CONTRACTS.get(ext_contract_id, []))
            return mockserver.make_response(
                json={'contracts': contract_list}, status=200,
            )

        @staticmethod
        @mockserver.json_handler('/corp-clients/v1/contracts/created-since')
        async def get_contracts_created_since(request):
            created_since = request.query.get('created_since')
            contract_list = []
            for contracts in CONTRACTS.values():
                contract_list.extend(contracts)

            contract_list = [
                contract
                for contract in contract_list
                if datetime.datetime.fromisoformat(contract['created'])
                >= datetime.datetime.fromisoformat(created_since)
            ]

            return mockserver.make_response(
                json={'contracts': contract_list}, status=200,
            )

        @staticmethod
        @mockserver.json_handler('/corp-clients/v1/contracts/threshold/update')
        async def update_thresholds(request):
            return mockserver.make_response(json={}, status=200)

    return MockCorpClients()


@pytest.fixture
def mock_exp3_get_values(patch):
    @patch('taxi.clients.experiments3.Experiments3Client.get_values')
    async def _get_values(
            consumer,
            experiments_args,
            client_application=None,
            user_agent=None,
            log_extra=None,
    ):
        contract_id = experiments_args[0].value
        return EXP_CONTRACTS[contract_id]

    return _get_values
