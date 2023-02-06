import datetime

import pytest

TASK_NAME = 'courier-phone-masking'
TZ_UTC = datetime.timezone.utc
TZ_MSK = datetime.timezone(datetime.timedelta(hours=3))


def sql_get_courier_phone_numbers(pgsql):
    cursor = pgsql['eats_orders_tracking'].cursor()
    cursor.execute(
        """
        SELECT order_nr, phone_number, extension, ttl AT TIME ZONE 'UTC',
         error_count
        FROM eats_orders_tracking.masked_courier_phone_numbers
        ORDER BY order_nr
        """,
    )
    return list(cursor)


@pytest.fixture(name='mock_claims_points_eta')
def _mock_claims_points_eta(mockserver):
    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/claims/points-eta',
    )
    def _handler(request):
        mock_response = {
            'id': 'test_id',
            'route_points': [
                {
                    'id': 1,
                    'address': {
                        'fullname': '1',
                        'coordinates': [35.8, 55.4],
                        'country': '1',
                        'city': '1',
                        'street': '1',
                        'building': '1',
                    },
                    'type': 'source',
                    'visit_order': 1,
                    'visit_status': 'pending',
                    'visited_at': {},
                },
                {
                    'id': 2,
                    'address': {
                        'fullname': '2',
                        'coordinates': [37.8, 55.4],
                        'country': '2',
                        'city': '2',
                        'street': '2',
                        'building': '2',
                    },
                    'type': 'destination',
                    'visit_order': 2,
                    'visit_status': 'pending',
                    'visited_at': {'expected': '2020-10-28T18:28:00.00+00:00'},
                },
            ],
            'performer_position': [37.8, 55.4],
        }
        return mockserver.make_response(json=mock_response, status=200)


async def test_dummy(taxi_eats_orders_tracking):
    # Workaround for TAXIDATA-3002: This test just loads service.
    pass


@pytest.mark.now('2021-01-09T20:30:00+00:00')
@pytest.mark.config(
    EATS_ORDERS_TRACKING_SELECT_WAYBILL_ENABLED={
        'is_allowed_select_waybill_info': True,
    },
)
@pytest.mark.pgsql(
    'eats_orders_tracking', files=['fill_masked_phone_numbers.sql'],
)
async def test_masking(
        taxi_eats_orders_tracking,
        mockserver,
        mocked_time,
        pgsql,
        mock_claims_points_eta,
):
    cargo_claims_claim_ids = set()

    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/driver-voiceforwarding',
    )
    def _handler_cargo_claims_driver_voiceforwarding(request):
        claim_id = request.json['claim_id']
        cargo_claims_claim_ids.add(claim_id)
        digit = claim_id[-1]
        mock_response = {
            'phone': digit + '0321',
            'ext': digit + '03',
            'ttl_seconds': 543,
        }
        return mockserver.make_response(json=mock_response, status=200)

    await taxi_eats_orders_tracking.run_distlock_task(TASK_NAME)

    # We don't know exact order of 'cargo-claims' calls so use 'set':
    expected_claim_ids = {'id2', 'id3', 'id4', 'id8'}
    assert cargo_claims_claim_ids == expected_claim_ids
    assert _handler_cargo_claims_driver_voiceforwarding.times_called == len(
        expected_claim_ids,
    )

    data = sql_get_courier_phone_numbers(pgsql)
    expected_ttl = datetime.datetime(2021, 1, 9, 20, 39, 3)
    assert data == [
        (
            '111111-111111',
            '10012',
            '101',
            datetime.datetime(2120, 10, 28, 0, 0),
            0,
        ),
        ('111111-222222', '20321', '203', expected_ttl, 0),
        ('111111-333333', '30321', '303', expected_ttl, 0),
        ('111111-444444', '40321', '403', expected_ttl, 0),
        (
            '111111-555555',
            '50012',
            '501',
            datetime.datetime(2021, 1, 9, 0, 0),
            10,
        ),
        ('111111-666666', None, None, None, 0),
        ('111111-888888', '80321', '803', expected_ttl, 0),
    ]


