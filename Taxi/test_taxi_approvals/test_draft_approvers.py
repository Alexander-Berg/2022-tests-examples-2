import pytest

from taxi_approvals.internal import headers as headers_module
from taxi_approvals.internal import models


@pytest.fixture(name='drafts_approvers')
def _drafts_approvers(taxi_approvals_client):
    async def _request(
            draft_id,
            scheme_type=models.SchemeType.ADMIN,
            tplatform_namespace=None,
    ):
        params = {}
        headers_override = {}
        if tplatform_namespace:
            params['tplatform_namespace'] = tplatform_namespace
        if scheme_type is models.SchemeType.WFM_EFFRAT:
            headers_override = {headers_module.X_YANDEX_UID: 'login'}
        response = await taxi_approvals_client.get(
            f'/drafts/{draft_id}/approvers/',
            headers={
                headers_module.X_DRAFT_SCHEME_TYPE: scheme_type.value,
                headers_module.X_MULTISERVICES_PLATFORM: str(
                    scheme_type == models.SchemeType.PLATFORM,
                ).lower(),
                **headers_override,
            },
            params=params,
        )
        return response

    return _request


@pytest.mark.parametrize(
    'draft_id, expected',
    [
        (
            1,
            {
                'approvers_groups': [
                    {
                        'group_name': 'test_name',
                        'approvals_number': 1,
                        'logins': ['papay', 'test_login_4'],
                    },
                ],
            },
        ),
        (
            3,
            {
                'approvers_groups': [
                    {
                        'group_name': 'test_name',
                        'approvals_number': 1,
                        'logins': ['papay'],
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.config(
    APPROVALS_NAMESPACES_CONFIG={'tariff_editor_namespaces': ['taxi']},
)
@pytest.mark.now('2019-05-14T00:05:00+0000')
@pytest.mark.pgsql('approvals', files=['dyn_perm_approve.sql'])
async def test_draft_approvers_with_dynamic_permission(
        drafts_approvers, draft_id, expected,
):
    response = await drafts_approvers(draft_id)
    content = await response.json()
    assert response.status == 200
    content['approvers_groups'][0]['logins'].sort()
    assert content == expected


@pytest.mark.now('2019-05-14T00:05:00+0000')
@pytest.mark.pgsql('approvals', files=['skip_approved_groups.sql'])
@pytest.mark.parametrize(
    'draft_id, expected',
    [
        (
            1,
            {
                'approvers_groups': [
                    {
                        'group_name': 'developers',
                        'approvals_number': 1,
                        'logins': ['papay', 'test_developer'],
                    },
                ],
            },
        ),
        (
            2,
            {
                'approvers_groups': [
                    {
                        'approvals_number': 1,
                        'group_name': 'developers',
                        'logins': ['papay', 'test_developer'],
                    },
                    {
                        'approvals_number': 1,
                        'group_name': 'managers',
                        'logins': ['papay', 'test_manager'],
                    },
                ],
            },
        ),
    ],
)
async def test_draft_delete_approvers(drafts_approvers, draft_id, expected):
    response = await drafts_approvers(draft_id)
    content = await response.json()
    assert response.status == 200
    for i in range(len(content['approvers_groups'])):
        content['approvers_groups'][i]['logins'].sort()
    content['approvers_groups'] = sorted(
        content['approvers_groups'], key=lambda x: x['group_name'],
    )
    assert content == expected


@pytest.mark.pgsql('approvals', files=['data.sql'])
async def test_platform_approvers(drafts_approvers, grands_retrieve_mock):
    mock = grands_retrieve_mock()
    response = await drafts_approvers(
        19, scheme_type=models.SchemeType.PLATFORM, tplatform_namespace='eda',
    )
    content = await response.json()
    assert response.status == 200, content
    for i in range(len(content['approvers_groups'])):
        content['approvers_groups'][i]['logins'].sort()
    assert content == {
        'approvers_groups': [
            {
                'approvals_number': 1,
                'group_name': 'test_name',
                'logins': ['some_man', 'superuser'],
            },
        ],
    }
    assert mock.times_called == 1


@pytest.mark.config(
    BANK_ROLES_CHECKER_APPROVE_RULES={
        'test': {
            'map_to_slug_paths': {'^BANK.+': {'slug_paths': ['test/path']}},
            'slug_paths_if_no_rule': ['superuser'],
        },
    },
)
@pytest.mark.pgsql('approvals', files=['data.sql'])
async def test_bank_approvers(drafts_approvers, bank_idm_mock):
    response = await drafts_approvers(23, scheme_type=models.SchemeType.BANK)
    content = await response.json()
    assert response.status == 200, content
    assert content == {
        'approvers_groups': [
            {
                'approvals_number': 1,
                'group_name': 'test_name',
                'logins': ['test_user'],
            },
        ],
    }
    assert bank_idm_mock.get_user_roles.times_called == 0
    assert bank_idm_mock.get_logins.times_called == 1


@pytest.mark.pgsql('approvals', files=['data.sql'])
async def test_wfm_effrat_approvers(drafts_approvers, access_control_mock):
    response = await drafts_approvers(
        22, scheme_type=models.SchemeType.WFM_EFFRAT,
    )
    content = await response.json()
    assert response.status == 200, content
    assert content == {
        'approvers_groups': [
            {
                'approvals_number': 1,
                'group_name': 'test_name',
                'logins': ['uid1'],
            },
        ],
    }
    assert access_control_mock.check_users.times_called == 1
