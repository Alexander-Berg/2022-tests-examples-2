import pytest

DEFAULT_HEADERS = {
    'Accept-Language': 'en',
    'X-Remote-IP': '12.34.56.78',
    'X-YaTaxi-Driver-Profile-Id': 'driver_id1',
    'X-YaTaxi-Park-Id': 'park_id1',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.40',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
    'X-Idempotency-Token': 'idempotency_token',
}

SCOPE = 'taximeter_async_operations'


@pytest.fixture(name='multi_skip_source_points')
def _multi_skip_source_points(taxi_cargo_orders):
    async def _wrapper(order_id, point_id):
        response = await taxi_cargo_orders.post(
            '/driver/v1/cargo-claims/v1/cargo/async/multi-skip-source-points',
            json={
                'cargo_ref_id': f'order/{order_id}',
                'point_id': point_id,
                'last_known_status': 'new',
                'reasons': ['some_reason_id'],
                'comment': 'Some comment',
            },
            headers=DEFAULT_HEADERS,
        )
        assert response.status_code == 200
        return response

    return _wrapper


@pytest.fixture(name='mock_increment_state_version')
def _mock_increment_state_version(mockserver):
    def _wrapper(cargo_order_id):
        @mockserver.json_handler(
            f'/cargo-dispatch/v1/waybill/state-version/increment',
        )
        def _mock(request):
            assert request.json == {'cargo_order_id': cargo_order_id}
            return {'state_version': '1234567890'}

        return _mock

    return _wrapper


@pytest.fixture(name='mock_processing_create_event')
def _mock_processing_create_event(mockserver):
    def _wrapper(cargo_order_id, expected_request):
        @mockserver.json_handler(f'/processing/v1/cargo/{SCOPE}/create-event')
        def _mock(request):
            assert request.args['item_id'] == f'order/{cargo_order_id}'
            assert request.json == expected_request
            return {'event_id': '0987654321'}

        return _mock

    return _wrapper


async def test_multi_skip_source_points(
        taxi_cargo_orders,
        mock_increment_state_version,
        mock_processing_create_event,
        multi_skip_source_points,
        default_order_id,
        kind='multi-skip-source-points-begin',
        point_id=642499,
):
    mock_increment_state_version(default_order_id)
    mock_processing_create_event(
        default_order_id,
        expected_request={
            'kind': kind,
            'accept_language': 'en',
            'remote_ip': '12.34.56.78',
            'taximeter_app': {
                'platform': 'android',
                'version': '9.40',
                'version_type': '',
            },
            'claim_point_id': point_id,
            'last_known_status': 'new',
            'reasons': ['some_reason_id'],
            'comment': 'Some comment',
        },
    )

    response = await multi_skip_source_points(
        default_order_id, point_id=642499,
    )
    assert response.json() == {'state_version': '1234567890'}
