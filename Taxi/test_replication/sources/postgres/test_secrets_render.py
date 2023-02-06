import copy

import pytest

from replication.foundation.secrets import exceptions as secrets_exceptions
from replication.foundation.secrets import render as secrets_render
from replication.sources.postgres import core as postgres
from replication.sources.postgres import definitions
from replication.sources.postgres import secrets as pg_secrets
from replication.sources.postgres.core import shards_util


@pytest.mark.parametrize(
    'raw_secret, expected_output',
    [
        (
            {
                'shards.0.host': 'test.host.0',
                'shards.1.password': 'password1',
                'shards.1.db_name': 'db1',
                'shards.1.port': '1',
                'shards.0.port': '0',
                'shards.0.db_name': 'db0',
                'shards.0.password': 'password0',
                'shards.1.host': 'test.host.1',
                'shards.0.user': 'user0',
                'shards.1.user': 'user1',
            },
            [
                {
                    'shard_number': 0,
                    'hosts': [
                        'host=test.host.0 port=0 dbname=db0 user=user0 '
                        'password=password0 sslmode=require',
                    ],
                },
                {
                    'shard_number': 1,
                    'hosts': [
                        'host=test.host.1 port=1 dbname=db1 user=user1 '
                        'password=password1 sslmode=require',
                    ],
                },
            ],
        ),
    ],
)
def test_render(raw_secret, expected_output):
    rendered = secrets_render.render_strongbox_secret(
        raw_secret=raw_secret,
        template=pg_secrets.STRONGBOX_SECRET_TEMPLATE,
        required_keys=pg_secrets.STRONGBOX_SECRET_KEYS,
    )
    assert rendered == expected_output


@pytest.mark.parametrize(
    'raw_secret, expected_exception, missing_keys',
    [
        (
            {
                'shards.0.host': 'test.host.0',
                'shards.0.port': '0',
                'shards.0.db_name': 'db0',
                'shards.0.user': 'user0',
                'shards.0.password': 'password0',
                'shards.1.host': 'test.host.1',
            },
            secrets_exceptions.IncompleteSecretError,
            [
                'shards.1.db_name',
                'shards.1.password',
                'shards.1.port',
                'shards.1.user',
            ],
        ),
    ],
)
def test_render_fail(raw_secret, expected_exception, missing_keys):
    with pytest.raises(expected_exception) as exc_info:
        secrets_render.render_strongbox_secret(
            raw_secret=raw_secret,
            template=pg_secrets.STRONGBOX_SECRET_TEMPLATE,
            required_keys=pg_secrets.STRONGBOX_SECRET_KEYS,
        )

    assert missing_keys == exc_info.value.missing_keys


def test_source_meta(replication_ctx):
    rules = replication_ctx.rule_keeper.rules_storage.get_rules_list(
        rule_name='yav_secret_postgres',
        source_types=[postgres.SOURCE_TYPE_POSTGRES],
    )
    rule = rules[0]
    meta = rule.source.meta
    assert meta.dsn == (
        'host=test.host.0 port=0 dbname=db0 user=user0 password=password0 '
        'sslmode=require'
    )
    assert meta.shard_num == 0


@pytest.mark.parametrize(
    'broken_key, broken_value, exc_text',
    [
        (
            'hosts',
            [
                'host=test, test port=1111 dbname=testsuite '
                'user=user password=password sslmode=disable',
            ],  # extra space in host, processed in external module
            (
                '<class \'ValueError\'>: unknown error while '
                'parsing pg connection'
            ),
        ),
        (
            'hosts',
            [
                'host=testsuite port=1111 dbname=testsuite '
                'user= password=password sslmode=disable',
            ],  # empty user
            'Empty fields in secret: [\'user\']',
        ),
        (
            'hosts',
            [
                'host=testsuite port=test dbname=testsuite '
                'user=user password=password sslmode=disable',
            ],  # port is not int
            'port should be an int or be convertable to int',
        ),
    ],
)
def test_broken_secrets(monkeypatch, broken_key, broken_value, exc_text):
    # pylint: disable=protected-access
    shards = copy.deepcopy(definitions._TESTSUITE_SECRET)
    shards[0][broken_key] = broken_value
    monkeypatch.setattr(definitions, '_TESTSUITE_SECRET', shards)
    with pytest.raises(shards_util.CannotParseSecretError) as exc:
        shards_util.get_pg_connections(shards)
    assert exc_text in str(exc.value)
