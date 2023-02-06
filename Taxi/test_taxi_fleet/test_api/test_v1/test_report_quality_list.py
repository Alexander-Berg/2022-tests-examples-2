import aiohttp.web
import pytest


@pytest.mark.pgsql('taxi_db_opteum', files=('taxi_db_opteum.sql',))
async def test_success(web_app_client, headers, mockserver, load_json):
    stub = load_json('success.json')
    stub_parks_drivers = load_json('success_parks_drivers.json')

    @mockserver.json_handler('/parks/driver-profiles/list')
    async def _v1_driver_profiles_retrieve(request):
        assert request.json == stub_parks_drivers['request_drivers']
        return aiohttp.web.json_response(
            stub_parks_drivers['response_drivers'],
        )

    response = await web_app_client.post(
        '/api/v1/reports/quality/list',
        headers=headers,
        json={
            'date_from': '2020-03-02',
            'date_to': '2020-03-15',
            'limit': 25,
            'sort_order': {'direction': 'asc', 'field': 'rating_end'},
        },
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']


@pytest.mark.pgsql('taxi_db_opteum', files=('taxi_db_opteum.sql',))
async def test_success_with_driver_ids(
        web_app_client, headers, mockserver, load_json,
):
    stub = load_json('success.json')
    stub_parks_drivers = load_json('success_parks_drivers.json')

    @mockserver.json_handler('/parks/driver-profiles/list')
    async def _v1_driver_profiles_retrieve(request):
        assert (
            request.json
            == stub_parks_drivers['request_drivers_with_driver_ids']
        )
        return aiohttp.web.json_response(
            stub_parks_drivers['response_drivers_with_driver_ids'],
        )

    response = await web_app_client.post(
        '/api/v1/reports/quality/list',
        headers=headers,
        json={
            'date_from': '2020-03-02',
            'date_to': '2020-03-15',
            'limit': 25,
            'sort_order': {'direction': 'asc', 'field': 'rating_end'},
            'driver_ids': ['038b62af7118498583d3ec1d05132fee'],
        },
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response_with_driver_ids']


@pytest.mark.pgsql('taxi_db_opteum', files=('taxi_db_opteum.sql',))
async def test_success_period_one_week(
        web_app_client, headers, mockserver, load_json,
):
    stub = load_json('success.json')
    stub_parks_drivers = load_json('success_parks_drivers.json')

    @mockserver.json_handler('/parks/driver-profiles/list')
    async def _v1_driver_profiles_retrieve(request):
        assert request.json == stub_parks_drivers['request_drivers_p1w']
        return aiohttp.web.json_response(
            stub_parks_drivers['response_drivers_p1w'],
        )

    response = await web_app_client.post(
        '/api/v1/reports/quality/list',
        headers=headers,
        json={
            'date_from': '2020-03-09',
            'date_to': '2020-03-15',
            'limit': 25,
            'sort_order': {'direction': 'asc', 'field': 'rating_end'},
        },
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response_p1w']


@pytest.mark.pgsql('taxi_db_opteum', files=('taxi_db_opteum.sql',))
async def test_success_support_mode(
        web_app_client, headers_support, mockserver, load_json,
):
    stub = load_json('success.json')
    stub_parks_drivers = load_json('success_parks_drivers.json')

    @mockserver.json_handler('/parks/driver-profiles/list')
    async def _v1_driver_profiles_retrieve(request):
        assert request.json == stub_parks_drivers['request_drivers']
        return aiohttp.web.json_response(
            stub_parks_drivers['response_drivers'],
        )

    response = await web_app_client.post(
        '/api/v1/reports/quality/list',
        headers=headers_support,
        json={
            'date_from': '2020-03-02',
            'date_to': '2020-03-15',
            'limit': 25,
            'sort_order': {'direction': 'asc', 'field': 'rating_end'},
        },
    )

    assert response.status == 200

    report = []
    for item in stub['service_response']['report']:
        del item['driver']['phone']
        report.append(item)
    stub['service_response']['report'] = report

    data = await response.json()
    assert data == stub['service_response']
