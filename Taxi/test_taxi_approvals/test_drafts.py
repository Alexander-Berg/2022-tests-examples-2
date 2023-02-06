import json

import pytest

from taxi_approvals import queries as query
from taxi_approvals.api import drafts as drafts_module
from taxi_approvals.internal import audit_log as a_log


@pytest.mark.pgsql('approvals', files=['draft_apply_and_finish_time.sql'])
async def test_get_drafts_list__start_and_finish_apply_time(
        taxi_approvals_client,
):
    response = await taxi_approvals_client.post(
        '/drafts/list/', json={}, headers={'X-Yandex-Login': 'test_login'},
    )
    assert response.status == 200
    drafts = await response.json()

    assert drafts[0]['start_apply_time'] == '2017-11-01T04:15:00+0300'
    assert drafts[0]['finish_apply_time'] == '2017-11-01T04:15:55+0300'

    assert 'start_apply_time' not in drafts[2]
    assert 'finish_apply_time' not in drafts[2]


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                APPROVALS_NAMESPACES_CONFIG={
                    'tariff_editor_namespaces': ['taxi', 'market'],
                },
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                APPROVALS_NAMESPACES_CONFIG={'tariff_editor_namespaces': []},
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    'draft_url, should_be_non_empty',
    [
        pytest.param('/drafts/1/?tplatform_namespace=taxi', True),
        pytest.param(
            '/v2/drafts/?id=1&service_name=lolka&tplatform_namespace=taxi',
            True,
        ),
        pytest.param('/drafts/2/?tplatform_namespace=taxi', False),
        pytest.param('/v2/drafts/?id=2&tplatform_namespace=taxi', False),
        pytest.param(
            '/drafts/3/?tplatform_namespace=lavka',
            True,
            id='draft_has_not_schema',
        ),
        pytest.param(
            '/v2/drafts/?id=3&tplatform_namespace=lavka',
            True,
            id='draft_has_not_schema',
        ),
        pytest.param('/drafts/4/', True, id='draft_has_not_api_path'),
        pytest.param('/v2/drafts/?id=4', True, id='draft_has_not_api_path'),
    ],
)
@pytest.mark.pgsql('approvals', files=['draft_apply_and_finish_time.sql'])
async def test_draft_get_start_and_finish_apply_time(
        taxi_approvals_client, draft_url, should_be_non_empty,
):
    response = await taxi_approvals_client.get(
        draft_url, json={}, headers={'X-Yandex-Login': 'test_login'},
    )
    assert response.status == 200
    draft = await response.json()

    if should_be_non_empty:
        assert draft['start_apply_time'] == '2017-11-01T04:15:00+0300'
        assert draft['finish_apply_time'] == '2017-11-01T04:15:55+0300'
    else:
        assert 'start_apply_time' not in draft
        assert 'finish_apply_time' not in draft


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                APPROVALS_NAMESPACES_CONFIG={
                    'tariff_editor_namespaces': ['lavka', 'eda'],
                },
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                APPROVALS_NAMESPACES_CONFIG={'tariff_editor_namespaces': []},
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    'params, status, code',
    [
        pytest.param({'id': 1, 'tplatform_namespace': 'taxi'}, 200, None),
        pytest.param({'id': 3, 'tplatform_namespace': 'lavka'}, 200, None),
        pytest.param({'id': 4}, 200, None),
        pytest.param(
            {'id': 144, 'tplatform_namespace': 'taxi'}, 404, 'NOT_FOUND',
        ),
        pytest.param({'id': 1}, 400, 'TPLATFORM_NAMESPACE_QUERY_EMPTY'),
        pytest.param(
            {'id': 1, 'tplatform_namespace': 'market'},
            400,
            'TPLATFORM_NAMESPACE_MISMATCH',
        ),
        pytest.param({'id': 'Bad_value'}, 400, 'VALUE_ERROR'),
        pytest.param({}, 400, 'ID_FIELD_ERROR'),
    ],
)
@pytest.mark.pgsql('approvals', files=['draft_apply_and_finish_time.sql'])
async def test_draft_get_short_info(
        taxi_approvals_client, params, status, code,
):
    response = await taxi_approvals_client.get(
        '/v2/drafts/short_info/',
        json=None,
        params=params,
        headers={'X-Yandex-Login': 'test_login'},
    )
    assert response.status == status
    draft = await response.json()
    if response.status == 200:
        assert draft['api_path']
        assert draft['service_name']
    else:
        assert draft['code'] == code


