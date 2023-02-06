import pytest

ORDER_NR = '123456-123456'
CLAIM_ID = 'some_claim_id'
CLAIM_ALIAS = 'some_claim_alias'

CARGO_CLAIMS_FULL_URL = '/cargo-claims/v2/claims/full'
TRACKING_URL = (
    '/eats-orders-tracking/internal/eats-orders-tracking'
    '/v1/get-claim-by-order-nr'
)
VGW_FORWARDINS_URL = '/vgw-api/v1/forwardings'

CLAIMS_FULL_RESPONSE = {
    'created_ts': '2020-09-23T00:01:03.154152+03:00',
    'id': 'b1fe01ddc30247279f806e6c5e210a9f',
    'items': [],
    'route_points': [],
    'status': 'performer_found',
    'updated_ts': '2020-09-23T14:49:01.174824+00:00',
    'user_request_revision': '123',
    'version': 1,
    'taxi_order_id': '659e62adad2a4927bbafc8679da2bdb5',
}

CLAIMS_FULL_ERROR_404 = {'code': 'not_found', 'message': 'Claim not found'}

VGW_FORWARDINS_RESPONSE = [
    {
        'callee': 'driver',
        'callee_phone_id': 'driver_phone_pd_id',
        'created_at': '2019-03-22T13:10:00+0300',
        'external_ref_id': ORDER_NR,
        'forwarding_id': 'forwarding_id_2',
        'gateway_id': 'mtt',
        'requester': 'passenger',
        'requester_phone_id': 'passenger_phone_pd_id',
        'state': 'created',
        'talks': [
            {
                'id': 'B674108217FEC529CC37E6234D526B36',
                'length': 35,
                'started_at': '2019-03-22T13:00:28+0300',
            },
            {
                'id': 'B674108217FEC529CC37E6234D526B37',
                'length': 30,
                'started_at': '2019-03-22T13:00:28+0300',
            },
        ],
    },
]

VGW_FORWARDINS_ERROR_400 = {
    'code': 'RegionIsNotSupported',
    'message': 'Region is not supported',
    'error': {
        'code': 'RegionIsNotSupported',
        'message': 'Region is not supported',
    },
}

VGW_FORWARDINS_ERROR_500 = {
    'code': 500,
    'message': 'Internal server error',
    'error': {'code': 'ArchiveError', 'message': 'Archive error'},
}

TRACKING_RESPONSE = {
    'order_nr': ORDER_NR,
    'claim_id': CLAIM_ID,
    'claim_alias': CLAIM_ALIAS,
}

TRACKING_ERROR_400 = {
    'code': 'NOT_FOUND_COURIER_DATA',
    'message': 'Courier data is not found',
}

EXPECTED_RESPONSE = {
    'talks': [
        {
            'gateway_id': 'mtt',
            'talk_id': 'B674108217FEC529CC37E6234D526B36',
            'talk_type': 'picker',
        },
        {
            'gateway_id': 'mtt',
            'talk_id': 'B674108217FEC529CC37E6234D526B37',
            'talk_type': 'picker',
        },
        {
            'gateway_id': 'mtt',
            'talk_id': 'B674108217FEC529CC37E6234D526B36',
            'talk_type': 'courier',
        },
        {
            'gateway_id': 'mtt',
            'talk_id': 'B674108217FEC529CC37E6234D526B37',
            'talk_type': 'courier',
        },
    ],
}

EXPECTED_EMPTY_RESPONSE: dict = {'talks': []}

EXPECTED_CLIENTS_ERROR_RESPONSE = {
    'talks': [
        {
            'gateway_id': 'mtt',
            'talk_id': 'B674108217FEC529CC37E6234D526B36',
            'talk_type': 'picker',
        },
        {
            'gateway_id': 'mtt',
            'talk_id': 'B674108217FEC529CC37E6234D526B37',
            'talk_type': 'picker',
        },
    ],
}


@pytest.mark.now('2020-04-28T12:10:00+03:00')
async def test_green_flow(
        # ---- fixtures ----
        mockserver,
        taxi_eats_support_misc_web,
        # ---- parameters ----
):
    @mockserver.json_handler(CARGO_CLAIMS_FULL_URL)
    def _mock_claims_full(request):
        return mockserver.make_response(status=200, json=CLAIMS_FULL_RESPONSE)

    @mockserver.json_handler(TRACKING_URL)
    def _mock_orders_tracking(request):
        return mockserver.make_response(status=200, json=TRACKING_RESPONSE)

    @mockserver.json_handler(VGW_FORWARDINS_URL)
    def _mock_vgw_forwardings(request):
        return mockserver.make_response(
            status=200, json=VGW_FORWARDINS_RESPONSE,
        )

    response = await taxi_eats_support_misc_web.get(
        '/v1/get-talks', params={'order_nr': ORDER_NR},
    )

    assert response.status == 200
    data = await response.json()
    assert data == EXPECTED_RESPONSE


