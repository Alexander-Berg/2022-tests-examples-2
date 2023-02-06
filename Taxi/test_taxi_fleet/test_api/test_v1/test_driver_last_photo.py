import aiohttp.web
import pytest


@pytest.mark.parametrize(
    'dp_list_response, expected_code, expected_response',
    [
        ('response-removed', 404, 'response-404'),
        ('response-not-removed', 200, 'response-200'),
    ],
)
async def test_success(
        web_app_client,
        headers,
        mockserver,
        mock_udriver_photos,
        load_json,
        dp_list_response,
        expected_code,
        expected_response,
):
    stub = load_json('success.json')

    @mockserver.json_handler('/parks/driver-profiles/list')
    async def _v1_parks_driver_profiles_list(request):
        assert request.json == stub['driver-profiles-list']['request']
        return aiohttp.web.json_response(
            stub['driver-profiles-list'][dp_list_response],
        )

    @mock_udriver_photos('/driver-photos/v1/last-not-rejected-photo')
    async def _driver_photo(request):
        assert request.query == stub['udriver_photos']['request']
        return aiohttp.web.json_response(stub['udriver_photos']['response'])

    response = await web_app_client.post(
        '/api/v1/drivers/last-photo',
        headers=headers,
        json=stub['service']['request'],
    )

    assert response.status == expected_code

    data = await response.json()
    assert data == stub['service'][expected_response]
    assert _v1_parks_driver_profiles_list.times_called == 1