@pytest.mark.config(
    APPROVALS_NAMESPACES_CONFIG={'tariff_editor_namespaces': ['taxi']},
)
@pytest.mark.pgsql('approvals', files=['data.sql'])
async def test_comments(taxi_approvals_client):
    response = await taxi_approvals_client.post(
        '/drafts/1/comment/',
        data=json.dumps({'comment': 'hiii'}),
        headers={'X-Yandex-Login': 'test_login'},
    )
    assert response.status == 200
    content = await response.json()
    assert content['comments'] == [
        {'login': 'asd', 'comment': 'ert'},
        {'login': 'test_login', 'comment': 'hiii'},
    ]


DYN_DRAFT_RESULT = {
    'created_by': 'test_user',
    'description': 'test',
    'created': '2017-11-01T04:10:00+0300',
    'run_manually': False,
    'service_name': 'test_service',
    'api_path': 'test/api/new',
    'approvals': [
        {
            'created': '2017-11-01T01:10:00+0300',
            'group': 'test_name',
            'login': 'test_login',
        },
    ],
    'version': 2,
    'comments': [],
    'id': 1,
    'status': 'approved',
    'mode': 'poll',
    'change_doc_id': '234',
    'tickets': [],
    'summary': {},
    'object_id': 'test_service:test/api/new',
    'errors': [],
    'headers': {},
    'query_params': {},
    'scheme_type': 'admin',
}


@pytest.mark.parametrize(
    'params',
    [({'meta_data': 'item_name_1'}), ({'existing_param': 'some_value'})],
)
@pytest.mark.config(
    USE_NEW_DYNAMIC_FLOW=True,
    APPROVALS_NAMESPACES_CONFIG={'tariff_editor_namespaces': ['taxi']},
)
@pytest.mark.pgsql('approvals', files=['dyn_perm.sql'])
@pytest.mark.now('2017-11-01T01:10:00+0300')
async def test_dynamic_permissions(taxi_approvals_client, params):
    response = await taxi_approvals_client.put(
        '/drafts/1/approval/',
        headers={'X-Yandex-Login': 'test_login'},
        json={},
        params=params,
    )
    assert response.status == 200
    content = await response.json()
    content.pop('updated')
    content.pop('data')
    assert content == DYN_DRAFT_RESULT


@pytest.mark.pgsql('approvals', files=['dyn_perm.sql'])
@pytest.mark.now('2017-11-01T01:10:00+0300')
@pytest.mark.config(
    USE_NEW_DYNAMIC_FLOW=True,
    APPROVALS_NAMESPACES_CONFIG={'tariff_editor_namespaces': ['taxi']},
)
async def test_new_dynamic_permissions(taxi_approvals_client):
    response = await taxi_approvals_client.put(
        '/drafts/1/approval/',
        headers={'X-Yandex-Login': 'test_login'},
        json={'other_meta_data': 'other_item_name_1'},
        params={'meta_data': 'item_name_1'},
    )
    assert response.status == 200
    content = await response.json()
    content.pop('updated')
    content.pop('data')
    assert content == DYN_DRAFT_RESULT


