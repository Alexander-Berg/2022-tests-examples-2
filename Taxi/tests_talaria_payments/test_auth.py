import pytest


@pytest.mark.parametrize(
    'endpoint, method',
    [('create', 'POST'), ('retrieve', 'GET'), ('update', 'POST')],
)
@pytest.mark.parametrize(
    'api_key, ip_address, authorized',
    [
        ('wind_api_key', '1.1.1.1', True),
        ('wrong_api_key', '1.1.1.1', False),
        ('wind_api_key', '42.42.42.42', False),
    ],
)
async def test_auth(
        mockserver,
        taxi_talaria_payments,
        load_json,
        endpoint,
        method,
        api_key,
        ip_address,
        authorized,
):
    @mockserver.json_handler('.*', regex=True)
    def _any_endpoint(request):
        pass

    if method == 'POST':
        response = await taxi_talaria_payments.post(
            f'/talaria-payments/v1/payments/{endpoint}',
            json=load_json(f'payments_{endpoint}_request.json'),
            headers={'x-api-key': api_key, 'X-Real-IP': ip_address},
        )
    else:
        response = await taxi_talaria_payments.get(
            f'/talaria-payments/v1/payments/{endpoint}',
            params=load_json(f'payments_{endpoint}_request.json'),
            headers={'x-api-key': api_key, 'X-Real-IP': ip_address},
        )
    if authorized:
        assert response.status_code != 401
    else:
        assert response.status_code == 401
        assert response.json() == {
            'code': 'unauthorized',
            'message': 'unauthorized',
        }
