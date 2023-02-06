import pytest


@pytest.mark.parametrize('payment_type', ['card', 'mobile'])
async def test_payment_debt(
        taxi_talaria_misc,
        mockserver,
        default_pa_headers,
        wind_user_auth_mock,
        payment_type,
        pgsql,
):
    @mockserver.json_handler('/wind/pf/server/v1/yandexPayment/topup')
    def _mock_wind_topups(request):
        assert request.headers.get('x-api-key') == 'windapikey'

        assert request.json['topup_id'] == 'payPerRide'
        assert (
            request.json['wind_user_id']
            == '269f324a-7f9d-4d11-8f8e-7352b411767e'
        )
        assert request.json['yandex_uid'] == 'yandex_uid'
        if payment_type == 'card':
            assert request.json['payment_method'] == {
                'id': 'card_id',
                'type': 'card',
            }
        else:
            assert request.json['payment_method'] == {
                'id': 'apple_id',
                'type': 'applepay',
            }
        assert 'operation_id' in request.json
        return {'result': 0}

    @mockserver.json_handler(
        '/stq-agent/queues/api/add/talaria_misc_debts_payment_polling',
    )
    def _mock_debts_payment_polling(request):
        kwargs = request.json['kwargs']
        assert kwargs['personal_phone_id'] == 'phone_pd_id'
        assert kwargs['yandex_uid'] == 'yandex_uid'
        assert 'operation_id' in kwargs
        return {}

    if payment_type == 'card':
        payload = {'paymethod_id': 'card_id'}
    else:
        payload = {'mobile_paymethod_id': 'apple_id'}

    response = await taxi_talaria_misc.post(
        '/4.0/scooters/v1/payment/debts',
        json=payload,
        headers={'lon': '32.1', 'lat': '12.3', **default_pa_headers()},
    )
    assert response.status_code == 200
    assert _mock_wind_topups.times_called == 1
    assert _mock_debts_payment_polling.times_called == 1

    cursor = pgsql['talaria_misc'].cursor()
    cursor.execute(
        f'SELECT wind_user_id, payment_status ' f'FROM talaria_misc.debts;',
    )
    assert cursor.fetchall() == [
        ('269f324a-7f9d-4d11-8f8e-7352b411767e', 'pending'),
    ]


@pytest.mark.parametrize(
    'expected_call_count',
    [
        pytest.param(
            0,
            marks=(
                pytest.mark.pgsql(
                    'talaria_misc', files=['user_pending_debts.sql'],
                ),
            ),
            id='pending',
        ),
        pytest.param(
            1,
            marks=(
                pytest.mark.pgsql(
                    'talaria_misc', files=['user_init_debts.sql'],
                ),
            ),
            id='init',
        ),
    ],
)
async def test_concurrent_debt(
        taxi_talaria_misc,
        mockserver,
        default_pa_headers,
        wind_user_auth_mock,
        pgsql,
        expected_call_count,
):
    @mockserver.json_handler('/wind/pf/server/v1/yandexPayment/topup')
    def _mock_wind_topups(request):
        assert request.json['operation_id'] == 'operation_id'
        return {'result': 0}

    @mockserver.json_handler(
        '/stq-agent/queues/api/add/talaria_misc_debts_payment_polling',
    )
    def _mock_debts_payment_polling(request):
        assert request.json['kwargs']['operation_id'] == 'operation_id'
        return {}

    response = await taxi_talaria_misc.post(
        '/4.0/scooters/v1/payment/debts',
        json={'paymethod_id': 'card_id'},
        headers={'lon': '32.1', 'lat': '12.3', **default_pa_headers()},
    )
    assert response.status_code == 200
    assert _mock_wind_topups.times_called == expected_call_count
    assert _mock_debts_payment_polling.times_called == expected_call_count