@pytest.mark.pgsql('approvals', files=['dyn_perm.sql'])
@pytest.mark.now('2017-11-01T01:10:00+0300')
@pytest.mark.config(
    USE_NEW_DYNAMIC_FLOW=True,
    APPROVALS_NAMESPACES_CONFIG={'tariff_editor_namespaces': ['taxi']},
)
@pytest.mark.parametrize(
    'login,draft_id,is_ok',
    [
        ('test_login', '1', True),
        ('test_login', '1', True),
        ('test_login_3', '1', True),
        ('test_login_3', '2', False),
    ],
)
async def test_both_permissions(taxi_approvals_client, login, draft_id, is_ok):
    await _test_both_permissions(taxi_approvals_client, login, draft_id, is_ok)


@pytest.mark.pgsql('approvals', files=['dyn_perm.sql'])
@pytest.mark.now('2017-11-01T01:10:00+0300')
@pytest.mark.config(
    USE_NEW_DYNAMIC_FLOW=True,
    APPROVALS_NAMESPACES_CONFIG={'tariff_editor_namespaces': ['taxi']},
)
@pytest.mark.parametrize(
    'login,draft_id,is_ok',
    [
        ('test_login', '1', True),
        ('test_login', '1', True),
        ('test_login_3', '1', True),
        ('test_login_3', '2', False),
        ('test_login_3', '3', True),  # user has the default dyn permission
        ('test_login_4', '3', False),  # user hasn't the default dyn permission
    ],
)
async def test_both_permissions_new(
        taxi_approvals_client, login, draft_id, is_ok,
):
    await _test_both_permissions(taxi_approvals_client, login, draft_id, is_ok)


async def _test_both_permissions(
        taxi_approvals_client, login, draft_id, is_ok,
):
    response = await taxi_approvals_client.put(
        f'/drafts/{draft_id}/approval/',
        headers={'X-Yandex-Login': login},
        json={},
        params={'meta_data': 'item_name_1'},
    )
    content = await response.json()
    if is_ok:
        assert response.status == 200
    else:
        assert response.status == 403
        assert content['code'] == 'NO_PERMISSION_ERROR'


@pytest.mark.parametrize(
    'comment',
    [
        pytest.param('test comment', id='with_comment'),
        pytest.param(None, id='no_comment'),
    ],
)
@pytest.mark.parametrize(
    'finish_status,errors',
    [('succeeded', None), ('failed', [{'message': 'Error random message'}])],
)
@pytest.mark.config(
    APPROVALS_NAMESPACES_CONFIG={'tariff_editor_namespaces': ['taxi']},
)
@pytest.mark.pgsql('approvals', files=['edit.sql'])
async def test_draft_finish(
        finish_status, errors, comment, taxi_approvals_client, patch,
):
    @patch('taxi_approvals.internal.audit_log.audit_log')
    async def audit_log(status, applying_doc, applying_data, ticket, *, app):
        audit_action_id = a_log.get_audit_action_id(applying_doc, app)
        assert audit_action_id == 'test_apply_audit_action_id'

    req_body = {'final_status': finish_status}
    if comment:
        req_body['comment'] = comment
    if errors:
        req_body['errors'] = errors
    response = await taxi_approvals_client.post(
        '/drafts/2/finish/',
        json=req_body,
        headers={'X-Yandex-Login': 'script_robot'},
    )

    assert response.status == 200
    if req_body['final_status'] == 'succeeded':
        assert len(audit_log.calls) == 1
    else:
        assert not audit_log.calls

    content = await response.json()
    assert content['status'] == finish_status
    if finish_status == 'failed':
        assert content['errors'] == errors

    if comment:
        assert {'login': 'script_robot', 'comment': comment} in content[
            'comments'
        ]


