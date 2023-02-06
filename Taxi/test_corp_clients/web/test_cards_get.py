import pytest

from test_corp_clients.web import test_utils


@pytest.mark.parametrize(
    ['client_id', 'main_payment_method_id'],
    [
        pytest.param('client_id_1', 'card-123-long'),
        pytest.param('client_id_2', None),
    ],
)
async def test_cards(
        web_app_client,
        load_json,
        blackbox_mock,
        patch,
        client_id,
        main_payment_method_id,
):
    @patch('taxi.clients.billing_v2.BalanceClient.get_bound_payment_methods')
    async def _get_bound_payment_methods(operator_uid, service_id):
        return test_utils.GET_BOUND_PAYMENT_METHODS_RESP

    response = await web_app_client.get(
        '/v1/cards/list', params={'client_id': client_id},
    )
    assert response.status == 200
    response_json = await response.json()
    expected_cards = load_json('expected_cards.json')

    assert response_json['cards'] == expected_cards

    if main_payment_method_id is not None:
        assert (
            response_json['main_payment_method_id'] == main_payment_method_id
        )
    else:
        assert 'main_payment_method_id' not in response_json


async def test_cards_not_found(
        web_app_client, load_json, blackbox_mock, patch,
):
    response = await web_app_client.get(
        '/v1/cards/list', params={'client_id': 'client_id_xxx'},
    )
    assert response.status == 404
