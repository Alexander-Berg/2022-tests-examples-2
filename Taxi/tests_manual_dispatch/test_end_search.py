import copy

import bson
import pytest

FIELDS_RESPONSE = {
    'document': {
        'order': {
            'user_id': '7b8e146257b44123b25ce2491f1dafd8',
            'status': 'pending',
        },
        '_id': '4b43de8afe042e02b0926fc0ae15f9e9',
        'processing': {'version': 5},
    },
    'order_id': '4b43de8afe042e02b0926fc0ae15f9e9',
    'replica': 'master',
    'revision': {'version': 'DAAAAAAABgAMAAQABgAAAAft4rR0AQAA'},
}


@pytest.mark.config(MANUAL_DISPATCH_DISABLE_LEGACY_HANDLERS=True)
@pytest.mark.now('2020-09-21T12:34:57.324+00:00')
async def test_end_search_success(taxi_manual_dispatch, headers, mockserver):
    @mockserver.json_handler(
        'order-core/internal/processing/v1/order-proc/get-fields',
    )
    def mock_get_order_fields(request):
        request_body = bson.BSON.decode(request.get_data())
        assert set(request_body['fields']) > set(
            ['order.user_id', 'order.status'],
        )
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(FIELDS_RESPONSE),
        )

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/set-fields',
    )
    def mock_set_order_fields(request):
        assert request.content_type == 'application/bson'
        request_body = bson.BSON.decode(request.get_data())
        assert request_body['update']['$set'] == {
            'order_info.need_sync': True,
            'order.status': 'finished',
            'order.taxi_status': 'expired',
        }
        assert request_body['update']['$push'] == {
            'order_info.statistics.status_updates': {
                'h2': False,
                'h': True,
                'c': {'$date': '2020-09-21T12:34:57.324+0000'},
                's': 'finished',
                't': 'expired',
                'q': 'manual_dispatch',
                'stp': True,
            },
        }
        assert request_body['update']['$inc'] == {'processing.version': 1}
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(FIELDS_RESPONSE),
        )

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/event/start-lookup',
    )
    def start_lookup(request):
        assert bson.BSON.decode(request.get_data()) == {
            'filters': {'status': 'pending'},
        }
        return mockserver.make_response('', status=200)

    response = await taxi_manual_dispatch.post(
        '/v1/dispatch/end-search',
        headers=headers,
        json={'order_id': 'order_id_1'},
    )
    assert response.status_code == 200
    assert mock_set_order_fields.times_called == 1
    assert mock_get_order_fields.times_called == 1
    assert start_lookup.times_called == 0


@pytest.mark.config(MANUAL_DISPATCH_DISABLE_LEGACY_HANDLERS=True)
async def test_end_search_404(taxi_manual_dispatch, headers, mockserver):
    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def get_order_fields(request):
        return mockserver.make_response(
            status=404,
            json={
                'code': 'no_such_order',
                'message': 'No such order in order_core_response.json',
            },
        )

    response = await taxi_manual_dispatch.post(
        '/v1/dispatch/end-search',
        headers=headers,
        json={'order_id': 'order_id_1'},
    )
    assert response.status_code == 404
    assert get_order_fields.times_called == 1


@pytest.mark.config(MANUAL_DISPATCH_DISABLE_LEGACY_HANDLERS=True)
async def test_not_pending(taxi_manual_dispatch, headers, mockserver):
    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def get_order_fields(request):
        response = copy.deepcopy(FIELDS_RESPONSE)
        response['document']['order']['status'] = 'finished'
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(response),
        )

    response = await taxi_manual_dispatch.post(
        '/v1/dispatch/end-search',
        headers=headers,
        json={'order_id': 'order_id_1'},
    )
    assert response.status_code == 409
    assert get_order_fields.times_called == 1
    assert response.json()['code'] == 'search_ended'
