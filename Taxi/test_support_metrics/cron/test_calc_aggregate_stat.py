# pylint: disable=redefined-outer-name
import datetime
import json

import asyncpg.exceptions as apg_exc
import freezegun
import pytest
import pytz

from support_metrics.aggregated_statistics import manager
from support_metrics.aggregated_statistics import stat_calculator
from support_metrics.generated.cron import run_cron
from . import expected_calc_aggregate_stat as expected


NOW = datetime.datetime(2019, 7, 2, 12, 2, 23)


async def _check_result(db, expected_result, expected_updated_time=None):
    result = await db.primary_fetch(
        'SELECT * FROM events.aggregated_stat ORDER BY id ASC',
    )
    expected_stat = sorted(expected_result, key=lambda x: x['id'])
    assert len(expected_result) == len(result)
    for i, record in enumerate(result):
        assert record['id'] == expected_stat[i]['id'], dict(record)
        assert record['source'] == expected_stat[i]['source']
        assert record['created_ts'] == expected_stat[i]['created_ts']
        if expected_updated_time:
            assert record['updated_ts'] == expected_updated_time.replace(
                tzinfo=pytz.utc,
            )
        assert record['sent'] == expected_stat[i]['sent']
        assert json.loads(record['stat']) == expected_stat[i]['stat']


