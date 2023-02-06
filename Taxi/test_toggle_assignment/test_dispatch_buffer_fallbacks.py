import datetime
import json

import pytest

from tests_dispatch_buffer import utils
from tests_dispatch_buffer.test_toggle_assignment import data


def serialize_callback_to_pg(callback: dict) -> str:
    return (
        f'(\'{callback["url"]}\','
        f'\'{callback["timeout_ms"]} milliseconds\'::interval,'
        f'{callback["attempts"]})'
    )


@pytest.mark.parametrize(
    'handler_name,response_json,response_code,metric_name,metric_counter',
    [
        (
            '/candidates/order-search',
            {},
            500,
            'dispatch-buffer.candidates./order-search.error',
            1,
        ),
        (
            '/lookup/event',
            {'success': False},
            200,
            'dispatch-buffer.lookup./event.error',
            1,
        ),
        (
            '/lookup/event',
            {'success': True},
            200,
            'dispatch-buffer.lookup./event.ok',
            1,
        ),
    ],
)
async def test_external_requests_metrics(
        taxi_dispatch_buffer,
        pgsql,
        mockserver,
        load_json,
        statistics,
        handler_name,
        response_json,
        response_code,
        metric_name,
        metric_counter,
):
    @mockserver.json_handler('/candidates/order-search')
    def _mock_order_search(request):
        assert request.headers.get('Content-Type') == 'application/json'
        return {'candidates': [data.CANDIDATE]}

    @mockserver.json_handler('/driver_scoring/v2/score-candidates-bulk')
    def _mock_driver_scoring_bulk(request):
        return {'responses': [data.SCORING_RESPONSE]}

    @mockserver.json_handler(handler_name)
    def _mock_handler(request):
        return mockserver.make_response(
            json=response_json, status=response_code,
        )

    callback = {
        'url': mockserver.url(
            '/lookup/event?order_id=a0b4d8488395bc9f652addd&version=1',
        ),
        'timeout_ms': 200,
        'attempts': 2,
    }

    utils.insert_order(
        pgsql,
        service='taxi',
        user_id='user_id',
        order_id='a0b4d8488395bc9f652addd',
        zone_id='example',
        classes='{"econom"}',
        agglomeration='example_agglomeration',
        created=datetime.datetime.now(),
        dispatch_status='idle',
        callback=serialize_callback_to_pg(callback),
        order_meta=json.dumps(data.ORDER_META),
    )

    async with statistics.capture(taxi_dispatch_buffer) as capture:
        await taxi_dispatch_buffer.run_task('distlock/buffer_assignment')

    assert capture.statistics[metric_name] == metric_counter


async def test_error_by_duplication_order_id_metrics(
        taxi_dispatch_buffer, pgsql, statistics, load_json,
):
    utils.insert_order(
        pgsql,
        service='taxi',
        user_id='user_id',
        order_id='8fa174f64a0b4d8488395bc9f652addd',
        zone_id='example',
        classes='{"econom"}',
        created=datetime.datetime.now(),
        dispatch_status='dispatched',
        order_meta='{}',
    )
    order_meta = load_json('performer_order_meta.json')
    async with statistics.capture(taxi_dispatch_buffer) as capture:
        response = await taxi_dispatch_buffer.post(
            'performer-for-order', json=order_meta,
        )
    assert response.status_code == 500
    assert capture.statistics['dispatch-buffer.create.sql.query.error'] == 1


async def test_pgsql_statement_error_metrics(
        taxi_dispatch_buffer, pgsql, statistics, load_json, mockserver,
):
    @mockserver.json_handler('/candidates/order-search')
    def _mock_order_search(request):
        return {'candidates': [data.CANDIDATE]}

    @mockserver.json_handler('/driver_scoring/v2/score-candidates-bulk')
    def _mock_driver_scoring_bulk(request):
        return {'responses': [data.SCORING_RESPONSE]}

    utils.insert_order(
        pgsql,
        service='taxi',
        user_id='user_id',
        order_id='8fa174f64a0b4d8488395bc9f652addd',
        zone_id='example',
        classes='{"econom"}',
        agglomeration='example_agglomeration',
        created=datetime.datetime.now(),
        dispatch_status='idle',
        order_meta=json.dumps(data.ORDER_META),
    )

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
            'dispatch-buffer.update_orders_with_dispatched_drivers.'
            'sql.query.error'
        ]
        == 1
    )
