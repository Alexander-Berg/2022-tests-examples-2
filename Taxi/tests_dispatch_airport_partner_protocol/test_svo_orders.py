import bson
import pytest


from tests_dispatch_airport_partner_protocol import common


@pytest.mark.parametrize('status_code', [200, 404, 500])
async def test_svo_orders_reposition(
        taxi_dispatch_airport_partner_protocol, mockserver, status_code,
):
    @mockserver.json_handler('/dispatch-airport/v1/relocate/status')
    def _relocate_status(request):
        assert request.json['session_id'] == 'order_id_1'
        if status_code != 200:
            return mockserver.make_response(status=status_code)
        return {'car_number': 'A111AA', 'status': 'driving'}

    @mockserver.json_handler(
        'order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _get_fields(request):
        assert False

    response = await taxi_dispatch_airport_partner_protocol.get(
        '/svo/orders',
        params={'order_id': 'rep:order_id_1'},
        headers=common.DEFAULT_SVO_AUTH_TOKEN_HEADER,
    )
    assert response.status_code == status_code
    if status_code == 200:
        assert response.json() == {
            'orders': [{'order_id': 'rep:order_id_1', 'status': 'driving'}],
        }


@pytest.mark.parametrize(
    'order_proc_status, status, taxi_status, performer, result',
    [
        ('pending', 'pending', None, '123', 'pending'),
        ('finished', 'assigned', None, None, 'failedtoassign'),
        ('finished', 'assigned', None, '123', 'driving'),
        ('assigned', 'assigned', 'driving', None, 'driving'),
        ('assigned', 'assigned', 'waiting', '123', 'waiting'),
        ('assigned', 'assigned', 'transporting', '123', 'transporting'),
        ('assigned', 'finished', 'complete', '123', 'complete'),
        ('assigned', 'cancelled', 'driving', '123', 'cancelled'),
        ('assigned', 'finished', 'cancelled', '123', 'cancelled'),
        ('assigned', 'finished', 'failed', '123', 'cancelled'),
        ('finished', 'finished', 'expired', '123', 'expired'),
        ('finished', 'assigned', 'expired', '123', 'unknown'),
    ],
)
async def test_svo_orders_order_core(
        taxi_dispatch_airport_partner_protocol,
        mockserver,
        order_proc_status,
        status,
        taxi_status,
        performer,
        result,
):
    @mockserver.json_handler('/dispatch-airport/v1/relocate/status')
    def _relocate_status(request):
        assert False

    @mockserver.json_handler(
        'order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _get_fields(request):
        response_fields = {
            'document': {
                '_id': '123',
                'status': order_proc_status,
                'order': {'status': status, 'taxi_status': taxi_status},
                'performer': {'candidate_index': performer},
            },
            'revision': {'processing.version': 1, 'order.version': 1},
        }
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(response_fields),
        )

    response = await taxi_dispatch_airport_partner_protocol.get(
        '/svo/orders',
        params={'order_id': 'order_id_1'},
        headers=common.DEFAULT_SVO_AUTH_TOKEN_HEADER,
    )
    assert response.json() == {
        'orders': [{'order_id': 'order_id_1', 'status': result}],
    }


@pytest.mark.parametrize('status_code', [200, 404, 500])
async def test_svo_orders_order_core_codes(
        taxi_dispatch_airport_partner_protocol, mockserver, status_code,
):
    @mockserver.json_handler('/dispatch-airport/v1/relocate/status')
    def _relocate_status(request):
        assert False

    @mockserver.json_handler(
        'order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _get_fields(request):
        if status_code != 200:
            return mockserver.make_response(
                status=status_code,
                json={'code': 'no_such_order', 'message': 'No such order'},
            )
        response_fields = {
            'document': {
                '_id': '123',
                'status': 'assigned',
                'order': {'status': 'assigned', 'taxi_status': 'driving'},
                'performer': {'candidate_index': '123'},
            },
            'revision': {'processing.version': 1, 'order.version': 1},
        }
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(response_fields),
        )

    response = await taxi_dispatch_airport_partner_protocol.get(
        '/svo/orders',
        params={'order_id': 'order_id_1'},
        headers=common.DEFAULT_SVO_AUTH_TOKEN_HEADER,
    )
    assert response.status_code == status_code
    if status_code == 200:
        assert response.json() == {
            'orders': [{'order_id': 'order_id_1', 'status': 'driving'}],
        }


async def test_negative(taxi_dispatch_airport_partner_protocol):
    resp = await taxi_dispatch_airport_partner_protocol.get(
        '/svo/orders',
        params={'order_id': 'order_id_1'},
        headers={'Ya-Taxi-Token': 'not_existing_api_key'},
    )
    assert resp.status_code == 403
    assert resp.json()['code'] == 'INVALID_API_KEY'

    # bad request, no Api-Key header
    resp = await taxi_dispatch_airport_partner_protocol.get(
        '/svo/orders', params={'order_id': 'order_id_1'}, headers={},
    )
    assert resp.status_code == 400

    # bad request, no order_id
    resp = await taxi_dispatch_airport_partner_protocol.get(
        '/svo/orders', params={}, headers=common.DEFAULT_SVO_AUTH_TOKEN_HEADER,
    )
    assert resp.status_code == 400
