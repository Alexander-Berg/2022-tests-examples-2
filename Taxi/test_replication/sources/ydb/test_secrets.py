import pytest

from replication.foundation.secrets import exceptions as secrets_exceptions
from replication.foundation.secrets import validate as secrets_validate
from replication.sources.ydb import secrets as ydb_secrets


@pytest.mark.parametrize(
    'raw_secret',
    [{'database': 'local', 'endpoint': 'localhost', 'token': 'secret'}],
)
def test_validate_success(raw_secret):
    secrets_validate.validate_secret(
        raw_secret=raw_secret, required_keys=ydb_secrets.YAV_SECRET_KEYS,
    )


@pytest.mark.parametrize(
    'raw_secret, expected_exception, missing_keys',
    [
        (
            {'database': 'local'},
            secrets_exceptions.IncompleteSecretError,
            ['endpoint', 'token'],
        ),
    ],
)
def test_validate_fail(raw_secret, expected_exception, missing_keys):
    with pytest.raises(expected_exception) as exc_info:
        secrets_validate.validate_secret(
            raw_secret=raw_secret, required_keys=ydb_secrets.YAV_SECRET_KEYS,
        )
    assert missing_keys == exc_info.value.missing_keys
