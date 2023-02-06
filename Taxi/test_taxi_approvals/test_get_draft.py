import pytest

from taxi_approvals.internal import headers as headers_module


@pytest.fixture(name='get_draft_v1')
def _get_draft_v1(taxi_approvals_client):
    async def _request(draft_id, is_platform=False, tplatform_namespace=None):
        headers = {headers_module.X_YANDEX_LOGIN: 'test_login'}
        if is_platform:
            headers[headers_module.X_MULTISERVICES_PLATFORM] = 'true'
        params = {}
        if tplatform_namespace:
            params['tplatform_namespace'] = tplatform_namespace
        response = await taxi_approvals_client.get(
            f'/drafts/{draft_id}/', params=params, headers=headers,
        )
        return response

    return _request


@pytest.fixture(name='get_draft_v2')
def _get_draft_v2(taxi_approvals_client):
    async def _request(draft_id, tplatform_namespace=None, is_platform=False):
        headers = {
            headers_module.X_YANDEX_LOGIN: 'test_login',
            headers_module.X_MULTISERVICES_PLATFORM: str(is_platform).lower(),
        }
        response = await taxi_approvals_client.get(
            '/v2/drafts/',
            params={
                'id': draft_id,
                'tplatform_namespace': tplatform_namespace,
            },
            headers=headers,
        )
        return response

    return _request


@pytest.mark.parametrize(
    ['draft_id', 'tplatform_namespace', 'scheme_type'],
    [(1, 'taxi', 'admin'), (19, 'eda', 'platform')],
)
@pytest.mark.pgsql('approvals', files=['data.sql'])
async def test_draft_get_v1(
        get_draft_v1, draft_id, tplatform_namespace, scheme_type,
):
    response = await get_draft_v1(
        draft_id, scheme_type == 'platform', tplatform_namespace,
    )
    draft = await response.json()
    assert response.status == 200, draft
    assert draft['id'] == draft_id
    assert draft['scheme_type'] == scheme_type


@pytest.mark.parametrize(
    ['draft_id', 'tplatform_namespace', 'scheme_type'],
    [(1, 'taxi', 'admin'), (19, 'eda', 'platform')],
)
@pytest.mark.pgsql('approvals', files=['data.sql'])
async def test_draft_get_v1_bad_schemes(
        get_draft_v1, draft_id, tplatform_namespace, scheme_type,
):
    response = await get_draft_v1(
        draft_id, scheme_type == 'admin', tplatform_namespace,
    )
    content = await response.json()
    assert response.status == 400, content
    assert content['code'] == 'WRONG_SCHEME_TYPE'


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                APPROVALS_NAMESPACES_CONFIG={
                    'tariff_editor_namespaces': ['taxi', 'eda'],
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
    ['draft_id', 'namespace', 'scheme_type'],
    [(1, 'taxi', 'admin'), (19, 'eda', 'platform')],
)
@pytest.mark.pgsql('approvals', files=['data.sql'])
async def test_draft_get_v2(get_draft_v2, draft_id, namespace, scheme_type):
    response = await get_draft_v2(
        draft_id, namespace, scheme_type == 'platform',
    )
    draft = await response.json()
    assert response.status == 200, draft
    assert draft['id'] == draft_id
    assert draft['scheme_type'] == scheme_type


@pytest.mark.parametrize(
    ['draft_id', 'namespace', 'scheme_type'],
    [(1, 'taxi', 'admin'), (19, 'eda', 'platform')],
)
@pytest.mark.pgsql('approvals', files=['data.sql'])
async def test_draft_get_v2_bad_schemes(
        get_draft_v2, draft_id, namespace, scheme_type,
):
    response = await get_draft_v2(draft_id, namespace, scheme_type == 'admin')
    content = await response.json()
    assert response.status == 400, content
    assert content['code'] == 'WRONG_SCHEME_TYPE'


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                APPROVALS_NAMESPACES_CONFIG={
                    'tariff_editor_namespaces': ['lavka', 'market'],
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
    ['draft_id', 'namespace', 'scheme_type', 'status', 'error_code'],
    [
        (1, 'wrong_namespace', 'admin', 400, 'TPLATFORM_NAMESPACE_MISMATCH'),
        (
            19,
            'wrong_namespace',
            'platform',
            400,
            'TPLATFORM_NAMESPACE_MISMATCH',
        ),
        (1, '', 'admin', 400, 'TPLATFORM_NAMESPACE_QUERY_EMPTY'),
        (19, '', 'platform', 400, 'TPLATFORM_NAMESPACE_QUERY_EMPTY'),
    ],
)
@pytest.mark.pgsql('approvals', files=['data.sql'])
async def test_draft_get_v2_bad_namespace(
        get_draft_v2, draft_id, namespace, scheme_type, status, error_code,
):
    response = await get_draft_v2(
        draft_id, namespace, scheme_type == 'platform',
    )
    content = await response.json()
    assert response.status == status, content
    assert content['code'] == error_code
