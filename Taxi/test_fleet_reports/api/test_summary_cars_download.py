import aiohttp.web
import pytest


@pytest.mark.pgsql('fleet_reports', files=('success.sql',))
async def test_success(web_app_client, headers, mock_api7, load_json):
    stub = load_json('success.json')

    @mock_api7('/v1/parks/cars/list')
    async def _list_cars(request):
        assert request.json == stub['cars']['request']
        return aiohttp.web.json_response(stub['cars']['response'])

    @mock_api7('/v1/parks/driver-profiles/list')
    async def _list_drivers(request):
        assert request.json == stub['drivers']['request']
        return aiohttp.web.json_response(stub['drivers']['response'])

    response = await web_app_client.post(
        '/reports-api/v1/summary/cars/download',
        headers=headers,
        json=stub['service']['request'],
    )

    assert response.status == 200


@pytest.mark.translations(
    fleet_page_report_summary_cars={
        'th_car_id': {'ru': 'ID автомобиля'},
        'th_car': {'ru': 'Автомобиль'},
        'th_drivers': {'ru': 'Водители со списаниями'},
        'th_orders': {'ru': 'Успешно выполненные заказы'},
        'th_distance': {'ru': 'Км на заказах'},
        'th_cash': {'ru': 'Наличные'},
        'th_cashless': {'ru': 'Безналичные'},
        'th_price_rent': {'ru': 'Аренда'},
        'th_rent_withdraw': {'ru': ''},
        'th_rent_withhold': {'ru': ''},
        'th_rent_cancel': {'ru': ''},
        'th_rent_withdraw_wait': {'ru': ''},
        'th_rent': {'ru': 'Сдаваемость'},
        'th_rent_days': {'ru': 'Дни со списанием аренды'},
    },
)
@pytest.mark.pgsql('fleet_reports', files=('division_by_zero.sql',))
async def test_division_by_zero(
        web_app_client, headers, mock_api7, load_json, load,
):
    stub = load_json('division_by_zero.json')
    summary_cars_stub = load('summary_cars.csv')

    @mock_api7('/v1/parks/cars/list')
    async def _list_cars(request):
        assert request.json == stub['cars']['request']
        return aiohttp.web.json_response(stub['cars']['response'])

    @mock_api7('/v1/parks/driver-profiles/list')
    async def _list_drivers(request):
        assert request.json == stub['drivers']['request']
        return aiohttp.web.json_response(stub['drivers']['response'])

    response = await web_app_client.post(
        '/reports-api/v1/summary/cars/download',
        headers=headers,
        json=stub['service']['request'],
    )

    response_summary_cars_csv = await response.text(encoding='utf-8')

    assert response.status == 200
    assert response_summary_cars_csv.replace('\r\n', '\n') == summary_cars_stub
