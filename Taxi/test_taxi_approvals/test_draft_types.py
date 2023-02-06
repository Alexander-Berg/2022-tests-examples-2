import logging

import pytest

from taxi_approvals.internal import headers as headers_module


@pytest.fixture(name='get_draft_types')
def _get_draft_types(taxi_approvals_client):
    async def _request(draft_type, is_platform=False):
        headers = {headers_module.X_YANDEX_LOGIN: 'test_login'}
        if is_platform:
            headers[headers_module.X_MULTISERVICES_PLATFORM] = 'true'
        if draft_type:
            headers[headers_module.X_DRAFT_SCHEME_TYPE] = draft_type
        response = await taxi_approvals_client.get(
            '/drafts/types/', headers=headers,
        )
        return response

    return _request


@pytest.mark.parametrize(
    'is_platform, api_path, entity, service_name, zone_filter, draft_type, '
    'service_wide_entity',
    [
        pytest.param(
            True,
            'test_draft_get_types',
            'some_platform_entity',
            'test_service',
            True,
            '',
            '',
        ),
        pytest.param(
            True,
            'test_draft_get_types',
            'some_platform_entity',
            'test_service',
            True,
            'platform',
            '',
        ),
        pytest.param(
            False,
            'bank_test_api',
            'bank_entity',
            'bank_service',
            False,
            'bank',
            '',
        ),
        pytest.param(
            False,
            'bank_test_api_configs',
            'bank_entity_configs',
            'bank_service_configs',
            False,
            'bank',
            '',
        ),
        pytest.param(
            False,
            'test_api',
            'wfm_entity',
            'wfm_service',
            False,
            'wfm_effrat',
            '',
        ),
        pytest.param(
            False,
            'test_draft_get_types',
            'another_entity',
            'test_service',
            False,
            '',
            'some_entity',
        ),
    ],
)
async def test_get_draft_types(
        get_draft_types,
        is_platform,
        api_path,
        entity,
        service_name,
        zone_filter,
        draft_type,
        service_wide_entity,
):
    response = await get_draft_types(draft_type, is_platform=is_platform)
    types = await response.json()
    logging.error(f'response {types}')
    assert response.status == 200, types
    expected = {
        'entity': entity,
        'api_path': api_path,
        'service_name': service_name,
        'zone_filter': zone_filter,
        'entity_localized': 'drafts.%s' % entity,
        'api_path_localized': 'drafts.%s' % api_path,
    }

    if draft_type == 'bank':
        assert expected in types
        return

    if not service_wide_entity:
        assert [expected] == types
        return

    assert expected in types

    expected_with_service_entity = {
        'entity': service_wide_entity,
        'api_path': api_path + '_no_entity',
        'service_name': service_name,
        'zone_filter': True,
        'entity_localized': 'drafts.%s' % service_wide_entity,
        'api_path_localized': 'drafts.%s' % api_path + '_no_entity',
    }

    assert expected_with_service_entity in types
