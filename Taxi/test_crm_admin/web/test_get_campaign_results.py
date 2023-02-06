import pytest


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_empty_data(web_app_client):
    response = await web_app_client.get('/v1/campaigns/results?campaign_id=21')
    assert response.status == 200
    response_data = await response.json()
    assert response_data == []


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_sorted_data(web_app_client):
    response = await web_app_client.get('/v1/campaigns/results?campaign_id=51')
    assert response.status == 200
    response_data = await response.json()
    assert len(response_data) == 3
    assert response_data[0] == {
        'metric': 'Profit',
        'description': 'description 51_1',
        'hint': 'hint 51_1',
        'grade': -2,
        'value': 51.1,
        'unit': 'unit 51_1',
        'secondary_value': 5.11,
        'secondary_unit': 'secondary_unit 51_1',
        'secondary_description': 'secondary_description 51_1',
        'recommendation': 'recommendation 51_1',
        'statistical_significance': False,
        'is_final': True,
        'metric_order': 1,
    }
