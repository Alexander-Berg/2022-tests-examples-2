import pytest


@pytest.mark.config(
    DRIVER_REFERRALS_TARIFFS_BY_ORDERS_PROVIDER={
        'taxi': [],
        'eda': ['eda'],
        'lavka': ['lavka'],
        'retail': ['lavka'],
        'cargo': [],
        'taxi_walking_courier': [],
    },
)
async def test_admin_tariffs_by_orders_provider_get(web_app_client):
    response = await web_app_client.get('/admin/tariffs_by_orders_provider/')
    assert response.status == 200
    data = await response.json()
    assert data['taxi'] == []
    assert data['eda'] == [{'name': 'eda', 'translation': 'eda'}]
    assert data['lavka'] == [{'name': 'lavka', 'translation': 'lavka'}]
    assert data['retail'] == [{'name': 'lavka', 'translation': 'lavka'}]
