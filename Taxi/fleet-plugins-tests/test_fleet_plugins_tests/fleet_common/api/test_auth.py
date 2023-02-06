import aiohttp.web
import pytest


@pytest.mark.pgsql('taxi_db_opteum', files=('parks.sql',))
async def test_success_with_park_id(
        web_app_client, mock_api7, mock_dispatcher_access_control, load_json,
):
    stub = load_json('success.json')

    @mock_api7('/v1/parks')
    async def _parks(request):
        return aiohttp.web.json_response(stub['parks_response'])

    @mock_dispatcher_access_control('/v1/parks/users/yandex/grants/list')
    async def _v1_parks_users_yandex_grants_list(request):
        return aiohttp.web.json_response(
            stub['dispatcher_access_control_response'],
        )

    response = await web_app_client.post(
        '/fleet_common/services/auth',
        headers=stub['service_request_headers']['success'],
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']


@pytest.mark.pgsql('taxi_db_opteum', files=('parks.sql',))
async def test_success_without_park_id(
        web_app_client, mock_api7, mock_dispatcher_access_control, load_json,
):
    stub = load_json('success.json')

    @mock_api7('/v1/parks')
    async def _parks(request):
        return aiohttp.web.json_response(stub['parks_response'])

    @mock_dispatcher_access_control('/v1/parks/users/yandex/grants/list')
    async def _v1_parks_users_yandex_grants_list(request):
        return aiohttp.web.json_response(
            stub['dispatcher_access_control_response'],
        )

    response = await web_app_client.post(
        '/fleet_common/services/auth',
        headers=stub['service_request_headers']['success'],
    )

    assert response.status == 200
    # TODO check response


@pytest.mark.pgsql('taxi_db_opteum', files=('parks.sql',))
async def test_success_with_user(
        web_app_client, mock_api7, mock_dispatcher_access_control, load_json,
):
    stub = load_json('success.json')

    @mock_api7('/v1/parks')
    async def _parks(request):
        return aiohttp.web.json_response(stub['parks_response'])

    @mock_dispatcher_access_control('/v1/parks/users/yandex/grants/list')
    async def _v1_parks_users_yandex_grants_list(request):
        return aiohttp.web.json_response(
            stub['dispatcher_access_control_response'],
        )

    @mock_api7('/v1/users/list')
    async def _users(request):
        return aiohttp.web.json_response(stub['users_response'])

    response = await web_app_client.post(
        '/fleet_common/services/auth-with-user',
        headers=stub['service_request_headers']['success'],
    )

    assert response.status == 200
    # TODO check response


@pytest.mark.pgsql('taxi_db_opteum', files=('parks.sql',))
async def test_park_not_found(web_app_client, mock_api7, load_json):
    stub = load_json('success.json')

    @mock_api7('/v1/parks')
    async def _parks(request):
        return aiohttp.web.json_response(stub['parks_response'])

    response = await web_app_client.post(
        '/fleet_common/services/auth',
        headers=stub['service_request_headers']['park_not_found'],
    )

    assert response.status == 404