@pytest.mark.config(
    SUPPORT_METRICS_SIMULTANEOUS_CALCULATION=False,
    SUPPORT_METRICS_AGGREGATE_LINES_BACKLOG_ENABLED=True,
    CHATTERBOX_LINES={
        'first': {'mode': 'online'},
        'second': {'mode': 'offline'},
    },
    CHATTERBOX_STAT_IVR_CALLS_SETTINGS={
        'success_call': {
            'conditions': [
                {'lower_limit': 20, 'name': 'gt20'},
                {'upper_limit': 20, 'name': 'lt20'},
                {'lower_limit': 20, 'upper_limit': 40, 'name': 'gt20_lt40'},
            ],
        },
        'missed_call': {'conditions': [{'lower_limit': 20, 'name': 'gt20'}]},
    },
)
@pytest.mark.parametrize(
    'expected_result, calculators',
    [
        (
            [
                expected.STATS_BY_DAY_02_07_2019
                + expected.STATS_BY_HOUR_12
                + expected.STATS_BY_MINUTE_12_01,
                expected.STATS_BY_DAY_02_07_2019
                + expected.STATS_BY_HOUR_12
                + expected.STATS_BY_MINUTE_12_01
                + expected.STATS_BY_MINUTE_12_02,
            ],
            [
                stat_calculator.CreateCalculator,
                stat_calculator.CreateByLineCalculator,
                stat_calculator.CreateByLoginCalculator,
                stat_calculator.ForwardCalculator,
                stat_calculator.CloseCalculator,
                stat_calculator.CloseChatByLoginCalculator,
                stat_calculator.CloseTicketByLoginCalculator,
                stat_calculator.DismissCalculator,
                stat_calculator.ExportCalculator,
                stat_calculator.CommentCalculator,
                stat_calculator.CommunicateCalculator,
                stat_calculator.FirstAcceptCalculator,
                stat_calculator.FirstAcceptByLineCalculator,
                stat_calculator.FirstAcceptByLoginCalculator,
                stat_calculator.LostCalculator,
                stat_calculator.LostByLineCalculator,
                stat_calculator.LostByLoginCalculator,
                stat_calculator.SlaLineCalculator,
                stat_calculator.SlaSupporterCalculator,
                stat_calculator.SipCallsCalculator,
                stat_calculator.SipSuccessCallsCalculator,
                stat_calculator.SipIncomingCallsCalculator,
                stat_calculator.SipCallsByLoginCalculator,
                stat_calculator.SipSuccessCallsByLoginCalculator,
                stat_calculator.SipIncomingCallsByLoginCalculator,
            ],
        ),
        (
            [
                expected.FIRST_ANSWER_BY_DAY
                + expected.FIRST_ANSWER_BY_HOUR
                + expected.FIRST_ANSWER_BY_12_00,
                expected.FIRST_ANSWER_BY_DAY
                + expected.FIRST_ANSWER_BY_HOUR
                + expected.FIRST_ANSWER_BY_12_00
                + expected.FIRST_ANSWER_BY_12_02,
            ],
            [
                stat_calculator.MaxFirstAnswerByLine,
                stat_calculator.FirstAnswerByLogin,
                stat_calculator.FirstAnswerByLine,
            ],
        ),
        (
            [
                expected.AHT_BY_DAY + expected.AHT_BY_HOUR,
                expected.AHT_BY_DAY + expected.AHT_BY_HOUR,
            ],
            [stat_calculator.AhtByLogin, stat_calculator.AhtByLine],
        ),
        (
            [
                expected.AHT_LINE_LOGIN_BY_DAY
                + expected.AHT_LINE_LOGIN_BY_HOUR,
                expected.AHT_LINE_LOGIN_BY_DAY
                + expected.AHT_LINE_LOGIN_BY_HOUR,
            ],
            [stat_calculator.AhtByLineLogin],
        ),
        (
            [
                expected.SPEED_ANSWER_BY_DAY + expected.SPEED_ANSWER_BY_HOUR,
                expected.SPEED_ANSWER_BY_DAY + expected.SPEED_ANSWER_BY_HOUR,
            ],
            [
                stat_calculator.SpeedAnswerByLine,
                stat_calculator.SpeedAnswerByLogin,
                stat_calculator.SpeedAnswerByLineLogin,
            ],
        ),
        (
            [
                expected.ONLINE_BY_DAY
                + expected.ONLINE_BY_HOUR
                + expected.ONLINE_BY_12_00
                + expected.ONLINE_BY_12_01,
                expected.ONLINE_BY_DAY
                + expected.ONLINE_BY_HOUR
                + expected.ONLINE_BY_12_00
                + expected.ONLINE_BY_12_01
                + expected.ONLINE_BY_12_02
                + expected.ONLINE_BY_12_03,
            ],
            [
                stat_calculator.OnlineByLogin,
                stat_calculator.OnlineByLine,
                stat_calculator.OnlineByProject,
            ],
        ),
        (
            [
                expected.LINES_BACKLOG_BY_DAY_1
                + expected.LINES_BACKLOG_BY_HOUR
                + expected.LINES_BACKLOG_BY_12_00,
                expected.LINES_BACKLOG_BY_DAY_1
                + expected.LINES_BACKLOG_BY_DAY_2
                + expected.LINES_BACKLOG_BY_HOUR
                + expected.LINES_BACKLOG_BY_12_00,
            ],
            [stat_calculator.LinesBacklogAverageCountCalculator],
        ),
        (
            [expected.IVR_SUCCESS_CALL_1, expected.IVR_SUCCESS_CALL_1],
            [stat_calculator.IvrSuccessCallsByLineCalculator],
        ),
        (
            [expected.IVR_MISSED_CALL_1, expected.IVR_MISSED_CALL_1],
            [stat_calculator.IvrMissedCallsByLineCalculator],
        ),
    ],
)
async def test_calc_stat(
        cron_context, expected_result, calculators, monkeypatch,
):
    monkeypatch.setattr(manager, 'STAT_CALCULATORS', calculators)
    with freezegun.freeze_time(NOW - datetime.timedelta(minutes=2)):
        await run_cron.main(
            ['support_metrics.crontasks.calculate_aggregate_stat', '-t', '0'],
        )
    db = cron_context.postgresql.support_metrics[0]
    await _check_result(
        db,
        expected_result[0],
        expected_updated_time=NOW - datetime.timedelta(minutes=2),
    )

    with freezegun.freeze_time(NOW):
        await run_cron.main(
            ['support_metrics.crontasks.calculate_aggregate_stat', '-t', '0'],
        )
    await _check_result(db, expected_result[1])


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    SUPPORT_METRICS_DELAY_BY_INTERVAL={'__default__': 4},
    CHATTERBOX_LINES={
        'first': {'mode': 'online'},
        'second': {'mode': 'offline'},
    },
)
@pytest.mark.parametrize(
    'expected_result, calculators',
    [
        (
            expected.STATS_BY_DAY_02_07_2019
            + expected.STATS_BY_HOUR_12
            + expected.STATS_BY_MINUTE_12_01
            + expected.STATS_BY_MINUTE_12_02,
            [
                stat_calculator.CreateCalculator,
                stat_calculator.CreateByLineCalculator,
                stat_calculator.CreateByLoginCalculator,
                stat_calculator.ForwardCalculator,
                stat_calculator.CloseCalculator,
                stat_calculator.CloseChatByLoginCalculator,
                stat_calculator.CloseTicketByLoginCalculator,
                stat_calculator.DismissCalculator,
                stat_calculator.ExportCalculator,
                stat_calculator.CommentCalculator,
                stat_calculator.CommunicateCalculator,
                stat_calculator.FirstAcceptCalculator,
                stat_calculator.FirstAcceptByLineCalculator,
                stat_calculator.FirstAcceptByLoginCalculator,
                stat_calculator.LostCalculator,
                stat_calculator.LostByLineCalculator,
                stat_calculator.LostByLoginCalculator,
                stat_calculator.SlaLineCalculator,
                stat_calculator.SlaSupporterCalculator,
                stat_calculator.SipCallsCalculator,
                stat_calculator.SipSuccessCallsCalculator,
                stat_calculator.SipIncomingCallsCalculator,
                stat_calculator.SipCallsByLoginCalculator,
                stat_calculator.SipSuccessCallsByLoginCalculator,
                stat_calculator.SipIncomingCallsByLoginCalculator,
            ],
        ),
    ],
)
async def test_calc_stat_big_window(
        cron_context, expected_result, calculators, monkeypatch,
):
    monkeypatch.setattr(manager, 'STAT_CALCULATORS', calculators)

    await run_cron.main(
        ['support_metrics.crontasks.calculate_aggregate_stat', '-t', '0'],
    )
    db = cron_context.postgresql.support_metrics[0]
    await _check_result(db, expected_result, expected_updated_time=NOW)


