# pylint: disable=protected-access

import datetime

import pytest

from replication.monrun import general_check

NOW = datetime.datetime(2018, 11, 14, 12, 0)


_CHECK_NAME = 'archiving-delay'


@pytest.mark.config(
    REPLICATION_SERVICE_CTL={'archiving': {'disable_all': True}},
)
async def test_check_archiving_disabled(replication_ctx):
    res = await general_check.run_general_check(
        replication_ctx, general_check_type=_CHECK_NAME,
    )
    assert res == '1; Archiving disabled'


@pytest.mark.config(
    REPLICATION_SERVICE_CTL={
        'archiving': {'disabled': ['queue_mongo-staging_test_rule']},
    },
    REPLICATION_MONRUN_THRESHOLDS={
        'archiving_delay': {
            '__default__': {
                'archiving_delay': {'warning': 600, 'critical': 900},
            },
        },
    },
)
@pytest.mark.now(NOW.isoformat())
async def test_check_rule_disabled(replication_ctx):
    res = await general_check.run_general_check(
        replication_ctx, general_check_type=_CHECK_NAME,
    )
    assert res == '0; OK'


@pytest.mark.config(
    REPLICATION_MONRUN_THRESHOLDS={
        'archiving_delay': {
            '__disabled__': ['queue_mongo-staging_test_rule'],
            '__default__': {
                'archiving_delay': {'warning': 600, 'critical': 900},
            },
        },
    },
)
@pytest.mark.now(NOW.isoformat())
async def test_check_check_disabled(replication_ctx):
    res = await general_check.run_general_check(
        replication_ctx, general_check_type=_CHECK_NAME,
    )
    assert res == '0; OK'


@pytest.mark.config(
    REPLICATION_MONRUN_THRESHOLDS={
        'archiving_delay': {
            '__default__': {
                'archiving_delay': {'warning': 600, 'critical': 900},
            },
        },
    },
)
@pytest.mark.now(NOW.isoformat())
async def test_check_archiving_crit(replication_ctx):
    res = await general_check.run_general_check(
        replication_ctx, general_check_type=_CHECK_NAME,
    )
    assert res == (
        '2; CRIT (1 problem): queue_mongo-staging_test_rule: '
        'archiving_delay = 1980 min'
    )


@pytest.mark.config(
    REPLICATION_MONRUN_THRESHOLDS={
        'archiving_delay': {
            '__default__': {
                'archiving_delay': {'warning': 600, 'critical': 900},
            },
        },
    },
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.filldb(replication_state='empty')
async def test_check_archiving_no_init(replication_ctx):
    res = await general_check.run_general_check(
        replication_ctx, general_check_type=_CHECK_NAME,
    )
    assert res == '0; OK'


@pytest.mark.config(
    REPLICATION_MONRUN_THRESHOLDS={
        'archiving_delay': {
            '__default__': {
                'archiving_delay': {'warning': 600, 'critical': 900},
            },
        },
    },
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.filldb(replication_settings='empty')
async def test_check_archiving_ok(replication_ctx):
    res = await general_check.run_general_check(
        replication_ctx, general_check_type=_CHECK_NAME,
    )
    assert res == '0; OK'
