# pylint: disable=protected-access
import pathlib

import pytest

from replication.drafts import exceptions
from replication.drafts.models import yt_ctl


@pytest.mark.parametrize(
    'rule_scope, target_name', [('admin_draft_scope', 'admin_draft_raw1')],
)
def test_func_check_queue_snapshot(
        replication_ctx, replication_client, rule_scope, target_name,
):
    yt_ctl._check_queue_snapshot(
        replication_ctx.rule_keeper, rule_scope, target_name,
    )


@pytest.mark.parametrize(
    'rule_scope, target_name, expected',
    [
        (
            'admin_draft_scope_snapshot',
            'admin_draft_snapshot_raw1',
            'You are trying to apply draft to rule '
            '\'admin_draft_snapshot\' with replication type '
            '\'queue_snapshot\'. Only \'queue\' replication '
            'type is allowed',
        ),
    ],
)
def test_func_check_queue_snapshot_exceptions(
        replication_ctx, replication_client, rule_scope, target_name, expected,
):
    try:
        yt_ctl._check_queue_snapshot(
            replication_ctx.rule_keeper, rule_scope, target_name,
        )
    except exceptions.DraftCheckError as draft_check_error:
        assert draft_check_error.error_info.message == expected


@pytest.fixture
def test_env_id_setter(static_dir):
    return 'admin_drafts#' + pathlib.Path(static_dir).parent.stem
