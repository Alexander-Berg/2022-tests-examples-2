# pylint: disable=redefined-outer-name,unused-variable
import datetime
import logging

import pytest

from taxi_billing_audit.generated.cron import run_cron
from taxi_billing_audit.internal import utils
from test_taxi_billing_audit import conftest as tst
from .support import Markers


MY_LOGGER = 'taxi_billing_audit.crontasks.tasks.journal_vs_tlog_check'

PREFIX = '//home/taxi/unittests/'

NOW = datetime.datetime(2019, 12, 1, 20, 30, 42).strftime('%Y-%m-%d %H:%M:%S')


def _yday(days: int = 1) -> int:
    return utils.to_msec(
        utils.midnight(utils.now() - datetime.timedelta(days=days)),
    )


@pytest.fixture
def today():
    return _yday(0)


@pytest.fixture
def yday():
    return _yday(1)


@pytest.fixture
def yyday():
    return _yday(2)


@pytest.fixture
def yyyday():
    return _yday(3)


async def test_days(today, yday, yyday, yyyday):
    day = 1_000_000 * 60 * 60 * 24
    now = utils.to_msec(utils.now())
    assert isinstance(today, int)
    assert isinstance(yday, int)
    assert isinstance(yyday, int)
    assert isinstance(yyyday, int)
    assert 0 <= now - today < day
    assert today - yday == day
    assert yday - yyday == day
    assert yyday - yyyday == day


@pytest.mark.now(NOW)
@pytest.mark.config(BILLING_AUDIT_JOURNAL_VS_TLOG_CHECK_ENABLED=False)
@pytest.mark.config(BILLING_AUDIT_JOURNAL_VS_TLOG_DAYS_PRESERVE=0)
@pytest.mark.parametrize(
    'task',
    [
        'taxi_billing_audit.crontasks.journal_vs_tlog_check_hahn',
        'taxi_billing_audit.crontasks.journal_vs_tlog_check_arnold',
    ],
)
async def test_checker_disabled(
        patch, caplog, patched_secdist, mocked_yt, mocked_yql, task,
):
    caplog.set_level(logging.INFO, logger=MY_LOGGER)
    await run_cron.main([task, '-t', '0'])

    lines = [x.getMessage() for x in caplog.records if x.name == MY_LOGGER]
    expected_markers = Markers(
        disabled=True, success=False, missing=False, duplicates=False,
    )
    assert expected_markers == Markers.from_log(lines)


@pytest.mark.now(NOW)
@pytest.mark.config(BILLING_AUDIT_JOURNAL_VS_TLOG_CHECK_ENABLED=True)
@pytest.mark.config(BILLING_AUDIT_JOURNAL_VS_TLOG_DAYS_PRESERVE=0)
@pytest.mark.config(BILLING_AUDIT_JOURNAL_VS_TLOG_PATHS=[])
@pytest.mark.parametrize(
    'task',
    [
        'taxi_billing_audit.crontasks.journal_vs_tlog_check_hahn',
        'taxi_billing_audit.crontasks.journal_vs_tlog_check_arnold',
    ],
)
async def test_checker_no_paths(
        patch, caplog, patched_secdist, mocked_yt, mocked_yql, task,
):
    caplog.set_level(logging.INFO, logger=MY_LOGGER)
    await run_cron.main([task, '-t', '0'])

    lines = [x.getMessage() for x in caplog.records if x.name == MY_LOGGER]
    assert not any('task disabled by config' in x for x in lines)
    assert any('tlog path set is empty' in x for x in lines)


