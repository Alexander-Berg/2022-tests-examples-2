import pytest

from testsuite.utils import matching

from . import utils_v2


@pytest.mark.parametrize(
    'handler, method',
    [
        ('/api/integration/v2/claims/info', 'post'),
        ('/v2/claims/full', 'get'),
        pytest.param('/api/integration/v2/claims/info', 'post'),
        pytest.param('/v2/claims/full', 'get'),
    ],
)
async def test_claim_not_found(
        taxi_cargo_claims, get_default_headers, handler: str, method: str,
):
    response = await getattr(taxi_cargo_claims, method)(
        f'{handler}?claim_id=some_not_found', headers=get_default_headers(),
    )
    assert response.status_code == 404


async def test_bad_corp_client(
        taxi_cargo_claims, get_default_headers, state_controller,
):
    state_controller.use_create_version('v2')
    claim_info = await state_controller.apply(target_status='new')

    response = await taxi_cargo_claims.post(
        f'/api/integration/v2/claims/info?claim_id={claim_info.claim_id}',
        headers=get_default_headers('other_corp_id0123456789012345678'),
    )
    assert response.status_code == 404


@pytest.mark.parametrize(
    'handler, method, response_getter, need_zone_id',
    [
        pytest.param(
            '/api/integration/v2/claims/info',
            'post',
            utils_v2.get_default_response_v2,
            False,
            id='api_newway',
        ),
        pytest.param(
            '/v2/claims/full',
            'get',
            utils_v2.get_default_response_v2_inner,
            True,
            id='internal_newway',
        ),
    ],
)
async def test_get_v2_200(
        taxi_cargo_claims,
        get_default_headers,
        handler: str,
        method: str,
        response_getter,
        state_controller,
        mockserver,
        need_zone_id,
):
    @mockserver.json_handler('/esignature-issuer/v1/signatures/list')
    def _signature_list(request):
        return {
            'doc_type': request.json['doc_type'],
            'doc_id': request.json['doc_id'],
            'signatures': [
                {
                    'signature_id': 'sender_to_driver_1',
                    'signer_id': '+79999999991_id',
                    'sign_type': 'ya_sms',
                    'code_masked': '12**56',
                },
            ],
        }

    state_controller.use_create_version('v2')
    request = utils_v2.get_create_request()
    state_controller.handlers().create.request = request
    state_controller.handlers().create.headers = get_default_headers()
    state_controller.handlers().create.headers['User-Agent'] = 'Yandex'
    claim_info = await state_controller.apply(
        target_status='ready_for_approval',
    )

    claim_id = claim_info.claim_id
    point_ids = utils_v2.get_point_id_to_claim_point_id(
        request, claim_info.claim_full_response,
    )

    expected_response = response_getter(claim_id, point_ids)
    expected_response['matched_cars'] = [
        {'taxi_class': 'cargo', 'cargo_loaders': 2, 'cargo_type': 'lcv_m'},
    ]
    expected_response['status'] = 'ready_for_approval'
    expected_response['initiator_yandex_login'] = 'abacaba'
    if handler == '/v2/claims/full':
        expected_response['origin_info'] = {
            'origin': 'api',
            'displayed_origin': 'API',
            'user_agent': 'Yandex',
        }
        expected_response['taxi_requirements'] = {
            'cargo_loaders': 2,
            'cargo_type': 'lcv_m',
        }
        expected_response['dispatch_flow'] = 'newway'
        expected_response['initiator_yandex_uid'] = 'user_id'

    if need_zone_id:
        expected_response['zone_id'] = 'moscow'

    response = await getattr(taxi_cargo_claims, method)(
        f'{handler}?claim_id={claim_id}', headers=get_default_headers(),
    )

    assert response.status_code == 200

    json = response.json()
    del json['created_ts']
    del json['updated_ts']
    del json['taxi_offer']
    if 'segments' in expected_response:
        del expected_response['segments']
    if 'segments' in json:
        del json['segments']
    if json.get('revision'):
        del json['revision']
    json['pricing'] = {}
    if 'mpc_corrections_count' in json:
        del json['mpc_corrections_count']

    assert json == expected_response


