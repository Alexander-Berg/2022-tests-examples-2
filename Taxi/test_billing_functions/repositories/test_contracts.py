import datetime as dt

import pytest

from billing_functions.repositories import contracts as contracts_repo


async def test_billing_replication_repo(stq3_context, mockserver):
    request_query = None

    @mockserver.json_handler('/billing-replication/v1/active-contracts/')
    def _active_contracts(request):
        nonlocal request_query
        request_query = request.query
        return mockserver.make_response(
            status=200,
            json=[
                {
                    'ID': 1,
                    'CURRENCY': 'RUB',
                    'SERVICES': [1],
                    'DT': '2021-05-17T00:00:00',
                    'FIRM_ID': 1,
                },
                {
                    'ID': 2,
                    'CURRENCY': 'RUB',
                    'SERVICES': [1, 2],
                    'DT': '2021-05-18T00:00:00',
                    'FIRM_ID': 2,
                },
            ],
        )

    contracts = await stq3_context.contracts.get_contracts(
        billing_client_id='1',
        active_ts=dt.datetime(2021, 5, 17, tzinfo=dt.timezone.utc),
        actual_ts=dt.datetime(2021, 5, 18, tzinfo=dt.timezone.utc),
        service_ids=[1, 2, 3],
        service_ids_prev_active=[1, 2],
    )
    assert request_query == {
        'client_id': '1',
        'active_ts': '2021-05-17T00:00:00.000000+00:00',
        'actual_ts': '2021-05-18T00:00:00.000000+00:00',
        'service_id': '1,2,3',
        'service_id_prev_active': '1,2',
    }
    assert contracts == [
        contracts_repo.Contract(
            id=1,
            currency='RUB',
            service_ids=[1],
            begin=dt.datetime(2021, 5, 16, 21, 0, tzinfo=dt.timezone.utc),
            firm_id=1,
            is_yandex_bank_enabled=False,
        ),
        contracts_repo.Contract(
            id=2,
            currency='RUB',
            service_ids=[1, 2],
            begin=dt.datetime(2021, 5, 17, 21, 0, tzinfo=dt.timezone.utc),
            firm_id=2,
            is_yandex_bank_enabled=False,
        ),
    ]


@pytest.mark.parametrize(
    'test_data_json', ['no_contracts.json', 'some_contracts.json'],
)
@pytest.mark.json_obj_hook(Contract=contracts_repo.Contract)
def test_select_latest_contract_per_service(load_py_json, test_data_json):
    test_data = load_py_json(test_data_json)
    result = contracts_repo.select_latest_per_service(test_data['contracts'])
    assert result == test_data['expected_result']


@pytest.mark.parametrize('test_data_json', ['ambiguous_contracts.json'])
@pytest.mark.json_obj_hook(Contract=contracts_repo.Contract)
def test_ambiguous_contract_per_service(load_py_json, test_data_json):
    test_data = load_py_json(test_data_json)
    with pytest.raises(ValueError):
        contracts_repo.select_latest_per_service(test_data['contracts'])
