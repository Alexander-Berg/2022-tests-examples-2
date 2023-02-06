# pylint: disable=redefined-outer-name,unused-variable
import logging

import pytest

from taxi_billing_audit.generated.cron import run_cron
from test_taxi_billing_audit import conftest as tst


MY_LOGGER = 'taxi_billing_audit.crontasks.startrack_ticket_create'

_EXPECTED_TAXI_FAILED_REFUNDS_TABLE = """
||((/orders/abc2 abc2))|GEL|13.2||
||((/orders/abc1 abc1))|RUB|15.45||
"""


@pytest.mark.config(BILLING_AUDIT_STARTRACK_TICKET_CREATE_ENABLED=False)
async def test_checker_disabled(
        caplog, patched_secdist, mocked_startrack, mocked_yt, mocked_yql,
):
    caplog.set_level(logging.INFO, logger=MY_LOGGER)
    await run_cron.main(
        ['taxi_billing_audit.crontasks.startrack_ticket_create', '-t', '0'],
    )
    assert not mocked_startrack.requests


@pytest.mark.config(BILLING_AUDIT_STARTRACK_TICKET_CREATE_ENABLED=True)
async def test_checker_no_issues(
        caplog, patched_secdist, mocked_startrack, mocked_yt, mocked_yql,
):
    #
    # typical startrack_ticket_create session:
    # 1. find_issues -- expect [[[int,str,str,str,dict]*]]
    # 2. call startrek (if find_issues found something)
    # 3. append the table tickets
    #
    mocked_yql.append(
        tst.MockedRequest(tst.MockedResult(tst.STATUS_COMPLETED, [])),
    )
    caplog.set_level(logging.INFO, logger=MY_LOGGER)
    await run_cron.main(
        ['taxi_billing_audit.crontasks.startrack_ticket_create', '-t', '0'],
    )
    assert not mocked_yt.read_table(tst.YT_DIR + 'results').rows
    assert not mocked_startrack.requests


