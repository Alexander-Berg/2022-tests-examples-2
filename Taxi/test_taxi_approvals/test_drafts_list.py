import pytest

from taxi_approvals.internal import headers as headers_module


@pytest.mark.parametrize(
    'filters,query,list_length',
    [
        ({}, {}, 12),
        ({'service_name': 'test_service', 'api_path': 'test_api2'}, {}, 2),
        ({'services_names': ['test_service2', 'test_service']}, {}, 12),
        (
            {
                'services_names': ['test_service2'],
                'service_name': 'test_service',
            },
            {},
            8,
        ),
        ({'api_path': 'test_api2'}, {}, 4),
        ({'api_paths': ['test_api2', 'test_api']}, {}, 6),
        ({'summoned_users': ['not_existed', 'not_existed_2']}, {}, 0),
        ({'summoned_users': ['test_login1', 'test_login2']}, {}, 6),
        ({'in_multidraft': True}, {}, 4),
        ({'in_multidraft': False}, {}, 8),
        ({'drafts_ids': [1, 2]}, {}, 2),
        (
            {
                'created_before': '2017-11-01T04:10:00+0300',
                'created_after': '2017-11-01T04:10:00+0300',
            },
            {},
            12,
        ),
        ({'created_by': 'test_user'}, {}, 2),
        ({'authors': ['test_user']}, {}, 2),
        ({'authors': ['test_user', 'test_user2']}, {}, 3),
        ({}, {'tplatform_namespace': 'taxi'}, 5),
        ({}, {'tplatform_namespace': 'lavka'}, 4),
        ({}, {'tplatform_namespace': 'eda'}, 3),
        ({}, {'tplatform_namespace': 'search_portal'}, 0),
        ({}, {'tplatform_namespace': ''}, 12),
    ],
)
@pytest.mark.pgsql('approvals', files=['data.sql'])
async def test_get_drafts_list(
        taxi_approvals_client, query, filters, list_length,
):
    response = await taxi_approvals_client.post(
        '/drafts/list/',
        params=query,
        json=filters,
        headers={'X-Yandex-Login': 'test_login'},
    )
    assert response.status == 200
    content = await response.json()
    assert len(content) == list_length


@pytest.mark.parametrize(
    'filters,list_length', [({}, 2), ({'drafts_ids': [1, 2]}, 2)],
)
@pytest.mark.pgsql('approvals', files=['data.sql'])
async def test_platform_drafts_list(
        taxi_approvals_client, filters, list_length,
):
    response = await taxi_approvals_client.post(
        '/drafts/list/',
        json=filters,
        headers={
            headers_module.X_YANDEX_LOGIN: 'test_login',
            headers_module.X_MULTISERVICES_PLATFORM: 'true',
        },
    )
    assert response.status == 200
    content = await response.json()
    assert len(content) == list_length


@pytest.mark.parametrize(
    'request_data, expected_draft_ids',
    [
        pytest.param(
            {
                'custom_filters': [
                    {'path': 'project_id', 'values': ['1', '2']},
                ],
                'service_name': 'test_service',
                'api_path': 'test_api',
            },
            [1, 4],
            id='test single service_name and api_path',
        ),
        pytest.param(
            {
                'custom_filters': [
                    {'path': 'project_id', 'values': ['1', '2']},
                ],
                'services_names': ['test_service', 'empty_service'],
                'api_paths': ['test_api', 'empty_service_api'],
            },
            [1, 4],
            id='test services_names and api_paths',
        ),
        pytest.param(
            {
                'services_names': ['test_service', 'empty_service'],
                'api_paths': ['test_api', 'empty_service_api'],
            },
            [1, 2, 3, 4],
            id='test with out custom_filters',
        ),
        pytest.param(
            {
                'custom_filters': [{'path': 'project_id', 'values': ['2']}],
                'services_names': ['test_service', 'empty_service'],
                'api_paths': ['test_api', 'empty_service_api'],
            },
            [4],
            id='find by values',
        ),
        pytest.param(
            {
                'custom_filters': [{'path': 'project_id', 'values': ['2']}],
                'service_name': 'test_service',
            },
            [4],
            id='only service_name',
        ),
        pytest.param(
            {
                'custom_filters': [
                    {'path': 'project_id', 'values': ['1', '2']},
                    {'path': 'service_name', 'values': ['some_service']},
                ],
                'service_name': 'test_service',
                'api_path': 'test_api',
            },
            [1, 4],
            id='test list custom_filters, and single service_name',
        ),
        pytest.param(
            {
                'custom_filters': [
                    {'path': 'project_id', 'values': ['1', '2']},
                    {'path': 'service_name', 'values': ['some_service']},
                ],
                'services_names': ['test_service', 'test_service_2'],
                'api_path': 'test_api',
            },
            [1, 4],
            id='single api_path and many custom_filters',
        ),
        pytest.param(
            {
                'custom_filters': [
                    {'path': 'project_id', 'values': ['1', '2']},
                    {'path': 'service_name', 'values': ['some_service']},
                ],
                'services_names': ['test_service', 'test_service_2'],
                'api_paths': ['test_api', 'test_api_2'],
            },
            [1, 4, 5],
            id='many custom_filters',
        ),
        pytest.param(
            {
                'custom_filters': [
                    {'path': 'project_id', 'values': ['1', '2']},
                    {'path': 'service_name', 'values': ['some_service']},
                ],
                'services_names': ['test_service', 'test_service_2'],
                'api_paths': ['test_api', 'test_api_2'],
                'drafts_ids': [1, 5],
            },
            [1, 5],
            id='check intersection draft_ids',
        ),
        pytest.param(
            {
                'custom_filters': [
                    {'path': 'project_id', 'values': ['5']},
                    {'path': 'service_name', 'values': ['not_found']},
                ],
                'services_names': ['test_service', 'test_service_2'],
                'api_paths': ['test_api', 'test_api_2'],
                'drafts_ids': [1, 5],
            },
            [],
            id='check empty filtered_draft_ids',
        ),
        pytest.param(
            {
                'services_names': ['test_service', 'test_service_2'],
                'api_paths': ['test_api', 'test_api_2'],
                'drafts_ids': [],
            },
            [1, 2, 4, 5],
            id='check empty drafts_ids',
        ),
    ],
)
@pytest.mark.pgsql('approvals', files=['drafts_search.sql'])
async def test_search_drafts_by_filters(
        taxi_approvals_client, request_data, expected_draft_ids,
):
    response = await taxi_approvals_client.post(
        '/drafts/list/',
        json=request_data,
        headers={headers_module.X_YANDEX_LOGIN: 'test_login'},
    )
    assert response.status == 200
    content = await response.json()
    draft_ids = [item['id'] for item in content]
    draft_ids.sort()
    expected_draft_ids.sort()
    assert draft_ids == expected_draft_ids
