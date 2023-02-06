import datetime

from aiohttp import web
import pytest

from taxi.util import dates as date_utils

from test_payments_eda import consts

DATE_TIME = datetime.datetime(2019, 6, 4, 3, 11, 22)


@pytest.mark.now(DATE_TIME.isoformat())
async def test_basic(web_app_client, mockserver, mock_uuid):
    def validate_update_request(request, v2_update):
        body = request.json

        items_field = 'items_by_payment_type' if v2_update else 'items'
        assert body == {
            'id': 'my-order',
            'originator': 'processing',
            'operation_id': 'cancel:foobar',
            items_field: [],
        }

    @mockserver.json_handler('/transactions-eda/v2/invoice/update')
    def v2_update_handler(request):
        validate_update_request(request, v2_update=True)
        return {}

    @mockserver.json_handler('/transactions-eda/invoice/clear')
    def clear_handler(request):
        assert request.json == {
            'id': 'my-order',
            'clear_eta': date_utils.localize(DATE_TIME).isoformat(),
        }
        return {}

    mock_uuid('foobar')

    response = await web_app_client.post(
        '/v1/orders/cancel', params={'order_id': 'my-order'}, json={},
    )

    assert response.status == 200
    assert v2_update_handler.times_called == 1
    assert clear_handler.times_called == 1


@pytest.mark.parametrize('http_code', [404, 409])
async def test_http_errors(web_app_client, mockserver, http_code):
    bad_response = web.Response(
        status=http_code, body='{"code": "error", "message": "error"}',
    )

    @mockserver.json_handler('/transactions-eda/v2/invoice/update')
    def v2_update_handler(request):
        return bad_response

    response = await web_app_client.post(
        '/v1/orders/cancel', params={'order_id': 'my-order'}, json={},
    )

    assert response.status == http_code
    assert v2_update_handler.times_called == 1


async def test_cancel_from_israel(web_app_client, mockserver, mock_uuid):
    @mockserver.json_handler('/transactions-lavka-isr/v2/invoice/update')
    def v2_update_handler(request):
        return {}

    @mockserver.json_handler('/transactions-lavka-isr/invoice/clear')
    def clear_handler(request):
        return {}

    mock_uuid('foobar')

    response = await web_app_client.post(
        '/v1/orders/cancel',
        params={'order_id': consts.GROCERY_ORDER_ID},
        json={'country_iso2': 'IL'},
    )

    assert response.status == 200
    assert v2_update_handler.times_called == 1
    assert clear_handler.times_called == 1
