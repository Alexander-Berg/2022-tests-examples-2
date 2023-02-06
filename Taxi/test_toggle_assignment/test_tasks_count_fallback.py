import datetime
import json

import pytest

from tests_dispatch_buffer import utils
from tests_dispatch_buffer.test_toggle_assignment import data


@pytest.mark.parametrize('dispatch_status', ['idle', 'dispatched'])
async def test_tasks_count_fallback(
        taxi_dispatch_buffer, pgsql, mockserver, statistics, dispatch_status,
):
    @mockserver.json_handler('/candidates/order-search')
    def _mock_order_search(request):
        assert request.headers.get('Content-Type') == 'application/json'
        return {'candidates': []}

    utils.insert_order(
        pgsql,
        service='taxi',
        user_id='user_id',
        order_id='8fa174f64a0b4d8488395bc9f652addd',
        agglomeration='example_agglomeration',
        zone_id='example',
        classes='{"econom"}',
        created=datetime.datetime.now(),
        dispatch_status=dispatch_status,
        order_meta=json.dumps(data.ORDER_META),
    )

    async with statistics.capture(taxi_dispatch_buffer) as capture:
        await taxi_dispatch_buffer.run_task('distlock/buffer_assignment')

    assert (
        capture.statistics[
            ('dispatch-buffer.tasks_count.' 'example_agglomeration.started')
        ]
        == 1
    )
    if dispatch_status == 'dispatched':
        assert (
            capture.statistics[
                (
                    'dispatch-buffer.tasks_count.'
                    'example_agglomeration.no_orders'
                )
            ]
            == 1
        )
    else:
        assert (
            capture.statistics[
                'dispatch-buffer.tasks_count.example_agglomeration.success'
            ]
            == 1
        )


async def test_tasks_count_fallback_error(
        taxi_dispatch_buffer, pgsql, mockserver, statistics,
):
    @mockserver.json_handler('/candidates/order-search')
    def _mock_order_search(request):
        assert request.headers.get('Content-Type') == 'application/json'
        return {'candidates': []}

    cursor = pgsql['driver_dispatcher'].cursor()
    cursor.execute(
        f"""
        CREATE OR REPLACE FUNCTION raise_exception()
        RETURNS TRIGGER AS $$
        BEGIN
            RAISE EXCEPTION 'Simple-dimple exception';
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER raise_exception_trigger
        BEFORE UPDATE ON dispatch_buffer.dispatch_meta
        EXECUTE PROCEDURE raise_exception();
    """,
    )

    utils.insert_order(
        pgsql,
        service='taxi',
        user_id='user_id',
        order_id='8fa174f64a0b4d8488395bc9f652addd',
        agglomeration='example_agglomeration',
        zone_id='example',
        classes='{"econom"}',
        created=datetime.datetime.now(),
        dispatch_status='idle',
        order_meta=json.dumps(data.ORDER_META),
    )

    async with statistics.capture(taxi_dispatch_buffer) as capture:
        try:
            await taxi_dispatch_buffer.run_task('distlock/buffer_assignment')
        except BaseException:
            pass

    cursor.execute(
        f"""
        DROP TRIGGER raise_exception_trigger ON dispatch_buffer.dispatch_meta;
    """,
    )

    assert (
        capture.statistics[
            'dispatch-buffer.tasks_count.example_agglomeration.error'
        ]
        == 1
    )
