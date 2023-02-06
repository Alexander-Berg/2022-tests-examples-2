import datetime

import pytest

from replication.foundation.metrics import replication_delays
from replication.monrun import general_check
from replication.monrun import team_check
from replication.monrun.checks import replication_delays as monrun

NOW = datetime.datetime(2018, 5, 10, 2, 0)


@pytest.mark.config(REPLICATION_CRON_MAIN_SETUP={'disable_all': True})
async def test_check_replication_disabled(replication_ctx):
    res = await general_check.run_general_check(
        replication_ctx, general_check_type='sync-delay',
    )
    assert res == '0; Replication disabled'


@pytest.mark.config(
    REPLICATION_MONRUN_THRESHOLDS={
        monrun.CHECK_TYPE: {
            '__default__': {
                replication_delays.names.SYNC_DELAY: {
                    'warning': 600,
                    'critical': 900,
                },
                replication_delays.names.DISABLED_RULES_CHECKS[
                    replication_delays.names.SYNC_DELAY
                ]: {'warning': 60000, 'critical': 90000},
                replication_delays.names.RELATIVE_DELAY: {
                    'warning': 1,
                    'critical': 2,
                },
            },
            '__overrides__': [
                {
                    'items': [
                        'queue_mongo-staging_test_rule-'
                        'yt-test_rule_struct-arni',
                        'queue_mongo-staging_test_rule-'
                        'yt-test_rule_struct-hahn',
                    ],
                    'value': {
                        replication_delays.names.DELAY_FROM_NOW: {
                            'critical': 7000 * 60,
                            'warning': 6700 * 60,
                        },
                    },
                },
                {
                    'items': ['mongo-test_rule-queue_mongo-staging_test_rule'],
                    'value': {
                        replication_delays.names.DELAY_FROM_NOW: {
                            'critical': 23,
                            'warning': 20,
                        },
                    },
                },
                {
                    'items': [r'.+test_api_basestamp.+'],
                    'value': {
                        replication_delays.names.DELAY_FROM_NOW: {
                            'critical': 6000 * 60,
                            'warning': 5500 * 60,
                        },
                    },
                },
            ],
        },
    },
)
@pytest.mark.now(NOW.isoformat())
async def test_replication_checks(replication_ctx):
    res = await general_check.run_general_check(
        replication_ctx, general_check_type='sync-delay',
    )

    assert res == (
        '2; CRIT (4 problems): '
        '[Task queue_mongo -> yt has no successful runs]: '
        'test_rule-*-(arni, hahn) = 6561 min > 16 min, '
        '[Task mongo -> queue_mongo has no successful runs '
        'https://unittests/replications/show/test_api_basestamp]: '
        'test_rule = 3681 min > 18 min, '
        '[Task queue_mongo -> yt disabled too long]: '
        'test_rule-bson-hahn = 37 hours > 25 hours, '
        '[Task queue_mongo -> yt has no successful runs '
        'https://unittests/replications/show/all_sources]: '
        'basic_source_mongo_snapshot-arni = 2241 min > 35 min'
    )

    res = await general_check.run_general_check(
        replication_ctx, general_check_type='delay-from-now',
    )

    assert res == (
        '2; CRIT (2 problems): '
        '[Task queue_mongo -> yt delay from now is too great '
        'https://unittests/replications/show/test_api_basestamp]: '
        'test_api_basestamp-struct-(arni, hahn) = 133 hours > 100 hours, '
        '[Task mongo -> queue_mongo delay from now is too great '
        'https://unittests/replications/show/test_api_basestamp]: '
        'test_rule = 393904 sec > 23 sec, '
        'WARN (1 problem): '
        '[Task queue_mongo -> yt delay from now is too great '
        'https://unittests/replications/show/test_api_basestamp]: '
        'test_rule-struct-arni = 112 hours > 111 hours'
    )

    res = await general_check.run_general_check(
        replication_ctx, general_check_type='relative-delay',
    )
    assert res == (
        '2; CRIT (1 problem): '
        '[Task queue_mongo -> yt has too big '
        'delay behind other targets of group '
        'https://unittests/replications/show/test_api_basestamp]: '
        'test_rule-bson-arni = 120 sec > 2 sec'
    )


