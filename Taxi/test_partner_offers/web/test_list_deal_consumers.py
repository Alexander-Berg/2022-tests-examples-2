import pytest

LOYALTY_TRANSLATIONS = {
    'loyalty.status.title_bronze': {'ru': 'Бронзовый'},
    'loyalty.status.title_silver': {'ru': 'Серебряный'},
    'loyalty.status.title_gold': {'ru': 'Золотой'},
    'loyalty.status.title_platinum': {'ru': 'Платиновый'},
}

TARIFF_EDITOR_TRANSLATIONS = {
    'partner_deals_consumer_courier': {'ru': 'Курьер'},
    'partner_deals_consumer_driver': {'ru': 'Водитель'},
}


@pytest.mark.translations(
    taximeter_backend_driver_messages=LOYALTY_TRANSLATIONS,
    tariff_editor=TARIFF_EDITOR_TRANSLATIONS,
)
async def test_list_deal_consumers(web_app_client):
    response = await web_app_client.post(
        '/internal/v1/deals/consumers/list',
        headers={'Accept-Language': 'ru-Ru'},
    )
    assert response.status == 200, await response.text()
    assert await response.json() == {
        'groups': [
            {
                'code': 'driver',
                'label': 'Водитель',
                'loyalty_statuses': [
                    {'code': 'bronze', 'label': 'Бронзовый'},
                    {'code': 'gold', 'label': 'Золотой'},
                    {'code': 'platinum', 'label': 'Платиновый'},
                    {'code': 'silver', 'label': 'Серебряный'},
                ],
            },
            {
                'code': 'courier',
                'label': 'Курьер',
                'loyalty_statuses': [
                    {'code': '1', 'label': '1'},
                    {'code': '2', 'label': '2'},
                    {'code': '3', 'label': '3'},
                    {'code': '4', 'label': '4'},
                    {'code': '5', 'label': '5'},
                ],
            },
        ],
    }
