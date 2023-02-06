import datetime

from aiohttp import web
import bson
import pytest
import yt.wrapper as ytw

from taxi_antifraud.crontasks import cancel_order
from taxi_antifraud.generated.cron import run_cron
from test_taxi_antifraud.cron.utils import state
import test_taxi_antifraud.test_cancel_order as tst

CURSOR_STATE_NAME = cancel_order.CURSOR_STATE_NAME

YT_TABLE_PATH = '//home/taxi-fraud/unittests/kopatel/cancel_order'


@pytest.mark.config(
    AFS_CRON_CANCEL_ORDERS_ENABLED=True,
    AFS_CRON_CANCEL_ORDERS_INPUT_TABLE_SUFFIX='kopatel/cancel_order',
    AFS_CRON_CANCEL_ORDERS_SLEEP_TIME_SECONDS=0.01,
    AFS_CRON_CURSOR_USE_PGSQL='enabled',
)
async def test_cron(
        yt_client,
        db,
        mockserver,
        mock_billing_orders,
        mock_order_core,
        cron_context,
):
    (
        _order_core_cancel_order,
        _order_core_set_order_fields,
        _order_core_restart_processing,
        _rebill_order,
    ) = tst.setup_mocks(mockserver, mock_billing_orders, mock_order_core)

    data = [
        dict(order_id='8c83b49edb274ce0992f337061047375', cancel_type='full'),
    ]

    yt_client.create(
        'table', path=YT_TABLE_PATH, recursive=True, ignore_existing=True,
    )
    yt_client.write_table(YT_TABLE_PATH, data)
    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)

    await run_cron.main(['taxi_antifraud.crontasks.cancel_order', '-t', '0'])

    async def check():
        assert await state.get_all_cron_state(master_pool) == {
            CURSOR_STATE_NAME: str(len(data)),
        }

        assert _order_core_cancel_order.times_called == 1
        assert _order_core_set_order_fields.times_called == 1
        assert _order_core_restart_processing.times_called == 1
        assert _rebill_order.times_called == 0  # no excplicit rebill calls

    await check()

    bad_data = [dict(order_id='unknown-order-id', cancel_type='full')]
    yt_client.write_table(ytw.TablePath(YT_TABLE_PATH, append=True), bad_data)

    with pytest.raises(Exception):
        await run_cron.main(
            ['taxi_antifraud.crontasks.cancel_order', '-t', '0'],
        )

    # check no changes
    await check()


@pytest.mark.config(
    AFS_CRON_CANCEL_ORDERS_ENABLED=True,
    AFS_CRON_CANCEL_ORDERS_INPUT_TABLE_SUFFIX='kopatel/cancel_order',
    AFS_CRON_CANCEL_ORDERS_SLEEP_TIME_SECONDS=0.01,
    AFS_CRON_CURSOR_USE_PGSQL='enabled',
)
async def test_reset_cost_to_zero(
        yt_client,
        mockserver,
        mock_billing_orders,
        mock_order_core,
        cron_context,
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
    def _order_core_order_fields(request):
        assert request.method == 'POST'
        response = dict(
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
        )
        return web.json_response(status=200, data=response)

    @mock_order_core('/v1/tc/set-order-fields')
    def _order_core_set_order_fields(request):
        assert request.method == 'POST'
        return web.json_response(data=dict())

    @mockserver.json_handler('/archive-api/archive/order')
    def _archive_order(request):
        order_doc = {
            'cost': 0.0,
            'driver_cost': {'cost': 0.0},
            'updated': datetime.datetime(2020, 2, 5, 16, 57, 0, 549000),
            'version': 3,
        }

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
    def _rebill_order(request):
        assert request.method == 'POST'
        return web.json_response(data=dict())

    data = [
        dict(
            order_id='8c83b49edb274ce0992f337061047375',
            cancel_type='reset_cost_to_zero',
        ),
    ]

    yt_client.create(
        'table', path=YT_TABLE_PATH, recursive=True, ignore_existing=True,
    )
    yt_client.write_table(YT_TABLE_PATH, data)
    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)

    await run_cron.main(['taxi_antifraud.crontasks.cancel_order', '-t', '0'])

    assert await state.get_all_cron_state(master_pool) == {
        CURSOR_STATE_NAME: str(len(data)),
    }

    assert _order_core_set_order_fields.times_called == 1
    assert _order_core_restart_processing.times_called == 1
    assert _rebill_order.times_called == 1
