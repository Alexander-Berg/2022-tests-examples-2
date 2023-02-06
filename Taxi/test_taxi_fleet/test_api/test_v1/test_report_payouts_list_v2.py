import aiohttp.web
import pytest

URL = '/api/v1/reports/payouts/list/v2'

STATUSES = [
    {
        'fleet_status': 'created',
        'oebs_statuses': ['CREATED'],
        'selected': True,
        'tanker_key': {
            'key': 'status_created',
            'keyset': 'opteum_page_report_payouts',
        },
    },
    {
        'fleet_status': 'transmitted',
        'oebs_statuses': ['TRANSMITTED'],
        'selected': True,
        'tanker_key': {
            'key': 'status_transmitted',
            'keyset': 'opteum_page_report_payouts',
        },
    },
    {
        'fleet_status': 'paid',
        'oebs_statuses': ['CONFIRMED', 'RECONCILED'],
        'selected': True,
        'tanker_key': {
            'key': 'status_paid',
            'keyset': 'opteum_page_report_payouts',
        },
    },
    {
        'fleet_status': 'canceled',
        'oebs_statuses': ['VOID', 'DEFERRED', 'RETURNED'],
        'selected': False,
        'tanker_key': {
            'key': 'status_canceled',
            'keyset': 'opteum_page_report_payouts',
        },
    },
]


@pytest.mark.config(OPTEUM_REPORT_PAYOUTS_STATUSES=STATUSES)
async def test_success(
        web_app_client,
        mock_parks,
        headers,
        load_json,
        mock_billing_bank_orders,
):
    service_stub = load_json('service_success.json')
    billing_bank_orders_stub = load_json('billing_bank_orders_success.json')

    @mock_billing_bank_orders('/v1/parks/payments/search')
    async def _v1_parks_payments_search(request):
        assert request.json == billing_bank_orders_stub['request']
        return aiohttp.web.json_response(billing_bank_orders_stub['response'])

    response = await web_app_client.post(
        URL, headers=headers, json=service_stub['request'],
    )

    assert response.status == 200, (
        await response.json() == service_stub['response']
    )
