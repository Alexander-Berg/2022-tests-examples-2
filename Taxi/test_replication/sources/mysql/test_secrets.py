import pytest

from replication.foundation.secrets import exceptions as secrets_exceptions
from replication.foundation.secrets import render as secrets_render
from replication.sources.mysql import secrets as mysql_secrets
from replication.sources.mysql.core import source as mysql


@pytest.mark.parametrize(
    'raw_secret, expected_output',
    [
        (
            {
                'shards.0.database': 'testsuite0',
                'shards.0.host': 'testsuite0.yandex.net',
                'shards.0.password': 'secret0',
                'shards.0.port': '3306',
                'shards.0.user': 'testsuite0',
                'shards.0.shard_number': '0',
                'shards.1.database': 'testsuite1',
                'shards.1.host': 'testsuite1.yandex.net',
                'shards.1.password': 'secret1',
                'shards.1.port': '3306',
                'shards.1.user': 'testsuite1',
                'shards.1.shard_number': '1',
            },
            [
                {
                    'database': 'testsuite0',
                    'host': 'testsuite0.yandex.net',
                    'password': 'secret0',
                    'port': 3306,
                    'user': 'testsuite0',
                    'shard_number': 0,
                },
                {
                    'database': 'testsuite1',
                    'host': 'testsuite1.yandex.net',
                    'password': 'secret1',
                    'port': 3306,
                    'user': 'testsuite1',
                    'shard_number': 1,
                },
            ],
        ),
    ],
)
def test_render(raw_secret, expected_output):
    rendered = secrets_render.render_strongbox_secret(
        raw_secret=raw_secret,
        template=mysql_secrets.STRONGBOX_SECRET_TEMPLATE,
        required_keys=mysql_secrets.STRONGBOX_SECRET_KEYS,
    )
    assert rendered == expected_output


@pytest.mark.parametrize(
    'raw_secret, expected_exception, missing_keys',
    [
        (
            {
                'shards.0.database': 'test',
                'shards.0.user': 'user0',
                'shards.0.password': 'password0',
                'shards.0.shard_number': '0',
                'shards.0.port': 1234,
                'shards.0.host': 'test',
                'shards.1.database': 'test_db',
            },
            secrets_exceptions.IncompleteSecretError,
            [
                'shards.1.host',
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
            template=mysql_secrets.STRONGBOX_SECRET_TEMPLATE,
            required_keys=mysql_secrets.STRONGBOX_SECRET_KEYS,
        )
    assert missing_keys == exc_info.value.missing_keys


@pytest.mark.nofilldb
def test_source_meta(replication_ctx):
    rules = replication_ctx.rule_keeper.rules_storage.get_rules_list(
        rule_name='mysql_test_rule_yav',
        source_types=[mysql.SOURCE_TYPE_MYSQL],
    )
    rule = rules[0]
    meta = rule.source.meta
    conn_settings = meta.connection_settings
    assert conn_settings.database == 'testsuite0'
    assert conn_settings.host == 'testsuite0.yandex.net'
    assert conn_settings.password == 'secret0'
    assert conn_settings.port == 3306
    assert conn_settings.shard_number == 0
    assert conn_settings.user == 'testsuite0'
