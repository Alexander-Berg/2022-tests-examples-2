import datetime
import time

import pytest

from testsuite.utils import matching


@pytest.fixture(name='mock_driver_route_watcher')
def _mock_driver_route_watcher(mockserver):
    @mockserver.json_handler(
        '/driver-route-responder/cargo/timeleft-by-courier',
    )
    def mock(request):
        assert (
            request.json['verification_data']['cargo_order_id']
            == '9db1622e-582d-4091-b6fc-4cb2ffdc12c0'
        )
        return context.response

    class Context:
        def __init__(self):
            self.response = {}
            self.handler = mock

    context = Context()

    return context


@pytest.mark.now('2021-01-01T00:00:00.000Z')
@pytest.mark.config(
    CARGO_CLAIMS_ETA_SOURCE_BY_CORP_CLIENT={
        '__default__': 'driver_route_watcher',
    },
    CARGO_CLAIMS_GET_ETA_FROM_LOGISTIC_DISPATCHER={
        '__default__': False,
        '/api/integration/v1/claims/points-eta/post': True,
        '/v2/claims/points-eta/post': True,
    },
)
@pytest.mark.parametrize(
    'target_status, next_point, drw_response, expected_points_visited_at',
    [
        pytest.param(
            'performer_found',
            1,
            {
                'courier': 'park_id_1_driver_uuid_1',
                'position': [55, 37],
                'etas': [
                    {
                        'point': [55.1, 37.2],
                        'time_left': 1800.0,
                        'distance_left': 1000.0,
                        'point_id': '1',
                    },
                    {
                        'point': [55.2, 37.3],
                        'time_left': 3600.0,
                        'distance_left': 2000.0,
                        'point_id': '2',
                    },
                    {
                        'point': [55.3, 37.4],
                        'time_left': 5400.0,
                        'distance_left': 3000.0,
                        'point_id': '3',
                    },
                ],
            },
            [
                {
                    'expected': '2021-01-01T00:30:00+00:00',
                    'expected_waiting_time_sec': 180,
                },
                {
                    'expected': '2021-01-01T01:00:00+00:00',
                    'expected_waiting_time_sec': 180,
                },
                {
                    'expected': '2021-01-01T01:30:00+00:00',
                    'expected_waiting_time_sec': 180,
                },
            ],
            id='happy_path',
        ),
        pytest.param(
            'pickuped',
            2,
            {
                'courier': 'park_id_1_driver_uuid_1',
                'position': [55, 37],
                'etas': [
                    {
                        'point': [55.2, 37.3],
                        'time_left': 3600.0,
                        'distance_left': 2000.0,
                        'point_id': '2',
                    },
                    {
                        'point': [55.3, 37.4],
                        'time_left': 5400.0,
                        'distance_left': 3000.0,
                        'point_id': '3',
                    },
                ],
            },
            [
                {
                    'actual': matching.any_string,
                    'expected_waiting_time_sec': 180,
                },
                {
                    'expected': '2021-01-01T01:00:00+00:00',
                    'expected_waiting_time_sec': 180,
                },
                {
                    'expected': '2021-01-01T01:30:00+00:00',
                    'expected_waiting_time_sec': 180,
                },
            ],
            id='some_points_missing',
        ),
    ],
)
async def test_get_eta_from_drw(
        mockserver,
        taxi_cargo_claims,
        taxi_config,
        exp_cargo_waiting_times_by_point,
        create_segment_with_performer,
        get_db_segment_ids,
        get_default_headers,
        state_controller,
        mock_driver_route_watcher,
        target_status,
        next_point,
        drw_response,
        expected_points_visited_at,
):
    await exp_cargo_waiting_times_by_point(enabled=True)
    claim_info = await create_segment_with_performer()
    claim_id = claim_info.claim_id

    if drw_response is not None:
        segment_ids = await get_db_segment_ids()
        segment_id = segment_ids[0]

        segment = await taxi_cargo_claims.post(
            f'/v1/segments/info?segment_id={segment_id}',
            json={},
            headers=get_default_headers(),
        )

        for point in segment.json()['points']:
            for plan_point in drw_response['etas']:
                if plan_point['point_id'] == str(point['claim_point_id']):
                    plan_point['point_id'] = point['point_id']

    mock_driver_route_watcher.response = drw_response

    await state_controller.apply(
        fresh_claim=False,
        target_status=target_status,
        next_point_order=next_point,
    )

    int_response = await taxi_cargo_claims.post(
        f'/api/integration/v1/claims/points-eta',
        params={'claim_id': claim_id},
        headers=get_default_headers(),
    )
    assert int_response.status_code == 200
    inn_response = await taxi_cargo_claims.post(
        f'/v2/claims/points-eta',
        params={'claim_id': claim_id},
        headers=get_default_headers(),
    )
    assert inn_response.status_code == 200
    assert int_response.json() == inn_response.json()
    json = int_response.json()

    assert 'performer_position' in json
    assert json['performer_position'] == drw_response['position']

    points_etas = [point['visited_at'] for point in json['route_points']]
    assert points_etas == expected_points_visited_at

    assert mock_driver_route_watcher.handler.times_called == 2


