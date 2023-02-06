import datetime

from aiohttp import web
import bson
import pytest


def setup_mocks(mockserver, mock_billing_orders, mock_order_core):
    @mock_order_core('/internal/antifraud/v1/cancel-order')
    def _order_core_cancel_order(request):
        assert request.method == 'POST'
        responses = {
            '8c83b49edb274ce0992f337061047375': 200,
            'unknown-order-id': 404,
            'order-in-transporting-state': 406,
        }
        return web.Response(status=responses[request.query['order_id']])

    @mock_order_core('/v1/tc/order-fields')
    def _order_core_order_fields(request):
        assert request.method == 'POST'
        responses = {
            '8c83b49edb274ce0992f337061047375': (
                200,
                dict(
                    order_id='8c83b49edb274ce0992f337061047375',
                    fields={
                        'order': {
                            'cost': 123,
                            'driver_cost': {'cost': 120},
                            'nz': 'msk',
                            'user_id': 'aaa',
                            'request': {'due': '2019-01-29T00:00:00+00:00'},
                            'status': 'finished',
                            'taxi_status': 'complete',
                            'version': 2,
                        },
                        'payment_tech': {'type': 'card'},
                        'performer': {'alias_id': 'xxx'},
                        'updated': '2019-01-29T00:00:00+00:00',
                    },
                    version='PROC_VERSION',
                    replica='secondary',
                ),
            ),
            'unknown-order-id': (
                404,
                dict(code='404', message='Ne hash los\''),
            ),
            'order-in-transporting-state': (
                200,
                dict(
                    order_id='order-in-transporting-state',
                    fields={
                        'order': {
                            'cost': 123,
                            'driver_cost': {'cost': 120},
                            'nz': 'msk',
                            'user_id': 'aaa',
                            'request': {'due': '2019-01-29T00:00:00+00:00'},
                            'status': 'assigned',
                            'taxi_status': 'transporting',
                            'version': 2,
                        },
                        'payment_tech': {'type': 'card'},
                        'performer': {'alias_id': 'xxx'},
                        'updated': '2019-01-29T00:00:00+00:00',
                    },
                    version='PROC_VERSION',
                    replica='secondary',
                ),
            ),
        }
        response = responses[request.json['order_id']]
        return web.json_response(status=response[0], data=response[1])

    @mock_order_core('/v1/tc/set-order-fields')
    def _order_core_set_order_fields(request):
        assert request.method == 'POST'
        requests = {
            '8c83b49edb274ce0992f337061047375': {
                'call_processing': False,
                'order_id': '8c83b49edb274ce0992f337061047375',
                'update': {
                    'set': {
                        'order.cost': 0.0,
                        'order.driver_cost.calc_method': 'other',
                        'order.driver_cost.cost': 0,
                        'order.driver_cost.reason': (
                            'cost_changed_by_antifraud'
                        ),
                        'order.antifraud_comment': 'full cancel',
                        'order.antifraud_old_cost': 120,
                        'order.cost_was_changed_by_antifraud': True,
                        'order_info.need_sync': True,
                    },
                    'inc': {'processing.version': 1, 'order.version': 1},
                },
                'user_id': 'aaa',
                'version': 'PROC_VERSION',
            },
        }
        assert request.json == requests[request.json['order_id']]
        return web.json_response(data=dict())

    @mock_order_core('/internal/processing/v1/event/restart-processing')
    def _order_core_restart_processing(req):
        assert 'due' not in req.query
        body = bson.BSON(req.get_data()).decode()
        assert body == {}
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=req.get_data(),
        )

    @mockserver.json_handler('/archive-api/archive/order')
    def _archive_order(request):
        responses = {
            '8c83b49edb274ce0992f337061047375': {
                'cost': 0.0,
                'driver_cost': {'cost': 0.0},
                'updated': datetime.datetime(2020, 2, 5, 16, 57, 0, 549000),
                'version': 3,
            },
        }
        order_doc = responses[request.json['id']]

        return web.Response(
            body=bson.BSON.encode({'doc': order_doc}),
            headers={'Content-Type': 'application/bson'},
        )

    @mockserver.json_handler('/archive-api/archive/order_proc/restore')
    def _archive_api_restore_order_proc(request):
        return [{'id': 'some_id', 'status': 'ok'}]

    @mockserver.json_handler('/archive-api/archive/orders/restore')
    def _archive_api_restore_order(request):
        return [{'id': 'some_id', 'status': 'ok'}]

    @mock_billing_orders('/v1/rebill_order')
    def _rebill_order(request):
        assert request.method == 'POST'
        requests = {
            '8c83b49edb274ce0992f337061047375': {
                'idempotency_token': (
                    'updated/2020-02-05T16:57:00.549000+00:00'
                ),
                'order': {
                    'alias_id': 'xxx',
                    'due': '2019-01-29T03:00:00+03:00',
                    'id': '8c83b49edb274ce0992f337061047375',
                    'version': 3,
                    'zone_name': 'msk',
                },
                'reason': {
                    'data': {
                        'ticket_id': 'TAXIFRAUD-1789',
                        'ticket_type': 'startrack',
                    },
                    'kind': 'cost_changed',
                },
            },
        }
        assert request.json == requests[request.json['order']['id']]
        return web.json_response(data=dict())

    return (
        _order_core_cancel_order,
        _order_core_set_order_fields,
        _order_core_restart_processing,
        _rebill_order,
    )


@pytest.mark.parametrize(
    (
        'order_id,order_core_set_fields_called,order_core_calcel_order_called,'
        'order_core_restart_processing_called, afs_cancel_order_response_code'
    ),
    [
        ('8c83b49edb274ce0992f337061047375', True, True, True, 200),
        ('unknown-order-id', False, False, False, 500),
        ('order-in-transporting-state', False, False, False, 200),
    ],
)
async def test_cancel_order(
        order_id,
        order_core_set_fields_called,
        order_core_calcel_order_called,
        order_core_restart_processing_called,
        afs_cancel_order_response_code,
        web_app_client,
        mockserver,
        mock_billing_orders,
        mock_order_core,
):
    (
        _order_core_cancel_order,
        _order_core_set_order_fields,
        _order_core_restart_processing,
        _rebill_order,
    ) = setup_mocks(mockserver, mock_billing_orders, mock_order_core)

    response = await web_app_client.post(
        '/v1/order/cancel', params={'order_id': order_id},
    )

    assert response.status == afs_cancel_order_response_code
    assert order_core_set_fields_called == (
        _order_core_set_order_fields.times_called != 0
    )
    assert order_core_calcel_order_called == (
        _order_core_cancel_order.times_called != 0
    )
    assert order_core_restart_processing_called == (
        _order_core_restart_processing.times_called != 0
    )
    assert _rebill_order.times_called == 0