@pytest.mark.now(NOW)
@pytest.mark.config(BILLING_AUDIT_JOURNAL_VS_TLOG_CHECK_ENABLED=True)
@pytest.mark.config(BILLING_AUDIT_JOURNAL_VS_TLOG_DAYS_PRESERVE=0)
@pytest.mark.config(
    BILLING_AUDIT_JOURNAL_VS_TLOG_PATHS=[
        'export/tlog/expenses',
        'export/tlog/revenues',
        'export/tlog/payments',
    ],
)
@pytest.mark.parametrize(
    'task',
    [
        'taxi_billing_audit.crontasks.journal_vs_tlog_check_hahn',
        'taxi_billing_audit.crontasks.journal_vs_tlog_check_arnold',
    ],
)
async def test_checker_no_issues(
        patch, caplog, patched_secdist, mocked_yt, mocked_yql, task,
):
    #
    # typical YQL Session for journal_vs_tlog_check:
    # 1. get_last_session_finished() -- expect [[[int]]]
    # 2. check_missing_and_duplicates() -- expect [[[int, int, int]*]]
    # 3. append to the tables results and sessions
    #
    mocked_yql.append(  # get_last_session_finished
        tst.MockedRequest(
            tst.MockedResult(tst.STATUS_COMPLETED, [tst.MockedTable([[0]])]),
        ),
    )
    mocked_yql.append(  # check_missing_and_duplicates
        tst.MockedRequest(
            tst.MockedResult(tst.STATUS_COMPLETED, [tst.MockedTable([])]),
        ),
    )

    caplog.set_level(logging.INFO, logger=MY_LOGGER)
    await run_cron.main([task, '-t', '0'])

    lines = [x.getMessage() for x in caplog.records if x.name == MY_LOGGER]
    assert not any('task disabled by config' in x for x in lines)
    assert not any('tlog path set is empty' in x for x in lines)
    expected_markers = Markers(
        disabled=False, success=True, missing=False, duplicates=False,
    )
    assert expected_markers == Markers.from_log(lines)
    assert expected_markers == Markers.from_db(mocked_yt)


@pytest.mark.now(NOW)
@pytest.mark.config(BILLING_AUDIT_JOURNAL_VS_TLOG_CHECK_ENABLED=True)
@pytest.mark.config(BILLING_AUDIT_JOURNAL_VS_TLOG_DAYS_PRESERVE=0)
@pytest.mark.config(
    BILLING_AUDIT_JOURNAL_VS_TLOG_PATHS=[
        'export/tlog/expenses',
        'export/tlog/revenues',
        'export/tlog/payments',
    ],
)
@pytest.mark.parametrize(
    'task',
    [
        'taxi_billing_audit.crontasks.journal_vs_tlog_check_hahn',
        'taxi_billing_audit.crontasks.journal_vs_tlog_check_arnold',
    ],
)
async def test_checker_has_missing(
        patch, caplog, patched_secdist, mocked_yt, mocked_yql, task,
):
    mocked_yql.append(  # get_last_session_finished
        tst.MockedRequest(
            tst.MockedResult(tst.STATUS_COMPLETED, [tst.MockedTable([[0]])]),
        ),
    )
    mocked_yql.append(  # check_missing_and_duplicates
        tst.MockedRequest(
            tst.MockedResult(
                tst.STATUS_COMPLETED,
                [tst.MockedTable([[101, None, 1], [102, None, 1]])],
            ),
        ),
    )

    caplog.set_level(logging.INFO, logger=MY_LOGGER)
    await run_cron.main([task, '-t', '0'])

    lines = [x.getMessage() for x in caplog.records if x.name == MY_LOGGER]
    expected_markers = Markers(
        disabled=False, success=False, missing=True, duplicates=False,
    )
    assert expected_markers == Markers.from_log(lines)
    assert expected_markers == Markers.from_db(mocked_yt)


@pytest.mark.now(NOW)
@pytest.mark.config(BILLING_AUDIT_JOURNAL_VS_TLOG_CHECK_ENABLED=True)
@pytest.mark.config(BILLING_AUDIT_JOURNAL_VS_TLOG_DAYS_PRESERVE=0)
@pytest.mark.config(
    BILLING_AUDIT_JOURNAL_VS_TLOG_PATHS=[
        'export/tlog/expenses',
        'export/tlog/revenues',
        'export/tlog/payments',
    ],
)
@pytest.mark.parametrize(
    'task',
    [
        'taxi_billing_audit.crontasks.journal_vs_tlog_check_hahn',
        'taxi_billing_audit.crontasks.journal_vs_tlog_check_arnold',
    ],
)
async def test_checker_has_extra(
        patch, caplog, patched_secdist, mocked_yt, mocked_yql, task,
):
    mocked_yql.append(  # get_last_session_finished
        tst.MockedRequest(
            tst.MockedResult(tst.STATUS_COMPLETED, [tst.MockedTable([[0]])]),
        ),
    )
    mocked_yql.append(
        tst.MockedRequest(
            tst.MockedResult(
                tst.STATUS_COMPLETED,
                [tst.MockedTable([[103, 103, 3], [104, 104, 4]])],
            ),
        ),
    )

    caplog.set_level(logging.INFO, logger=MY_LOGGER)
    await run_cron.main([task, '-t', '0'])

    lines = [x.getMessage() for x in caplog.records if x.name == MY_LOGGER]
    expected_markers = Markers(
        disabled=False, success=False, missing=False, duplicates=True,
    )
    assert expected_markers == Markers.from_log(lines)
    assert expected_markers == Markers.from_db(mocked_yt)


