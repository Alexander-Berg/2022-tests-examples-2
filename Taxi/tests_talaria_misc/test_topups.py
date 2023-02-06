import pytest


async def test_topup(
        taxi_talaria_misc,
        mockserver,
        default_pa_headers,
        wind_user_auth_mock,
        wind_api_key,
):
    @mockserver.json_handler('/wind/pf/server/v1/yandexPayment/topup')
    def _mock_wind_topups(request):
        assert request.headers.get('x-api-key') == wind_api_key

        assert request.json == {
            'topup_id': 'topup_id_value',
            'operation_id': 'operation_id_value',
            'wind_user_id': '269f324a-7f9d-4d11-8f8e-7352b411767e',
            'yandex_uid': 'yandex_uid',
            'payment_method': {'id': 'payment_method_id', 'type': 'card'},
            'antifraud_data': {
                'user_ip': '1.2.3.4',
                'yandex_login_id': 'login_id',
            },
        }
        return {'result': 0}

    response = await taxi_talaria_misc.post(
        '/4.0/scooters/v1/wind-wallet/v1/topup',
        json={
            'topup_id': 'topup_id_value',
            'operation_id': 'operation_id_value',
            'payment_method': {'id': 'payment_method_id', 'type': 'card'},
        },
        headers=default_pa_headers(),
    )

    assert response.status_code == 200
    assert response.json() == {}
    assert _mock_wind_topups.times_called == 1


@pytest.mark.parametrize(
    'status', ['pending', 'success', 'failed', 'not_found'],
)
async def test_topup_status(
        taxi_talaria_misc,
        mockserver,
        default_pa_headers,
        wind_user_auth_mock,
        status,
):
    @mockserver.json_handler('/wind/pf/server/v1/yandexPayment/topup/status')
    def _mock_wind_topups_status(request):
        assert request.query == {'operation_id': 'operation_id_value'}
        if status == 'not_found':
            return mockserver.make_response(status=404)
        return {'result': 0, 'status': status}

    response = await taxi_talaria_misc.get(
        '/4.0/scooters/v1/wind-wallet/v1/topup/status',
        params={'operation_id': 'operation_id_value'},
        headers=default_pa_headers(),
    )
    if status == 'not_found':
        assert response.status_code == 404
    else:
        assert response.status_code == 200
        assert response.json() == {'status': status}
    assert _mock_wind_topups_status.times_called == 1


@pytest.mark.config(
    TALARIA_MISC_WALLET_SETTINGS={'stories_info_tag': 'stories_info_tag'},
)
async def test_200_wallet_status(
        taxi_talaria_misc,
        mockserver,
        load_json,
        default_pa_headers,
        wind_user_auth_mock,
):
    @mockserver.json_handler('/wind/pf/v1/user')
    def _mock_wind_pf_get_user(request):
        return load_json('wind_pf_v1_user_response_default.json')

    @mockserver.json_handler('/wind/pf/v1/topUps')
    def _mock_wind_topups(request):
        return {
            'reason': 'succeed',
            'result': 0,
            'items': [
                {
                    'billingDescText': '€10 for Top up WIND',
                    'billingTitleText': '€10 for Top up WIND',
                    'bonus': 60,
                    'currency': 'ils',
                    'descText': 'WIND top up € 10 Get €0.6',
                    'isSpecial': 0,
                    'price': 1000,
                    'titleText': 'Top up € 10 Get €0.6!',
                    'topUpId': 'topup100_ils',
                    'walletTitleText': 'Get €0.6 bonus',
                },
            ],
        }

    response = await taxi_talaria_misc.get(
        '/4.0/scooters/v1/wind-wallet/v1/status',
        headers={'x-yataxi-scooters-tag': 'wind', **default_pa_headers('123')},
    )

    assert response.status_code == 200
    assert response.json() == {
        'currency_rules': {
            'code': 'ILS',
            'sign': '₪',
            'template': '$SIGN$$VALUE$ $CURRENCY$',
            'text': 'shekel',
        },
        'balance': 100,
        'topups': [
            {
                'topup_id': 'topup100_ils',
                'price': 10.0,
                'bonus': 0.6,
                'currency': 'ils',
            },
        ],
        'stories_info_tag': 'stories_info_tag',
    }
    assert _mock_wind_pf_get_user.times_called == 1
    assert _mock_wind_topups.times_called == 1
