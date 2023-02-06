# pylint: disable=unused-variable
import json

import pytest

from taxi.util import permissions

USER_RESPONSE = {'status': 'ok'}


@pytest.mark.parametrize(
    'url,data',
    [
        (
            '/dynamic_permissions/create/',
            {
                'path': 'test_path',
                'service': 'test_service',
                'name': 'test_name',
                'rules': [
                    {
                        'extract_rule': {
                            'storage': 'request',
                            'path': 'asd.0.rr',
                        },
                        'items': {
                            'name_1': {'permission_name': 'dyn_perm_1'},
                            'name_2': {'permission_name': 'dyn_perm_2'},
                        },
                    },
                ],
            },
        ),
        (
            '/dynamic_permissions/update/',
            {
                'id': 'test_id_2',
                'version': 1,
                'rules': [
                    {
                        'extract_rule': {
                            'storage': 'url',
                            'path': 'named_name',
                        },
                        'items': {
                            'name_1': {'permission_name': 'dyn_perm_1'},
                            'name_2': {'permission_name': 'dyn_perm_2'},
                            'name_3': {'permission_name': 'dyn_perm_3'},
                        },
                    },
                ],
            },
        ),
    ],
)
async def test_dynamic_permissions_api(taxi_api_admin_client, url, data, db):
    response = await taxi_api_admin_client.post(url, json=data)
    data = await response.json()
    assert response.status == 200
    created_perm = await db.dynamic_permissions.find_one({'_id': data['id']})
    doc = permissions.DynamicPermission(created_perm)
    prepared_perm = doc.prepare_to_view()
    assert data == prepared_perm


@pytest.mark.parametrize(
    'url,method,data,expected_status',
    [
        (
            '/service_with_dynamic_permission/user/test_user_1/retrieve/',
            'POST',
            {},
            200,
        ),
        (
            '/service_with_dynamic_permission/user/search/',
            'POST',
            {'name': [{'mm': 'test_user_1'}, {'mm': 324}]},
            200,
        ),
        (
            '/service_with_dynamic_permission/user/retrieve_base_perm/',
            'POST',
            {'name': [{'mm': 'test_user_1'}, {'mm': 324}]},
            200,
        ),
        (
            '/service_with_dynamic_permission/user/retrieve_base_perm/',
            'POST',
            {'name': [{'mm': 'test_user_2'}, {'mm': 324}]},
            200,
        ),
        (
            '/service_with_dynamic_permission/user/retrieve_base_perm/',
            'POST',
            {'name': [{'mm': 'test_user_3'}, {'mm': 324}]},
            200,
        ),
        (
            '/service_with_dynamic_permission/user/retrieve_base_perm/',
            'POST',
            {'name': [{'some_random': 'asd'}]},
            200,
        ),
    ],
)
@pytest.mark.config(USE_NEW_DYNAMIC_FLOW=True)
async def test_scheme_with_dyn_perm(
        taxi_api_admin_client,
        url,
        method,
        data,
        expected_status,
        patch_aiohttp_session,
        response_mock,
):
    @patch_aiohttp_session('http://unstable-service-host.net/user/')
    def patch_user_request(method, url, **kwargs):
        return response_mock(
            text=str(USER_RESPONSE),
            read=bytes(json.dumps(USER_RESPONSE), encoding='utf-8'),
        )

    response = await taxi_api_admin_client.request(method, url, json=data)
    assert response.status == expected_status


@pytest.mark.parametrize(
    'url,method,data,expected_status,expected_result',
    [
        (
            '/service_with_dynamic_permission/just/another/request/',
            'POST',
            {'name': [{'mm': 'test_user_2'}]},
            403,
            {
                'status': 'error',
                'details': (
                    'Lack of following permissions (one of dynamic from rule '
                    'workability_scope '
                    '(view_price_modifications_taxi OR '
                    'view_price_modifications_cargo))'
                ),
            },
        ),
    ],
)
@pytest.mark.config(USE_NEW_DYNAMIC_FLOW=True)
async def test_non_dynamic_perm(
        taxi_api_admin_client,
        url,
        method,
        data,
        expected_status,
        expected_result,
):
    response = await taxi_api_admin_client.request(method, url, json=data)
    data = await response.json()
    assert response.status == expected_status, data
    assert data == expected_result
