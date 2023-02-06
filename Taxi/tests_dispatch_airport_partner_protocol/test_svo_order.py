import pytest

from tests_dispatch_airport_partner_protocol import common


@pytest.mark.parametrize(
    'error_code, status_code',
    [
        ('ok', 200),
        ('wrong_number', 404),
        ('wrong_polygon', 404),
        ('driver_busy', 400),
    ],
)
async def test_svo_order(
        taxi_dispatch_airport_partner_protocol,
        mockserver,
        error_code,
        status_code,
):
    @mockserver.json_handler('/dispatch-airport/v1/relocate/start')
    def _relocate_start(request):
        if status_code != 200:
            return mockserver.make_response(
                json={'code': error_code, 'message': error_code},
                status=status_code,
            )

        assert 'X-Idempotency-Token' in request.headers
        return {'session_id': 'session_id'}

    response = await taxi_dispatch_airport_partner_protocol.post(
        '/svo/order',
        {
            'car_number': 'A111AA',
            'polygon_id': 'polygon_id',
            'is_reposition': True,
        },
        headers=common.DEFAULT_SVO_AUTH_TOKEN_HEADER,
    )
    assert response.status_code == status_code
    if status_code == 200:
        assert response.json() == {'order_id': 'rep:session_id'}
    else:
        assert response.json() == {'code': error_code, 'message': error_code}


async def test_idempotency_token(
        taxi_dispatch_airport_partner_protocol, mockserver,
):
    @mockserver.json_handler('/dispatch-airport/v1/relocate/start')
    def _relocate_start(request):
        assert request.headers['X-Idempotency-Token'] == 'some_token'
        return {'session_id': 'session_id'}

    response = await taxi_dispatch_airport_partner_protocol.post(
        '/svo/order',
        {
            'car_number': 'A111AA',
            'polygon_id': 'polygon_id',
            'is_reposition': True,
            'idempotency_token': 'some_token',
        },
        headers=common.DEFAULT_SVO_AUTH_TOKEN_HEADER,
    )
    assert response.status_code == 200
    assert response.json() == {'order_id': 'rep:session_id'}


async def test_session_creation_failed(
        taxi_dispatch_airport_partner_protocol, mockserver,
):
    @mockserver.json_handler('/dispatch-airport/v1/relocate/start')
    def _relocate_start(request):
        return {
            'session_creation_fail_reason_code': 'some_code',
            'session_creation_fail_reason_msg': 'some_msg',
        }

    response = await taxi_dispatch_airport_partner_protocol.post(
        '/svo/order',
        {
            'car_number': 'A111AA',
            'polygon_id': 'polygon_id',
            'is_reposition': True,
        },
        headers=common.DEFAULT_SVO_AUTH_TOKEN_HEADER,
    )
    assert response.status_code == 200
    assert response.json() == {
        'order_creation_fail_reason_code': 'some_code',
        'order_creation_fail_reason_msg': 'some_msg',
    }


async def test_session_creation_failed_without_reason(
        taxi_dispatch_airport_partner_protocol, mockserver,
):
    @mockserver.json_handler('/dispatch-airport/v1/relocate/start')
    def _relocate_start(request):
        return {}

    response = await taxi_dispatch_airport_partner_protocol.post(
        '/svo/order',
        {
            'car_number': 'A111AA',
            'polygon_id': 'polygon_id',
            'is_reposition': True,
        },
        headers=common.DEFAULT_SVO_AUTH_TOKEN_HEADER,
    )
    assert response.status_code == 500


async def test_negative(taxi_dispatch_airport_partner_protocol):
    resp = await taxi_dispatch_airport_partner_protocol.post(
        '/svo/order',
        {
            'car_number': 'A111AA',
            'polygon_id': 'polygon_id',
            'is_reposition': True,
        },
        headers={'Ya-Taxi-Token': 'not_existing_api_key'},
    )
    assert resp.status_code == 403
    assert resp.json()['code'] == 'INVALID_API_KEY'

    # bad request, no Api-Key header
    resp = await taxi_dispatch_airport_partner_protocol.post(
        '/svo/order',
        {
            'car_number': 'A111AA',
            'polygon_id': 'polygon_id',
            'is_reposition': True,
        },
        headers={},
    )
    assert resp.status_code == 400

    # bad request, not reposition
    resp = await taxi_dispatch_airport_partner_protocol.post(
        '/svo/order',
        {
            'car_number': 'A111AA',
            'polygon_id': 'polygon_id',
            'is_reposition': False,
        },
        headers=common.DEFAULT_SVO_AUTH_TOKEN_HEADER,
    )
    assert resp.status_code == 400
    assert resp.json()['code'] == 'NOT_REPOSITION'
