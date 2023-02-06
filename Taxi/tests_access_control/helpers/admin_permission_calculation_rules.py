from tests_access_control.helpers import common


async def create_calculation_rule(
        taxi_access_control,
        system_slug,
        slug,
        storage,
        path,
        *,
        expected_status_code,
        expected_response_json,
):
    response_json = await common.post(
        taxi_access_control,
        '/v1/admin/calculation-rules/create/',
        {
            'system_slug': system_slug,
            'slug': slug,
            'storage': storage,
            'path': path,
        },
        expected_status_code,
    )

    if 'created_at' in response_json:
        del response_json['created_at']
    if 'updated_at' in response_json:
        del response_json['updated_at']

    if expected_status_code == 400:
        assert response_json['code'] == '400'
    else:
        assert expected_response_json == response_json, (
            expected_response_json,
            response_json,
        )
    return response_json
