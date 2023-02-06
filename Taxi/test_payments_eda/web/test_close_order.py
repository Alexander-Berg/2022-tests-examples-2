import datetime

from aiohttp import web
import pytest

from taxi.util import dates as date_utils

from test_payments_eda import consts

DATE_TIME = datetime.datetime(2019, 6, 4, 3, 11, 22)


async def test_not_found(web_app_client, mockserver):
    @mockserver.json_handler('/transactions-eda/invoice/clear')
    def _invoice_clear(request):
        return web.Response(
            status=404, body='{"code": "error", "message": "error"}',
        )

    response = await web_app_client.post(
        '/v1/orders/close', params={'order_id': 'not-found'}, json={},
    )
    assert response.status == 404


@pytest.mark.now(DATE_TIME.isoformat())
async def test_basic(web_app_client, mockserver):
    @mockserver.json_handler('/transactions-eda/invoice/clear')
    def invoice_clear(request):
        assert request.json == {
            'id': 'my-order',
            'clear_eta': date_utils.localize(DATE_TIME).isoformat(),
        }
        return {}

    response = await web_app_client.post(
        '/v1/orders/close', params={'order_id': 'my-order'}, json={},
    )
    assert response.status == 200

    assert invoice_clear.times_called == 1


@pytest.mark.parametrize('from_russia', [True, False])
async def test_close_grocery_order(web_app_client, mockserver, from_russia):
    @mockserver.json_handler('/transactions-lavka-isr/invoice/clear')
    def invoice_clear_isr(request):
        return {}

    @mockserver.json_handler('/transactions-eda/invoice/clear')
    def invoice_clear_rus(request):
        return {}

    data = {}
    if not from_russia:
        data['country_iso2'] = 'IL'

    response = await web_app_client.post(
        '/v1/orders/close',
        params={'order_id': consts.GROCERY_ORDER_ID},
        json=data,
    )
    assert response.status == 200

    if from_russia:
        assert invoice_clear_rus.times_called == 1
    else:
        assert invoice_clear_isr.times_called == 1
