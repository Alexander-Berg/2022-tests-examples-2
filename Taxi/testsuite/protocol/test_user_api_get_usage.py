import pytest


DRIVERTAG = 'c457f916dad5ed96dcc05e150df711ad5fdf0f7239a355531b07c45cabff7ef9'


@pytest.fixture(autouse=True)
def user_api_service_autouse(mockserver, config):
    config.set_values(
        dict(
            USER_API_USE_USER_PHONES_RETRIEVAL=True,
            USER_API_USE_USER_PHONES_BULK_RETRIEVAL=True,
            USER_API_CLIENT_USER_PHONES_TIMEOUT_MS=2000,
        ),
    )


@pytest.mark.config(
    USER_API_USER_PHONES_RETRIEVAL_ENDPOINTS={'__default__': True},
)
def test_get_referrals_user_api_call(taxi_protocol, mockserver, load_json):
    @mockserver.json_handler('/blackbox')
    def mock_blackbox(request):
        return {
            'uid': {'value': '4003514362'},
            'status': {'value': 'VALID'},
            'oauth': {'scope': 'yataxi:read yataxi:write yataxi:pay'},
            'aliases': {'10': 'phonish'},
            'phones': [
                {'attributes': {'102': '+79998887766'}, 'id': '1111'},
                {
                    'attributes': {'102': '+72222222222', '107': '1'},
                    'id': '2222',
                },
            ],
        }

    @mockserver.json_handler('/user-api/user_phones/get')
    def mock_user_api(request):
        assert request.json == {
            'id': '5714f45e98956f06baaaed42',
            'primary_replica': False,
        }
        return load_json('referrals_response.json')

    response = taxi_protocol.post(
        '3.0/getreferral',
        json={
            'id': 'b300bda7d41b4bae8d58dfa93221ef25',
            'format_currency': True,
        },
        bearer='test_token',
    )
    assert response.status_code == 406
    assert mock_user_api.times_called == 1


@pytest.mark.filldb(order_proc='vgw')
@pytest.mark.now('2018-02-25T00:00:00')
def test_base_vgw(taxi_protocol, mockserver):
    @mockserver.json_handler('/user-api/user_phones/get_bulk')
    def mock_user_api(request):
        assert request.json == {
            'ids': ['5714f45e98956f06baaae3d4'],
            'primary_replica': False,
        }
        return {
            'items': [
                {
                    'id': '5714f45e98956f06baaae3d4',
                    'phone': '+79031524201',
                    'type': 'yandex',
                },
            ],
        }

    # Mock calls to partner
    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def mock_redirections(request):
        return {'phone': '+75557775522', 'ext': '007'}

    # Call
    response = taxi_protocol.post(
        'voicegatewaysobtain',
        {
            'requests': [
                {
                    'order_id': '<order_id>',
                    'caller': 'user',
                    'callee': 'driver',
                    'callee_phone': '+79031524200',
                    'ttl_seconds_new': 2 * 60 * 60,
                    'ttl_seconds_min': 1 * 60 * 60,
                },
            ],
        },
    )
    # Check response
    assert response.status_code == 200
    assert response.json() == {
        'gateways': [
            {
                'gateway': {
                    'ext': '007',
                    'phone': '+75557775522',
                    'ttl_seconds': 7200,
                },
            },
        ],
    }
    assert mock_user_api.times_called == 1
