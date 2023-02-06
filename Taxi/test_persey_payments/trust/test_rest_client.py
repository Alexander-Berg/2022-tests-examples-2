# pylint: disable=no-self-use
import pytest

from taxi.clients import http_client

from persey_payments.trust import rest_client


class DummyTvm:
    async def get_auth_headers(self, service_name, *, log_extra):
        return {}


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
        'food_payment.methods.check-refund.error',
        'food_payment.methods.check-refund.limited',
        'food_payment.methods.check-refund.success',
        'food_payment.methods.check-refund',
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
        'food_payment.methods.create-web-basket',
        'food_payment.methods.create-web-basket.error',
        'food_payment.methods.create-web-basket.limited',
        'food_payment.methods.create-web-basket.success',
        'food_payment.methods.deliver-basket',
        'food_payment.methods.deliver-basket.error',
        'food_payment.methods.deliver-basket.limited',
        'food_payment.methods.deliver-basket.success',
        'food_payment.methods.clear-order',
        'food_payment.methods.clear-order.error',
        'food_payment.methods.clear-order.limited',
        'food_payment.methods.clear-order.success',
        'food_payment.methods.cancel-order',
        'food_payment.methods.cancel-order.error',
        'food_payment.methods.cancel-order.limited',
        'food_payment.methods.cancel-order.success',
        'food_payment.methods.create-subscription',
        'food_payment.methods.create-subscription.error',
        'food_payment.methods.create-subscription.limited',
        'food_payment.methods.create-subscription.success',
        'food_payment.methods.check-subscription',
        'food_payment.methods.check-subscription.error',
        'food_payment.methods.check-subscription.limited',
        'food_payment.methods.check-subscription.success',
        'food_payment.methods.cancel-subscription',
        'food_payment.methods.cancel-subscription.error',
        'food_payment.methods.cancel-subscription.limited',
        'food_payment.methods.cancel-subscription.success',
        'food_payment.methods.get-payment-methods',
        'food_payment.methods.get-payment-methods.error',
        'food_payment.methods.get-payment-methods.limited',
        'food_payment.methods.get-payment-methods.success',
        'food_payment.methods.change-subs-payment-method',
        'food_payment.methods.change-subs-payment-method.error',
        'food_payment.methods.change-subs-payment-method.limited',
        'food_payment.methods.change-subs-payment-method.success',
    }

    # pylint: disable=protected-access
    assert set(rest_client._all_metric_names('food_payment')) == expected


@pytest.mark.nofilldb
async def test_create_order_basic(mockserver):
    class Ratelimiter:
        def ratelimit(self, name):
            return True

    @mockserver.json_handler('/trust/orders/')
    async def trust_orders_handler(request):
        return {
            'order_id': 'new-order',
            'status_code': 'created',
            'status': 'success',
        }

    metrics = DummyMetrics()
    client = rest_client.TrustClient(
        base_url=mockserver.url('trust/'),
        http_session=http_client.HTTPClient(),
        billing_service_id='testsuite',
        tvm_client=DummyTvm(),
        metrics_=metrics,
        ratelimiter=Ratelimiter(),
        service_token='token',
    )

    await client.create_order(
        yandex_uid='123', product_id='product_1', log_extra=None,
    )

    assert trust_orders_handler.times_called == 1
    assert metrics.events == [
        'testsuite.methods.create-order',
        'testsuite.methods.create-order.success',
    ]
