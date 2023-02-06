import json

import pytest

from taxi_approvals.internal import headers as headers_module
from taxi_approvals.internal import models


@pytest.fixture(name='drafts_approval')
def _drafts_approval(taxi_approvals_client):
    async def _request(
            draft_id,
            data,
            login,
            scheme_type=models.SchemeType.ADMIN,
            tplatform_namespace=None,
    ):
        params = {}
        headers_override = {}
        if tplatform_namespace:
            params['tplatform_namespace'] = tplatform_namespace
        if scheme_type is models.SchemeType.WFM_EFFRAT:
            headers_override = {headers_module.X_YANDEX_UID: login}
        response = await taxi_approvals_client.put(
            f'/drafts/{draft_id}/approval/',
            data=json.dumps(data),
            headers={
                headers_module.X_YANDEX_LOGIN: login,
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
    'draft_id,data,expected,login',
    [
        (1, {}, 'approvals_expected.json', 'test_login'),
        (1, {'version': 1}, 'approvals_expected.json', 'test_login'),
        (
            1,
            {'version': 42},
            {'status': 409, 'code': 'VERSION_ERROR'},
            'test_login',
        ),
        (
            1,
            {'version': 1},
            'approve_by_author_with_dyn_perm.json',
            'test_user',
        ),
        (
            9,
            {'version': 1},
            'approve_by_author_group_is_not_audit.json',
            'test_login_5',
        ),
        (
            10,
            {'version': 1},
            {'status': 403, 'code': 'CANNOT_APPROVE'},
            'test_login_5',
        ),
        (
            11,
            {'version': 1},
            'approve_by_author_group_is_audit.json',
            'test_login_5',
        ),
        (11, {'version': 1}, 'test_superuser.json', 'papay'),
        (12, {'version': 2}, 'non_existent_group_test.json', 'papay'),
        (14, {'version': 2}, {'status': 403, 'code': 'DRAFT_ERROR'}, 'papay'),
    ],
)
@pytest.mark.pgsql('approvals', files=['edit.sql'])
@pytest.mark.usefixtures('stq_put_mock')
@pytest.mark.config(
    USE_NEW_DYNAMIC_FLOW=True,
    APPROVALS_NAMESPACES_CONFIG={'tariff_editor_namespaces': ['taxi']},
)
@pytest.mark.now('2017-11-01T01:10:00+0300')
async def test_approvals(
        drafts_approval, load, draft_id, data, expected, login,
):
    response = await drafts_approval(draft_id, data, login)
    content = await response.json()
    if response.status == 200:
        expected = json.loads(load(expected))
        content.pop('updated')
        assert content == expected
    else:
        assert response.status == expected['status'], content
        assert content['code'] == expected['code']


@pytest.mark.pgsql('approvals', files=['edit.sql'])
@pytest.mark.usefixtures('stq_put_mock')
@pytest.mark.config(
    USE_NEW_DYNAMIC_FLOW=True,
    APPROVALS_NAMESPACES_CONFIG={'tariff_editor_namespaces': ['taxi']},
    APPROVALS_FREEZE_SETTINGS={'enabled': True, 'allowed_draft_ids': [9]},
)
@pytest.mark.now('2017-11-01T01:10:00+0300')
async def test_freeze_approval_error(drafts_approval):
    response = await drafts_approval(1, {'version': 1}, 'test_login')
    content = await response.json()
    assert response.status == 400, content
    assert content == {
        'code': 'APPROVALS_FREEZE_CHECK_FAILED',
        'message': (
            'There is a deployment freeze. Drafts\' apply is disabled. \n'
            'If you want to make this change, you need to add draft id 1 to '
            'APPROVALS_FREEZE_SETTINGS config'
        ),
        'status': 'error',
    }


@pytest.mark.pgsql('approvals', files=['edit.sql'])
@pytest.mark.usefixtures('stq_put_mock')
@pytest.mark.config(
    USE_NEW_DYNAMIC_FLOW=True,
    APPROVALS_NAMESPACES_CONFIG={'tariff_editor_namespaces': ['taxi']},
    APPROVALS_FREEZE_SETTINGS={'enabled': True, 'allowed_draft_ids': [9]},
)
@pytest.mark.now('2017-11-01T01:10:00+0300')
async def test_freeze_approval_ok(drafts_approval):
    response = await drafts_approval(9, {'version': 1}, 'test_login')
    content = await response.json()
    assert response.status == 200, content


@pytest.mark.pgsql('approvals', files=['edit.sql'])
@pytest.mark.usefixtures('stq_put_mock')
async def test_platform_approvals(drafts_approval, grands_retrieve_mock):
    mock = grands_retrieve_mock()
    response = await drafts_approval(
        16,
        {},
        'superuser',
        scheme_type=models.SchemeType.PLATFORM,
        tplatform_namespace='taxi',
    )
    content = await response.json()
    assert response.status == 200, content
    assert content['id'] == 16
    assert content['scheme_type'] == models.SchemeType.PLATFORM.value
    assert content['status'] == 'approved'
    assert mock.times_called == 1


@pytest.mark.pgsql('approvals', files=['edit.sql'])
@pytest.mark.usefixtures('stq_put_mock')
async def test_bad_platform_approvals(drafts_approval, grands_retrieve_mock):
    mock = grands_retrieve_mock()
    response = await drafts_approval(
        16,
        {},
        'some_man',
        scheme_type=models.SchemeType.PLATFORM,
        tplatform_namespace='taxi',
    )
    content = await response.json()
    assert response.status == 403, content
    assert content == {
        'code': 'NO_PERMISSION_ERROR',
        'message': 'User has no permission to perform this action',
        'status': 'error',
    }
    assert mock.times_called == 1


@pytest.mark.pgsql('approvals', files=['edit.sql'])
async def test_bank_approvals(drafts_approval, bank_idm_mock):
    response = await drafts_approval(
        17, {}, 'test_user', scheme_type=models.SchemeType.BANK,
    )
    content = await response.json()
    assert response.status == 200, content
    assert content['id'] == 17
    assert content['scheme_type'] == 'bank'
    assert content['status'] == 'approved'
    assert bank_idm_mock.get_user_roles.times_called == 1
    assert bank_idm_mock.get_logins.times_called == 0


@pytest.mark.config(
    BANK_ROLES_CHECKER_APPROVE_RULES={
        'test': {
            'map_to_slug_paths': {'^BANK.+': {'slug_paths': ['test/path']}},
            'slug_paths_if_no_rule': ['cpp_manager'],
        },
    },
)
@pytest.mark.parametrize(
    'login, found', [('test_user', True), ('test_user_second', False)],
)
@pytest.mark.pgsql('approvals', files=['data.sql'])
async def test_bank_approvals_by_rule(
        drafts_approval, bank_idm_mock, login, found,
):
    response = await drafts_approval(
        23, {}, login, scheme_type=models.SchemeType.BANK,
    )
    content = await response.json()
    if found:
        assert response.status == 200, content
        assert content['id'] == 23
        assert content['scheme_type'] == 'bank'
        assert content['status'] == 'approved'
    else:
        assert content == {
            'code': 'NO_PERMISSION_ERROR',
            'message': 'User has no permission to perform this action',
            'status': 'error',
        }
    assert bank_idm_mock.get_user_roles.times_called == 1
    assert bank_idm_mock.get_logins.times_called == 0


@pytest.mark.pgsql('approvals', files=['edit.sql'])
async def test_bad_bank_approvals(drafts_approval, bank_idm_mock):
    response = await drafts_approval(
        17, {}, 'bad_user', scheme_type=models.SchemeType.BANK,
    )
    assert response.status == 403
    assert bank_idm_mock.get_user_roles.times_called == 1
    assert bank_idm_mock.get_logins.times_called == 0


@pytest.mark.pgsql('approvals', files=['data.sql'])
async def test_bad_bank_approvals_rule(drafts_approval, bank_idm_mock):
    response = await drafts_approval(
        24, {}, 'test_user', scheme_type=models.SchemeType.BANK,
    )
    content = await response.json()
    assert response.status == 403
    assert content['code'] == 'INVALID_FIELD_FOR_RULE'
    assert bank_idm_mock.get_user_roles.times_called == 0
    assert bank_idm_mock.get_logins.times_called == 0


@pytest.mark.pgsql('approvals', files=['edit.sql'])
async def test_wfm_effrat_approvals(drafts_approval, access_control_mock):
    response = await drafts_approval(
        18, {}, 'uid1', scheme_type=models.SchemeType.WFM_EFFRAT,
    )
    content = await response.json()
    assert response.status == 200, content
    assert content['id'] == 18
    assert content['scheme_type'] == 'wfm_effrat'
    assert content['status'] == 'approved'
    assert access_control_mock.check_users.times_called == 1


@pytest.mark.pgsql('approvals', files=['edit.sql'])
async def test_bad_wfm_effrat_approvals(drafts_approval, access_control_mock):
    response = await drafts_approval(
        18, {}, 'user2', scheme_type=models.SchemeType.WFM_EFFRAT,
    )
    assert response.status == 403
    assert access_control_mock.check_users.times_called == 1
