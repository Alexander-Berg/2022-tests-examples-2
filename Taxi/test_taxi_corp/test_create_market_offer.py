import pytest


@pytest.mark.parametrize(
    ['passport_mock', 'expected_code', 'expected_response'],
    [
        pytest.param('client1', 200, {}),
        pytest.param(
            'client1', 400, {'code': 'bad_request', 'message': 'fail'},
        ),
        pytest.param('client1', 409, {'code': 'conflict', 'message': 'fail'}),
    ],
    indirect=['passport_mock'],
)
async def test_create_market_offer(
        taxi_corp_real_auth_client,
        passport_mock,
        mock_corp_requests,
        expected_code,
        expected_response,
):
    mock_corp_requests.data.market_offer_creation_code = expected_code
    mock_corp_requests.data.market_offer_creation_response = expected_response

    response = await taxi_corp_real_auth_client.post(
        '/1.0/client/client1/market-offer/create',
    )
    response_json = await response.json()
    assert response.status == expected_code, response_json
    assert response_json == expected_response

    if expected_code == 200:
        assert mock_corp_requests.market_offer.next_call()['request'].json == {
            'client_id': 'client1',
            'edo_operator': 'diadoc',
        }
