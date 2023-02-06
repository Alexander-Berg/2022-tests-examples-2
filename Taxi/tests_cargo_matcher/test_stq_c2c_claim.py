async def test_c2c_claim(
        mockserver,
        stq_runner,
        mock_finish_estimate,
        mock_claims_full,
        get_currency_rules,
        mock_int_api_profile,
):
    del mock_claims_full.response['corp_client_id']
    mock_claims_full.response['yandex_uid'] = 'yandex_uid_1'
    mock_claims_full.response['c2c_data'] = {
        'payment_type': 'applepay',
        'payment_method_id': '+70009999999',
    }

    mock_int_api_profile.expected_request = {
        'user': {
            'personal_phone_id': 'personal_phone_id_123',
            'yandex_uid': 'yandex_uid_1',
        },
        'name': 'Petya',
        'sourceid': 'cargo_c2c',
    }

    @mockserver.json_handler('/int-authproxy/v1/orders/estimate')
    def _orders_estimate(request):
        assert request.json == {
            'sourceid': 'cargo_c2c',
            'selected_class': 'express',
            'user': {
                'personal_phone_id': 'personal_phone_id_123',
                'user_id': 'taxi_user_id_1',
            },
            'payment': {
                'type': 'applepay',
                'payment_method_id': '+70009999999',
            },
            'requirements': {'door_to_door': True},
            'route': [[37.1, 55.1], [37.2, 55.3]],
        }
        return {
            'offer': 'taxi_offer_id_1',
            'is_fixed_price': True,
            'currency_rules': get_currency_rules,
            'service_levels': [{'class': 'express', 'price_raw': 999.001}],
        }

    await stq_runner.cargo_matcher_claim_estimating.call(
        task_id='claim_id_1', args=[],
    )

    assert mock_claims_full.mock.times_called == 1
    assert mock_int_api_profile.mock.times_called == 1
    assert _orders_estimate.times_called == 1