_TEAM_MODULE = 'replication.monrun.team_check'
_GENERAL_MODULE = 'replication.monrun.general_check'


@pytest.mark.config(REPLICATION_CRON_MAIN_SETUP={'disable_all': True})
async def test_team_replication_disabled(replication_ctx):
    res = await team_check.run_team_check(
        replication_ctx, team_check_type='delay', dev_team='testsuite',
    )
    assert res == '0; Replication disabled'


async def test_team_replication_ok(replication_ctx):
    res = await team_check.run_team_check(
        replication_ctx, team_check_type='delay', dev_team='testsuite',
    )
    assert res == '0; Ok, found 9 initialized targets'


_TEAM_MSG = (
    '2; CRIT (4 problems): '
    '[Task mongo -> queue_mongo delay from now is too great '
    'https://unittests/replications/show/test_api_basestamp]: '
    'test_rule = 393904 sec > 23 sec, '
    '[Task queue_mongo -> yt has no successful runs]: '
    'test_rule-*-(arni, hahn) = 6561 min > 16 min, '
    'basic_source_mongo_snapshot-arni = 2241 min > 35 min, '
    '[Task mongo -> queue_mongo has no successful runs '
    'https://unittests/replications/show/test_api_basestamp]: '
    'test_rule = 3681 min > 18 min'
)


@pytest.mark.config(
    REPLICATION_MONRUN_THRESHOLDS={
        'replication': {
            '__default__': {'sync_delay': {'warning': 600, 'critical': 900}},
            '__overrides__': [
                {
                    'items': ['mongo-test_rule-queue_mongo-staging_test_rule'],
                    'value': {
                        replication_delays.names.DELAY_FROM_NOW: {
                            'critical': 23,
                            'warning': 20,
                        },
                    },
                },
            ],
        },
    },
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'expected',
    [
        _TEAM_MSG,
        (
            pytest.param(
                _TEAM_MSG,
                id='hahn alerts not suppressed',
                marks=pytest.mark.config(
                    REPLICATION_WEB_CTL={
                        'runtime': {
                            'yt_infra': {'suppress_sync_delay_threshold': 100},
                        },
                    },
                ),
            )
        ),
        (
            pytest.param(
                '2; CRIT (4 problems): '
                '[Task mongo -> queue_mongo delay from now is too great '
                'https://unittests/replications/show/test_api_basestamp]: '
                'test_rule = 393904 sec > 23 sec, '
                '[Task mongo -> queue_mongo has no successful runs '
                'https://unittests/replications/show/test_api_basestamp]: '
                'test_rule = 3681 min > 18 min, '
                '[Task queue_mongo -> yt has no successful runs]: '
                'basic_source_mongo_snapshot-arni = 2241 min > 35 min, '
                'test_rule-*-arni = 2241 min > 16 min',
                id='hahn alerts suppressed',
                marks=pytest.mark.config(
                    REPLICATION_WEB_CTL={
                        'runtime': {
                            'yt_infra': {'suppress_sync_delay_threshold': 600},
                        },
                    },
                ),
            )
        ),
    ],
)
async def test_team_replication_checks(replication_ctx, expected):
    res = await team_check.run_team_check(
        replication_ctx, team_check_type='delay', dev_team='testsuite',
    )
    assert res == expected


@pytest.mark.parametrize(
    'delay_name, expected',
    [
        ('sync-delay', '0; Ok, found 9 initialized targets'),
        ('relative-delay', '0; Ok, found 9 initialized targets'),
        ('delay-from-now', '0; Ok, found 9 initialized targets'),
    ],
)
async def tests_general_replication_delay(
        replication_ctx, delay_name, expected,
):

    res = await general_check.run_general_check(
        replication_ctx, general_check_type=delay_name,
    )
    assert res == expected
