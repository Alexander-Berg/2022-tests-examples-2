import aiohttp.web
import pytest

# Feel free to provide your custom implementation to override generated tests.

# pylint: disable=import-error,wildcard-import
from corp_billing_plugins.generated_tests import *  # noqa


# Every service must have this handler
@pytest.mark.config(
    CORP_BILLING_CARGO_SYNC_ENABLED=False,
    CORP_BILLING_DRIVE_SYNC_ENABLED=False,
    CORP_BILLING_EATS_SYNC_ENABLED=False,
    CORP_BILLING_TANKER_SYNC_ENABLED=False,
)
@pytest.mark.servicetest
async def test_ping(
        taxi_corp_billing, mockserver, load_json, sync_with_corp_cabinet,
):
    topic = load_json('topic_eats_order_with_refund.json')
    billing_order_status = load_json('billing_orders_process_response.json')
    billing_order = load_json('billing_order_eats_with_refund.json')

    @mockserver.json_handler('/corp-billing-events/v1/topics/compact')
    def events_topics_handler(request):  # pylint: disable=W0612
        # _print(request)
        return {'topics': [topic]}

    @mockserver.json_handler('/corp-billing-events/v1/events')
    def events_push_handler(request):  # pylint: disable=W0612
        _print(request)
        return {}

    @mockserver.json_handler('/corp-billing-events/v1/events/journal/topics')
    def events_journal_handler(request):  # pylint: disable=W0612
        # _print(request)
        changed = {
            'namespace': topic['namespace'],
            'topic': {
                'type': topic['topic']['type'],
                'external_ref': topic['topic']['external_ref'],
            },
        }
        body = {'changed_topics': [changed], 'cursor': '1'}
        return aiohttp.web.json_response(
            body, status=200, headers={'X-Polling-Delay-Ms': '10000'},
        )

    @mockserver.json_handler('/billing-orders/v2/process/async')
    def billing_orders_process_handler(request):  # pylint: disable=W0612
        _print(request)
        return billing_order_status

    @mockserver.json_handler('/billing-reports/v1/balances/select')
    def billing_reports_balances_handler(
            request,
    ):  # noqa pylint: disable=C0103, W0612
        _print(request)
        return {'entries': []}

    @mockserver.json_handler('/corp-billing/v1/billing-orders')
    def billing_orders_handler(request):  # pylint: disable=W0612
        _print(request)
        return {'orders': [billing_order]}

    await sync_with_corp_cabinet()

    response = await taxi_corp_billing.get('ping')
    # Status code must be checked for every request
    assert response.status_code == 200
    # Response content (even empty) must be checked for every request
    assert response.content == b''


def _print(request):
    print('#' * 72)
    print(request.method, request.path)
    print(request.json)
    print('-' * 72)
