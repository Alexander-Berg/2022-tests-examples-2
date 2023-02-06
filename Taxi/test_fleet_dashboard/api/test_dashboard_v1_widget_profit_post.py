import aiohttp.web
import pytest

ENDPOINT = '/dashboard/v1/widget/profit'


def build_headers(park_id) -> dict:
    return {
        'X-Ya-User-Ticket': 'user_ticket',
        'X-Ya-User-Ticket-Provider': 'yandex',
        'X-Yandex-Login': 'tarasalk',
        'X-Yandex-UID': '123',
        'X-Park-Id': park_id,
        'X-Real-IP': '127.0.0.1',
        'Accept-Language': 'ru',
    }


FLEET_DASHBOARD_WIDGET_SERIES = {
    'widgets': [
        {
            'id': 'profit',
            'series': {
                'yandex_fleet': ['orders', 'shifts', 'bonus', 'driver_fix'],
                'yango_fleet': ['orders'],
            },
        },
    ],
}


FLEET_DASHOARD_KEYSET = {
    'widget.profit.series.orders': {'ru': 'Заказы'},
    'widget.profit.series.shifts': {'ru': 'Смены'},
    'widget.profit.series.bonus': {'ru': 'Бонусы'},
    'widget.profit.series.driver_fix': {'ru': 'Режим "Время"'},
}


@pytest.mark.config(
    FLEET_DASHBOARD_WIDGET_SERIES=FLEET_DASHBOARD_WIDGET_SERIES,
)
@pytest.mark.parametrize(
    'success_json, park_id',
    [
        ('success.json', '7ad36bc7560449998acbe2c57a75c293'),
        ('success_saas.json', 'c5cdea22ad6b4e4da8f3fdbd4bddc2e7'),
    ],
)
@pytest.mark.translations(fleet_dashboard=FLEET_DASHOARD_KEYSET)
async def test_success(
        web_app_client,
        mock_parks,
        mock_territories_api,
        mock_billing_reports,
        load_json,
        success_json,
        park_id,
):
    stub = load_json(success_json)

    @mock_billing_reports('/v1/balances/select')
    async def __balances(request):
        assert request.json == stub['ba_request']
        return aiohttp.web.json_response(stub['ba_response'])

    response = await web_app_client.post(
        ENDPOINT,
        headers=build_headers(park_id),
        json={
            'date_from': '2020-01-20T00:00:00+03:00',
            'date_to': '2020-01-27T00:00:00+03:00',
        },
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']


@pytest.mark.config(
    FLEET_DASHBOARD_WIDGET_SERIES=FLEET_DASHBOARD_WIDGET_SERIES,
)
@pytest.mark.parametrize(
    'success_empty_json, park_id',
    [
        ('success_empty.json', '7ad36bc7560449998acbe2c57a75c293'),
        ('success_empty_saas.json', 'c5cdea22ad6b4e4da8f3fdbd4bddc2e7'),
    ],
)
@pytest.mark.translations(fleet_dashboard=FLEET_DASHOARD_KEYSET)
async def test_success_empty_response(
        web_app_client,
        mock_parks,
        mock_territories_api,
        mock_billing_reports,
        load_json,
        success_empty_json,
        park_id,
):
    stub = load_json(success_empty_json)

    @mock_billing_reports('/v1/balances/select')
    async def __balances(request):
        assert request.json == stub['ba_request']
        return aiohttp.web.json_response(stub['ba_response'])

    response = await web_app_client.post(
        ENDPOINT,
        headers=build_headers(park_id),
        json={
            'date_from': '2020-01-20T00:00:00+03:00',
            'date_to': '2020-01-27T00:00:00+03:00',
        },
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']
