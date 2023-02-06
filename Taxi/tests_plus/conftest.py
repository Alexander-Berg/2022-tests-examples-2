# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from plus_plugins import *  # noqa: F403 F401
import pytest

from tests_plus.utils import requests
from tests_plus.utils import responses


@pytest.fixture
def web_plus(taxi_plus):
    class Ctx:
        def __init__(self, taxi_plus):
            self.subscription_info = requests.SubscriptionInfoRequest(
                taxi_plus,
            )
            self.subscription_info_v2 = requests.SubscriptionInfoRequestV2(
                taxi_plus,
            )
            self.subscription_purchase = requests.SubscriptionPurchaseRequest(
                taxi_plus,
            )
            self.subscription_upgrade = requests.SubscriptionUpgrade(taxi_plus)
            self.subscription_status = requests.SubscriptionStatusRequest(
                taxi_plus,
            )
            self.internal_list = requests.InternalListRequest(taxi_plus)
            self.uid_notify_handle = requests.UidNotifyHandle(taxi_plus)
            self.subscription_stop = requests.SubscriptionStop(taxi_plus)
            self.totw_info = requests.TotwInfo(taxi_plus)
            self.country = requests.Country(taxi_plus)

    return Ctx(taxi_plus)


@pytest.fixture(name='mock_mediabilling')
def _mock_mediabilling(mockserver, load_json):
    class Context:
        submit_order = responses.SubmitNativeOrderResponse()
        order_info = responses.BillingOrderInfoResponse()
        transfer = responses.TransferResponse()
        stop_subscription = responses.StopSubscription()
        transitions = responses.TransitionsResponse(load_json)

    context = Context()

    @mockserver.handler(
        '/mediabilling/internal-api/account/submit-native-order',
    )
    def _mock_submit(request):
        assert request.query['source'] == 'taxi'
        return context.submit_order.make_response(mockserver)

    @mockserver.handler(
        '/mediabilling/internal-api/account/billing/order-info',
    )
    def _mock_order_info(request):
        return context.order_info.make_response(mockserver)

    @mockserver.handler(
        '/mediabilling/internal-api'
        '/subscription/transfer-native-subscription',
    )
    def _mock_transfer(request):
        return context.transfer.make_response(mockserver)

    @mockserver.handler('/mediabilling/internal-api/account/stop-subscription')
    def _mock_stop_subscription(request):
        return context.stop_subscription.make_response(mockserver)

    @mockserver.handler('/fast-prices/billing/transitions')
    def _mock_get_transitions(request):

        return context.transitions.make_response(mockserver)

    return context


@pytest.fixture(name='mock_mediabilling_v2')
def _mock_mediabilling_v2(mockserver):
    class Context:
        cashback_status = responses.CashbackStatusResponse()

    context = Context()

    @mockserver.handler('/mediabilling-v2/billing/cashback-status')
    def _mock_cashback_status(request):
        assert request.query['status'] == 'enabled'
        assert request.query['uid'] == '123456'
        return context.cashback_status.make_response(mockserver)

    return context


@pytest.fixture(name='mock_order_core')
def _mock_order_core(mockserver):
    class Context:
        order_fields = responses.OrderFields()

    context = Context()

    @mockserver.handler('/order-core/v1/tc/order-fields')
    def _mock_order_fields(request):
        return context.order_fields.make_response(mockserver)

    return context


@pytest.fixture(autouse=True)
def _mock_plus_wallet(mockserver):
    @mockserver.handler('/plus-wallet/v1/balances')
    def _mock_balances(request):
        balances = [
            {
                'balance': '120.0000',
                'currency': 'RUB',
                'wallet_id': 'some_wallet_id',
            },
        ]
        return mockserver.make_response(
            json={'balances': balances}, status=200,
        )