@pytest.mark.now('2020-04-28T12:10:00+03:00')
@pytest.mark.parametrize(
    """fwd_code,fwd_response""",
    [(400, VGW_FORWARDINS_ERROR_400), (500, VGW_FORWARDINS_ERROR_500)],
)
async def test_forwardings_error(
        # ---- fixtures ----
        mockserver,
        taxi_eats_support_misc_web,
        # ---- parameters ----
        fwd_code,
        fwd_response,
):
    @mockserver.json_handler(CARGO_CLAIMS_FULL_URL)
    def _mock_claims_full(request):
        return mockserver.make_response(status=200, json=CLAIMS_FULL_RESPONSE)

    @mockserver.json_handler(TRACKING_URL)
    def _mock_orders_tracking(request):
        return mockserver.make_response(status=200, json=TRACKING_RESPONSE)

    @mockserver.json_handler(VGW_FORWARDINS_URL)
    def _mock_vgw_forwardings(request):
        return mockserver.make_response(status=fwd_code, json=fwd_response)

    response = await taxi_eats_support_misc_web.get(
        '/v1/get-talks', params={'order_nr': ORDER_NR},
    )

    assert response.status == 200
    data = await response.json()
    assert data == EXPECTED_EMPTY_RESPONSE


@pytest.mark.now('2020-04-28T12:10:00+03:00')
@pytest.mark.parametrize(
    """tracking_code,tracking_response""",
    [(400, TRACKING_ERROR_400), (500, None)],
)
async def test_tracking_error(
        # ---- fixtures ----
        mockserver,
        taxi_eats_support_misc_web,
        # ---- parameters ----
        tracking_code,
        tracking_response,
):
    @mockserver.json_handler(CARGO_CLAIMS_FULL_URL)
    def _mock_claims_full(request):
        return mockserver.make_response(status=200, json=CLAIMS_FULL_RESPONSE)

    @mockserver.json_handler(TRACKING_URL)
    def _mock_orders_tracking(request):
        return mockserver.make_response(
            status=tracking_code, json=tracking_response,
        )

    @mockserver.json_handler(VGW_FORWARDINS_URL)
    def _mock_vgw_forwardings(request):
        return mockserver.make_response(
            status=200, json=VGW_FORWARDINS_RESPONSE,
        )

    response = await taxi_eats_support_misc_web.get(
        '/v1/get-talks', params={'order_nr': ORDER_NR},
    )

    assert response.status == 200
    data = await response.json()
    assert data == EXPECTED_CLIENTS_ERROR_RESPONSE
    assert _mock_claims_full.times_called == 0
    assert _mock_vgw_forwardings.times_called == 1


@pytest.mark.now('2020-04-28T12:10:00+03:00')
@pytest.mark.parametrize(
    """claims_code,claims_response""",
    [(404, CLAIMS_FULL_ERROR_404), (500, None)],
)
async def test_claims_error(
        # ---- fixtures ----
        mockserver,
        taxi_eats_support_misc_web,
        # ---- parameters ----
        claims_code,
        claims_response,
):
    @mockserver.json_handler(CARGO_CLAIMS_FULL_URL)
    def _mock_claims_full(request):
        return mockserver.make_response(
            status=claims_code, json=claims_response,
        )

    @mockserver.json_handler(TRACKING_URL)
    def _mock_orders_tracking(request):
        return mockserver.make_response(status=200, json=TRACKING_RESPONSE)

    @mockserver.json_handler(VGW_FORWARDINS_URL)
    def _mock_vgw_forwardings(request):
        return mockserver.make_response(
            status=200, json=VGW_FORWARDINS_RESPONSE,
        )

    response = await taxi_eats_support_misc_web.get(
        '/v1/get-talks', params={'order_nr': ORDER_NR},
    )

    assert response.status == 200
    data = await response.json()
    assert data == EXPECTED_CLIENTS_ERROR_RESPONSE
    assert _mock_vgw_forwardings.times_called == 1
