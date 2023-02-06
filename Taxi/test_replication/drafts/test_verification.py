import pathlib

import pytest

from replication.drafts import admin_run_draft
from replication.verification import setup


@pytest.mark.parametrize(
    'payload', [{'action': 'init', 'target_names': ['staging_admin_draft']}],
)
async def test_verification_draft(
        replication_ctx, replication_client, payload,
):
    verification_context = await setup.make_context(
        replication_ctx.db,
        replication_ctx.rule_keeper,
        replication_ctx.pluggy_deps.source_definitions,
    )
    verification_target_names = payload['target_names']
    draft_data = {
        'draft_name': 'verification',
        'rule_scope': 'admin_draft_scope',
        'payload': payload,
    }
    response = await replication_client.post(
        f'/admin/v1/drafts/check', json=draft_data,
    )
    assert response.status == 200, await response.text()
    await replication_ctx.rule_keeper.on_shutdown()
    await admin_run_draft.process_draft(replication_ctx, draft_data)
    verification_rules = verification_context.get_rules_by_target_names(
        verification_target_names,
    )
    for verification_rule in verification_rules:
        await verification_rule.state.refresh()
        assert verification_rule.is_initialized


@pytest.fixture
def test_env_id_setter(static_dir):
    return 'admin_drafts#' + pathlib.Path(static_dir).parent.stem
