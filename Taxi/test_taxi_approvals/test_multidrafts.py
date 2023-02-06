import pytest


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
                'version': 3,
                'comments': [],
                'data': {},
                'tickets': [],
                'description': 'descr',
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
async def test_edit_multidraft(
        taxi_approvals_client, draft_id, status, response_data, error_code,
):
    response = await taxi_approvals_client.post(
        f'/multidrafts/edit/?id={draft_id}',
        json={'request_id': 'test-id', 'description': 'descr', 'version': 2},
        headers={'X-Yandex-Login': 'test_user'},
    )
    assert response.status == status
    content = await response.json()
    if response.status == 200:
        assert content.pop('updated')
        assert content == response_data
    else:
        assert content['code'] == error_code


@pytest.mark.parametrize(
    'draft_id,status,error_code',
    [
        (1, 400, 'WRONG_DRAFT_TYPE'),
        (4, 409, 'MULTIDRAFT_NOT_EMPTY'),
        (6, 200, None),
        (-1, 404, 'NOT_FOUND'),
    ],
)
@pytest.mark.pgsql('approvals', files=['data.sql'])
async def test_delete_multidraft(
        taxi_approvals_client, draft_id, status, error_code,
):
    response = await taxi_approvals_client.delete(
        f'/multidrafts/?id={draft_id}',
        headers={'X-Yandex-Login': 'test_user'},
    )
    content = await response.json()
    assert response.status == status, f'{content}'
    if response.status == 200:
        assert content == {}
    else:
        assert content['code'] == error_code


@pytest.mark.parametrize(
    'draft_id,version,attached,status,error_code',
    [
        (1, 1, None, 400, 'WRONG_DRAFT_TYPE'),
        (4, 1, None, 409, 'VERSION_ERROR'),
        (4, 2, None, 409, 'ATTACHED_DRAFTS_NOT_MATCH'),
        (6, 2, None, 200, None),
        (-1, -1, None, 404, 'NOT_FOUND'),
        (
            4,
            2,
            [{'id': 5, 'version': 1}],
            409,
            'ATTACHED_DRAFTS_VERSIONS_NOT_MATCH',
        ),
        (4, 2, [{'id': 6, 'version': 1}], 409, 'ATTACHED_DRAFTS_NOT_MATCH'),
        (
            4,
            2,
            [{'id': 6, 'version': 1}, {'id': 5, 'version': 2}],
            409,
            'ATTACHED_DRAFTS_NOT_MATCH',
        ),
        (4, 2, [{'id': 5, 'version': 2}], 200, None),
    ],
)
@pytest.mark.config(
    APPROVALS_NAMESPACES_CONFIG={'tariff_editor_namespaces': ['taxi']},
)
@pytest.mark.pgsql('approvals', files=['data.sql'])
async def test_v2_delete_multidraft(
        taxi_approvals_client, draft_id, version, status, attached, error_code,
):
    body = {'id': draft_id, 'version': version}
    if attached:
        body['attached'] = attached
    response = await taxi_approvals_client.post(
        f'/v2/multidrafts/delete/',
        json=body,
        headers={'X-Yandex-Login': 'test_user'},
    )
    content = await response.json()
    assert response.status == status, f'{content}'
    if response.status == 200:
        assert content == {}
    else:
        assert content['code'] == error_code, f'{content}'