@pytest.mark.pgsql(
    'support_metrics',
    files=['pg_support_metrics_monitor.sql', 'pg_support_metrics.sql'],
)
@pytest.mark.now((NOW + datetime.timedelta(minutes=5)).isoformat())
@pytest.mark.config(
    CHATTERBOX_LINES={
        'first': {'mode': 'online'},
        'second': {'mode': 'offline'},
    },
)
@pytest.mark.parametrize(
    'expected_result, calculators',
    [
        (
            expected.STATS_BY_DAY_02_07_2019 + expected.STATS_BY_HOUR_12,
            [
                stat_calculator.CreateCalculator,
                stat_calculator.CreateByLineCalculator,
                stat_calculator.CreateByLoginCalculator,
                stat_calculator.ForwardCalculator,
                stat_calculator.CloseCalculator,
                stat_calculator.CloseChatByLoginCalculator,
                stat_calculator.CloseTicketByLoginCalculator,
                stat_calculator.DismissCalculator,
                stat_calculator.ExportCalculator,
                stat_calculator.CommentCalculator,
                stat_calculator.CommunicateCalculator,
                stat_calculator.FirstAcceptCalculator,
                stat_calculator.FirstAcceptByLineCalculator,
                stat_calculator.FirstAcceptByLoginCalculator,
                stat_calculator.LostCalculator,
                stat_calculator.LostByLineCalculator,
                stat_calculator.LostByLoginCalculator,
                stat_calculator.SlaLineCalculator,
                stat_calculator.SlaSupporterCalculator,
                stat_calculator.SipCallsCalculator,
                stat_calculator.SipSuccessCallsCalculator,
                stat_calculator.SipIncomingCallsCalculator,
                stat_calculator.SipCallsByLoginCalculator,
                stat_calculator.SipSuccessCallsByLoginCalculator,
                stat_calculator.SipIncomingCallsByLoginCalculator,
            ],
        ),
    ],
)
async def test_calc_stat_monitor(
        cron_context, expected_result, calculators, monkeypatch,
):
    monkeypatch.setattr(manager, 'STAT_CALCULATORS', calculators)
    await run_cron.main(
        ['support_metrics.crontasks.calculate_aggregate_stat', '-t', '0'],
    )
    db = cron_context.postgresql.support_metrics[0]
    await _check_result(
        db,
        expected_result,
        expected_updated_time=NOW + datetime.timedelta(minutes=5),
    )


@pytest.mark.pgsql(
    'support_metrics', files=['pg_support_metrics_limit_exceed.sql'],
)
@pytest.mark.now((NOW + datetime.timedelta(minutes=5)).isoformat())
async def test_calc_stat_query_limit():
    # if it fails with "asyncpg.exceptions._base.InterfaceError:
    # the number of query arguments cannot exceed 32767"
    # you should decrease AGGREGATED_STAT_CHUNK const
    try:
        await run_cron.main(
            ['support_metrics.crontasks.calculate_aggregate_stat', '-t', '0'],
        )
    # pylint: disable=protected-access
    except apg_exc._base.InterfaceError:
        assert False, 'Decrease AGGREGATED_STAT_CHUNK const'

    assert True
