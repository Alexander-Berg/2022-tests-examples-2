from typing import Any
from typing import Dict

import pytest

from taxi.clients import admin as taxi_api_admin


@pytest.fixture(name='taxi_api_admin_mock')
async def _taxi_api_admin_mock(patch):
    @patch('taxi.clients.admin.AdminApiClient.get_user_info')
    async def _get_user_info(*args, **kwargs) -> Dict[str, Any]:
        return {
            'login': 'some_user',
            'permissions': [
                'approve_cron_tasks',
                'get_surge_zones',
                'view_geosubventions',
                'create_geosubvention_calculations',
            ],
        }


@pytest.mark.config(
    ATLAS_BACKEND_ABK_PERMISSIONS=[
        'create_and_view_operations',
        'create_discounts_operation_calculations',
        'create_geosubvention_calculations',
        'edit_discounts_algorithms_configs',
        'edit_subventions_admin_confirmations',
        'view_discounts_operation_calculations',
        'view_geosubventions',
    ],
)
async def test_get_abk_permissions(
        web_app_client, atlas_blackbox_mock, taxi_api_admin_mock,
):
    response = await web_app_client.get('/api/abk-permissions')
    assert response.status == 200
    content = await response.json()
    assert len(content['permissions']) == 2
    assert {*content['permissions']} == {
        'create_geosubvention_calculations',
        'view_geosubventions',
    }


@pytest.mark.config(ATLAS_BACKEND_ABK_PERMISSIONS=[])
async def test_get_abk_permissions_on_empty_config(
        web_app_client, atlas_blackbox_mock, taxi_api_admin_mock,
):
    response = await web_app_client.get('/api/abk-permissions')
    assert response.status == 200
    content = await response.json()
    assert content['permissions'] == []


async def test_get_abk_permissions_on_unreachable_taxi_api_admin(
        web_app_client, atlas_blackbox_mock, patch,
):
    @patch('taxi.clients.admin.AdminApiClient.get_user_info')
    async def _get_user_info(*args, **kwargs):
        raise taxi_api_admin.AdminTimeoutError('Host is unreachable')

    response = await web_app_client.get('/api/abk-permissions')
    assert response.status == 200
    content = await response.json()
    assert content['permissions'] == []
