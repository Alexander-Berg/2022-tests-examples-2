import aiohttp.web
import pytest

URL = '/api/v1/reports/payouts/details/download/v3'

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


@pytest.mark.config(
    OPTEUM_REPORT_PAYOUTS_STATUSES=STATUSES,
    TAXI_FLEET_REPORT_PAYOUTS_DOWNLOAD_ZIP={'enable': False},
)
async def test_success_csv(
        web_app_client,
        mock_parks,
        headers,
        load_json,
        mock_fleet_reports_storage,
        stq,
):
    stub = load_json('success.json')

    @mock_fleet_reports_storage('/internal/user/v1/operations/create')
    async def _create(request):
        assert request.json == stub['fleet_reports_storage']['request']
        return aiohttp.web.json_response(data={})

    response = await web_app_client.post(
        URL, headers=headers, json=stub['service']['request'],
    )

    assert stq.payout_details_async_download_preparer.has_calls
    assert response.status == 200


@pytest.mark.config(
    OPTEUM_REPORT_PAYOUTS_STATUSES=STATUSES,
    TAXI_FLEET_REPORT_PAYOUTS_DOWNLOAD_ZIP={'enable': False},
)
async def test_success_csv_new(
        web_app_client,
        mock_parks,
        headers,
        load_json,
        mock_fleet_reports_storage,
        stq,
):
    stub = load_json('success.json')

    @mock_fleet_reports_storage('/internal/user/v1/operations/create')
    async def _create(request):
        assert request.json == stub['fleet_reports_storage']['request']
        return aiohttp.web.json_response(data={})

    headers.update(
        {
            'X-YaTaxi-Fleet-Permissions': (
                'report_payouts_details_download_async_new'
            ),
        },
    )
    response = await web_app_client.post(
        URL, headers=headers, json=stub['service']['request'],
    )

    assert stq.payout_details_async_download_preparer.has_calls
    assert response.status == 200
