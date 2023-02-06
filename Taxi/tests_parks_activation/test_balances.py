import pytest


async def test_success(taxi_parks_activation):
    response = await taxi_parks_activation.get(
        '/v1/parks/activation/balances', params={'park_id': '100'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'balances': [
            {'contract_id': 553918, 'balance': '0', 'currency': 'RUB'},
        ],
        'threshold': '10.1',
        'threshold_dynamic': '35',
    }


async def test_unknown_park_id(taxi_parks_activation):
    response = await taxi_parks_activation.get(
        '/v1/parks/activation/balances', params={'park_id': 'wrong_park_id'},
    )
    assert response.status_code == 404


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


async def test_multiple_dataset_1(mockserver, taxi_parks_activation):
    @mockserver.json_handler('/billing-replication/v1/clients/by_revision/')
    def _mock_clients_by_revision(request):
        return make_response(
            request,
            'clients',
            [
                {'park_id': '100', 'client_id': '103917439', 'revision': 1},
                {
                    'park_id': '200',
                    'client_id': '105352633',
                    'revision': 4399509443,
                },
            ],
        )

    @mockserver.json_handler('/billing-replication/v1/contracts/by_revision/')
    def _mock_contracts_by_revision(request):
        return make_response(
            request,
            'contracts',
            [
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
            ],
        )

    @mockserver.json_handler('/billing-replication/v1/balances/by_revision/')
    def _mock_balances_by_revision(request):
        return make_response(
            request,
            'balances',
            [
                {
                    'ContractID': 553918,
                    'Balance': '0',
                    'CommissionToPay': None,
                    'NettingLastDt': '2020-05-15 00:00:00',
                    'revision': 1,
                },
            ],
        )

    response = await taxi_parks_activation.get(
        '/v1/parks/activation/balances', params={'park_id': '100'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'balances': [],
        'threshold': '10.1',
        'threshold_dynamic': '35',
    }


async def test_multiple_dataset_2(mockserver, taxi_parks_activation):
    @mockserver.json_handler('/billing-replication/v1/clients/by_revision/')
    def _mock_clients_by_revision(request):
        return make_response(
            request,
            'clients',
            [{'park_id': '100', 'client_id': '103917439', 'revision': 1}],
        )

    @mockserver.json_handler('/billing-replication/v1/contracts/by_revision/')
    def _mock_contracts_by_revision(request):
        return make_response(
            request,
            'contracts',
            [
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
            ],
        )

    @mockserver.json_handler('/billing-replication/v1/balances/by_revision/')
    def _mock_balances_by_revision(request):
        return make_response(
            request,
            'balances',
            [
                {
                    'ContractID': 553918,
                    'Balance': None,
                    'CommissionToPay': None,
                    'NettingLastDt': '2020-05-15 00:00:00',
                    'revision': 1,
                },
            ],
        )

    response = await taxi_parks_activation.get(
        '/v1/parks/activation/balances', params={'park_id': '100'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'balances': [{'contract_id': 553918, 'currency': 'RUB'}],
        'threshold': '10.1',
        'threshold_dynamic': '35',
    }


async def test_multiple_dataset_3(mockserver, taxi_parks_activation):
    @mockserver.json_handler('/billing-replication/v1/clients/by_revision/')
    def _mock_clients_by_revision(request):
        return make_response(
            request,
            'clients',
            [{'park_id': '100', 'client_id': '103917439', 'revision': 1}],
        )

    @mockserver.json_handler('/billing-replication/v1/contracts/by_revision/')
    def _mock_contracts_by_revision(request):
        return make_response(
            request,
            'contracts',
            [
                {
                    'ID': 553918,
                    'client_id': '103917439',
                    'type': 'GENERAL',
                    'IS_ACTIVE': 1,
                    'PAYMENT_TYPE': 2,
                    'CURRENCY': None,
                    'NETTING': 1,
                    'SERVICES': [128, 124, 125, 605, 111],
                    'status': 'ACTIVE',
                    'revision': 1,
                    'FINISH_DT': '2020-11-10 00:00:00',
                },
            ],
        )

    @mockserver.json_handler('/billing-replication/v1/balances/by_revision/')
    def _mock_balances_by_revision(request):
        return make_response(
            request,
            'balances',
            [
                {
                    'ContractID': 553918,
                    'Balance': '10',
                    'CommissionToPay': None,
                    'NettingLastDt': '2020-05-15 00:00:00',
                    'revision': 1,
                },
            ],
        )

    response = await taxi_parks_activation.get(
        '/v1/parks/activation/balances', params={'park_id': '100'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'balances': [{'contract_id': 553918, 'balance': '10'}],
        'threshold': '10.1',
        'threshold_dynamic': '35',
    }


@pytest.mark.pgsql(
    'parks_activation', files=['pg_parks_activation_without_threshold.sql'],
)
async def test_multiple_dataset_4(taxi_parks_activation):
    response = await taxi_parks_activation.get(
        '/v1/parks/activation/balances', params={'park_id': '100'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'balances': [
            {'contract_id': 553918, 'balance': '0', 'currency': 'RUB'},
        ],
    }
