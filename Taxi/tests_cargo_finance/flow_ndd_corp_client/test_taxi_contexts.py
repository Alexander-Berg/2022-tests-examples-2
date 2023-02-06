import json

TAXI_CORP_V1_CLIENT_RESPONSE = {
    'client_id': '',
    'name': '',
    'contract_id': '',
    'billing_client_id': 'billing_client',
    'billing_contract_id': '',
    'services': {},
    'country': '',
}


async def test_taxi_corp_context(mockserver, taxi_cargo_finance):
    @mockserver.json_handler('/taxi-corp-integration/v1/client')
    def handler(request):
        return TAXI_CORP_V1_CLIENT_RESPONSE

    response = await taxi_cargo_finance.post(
        '/internal/cargo-finance/flow/ndd-corp-client/func/taxi-corp-context',
        params={'corp_client_id': 'client________________________32'},
    )
    assert response.status_code == 200
    assert handler.times_called == 1
    assert response.json()['context']['billing_client_id'] == 'billing_client'


async def test_taxi_agglomerations_context(mockserver, taxi_cargo_finance):
    @mockserver.json_handler(
        '/taxi-agglomerations/v1/geo_nodes/get_mvp_oebs_id',
    )
    def handler(request):
        return {'oebs_mvp_id': 'some_id'}

    response = await taxi_cargo_finance.post(
        '/internal/cargo-finance/flow/ndd-corp-client/func/taxi-agglomerations-context',  # noqa: E501
        params={'zone_id': 'moscow'},
    )

    assert response.status_code == 200
    assert handler.times_called == 1
    assert response.json()['context']['oebs_mvp_id'] == 'some_id'


async def test_taxi_billing_replication_context(
        mockserver, taxi_cargo_finance,
):
    @mockserver.handler('/billing-replication/v1/active-contracts/')
    def handler(request):
        return mockserver.make_response(json.dumps([{'ID': 123456}]), 200)

    response = await taxi_cargo_finance.post(
        '/internal/cargo-finance/flow/ndd-corp-client/func/taxi-billing-replication-context',  # noqa: E501
        {
            'billing_client_id': 'some_client_id',
            'order_instant': '1970-01-01T00:00:00+00:00',
        },
    )

    assert response.status_code == 200
    assert handler.times_called == 1
    assert response.json()['context']['billing_contract_id'] == '123456'
