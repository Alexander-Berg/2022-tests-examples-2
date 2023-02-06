import datetime

import aiohttp.web
import pytest

from taxi.util import dates

PREFIX = 'payments_eda.retrieve_order'


# pylint: disable=C0103
pytestmark = [
    pytest.mark.config(LOCALES_SUPPORTED=['en']),
    pytest.mark.translations(
        client_messages={
            f'{PREFIX}.payment_status.paid': {'en': 'paid message'},
            f'{PREFIX}.payment_status.payment_failed': {
                'en': 'payment_failed message',
            },
            f'{PREFIX}.errors.payment_not_found.message': {
                'en': 'not found message',
            },
            f'{PREFIX}.errors.pending_timeout.message': {
                'en': 'pending timeout',
            },
            f'{PREFIX}.payment_status.pending': {'en': 'pending message'},
        },
    ),
]


async def _send_and_check(
        web_app_client,
        build_pa_headers,
        http_status,
        response_status,
        response_message,
        yandex_uid='yandex_uid',
        service='restaurants',
        external_ref='order_id',
):
    resp = await web_app_client.post(
        '/4.0/payments/v1/orders/retrieve',
        params={
            'service': service,
            'hmac': 'hmac',
            'external_ref': external_ref,
        },
        headers=build_pa_headers(
            '1.1.1.1',
            'en-EN',
            yandex_uid=yandex_uid,
            bound_uids='',
            user_agent=None,
        ),
    )
    assert resp.status == http_status
    if http_status == 200:
        assert await resp.json() == {
            'status': response_status,
            'message': response_message,
        }
        assert resp.headers.get('X-Polling-Delay') == '2'
    elif http_status == 404:
        data = await resp.json()
        assert data['code'] == 'payment_not_found'
    elif http_status == 410:
        data = await resp.json()
        assert data['code'] == 'pending_timeout'


async def _check_order_retrieve(
        web_app_client,
        mockserver,
        build_pa_headers,
        iiko_int_status,
        http_status,
        response_status,
        response_message,
        request_uid='yandex_uid',
        order_uid='yandex_uid',
        service='restaurants',
        external_ref='order_id',
        status_updated_at=datetime.datetime.now().isoformat(),
):
    @mockserver.json_handler('/iiko-integration/v1/order')
    def _iiko_order_mock(req):
        return {
            'order_id': '123',
            'restaurant_order_id': 'restaurant_order_id',
            'amount': '123.43',
            'discount': '0.00',
            'amount_without_discount': '123.43',
            'currency': 'RUB',
            'status': {
                'invoice_status': iiko_int_status,
                'restaurant_status': 'PENDING',
                'updated_at': status_updated_at,
            },
            'cashback': {'rate': '2', 'value': 'cashback_value'},
            'restaurant_info': {
                'name': 'name',
                'region_id': 1,
                'country_code': 'country_code',
                'geopoint': {'lat': 30.313119, 'lon': 59.931513},
                'eda_client_id': 42,
            },
            'items': [],
            'yandex_uid': order_uid,
        }

    await _send_and_check(
        web_app_client,
        build_pa_headers,
        http_status,
        response_status,
        response_message,
        yandex_uid=request_uid,
        service=service,
        external_ref=external_ref,
    )


async def _check_order_retrieve_fallback(
        web_app_client,
        mockserver,
        build_pa_headers,
        invoice_status,
        http_status,
        response_status,
        response_message,
        yandex_uid='yandex_uid',
        service='restaurants',
        external_ref='order_id',
):
    @mockserver.json_handler('/transactions-eda/invoice/retrieve')
    def _mock_invoice_retrieve(request):
        if external_ref != 'order_id':
            return aiohttp.web.Response(status=404)
        return {
            'cleared': {},
            'currency': 'RUB',
            'debt': {},
            'held': {},
            'id': 'order_id',
            'service': 'restaurants',
            'invoice_due': '2018-07-20T14:00:00.0000+0000',
            'operation_info': {
                'originator': 'processing',
                'priority': 1,
                'version': 1,
            },
            'payment_type': 'card',
            'status': invoice_status,
            'sum_to_pay': {'food': 123},
            'yandex_uid': 'yandex_uid',
        }

    await _send_and_check(
        web_app_client,
        build_pa_headers,
        http_status,
        response_status,
        response_message,
        yandex_uid=yandex_uid,
        service=service,
        external_ref=external_ref,
    )


@pytest.mark.parametrize(
    ['iiko_int_status', 'http_status', 'response_status', 'response_message'],
    [
        pytest.param(
            'INIT',
            404,
            None,
            'not found message',
            id='order_with_pending_status',
        ),
        pytest.param(
            'HOLDING',
            200,
            'pending',
            'pending message',
            id='order_with_holding_status',
        ),
        pytest.param(
            'HELD', 200, 'paid', 'paid message', id='order_with_held_status',
        ),
        pytest.param(
            'CLEARING',
            200,
            'paid',
            'paid message',
            id='order_with_clearing_status',
        ),
        pytest.param(
            'CLEARED',
            200,
            'paid',
            'paid message',
            id='order_with_cleared_status',
        ),
        pytest.param(
            'CLEAR_FAILED',
            200,
            'paid',
            'paid message',
            id='order_with_clear_failed_status',
        ),
        pytest.param(
            'REFUNDING',
            200,
            'paid',
            'paid message',
            id='order_with_refunding_status',
        ),
        pytest.param(
            'HOLD_FAILED',
            200,
            'payment_failed',
            'payment_failed message',
            id='order_with_hold_failed_status',
        ),
    ],
)
async def test_order_retrieve_different_statuses(
        web_app_client,
        mockserver,
        build_pa_headers,
        iiko_int_status,
        http_status,
        response_status,
        response_message,
):
    await _check_order_retrieve(
        web_app_client,
        mockserver,
        build_pa_headers,
        iiko_int_status,
        http_status,
        response_status,
        response_message,
    )


