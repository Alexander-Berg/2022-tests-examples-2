import json

import pytest

from taxi_approvals.internal import headers as headers_module
from taxi_approvals.internal import models


@pytest.fixture(name='v2_drafts_reject')
def _v2_drafts_reject(taxi_approvals_client):
    async def _request(
            draft_id,
            service_name=None,
            login='test_login',
            scheme_type=models.SchemeType.ADMIN,
            tplatform_namespace=None,
    ):
        data = {'draft_id': draft_id, 'comment': 'test'}
        if service_name:
            data['service_name'] = service_name
        params = {}
        if tplatform_namespace:
            params['tplatform_namespace'] = tplatform_namespace
        response = await taxi_approvals_client.post(
            '/v2/drafts/reject/',
            json=data,
            params=params,
            headers={
                headers_module.X_YANDEX_LOGIN: login,
                headers_module.X_DRAFT_SCHEME_TYPE: scheme_type.value,
                headers_module.X_MULTISERVICES_PLATFORM: str(
                    scheme_type == models.SchemeType.PLATFORM,
                ).lower(),
            },
        )
        return response

    return _request


@pytest.mark.parametrize(
    'draft_id,service_name,expected',
    [
        (1, None, 'reject_expected_1.json'),
        (2, 'test_service', 'reject_expected_2.json'),
    ],
)
@pytest.mark.pgsql('approvals', files=['reject.sql'])
@pytest.mark.now('2017-11-01T01:10:00+0300')
async def test_reject(
        draft_id, service_name, expected, v2_drafts_reject, load,
):
    response = await v2_drafts_reject(
        draft_id, service_name, tplatform_namespace='taxi',
    )
    content = await response.json()
    assert response.status == 200
    assert content.pop('updated')
    expected = json.loads(load(expected))
    assert content == expected


@pytest.mark.pgsql('approvals', files=['reject.sql'])
async def test_platform_reject(v2_drafts_reject, grands_retrieve_mock):
    mock = grands_retrieve_mock()
    response = await v2_drafts_reject(
        3,
        login='superuser',
        scheme_type=models.SchemeType.PLATFORM,
        tplatform_namespace='taxi',
    )
    content = await response.json()
    assert response.status == 200, content
    assert content['id'] == 3
    assert content['scheme_type'] == 'platform'
    assert content['status'] == 'rejected'
    assert mock.times_called == 1


@pytest.mark.pgsql('approvals', files=['reject.sql'])
async def test_bad_platform_reject(v2_drafts_reject, grands_retrieve_mock):
    mock = grands_retrieve_mock()
    response = await v2_drafts_reject(
        3,
        login='some_man',
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


@pytest.mark.pgsql('approvals', files=['reject.sql'])
async def test_bank_approvals(v2_drafts_reject, bank_idm_mock):
    response = await v2_drafts_reject(
        4, {}, 'test_user', scheme_type=models.SchemeType.BANK,
    )
    content = await response.json()
    assert response.status == 200, content
    assert content['id'] == 4
    assert content['scheme_type'] == 'bank'
    assert content['status'] == 'rejected'
    assert bank_idm_mock.get_user_roles.times_called == 1
    assert bank_idm_mock.get_logins.times_called == 0


@pytest.mark.pgsql('approvals', files=['reject.sql'])
async def test_bad_bank_approvals(v2_drafts_reject, bank_idm_mock):
    response = await v2_drafts_reject(
        4, {}, 'bad_user', scheme_type=models.SchemeType.BANK,
    )
    assert response.status == 403
    assert bank_idm_mock.get_user_roles.times_called == 1
    assert bank_idm_mock.get_logins.times_called == 0
