from aiohttp import web
import pytest

from eats_tips_withdrawal.common import constants
from test_eats_tips_withdrawal import conftest


ROUBLES_CURRENCY_RULES = {
    'code': 'RUB',
    'sign': '₽',
    'template': '$VALUE$&nbsp$SIGN$$CURRENCY$',
    'text': 'руб.',
}
JWTS = {'00000000-0000-0000-0000-000000000001': conftest.JWT_USER_1}


@pytest.mark.parametrize(
    'partner_id, withdrawal_type, amount, expected_result, place_ids',
    [
        pytest.param(
            '00000000-0000-0000-0000-000000000001',
            'best2pay',
            105,
            {'price_value': '18', 'currency': ROUBLES_CURRENCY_RULES},
            [],
            id='min price',
        ),
        pytest.param(
            '00000000-0000-0000-0000-000000000001',
            'best2pay',
            5051,
            {'price_value': '50.51', 'currency': ROUBLES_CURRENCY_RULES},
            [],
            id='2 digits precision organic',
        ),
        pytest.param(
            '00000000-0000-0000-0000-000000000001',
            'best2pay',
            5050,
            {'price_value': '50.50', 'currency': ROUBLES_CURRENCY_RULES},
            [],
            id='2 digits precision quantize',
        ),
        pytest.param(
            '00000000-0000-0000-0000-000000000001',
            'best2pay',
            5000,
            {'price_value': '50', 'currency': ROUBLES_CURRENCY_RULES},
            [],
            id='normalize without comma',
        ),
        pytest.param(
            '00000000-0000-0000-0000-000000000001',
            'best2pay',
            500000,
            {'price_value': '1000', 'currency': ROUBLES_CURRENCY_RULES},
            [],
            id='max price',
        ),
        pytest.param(
            '00000000-0000-0000-0000-000000000001',
            'best2pay',
            99999,
            {'price_value': '999.99', 'currency': ROUBLES_CURRENCY_RULES},
            [],
            id='almost max price',
        ),
        pytest.param(
            '00000000-0000-0000-0000-000000000001',
            'best2pay',
            99900,
            {'price_value': '999', 'currency': ROUBLES_CURRENCY_RULES},
            [],
            id='almost max price with no comma',
        ),
        pytest.param(
            '00000000-0000-0000-0000-000000000001',
            'best2pay',
            99900,
            {'price_value': '0', 'currency': ROUBLES_CURRENCY_RULES},
            ['1'],
            id='almost max price with no comma elite brands',
        ),
        pytest.param(
            '00000000-0000-0000-0000-000000000001',
            'SBPb2p',
            500000,
            {
                'price_value': '0',
                'currency': ROUBLES_CURRENCY_RULES,
                'minimal_amount': str(constants.SBP_MIN_PAY),
            },
            [],
            id='no fee big amount',
        ),
        pytest.param(
            '00000000-0000-0000-0000-000000000001',
            'SBPb2p',
            5,
            {
                'price_value': '0',
                'currency': ROUBLES_CURRENCY_RULES,
                'minimal_amount': str(constants.SBP_MIN_PAY),
            },
            [],
            id='no fee small amount',
        ),
    ],
)
@pytest.mark.client_experiments3(
    consumer='eats-tips-withdrawal/withdrawal-fee-settings',
    experiment_name='eda_tips_withdrawals_fee_settings',
    args=[
        {'name': 'brands', 'type': 'set_string', 'value': []},
        {'name': 'withdrawal_type', 'type': 'string', 'value': 'best2pay'},
        {'name': 'amount', 'type': 'double', 'value': 105.0},
    ],
    value={'min': 18, 'max': 1000, 'percent': 1},
)
@pytest.mark.client_experiments3(
    consumer='eats-tips-withdrawal/withdrawal-fee-settings',
    experiment_name='eda_tips_withdrawals_fee_settings',
    args=[
        {'name': 'brands', 'type': 'set_string', 'value': []},
        {'name': 'withdrawal_type', 'type': 'string', 'value': 'best2pay'},
        {'name': 'amount', 'type': 'double', 'value': 5051.0},
    ],
    value={'min': 18, 'max': 1000, 'percent': 1},
)
@pytest.mark.client_experiments3(
    consumer='eats-tips-withdrawal/withdrawal-fee-settings',
    experiment_name='eda_tips_withdrawals_fee_settings',
    args=[
        {'name': 'brands', 'type': 'set_string', 'value': []},
        {'name': 'withdrawal_type', 'type': 'string', 'value': 'best2pay'},
        {'name': 'amount', 'type': 'double', 'value': 5050.0},
    ],
    value={'min': 18, 'max': 1000, 'percent': 1},
)
@pytest.mark.client_experiments3(
    consumer='eats-tips-withdrawal/withdrawal-fee-settings',
    experiment_name='eda_tips_withdrawals_fee_settings',
    args=[
        {'name': 'brands', 'type': 'set_string', 'value': []},
        {'name': 'withdrawal_type', 'type': 'string', 'value': 'best2pay'},
        {'name': 'amount', 'type': 'double', 'value': 5000.0},
    ],
    value={'min': 18, 'max': 1000, 'percent': 1},
)
@pytest.mark.client_experiments3(
    consumer='eats-tips-withdrawal/withdrawal-fee-settings',
    experiment_name='eda_tips_withdrawals_fee_settings',
    args=[
        {'name': 'brands', 'type': 'set_string', 'value': []},
        {'name': 'withdrawal_type', 'type': 'string', 'value': 'best2pay'},
        {'name': 'amount', 'type': 'double', 'value': 500000.0},
    ],
    value={'min': 18, 'max': 1000, 'percent': 1},
)
@pytest.mark.client_experiments3(
    consumer='eats-tips-withdrawal/withdrawal-fee-settings',
    experiment_name='eda_tips_withdrawals_fee_settings',
    args=[
        {'name': 'brands', 'type': 'set_string', 'value': []},
        {'name': 'withdrawal_type', 'type': 'string', 'value': 'best2pay'},
        {'name': 'amount', 'type': 'double', 'value': 99999.0},
    ],
    value={'min': 18, 'max': 1000, 'percent': 1},
)
@pytest.mark.client_experiments3(
    consumer='eats-tips-withdrawal/withdrawal-fee-settings',
    experiment_name='eda_tips_withdrawals_fee_settings',
    args=[
        {'name': 'brands', 'type': 'set_string', 'value': []},
        {'name': 'withdrawal_type', 'type': 'string', 'value': 'best2pay'},
        {'name': 'amount', 'type': 'double', 'value': 99900.0},
    ],
    value={'min': 18, 'max': 1000, 'percent': 1},
)
@pytest.mark.client_experiments3(
    consumer='eats-tips-withdrawal/withdrawal-fee-settings',
    experiment_name='eda_tips_withdrawals_fee_settings',
    args=[
        {'name': 'brands', 'type': 'set_string', 'value': ['elite']},
        {'name': 'withdrawal_type', 'type': 'string', 'value': 'best2pay'},
        {'name': 'amount', 'type': 'double', 'value': 99900.0},
    ],
    value={'min': 0, 'max': 0, 'percent': 0},
)
@pytest.mark.client_experiments3(
    consumer='eats-tips-withdrawal/withdrawal-fee-settings',
    experiment_name='eda_tips_withdrawals_fee_settings',
    args=[
        {'name': 'brands', 'type': 'set_string', 'value': []},
        {'name': 'withdrawal_type', 'type': 'string', 'value': 'best2pay'},
        {'name': 'amount', 'type': 'double', 'value': 1.0},
    ],
    value={'min': 0, 'max': 100, 'percent': 1},
)
@pytest.mark.client_experiments3(
    consumer='eats-tips-withdrawal/withdrawal-fee-settings',
    experiment_name='eda_tips_withdrawals_fee_settings',
    args=[
        {'name': 'brands', 'type': 'set_string', 'value': []},
        {'name': 'withdrawal_type', 'type': 'string', 'value': 'SBPb2p'},
        {'name': 'amount', 'type': 'double', 'value': 5.0},
    ],
    value={'min': 0, 'max': 0, 'percent': 0},
)
async def test_withdrawal_commission_settings(
        taxi_eats_tips_withdrawal_web,
        mock_eats_tips_partners,
        partner_id,
        withdrawal_type,
        amount,
        expected_result,
        place_ids,
):
    @mock_eats_tips_partners('/v2/partner')
    async def _mock_v2_partner(request):
        return web.json_response(
            conftest.format_partner_response(partner_id, place_ids),
            status=200,
        )

    @mock_eats_tips_partners('/v1/partner/alias-to-id')
    async def _mock_alias_to_id(request):
        return web.json_response(
            {'id': partner_id, 'alias': request.query['alias']},
        )

    query_params = {'amount': amount}
    if withdrawal_type:
        query_params['withdrawal_type'] = withdrawal_type
    response = await taxi_eats_tips_withdrawal_web.get(
        '/v1/withdrawal/commission-settings',
        params=query_params,
        headers={'X-Chaevie-Token': JWTS[partner_id]},
    )
    content = await response.json()
    assert content == expected_result
