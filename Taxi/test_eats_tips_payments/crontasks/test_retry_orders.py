import datetime

from aiohttp import web
import pytest

from eats_tips_payments.generated.cron import run_cron


@pytest.mark.now('2022-02-17 22:00:00+03:00')
async def test_retry_orders(mock_best2pay, load, pgsql):
    @mock_best2pay('/webapi/Order')
    async def _mock_b2p_order(request):
        order_id = request.query['id']
        if order_id in ('101', '104'):
            return web.Response(
                status=200,
                content_type='text/html',
                body=load('b2p_order_response_complete.xml'),
            )
        if order_id in ('105',):
            return web.Response(
                status=200,
                content_type='text/html',
                body=load('b2p_order_response_authorize.xml'),
            )
        assert 0, f'unexpected order id: {order_id}'

    @mock_best2pay('/webapi/b2puser/Complete')
    async def _mock_b2p_complete(request):
        order_id = request.form['id']
        if order_id in ('105',):
            return web.Response(
                status=200,
                content_type='text/html',
                body=load('b2p_complete_response_error.xml'),
            )
        if order_id in ('106',):
            return web.Response(
                status=200,
                content_type='text/html',
                body=load('b2p_complete_response.xml'),
            )
        assert 0, f'unexpected order id: {order_id}'

    await run_cron.main(
        ['eats_tips_payments.crontasks.retry_orders', '-t', '0'],
    )

    with pgsql['eats_tips_payments'].dict_cursor() as cursor:
        cursor.execute('select * from eats_tips_payments.orders;')
        orders_by_id = {row['id']: row for row in cursor.fetchall()}
    # заказ уже имеет статус COMPLETED в B2P и проставился при повторной
    # попытке
    assert orders_by_id['order_id_1']['status'] == 'COMPLETED'
    assert orders_by_id['order_id_1']['status_b2p'] == 'COMPLETED'
    # заказ не был обработан, т.к. слишком свежий
    assert orders_by_id['order_id_2']['status'] == 'COMPLETE_FAILED'
    # заказ не был обработан, т.к. имеет статус AUTHORIZE_FAILED,
    # который не подлежит допроводке
    assert orders_by_id['order_id_3']['status'] == 'AUTHORIZE_FAILED'
    # complete завершился успешно при повторной попытке
    assert orders_by_id['order_id_4']['status'] == 'COMPLETED'
    # complete завершился ошибкой при повторной попытке
    assert orders_by_id['order_id_5']['status'] == 'COMPLETE_FAILED'
    # заказ не был обработан, т.к. слишком старый
    assert orders_by_id['order_id_6']['status'] == 'COMPLETE_FAILED'
    # заказ не был обработан, т.к. ещё не наступило время следующей попытки
    assert orders_by_id['order_id_7']['status'] == 'COMPLETE_FAILED'
    # заказ не был обработан, т.к. превышено число попыток
    assert orders_by_id['order_id_8']['status'] == 'COMPLETE_FAILED'

    with pgsql['eats_tips_payments'].dict_cursor() as cursor:
        cursor.execute('select * from eats_tips_payments.orders_retries;')
        orders_retries_by_id = {
            row['order_id']: row for row in cursor.fetchall()
        }
    assert orders_retries_by_id['order_id_1']['tries'] == 1
    assert orders_retries_by_id['order_id_1']['next_try'] == datetime.datetime(
        2022, 2, 17, 19, 20, tzinfo=datetime.timezone.utc,
    )
    assert orders_retries_by_id['order_id_4']['tries'] == 2
    assert orders_retries_by_id['order_id_4']['next_try'] == datetime.datetime(
        2022, 2, 17, 22, 20, tzinfo=datetime.timezone.utc,
    )
