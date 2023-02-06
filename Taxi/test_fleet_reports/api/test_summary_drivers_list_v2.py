import aiohttp.web
import pytest


async def _test_func(web_app_client, headers, mock_api7, stub):
    @mock_api7('/v1/parks/driver-profiles/list')
    async def _list_drivers(request):
        assert request.json == stub['drivers']['request']
        return aiohttp.web.json_response(stub['drivers']['response'])

    response = await web_app_client.post(
        '/reports-api/v2/summary/drivers/list',
        headers=headers,
        json=stub['service']['request'],
    )

    assert response.status == stub['service']['response_code']

    data = await response.json()
    assert data == stub['service']['response']


@pytest.mark.pgsql('fleet_reports', files=('success.sql',))
@pytest.mark.config(
    FLEET_REPORTS_BILLING_ACCOUNTS_MAPPING={
        'report_summary': {
            'price_cash': [
                {'category_id': 'category_1'},
                {'category_id': 'category_2'},
            ],
            'price_cashless': [
                {
                    'agreement_id': 'agreement_1',
                    'sub_account': 'sub_account_1',
                },
            ],
            'price_platform_commission': [],
            'price_park_commission': [],
            'price_software_commission': [],
            'price_other_gas': [],
        },
    },
)
@pytest.mark.parametrize(
    'stub_file_name', ['success.json', 'date_validation.json'],
)
async def test_by_stubs(
        web_app_client, headers, mock_api7, load_json, stub_file_name,
):
    stub = load_json(stub_file_name)

    await _test_func(web_app_client, headers, mock_api7, stub)
