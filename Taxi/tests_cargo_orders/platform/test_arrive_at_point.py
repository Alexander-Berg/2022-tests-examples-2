import pytest

from testsuite.utils import matching

DEFAULT_HEADERS = {'Accept-Language': 'en'}


TEST_SIMPLE_JSON_PERFORMER_RESULT = {
    'car_id': 'car_id1',
    'car_model': 'some_car_model',
    'car_number': 'some_car_number',
    'driver_id': 'driver_id1',
    'is_deaf': False,
    'lookup_version': 1,
    'name': 'Kostya',
    'order_alias_id': '1234',
    'order_id': '9db1622e-582d-4091-b6fc-4cb2ffdc12c0',
    'park_clid': 'park_clid1',
    'park_id': 'park_id1',
    'park_name': 'some_park_name',
    'park_org_name': 'some_park_org_name',
    'phone_pd_id': 'phone_pd_id',
    'revision': 1,
    'tariff_class': 'cargo',
    'transport_type': 'electric_bicycle',
}


@pytest.fixture
def _platform_arrive_at_point(default_order_id, taxi_cargo_orders):
    async def _wrapper(point_id, driver_id='driver_id1', park_id='park_id1'):
        return await taxi_cargo_orders.post(
            '/v1/pro-platform/arrive_at_point',
            headers=DEFAULT_HEADERS,
            json={
                'cargo_ref_id': 'order/' + default_order_id,
                'last_known_status': 'new',
                'idempotency_token': 'some_token',
                'point_id': 1,
                'performer_params': {
                    'driver_profile_id': driver_id,
                    'park_id': park_id,
                    'app': {
                        'version_type': '',
                        'version': '9.40',
                        'platform': 'android',
                    },
                    'remote_ip': '12.34.56.78',
                },
            },
        )

    return _wrapper


@pytest.mark.parametrize(
    'claims_response_code,point_id,result_code',
    [
        (200, 100500, 200),
        (404, 100500, 404),
        (409, 100500, 409),
        (500, 100500, 500),
    ],
)
@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    name='cargo_orders_yagr_store_driver_position',
    consumers=['cargo-orders/yagr-store-driver-position'],
    default_value={'enabled': True},
)
async def test_claims_exchange_statuses(
        _platform_arrive_at_point,
        mockserver,
        mock_driver_tags_v1_match_profile,
        claims_response_code: int,
        point_id: int,
        result_code: int,
        my_waybill_info,
):
    @mockserver.json_handler('/cargo-dispatch/v1/waybill/arrive-at-point')
    def _mock_segment_init(request):
        return mockserver.make_response(
            json={'new_status': 'new', 'waybill_info': my_waybill_info}
            if claims_response_code == 200
            else {'code': 'not_found', 'message': 'some message'},
            status=claims_response_code,
        )

    @mockserver.json_handler('/yagr-raw/service/v2/position/store')
    def _mock_position_store(request):
        return mockserver.make_response(
            status=result_code,
            headers={'X-Polling-Power-Policy': 'policy'},
            content_type='application/json',
        )

    response = await _platform_arrive_at_point(point_id)
    assert response.status_code == result_code
    if result_code == 200:
        assert response.json() == {
            'performer': TEST_SIMPLE_JSON_PERFORMER_RESULT,
            'waybill': my_waybill_info,
            'status': matching.AnyString(),
        }


@pytest.mark.parametrize(
    'driver_id, park_id', [('driver_id1', ''), ('driver', 'park_id1')],
)
async def test_not_authorized(
        _platform_arrive_at_point, my_waybill_info, driver_id, park_id,
):
    response = await _platform_arrive_at_point(100500, driver_id, park_id)
    assert response.status_code == 403
    assert response.json() == {
        'code': 'not_authorized',
        'message': 'Попробуйте снова',
    }


async def test_batch(
        _platform_arrive_at_point,
        mockserver,
        mock_driver_tags_v1_match_profile,
        my_batch_waybill_info,
):
    @mockserver.json_handler('/cargo-dispatch/v1/waybill/arrive-at-point')
    def _mock_segment_init(request):
        return {'new_status': 'new', 'waybill_info': my_batch_waybill_info}

    response = await _platform_arrive_at_point(1)

    for item in my_batch_waybill_info['execution']['points']:
        item['eta_calculation_awaited'] = False
        del item['status']
    my_batch_waybill_info['waybill']['optional_return'] = False

    assert response.status_code == 200
    assert response.json() == {
        'performer': TEST_SIMPLE_JSON_PERFORMER_RESULT,
        'waybill': my_batch_waybill_info,
        'status': matching.AnyString(),
    }
