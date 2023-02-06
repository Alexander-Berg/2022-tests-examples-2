from tests_access_control.helpers import common


async def create_system(
        taxi_access_control,
        slug,
        *,
        expected_status_code,
        expected_response_json,
):
    response_json = await common.post(
        taxi_access_control,
        '/v1/admin/system/create/',
        {'slug': slug},
        expected_status_code,
    )
    if expected_status_code == 200:
        assert response_json['system'].pop('created_at')
        assert response_json['system'].pop('updated_at')
    assert expected_response_json == response_json, (
        expected_response_json,
        response_json,
    )
    return response_json


async def retrieve_system(
        taxi_access_control,
        data,
        *,
        expected_status_code,
        expected_response_json,
):
    response_json = await common.post(
        taxi_access_control,
        '/v1/admin/system/retrieve/',
        data,
        expected_status_code,
    )
    for system in response_json['systems']:
        assert system.pop('created_at')
        assert system.pop('updated_at')
    assert expected_response_json == response_json, (
        expected_response_json,
        response_json,
    )
    return response_json


async def get_system(
        taxi_access_control,
        params,
        *,
        expected_status_code,
        expected_response_json,
):
    response_json = await common.get(
        taxi_access_control, '/v1/admin/system/', params, expected_status_code,
    )
    if expected_status_code == 200:
        assert response_json['system'].pop('created_at')
        assert response_json['system'].pop('updated_at')
    assert expected_response_json == response_json, (
        expected_response_json,
        response_json,
    )
    return response_json
