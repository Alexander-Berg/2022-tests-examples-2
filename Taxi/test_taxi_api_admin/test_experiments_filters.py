# pylint: disable=protected-access
# pylint: disable=unused-variable
import json as json_

import pytest


@pytest.mark.parametrize(
    'test_url,data,params,config,expected',
    [
        (
            '/service_with_experiments_filters/v1/tariffs/',
            {'test': 1, 'test2': 2},
            {},
            {'test': 1},
            200,
        ),
        (
            '/service_with_experiments_filters/v1/tariffs/',
            {'test': 1, 'test2': 2, 'test3': 2},
            {},
            {'$body': {'test': 1, 'test2': 2}},
            200,
        ),
        (
            '/service_with_experiments_filters/v1/tariffs/',
            {'test': 1},
            {'test': 2, 'test1': 3},
            {'$query': {'test': 2}},
            200,
        ),
        (
            '/service_with_experiments_filters/v1/tariffs/',
            {'test': 1, 'test2': 2, 'test3': 2},
            {'test': 2, 'test1': 3},
            {'$body': {'test': 1, 'test2': 2}, '$query': {'test': 1}},
            422,
        ),
        (
            '/service_with_experiments_filters/v1/tariffs/',
            {},
            {},
            {'$body': {'test': 1, 'test2': 2}, '$query': {'test': 1}},
            422,
        ),
    ],
)
async def test_service_with_no_response(
        test_url,
        data,
        params,
        config,
        expected,
        taxi_api_admin_client,
        patch_aiohttp_session,
        response_mock,
        client_experiments3,
):
    @patch_aiohttp_session('http://unstable-service.yandex.net')
    def patch_request(*args, **kwargs):
        return response_mock(read=b'ok')

    client_experiments3.add_record(
        consumer='api_admin/service',
        config_name='admin_restrictions',
        args=[
            {'name': 'groups', 'type': 'set_string', 'value': []},
            {'name': 'login', 'type': 'string', 'value': 'superuser'},
        ],
        value={'/admin/service_with_experiments_filters/v1/tariffs/': config},
    )

    data_as_str = json_.dumps(data)
    response = await taxi_api_admin_client.request(
        'POST', test_url, data=data_as_str, params=params,
    )
    content = await response.text()
    assert response.status == expected, f'Content: {content}'
