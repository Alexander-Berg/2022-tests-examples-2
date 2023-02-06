import pytest


PG_SCHEMA = 'eats_logistics_performer_payouts'
PG_FILES = [
    'eats_logistics_performer_payouts/insert_all_factors.sql',
    'insert_courier_contexts.sql',
    'insert_courier_demand_coeffs.sql',
    'insert_factor_values.sql',
    'insert_payout_coeffs.sql',
]

EXP_NAME = 'eats_payouts_cpo_predict_pipeline'
EXP_CONSUMER = 'eats-logistics-performer-payouts/cpo_predict_calculator'
EXP_MATCH = {'predicate': {'type': 'true'}, 'enabled': True}
EXP_DEFAULT_JSON = {'pipeline_name': 'predict_cpo_basic'}
EXP_NOPIPELINE_JSON = {'pipeline_name': 'none'}

KEY = '1'

COURIER_ID = 'cc09111122223333000000000000_112305af111122220000000000000000'
ORDER_NR = '000100-123456'
CLAIM_ID = 'aafd000000000000dccb122411119999'
COEFF = 1.4
TO_REST_DISTANCE_M = 450
TO_CLIENT_DISTANCE_M = 600

COURIER_ID_EXTRA = (
    'dd07111122223333000000000000_89f5ccd8111122220000000000000000'
)
TO_REST_DISTANCE_EXTRA_M = 300
ORDER_NR_EXTRA = '000200-778450'
CLAIM_ID_EXTRA = 'aafd000000000000dccb122411118888'
COEFF_EXTRA = 2.2
BATCH_RADIUS_DISTANCE_M = 60
BATCH_TO_SECOND_CLIENT_DIST_M = 300

COURIER_ID_NOTINCACHE = (
    'ffa8111122223333000000000000_00ccca05111122220000000000000000'
)

ORDER_NR_NOTINDB = '000300-773109'
CLAIM_ID_NOTINDB = 'aafd000000000000dccb122411117777'

COURIER_ID_NOCTX = (
    'cce7111122223333000000000000_00ef8c54111122220000000000000000'
)

EXP_CPO_VALUE = 89.4
EXP_CPO_VALUE_EXTRA_CANDIDATE = 85.2
EXP_CPO_VALUE_LIVE_BATCH = 165.24


@pytest.mark.experiments3(
    name=EXP_NAME,
    consumers=[EXP_CONSUMER],
    is_config=True,
    match=EXP_MATCH,
    default_value=EXP_DEFAULT_JSON,
    clauses=[],
)
@pytest.mark.pgsql(PG_SCHEMA, files=PG_FILES)
@pytest.mark.now('2021-05-11T01:00:30+00:00')
async def test_cpo_estimate(taxi_eats_logistics_performer_payouts):
    request_json = {
        'courier_id': COURIER_ID,
        'claim_uuid': CLAIM_ID,
        'order_nr': ORDER_NR,
        'to_rest_distance_m': TO_REST_DISTANCE_M,
        'to_client_distance_m': TO_CLIENT_DISTANCE_M,
    }
    response = await taxi_eats_logistics_performer_payouts.post(
        'v1/cpo/estimate', json=request_json,
    )
    assert response.status_code == 200
    assert response.json()['cpo_value'] == EXP_CPO_VALUE