@pytest.mark.now('2021-01-09T20:30:00+00:00')
@pytest.mark.config(
    EATS_ORDERS_TRACKING_SELECT_WAYBILL_ENABLED={
        'is_allowed_select_waybill_info': True,
    },
)
@pytest.mark.pgsql(
    'eats_orders_tracking',
    files=['fill_masked_phone_numbers.sql', 'fill_masked_phone_for_409.sql'],
)
async def test_masking_errors(
        taxi_eats_orders_tracking,
        mockserver,
        mocked_time,
        pgsql,
        mock_claims_points_eta,
):
    cargo_claims_claim_ids = set()

    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/driver-voiceforwarding',
    )
    def _handler_cargo_claims_driver_voiceforwarding(request):
        claim_id = request.json['claim_id']
        cargo_claims_claim_ids.add(claim_id)
        digit = claim_id[-1]
        if claim_id in ['id3', 'id4']:
            mock_response = {'code': 'not_found', 'message': 'bad'}
            return mockserver.make_response(json=mock_response, status=404)
        if claim_id in ['id7']:
            mock_response = {
                'code': 'claim_is_outdated',
                'message': 'Claim is in final state',
            }
            return mockserver.make_response(json=mock_response, status=409)
        mock_response = {
            'phone': digit + '0321',
            'ext': digit + '03',
            'ttl_seconds': 543,
        }
        return mockserver.make_response(json=mock_response, status=200)

    await taxi_eats_orders_tracking.run_distlock_task(TASK_NAME)

    # We don't know exact order of 'cargo-claims' calls so use 'set':
    expected_claim_ids = {'id2', 'id3', 'id4', 'id7', 'id8'}
    assert cargo_claims_claim_ids == expected_claim_ids
    assert _handler_cargo_claims_driver_voiceforwarding.times_called == len(
        expected_claim_ids,
    )

    data = sql_get_courier_phone_numbers(pgsql)
    assert data == [
        (
            '111111-111111',
            '10012',
            '101',
            datetime.datetime(2120, 10, 28, 0, 0),
            0,
        ),
        (
            '111111-222222',
            '20321',
            '203',
            datetime.datetime(2021, 1, 9, 20, 39, 3),
            0,
        ),
        ('111111-333333', None, None, None, 4),
        (
            '111111-444444',
            '40012',
            '401',
            datetime.datetime(2021, 1, 9, 0, 0),
            10,
        ),
        (
            '111111-555555',
            '50012',
            '501',
            datetime.datetime(2021, 1, 9, 0, 0),
            10,
        ),
        ('111111-666666', None, None, None, 0),
        (
            '111111-888888',
            '80321',
            '803',
            datetime.datetime(2021, 1, 9, 20, 39, 3),
            0,
        ),
    ]


@pytest.mark.config(
    EATS_ORDERS_TRACKING_COURIER_CARGO_CLAIMS_MASKING={
        'is_cargo_claims_voiceforwarding_enabled': False,
    },
)
@pytest.mark.pgsql(
    'eats_orders_tracking', files=['fill_masked_phone_numbers.sql'],
)
async def test_masking_disabled(taxi_eats_orders_tracking, pgsql):
    data_before = sql_get_courier_phone_numbers(pgsql)

    # Ensure there are no calls to cargo-claims:
    await taxi_eats_orders_tracking.run_distlock_task(TASK_NAME)

    data = sql_get_courier_phone_numbers(pgsql)
    assert data == data_before