@pytest.mark.parametrize(
    (
        'target_status,next_point,logistics_dispatcher_response,'
        'expected_points_visited_at'
    ),
    [
        pytest.param(
            'performer_found',
            1,
            {
                'plan': [
                    {
                        'timestamp': 1602313200,
                        'id': 1,
                        'cargo_point_id': '1',
                        'location': [37.2, 55.8],
                    },
                    {
                        'timestamp': 1602316800,
                        'id': 2,
                        'cargo_point_id': '2',
                        'location': [37.0, 55.8],
                    },
                    {
                        'timestamp': 1602320400,
                        'id': 3,
                        'cargo_point_id': '3',
                        'location': [37.0, 55.0],
                    },
                    {
                        'timestamp': 1602324000,
                        'id': 4,
                        'cargo_point_id': '4',
                        'location': [37.0, 55.5],
                    },
                ],
                'contractor': {'external_order_id': 'taxi_order_id'},
            },
            [
                {
                    'expected': '2020-10-10T07:00:00+00:00',
                    'expected_waiting_time_sec': 180,
                },
                {
                    'expected': '2020-10-10T08:00:00+00:00',
                    'expected_waiting_time_sec': 180,
                },
                {
                    'expected': '2020-10-10T09:00:00+00:00',
                    'expected_waiting_time_sec': 180,
                },
                {
                    'expected': '2020-10-10T10:00:00+00:00',
                    'expected_waiting_time_sec': 180,
                },
            ],
            id='no_point_visited',
        ),
        pytest.param(
            'pickuped',
            2,
            {
                'plan': [
                    {
                        'timestamp': 1602316800,
                        'id': 2,
                        'cargo_point_id': '2',
                        'location': [37.0, 55.8],
                    },
                    {
                        'timestamp': 1602320400,
                        'id': 3,
                        'cargo_point_id': '3',
                        'location': [37.0, 55.0],
                    },
                    {
                        'timestamp': 1602324000,
                        'id': 4,
                        'cargo_point_id': '4',
                        'location': [37.0, 55.5],
                    },
                ],
                'contractor': {'external_order_id': 'taxi_order_id'},
            },
            [
                {
                    'actual': matching.any_string,
                    'expected_waiting_time_sec': 180,
                },
                {
                    'expected': '2020-10-10T08:00:00+00:00',
                    'expected_waiting_time_sec': 180,
                },
                {
                    'expected': '2020-10-10T09:00:00+00:00',
                    'expected_waiting_time_sec': 180,
                },
                {
                    'expected': '2020-10-10T10:00:00+00:00',
                    'expected_waiting_time_sec': 180,
                },
            ],
            id='source_point_visited',
        ),
        pytest.param(
            'pickuped',
            2,
            {
                'plan': [
                    {
                        'timestamp': 1602316800,
                        'id': 2,
                        'cargo_point_id': '2',
                        'location': [37.0, 55.8],
                    },
                    {
                        'timestamp': 1602320400,
                        'id': 3,
                        'cargo_point_id': '3',
                        'location': [37.0, 55.0],
                    },
                ],
                'contractor': {'external_order_id': 'taxi_order_id'},
            },
            [
                {
                    'actual': matching.any_string,
                    'expected_waiting_time_sec': 180,
                },
                {
                    'expected': '2020-10-10T08:00:00+00:00',
                    'expected_waiting_time_sec': 180,
                },
                {
                    'expected': '2020-10-10T09:00:00+00:00',
                    'expected_waiting_time_sec': 180,
                },
                {},
            ],
            id='some_points_missing',
        ),
        pytest.param(
            'performer_found',
            1,
            {
                'plan': [
                    {
                        'timestamp': 1602313200,
                        'id': 1,
                        'cargo_point_id': '1',
                        'location': [37.2, 55.8],
                    },
                    {
                        'timestamp': 1602316800,
                        'id': 2,
                        'cargo_point_id': '2',
                        'location': [37.0, 55.8],
                    },
                    {
                        'timestamp': 1602320400,
                        'id': 3,
                        'cargo_point_id': '3',
                        'location': [37.0, 55.0],
                    },
                    {
                        'timestamp': 1602324000,
                        'id': 4,
                        'cargo_point_id': '4',
                        'location': [37.0, 55.5],
                    },
                ],
                'contractor': {'external_order_id': 'fake'},
            },
            [
                {'expected_waiting_time_sec': 180},
                {'expected_waiting_time_sec': 180},
                {'expected_waiting_time_sec': 180},
                {'expected_waiting_time_sec': 180},
            ],
            id='order_id_mismatch',
        ),
        pytest.param(
            'performer_found',
            1,
            None,
            [
                {'expected_waiting_time_sec': 180},
                {'expected_waiting_time_sec': 180},
                {'expected_waiting_time_sec': 180},
                {'expected_waiting_time_sec': 180},
            ],
            id='logistic_dispatcher_exception',
        ),
    ],
)
@pytest.mark.now('2020-10-10T06:59:00+00:00')
async def test_get_eta_from_logistic_dispatcher(
        mockserver,
        taxi_cargo_claims,
        taxi_config,
        create_segment_with_performer,
        exp_cargo_waiting_times_by_point,
        get_db_segment_ids,
        get_default_headers,
        state_controller,
        target_status,
        next_point,
        logistics_dispatcher_response,
        expected_points_visited_at,
):
    await exp_cargo_waiting_times_by_point(enabled=True)
    claim_info = await create_segment_with_performer()

    if logistics_dispatcher_response is not None:
        segment_ids = await get_db_segment_ids()
        segment_id = segment_ids[0]

        segment = await taxi_cargo_claims.post(
            f'/v1/segments/info?segment_id={segment_id}',
            json={},
            headers=get_default_headers(),
        )

        for point in segment.json()['points']:
            for plan_point in logistics_dispatcher_response['plan']:
                if plan_point['cargo_point_id'] == str(
                        point['claim_point_id'],
                ):
                    plan_point['cargo_point_id'] = point['point_id']

    @mockserver.json_handler('/logistic-dispatcher/api/contractor/session')
    def _mock_logistic_dispatcher(request):
        if logistics_dispatcher_response is not None:
            return logistics_dispatcher_response
        return mockserver.make_response(status=500)

    await state_controller.apply(
        fresh_claim=False,
        target_status=target_status,
        next_point_order=next_point,
    )

    taxi_config.set_values(
        dict(
            CARGO_CLAIMS_GET_ETA_FROM_LOGISTIC_DISPATCHER={
                '__default__': True,
            },
        ),
    )
    await taxi_cargo_claims.invalidate_caches()

    response = await taxi_cargo_claims.post(
        f'/api/integration/v2/claims/info?claim_id={claim_info.claim_id}',
        headers=get_default_headers(),
    )

    assert response.status_code == 200

    json = response.json()
    for (point, expected_visited_at) in zip(
            json['route_points'], expected_points_visited_at,
    ):
        assert point['visited_at'] == expected_visited_at, point['id']