@pytest.mark.now(NOW)
@pytest.mark.config(BILLING_AUDIT_JOURNAL_VS_TLOG_CHECK_ENABLED=True)
@pytest.mark.config(BILLING_AUDIT_JOURNAL_VS_TLOG_DAYS_PRESERVE=0)
@pytest.mark.config(
    BILLING_AUDIT_JOURNAL_VS_TLOG_PATHS=[
        'export/tlog/expenses',
        'export/tlog/revenues',
        'export/tlog/payments',
    ],
)
@pytest.mark.parametrize(
    'task',
    [
        'taxi_billing_audit.crontasks.journal_vs_tlog_check_hahn',
        'taxi_billing_audit.crontasks.journal_vs_tlog_check_arnold',
    ],
)
async def test_checker_has_both(
        patch, caplog, patched_secdist, mocked_yt, mocked_yql, task,
):
    mocked_yql.append(  # get_last_session_finished
        tst.MockedRequest(
            tst.MockedResult(tst.STATUS_COMPLETED, [tst.MockedTable([[0]])]),
        ),
    )
    mocked_yql.append(
        tst.MockedRequest(
            tst.MockedResult(
                tst.STATUS_COMPLETED,
                [
                    tst.MockedTable(
                        [
                            [101, None, 1],
                            [102, 102, 2],
                            [103, None, 1],
                            [104, 104, 3],
                        ],
                    ),
                ],
            ),
        ),
    )

    caplog.set_level(logging.INFO, logger=MY_LOGGER)
    await run_cron.main([task, '-t', '0'])

    lines = [x.getMessage() for x in caplog.records if x.name == MY_LOGGER]
    expected_markers = Markers(
        disabled=False, success=False, missing=True, duplicates=True,
    )
    assert expected_markers == Markers.from_log(lines)
    assert expected_markers == Markers.from_db(mocked_yt)


@pytest.mark.now(NOW)
@pytest.mark.config(BILLING_AUDIT_JOURNAL_VS_TLOG_CHECK_ENABLED=True)
@pytest.mark.config(BILLING_AUDIT_JOURNAL_VS_TLOG_DAYS_PRESERVE=0)
@pytest.mark.config(
    BILLING_AUDIT_JOURNAL_VS_TLOG_PATHS=[
        'export/tlog/expenses',
        'export/tlog/revenues',
        'export/tlog/payments',
    ],
)
@pytest.mark.parametrize(
    'task',
    [
        'taxi_billing_audit.crontasks.journal_vs_tlog_check_hahn',
        'taxi_billing_audit.crontasks.journal_vs_tlog_check_arnold',
    ],
)
async def test_journal_partitioning(
        patch, caplog, patched_secdist, mocked_yt, mocked_yql, task,
):
    #
    # typical YQL Session for journal_vs_tlog_check:
    # 1. get_last_session_finished() -- expect [[[int]]]
    # 2. check_missing_and_duplicates() -- expect [[[int, int, int]*]]
    # 3. append to the tables results and sessions
    #
    mocked_yql.append(  # get_last_session_finished
        tst.MockedRequest(
            tst.MockedResult(tst.STATUS_COMPLETED, [tst.MockedTable([[0]])]),
        ),
    )
    mocked_yql.append(  # check_missing_and_duplicates
        tst.MockedRequest(
            tst.MockedResult(tst.STATUS_COMPLETED, [tst.MockedTable([])]),
        ),
    )
    caplog.set_level(logging.INFO, logger=MY_LOGGER)
    await run_cron.main([task, '-t', '0'])

    lines = [x.getMessage() for x in caplog.records]
    # we must remove journal after month or so also and the next assertion
    assert any('replica/api/billing_accounts/journal' in x for x in lines)
    assert any(
        'replica/api/billing_accounts/journal_monthly' in x for x in lines
    )


