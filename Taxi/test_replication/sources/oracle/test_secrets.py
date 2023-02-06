import pytest

from replication.foundation.secrets import exceptions as secrets_exceptions
from replication.foundation.secrets import render as secrets_render
from replication.sources.oracle import secrets as oracle_secrets
from replication.sources.oracle.core import source as oracle


@pytest.mark.parametrize(
    'raw_secret, expected_output',
    [
        (
            {
                'shards.0.dsn': (
                    '(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)'
                    '(HOST=tst.host0.example.com)(PORT=1531))'
                    '(CONNECT_DATA=(SERVICE_NAME=test)))'
                ),
                'shards.0.user': 'user0',
                'shards.0.password': 'password0',
                'shards.0.shard_number': '0',
                'shards.1.dsn': (
                    '(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)'
                    '(HOST=tst.host1.example.com)(PORT=1531))'
                    '(CONNECT_DATA=(SERVICE_NAME=test)))'
                ),
                'shards.1.user': 'user1',
                'shards.1.password': 'password1',
                'shards.1.shard_number': '1',
            },
            [
                {
                    'dsn': (
                        '(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)'
                        '(HOST=tst.host0.example.com)(PORT=1531))'
                        '(CONNECT_DATA=(SERVICE_NAME=test)))'
                    ),
                    'user': 'user0',
                    'password': 'password0',
                    'shard_number': 0,
                },
                {
                    'dsn': (
                        '(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)'
                        '(HOST=tst.host1.example.com)(PORT=1531))'
                        '(CONNECT_DATA=(SERVICE_NAME=test)))'
                    ),
                    'user': 'user1',
                    'password': 'password1',
                    'shard_number': 1,
                },
            ],
        ),
    ],
)
def test_render(raw_secret, expected_output):
    rendered = secrets_render.render_strongbox_secret(
        raw_secret=raw_secret,
        template=oracle_secrets.STRONGBOX_SECRET_TEMPLATE,
        required_keys=oracle_secrets.STRONGBOX_SECRET_KEYS,
    )
    assert rendered == expected_output


@pytest.mark.parametrize(
    'raw_secret, expected_output, expected_exception, missing_keys',
    [
        (
            {
                'shards.0.dsn': (
                    '(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)'
                    '(HOST=tst.host0.example.com)(PORT=1531))'
                    '(CONNECT_DATA=(SERVICE_NAME=test)))'
                ),
                'shards.0.user': 'user0',
                'shards.0.password': 'password0',
                'shards.0.shard_number': '0',
                'shards.1.dsn': (
                    '(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)'
                    '(HOST=tst.host1.example.com)(PORT=1531))'
                    '(CONNECT_DATA=(SERVICE_NAME=test)))'
                ),
            },
            None,
            secrets_exceptions.IncompleteSecretError,
            ['shards.1.password', 'shards.1.user'],
        ),
    ],
)
def test_render_fail(
        raw_secret, expected_output, expected_exception, missing_keys,
):
    with pytest.raises(expected_exception) as exc_info:
        secrets_render.render_strongbox_secret(
            raw_secret=raw_secret,
            template=oracle_secrets.STRONGBOX_SECRET_TEMPLATE,
            required_keys=oracle_secrets.STRONGBOX_SECRET_KEYS,
        )
    assert missing_keys == exc_info.value.missing_keys


def test_source_meta(replication_ctx):
    rules = replication_ctx.rule_keeper.rules_storage.get_rules_list(
        rule_name='oracle_test_yav', source_types=[oracle.SOURCE_TYPE_ORACLE],
    )
    rule = rules[0]
    meta = rule.source.meta
    conn_settings = meta.connection_settings
    assert conn_settings.dsn == (
        '(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=tst.host0.example.com)'
        '(PORT=1531))(CONNECT_DATA=(SERVICE_NAME=test)))'
    )
    assert conn_settings.shard_number == 0
    assert conn_settings.user == 'user0'
    assert conn_settings.password == 'password0'
