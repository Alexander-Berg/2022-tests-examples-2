import aiohttp.web
import pytest


@pytest.mark.now('2020-07-17T14:31:01.467800+03:00')
async def test_success(
        web_app_client,
        mock_parks,
        mock_territories_countries_list,
        headers,
        load_json,
        mock_fleet_rent_py3,
        mock_billing_reports,
):
    service_stub = load_json('service_success.json')
    fleet_rent_stub = load_json('fleet_rent_success.json')
    billing_reports_balances_stub = load_json(
        'billing_reports_balances_success.json',
    )
    billing_reports_journal_stub = load_json(
        'billing_reports_journal_success.json',
    )

    @mock_fleet_rent_py3('/v1/park/rents/')
    async def _v1_park_rents(request):
        assert request.query == fleet_rent_stub['request']
        return aiohttp.web.json_response(fleet_rent_stub['response'])

    @mock_billing_reports('/v1/balances/select')
    async def _v1_balances_select(request):
        assert request.json == billing_reports_balances_stub['request']
        return aiohttp.web.json_response(
            billing_reports_balances_stub['response'],
        )

    @mock_billing_reports('/v1/journal/select')
    async def _v1_journal_select(request):
        assert request.json == billing_reports_journal_stub['request']
        return aiohttp.web.json_response(
            billing_reports_journal_stub['response'],
        )

    response = await web_app_client.post(
        '/api/v1/regular-charges/details/v2',
        headers=headers,
        json=service_stub['request'],
    )

    assert response.status == 200

    data = await response.json()
    assert data == service_stub['response']
