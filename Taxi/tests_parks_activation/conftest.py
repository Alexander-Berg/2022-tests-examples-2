# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from parks_activation_plugins import *  # noqa: F403 F401


@pytest.fixture(autouse=True)
def billing_replication_mock_server(mockserver, load_json):
    clients = [
        {'park_id': '100', 'client_id': '103917439', 'revision': 1},
        {'park_id': '200', 'client_id': '105352633', 'revision': 4399509443},
        {'park_id': '300', 'client_id': '106917439', 'revision': 1},
        {'park_id': '400', 'client_id': '106917440', 'revision': 1},
    ]
    contracts = [
        {
            'ID': 553918,
            'client_id': '103917439',
            'type': 'GENERAL',
            'IS_ACTIVE': 1,
            'PAYMENT_TYPE': 2,
            'CURRENCY': 'RUR',
            'NETTING': 1,
            'SERVICES': [128, 124, 125, 605, 111],
            'status': 'ACTIVE',
            'revision': 1,
            'FINISH_DT': '2020-11-10 00:00:00',
        },
        {
            'ID': 553918,
            'client_id': '103917439',
            'type': 'GENERAL',
            'IS_ACTIVE': 1,
            'PAYMENT_TYPE': 2,
            'CURRENCY': 'RUR',
            'NETTING': 1,
            'SERVICES': [1161, 1162, 1163],
            'status': 'ACTIVE',
            'revision': 1,
            'FINISH_DT': '2020-11-10 00:00:00',
        },
        {
            'ID': 553920,
            'client_id': '105352633',
            'type': 'GENERAL',
            'IS_ACTIVE': 1,
            'CURRENCY': 'RUR',
            'NETTING': 1,
            'SERVICES': [128, 124, 125, 605, 111],
            'status': 'ACTIVE',
            'revision': 2,
        },
        {
            'ID': 553922,
            'client_id': '106917439',
            'type': 'GENERAL',
            'IS_ACTIVE': 0,
            'IS_SIGNED': 1,
            'PAYMENT_TYPE': 2,
            'CURRENCY': 'RUR',
            'NETTING': 1,
            'SERVICES': [128, 124, 125, 605, 111],
            'status': 'ACTIVE',
            'revision': 1,
            'DT': '2020-01-01 00:00:00',
        },
        {
            'ID': 553923,
            'client_id': '106917440',
            'type': 'GENERAL',
            'IS_ACTIVE': 0,
            'IS_SIGNED': 1,
            'IS_FAXED': 1,
            'PAYMENT_TYPE': 2,
            'CURRENCY': 'RUR',
            'NETTING': 1,
            'SERVICES': [1161, 1162, 1163],
            'status': 'ACTIVE',
            'revision': 1,
            'FINISH_DT': '2022-02-20 00:00:00',
        },
    ]
    balances = [
        {
            'ContractID': 553918,
            'Balance': '0',
            'CommissionToPay': None,
            'NettingLastDt': '2020-05-15 00:00:00',
            'revision': 1,
        },
        {
            'ContractID': 553922,
            'Balance': '10000',
            'CommissionToPay': None,
            'NettingLastDt': '2020-05-15 00:00:00',
            'revision': 1,
        },
    ]

    def make_response(request, field, items):
        items_for_response = [
            item
            for item in items
            if item['revision'] > int(request.args['revision'])
        ][: int(request.args['limit'])]
        return {
            field: [item for item in items_for_response],
            'max_revision': (
                max(item['revision'] for item in items_for_response)
                if items_for_response
                else 0
            ),
        }

    @mockserver.json_handler('/billing-replication/v1/clients/by_revision/')
    def _mock_clients_by_revision(request):
        return make_response(request, 'clients', clients)

    @mockserver.json_handler('/billing-replication/v1/contracts/by_revision/')
    def _mock_contracts_by_revision(request):
        return make_response(request, 'contracts', contracts)

    @mockserver.json_handler('/billing-replication/v1/balances/by_revision/')
    def _mock_balances_by_revision(request):
        return make_response(request, 'balances', balances)

    @mockserver.json_handler('/billing-replication/v2/balances/by_revision/')
    def _mock_v2_balances_by_revision(request):
        revision = int(request.json['revision'])
        if revision != 0:
            return mockserver.make_response(
                status=200, json={'max_revision': revision, 'balances': []},
            )
        return mockserver.make_response(
            status=200, json=load_json('balances_v2.json'),
        )

    @mockserver.json_handler(
        'parks-replica/v1/parks/billing_client_id_history/retrieve',
    )
    def _mock_v1_parks_billing_client_id_history_retrieve(request):
        if request.args['park_id'] == '100':
            return {
                'billing_client_ids': [
                    {
                        'billing_client_id': '103917439',
                        'start': None,
                        'end': '2020-11-09T21:00:00+0000',
                    },
                ],
            }
        return {
            'billing_client_ids': [
                {'billing_client_id': '106917440', 'start': None, 'end': None},
            ],
        }


@pytest.fixture(autouse=True)
def reset_revision(testpoint):
    @testpoint('parks-activation::reset-parks-activation-cache-revision')
    def _reset_revision(data):
        pass
