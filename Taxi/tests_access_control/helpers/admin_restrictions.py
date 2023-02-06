from tests_access_control.helpers import common


async def create_restriction(
        taxi_access_control,
        system_slug,
        role_slug,
        handler_path,
        handler_method,
        restriction,
        *,
        expected_status_code,
        expected_response_json,
):
    response_json = await common.post(
        taxi_access_control,
        f'/v1/admin/restrictions/create/',
        {
            'restriction': {
                'handler': {'method': handler_method, 'path': handler_path},
                'predicate': restriction,
            },
        },
        expected_status_code,
        params={'system': system_slug, 'role': role_slug},
    )

    assert expected_response_json == response_json, (
        expected_response_json,
        response_json,
    )

    return response_json


async def update_restriction(
        taxi_access_control,
        system_slug,
        role_slug,
        handler_path,
        handler_method,
        restriction,
        *,
        expected_status_code,
        expected_response_json,
):
    response_json = await common.post(
        taxi_access_control,
        f'/v1/admin/restrictions/update/',
        {'predicate': restriction},
        expected_status_code,
        params={
            'system': system_slug,
            'role': role_slug,
            'handler_path': handler_path,
            'handler_method': handler_method,
        },
    )

    assert expected_response_json == response_json, (
        expected_response_json,
        response_json,
    )

    return response_json


async def delete_restriction(
        taxi_access_control,
        system_slug,
        role_slug,
        handler_path,
        handler_method,
        *,
        expected_status_code,
        expected_response_json,
):
    response_json = await common.post(
        taxi_access_control,
        '/v1/admin/restrictions/delete/',
        None,
        expected_status_code,
        params={
            'system': system_slug,
            'role': role_slug,
            'handler_path': handler_path,
            'handler_method': handler_method,
        },
    )

    assert expected_response_json == response_json, (
        expected_response_json,
        response_json,
    )

    return response_json


async def get_restriction(
        taxi_access_control,
        system_slug,
        role_slug,
        handler_path,
        handler_method,
        *,
        expected_status_code,
        expected_response_json,
):
    response_json = await common.get(
        taxi_access_control,
        '/v1/admin/restrictions/',
        {
            'system': system_slug,
            'role': role_slug,
            'handler_path': handler_path,
            'handler_method': handler_method,
        },
        expected_status_code,
    )

    assert expected_response_json == response_json, (
        expected_response_json,
        response_json,
    )

    return response_json


async def retrieve_restriction(
        taxi_access_control,
        system_slug,
        role_slug,
        body,
        *,
        expected_status_code,
        expected_response_json,
):
    response_json = await common.post(
        taxi_access_control,
        '/v1/admin/restrictions/retrieve/',
        body,
        expected_status_code,
        params={'system': system_slug, 'role': role_slug},
    )

    assert expected_response_json == response_json, (
        expected_response_json,
        response_json,
    )

    return response_json
