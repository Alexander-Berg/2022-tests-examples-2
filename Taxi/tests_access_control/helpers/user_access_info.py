from tests_access_control.helpers import common


async def get_user_access_info(
        taxi_access_control,
        provider,
        provider_user_id,
        *,
        expected_status_code,
        expected_response_json,
):
    response_json = await common.post(
        taxi_access_control,
        '/v1/get-user-access-info/',
        {'provider': provider, 'provider_user_id': provider_user_id},
        expected_status_code,
    )
    assert expected_response_json == response_json, (
        expected_response_json,
        response_json,
    )
    return response_json
