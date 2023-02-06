import datetime

from aiohttp import web
import bson
import pytest

from taxi_antifraud.crontasks import return_commission
from taxi_antifraud.generated.cron import run_cron
from test_taxi_antifraud.cron.utils import data as data_module
from test_taxi_antifraud.cron.utils import state

CURSOR_STATE_NAME = return_commission.CURSOR_STATE_NAME

YT_DIRECTORY_PATH = '//home/taxi-fraud/unittests/kopatel'
YT_TABLE_PATH = YT_DIRECTORY_PATH + '/collusion'


@pytest.mark.config(
    AFS_CRON_RETURN_COMMISSION_ENABLED=True,
    AFS_CRON_RETURN_COMMISSION_INPUT_COLLUSION_TABLE_SUFFIX='kopatel/collusion',  # noqa: E501 pylint: disable=line-too-long
    AFS_CRON_RETURN_COMMISSION_SLEEP_TIME_SECONDS=0.01,
    AFS_CRON_CURSOR_USE_PGSQL='enabled',
)
@pytest.mark.now('2020-08-19T21:33:44')
async def test_cron(
        mock_order_core,
        mock_billing_orders,
        mockserver,
        yt_apply,
        yt_client,
        cron_context,
        db,
        patch,
):
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

    @mock_order_core('/v1/tc/order-fields')
    def _order_core_get(request):
        assert request.method == 'POST'
        responses = {
            '8c83b49edb274ce0992f337061047375': dict(
                order_id='8c83b49edb274ce0992f337061047375',
                fields={
                    'order': {
                        'cost': 123,
                        'driver_cost': {'cost': 120},
                        'nz': 'msk',
                        'user_id': 'aaa',
                        'request': {'due': '2019-01-29T00:00:00+00:00'},
                        'version': 2,
                    },
                    'payment_tech': {'type': 'card'},
                    'performer': {'alias_id': 'xxx'},
                    'updated': '2019-01-29T00:00:00+00:00',
                },
                version='PROC_VERSION',
                replica='secondary',
            ),
            'd41d8cd98f004204a9800998ecf84eee': dict(
                order_id='d41d8cd98f004204a9800998ecf84eee',
                fields={
                    'order': {
                        'cost': 234,
                        'driver_cost': {'cost': 237},
                        'nz': 'spb',
                        'user_id': 'bbb',
                        'request': {'due': '2019-04-18T00:00:00+00:00'},
                        'version': 4,
                    },
                    'payment_tech': {'type': 'card'},
                    'performer': {'alias_id': 'yyy'},
                    'updated': '2019-05-11T00:00:00+00:00',
                },
                version='PROC_VERSION2',
                replica='secondary',
            ),
            'too_old': dict(
                order_id='too_old',
                fields={
                    'order': {
                        'cost': 456,
                        'driver_cost': {'cost': 476},
                        'nz': 'ekb',
                        'user_id': 'ccc',
                        'request': {'due': '2019-06-04T00:00:00+00:00'},
                        'version': 6,
                    },
                    'payment_tech': {'type': 'card'},
                    'performer': {'alias_id': 'zzz'},
                    'updated': '2019-06-05T00:00:00+00:00',
                },
                version='PROC_VERSION2',
                replica='secondary',
            ),
            'corp_order': dict(
                order_id='corp_order',
                fields={
                    'order': {
                        'cost': 456,
                        'driver_cost': {'cost': 476},
                        'nz': 'ekb',
                        'user_id': 'ccc',
                        'request': {'due': '2019-06-04T00:00:00+00:00'},
                        'version': 6,
                    },
                    'payment_tech': {'type': 'corp'},
                    'performer': {'alias_id': 'zzz'},
                    'updated': '2019-06-05T00:00:00+00:00',
                },
                version='PROC_VERSION2',
                replica='secondary',
            ),
            'costs_already_equal_planned': dict(
                order_id='costs_already_equal_planned',
                fields={
                    'order': {
                        'cost': 777,
                        'driver_cost': {'cost': 789},
                        'nz': 'kaz',
                        'user_id': 'bbb',
                        'request': {'due': '2019-04-26T00:00:00+00:00'},
                        'version': 4,
                    },
                    'payment_tech': {'type': 'card'},
                    'performer': {'alias_id': 'www'},
                    'updated': '2019-05-11T00:00:00+00:00',
                },
                version='PROC_VERSION2',
                replica='secondary',
            ),
        }
        return web.json_response(data=responses[request.json['order_id']])

    @mock_order_core('/v1/tc/set-order-fields')
    def _order_core_set(request):
        assert request.method == 'POST'
        requests = {
            '8c83b49edb274ce0992f337061047375': {
                'call_processing': False,
                'order_id': '8c83b49edb274ce0992f337061047375',
                'update': {
                    'set': {
                        'order.cost': 1234.0,
                        'order.driver_cost.calc_method': 'other',
                        'order.driver_cost.cost': 1234,
                        'order.driver_cost.reason': (
                            'cost_changed_by_antifraud'
                        ),
                        'order.antifraud_comment': 'collusion',
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

    @mockserver.json_handler('/archive-api/archive/order')
    def _order(request):
        responses = {
            '8c83b49edb274ce0992f337061047375': {
                'cost': 1234.0,
                'driver_cost': {'cost': 1234.0},
                'updated': datetime.datetime(2020, 2, 5, 16, 57, 0, 549000),
                'version': 3,
            },
            'd41d8cd98f004204a9800998ecf84eee': {
                'cost': 123.0,
                'driver_cost': {'cost': 120.0},
                'updated': datetime.datetime(2020, 2, 5, 16, 57, 0, 549000),
                'version': 2,
            },
            'too_old': {
                'cost': 2.0,
                'driver_cost': {'cost': 2.0},
                'updated': datetime.datetime(2020, 2, 5, 16, 57, 0, 549000),
                'version': 1,
            },
            'corp_order': {
                'cost': 2.0,
                'driver_cost': {'cost': 2.0},
                'updated': datetime.datetime(2020, 2, 5, 16, 57, 0, 549000),
                'version': 1,
            },
            'costs_already_equal_planned': {
                'cost': 777.0,
                'driver_cost': {'cost': 789.0},
                'updated': datetime.datetime(2020, 2, 5, 16, 57, 0, 549000),
                'version': 5,
            },
        }
        order_doc = responses[request.json['id']]

        return web.Response(
            body=bson.BSON.encode({'doc': order_doc}),
            headers={'Content-Type': 'application/bson'},
        )

    @mockserver.json_handler('/archive-api/archive/orders/restore')
    def _archive_api_restore_order(request):
        return [{'id': 'some_id', 'status': 'ok'}]

    @mockserver.json_handler('/archive-api/archive/order_proc/restore')
    def _archive_api_restore_order_proc(request):
        return [{'id': 'some_id', 'status': 'ok'}]

    @mock_billing_orders('/v1/rebill_order')
    def rebill_order(request):
        assert request.method == 'POST'

        if request.json['order']['id'] == 'too_old':
            return web.json_response(
                data=dict(
                    code='rebill_order_is_not_allowed',
                    message='rebill of old orders is not allowed',
                ),
                status=400,
            )

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
            'd41d8cd98f004204a9800998ecf84eee': {
                'idempotency_token': (
                    'updated/2020-02-05T16:57:00.549000+00:00'
                ),
                'order': {
                    'alias_id': 'yyy',
                    'due': '2019-04-18T03:00:00+03:00',
                    'id': 'd41d8cd98f004204a9800998ecf84eee',
                    'version': 2,
                    'zone_name': 'spb',
                },
                'reason': {
                    'data': {
                        'ticket_id': 'TAXIFRAUD-1789',
                        'ticket_type': 'startrack',
                    },
                    'kind': 'cost_changed',
                },
            },
            'costs_already_equal_planned': {
                'idempotency_token': (
                    'updated/2020-02-05T16:57:00.549000+00:00'
                ),
                'order': {
                    'alias_id': 'www',
                    'due': '2019-04-26T03:00:00+03:00',
                    'id': 'costs_already_equal_planned',
                    'version': 5,
                    'zone_name': 'kaz',
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

    data = [
        {'order_id': '8c83b49edb274ce0992f337061047375', 'plan_cost': 1234},
        {'order_id': 'd41d8cd98f004204a9800998ecf84eee', 'plan_cost': 56},
        {'order_id': 'too_old', 'plan_cost': 1},
        {'order_id': 'corp_order', 'plan_cost': 1234},
        {'order_id': 'costs_already_equal_planned', 'plan_cost': 789},
    ]

    master_pool = cron_context.pg.master_pool
    await data_module.prepare_data(
        data,
        yt_client,
        master_pool,
        CURSOR_STATE_NAME,
        YT_DIRECTORY_PATH,
        YT_TABLE_PATH,
    )

    await run_cron.main(
        ['taxi_antifraud.crontasks.return_commission', '-t', '0'],
    )

    assert await state.get_all_cron_state(master_pool) == {
        CURSOR_STATE_NAME: str(len(data)),
    }

    assert _order_core_set.times_called == 1
    assert _order_core_restart_processing.times_called == 1
    assert rebill_order.times_called == 2
