import pytest

from test_payments_eda import consts


@pytest.fixture(name='mock_transactions_eda')
def _mock_transactions_eda(mockserver, load_json):
    def mock_maker(yandex_uid='yandex_uid', user_id='user_id'):
        @mockserver.json_handler('/transactions-eda/v2/invoice/retrieve')
        def _mock_invoice_retrieve(request):
            assert request.json['id'] == 'order_id'

            invoice = load_json('transactions_eda_invoice_retrieve.json')
            invoice['yandex_uid'] = yandex_uid
            invoice['id'] = 'order_id'
            invoice['service'] = 'grocery'
            invoice['external_user_info'] = {
                'origin': 'taxi',
                'user_id': user_id,
            }
            return invoice

        return _mock_invoice_retrieve

    return mock_maker


@pytest.fixture(name='mock_user_api')
def _mock_user_api(mockserver):
    def mock_maker(yandex_uid='yandex_uid', user_id='user_id'):
        @mockserver.json_handler('/user_api-api/users/get')
        def _mock_users_get(request):
            assert set(request.json['fields']) == {
                'phone_id',
                'application',
                'application_version',
                'yandex_uid',
            }
            return {
                'id': user_id,
                'yandex_uid': yandex_uid,
                'phone_id': 'phone_id',
                'application': 'iphone',
                'application_version': '600.3.0',
            }

        return _mock_users_get

    return mock_maker


@pytest.fixture(name='mock_order_status')
def _mock_order_status(mockserver):
    order_nr = r'(?P<order_id>[\w-]+)'

    def _with_status(status):
        @mockserver.json_handler(
            fr'/eda_superapp/internal-api/v1/order/{order_nr}/work-status',
            regex=True,
        )
        def _mock_status(request, order_id):
            return {'order_nr': order_id, 'status': status}

        return _mock_status

    return _with_status


@pytest.mark.parametrize(
    'exp_value, order_status, expected_status, expected_response',
    [
        pytest.param(
            {'enabled': True, 'rate': '0.05'},
            'finished',
            200,
            {
                'currency': 'RUB',
                'cashback': '50',
                'payload': {
                    'base_amount': '1000',
                    'order_id': 'order_id',
                    'cashback_service': 'go_grocery',
                },
            },
            id='cashback-enabled',
        ),
        pytest.param(
            {'enabled': True, 'rate': '0.05', 'instant_cashback': True},
            'finished',
            200,
            {
                'currency': 'RUB',
                'cashback': '100',
                'payload': {
                    'base_amount': '2000',
                    'order_id': 'order_id',
                    'cashback_service': 'go_grocery',
                },
            },
            id='instant-cashback',
        ),
        pytest.param(
            {'enabled': True, 'rate': '0'},
            'finished',
            200,
            {
                'currency': 'RUB',
                'cashback': '0',
                'payload': {
                    'base_amount': '1000',
                    'order_id': 'order_id',
                    'cashback_service': 'go_grocery',
                },
            },
            id='zero-rate',
        ),
        pytest.param(
            {'enabled': False}, 'finished', 409, None, id='cashback-disabled',
        ),
        pytest.param(None, 'finished', 409, None, id='exp-not-matched'),
        pytest.param(
            {'enabled': True}, 'in_work', 409, None, id='unfinished-order',
        ),
    ],
)
async def test_cashback_calc(
        web_app_client,
        client_experiments3,
        eda_doc_mockserver,
        mock_transactions_eda,
        mock_user_api,
        mock_order_status,
        exp_value,
        expected_status,
        expected_response,
        order_status,
):
    client_experiments3.add_record(
        consumer='payments_eda/cashback',
        experiment_name='superapp_cashback',
        args=[
            {'name': 'phone_id', 'type': 'string', 'value': 'phone_id'},
            {'name': 'yandex_uid', 'type': 'string', 'value': 'yandex_uid'},
            {'name': 'country_code', 'type': 'string', 'value': 'RU'},
            {'name': 'service', 'type': 'string', 'value': 'grocery'},
            {'name': 'application', 'type': 'application', 'value': 'iphone'},
            {
                'name': 'version',
                'type': 'application_version',
                'value': '600.3.0',
            },
        ],
        value=exp_value,
    )

    eda_doc_mockserver(
        {
            'country_code': 'RU',
            'uuid': 'some_uid',
            'service_product_id': 'eda_107819207_ride',
            'region_id': 123,
            'location': consts.LOCATION,
            'items': [
                {'amount': '10.50', 'currency': 'RUB', 'item_id': '123'},
            ],
        },
    )
    mock_order_status(order_status)
    mock_user_api()
    mock_transactions_eda()

    body = {'cleared': '1000', 'held': '1000', 'currency': 'RUB'}
    response = await web_app_client.post(
        '/v1/cashback/calc', params={'order_id': 'order_id'}, json=body,
    )
    assert response.status == expected_status
    if expected_response == 200:
        response_json = await response.json()
        assert response_json == expected_response
