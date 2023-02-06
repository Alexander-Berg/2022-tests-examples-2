from tests_access_control.helpers import common


async def create_group(
        taxi_access_control,
        system_slug,
        name,
        slug,
        *,
        parent_group_slug,
        expected_status_code,
        expected_response_json,
):
    data = {'name': name, 'system_slug': system_slug, 'slug': slug}
    if parent_group_slug:
        data['parent_group_slug'] = parent_group_slug
    response_json = await common.post(
        taxi_access_control,
        '/v1/admin/groups/create/',
        data,
        expected_status_code,
    )
    assert expected_response_json == response_json, (
        expected_response_json,
        response_json,
    )
    return response_json


async def retrieve_groups(
        taxi_access_control,
        data,
        params,
        *,
        expected_status_code,
        expected_response_json,
):
    response_json = await common.post(
        taxi_access_control,
        '/v1/admin/groups/retrieve/',
        data,
        expected_status_code,
        params=params,
    )
    assert expected_response_json == response_json, (
        expected_response_json,
        response_json,
    )
    return response_json


async def get_group(
        taxi_access_control,
        params,
        *,
        expected_status_code,
        expected_response_json,
):
    response_json = await common.get(
        taxi_access_control, '/v1/admin/groups/', params, expected_status_code,
    )
    assert expected_response_json == response_json, (
        expected_response_json,
        response_json,
    )
    return response_json
