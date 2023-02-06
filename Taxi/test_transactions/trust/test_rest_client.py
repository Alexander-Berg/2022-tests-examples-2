# pylint: disable=no-self-use
from typing import List

import pytest

from taxi.clients import http_client

from transactions.clients.trust import event_stats
from transactions.clients.trust import rest_client
from transactions.clients.trust import service_metrics as trust_service_metrics


class DummyTvm:
    async def get_auth_headers(self, service_name, *, log_extra):
        return {}


class DummyConfig:
    TRANSACTIONS_UPDATE_EVENT_STATS_FOR: List[str] = []
    TRANSACTIONS_UPDATE_SERVICE_STATS_FOR: List[str] = []
    TRANSACTIONS_TRUST_CLIENT_QOS = {
        '__default__': {'attempts': 2, 'timeout-ms': 5000},
    }
    TRANSACTIONS_BILLING_SERVICE_TOKENS = {
        'card': {
            'billing_api_key': 'taxifee_8c7078d6b3334e03c1b4005b02da30f4',
            'billing_payments_service_id': 124,
        },
        'uber': {
            'billing_api_key': 'ubertaxi_4ea0f5fc283dc942c27bc7ae022e8821',
            'billing_payments_service_id': 125,
        },
        'uber_roaming': {
            'billing_api_key': (
                'ubertaxi_roaming_8f0cbb8d35468f87bdae164f17e09011'
            ),
            'billing_payments_service_id': 605,
        },
        'food_payment': {
            'billing_api_key': 'food_payment_c808ddc93ffec050bf0624a4d3f3707c',
            'billing_payments_service_id': 629,
        },
    }


class DummyMetrics:
    def __init__(self):
        self.events = []

    def event(self, event):
        self.events.append(event)

    def add_series(self, metrics):
        pass


@pytest.mark.nofilldb
def test_metric_names():
    expected = {
        'food_payment.methods.cancel-basket.error',
        'food_payment.methods.cancel-basket.limited',
        'food_payment.methods.cancel-basket.success',
        'food_payment.methods.cancel-basket',
        'food_payment.methods.check-basket.error',
        'food_payment.methods.check-basket.limited',
        'food_payment.methods.check-basket.success',
        'food_payment.methods.check-basket',
        'food_payment.methods.check-basket-light.error',
        'food_payment.methods.check-basket-light.limited',
        'food_payment.methods.check-basket-light.success',
        'food_payment.methods.check-basket-light',
        'food_payment.methods.check-refund.error',
        'food_payment.methods.check-refund.limited',
        'food_payment.methods.check-refund.success',
        'food_payment.methods.check-refund',
        'food_payment.methods.check-topup.error',
        'food_payment.methods.check-topup.limited',
        'food_payment.methods.check-topup.success',
        'food_payment.methods.check-topup',
        'food_payment.methods.clear-basket.error',
        'food_payment.methods.clear-basket.limited',
        'food_payment.methods.clear-basket.success',
        'food_payment.methods.clear-basket',
        'food_payment.methods.create-basket.error',
        'food_payment.methods.create-basket.limited',
        'food_payment.methods.create-basket.success',
        'food_payment.methods.create-basket',
        'food_payment.methods.create-order.error',
        'food_payment.methods.create-order.limited',
        'food_payment.methods.create-order.success',
        'food_payment.methods.create-order',
        'food_payment.methods.create-product.error',
        'food_payment.methods.create-product.limited',
        'food_payment.methods.create-product.success',
        'food_payment.methods.create-product',
        'food_payment.methods.create-refund.error',
        'food_payment.methods.create-refund.limited',
        'food_payment.methods.create-refund.success',
        'food_payment.methods.create-refund',
        'food_payment.methods.create-topup.error',
        'food_payment.methods.create-topup.limited',
        'food_payment.methods.create-topup.success',
        'food_payment.methods.create-topup',
        'food_payment.methods.do-refund.error',
        'food_payment.methods.do-refund.limited',
        'food_payment.methods.do-refund.success',
        'food_payment.methods.do-refund',
        'food_payment.methods.pay-basket.error',
        'food_payment.methods.pay-basket.limited',
        'food_payment.methods.pay-basket.success',
        'food_payment.methods.pay-basket',
        'food_payment.methods.resize-basket.error',
        'food_payment.methods.resize-basket.limited',
        'food_payment.methods.resize-basket.success',
        'food_payment.methods.resize-basket',
        'food_payment.methods.start-topup.error',
        'food_payment.methods.start-topup.limited',
        'food_payment.methods.start-topup.success',
        'food_payment.methods.start-topup',
        'food_payment.transactions.antifraud',
        'food_payment.transactions.antifraud.allow',
        'food_payment.transactions.antifraud.block',
        'food_payment.transactions.antifraud-skipped',
        'food_payment.transactions.antifraud-skipped.service-unavailable',
        'food_payment.transactions.antifraud-skipped.disabled-by-config',
        'food_payment.transactions.hold-fail',
        'food_payment.transactions.success',
        'food_payment.methods.create-partner',
        'food_payment.methods.create-partner.error',
        'food_payment.methods.create-partner.limited',
        'food_payment.methods.create-partner.success',
        'food_payment.methods.get-product',
        'food_payment.methods.get-product.error',
        'food_payment.methods.get-product.limited',
        'food_payment.methods.get-product.success',
    }

    # pylint: disable=protected-access
    assert set(rest_client._all_metric_names('food_payment')) == expected