@pytest.mark.now('2021-01-01T00:00:00.000Z')
@pytest.mark.config(
    CARGO_CLAIMS_ETA_SOURCE_BY_CORP_CLIENT={
        '__default__': 'driver_route_watcher',
    },
    CARGO_CLAIMS_GET_ETA_FROM_LOGISTIC_DISPATCHER={
        '__default__': False,
        '/api/integration/v1/claims/points-eta/post': True,
        '/v2/claims/points-eta/post': True,
    },
    CARGO_CLAIMS_ENABLE_POINTS_ETA_PUMPKIN={
        'enabled': True,
        'mean_speed': {'__default__': 2},
    },
)
async def test_eta_pumpkin(
        taxi_cargo_claims,
        state_controller,
        exp_cargo_waiting_times_by_point,
        create_segment_with_performer,
        get_default_headers,
):
    await exp_cargo_waiting_times_by_point(enabled=True)
    claim_info = await create_segment_with_performer()
    claim_id = claim_info.claim_id

    await state_controller.apply(
        fresh_claim=False, target_status='pickuped', next_point_order=2,
    )

    response = await taxi_cargo_claims.post(
        f'/v2/claims/points-eta',
        params={'claim_id': claim_id},
        headers=get_default_headers(),
    )
    assert response.status_code == 200
    prepared_actual = response.json()['route_points'][0]['visited_at'][
        'actual'
    ].split('T')[1]
    prepared_expected = response.json()['route_points'][1]['visited_at'][
        'expected'
    ].split('T')[1]

    # between 55.7,37.5 and 55.6,37.6 - 12767 meters
    # speed 2 m/s from config
    # time between points = round(12767 / 2) = 6384 s
    # 6384 s > 1 hour 40 minutes (6000 seconds)

    actual = time.strptime(prepared_actual.split('.')[0], '%H:%M:%S')
    expected = time.strptime(prepared_expected.split('.')[0], '%H:%M:%S')
    actual_seconds = datetime.timedelta(
        hours=actual.tm_hour, minutes=actual.tm_min, seconds=actual.tm_sec,
    ).total_seconds()
    expected_seconds = datetime.timedelta(
        hours=expected.tm_hour,
        minutes=expected.tm_min,
        seconds=expected.tm_sec,
    ).total_seconds()
    assert actual_seconds + 6000 < expected_seconds


async def test_inactive_claim(
        mockserver,
        taxi_cargo_claims,
        taxi_config,
        create_segment_with_performer,
        get_db_segment_ids,
        get_default_headers,
        state_controller,
):
    claim_info = await state_controller.apply(target_status='failed')
    claim_id = claim_info.claim_id
    response = await taxi_cargo_claims.post(
        f'/api/integration/v1/claims/points-eta?claim_id={claim_id}',
        headers=get_default_headers(),
    )
    assert response.status_code == 409
    assert response.json() == {
        'code': 'inappropriate_status',
        'message': 'Заявка в неактивном статусе',
    }


async def test_no_performer(
        mockserver,
        taxi_cargo_claims,
        taxi_config,
        create_segment_with_performer,
        get_db_segment_ids,
        get_default_headers,
        state_controller,
):
    claim_info = await state_controller.apply(target_status='performer_draft')
    claim_id = claim_info.claim_id
    response = await taxi_cargo_claims.post(
        f'/api/integration/v1/claims/points-eta?claim_id={claim_id}',
        headers=get_default_headers(),
    )
    assert response.status_code == 409
    assert response.json() == {
        'code': 'no_performer_info',
        'message': 'Исполнитель еще не найден',
    }


@pytest.mark.config(
    CARGO_CLAIMS_ETA_SOURCE_BY_CORP_CLIENT={
        '__default__': 'driver_route_watcher',
    },
    CARGO_CLAIMS_GET_ETA_FROM_LOGISTIC_DISPATCHER={
        '__default__': False,
        '/api/integration/v1/claims/points-eta/post': True,
    },
)
async def test_no_eta(
        mockserver,
        taxi_cargo_claims,
        taxi_config,
        exp_cargo_waiting_times_by_point,
        create_segment_with_performer,
        get_db_segment_ids,
        get_default_headers,
        state_controller,
        mock_driver_route_watcher,
):
    await exp_cargo_waiting_times_by_point(enabled=True)
    claim_info = await create_segment_with_performer()
    claim_id = claim_info.claim_id

    await state_controller.apply(
        fresh_claim=False, target_status='performer_found', next_point_order=1,
    )

    mock_driver_route_watcher.response = {
        'courier': 'park_id_1_driver_uuid_1',
        'position': [55, 37],
        'etas': [],
    }

    response = await taxi_cargo_claims.post(
        f'/api/integration/v1/claims/points-eta?claim_id={claim_id}',
        headers=get_default_headers(),
    )
    assert response.status_code == 409
    assert response.json() == {
        'code': 'unknown_performer_position',
        'message': 'Не можем определить позицию исполнителя',
    }
    assert mock_driver_route_watcher.handler.times_called == 1


@pytest.mark.parametrize(
    ['config_enabled'],
    (
        pytest.param(
            True,
            marks=pytest.mark.config(CARGO_CLAIMS_ETA_USE_CACHE_ENABLED=True),
        ),
        pytest.param(
            False,
            marks=pytest.mark.config(CARGO_CLAIMS_ETA_USE_CACHE_ENABLED=False),
        ),
    ),
)
async def test_no_claim(
        taxi_cargo_claims, get_default_headers, config_enabled: bool,
):
    response = await taxi_cargo_claims.post(
        '/api/integration/v1/claims/points-eta',
        params={'claim_id': 'claim'},
        headers=get_default_headers(),
    )
    assert response.status_code == 404
