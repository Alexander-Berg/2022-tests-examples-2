import pytest

from archiving import settings
from archiving.cron_tasks import register_rules

_DEFAULT_SLEEP_DELAY = 200
_FROZEN_RULES_TO_LOAD = {
    'test_postgres',
    'test_postgres_tz',
    'test_rule',
    'test_rule_filter',
}


@pytest.fixture
def _archiving_register(mockserver):
    registered_rules = set()

    @mockserver.json_handler('/archiving-admin/archiving/v1/rules/register')
    def _handler(request):
        response = []
        for rule in request.json['rules']:
            rule_name = rule['rule_name']
            assert rule['sleep_delay'] == _DEFAULT_SLEEP_DELAY
            if rule_name not in registered_rules:
                response.append(
                    {
                        'rule_name': rule_name,
                        'group_name': rule['group_name'],
                        'source_type': rule['source_type'],
                    },
                )
        return {'rules': response}

    class _AdminPatcher:
        @staticmethod
        def register_rules(names):
            registered_rules.update(names)

        handler = _handler

    return _AdminPatcher


@pytest.mark.parametrize(
    'registered_rules,expected_registered',
    [
        (
            [],
            [
                'test_postgres',
                'test_postgres_tz',
                'test_rule',
                'test_rule_filter',
            ],
        ),
        (
            ['test_rule'],
            ['test_postgres', 'test_postgres_tz', 'test_rule_filter'],
        ),
        (
            ['test_rule_filter'],
            ['test_postgres', 'test_postgres_tz', 'test_rule'],
        ),
        (
            [
                'test_rule_filter',
                'test_rule',
                'test_postgres',
                'test_postgres_tz',
            ],
            [],
        ),
    ],
)
async def test_register_rules(
        monkeypatch,
        patch_test_env,
        cron_context,
        _archiving_register,
        registered_rules,
        expected_registered,
        requests_handlers,
):
    _archiving_register.register_rules(registered_rules)
    monkeypatch.setattr(settings, 'DEFAULT_SLEEP_DELAY', _DEFAULT_SLEEP_DELAY)
    rules = await register_rules.register_rules(
        cron_context, rules_to_load=_FROZEN_RULES_TO_LOAD,
    )
    assert rules == expected_registered


async def test_real_register_rules(
        monkeypatch, cron_context, _archiving_register,
):
    monkeypatch.setattr(settings, 'DEFAULT_SLEEP_DELAY', _DEFAULT_SLEEP_DELAY)
    rules = await register_rules.register_rules(cron_context)
    assert isinstance(rules, list)