@pytest.mark.config(BILLING_AUDIT_STARTRACK_TICKET_CREATE_ENABLED=True)
async def test_checker_some_issues(
        caplog, patched_secdist, mocked_startrack, mocked_yt, mocked_yql,
):
    mocked_yql.append(
        tst.MockedRequest(
            tst.MockedResult(
                tst.STATUS_COMPLETED,
                [
                    tst.MockedTable(
                        data=[
                            [
                                'session1',
                                '2019-08-10',
                                'CHECK_MISSING',
                                'FAILED',
                                {'missing_ids': [123, 456]},
                                'JOURNAL_VS_TLOG',
                            ],
                            [
                                'session1',
                                '2019-08-10',
                                'CHECK_DUPLICATES',
                                'FAILED',
                                {'duplicate_ids': [789]},
                                'JOURNAL_VS_TLOG',
                            ],
                            [
                                'session2',
                                '2019-08-11',
                                'CHECK_MISSING',
                                'FAILED',
                                {'missing_ids': [991, 992, 993]},
                                'JOURNAL_VS_TLOG',
                            ],
                            [
                                'session3',
                                '2019-08-11',
                                'CHECK_DIFFERENCES',
                                'FAILED',
                                {
                                    'difference': [
                                        {
                                            'Accounts': {
                                                'amount': '1',
                                                'count': '1',
                                                'currency': 'KAZ',
                                            },
                                            'YT': {},
                                        },
                                        {
                                            'Accounts': {},
                                            'YT': {
                                                'amount': '13',
                                                'count': '1',
                                                'currency': 'EUR',
                                            },
                                        },
                                        {
                                            'Accounts': {
                                                'amount': '40',
                                                'count': '12',
                                                'currency': 'RUB',
                                            },
                                            'YT': {
                                                'amount': '42.0000',
                                                'count': '12',
                                                'currency': 'RUB',
                                            },
                                        },
                                    ],
                                },
                                'JOURNAL_VS_TLOG',
                            ],
                            [
                                'session4',
                                '2019-08-19',
                                'CHECK_DOCS_VS_YT_ISSUES',
                                'FAILED',
                                {
                                    'not_calculated': [
                                        {'hour': 456000, 'shard': 1},
                                    ],
                                    'not_replicated': [
                                        {'hour': 456001, 'shard': 12},
                                        {'hour': 456001, 'shard': 13},
                                    ],
                                    'mismatch_num': [
                                        {'hour': 456002, 'shard': 111},
                                        {'hour': 456002, 'shard': 112},
                                        {'hour': 456003, 'shard': 112},
                                    ],
                                    'mismatch_hash': [
                                        {'hour': 456004, 'shard': 111},
                                    ],
                                },
                                'DOCS_VS_YT',
                            ],
                            [
                                'session5',
                                '2019-10-21',
                                'CHECK_DOCS_VS_YT_ISSUES',
                                'FAILED',
                                {
                                    'bad_num': {
                                        '1': [
                                            {
                                                'id_begin': 10000201,
                                                'id_end': 10000210,
                                                'pg_num': 1000,
                                                'yt_num': 1010,
                                            },
                                            {
                                                'id_begin': 10000210,
                                                'id_end': 10000220,
                                                'pg_num': 100,
                                                'yt_num': 99,
                                            },
                                        ],
                                        '123': [
                                            {
                                                'id_begin': 12300,
                                                'id_end': 12345,
                                                'pg_num': 1000,
                                                'yt_num': 0,
                                            },
                                        ],
                                    },
                                    'bad_hash': {
                                        '1': [
                                            {
                                                'id_begin': 1000,
                                                'id_end': 1010,
                                                'pg_hash': 1111,
                                                'yt_hash': 9999,
                                            },
                                        ],
                                    },
                                },
                                'DOCS_VS_YT',
                            ],
                            [
                                'session6',
                                '2019-10-21',
                                'CHECK_ACCOUNTS_VS_YT_DIFF',
                                'FAILED',
                                {
                                    'actual_amount': '-89.8472',
                                    'actual_count': 40,
                                    'currency': 'RUB',
                                    'expected_amount': '210.1528',
                                    'expected_count': 50,
                                    'max_id': 910150,
                                    'min_id': 410150,
                                    'shard_id': 150,
                                },
                                'JOURNAL_VS_YT_V3',
                            ],
                            [
                                'session7',
                                '2020-05-08',
                                'CHECK_COMPENSATION_REFUNDS',
                                'FAILED',
                                {
                                    'orders': [
                                        {
                                            'id': 'abc1',
                                            'currency': 'RUB',
                                            'lacking_refunds': '100500.0',
                                        },
                                        {
                                            'id': 'abc2',
                                            'currency': 'GEL',
                                            'lacking_refunds': '1050.0',
                                        },
                                        {
                                            'id': 'abc3',
                                            'currency': 'USD',
                                            'lacking_refunds': '15.0',
                                        },
                                    ],
                                },
                                'COMPENSATION_REFUNDS',
                            ],
                            [
                                'session8',
                                '2020-09-15',
                                'CHECK_TAXI_FAILED_REFUNDS',
                                'FAILED',
                                {
                                    'orders': [
                                        {
                                            'id': 'abc1',
                                            'currency': 'RUB',
                                            'refund_sum': 15.45,
                                        },
                                        {
                                            'id': 'abc2',
                                            'currency': 'GEL',
                                            'refund_sum': 13.2,
                                        },
                                    ],
                                },
                                'TAXI_FAILED_REFUNDS',
                            ],
                        ],
                        names=[
                            'id',
                            'day',
                            'check_type',
                            'outcome',
                            'details',
                        ],
                        types=['string', 'string', 'string', 'string', 'any'],
                    ),
                ],
            ),
        ),
    )
    caplog.set_level(logging.INFO, logger=MY_LOGGER)
    await run_cron.main(
        ['taxi_billing_audit.crontasks.startrack_ticket_create', '-t', '0'],
    )
    requests = mocked_startrack.requests
    print('--------- REQUESTS BEGIN ----------')
    for req in requests:
        print(req)
    print('--------- REQUESTS END ----------')
    assert len(mocked_startrack.requests) == 8
    assert '[123, 456]' in requests[0].json['description']
    assert '[789]' in requests[0].json['description']
    assert '[991, 992, 993]' in requests[1].json['description']
    assert '42.0000 RUB (YT)' in requests[2].json['description']
    assert '40 RUB (Accounts)' in requests[2].json['description']
    assert '1 KAZ (Accounts)' in requests[2].json['description']
    assert (
        '[{\'hour\': 456000, \'shard\': 1}]' in requests[3].json['description']
    )
    assert (
        '[{\'hour\': 456001, \'shard\': 12}, '
        '{\'hour\': 456001, \'shard\': 13}]' in requests[3].json['description']
    )
    assert (
        '[{\'hour\': 456002, \'shard\': 111}, '
        '{\'hour\': 456002, \'shard\': 112}, '
        '{\'hour\': 456003, \'shard\': 112}]'
        in requests[3].json['description']
    )
    assert (
        '[{\'hour\': 456004, \'shard\': 111}]'
        in requests[3].json['description']
    )
    assert (
        '||1|10000201|10000210|1000|1010||' in requests[4].json['description']
    )
    assert '||1|10000210|10000220|100|99||' in requests[4].json['description']
    assert '||123|12300|12345|1000|0||' in requests[4].json['description']
    assert '||1|1000|1010|1111|9999||' in requests[4].json['description']
    assert '[410150...910150]' in requests[5].json['description']
    assert '||abc1|RUB|100500.0||\n' in requests[6].json['description']
    assert '||abc2|GEL|1050.0||\n' in requests[6].json['description']
    assert '||abc3|USD|15.0||\n' in requests[6].json['description']
    assert 'RUB 100500.0' in requests[6].json['description']
    assert 'GEL 1050.0' in requests[6].json['description']
    assert 'USD 15.0' in requests[6].json['description']
    assert (
        _EXPECTED_TAXI_FAILED_REFUNDS_TABLE in requests[7].json['description']
    )
    rows = mocked_yt.read_table(tst.YT_DIR + 'tickets').rows
    assert len(rows) == 8
    assert rows[0][0] > 0
    assert rows[0][1] == 'session1'
    assert rows[0][2] != ''
    assert rows[1][0] > 0
    assert rows[1][1] == 'session2'
    assert rows[1][2] != ''
    assert rows[2][0] > 0
    assert rows[2][1] == 'session3'
    assert rows[2][2] != ''
    assert rows[3][0] > 0
    assert rows[3][1] == 'session4'
    assert rows[3][2] != ''
    assert rows[4][0] > 0
    assert rows[4][1] == 'session5'
    assert rows[4][2] != ''
    assert rows[5][1] == 'session6'
    assert rows[5][2] != ''
    assert rows[6][0] > 0
    assert rows[6][1] == 'session7'
    assert rows[6][2] != ''
    assert rows[6][0] > 0
    assert rows[7][1] == 'session8'
    assert rows[7][2] != ''