@pytest.mark.parametrize(
    ('target_status,next_point,' 'expected_waiting, exp_enabled'),
    [
        pytest.param(
            'performer_found',
            1,
            [{}, {}, {}, {}],
            False,
            id='no_point_visited',
        ),
        pytest.param(
            'pickuped',
            2,
            [
                {
                    'actual': matching.any_string,
                    'expected_waiting_time_sec': 180,
                },
                {'expected_waiting_time_sec': 180},
                {'expected_waiting_time_sec': 180},
                {'expected_waiting_time_sec': 180},
            ],
            True,
            id='source_point_visited',
        ),
    ],
)
@pytest.mark.now('2020-10-10T06:59:00+00:00')
async def test_empty_waiting_times_by_point(
        taxi_cargo_claims,
        create_segment_with_performer,
        exp_cargo_waiting_times_by_point,
        get_default_headers,
        state_controller,
        target_status,
        next_point,
        expected_waiting,
        exp_enabled,
):
    await exp_cargo_waiting_times_by_point(enabled=exp_enabled)
    claim_info = await create_segment_with_performer()

    await state_controller.apply(
        fresh_claim=False,
        target_status=target_status,
        next_point_order=next_point,
    )

    response = await taxi_cargo_claims.post(
        f'/api/integration/v2/claims/info?claim_id={claim_info.claim_id}',
        headers=get_default_headers(),
    )
    assert response.status_code == 200

    json = response.json()
    for (point, expected) in zip(json['route_points'], expected_waiting):
        assert point['visited_at'] == expected, point['id']


