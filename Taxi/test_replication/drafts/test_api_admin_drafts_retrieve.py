import pathlib

import pytest


@pytest.mark.parametrize(
    'rule_scope, status, expected_response',
    [
        ('admin_draft_scope', 200, None),
        (
            'not_found_scope',
            404,
            {
                'code': 'scope-not-found',
                'message': 'rule scope \'not_found_scope\' not found',
            },
        ),
        (None, 200, None),
    ],
)
async def test_admin_drafts_retrieve(
        replication_client, load_json, rule_scope, status, expected_response,
):
    params = {'rule_scope': rule_scope} if rule_scope is not None else None
    response = await replication_client.post(
        f'/admin/v1/drafts/retrieve', params=params,
    )
    assert response.status == status, await response.text()

    response_json = await response.json()
    assert response_json

    if expected_response is not None:
        assert response_json == expected_response


@pytest.fixture
def test_env_id_setter(static_dir):
    return 'admin_drafts#' + pathlib.Path(static_dir).parent.stem
