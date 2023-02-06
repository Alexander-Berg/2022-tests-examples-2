import aiohttp.web
import pytest


ENDPOINT = '/dashboard/v1/widget/orders/status'


FLEET_DASHOARD_KEYSET = {
    'widget.orders_status.series.successful': {'ru': 'Завершённые'},
    'widget.orders_status.series.driver_cancelled': {
        'ru': 'Отменены водителем',
    },
    'widget.orders_status.series.client_cancelled': {
        'ru': 'Отменены клиентом',
    },
    'widget.orders_status.series.total': {'ru': 'Всего'},
}

HEADERS = {
    'X-Ya-User-Ticket': 'user_ticket',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Yandex-Login': 'tarasalk',
    'X-Yandex-UID': '123',
    'X-Park-Id': 'c5cdea22ad6b4e4da8f3fdbd4bddc2e7',
    'X-Real-IP': '127.0.0.1',
    'Accept-Language': 'ru',
}


@pytest.mark.parametrize(
    'success_json', ['success.json', 'empty_one_response.json'],
)
@pytest.mark.translations(fleet_dashboard=FLEET_DASHOARD_KEYSET)
async def test_success(
        web_app_client, mock_driver_orders_metrics, load_json, success_json,
):
    stub = load_json(success_json)

    @mock_driver_orders_metrics('/v1/parks/orders/metrics-by-intervals')
    async def _orders_metrics_by_interval(request):
        assert request.json == stub['metrics']['request']
        return aiohttp.web.json_response(stub['metrics']['response'])

    response = await web_app_client.post(
        ENDPOINT, headers=HEADERS, json=stub['service']['request'],
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service']['response']