@pytest.mark.now('2021-01-09T20:30:00+00:00')
@pytest.mark.pgsql(
    'eats_orders_tracking', files=['fill_masked_phone_numbers.sql'],
)
async def test_valid_claim_point_id(
        taxi_eats_orders_tracking, mockserver, mock_claims_points_eta,
):
    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/driver-voiceforwarding',
    )
    def _handler_cargo_claims_driver_voiceforwarding(request):
        # 2 is id of destination point in mock_claims_points_eta
        assert request.json['point_id'] == 2
        mock_response = {'phone': '10321', 'ext': '103', 'ttl_seconds': 543}
        return mockserver.make_response(json=mock_response, status=200)

    await taxi_eats_orders_tracking.run_distlock_task(TASK_NAME)

    assert _handler_cargo_claims_driver_voiceforwarding.times_called > 0


@pytest.mark.now('2021-01-09T20:30:00+00:00')
@pytest.mark.pgsql(
    'eats_orders_tracking', files=['fill_masked_phone_numbers.sql'],
)
async def test_points_eta_failed(taxi_eats_orders_tracking, mockserver):
    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/claims/points-eta',
    )
    def _handler_cargo_claims_points_eta(request):
        mock_response = {
            'code': 'point_not_found',
            'message': 'point not found',
        }
        return mockserver.make_response(json=mock_response, status=404)

    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/driver-voiceforwarding',
    )
    def _handler_cargo_claims_driver_voiceforwarding(request):
        assert 'point_id' not in request.json
        mock_response = {'phone': '10321', 'ext': '103', 'ttl_seconds': 543}
        return mockserver.make_response(json=mock_response, status=200)

    await taxi_eats_orders_tracking.run_distlock_task(TASK_NAME)

    assert _handler_cargo_claims_driver_voiceforwarding.times_called > 0


@pytest.mark.pgsql(
    'eats_orders_tracking', files=['fill_masked_phone_numbers.sql'],
)
@pytest.mark.config(
    EATS_ORDERS_TRACKING_COURIER_CARGO_CLAIMS_MASKING={
        'is_cargo_claims_voiceforwarding_enabled': True,
        'minimal_ttl_seconds': 10,
    },
    EATS_ORDERS_TRACKING_SELECT_WAYBILL_ENABLED={
        'is_allowed_select_waybill_info': True,
    },
)
@pytest.mark.parametrize(
    'param_now,param_expected_masking',
    [
        # ttl in database in id2, id4 = '2021-01-09+00:00'
        pytest.param('2000-01-09+00:00+00:00', False, id='far_far_before_ttl'),
        pytest.param('2021-01-08T23:59:49+00:00', False, id='far_before_ttl'),
        pytest.param('2021-01-08T23:59:51+00:00', True, id='near_before_ttl'),
        pytest.param('2021-01-09T00:00:01+00:00', True, id='after_ttl'),
        pytest.param('2030-01-09+00:00', True, id='far_after_ttl'),
    ],
)
async def test_masking_select_for_update(
        taxi_eats_orders_tracking,
        mockserver,
        mocked_time,
        pgsql,
        mock_claims_points_eta,
        param_now,
        param_expected_masking,
):
    mocked_time.set(datetime.datetime.fromisoformat(param_now))
    await taxi_eats_orders_tracking.invalidate_caches()

    cargo_claims_claim_ids = set()

    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/driver-voiceforwarding',
    )
    def _handler_cargo_claims_driver_voiceforwarding(request):
        claim_id = request.json['claim_id']
        cargo_claims_claim_ids.add(claim_id)
        digit = claim_id[-1]
        mock_response = {
            'phone': digit + '0321',
            'ext': digit + '03',
            'ttl_seconds': 600,
        }
        return mockserver.make_response(json=mock_response, status=200)

    await taxi_eats_orders_tracking.run_distlock_task(TASK_NAME)

    # We don't know exact order of 'cargo-claims' calls so use 'set':
    expected_claim_ids = {'id3'}
    if param_expected_masking:
        expected_claim_ids.add('id2')
        expected_claim_ids.add('id4')
        expected_claim_ids.add('id8')

    assert cargo_claims_claim_ids == expected_claim_ids
    assert _handler_cargo_claims_driver_voiceforwarding.times_called == len(
        expected_claim_ids,
    )