@pytest.mark.nofilldb
@pytest.mark.parametrize(
    'responses, expected_times_called, expected_events',
    [
        (
            [
                {
                    'status': 200,
                    'json': {
                        'order_id': 'new-order',
                        'status_code': 'created',
                        'status': 'success',
                    },
                },
            ],
            1,
            ['card.methods.create-order', 'card.methods.create-order.success'],
        ),
        (
            [
                {'status': 500, 'json': {}},
                {
                    'status': 200,
                    'json': {
                        'order_id': 'new-order',
                        'status_code': 'created',
                        'status': 'success',
                    },
                },
            ],
            2,
            [
                'card.methods.create-order',
                'card.methods.create-order',
                'card.methods.create-order.success',
            ],
        ),
    ],
)
async def test_create_order(
        mockserver, responses, expected_times_called, expected_events,
):
    class Ratelimiter:
        def ratelimit(self, name):
            return True

    @mockserver.json_handler('/trust/orders/')
    async def trust_orders_handler(request):
        response_params = responses.pop(0)
        return mockserver.make_response(**response_params)

    metrics = DummyMetrics()
    client = rest_client.TrustClient(
        base_url=mockserver.url('trust/'),
        http_session=http_client.HTTPClient(),
        billing_service_id='card',
        tvm_client=DummyTvm(),
        metrics_=metrics,
        event_stats_=event_stats.EventStats(None, DummyConfig(), None),
        ratelimiter=Ratelimiter(),
        config=DummyConfig(),
    )

    await client.create_order(
        yandex_uid='123',
        user_ip='127.0.0.1',
        product_id='product_1',
        order_id='new-order',
        log_extra=None,
    )

    assert trust_orders_handler.times_called == expected_times_called
    assert metrics.events == expected_events


@pytest.mark.nofilldb
@pytest.mark.parametrize(
    'limit_in_transactions, expected_message, expected_events',
    [
        (
            True,
            'Ratelimit of 10 RPS exceeded for method create-order of '
            'service card, metric key card.methods.create-order',
            ['card.methods.create-order.limited'],
        ),
        (
            # If Trust returns 429, we should raise the same error.
            # We _did_ make a request to Trust, so total requests metric is
            # incremented
            False,
            'Trust rate limit exceeded',
            ['card.methods.create-order', 'card.methods.create-order.limited'],
        ),
    ],
)
async def test_create_order_ratelimited(
        mockserver, limit_in_transactions, expected_message, expected_events,
):
    class Ratelimiter:
        def get_ratelimit_for(self, name):
            assert name == 'card.methods.create-order'
            return 10

        def ratelimit(self, name):
            if limit_in_transactions:
                return False
            return True

    @mockserver.json_handler('/trust/orders/')
    async def trust_orders_handler(request):
        assert not limit_in_transactions
        return mockserver.make_response(
            status=429,
            content_type='text/plain',
            response='too many requests',
        )

    metrics = DummyMetrics()
    client = rest_client.TrustClient(
        base_url=mockserver.url('trust/'),
        http_session=http_client.HTTPClient(),
        billing_service_id='card',
        tvm_client=DummyTvm(),
        metrics_=metrics,
        event_stats_=event_stats.EventStats(None, DummyConfig(), None),
        ratelimiter=Ratelimiter(),
        config=DummyConfig(),
    )

    with pytest.raises(rest_client.RateLimitExceededError) as exc:
        await client.create_order(
            yandex_uid='123',
            user_ip='127.0.0.1',
            product_id='product_1',
            order_id='new-order',
            log_extra=None,
        )
    assert str(exc.value) == expected_message
    assert metrics.events == expected_events
    if not limit_in_transactions:
        assert trust_orders_handler.times_called == 1


@pytest.mark.parametrize(
    'label, event, expected_calls',
    [
        (
            'cancel-basket',
            'success',
            [
                {
                    'billing_service_id': 'card',
                    'method': 'UpdateBasket',
                    'status': 'success',
                    'log_extra': None,
                },
            ],
        ),
        ('get-order', 'success', []),
        ('cancel-basket', None, []),
    ],
)
@pytest.mark.nofilldb
async def test_service_metrics_event_methods(
        patch, label, event, expected_calls,
):
    # pylint: disable=protected-access
    @patch('transactions.clients.trust.event_stats.EventStats.save_for')
    async def save_for(billing_service_id, method, status, log_extra):
        pass

    service_metrics = trust_service_metrics.ServiceMetrics(
        metrics_=DummyMetrics(),
        event_stats_=event_stats.EventStats(None, None, None),
        ratelimiter=None,
        service_name='card',
    )
    service_metrics._event_methods(label, event)
    assert save_for.calls == expected_calls
