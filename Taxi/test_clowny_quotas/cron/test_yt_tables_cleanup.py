import pytest

from taxi import settings as taxi_settings

from clowny_quotas.crontasks import yt_tables_cleanup
from clowny_quotas.yt_tools.cleanup import rule_definitions
from clowny_quotas.yt_tools.cleanup import static_rotation_rules


_TEST_ROTATION_RULES = [
    rule_definitions.RotationRule(
        full_path='//unittests/{environment}/valid/node',
    ),
    rule_definitions.RotationRule(
        full_path='//unittests/{environment}/valid/ttl', ttl={'seconds': 2000},
    ),
]


@pytest.mark.config(
    YT_TABLE_CLEANUP_CONFIG={
        'rotation_rules': [
            {
                'full_path': '//unittests/{environment}/invalid/ttl',
                'ttl': {'second': 2000},
            },
            {'full_path': '//unittests/{environment}/valid/node'},
            {
                'full_path': '//unittests/{environment}/valid/ttl',
                'ttl': {'seconds': 2000},
            },
            {
                'full_path': '/unittests/invalid/prefix',
                'ttl': {'seconds': 2000},
            },
        ],
    },
)
async def test_load_static_rules(cron_context, monkeypatch):
    all_static_rules = [
        *static_rotation_rules.ROTATE_RULES_PRODUCTION,
        *static_rotation_rules.ROTATE_RULES_TESTING,
        *static_rotation_rules.ROTATE_RULES_UNSTABLE,
    ]
    expected_rules = [*all_static_rules, *_TEST_ROTATION_RULES]
    monkeypatch.setitem(
        static_rotation_rules.STATIC_RULES_BY_ENVS,
        taxi_settings.UNITTESTS,
        all_static_rules,
    )
    monkeypatch.setitem(
        yt_tables_cleanup.ENV_MAPPING,
        taxi_settings.UNITTESTS,
        {taxi_settings.UNITTESTS},
    )
    current_environment = taxi_settings.get_environment()
    # pylint: disable=protected-access
    loaded_rules = yt_tables_cleanup._load_rotation_rules(
        cron_context.config.YT_TABLE_CLEANUP_CONFIG,
        current_environment=current_environment,
    )
    loaded_rules[current_environment].sort(key=lambda rule: rule._full_path)
    expected_rules.sort(key=lambda rule: rule._full_path)
    assert loaded_rules[current_environment] == expected_rules
