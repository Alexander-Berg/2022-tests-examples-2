import datetime
import hashlib

import pytest

from replication import settings
from replication.verification import consts
from replication.verification.core import run

RULE_NAME = 'mongo-test_rule'
TEST_YT_REPLICATION_RULE_NAME = 'test_sharded_pg'
YT_VERIFICATION_RULE_NAMES = [
    'postgres-test_sharded_pg_shard0-test_sharded_pg_just_table',
    'postgres-test_sharded_pg_shard1-test_sharded_pg_just_table',
]


@pytest.fixture(name='patch_verification_settings')
def _patch_verification_settings(monkeypatch):
    monkeypatch.setattr(consts, 'DEFAULT_RETRIES_NUM', 0)
    monkeypatch.setattr(consts, 'DEFAULT_SLEEP_SECONDS', 0)


@pytest.mark.now('2019-05-20T12:35:00+0000')
@pytest.mark.mongodb_collections('test_coll')
async def test_verify_documents(
        monkeypatch, patch_verification_settings, replication_ctx,
):
    await replication_ctx.rule_keeper.verification_context_cache.ensure_init()
    verification_context = (
        replication_ctx.rule_keeper.verification_context_cache.cache
    )
    rule = verification_context.get_rule_by_name(RULE_NAME)

    class DummySha1:
        def __init__(self, data):
            pass

        # pylint: disable=no-self-use
        def hexdigest(self):
            return 'sha1hash'

    monkeypatch.setattr(hashlib, 'sha1', DummySha1)
    end_stamp = rule.get_max_stamp()
    await _run_and_check(
        rule,
        {
            '00_not_found': 'not_found',
            '04_mismatch': [
                '[root].updated: left=2019-05-20 00:11:00 '
                '!= right=2019-05-20 00:10:50',
            ],
        },
    )
    assert rule.state.current_stamp == datetime.datetime(2019, 5, 20, 0, 11)

    await rule.state.remove()
    await rule.state.init()

    assert rule.state.current_stamp is None

    assert rule.get_start_stamp() == (
        end_stamp - settings.VERIFICATION_DEFAULT_START_GAP
    )

    await _run_and_check(rule, {})
    assert rule.state.current_stamp is None  # no new data (max state -1h)


@pytest.mark.now('2019-05-20T12:35:00+0000')
@pytest.mark.pgsql('example_pg@0', files=['example_pg_shard0.sql'])
@pytest.mark.pgsql('example_pg@1', files=['example_pg_shard1.sql'])
@pytest.mark.yt(dyn_table_data=['yt_verification_table.yaml'])
@pytest.mark.use_yt_local
@pytest.mark.parametrize('rule_name', YT_VERIFICATION_RULE_NAMES)
async def test_verify_documents_to_yt(
        replication_ctx,
        patch_verification_settings,
        rule_name,
        yt_clients_storage,
        yt_client,
        yt_config,
        yt_apply,
        replace_frozen,
):
    await replication_ctx.rule_keeper.verification_context_cache.ensure_init()
    verification_context = (
        replication_ctx.rule_keeper.verification_context_cache.cache
    )
    rule = verification_context.get_rule_by_name(rule_name)
    end_stamp = rule.get_max_stamp()
    await _run_and_check(
        rule,
        {
            '(_id_1_, order)': (
                'docs_different_after_mapping: [\'[root].'
                'created_at: left=1557901800.0 != right='
                '231344.0\', \'[root].modified_at: '
                'left=1557901800.0 != right=231344.0\']'
            ),
            '(_id_2_, order)': 'doc_not_found_in_yt',
        },
    )
    await rule.state.remove()
    await rule.state.init()

    assert rule.state.current_stamp is None

    # pylint: disable=protected-access
    assert rule.get_start_stamp() == (end_stamp - rule._period_to_check)


async def _run_and_check(rule, expected_fails):
    assert not rule.state.disabled
    assert rule.is_active
    assert rule.state.current_fails == {}

    await run.verify_all_docs(rule)

    assert not rule.state.disabled
    assert rule.is_active

    assert rule.state.current_fails == expected_fails
