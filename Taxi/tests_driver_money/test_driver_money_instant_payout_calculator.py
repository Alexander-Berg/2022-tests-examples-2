import pytest


@pytest.mark.now('2019-06-02T12:00:00+0300')
@pytest.mark.parametrize(
    'instant_payouts_preview,expected_response',
    [
        (
            {
                'status': 'ready',
                'amount_minimum': '100',
                'amount_maximum': '500',
                'fee_percent': '5',
                'fee_minimum': '50',
                'withdrawal_amount': '200',
                'debit_amount': '200',
                'debit_fee': '10',
                'transfer_amount': '200',
                'cards': [
                    {
                        'id': '00000000-0000-0000-0000-000000000001',
                        'is_last_used': True,
                        'masked_pan': '123456***7890',
                        'issuer': 'visa',
                    },
                    {
                        'id': '11111111-1111-1111-1111-111111111111',
                        'is_last_used': False,
                        'masked_pan': '987654***3210',
                        'issuer': 'mir',
                    },
                ],
                'last_payout_method': 'card',
                'last_phone_pd_id': 'id1',
                'sbp_banks': [
                    {
                        'id': '1',
                        'name_en': 'bank1',
                        'name_ru': 'банк1',
                        'is_last_used': True,
                        'how_to_link': 'http://bank1/howto',
                    },
                    {
                        'id': '2',
                        'name_en': 'bank2',
                        'name_ru': 'банк2',
                        'is_last_used': False,
                    },
                ],
            },
            'expected_response.json',
        ),
    ],
)
async def test_driver_money_instant_payout_list(
        taxi_driver_money,
        instant_payouts_preview,
        expected_response,
        load_json,
        mockserver,
):
    @mockserver.json_handler(
        '/contractor-instant-payouts/v1/contractors/payouts/preview',
    )
    def _mock_instant_payouts_list(_):
        return instant_payouts_preview

    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def _mock_personal(_):
        return {'id': 'id1', 'value': '+70000000000'}

    response = await taxi_driver_money.get(
        'driver/v1/driver-money/v1/instant-payouts/calculator',
        params={'amount': '200'},
        headers={
            'User-Agent': 'Taximeter 8.90 (228)',
            'Accept-Language': 'ru',
            'X-Request-Application-Version': '8.90',
            'X-YaTaxi-Park-Id': 'park_id_0',
            'X-YaTaxi-Driver-Profile-Id': 'driver',
        },
    )
    assert response.status_code == 200
    assert response.json() == load_json(expected_response)


@pytest.mark.now('2019-06-02T12:00:00+0300')
@pytest.mark.parametrize(
    'instant_payouts_preview,expected_response',
    [
        (
            {
                'status': 'ready',
                'amount_minimum': '100',
                'amount_maximum': '500',
                'fee_percent': '5',
                'fee_minimum': '50',
                'withdrawal_amount': '200',
                'debit_amount': '200',
                'debit_fee': '10',
                'transfer_amount': '200',
                'cards': [],
            },
            'expected_response_no_item_card.json',
        ),
    ],
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='instant_payouts_hide_item_card',
    consumers=['driver_money/v1_driver_balance_main_filtered'],
    clauses=[],
    default_value={'enabled': True},
    is_config=True,
)
async def test_driver_money_instant_payout_calculator_no_item_card(
        taxi_driver_money,
        instant_payouts_preview,
        expected_response,
        load_json,
        mockserver,
):
    @mockserver.json_handler(
        '/contractor-instant-payouts/v1/contractors/payouts/preview',
    )
    def _mock_instant_payouts_list(_):
        return instant_payouts_preview

    response = await taxi_driver_money.get(
        'driver/v1/driver-money/v1/instant-payouts/calculator',
        params={'amount': '200'},
        headers={
            'User-Agent': 'Taximeter 8.90 (228)',
            'Accept-Language': 'ru',
            'X-Request-Application-Version': '8.90',
            'X-YaTaxi-Park-Id': 'park_id_0',
            'X-YaTaxi-Driver-Profile-Id': 'driver',
        },
    )
    assert response.status_code == 200
    assert response.json() == load_json(expected_response)