@pytest.mark.experiments3(
    name=EXP_NAME,
    consumers=[EXP_CONSUMER],
    is_config=True,
    match=EXP_MATCH,
    default_value=EXP_DEFAULT_JSON,
    clauses=[],
)
@pytest.mark.pgsql(PG_SCHEMA, files=PG_FILES)
@pytest.mark.now('2021-05-11T01:00:30+00:00')
@pytest.mark.parametrize(
    'orders,candidates,cpo_map',
    [
        pytest.param(
            [
                {
                    'order_nr': ORDER_NR,
                    'claim_uuid': CLAIM_ID,
                    'to_client_distance_m': TO_CLIENT_DISTANCE_M,
                },
            ],
            [
                {
                    'courier_id': COURIER_ID,
                    'to_rest_distance_m': TO_REST_DISTANCE_M,
                },
            ],
            {COURIER_ID: EXP_CPO_VALUE},
            id='compatibility',
        ),
        pytest.param(
            [
                {
                    'order_nr': ORDER_NR,
                    'claim_uuid': CLAIM_ID,
                    'is_first_in_batch': True,
                    'to_client_distance_m': TO_CLIENT_DISTANCE_M,
                },
                {
                    'order_nr': ORDER_NR_EXTRA,
                    'claim_uuid': CLAIM_ID_EXTRA,
                    'to_rest_distance_m': BATCH_RADIUS_DISTANCE_M,
                    'to_client_distance_m': BATCH_TO_SECOND_CLIENT_DIST_M,
                },
            ],
            [
                {
                    'courier_id': COURIER_ID,
                    'to_rest_distance_m': TO_REST_DISTANCE_M,
                },
            ],
            {COURIER_ID: EXP_CPO_VALUE_LIVE_BATCH},
            id='live_batch',
        ),
        pytest.param(
            [
                {
                    'order_nr': ORDER_NR,
                    'claim_uuid': CLAIM_ID,
                    'to_client_distance_m': TO_CLIENT_DISTANCE_M,
                },
            ],
            [
                {
                    'courier_id': COURIER_ID,
                    'to_rest_distance_m': TO_REST_DISTANCE_M,
                },
                {
                    'courier_id': COURIER_ID_EXTRA,
                    'to_rest_distance_m': TO_REST_DISTANCE_EXTRA_M,
                },
            ],
            {
                COURIER_ID: EXP_CPO_VALUE,
                COURIER_ID_EXTRA: EXP_CPO_VALUE_EXTRA_CANDIDATE,
            },
            id='multiple_candidates',
        ),
        pytest.param(
            [
                {
                    'order_nr': ORDER_NR,
                    'claim_uuid': CLAIM_ID,
                    'to_client_distance_m': TO_CLIENT_DISTANCE_M,
                },
            ],
            [
                {
                    'courier_id': COURIER_ID_NOTINCACHE,
                    'to_rest_distance_m': TO_REST_DISTANCE_M,
                },
            ],
            {COURIER_ID_NOTINCACHE: EXP_CPO_VALUE},
            id='courier_context_not_cached',
        ),
        pytest.param(
            [
                {
                    'order_nr': ORDER_NR,
                    'claim_uuid': CLAIM_ID,
                    'is_first_in_batch': True,
                    'to_client_distance_m': TO_CLIENT_DISTANCE_M,
                },
                {
                    'order_nr': ORDER_NR_EXTRA,
                    'claim_uuid': CLAIM_ID_EXTRA,
                    'to_rest_distance_m': BATCH_RADIUS_DISTANCE_M,
                    'to_client_distance_m': BATCH_TO_SECOND_CLIENT_DIST_M,
                },
            ],
            [
                {
                    'courier_id': COURIER_ID,
                    'to_rest_distance_m': TO_REST_DISTANCE_M,
                },
            ],
            {COURIER_ID: EXP_CPO_VALUE_LIVE_BATCH},
            marks=[
                pytest.mark.experiments3(
                    name=EXP_NAME,
                    consumers=[EXP_CONSUMER],
                    is_config=True,
                    match=EXP_MATCH,
                    default_value=EXP_NOPIPELINE_JSON,
                    clauses=[],
                ),
            ],
            id='cpp_cpo_override',
        ),
        pytest.param(
            [
                {
                    'order_nr': ORDER_NR_NOTINDB,
                    'claim_uuid': CLAIM_ID_NOTINDB,
                    'is_first_in_batch': True,
                    'to_client_distance_m': TO_CLIENT_DISTANCE_M,
                },
            ],
            [
                {
                    'courier_id': COURIER_ID,
                    'to_rest_distance_m': TO_REST_DISTANCE_M,
                },
            ],
            {},
            id='coeff_not_found',
        ),
        pytest.param(
            [
                {
                    'order_nr': ORDER_NR,
                    'claim_uuid': CLAIM_ID,
                    'is_first_in_batch': True,
                    'to_client_distance_m': TO_CLIENT_DISTANCE_M,
                },
            ],
            [
                {
                    'courier_id': COURIER_ID_NOCTX,
                    'to_rest_distance_m': TO_REST_DISTANCE_M,
                },
            ],
            {},
            id='context_not_found',
        ),
    ],
)
async def test_cpo_bulk_estimate(
        candidates, cpo_map, orders, taxi_eats_logistics_performer_payouts,
):
    request_json = {
        'args': [{'key': KEY, 'orders': orders, 'candidates': candidates}],
    }
    response = await taxi_eats_logistics_performer_payouts.post(
        'v1/cpo/bulk-estimate', json=request_json,
    )
    assert response.status_code == 200

    if cpo_map == {}:
        assert response.json()['info'] == []
    else:
        info = response.json()['info'][0]
        for courier in info['candidates']:
            courier_id = courier['courier_id']
            cpo_value = courier['cpo_value']
            assert cpo_value == cpo_map[courier_id]
