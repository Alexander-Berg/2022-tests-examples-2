import pytest


@pytest.mark.parametrize(
    'wind_result, expected_status_code, expected_json, expected_retry_after',
    [
        pytest.param(0, 200, {'operation_id': 'operation_id'}, None, id='ok'),
        pytest.param(
            -146,
            404,
            {
                'reason': {
                    'code': 'ERROR_FREEPASS_NOT_EXIST',
                    'description': 'Free pass is missing',
                    'title': 'Title',
                },
            },
            None,
            id='not_found',
        ),
        pytest.param(
            -3000,
            404,
            {
                'reason': {
                    'code': 'ERROR_FREE_PASS_NOT_EXIST',
                    'description': 'Free pass is missing',
                    'title': 'Title',
                },
            },
            None,
            id='also_not_found',
        ),
        pytest.param(
            -802,
            409,
            {'operation_id': 'unknown_operation_id'},
            None,
            id='duplicate',
        ),
        pytest.param(
            -147,
            429,
            {
                'reason': {
                    'code': 'DEFAULT_ERROR',
                    'description': 'Subtitle',
                    'title': 'Title',
                },
            },
            1,
            id='duplicate',
        ),
        pytest.param(
            1,
            500,
            {
                'reason': {
                    'code': 'DEFAULT_ERROR',
                    'description': 'Subtitle',
                    'title': 'Title',
                },
            },
            1,
            id='not_ok',
        ),
    ],
)
@pytest.mark.translations(
    client_messages={
        'talaria.error.title.payment_passes_post': {'en': 'Title'},
        'talaria.error.subtitle.default_error': {'en': 'Subtitle'},
        'talaria.error.subtitle.payment_passes_post'
        '.error_freepass_not_exist': {'en': 'Free pass is missing'},
        'talaria.error.subtitle.payment_passes_post.'
        'error_free_pass_not_exist': {'en': 'Free pass is missing'},
    },
)
async def test_payment_passes(
        taxi_talaria_misc,
        mockserver,
        default_pa_headers,
        wind_user_auth_mock,
        wind_result,
        expected_status_code,
        expected_retry_after,
        expected_json,
):
    @mockserver.json_handler('/wind/pf/server/v1/yandexPayment/freepasses')
    def _mock_wind_client(request):
        assert request.headers.get('x-api-key') == 'windapikey'
        assert request.json == {
            'antifraud_data': {
                'user_ip': '1.2.3.4',
                'yandex_login_id': 'login_id',
            },
            'free_pass_id': 'pass_id',
            'operation_id': 'operation_id',
            'payment_method': {'id': '123', 'type': 'card'},
            'user_location': {'latitude': 12.3, 'longitude': 32.1},
            'wind_user_id': '269f324a-7f9d-4d11-8f8e-7352b411767e',
            'yandex_uid': 'yandex_uid',
            'is_auto_reload': 0,
        }
        return {'result': wind_result}

    response = await taxi_talaria_misc.post(
        '/4.0/scooters/v1/payment/passes',
        json={
            'operation_id': 'operation_id',
            'pass_id': 'pass_id',
            'payment_method': {'type': 'card', 'id': '123'},
        },
        headers={'lon': '32.1', 'lat': '12.3', **default_pa_headers()},
    )
    assert _mock_wind_client.times_called == 1
    assert response.status_code == expected_status_code
    assert response.json() == expected_json
    if expected_retry_after:
        assert response.headers['retry-after'] == str(expected_retry_after)
    else:
        assert 'retry-after' not in response.headers


@pytest.mark.parametrize(
    'subscribe, expected_is_auto_reload',
    [
        pytest.param(True, 1, id='subscription_enabled'),
        pytest.param(False, 0, id='subscription_disabled'),
    ],
)
async def test_subscribe_field(
        taxi_talaria_misc,
        mockserver,
        default_pa_headers,
        wind_user_auth_mock,
        subscribe,
        expected_is_auto_reload,
):
    @mockserver.json_handler('/wind/pf/server/v1/yandexPayment/freepasses')
    def _mock_wind_client(request):
        assert request.json['is_auto_reload'] == expected_is_auto_reload
        return {'result': 0}

    response = await taxi_talaria_misc.post(
        '/4.0/scooters/v1/payment/passes',
        json={
            'operation_id': 'operation_id',
            'pass_id': 'pass_id',
            'payment_method': {'type': 'card', 'id': '123'},
            'subscribe': subscribe,
        },
        headers={'lon': '32.1', 'lat': '12.3', **default_pa_headers()},
    )
    assert _mock_wind_client.times_called == 1
    assert response.status_code == 200


@pytest.mark.parametrize(
    'status', ['pending', 'success', 'failed', 'not_found'],
)
async def test_payment_status(
        taxi_talaria_misc,
        mockserver,
        default_pa_headers,
        wind_user_auth_mock,
        status,
):
    @mockserver.json_handler(
        '/wind/pf/server/v1/yandexPayment/freepasses/paymentStatus',
    )
    def _mock_wind_client(request):
        assert request.headers.get('x-api-key') == 'windapikey'
        assert request.query == {'operation_id': 'operation_id'}
        if status == 'not_found':
            return mockserver.make_response(status=404)
        if status == 'failed':
            return {
                'result': 0,
                'status': status,
                'payment_error_reason': {
                    'code': 'code',
                    'description': 'decr',
                },
            }
        return {'result': 0, 'status': status}

    response = await taxi_talaria_misc.get(
        '/4.0/scooters/v1/payment/passes/status',
        params={'operation_id': 'operation_id'},
        headers=default_pa_headers(),
    )
    assert _mock_wind_client.times_called == 1
    if status == 'not_found':
        assert response.status_code == 404
        return

    assert response.status_code == 200
    data = response.json()
    if status == 'failed':
        assert data == {
            'status': status,
            'reason': {
                'code': 'code',
                'description': 'decr',
                'title': 'Couldn\'t complete payment',
            },
        }
    else:
        assert data == {'status': status}