@pytest.mark.now(NOW)
@pytest.mark.config(BILLING_AUDIT_JOURNAL_VS_TLOG_CHECK_ENABLED=True)
@pytest.mark.config(BILLING_AUDIT_JOURNAL_VS_TLOG_DAYS_PRESERVE=1)
@pytest.mark.config(
    BILLING_AUDIT_JOURNAL_VS_TLOG_PATHS=['export/tlog/something'],
)
@pytest.mark.parametrize(
    'task',
    [
        'taxi_billing_audit.crontasks.journal_vs_tlog_check_hahn',
        'taxi_billing_audit.crontasks.journal_vs_tlog_check_arnold',
    ],
)
@pytest.mark.parametrize(
    'met, skipped', [(0, True), (1, True), (2, False), (3, False)],
)
async def test_checker_already_processed(
        patch,
        caplog,
        patched_secdist,
        mocked_yt,
        mocked_yql,
        taxi_config,
        today,
        yday,
        yyday,
        yyyday,
        task,
        met,
        skipped,
):
    #
    # typical YQL Session for journal_vs_tlog_check:
    # 1. get_last_session_finished() -- expect [[[int]]]
    # 2. check_missing_and_duplicates() -- expect [[[int, int, int]*]]
    # 3. append to the tables results and sessions
    #
    last_met = [today, yday, yyday, yyyday][met]
    mocked_yql.append(  # get_last_session_finished
        tst.MockedRequest(
            tst.MockedResult(
                tst.STATUS_COMPLETED, [tst.MockedTable([[last_met]])],
            ),
        ),
    )
    mocked_yql.append(  # check_missing_and_duplicates
        tst.MockedRequest(
            tst.MockedResult(tst.STATUS_COMPLETED, [tst.MockedTable([])]),
        ),
    )

    caplog.set_level(logging.INFO, logger=MY_LOGGER)
    await run_cron.main([task, '-t', '0'])

    lines = [x.getMessage() for x in caplog.records if x.name == MY_LOGGER]
    assert any(['already checked.' in x for x in lines]) == skipped


@pytest.mark.now(NOW)
@pytest.mark.config(BILLING_AUDIT_JOURNAL_VS_TLOG_CHECK_ENABLED=True)
@pytest.mark.config(BILLING_AUDIT_JOURNAL_VS_TLOG_DAYS_PRESERVE=0)
@pytest.mark.config(
    BILLING_AUDIT_JOURNAL_VS_TLOG_PATHS=[
        'export/tlog/expenses',
        'export/tlog/revenues',
        'export/tlog/payments',
    ],
)
@pytest.mark.parametrize(
    'task',
    [
        'taxi_billing_audit.crontasks.journal_vs_tlog_check_hahn',
        'taxi_billing_audit.crontasks.journal_vs_tlog_check_arnold',
    ],
)
async def test_checker_gap_detected(
        patch, caplog, patched_secdist, mocked_yt, mocked_yql, task, yyyday,
):
    #
    # typical YQL Session for journal_vs_tlog_check:
    # 1. get_last_session_finished() -- expect [[[int]]]
    # 2. check_missing_and_duplicates() -- expect [[[int, int, int]*]]
    # 3. append to the tables results and sessions
    #

    mocked_yql.append(  # get_last_session_finished
        tst.MockedRequest(
            tst.MockedResult(
                tst.STATUS_COMPLETED, [tst.MockedTable([[yyyday]])],
            ),
        ),
    )
    mocked_yql.append(  # check_missing_and_duplicates
        tst.MockedRequest(
            tst.MockedResult(tst.STATUS_COMPLETED, [tst.MockedTable([])]),
        ),
    )

    caplog.set_level(logging.INFO, logger=MY_LOGGER)
    await run_cron.main([task, '-t', '0'])

    lines = [x.getMessage() for x in caplog.records if x.name == MY_LOGGER]
    assert any(['interval extended to' in x for x in lines])
