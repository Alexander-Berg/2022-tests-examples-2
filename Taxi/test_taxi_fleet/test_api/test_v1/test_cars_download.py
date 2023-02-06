import aiohttp.web
import pytest

URL = '/api/v1/cars/download'


async def test_success(web_app_client, headers, load_json, mock_api7):
    service_stub = load_json('service_success.json')
    api7_cars_stub = load_json('api7_cars_success.json')

    @mock_api7('/v1/parks/cars/list')
    async def _v1_parks_cars_list(request):
        assert request.json == api7_cars_stub['request']
        return aiohttp.web.json_response(api7_cars_stub['response'])

    response = await web_app_client.post(
        URL, headers=headers, json=service_stub['request'],
    )

    assert response.status == 200


@pytest.mark.translations(
    opteum_page_cars={
        'th_id': {'ru': ''},
        'th_status': {'ru': 'Статус'},
        'th_callsign': {'ru': 'Позывной'},
        'th_brand': {'ru': 'Бренд'},
        'th_model': {'ru': 'Модель'},
        'th_year': {'ru': 'Год'},
        'th_gov_number': {'ru': 'Гос. номер'},
        'th_color': {'ru': 'Цвет'},
        'th_permit': {'ru': 'Лицензия'},
        'th_vin': {'ru': 'VIN'},
        'th_sts': {'ru': 'СТС'},
        'th_created_date': {'ru': 'Дата создания'},
    },
)
async def test_prepared_file(
        web_app_client, headers, load_json, load, mock_api7,
):
    service_stub = load_json('service_success.json')
    api7_cars_stub = load_json('api7_cars_success.json')
    vehicles_stub = load('vehicles.csv')

    @mock_api7('/v1/parks/cars/list')
    async def _v1_parks_cars_list(request):
        assert request.json == api7_cars_stub['request']
        return aiohttp.web.json_response(api7_cars_stub['response'])

    response = await web_app_client.post(
        URL, headers=headers, json=service_stub['request'],
    )

    response_vehicles_csv = await response.text(encoding='utf-8')

    assert response_vehicles_csv.replace('\r\n', '\n') == vehicles_stub
