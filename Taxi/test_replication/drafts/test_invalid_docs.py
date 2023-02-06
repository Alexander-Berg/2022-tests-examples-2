# pylint: disable=protected-access
import pathlib

import pytest

from replication.drafts.models import invalid_docs


@pytest.mark.parametrize(
    'rule_scope, expected_variables',
    [
        (
            'admin_draft_scope',
            {
                'rule_names': {
                    'enum': ['admin_draft', 'admin_draft2'],
                    'type': 'string',
                },
                'current_thresholds': [
                    {
                        'invalid_docs_alert': 2,
                        'invalid_docs_can_continue': 3,
                        'rule_name': 'admin_draft',
                    },
                ],
            },
        ),
        (
            'admin_draft_scope2',
            {
                'rule_names': {'enum': ['admin_draft3'], 'type': 'string'},
                'current_thresholds': [],
            },
        ),
        (
            None,
            {
                'rule_names': {
                    'enum': [
                        'admin_draft',
                        'admin_draft2',
                        'admin_draft3',
                        'admin_draft4',
                        'admin_draft_snapshot',
                    ],
                    'type': 'string',
                },
                'current_thresholds': [
                    {
                        'invalid_docs_alert': 2,
                        'invalid_docs_can_continue': 3,
                        'rule_name': 'admin_draft',
                    },
                ],
            },
        ),
    ],
)
async def test_get_variables(replication_ctx, rule_scope, expected_variables):
    variables = await invalid_docs._get_variables(
        replication_ctx.rule_keeper, rule_scope=rule_scope,
    )
    assert variables == expected_variables


@pytest.mark.parametrize(
    'thresholds, expected',
    [
        (
            [
                {'rule_name': 'admin_draft', 'invalid_docs_alert': 3000},
                {'rule_name': 'admin_draft3', 'queue_old_docs_alert': 30},
            ],
            {
                '__default__': {},
                'admin_draft': {
                    'invalid_docs_alert': 3000,
                    'invalid_docs_can_continue': 3,
                },
                'admin_draft3': {'queue_old_docs_alert': 30},
            },
        ),
        ([{'rule_name': 'admin_draft'}], {'__default__': {}}),
    ],
)
async def test_change_thresholds(replication_ctx, thresholds, expected):
    invalid_docs_thresholds = (
        replication_ctx.pluggy_deps.invalid_docs_thresholds
    )

    await invalid_docs_thresholds.cache_holder.refresh_cache()
    assert (await invalid_docs_thresholds.get_thresholds()) == {
        '__default__': {},
        'admin_draft': {
            'invalid_docs_alert': 2,
            'invalid_docs_can_continue': 3,
        },
    }

    await invalid_docs._change_thresholds(
        replication_ctx, thresholds=thresholds,
    )

    await invalid_docs_thresholds.cache_holder.refresh_cache()
    assert (await invalid_docs_thresholds.get_thresholds()) == expected


@pytest.fixture
def test_env_id_setter(static_dir):
    return 'admin_drafts#' + pathlib.Path(static_dir).parent.stem
