import pytest

CLAIM_ID_0 = 'aafd000000000000dccb122411119999'
CLAIM_ID_1 = 'aaaf000000000000dddb111122223333'
CLAIM_ID_2 = 'bbbb000000000000ffff111122223333'

CLAIM_COEFF = {CLAIM_ID_0: 1.4, CLAIM_ID_1: 1.8}


@pytest.mark.pgsql(
    'eats_logistics_performer_payouts', files=['insert_coeffs.sql'],
)
@pytest.mark.parametrize(
    'claims,coeff',
    [
        pytest.param([CLAIM_ID_0], 1.4, id='single claim'),
        pytest.param([CLAIM_ID_0, CLAIM_ID_1], 1.6, id='avg by two'),
        pytest.param([CLAIM_ID_2], None, id='claim not found'),
    ],
)
async def test_blackbox_info(
        claims, coeff, taxi_eats_logistics_performer_payouts,
):
    request_json = {'claim_ids': claims}
    if coeff:
        response_json = {
            'courier_demand_multiplier': coeff,
            'claims_courier_demand_multiplier': [
                {
                    'claim_id': claim_id,
                    'courier_demand_multiplier': CLAIM_COEFF[claim_id],
                }
                for claim_id in claims
                if claim_id in CLAIM_COEFF
            ],
        }
    else:
        response_json = {}

    response = await taxi_eats_logistics_performer_payouts.post(
        'v1/blackbox/info', json=request_json,
    )
    assert response.status_code == 200
    assert response.json() == response_json
