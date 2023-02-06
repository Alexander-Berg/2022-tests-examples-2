import pytest


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
            'price_hiring_services': [],
        },
    },
)
async def test_success(web_app_client, headers, load_json):
    stub = load_json('success.json')

    response = await web_app_client.post(
        '/reports-api/v2/summary/parks/list', headers=headers,
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service']['response']