@pytest.mark.parametrize(
    'data,expected',
    [
        (
            [{'id': 1000, 'version': 1}, {'id': 2, 'version': 1}],
            {
                'approved': [],
                'not_approved': [
                    {
                        'id': 1000,
                        'version': 1,
                        'reason': (
                            'Draft with id=1000 and version=1 was not found'
                        ),
                    },
                    {
                        'id': 2,
                        'version': 1,
                        'reason': (
                            'Draft with id=2 and version=1 was not found'
                        ),
                    },
                ],
            },
        ),
        (
            [{'id': 1, 'version': 1}, {'id': 2, 'version': 2}],
            {
                'approved': [
                    {
                        'created_by': 'test_user',
                        'description': 'test',
                        'created': '2017-11-01T04:10:00+0300',
                        'run_manually': False,
                        'service_name': 'test_service',
                        'api_path': 'test_api',
                        'data': {'test_key': 'test_value'},
                        'approvals': [
                            {
                                'created': '2017-11-01T01:10:00+0300',
                                'group': 'test_name',
                                'login': 'test_login',
                            },
                        ],
                        'version': 2,
                        'comments': [],
                        'errors': [],
                        'id': 1,
                        'headers': {},
                        'query_params': {},
                        'status': 'approved',
                        'mode': 'push',
                        'change_doc_id': '234',
                        'ticket': 'TAXIRATE-35',
                        'tickets': ['TAXIRATE-35'],
                        'tplatform_namespace': 'taxi',
                        'deferred_apply': '2017-11-01T04:10:00+0300',
                        'summary': {},
                        'object_id': 'test_service:test_api',
                        'scheme_type': 'admin',
                    },
                ],
                'not_approved': [
                    {
                        'id': 2,
                        'version': 2,
                        'reason': 'Draft is not in need_approval status',
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.config(
    APPROVALS_NAMESPACES_CONFIG={'tariff_editor_namespaces': ['taxi']},
)
@pytest.mark.pgsql('approvals', files=['edit.sql'])
@pytest.mark.now('2017-11-01T01:10:00+0300')
async def test_add_approvals(patch, data, expected, taxi_approvals_client):
    @patch('taxi.stq.client.put')
    async def _put(*args, **kwargs):
        pass

    response = await taxi_approvals_client.put(
        '/drafts/bulk_approval/',
        json={'drafts': data},
        headers={'X-Yandex-Login': 'test_login'},
    )
    assert response.status == 200
    content = await response.json()
    for item in content['approved']:
        assert item.pop('updated')
    assert content == expected


@pytest.mark.parametrize(
    'draft_id,expected_status,expected',
    [
        (
            7,
            200,
            {
                'id': 7,
                'created_by': 'test_user',
                'comments': [],
                'created': '2017-11-01T04:10:00+0300',
                'description': 'test',
                'approvals': [],
                'status': 'need_approval',
                'version': 2,
                'run_manually': False,
                'service_name': 'test_service',
                'api_path': 'test_api',
                'data': {'test_key': 'test_value'},
                'mode': 'push',
                'change_doc_id': '239',
                'tickets': ['TAXIRATE-35'],
                'summary': {},
                'deferred_apply': '2017-11-01T04:10:00+0300',
                'errors': [],
                'headers': {},
                'query_params': {},
                'ticket': 'TAXIRATE-35',
                'tplatform_namespace': 'taxi',
                'object_id': 'test_service:test_api',
                'scheme_type': 'admin',
            },
        ),
        (8, 409, 'WRONG_STATUS'),
        (14, 403, 'DRAFT_ERROR'),
    ],
)
@pytest.mark.config(
    APPROVALS_NAMESPACES_CONFIG={'tariff_editor_namespaces': ['taxi']},
)
@pytest.mark.pgsql('approvals', files=['edit.sql'])
@pytest.mark.now('2017-11-01T01:10:00+0300')
async def test_delete_approvals(
        draft_id, expected, expected_status, taxi_approvals_client,
):
    response = await taxi_approvals_client.delete(
        f'/drafts/{draft_id}/approval/',
        headers={'X-Yandex-Login': 'test_login'},
    )
    assert response.status == expected_status
    if expected_status == 200:
        content = await response.json()
        content.pop('updated')
        assert content == expected
    else:
        content = await response.json()
        assert content['code'] == expected, content


@pytest.mark.parametrize(
    'data,expected_len,expected_status,error_code',
    [
        (
            [{'id': 1000, 'version': 1}, {'id': 2, 'version': 1}],
            None,
            404,
            'SOME_DRAFTS_NOT_FOUND',
        ),
        (
            [{'id': 2, 'version': 2}, {'id': 1, 'version': 1}],
            None,
            404,
            'MULTIDRAFT_WAS_NOT_FOUND',
        ),
        ([{'id': 8, 'version': 1}, {'id': 9, 'version': 1}], 2, 200, None),
        (
            [{'id': 7, 'version': 1}, {'id': 9, 'version': 1}],
            None,
            400,
            'SEVERAL_MULTIDRAFT_ID',
        ),
        ([{'id': 3, 'version': 2}], None, 404, 'MULTIDRAFT_WAS_NOT_FOUND'),
    ],
)
@pytest.mark.config(
    APPROVALS_NAMESPACES_CONFIG={
        'tariff_editor_namespaces': ['taxi', 'lavka'],
    },
)
@pytest.mark.pgsql('approvals', files=['data.sql'])
@pytest.mark.now('2017-11-01T01:10:00+0300')
async def test_add_strict_approvals(
        patch,
        data,
        expected_len,
        expected_status,
        error_code,
        taxi_approvals_client,
):
    @patch('taxi.stq.client.put')
    async def _put(*args, **kwargs):
        pass

    response = await taxi_approvals_client.put(
        '/drafts/bulk_strict_approval/',
        json={'drafts': data},
        headers={'X-Yandex-Login': 'test_login'},
    )
    content = await response.json()
    assert response.status == expected_status, f'Content: {content}'
    if response.status == 200:
        assert list(content.keys()) == ['approved']
        assert len(content['approved']) == expected_len, f'Content: {content}'
    else:
        assert content['code'] == error_code


@pytest.mark.parametrize(
    'data,expected_len,expected_status,error_code',
    [
        (
            [{'id': 8, 'version': 1}, {'id': 9, 'version': 1}],
            None,
            400,
            'MULTIDRAFT_UPDATE_ERROR',
        ),
    ],
)
@pytest.mark.config(
    APPROVALS_NAMESPACES_CONFIG={
        'tariff_editor_namespaces': ['taxi', 'lavka'],
    },
)
@pytest.mark.pgsql('approvals', files=['data.sql'])
@pytest.mark.now('2017-11-01T01:10:00+0300')
async def test_add_strict_approvals_custom(
        patch,
        data,
        expected_len,
        expected_status,
        error_code,
        taxi_approvals_client,
):
    @patch('taxi.stq.client.put')
    async def _put(*args, **kwargs):
        pass

    # pylint: disable=protected-access
    original = drafts_module._collect_draft_for_approval

    @patch('taxi_approvals.api.drafts._collect_draft_for_approval')
    async def _collect_draft_for_approval(
            request, drafts_list, *, raise_on_error,
    ):
        pool = request.app['pool']
        async with pool.acquire() as connection:

            await connection.fetchrow(
                query.UPDATE_MULTIDRAFT_VERSION_BY_ID, 3, 10, 2,
            )
        return await original(
            request, drafts_list, raise_on_error=raise_on_error,
        )

    response = await taxi_approvals_client.put(
        '/drafts/bulk_strict_approval/',
        json={'drafts': data},
        headers={'X-Yandex-Login': 'test_login'},
    )
    content = await response.json()
    assert response.status == expected_status, f'Content: {content}'
    if response.status == 200:
        assert list(content.keys()) == ['approved']
        assert len(content['approved']) == expected_len, f'Content: {content}'
    else:
        assert content['code'] == error_code


@pytest.mark.parametrize(
    'data,expected',
    [
        (
            {
                'drafts': [
                    {'id': 1000, 'version': 1},
                    {'id': 2, 'version': 1},
                ],
                'comment': 'test',
            },
            'rejects_expected_1.json',
        ),
        (
            {
                'drafts': [
                    {'id': 1, 'version': 1},
                    {'id': 2, 'version': 2},
                    {'id': 4, 'version': 2},
                    {'id': 5, 'version': 1},
                ],
                'comment': 'test',
            },
            'rejects_expected_2.json',
        ),
    ],
)
@pytest.mark.config(
    APPROVALS_NAMESPACES_CONFIG={'tariff_editor_namespaces': ['taxi']},
)
@pytest.mark.pgsql('approvals', files=['edit.sql'])
@pytest.mark.now('2017-11-01T01:10:00+0300')
async def test_rejects(patch, data, expected, taxi_approvals_client, load):
    @patch('taxi.stq.client.put')
    async def _put(*args, **kwargs):
        pass

    response = await taxi_approvals_client.post(
        '/drafts/bulk_reject/',
        json=data,
        headers={'X-Yandex-Login': 'test_login'},
    )
    content = await response.json()
    assert response.status == 200
    for item in content['rejected']:
        assert item.pop('updated')
    expected = json.loads(load(expected))
    assert content == expected


@pytest.mark.config(
    APPROVALS_NAMESPACES_CONFIG={'tariff_editor_namespaces': ['taxi']},
)
@pytest.mark.pgsql('approvals', files=['draft_apply_and_finish_time.sql'])
@pytest.mark.now('2017-11-01T01:10:00+0300')
async def test_manual_apply__start_and_finish_time(
        taxi_approvals_client, patch,
):
    @patch('taxi_approvals.internal.audit_log.audit_log')
    async def _audit_log(status, applying_doc, applying_data, ticket, *, app):
        audit_action_id = a_log.get_audit_action_id(applying_doc, app)
        assert audit_action_id == 'test_apply_audit_action_id'

    apply_response = await taxi_approvals_client.post(
        '/drafts/2/manual_apply/',
        json={},
        headers={'X-Yandex-Login': 'test_user2'},
    )
    assert apply_response.status == 200

    finish_response = await taxi_approvals_client.post(
        '/drafts/2/finish/',
        json={'final_status': 'succeeded'},
        headers={'X-Yandex-Login': 'test_user2'},
    )
    assert finish_response.status == 200

    draft = await finish_response.json()
    assert draft['start_apply_time'] == '2017-11-01T01:10:00+0300'
    assert draft['finish_apply_time'] == '2017-11-01T01:10:00+0300'


@pytest.mark.parametrize(
    'data,expected',
    [
        (
            {'drafts': [{'id': 1000, 'version': 1}, {'id': 4, 'version': 2}]},
            {
                'applied': [
                    {
                        'api_path': 'test_api2',
                        'approvals': [],
                        'change_doc_id': '237',
                        'comments': [
                            {'comment': 'meow', 'login': 'test_login'},
                        ],
                        'created': '2017-11-01T04:10:00+0300',
                        'created_by': 'test_user2',
                        'data': {},
                        'deferred_apply': '2017-11-01T04:10:00+0300',
                        'description': 'test2',
                        'errors': [],
                        'headers': {},
                        'query_params': {},
                        'id': 4,
                        'mode': 'poll',
                        'multidraft_id': 3,
                        'object_id': 'test_service:test_api2',
                        'run_manually': True,
                        'service_name': 'test_service',
                        'start_apply_time': '2017-11-01T01:10:00+0300',
                        'status': 'applying',
                        'summary': {},
                        'tickets': [],
                        'tplatform_namespace': 'taxi',
                        'version': 3,
                        'scheme_type': 'admin',
                    },
                ],
                'not_applied': [
                    {
                        'id': 1000,
                        'version': 1,
                        'reason': 'Draft with id=1000 was not found',
                    },
                ],
            },
        ),
        (
            {'drafts': [{'id': 1, 'version': 1}, {'id': 2, 'version': 2}]},
            {
                'applied': [],
                'not_applied': [
                    {
                        'id': 1,
                        'version': 1,
                        'reason': 'You are not author of the draft',
                    },
                    {
                        'id': 2,
                        'version': 2,
                        'reason': 'Draft is not in approved or failed status',
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.config(
    APPROVALS_NAMESPACES_CONFIG={'tariff_editor_namespaces': ['taxi']},
)
@pytest.mark.pgsql('approvals', files=['edit.sql'])
@pytest.mark.now('2017-11-01T01:10:00+0300')
async def test_manual_applies(data, expected, taxi_approvals_client):
    response = await taxi_approvals_client.post(
        '/drafts/bulk_manual_apply/',
        json=data,
        headers={'X-Yandex-Login': 'test_user2'},
    )
    content = await response.json()
    assert response.status == 200
    for item in content['applied']:
        assert item.pop('updated')
    assert content == expected


@pytest.mark.parametrize(
    'draft_id,service_name,status_code',
    [(1, 'test_service', 200), (2, 'test_service', 403)],
)
@pytest.mark.config(
    APPROVALS_NAMESPACES_CONFIG={'tariff_editor_namespaces': ['taxi']},
)
@pytest.mark.pgsql('approvals', files=['reapply.sql'])
@pytest.mark.now('2017-11-01T01:10:00+0300')
async def test_manual_reapply(
        draft_id, service_name, status_code, taxi_approvals_client,
):
    response = await taxi_approvals_client.post(
        f'/drafts/{draft_id}/manual_apply/',
        json={},
        headers={'X-Yandex-Login': 'test_user2'},
    )
    assert response.status == status_code


@pytest.mark.parametrize(
    'draft_id,service_name,status_code,error_code',
    [
        pytest.param(
            1,
            'test_service',
            200,
            None,
            id='apply_enabled',
            marks=[
                pytest.mark.config(
                    APPROVALS_FREEZE_SETTINGS={
                        'enabled': True,
                        'allowed_draft_ids': [1],
                    },
                ),
            ],
        ),
        pytest.param(
            1,
            'test_service',
            400,
            'APPROVALS_FREEZE_CHECK_FAILED',
            id='apply_disabled',
            marks=[
                pytest.mark.config(
                    APPROVALS_FREEZE_SETTINGS={
                        'enabled': True,
                        'allowed_draft_ids': [2],
                    },
                ),
            ],
        ),
    ],
)
@pytest.mark.config(
    APPROVALS_NAMESPACES_CONFIG={'tariff_editor_namespaces': ['taxi']},
)
@pytest.mark.pgsql('approvals', files=['reapply.sql'])
@pytest.mark.now('2017-11-01T01:10:00+0300')
async def test_manual_freeze_apply(
        draft_id, service_name, status_code, taxi_approvals_client, error_code,
):
    response = await taxi_approvals_client.post(
        f'/drafts/{draft_id}/manual_apply/',
        json={},
        headers={'X-Yandex-Login': 'test_user2'},
    )
    assert response.status == status_code
    content = await response.json()
    assert content.get('code') == error_code, content


@pytest.mark.parametrize(
    'data,status,error_code',
    [
        ({'id': 5, 'version': 2, 'multidraft_id': 6}, 400, 'ALREADY_ATTACHED'),
        (
            {'id': 1, 'version': 1, 'multidraft_id': 4},
            400,
            'WRONG_STATUS_DRAFT',
        ),
        ({'id': 1, 'version': 2, 'multidraft_id': 4}, 409, 'VERSION_ERROR'),
        ({'id': 5, 'version': 2, 'multidraft_id': 6}, 400, 'ALREADY_ATTACHED'),
        ({'id': 7, 'version': 1, 'multidraft_id': 4}, 200, None),
        ({'id': 7, 'version': 1, 'multidraft_id': 1000}, 404, 'NOT_FOUND'),
        (
            {'id': 15, 'version': 1, 'multidraft_id': 14},
            409,
            'APPROVERS_GROUPS_ERROR',
        ),
    ],
)
@pytest.mark.config(
    APPROVALS_NAMESPACES_CONFIG={'tariff_editor_namespaces': ['taxi']},
)
@pytest.mark.pgsql('approvals', files=['data.sql'])
@pytest.mark.now('2017-11-01T01:10:00+0300')
async def test_draft_attach(taxi_approvals_client, data, status, error_code):
    response = await taxi_approvals_client.post(
        '/drafts/attach/', json=data, headers={'X-Yandex-Login': 'test_login'},
    )
    content = await response.json()
    assert response.status == status
    if status == 200:
        assert content.pop('updated')
        assert content == {
            'api_path': 'test_api',
            'approvals': [],
            'change_doc_id': '300',
            'comments': [
                {'login': '_prepare_draft_response_200', 'comment': '200xxx'},
            ],
            'created': '2017-11-01T04:10:00+0300',
            'description': 'test',
            'errors': [],
            'id': 7,
            'mode': 'push',
            'multidraft_id': 4,
            'object_id': 'test_service:test_api',
            'run_manually': False,
            'service_name': 'test_service',
            'status': 'need_approval',
            'summary': {},
            'headers': {},
            'query_params': {},
            'summoned_users': [
                {
                    'login': 'test_login1',
                    'summoned': '2017-11-01T04:10:00+0300',
                },
                {
                    'login': 'test_login2',
                    'summoned': '2017-11-01T04:10:00+0300',
                },
            ],
            'tickets': [],
            'tplatform_namespace': 'taxi',
            'version': 2,
            'created_by': 'test_user_7',
            'data': {'test_key': 'test_value'},
            'deferred_apply': '2017-11-01T04:10:00+0300',
            'responsibles': ['test_login1', 'test_login2'],
            'scheme_type': 'admin',
        }
    else:
        assert content['code'] == error_code


@pytest.mark.parametrize(
    'data,status,error_code',
    [
        ({'id': 5, 'version': 2}, 200, None),
        ({'id': 1, 'version': 2}, 409, 'VERSION_ERROR'),
        ({'id': 4, 'version': 1}, 400, 'WRONG_DRAFT_TYPE'),
        ({'id': 1, 'version': 1}, 400, 'NOT_ATTACHED'),
    ],
)
@pytest.mark.config(
    APPROVALS_NAMESPACES_CONFIG={'tariff_editor_namespaces': ['taxi']},
)
@pytest.mark.pgsql('approvals', files=['data.sql'])
@pytest.mark.now('2017-11-01T01:10:00+0300')
async def test_draft_detach(taxi_approvals_client, data, status, error_code):
    response = await taxi_approvals_client.post(
        '/drafts/detach/', json=data, headers={'X-Yandex-Login': 'test_login'},
    )
    content = await response.json()
    assert response.status == status
    if status == 200:
        assert content.pop('updated')
        assert content == {
            'api_path': 'test_api2',
            'approvals': [],
            'change_doc_id': 'ch_22',
            'comments': [],
            'created': '2017-11-01T04:10:00+0300',
            'description': 'test2',
            'errors': [],
            'id': 5,
            'headers': {},
            'query_params': {},
            'mode': 'push',
            'object_id': 'test_service2:test_api2',
            'run_manually': False,
            'service_name': 'test_service2',
            'status': 'need_approval',
            'summary': {},
            'summoned_users': [],
            'tickets': ['TAXIRATE-35'],
            'ticket': 'TAXIRATE-35',
            'version': 3,
            'created_by': 'test_user',
            'data': {},
            'scheme_type': 'admin',
            'tplatform_namespace': 'taxi',
        }
    else:
        assert content['code'] == error_code
