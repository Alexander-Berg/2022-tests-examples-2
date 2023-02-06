import pathlib

import pytest

from replication.drafts import admin_run_draft


@pytest.mark.parametrize(
    'draft_data, status, expected_response',
    [
        (
            {
                'rule_scope': 'admin_draft_scope',
                'draft_name': 'change_state',
                'target_names': ['admin_draft_raw1'],
                'payload': {'action': 'init'},
            },
            200,
            {},
        ),
        (
            {
                'rule_scope': 'admin_draft_scope',
                'draft_name': 'invalid_docs',
                'payload': {
                    'action': 'remove_invalid_docs',
                    'rule_names': ['admin_draft'],
                },
            },
            200,
            {},
        ),
    ],
)
async def test_admin_drafts_apply(
        replication_client,
        replication_ctx,
        load_json,
        draft_data,
        status,
        expected_response,
):
    response = await replication_client.post(
        f'/admin/v1/drafts/check', json=draft_data,
    )
    assert response.status == 200, await response.text()
    await replication_ctx.rule_keeper.on_shutdown()
    await admin_run_draft.process_draft(replication_ctx, draft_data)


@pytest.fixture
def test_env_id_setter(static_dir):
    return 'admin_drafts#' + pathlib.Path(static_dir).parent.stem