@pytest.mark.now('2021-01-01T00:00:00.000Z')
@pytest.mark.config(
    CARGO_CLAIMS_ETA_SOURCE_BY_CORP_CLIENT={
        '__default__': 'driver_route_watcher',
    },
)
@pytest.mark.parametrize(
    ('target_status,next_point,drw_response,' 'expected_points_visited_at'),
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
                    {
                        'point': [55.4, 37.5],
                        'time_left': 7200.0,
                        'distance_left': 3000.0,
                        'point_id': '4',
                    },
                ],
            },
            [
                {'expected': '2021-01-01T00:30:00+00:00'},
                {'expected': '2021-01-01T01:00:00+00:00'},
                {'expected': '2021-01-01T01:30:00+00:00'},
                {'expected': '2021-01-01T02:00:00+00:00'},
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
                    {
                        'point': [55.4, 37.5],
                        'time_left': 7200.0,
                        'distance_left': 3000.0,
                        'point_id': '4',
                    },
                ],
            },
            [
                {'actual': matching.any_string},
                {'expected': '2021-01-01T01:00:00+00:00'},
                {'expected': '2021-01-01T01:30:00+00:00'},
                {'expected': '2021-01-01T02:00:00+00:00'},
            ],
            id='source_point_visited',
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
                {'actual': matching.any_string},
                {'expected': '2021-01-01T01:00:00+00:00'},
                {'expected': '2021-01-01T01:30:00+00:00'},
                {},
            ],
            id='some_points_missing',
        ),
    ],
)
async def test_get_eta_from_drw(
        mockserver,
        taxi_cargo_claims,
        taxi_config,
        create_segment_with_performer,
        get_db_segment_ids,
        get_default_headers,
        state_controller,
        target_status,
        next_point,
        drw_response,
        expected_points_visited_at,
):

    claim_info = await create_segment_with_performer()

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

    @mockserver.json_handler(
        '/driver-route-responder/cargo/timeleft-by-courier',
    )
    def _mock_drw(request):
        if drw_response is not None:
            return drw_response
        return mockserver.make_response(status=500)

    await state_controller.apply(
        fresh_claim=False,
        target_status=target_status,
        next_point_order=next_point,
    )

    taxi_config.set_values(
        dict(
            CARGO_CLAIMS_GET_ETA_FROM_LOGISTIC_DISPATCHER={
                '__default__': True,
            },
        ),
    )
    await taxi_cargo_claims.invalidate_caches()

    response = await taxi_cargo_claims.post(
        f'/api/integration/v2/claims/info?claim_id={claim_info.claim_id}',
        headers=get_default_headers(),
    )

    assert response.status_code == 200

    json = response.json()
    for (point, expected_visited_at) in zip(
            json['route_points'], expected_points_visited_at,
    ):
        assert point['visited_at'] == expected_visited_at, point['id']


async def test_performer_info(
        taxi_cargo_claims, state_controller, get_default_headers,
):
    state_controller.use_create_version('v2')
    request = utils_v2.get_create_request()
    state_controller.handlers().create.request = request
    claim_info = await state_controller.apply(target_status='performer_found')

    claim_id = claim_info.claim_id
    response = await getattr(taxi_cargo_claims, 'get')(
        f'/v2/claims/full?claim_id={claim_id}&parts=performer_info',
        headers=get_default_headers(),
    )
    assert response.status_code == 200
    assert response.json()['performer_info'] == {
        'courier_name': 'Kostya',
        'legal_name': 'park_org_name_1',
        'car_model': 'car_model_1',
        'car_number': 'car_number_1',
        'park_id': 'park_id1',
        'driver_id': 'driver_id1',
        'park_clid': 'park_clid1',
    }


