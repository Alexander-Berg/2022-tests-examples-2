import pytest

from testsuite.utils import matching


@pytest.fixture(name='mock_claims_exchange_init')
def _mock_claims_exchange_init(mockserver):
    def _wrapper(expected_request: dict = None, response: dict = None):
        @mockserver.json_handler('/cargo-claims/v1/segments/exchange/init')
        def _exchange_init(request):
            if expected_request:
                assert request.json == expected_request
            return (
                {
                    'new_status': 'pickup_confirmation',
                    'new_claim_status': 'ready_for_pickup_confirmation',
                }
                if response is None
                else response
            )

        return _exchange_init

    return _wrapper


@pytest.fixture(name='dispatch_init_point')
def _dispatch_init_point(
        taxi_cargo_dispatch, get_point_execution_by_visit_order,
):
    async def _wrapper(
            waybill_external_ref: str,
            is_driver_request: bool = True,
            do_arrive_at_point: bool = None,
    ):
        point = await get_point_execution_by_visit_order(
            waybill_ref=waybill_external_ref, visit_order=1,
        )

        request_body = {
            'last_known_status': 'new',
            'point_id': point['claim_point_id'],
            'is_driver_request': is_driver_request,
            'performer_info': {
                'driver_id': '789',
                'park_id': 'park_id_1',
                'taximeter_app': {
                    'version': '9.09',
                    'version_type': 'dev',
                    'platform': 'android',
                },
            },
        }

        headers = {'Accept-Language': 'ru', 'X-Remote-Ip': '0.0.0.0'}

        if is_driver_request:
            request_body['idempotency_token'] = '123456'
        else:
            headers.pop('X-Remote-Ip')
            headers['X-Idempotency-Token'] = 'admin_123456'

        if do_arrive_at_point:
            request_body['do_arrive_at_point'] = do_arrive_at_point

        response = await taxi_cargo_dispatch.post(
            '/v1/waybill/exchange/init',
            params={'waybill_external_ref': waybill_external_ref},
            json=request_body,
            headers=headers,
        )
        return response

    return _wrapper


async def test_happy_path(
        dispatch_init_point,
        happy_path_state_performer_found,
        mock_claims_exchange_init,
):
    mock_claims_exchange_init()
    response = await dispatch_init_point('waybill_fb_3')
    assert response.status_code == 200
    assert response.json() == {'new_status': 'pickup_confirmation'}


async def test_conflict(
        dispatch_init_point,
        happy_path_state_performer_found,
        mock_claims_exchange_init,
        mockserver,
):
    mock_claims_exchange_init(
        response=mockserver.make_response(
            status=409,
            json={'code': 'state_mismatch', 'message': 'initation conflict'},
        ),
    )
    response = await dispatch_init_point('waybill_fb_3')
    assert response.status_code == 409


async def test_send_driver(
        dispatch_init_point,
        happy_path_state_performer_found,
        mock_claims_exchange_init,
        get_point_execution_by_visit_order,
        waybill_ref='waybill_fb_3',
):
    point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=1,
    )

    mock_claims_exchange_init(
        expected_request={
            'cargo_order_id': matching.AnyString(),
            'idempotency_token': '123456',
            'driver': {
                'driver_profile_id': '789',
                'park_id': 'park_id_1',
                'taximeter_app': {
                    'version': '9.09',
                    'version_type': 'dev',
                    'platform': 'android',
                },
            },
            'last_known_status': 'new',
            'point_id': point['claim_point_id'],
        },
    )
    response = await dispatch_init_point(waybill_ref)
    assert response.status_code == 200


async def test_support_request(
        dispatch_init_point,
        happy_path_state_performer_found,
        mock_claims_exchange_init,
        get_point_execution_by_visit_order,
        waybill_ref='waybill_fb_3',
):
    point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=1,
    )

    mock_claims_exchange_init(
        expected_request={
            'cargo_order_id': matching.AnyString(),
            'idempotency_token': 'admin_123456',
            'last_known_status': 'new',
            'point_id': point['claim_point_id'],
        },
    )
    response = await dispatch_init_point(waybill_ref, is_driver_request=False)
    assert response.status_code == 200


