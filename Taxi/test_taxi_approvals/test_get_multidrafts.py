import pytest

from taxi_approvals.internal import headers as headers_module


@pytest.mark.parametrize(
    'draft_id,status,response_data,error_code',
    [
        (1, 400, None, 'WRONG_DRAFT_TYPE'),
        (
            4,
            200,
            {
                'id': 4,
                'created_by': 'test_user',
                'created': '2017-11-01T04:10:00+0300',
                'version': 2,
                'comments': [],
                'tickets': [],
                'data': {},
                'description': 'test2',
                'responsibles': ['test_login1'],
                'status': 'need_approval',
                'draft_types': [
                    {'api_path': 'test_api2', 'service_name': 'test_service2'},
                ],
                'approvals': [],
                'scheme_type': 'admin',
            },
            None,
        ),
    ],
)
@pytest.mark.pgsql('approvals', files=['data.sql'])
async def test_get_multidraft(
        taxi_approvals_client, draft_id, status, response_data, error_code,
):
    response = await taxi_approvals_client.get(
        f'/multidrafts/?id={draft_id}',
        headers={headers_module.X_YANDEX_LOGIN: 'test_login'},
    )
    assert response.status == status
    content = await response.json()
    if response.status == 200:
        assert content.pop('updated')
        assert content == response_data
    else:
        assert content['code'] == error_code


@pytest.mark.pgsql('approvals', files=['data.sql'])
async def test_get_good_scheme_admin(taxi_approvals_client):
    response = await taxi_approvals_client.get(
        f'/multidrafts/', params={'id': 4},
    )
    content = await response.json()
    assert response.status == 200, content
    assert content['id'] == 4
    assert content['scheme_type'] == 'admin'


@pytest.mark.pgsql('approvals', files=['data.sql'])
async def test_get_good_scheme_platform(taxi_approvals_client):
    response = await taxi_approvals_client.get(
        f'/multidrafts/',
        params={'id': 20},
        headers={headers_module.X_MULTISERVICES_PLATFORM: 'true'},
    )
    content = await response.json()
    assert response.status == 200, content
    assert content['id'] == 20
    assert content['scheme_type'] == 'platform'


@pytest.mark.parametrize(['draft_id', 'is_platform'], [(4, True), (20, False)])
@pytest.mark.pgsql('approvals', files=['data.sql'])
async def test_get_bad_scheme(taxi_approvals_client, draft_id, is_platform):
    response = await taxi_approvals_client.get(
        f'/multidrafts/',
        params={'id': draft_id},
        headers={
            headers_module.X_MULTISERVICES_PLATFORM: str(is_platform).lower(),
        },
    )
    content = await response.json()
    assert response.status == 400, content
    assert content['code'] == 'WRONG_SCHEME_TYPE'
