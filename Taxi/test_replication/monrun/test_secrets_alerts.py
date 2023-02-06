# pylint: disable=redefined-outer-name
import pytest

from replication import settings
from replication.foundation.metrics import names
from replication.monrun.checks import check_secrets_and_delays


@pytest.fixture
def _test_env_id():
    return 'monrun'


@pytest.fixture
def safe_load_rules(monkeypatch):
    monkeypatch.setattr(settings, 'SAFELY_LOAD_RULES', True)


@pytest.fixture
def mock_config_yaml():
    pass


@pytest.mark.parametrize(
    'responsible, expected_error',
    [
        (
            'empty_secret_team',
            'empty_secret_rule: rule empty_secret_rule: Secret(type=yav, '
            'id=\'sec-empty\') is empty',
        ),
        (
            'incomplete_secret_team',
            'incomplete_secret_rule: rule incomplete_secret_rule: '
            'Secret with alias broken is incomplete: missing '
            '\'[\'shards.0.db_name\', \'shards.0.password\', '
            '\'shards.0.port\', \'shards.0.user\']\' keys.',
        ),
        (
            'secret_not_in_config_team',
            'secret_not_in_config_rule: rule secret_not_in_config_rule: '
            'No secret with alias not_in_config_yaml in config.yaml',
        ),
        (
            'unavailable_secret_team',
            'unavailable_secret_rule: rule unavailable_secret_rule: '
            'Secret(type=yav, id=\'none\') is not '
            'available for replication, check https://docs.yandex-team.ru'
            '/taxi-replication/docs/arcadia/secrets#how_to_add '
            'on how to add secret.',
        ),
    ],
)
async def test_broken_secret(
        responsible, expected_error, safe_load_rules, replication_ctx,
):
    res = await check_secrets_and_delays.do_check(
        replication_ctx, names.TEAMS_DELAY_CHECK_NAMES, responsible,
    )
    assert expected_error in res