async def test_batch_order(
        dispatch_init_point,
        happy_path_state_performer_found,
        mock_claims_exchange_init,
        get_point_execution_by_visit_order,
        waybill_ref='waybill_smart_1',
):
    point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=1,
    )
    mock_claims_exchange_init(
        expected_request={
            'cargo_order_id': matching.AnyString(),
            'idempotency_token': '123456',
            'driver': {
                'driver_profile_id': '789',
                'park_id': 'park_id_1',
                'taximeter_app': {
                    'version': '9.09',
                    'version_type': 'dev',
                    'platform': 'android',
                },
            },
            'point_id': point['claim_point_id'],
        },
    )
    response = await dispatch_init_point(waybill_ref)
    assert response.status_code == 200


async def test_no_idempotency_token(
        taxi_cargo_dispatch,
        happy_path_state_performer_found,
        get_point_execution_by_visit_order,
        mock_claims_exchange_init,
):
    mock_claims_exchange_init()

    waybill_ref = 'waybill_smart_1'
    point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=1,
    )
    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/exchange/init',
        params={'waybill_external_ref': waybill_ref},
        json={'point_id': point['claim_point_id'], 'is_driver_request': False},
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'bad_request',
        'message': 'No idempotency token',
    }


async def test_do_arrive_at_point(
        dispatch_init_point,
        happy_path_state_performer_found,
        mock_claims_exchange_init,
        mock_claims_arrive_at_point,
        get_point_execution_by_visit_order,
        waybill_ref='waybill_fb_3',
):
    point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=1,
    )

    _mock_arrive = mock_claims_arrive_at_point(
        expected_request={
            'cargo_order_id': matching.AnyString(),
            'driver': {'driver_profile_id': '789', 'park_id': 'park_id_1'},
            'last_known_status': 'new',
            'point_id': point['claim_point_id'],
        },
    )

    mock_claims_exchange_init(
        expected_request={
            'cargo_order_id': matching.AnyString(),
            'idempotency_token': '123456',
            'driver': {
                'driver_profile_id': '789',
                'park_id': 'park_id_1',
                'taximeter_app': {
                    'version': '9.09',
                    'version_type': 'dev',
                    'platform': 'android',
                },
            },
            'last_known_status': 'new',
            'point_id': point['claim_point_id'],
        },
    )
    response = await dispatch_init_point(waybill_ref, do_arrive_at_point=True)
    assert response.status_code == 200

    assert _mock_arrive.times_called


async def test_do_not_arrive_at_point(
        dispatch_init_point,
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        mock_claims_exchange_init,
        mock_claims_arrive_at_point,
        get_point_execution_by_visit_order,
        waybill_ref='waybill_fb_3',
):
    """
    Point status already 'arrived'.
    So do not invoke /arrive-at-point
    """

    # Arrive first point
    segment = happy_path_claims_segment_db.get_segment('seg3')
    segment.set_point_visit_status('p1', 'arrived')

    point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=1,
    )

    _mock_arrive = mock_claims_arrive_at_point()
    mock_claims_exchange_init(
        expected_request={
            'cargo_order_id': matching.AnyString(),
            'idempotency_token': '123456',
            'driver': {
                'driver_profile_id': '789',
                'park_id': 'park_id_1',
                'taximeter_app': {
                    'version': '9.09',
                    'version_type': 'dev',
                    'platform': 'android',
                },
            },
            'last_known_status': 'new',
            'point_id': point['claim_point_id'],
        },
    )
    response = await dispatch_init_point(waybill_ref, do_arrive_at_point=True)
    assert response.status_code == 200

    assert not _mock_arrive.times_called


async def test_arrive_at_point_error(
        dispatch_init_point,
        happy_path_state_performer_found,
        mock_claims_arrive_at_point,
        mockserver,
        waybill_ref='waybill_fb_3',
):
    _mock_arrive = mock_claims_arrive_at_point(
        response=mockserver.make_response(
            status=409,
            json={'code': 'state_mismatch', 'message': 'more than 500 meters'},
        ),
    )
    response = await dispatch_init_point(waybill_ref, do_arrive_at_point=True)
    assert response.status_code == 409
    assert response.json() == {
        'code': 'state_mismatch',
        'message': 'more than 500 meters',
    }

    assert _mock_arrive.times_called