async def test_get_transport_type(
        taxi_cargo_claims, get_default_headers, prepare_state, get_segment,
):
    segment_id = await prepare_state(
        visit_order=1, last_exchange_init=False, transport_type='car',
    )
    claim_id = (await get_segment(segment_id))['diagnostics']['claim_id']

    response = await getattr(taxi_cargo_claims, 'get')(
        f'/v2/claims/full?claim_id={claim_id}&parts=performer_info',
        headers=get_default_headers(),
    )

    assert response.status_code == 200
    assert response.json()['performer_info']['transport_type'] == 'car'


def _points_only_response(claim):
    claim['items'] = []
    claim.pop('client_requirements')
    claim.pop('custom_context')


def _points_items_response(claim):
    claim.pop('client_requirements')
    claim.pop('custom_context')


async def test_taxi_order_id_200(
        taxi_cargo_claims, get_default_headers, state_controller,
):
    state_controller.use_create_version('v2')

    request = utils_v2.get_create_request()
    state_controller.handlers().create.request = request
    claim_info = await state_controller.apply(target_status='performer_draft')

    claim_id = claim_info.claim_id
    point_ids = utils_v2.get_point_id_to_claim_point_id(
        request, claim_info.claim_full_response,
    )

    expected_response = utils_v2.get_default_response_v2_inner(
        claim_id, point_ids,
    )

    expected_response['status'] = 'performer_draft'
    expected_response['taxi_order_id'] = 'taxi_order_id_1'

    response = await taxi_cargo_claims.get(
        f'/v2/claims/full?claim_id={claim_id}', headers=get_default_headers(),
    )
    assert response.status_code == 200
    json = response.json()
    assert json['taxi_order_id'] == 'taxi_order_id_1'
    assert json['status'] == 'performer_draft'


async def test_dragon_free_performer_lookup(
        taxi_cargo_claims, get_default_headers, create_segment,
):
    claim_info = await create_segment()
    claim_id = claim_info.claim_id

    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/info',
        params={'claim_id': claim_id},
        headers=get_default_headers(),
    )
    assert response.json()['available_cancel_state'] == 'free'


async def test_payment_method(
        taxi_cargo_claims,
        create_segment_with_payment,
        get_segment_id,
        get_default_headers,
        mock_payment_create,
        payment_method='card',
):
    claim_info = await create_segment_with_payment(
        payment_method=payment_method,
    )
    claim_id = claim_info.claim_id

    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/info',
        params={'claim_id': claim_id},
        headers=get_default_headers(),
    )
    assert response.status_code == 200

    claim = response.json()
    for point in claim['route_points']:
        if point['type'] == 'destination':
            assert (
                point['payment_on_delivery']['payment_ref_id']
                == matching.AnyString()
            )
            assert (
                point['payment_on_delivery']['payment_method']
                == payment_method
            )
            assert point['payment_on_delivery']['flow'] == 'service_usage'
        else:
            assert 'payment_on_delivery' not in point


async def test_taxi_requirements(
        taxi_cargo_claims,
        get_default_c2c_request_v2_full,
        state_controller,
        get_default_headers,
):
    request = get_default_c2c_request_v2_full(cargo=True)
    state_controller.use_create_version('v2_cargo_c2c')
    state_controller.handlers().create.request = request
    claim_info = await state_controller.apply(
        target_status='ready_for_pickup_confirmation', next_point_order=1,
    )

    response = await taxi_cargo_claims.get(
        '/v2/claims/full',
        params={'claim_id': claim_info.claim_id},
        headers=get_default_headers(),
    )

    assert response.status_code == 200
    assert response.json()['taxi_requirements'] == {'door_to_door': True}


async def test_route_id(
        taxi_cargo_claims,
        create_segment_with_performer,
        get_segment_id,
        get_default_headers,
        get_default_cargo_order_id,
        get_default_corp_client_id,
        route_id='12345',
):
    claim_info = await create_segment_with_performer(route_id=route_id)
    claim_id = claim_info.claim_id

    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/info',
        params={'claim_id': claim_id},
        headers=get_default_headers(),
    )
    assert response.status_code == 200
    assert response.json()['route_id'] == route_id
