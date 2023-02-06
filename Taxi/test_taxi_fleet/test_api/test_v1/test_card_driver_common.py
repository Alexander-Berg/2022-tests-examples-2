import aiohttp.web
import pytest


@pytest.mark.parametrize('is_removed_by_request', [None, False, True])
async def test_success(
        web_app_client,
        headers,
        mockserver,
        mock_api7,
        mock_udriver_photos,
        mock_driver_fix,
        load_json,
        is_removed_by_request,
):
    stub = load_json('success.json')

    @mockserver.json_handler('/parks/driver-profiles/retrieve')
    async def _driver_retrieve(request):
        assert request.json == stub['parks_driver_retrieve']['request']
        response = stub['parks_driver_retrieve']['response']
        if is_removed_by_request is not None:
            response['driver_profile'][
                'is_removed_by_request'
            ] = is_removed_by_request
            response['driver_profile']['is_readonly'] = is_removed_by_request
        return response

    @mockserver.json_handler(
        'taximeter-xservice/utils/qc/driver/exams/retrieve',
    )
    async def _get_driver_exams(request):
        assert request.json == stub['taximeter_driver_exams']['request']
        return aiohttp.web.json_response(
            stub['taximeter_driver_exams']['response'],
        )

    @mock_udriver_photos('/driver-photos/v1/last-not-rejected-photo')
    async def _get_driver_photo(request):
        assert request.query == stub['udriver_photos']['request']
        return aiohttp.web.json_response(stub['udriver_photos']['response'])

    @mock_driver_fix('/v1/view/status_summary')
    async def _get_driver_fix_status_summary(request):
        assert request.query == stub['driver_fix']['request']
        return aiohttp.web.json_response(stub['driver_fix']['response'])

    @mockserver.json_handler(
        'taximeter-xservice/utils/blacklist/drivers/check',
    )
    async def _get_driver_blacklist(request):
        assert request.json == stub['taximeter_driver_blacklist']['request']
        return aiohttp.web.json_response(
            stub['taximeter_driver_blacklist']['response'],
        )

    @mockserver.json_handler('taximeter-xservice/utils/blacklist/cars/check')
    async def _get_car_blacklist(request):
        assert request.json == stub['parks_car_blacklist']['request']
        return aiohttp.web.json_response(
            stub['parks_car_blacklist']['response'],
        )

    @mockserver.json_handler(
        '/contractor-profession/internal/v1/professions/get/active/bulk',
    )
    async def _professions_get(request):
        assert request.json == stub['contractor_profession']['request']
        return aiohttp.web.json_response(
            stub['contractor_profession']['response'],
        )

    response = await web_app_client.post(
        '/api/v1/cards/driver/common',
        headers=headers,
        json=stub['service']['request'],
    )

    assert response.status == 200

    data = await response.json()
    expected_response = stub['service']['response']
    if is_removed_by_request is not None:
        expected_response['driver']['driver_profile'][
            'is_readonly'
        ] = is_removed_by_request
        expected_response['driver']['driver_profile'][
            'is_removed_by_request'
        ] = is_removed_by_request
    if is_removed_by_request:
        expected_response.pop('driver_photo')
    assert data == expected_response