@pytest.mark.parametrize(
    ['invoice_status', 'http_status', 'response_status', 'response_message'],
    [
        pytest.param(
            'init',
            200,
            'pending',
            'pending message',
            id='invoice_with_init_status',
        ),
        pytest.param(
            'holding',
            200,
            'pending',
            'pending message',
            id='invoice_with_holding_status',
        ),
        pytest.param(
            'held', 200, 'paid', 'paid message', id='invoice_with_held_status',
        ),
        pytest.param(
            'clearing',
            200,
            'paid',
            'paid message',
            id='invoice_with_clearing_status',
        ),
        pytest.param(
            'cleared',
            200,
            'paid',
            'paid message',
            id='invoice_with_cleared_status',
        ),
        pytest.param(
            'clear-failed',
            200,
            'paid',
            'paid message',
            id='invoice_with_clear_failed_status',
        ),
        pytest.param(
            'hold-failed',
            200,
            'payment_failed',
            'payment_failed message',
            id='invoice_with_hold_failed_status',
        ),
        pytest.param(
            'refunding', 404, None, None, id='invoice_with_unknown_status',
        ),
    ],
)
@pytest.mark.config(PAYMENTS_EDA_RESTAURANT_STATUS_FALLBACK_ENABLED=True)
async def test_order_retrieve_different_statuses_fallback(
        web_app_client,
        mockserver,
        build_pa_headers,
        invoice_status,
        http_status,
        response_status,
        response_message,
):
    await _check_order_retrieve_fallback(
        web_app_client,
        mockserver,
        build_pa_headers,
        invoice_status,
        http_status,
        response_status,
        response_message,
    )


@pytest.mark.config(PAYMENTS_EDA_RESTAURANT_STATUS_FALLBACK_ENABLED=True)
@pytest.mark.parametrize(
    ['service', 'yandex_uid', 'order_id', 'http_status'],
    [
        pytest.param(
            'eats', 'yandex_uid', 'order_id', 400, id='wrong_service',
        ),
        pytest.param(
            'restaurants', 'wrong_uuid', 'order_id', 404, id='wrong_user',
        ),
        pytest.param(
            'restaurants',
            'yandex_uid',
            'wrong_order_id',
            404,
            id='wrong_order',
        ),
    ],
)
async def test_order_retrieve_failed_fallback(
        web_app_client,
        mockserver,
        build_pa_headers,
        service,
        yandex_uid,
        order_id,
        http_status,
):
    await _check_order_retrieve_fallback(
        web_app_client,
        mockserver,
        build_pa_headers,
        invoice_status='cleared',
        http_status=http_status,
        response_status=None,
        response_message=None,
        service=service,
        yandex_uid=yandex_uid,
        external_ref=order_id,
    )


@pytest.mark.parametrize(
    ('order_uid', 'expected_status'),
    (
        pytest.param('yandex_uid', 200, id='check_passed'),
        pytest.param('bad_uid', 404, id='check_failed'),
        pytest.param(None, 404, id='order_without_uid_error'),
    ),
)
async def test_uid_check(
        web_app_client,
        mockserver,
        build_pa_headers,
        order_uid,
        expected_status,
):
    await _check_order_retrieve(
        web_app_client=web_app_client,
        mockserver=mockserver,
        build_pa_headers=build_pa_headers,
        iiko_int_status='HOLDING',
        http_status=expected_status,
        response_status='pending',
        response_message='pending message',
        order_uid=order_uid,
    )


@pytest.mark.now('2020-07-28T15:41:52.501702+00:00')
@pytest.mark.config(QR_PAY_PENDING_TIMEOUT_SECONDS=5)
@pytest.mark.parametrize(
    ('status_age', 'expected_status'),
    (pytest.param(3, 200, id='ok'), pytest.param(8, 410, id='timeout')),
)
async def test_pending_timeout(
        web_app_client,
        mockserver,
        build_pa_headers,
        status_age,
        expected_status,
):
    status_updated_at = dates.utcnow() - datetime.timedelta(seconds=status_age)
    status_updated_at = status_updated_at.replace(
        tzinfo=datetime.timezone.utc,
    ).isoformat()
    await _check_order_retrieve(
        web_app_client=web_app_client,
        mockserver=mockserver,
        build_pa_headers=build_pa_headers,
        iiko_int_status='HOLDING',
        http_status=expected_status,
        response_status='pending',
        response_message='pending message',
        order_uid='yandex_uid',
        status_updated_at=status_updated_at,
    )
