# pylint: disable=protected-access

import pytest

from replication.monrun import general_check
from replication.monrun.checks import check_data


_MODULE = 'replication.monrun.general_check'


async def test_check_data_invalid_docs(replication_ctx):
    msg = await check_data._run_check(
        replication_ctx, [check_data.INVALID_DOCS], dev_team='testsuite',
    )
    assert msg == (
        '1; WARN (1 problem): test_initialize_columns '
        '(stage: target): invalid-docs = 2'
    )


async def test_check_data_queue_monitoring(replication_ctx):
    msg = await check_data._run_check(
        replication_ctx, [check_data.QUEUE_MONITORING], dev_team='testsuite',
    )
    assert (
        msg == '1; WARN (1 problem): test_initialize_columns: too_old_docs = 1'
    )


@pytest.mark.parametrize(
    'check_name, expected',
    [
        (
            check_data.INVALID_DOCS,
            (
                '1; WARN (1 problem): test_initialize_columns '
                '(stage: target): invalid-docs = 2'
            ),
        ),
        (
            check_data.QUEUE_MONITORING,
            '1; WARN (1 problem): test_initialize_columns: too_old_docs = 1',
        ),
    ],
)
async def test_check_data(replication_ctx, check_name, expected):
    res = await general_check.run_general_check(
        replication_ctx, general_check_type=check_name,
    )

    assert res == expected
