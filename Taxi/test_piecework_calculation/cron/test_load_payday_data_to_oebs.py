import copy
import datetime

import pytest

from piecework_calculation import constants
from piecework_calculation import payday
from piecework_calculation.generated.cron import run_cron


NOW = datetime.datetime(2022, 2, 20, 10, 5, 15, 123456)
EARLY = datetime.datetime(2022, 1, 31, 16, 59, 0)


NOT_LOAD_DATA_DB_STATE = [
    {
        'loan_id': '1',
        'updated': NOW,
        'status': constants.PAYDAY_TRANSACTION_FAILED_STATUS,
    },
    {
        'loan_id': '11',
        'updated': EARLY,
        'status': constants.PAYDAY_TRANSACTION_SENT_STATUS,
    },
    {
        'loan_id': '2',
        'updated': NOW,
        'status': constants.PAYDAY_TRANSACTION_FAILED_STATUS,
    },
    {
        'loan_id': '21',
        'updated': NOW,
        'status': constants.PAYDAY_TRANSACTION_FAILED_STATUS,
    },
    {
        'loan_id': '211',
        'updated': NOW,
        'status': constants.PAYDAY_TRANSACTION_FAILED_STATUS,
    },
    {
        'loan_id': '3',
        'updated': NOW,
        'status': constants.PAYDAY_TRANSACTION_FAILED_STATUS,
    },
    {
        'loan_id': '31',
        'updated': NOW,
        'status': constants.PAYDAY_TRANSACTION_FAILED_STATUS,
    },
    {
        'loan_id': '4',
        'updated': NOW,
        'status': constants.PAYDAY_TRANSACTION_FAILED_STATUS,
    },
    {
        'loan_id': '4_f',
        'updated': NOW,
        'status': constants.PAYDAY_TRANSACTION_FAILED_STATUS,
    },
    {
        'loan_id': '4_s',
        'updated': EARLY,
        'status': constants.PAYDAY_TRANSACTION_SENT_STATUS,
    },
    {
        'loan_id': '5',
        'updated': EARLY,
        'status': constants.PAYDAY_TRANSACTION_FAILED_STATUS,
    },
]


EXPECTED_PAYDAY_REQUEST = {
    'name': '2022-02-20T10:05:15.123456_0',
    'people': [
        {
            'login': 'test_1',
            'employeeTypes': [
                {
                    'employeeType': 'S',
                    'transactions': [
                        {
                            'paymentDate': '2022-02-20T00:00:00+07:00',
                            'transactionId': '1',
                            'paymentSum': 15.5,
                        },
                    ],
                },
            ],
        },
        {
            'login': 'test_2',
            'employeeTypes': [
                {
                    'employeeType': 'S',
                    'transactions': [
                        {
                            'paymentDate': '2022-02-15T23:00:00+08:00',
                            'transactionId': '2',
                            'paymentSum': 16.5,
                        },
                        {
                            'paymentDate': '2022-02-16T23:00:00+08:00',
                            'transactionId': '21',
                            'paymentSum': 18.5,
                        },
                        {
                            'paymentDate': '2022-02-28T15:59:00+08:00',
                            'transactionId': '211',
                            'paymentSum': 18.5,
                        },
                    ],
                },
            ],
        },
        {
            'login': 'test_3',
            'employeeTypes': [
                {
                    'employeeType': 'S',
                    'transactions': [
                        {
                            'paymentDate': '2022-02-24T15:00:00+03:00',
                            'transactionId': '3',
                            'paymentSum': 13.5,
                        },
                        {
                            'paymentDate': '2022-02-24T11:00:00+03:00',
                            'transactionId': '31',
                            'paymentSum': 16.5,
                        },
                    ],
                },
            ],
        },
        {
            'login': 'test_4',
            'employeeTypes': [
                {
                    'employeeType': 'S',
                    'transactions': [
                        {
                            'paymentDate': '2022-02-26T23:00:00+05:00',
                            'transactionId': '4',
                            'paymentSum': 12.5,
                        },
                        {
                            'paymentDate': '2022-02-24T23:00:00+05:00',
                            'transactionId': '4_f',
                            'paymentSum': 112.5,
                        },
                    ],
                },
            ],
        },
    ],
}


def check_payday_calls(
        mocked_payday_upload,
        expected_payday_times_called,
        expected_payday_request,
        deleted_transaction=None,
        change_payday_request=True,
):
    assert mocked_payday_upload.times_called == expected_payday_times_called
    people = copy.deepcopy(expected_payday_request['people'])
    for i in range(expected_payday_times_called):
        current_people = people
        payday_request = mocked_payday_upload.next_call()['request'].json
        payday_request['people'] = list(
            sorted(payday_request['people'], key=lambda x: x['login']),
        )
        for login in payday_request['people']:
            login['employeeTypes'][0]['transactions'] = list(
                sorted(
                    login['employeeTypes'][0]['transactions'],
                    key=lambda x: x['transactionId'],
                ),
            )
        packet_name = expected_payday_request['name'][:-1] + str(i)
        if i > 0 and deleted_transaction:
            people[-1]['employeeTypes'][0]['transactions'] = list(
                filter(
                    lambda x: x['transactionId'] != deleted_transaction,
                    people[-1]['employeeTypes'][0]['transactions'],
                ),
            )
            if not people[-1]['employeeTypes'][0]['transactions']:
                del people[-1]
        elif change_payday_request and i:
            current_people = people[:-i]

        current_expected_payday_request = {
            'name': packet_name,
            'people': current_people,
        }
        assert payday_request == current_expected_payday_request


async def check_db_transactions_status(cron_context, expected_statuses):
    async with cron_context.pg.slave_pool.acquire() as conn:
        pg_results = await conn.fetch(
            'SELECT loan_id, updated, oebs_sent_status AS status '
            'FROM piecework.payday_employee_loan ORDER BY loan_id',
        )
        pg_results = [dict(item) for item in pg_results]
        assert pg_results == expected_statuses


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'payday_response, expected_payday_request, expected_payday_times_called,'
    'expected_db_statuses',
    [
        (
            {'status': constants.PAYDAY_SUCCESS_STATUS},
            EXPECTED_PAYDAY_REQUEST,
            1,
            [
                {
                    'loan_id': '1',
                    'updated': NOW,
                    'status': constants.PAYDAY_TRANSACTION_SENT_STATUS,
                },
                {
                    'loan_id': '11',
                    'updated': EARLY,
                    'status': constants.PAYDAY_TRANSACTION_SENT_STATUS,
                },
                {
                    'loan_id': '2',
                    'updated': NOW,
                    'status': constants.PAYDAY_TRANSACTION_SENT_STATUS,
                },
                {
                    'loan_id': '21',
                    'updated': NOW,
                    'status': constants.PAYDAY_TRANSACTION_SENT_STATUS,
                },
                {
                    'loan_id': '211',
                    'updated': NOW,
                    'status': constants.PAYDAY_TRANSACTION_SENT_STATUS,
                },
                {
                    'loan_id': '3',
                    'updated': NOW,
                    'status': constants.PAYDAY_TRANSACTION_SENT_STATUS,
                },
                {
                    'loan_id': '31',
                    'updated': NOW,
                    'status': constants.PAYDAY_TRANSACTION_SENT_STATUS,
                },
                {
                    'loan_id': '4',
                    'updated': NOW,
                    'status': constants.PAYDAY_TRANSACTION_SENT_STATUS,
                },
                {
                    'loan_id': '4_f',
                    'updated': NOW,
                    'status': constants.PAYDAY_TRANSACTION_SENT_STATUS,
                },
                {
                    'loan_id': '4_s',
                    'updated': EARLY,
                    'status': constants.PAYDAY_TRANSACTION_SENT_STATUS,
                },
                {
                    'loan_id': '5',
                    'updated': EARLY,
                    'status': constants.PAYDAY_TRANSACTION_FAILED_STATUS,
                },
            ],
        ),
    ],
)
async def test_load_payday_data(
        cron_context,
        mock_payday_upload,
        payday_response,
        expected_payday_request,
        expected_payday_times_called,
        expected_db_statuses,
):
    mocked_payday_upload = mock_payday_upload(payday_response)

    await run_cron.main(
        [
            'piecework_calculation.crontasks.load_payday_data_to_oebs',
            '-t',
            '0',
        ],
    )

    check_payday_calls(
        mocked_payday_upload,
        expected_payday_times_called,
        expected_payday_request,
    )
    await check_db_transactions_status(cron_context, expected_db_statuses)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'payday_response, expected_payday_request, expected_payday_times_called, '
    'expected_error, oebs_sent_status, expected_db_statuses, '
    'expected_deleted_transaction',
    [
        (
            {
                'status': 'ERROR',
                'people': [
                    {
                        'login': '',
                        'errors': [{'errorCode': 'ASSIGNMENT_NOT_FOUND'}],
                        'employeeTypes': [
                            {
                                'employeeType': 'S',
                                'transactions': [
                                    {
                                        'transactionId': 'bad_transaction',
                                        'errors': [
                                            {
                                                'errorCode': (
                                                    'ASSIGNMENT_NOT_FOUND'
                                                ),
                                            },
                                        ],
                                    },
                                ],
                            },
                        ],
                    },
                ],
            },
            EXPECTED_PAYDAY_REQUEST,
            3,
            payday.OebsPaydayUploadError,
            None,
            NOT_LOAD_DATA_DB_STATE,
            None,
        ),
        (
            {
                'status': 'ERROR',
                'people': [
                    {
                        'login': 'test_1',
                        'errors': None,
                        'employeeTypes': [
                            {
                                'employeeType': 'S',
                                'transactions': [
                                    {
                                        'transactionId': '1',
                                        'errors': [
                                            {
                                                'errorCode': (
                                                    'ASSIGNMENT_NOT_FOUND'
                                                ),
                                            },
                                        ],
                                    },
                                ],
                            },
                        ],
                    },
                ],
            },
            EXPECTED_PAYDAY_REQUEST,
            3,
            payday.OebsPaydayUploadError,
            None,
            NOT_LOAD_DATA_DB_STATE,
            '1',
        ),
        (
            {
                'status': 'ERROR',
                'people': [
                    {
                        'login': '',
                        'errors': [{'errorCode': 'not period for login'}],
                    },
                ],
            },
            EXPECTED_PAYDAY_REQUEST,
            2,
            payday.OebsPaydayUploadLoginError,
            constants.PAYDAY_SUCCESS_STATUS,
            [
                {
                    'loan_id': '1',
                    'updated': NOW,
                    'status': constants.PAYDAY_TRANSACTION_SENT_STATUS,
                },
                {
                    'loan_id': '11',
                    'updated': EARLY,
                    'status': constants.PAYDAY_TRANSACTION_SENT_STATUS,
                },
                {
                    'loan_id': '2',
                    'updated': NOW,
                    'status': constants.PAYDAY_TRANSACTION_SENT_STATUS,
                },
                {
                    'loan_id': '21',
                    'updated': NOW,
                    'status': constants.PAYDAY_TRANSACTION_SENT_STATUS,
                },
                {
                    'loan_id': '211',
                    'updated': NOW,
                    'status': constants.PAYDAY_TRANSACTION_SENT_STATUS,
                },
                {
                    'loan_id': '3',
                    'updated': NOW,
                    'status': constants.PAYDAY_TRANSACTION_SENT_STATUS,
                },
                {
                    'loan_id': '31',
                    'updated': NOW,
                    'status': constants.PAYDAY_TRANSACTION_SENT_STATUS,
                },
                {
                    'loan_id': '4',
                    'updated': NOW,
                    'status': constants.PAYDAY_TRANSACTION_FAILED_STATUS,
                },
                {
                    'loan_id': '4_f',
                    'updated': NOW,
                    'status': constants.PAYDAY_TRANSACTION_FAILED_STATUS,
                },
                {
                    'loan_id': '4_s',
                    'updated': EARLY,
                    'status': constants.PAYDAY_TRANSACTION_SENT_STATUS,
                },
                {
                    'loan_id': '5',
                    'updated': EARLY,
                    'status': constants.PAYDAY_TRANSACTION_FAILED_STATUS,
                },
            ],
            None,
        ),
        (
            {
                'status': 'ERROR',
                'people': [
                    {
                        'login': '',
                        'employeeTypes': [
                            {
                                'employeeType': 'S',
                                'transactions': [
                                    {
                                        'transactionId': '4',
                                        'errors': [
                                            {
                                                'errorCode': (
                                                    'ASSIGNMENT_NOT_FOUND'
                                                ),
                                            },
                                        ],
                                    },
                                ],
                            },
                        ],
                    },
                ],
            },
            EXPECTED_PAYDAY_REQUEST,
            2,
            payday.OebsPaydayUploadTransactionError,
            constants.PAYDAY_SUCCESS_STATUS,
            [
                {
                    'loan_id': '1',
                    'updated': NOW,
                    'status': constants.PAYDAY_TRANSACTION_SENT_STATUS,
                },
                {
                    'loan_id': '11',
                    'updated': EARLY,
                    'status': constants.PAYDAY_TRANSACTION_SENT_STATUS,
                },
                {
                    'loan_id': '2',
                    'updated': NOW,
                    'status': constants.PAYDAY_TRANSACTION_SENT_STATUS,
                },
                {
                    'loan_id': '21',
                    'updated': NOW,
                    'status': constants.PAYDAY_TRANSACTION_SENT_STATUS,
                },
                {
                    'loan_id': '211',
                    'updated': NOW,
                    'status': constants.PAYDAY_TRANSACTION_SENT_STATUS,
                },
                {
                    'loan_id': '3',
                    'updated': NOW,
                    'status': constants.PAYDAY_TRANSACTION_SENT_STATUS,
                },
                {
                    'loan_id': '31',
                    'updated': NOW,
                    'status': constants.PAYDAY_TRANSACTION_SENT_STATUS,
                },
                {
                    'loan_id': '4',
                    'updated': NOW,
                    'status': constants.PAYDAY_TRANSACTION_FAILED_STATUS,
                },
                {
                    'loan_id': '4_f',
                    'updated': NOW,
                    'status': constants.PAYDAY_TRANSACTION_SENT_STATUS,
                },
                {
                    'loan_id': '4_s',
                    'updated': EARLY,
                    'status': constants.PAYDAY_TRANSACTION_SENT_STATUS,
                },
                {
                    'loan_id': '5',
                    'updated': EARLY,
                    'status': constants.PAYDAY_TRANSACTION_FAILED_STATUS,
                },
            ],
            '4',
        ),
    ],
)
async def test_load_payday_data_error(
        cron_context,
        mock_payday_upload,
        payday_response,
        expected_payday_request,
        expected_payday_times_called,
        expected_error,
        oebs_sent_status,
        expected_db_statuses,
        expected_deleted_transaction,
):
    mocked_payday_upload = mock_payday_upload(
        payday_response, status=oebs_sent_status,
    )

    with pytest.raises(expected_error):
        await run_cron.main(
            [
                'piecework_calculation.crontasks.load_payday_data_to_oebs',
                '-t',
                '0',
            ],
        )

    check_payday_calls(
        mocked_payday_upload,
        expected_payday_times_called,
        expected_payday_request,
        deleted_transaction=expected_deleted_transaction,
    )
    await check_db_transactions_status(cron_context, expected_db_statuses)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'payday_response, expected_payday_request, expected_payday_times_called, '
    'expected_error, mock_login, expected_db_statuses',
    [
        (
            {
                'status': 'ERROR',
                'people': [
                    {
                        'login': '',
                        'employeeTypes': [
                            {'employeeType': 'S', 'transactions': []},
                        ],
                    },
                ],
            },
            EXPECTED_PAYDAY_REQUEST,
            3,
            payday.OebsPaydayUploadError,
            None,
            NOT_LOAD_DATA_DB_STATE,
        ),
        (
            {
                'status': 'ERROR',
                'people': [
                    {'login': '', 'employeeTypes': [{'employeeType': 'S'}]},
                ],
            },
            EXPECTED_PAYDAY_REQUEST,
            3,
            payday.OebsPaydayUploadError,
            None,
            NOT_LOAD_DATA_DB_STATE,
        ),
        (
            {
                'status': 'ERROR',
                'people': [
                    {
                        'login': 'not_sent_login',
                        'employeeTypes': [
                            {
                                'employeeType': 'S',
                                'transactions': [
                                    {
                                        'transactionId': '4',
                                        'errors': [
                                            {
                                                'errorCode': (
                                                    'ASSIGNMENT_NOT_FOUND'
                                                ),
                                            },
                                        ],
                                    },
                                ],
                            },
                        ],
                    },
                ],
            },
            EXPECTED_PAYDAY_REQUEST,
            3,
            payday.OebsPaydayUploadError,
            'not_sent_login',
            NOT_LOAD_DATA_DB_STATE,
        ),
        (
            {
                'status': 'ERROR',
                'people': [
                    {
                        'login': '',
                        'employeeTypes': [
                            {
                                'employeeType': 'S',
                                'transactions': [
                                    {
                                        'transactionId': (
                                            'not_sent_transaction'
                                        ),
                                        'errors': [
                                            {
                                                'errorCode': (
                                                    'ASSIGNMENT_NOT_FOUND'
                                                ),
                                            },
                                        ],
                                    },
                                ],
                            },
                        ],
                    },
                ],
            },
            EXPECTED_PAYDAY_REQUEST,
            3,
            payday.OebsPaydayUploadError,
            None,
            NOT_LOAD_DATA_DB_STATE,
        ),
    ],
)
async def test_load_payday_data_error_not_change(
        cron_context,
        mock_payday_upload,
        payday_response,
        expected_payday_request,
        expected_payday_times_called,
        expected_error,
        mock_login,
        expected_db_statuses,
):
    mocked_payday_upload = mock_payday_upload(
        payday_response, login=mock_login,
    )

    with pytest.raises(expected_error):
        await run_cron.main(
            [
                'piecework_calculation.crontasks.load_payday_data_to_oebs',
                '-t',
                '0',
            ],
        )

    check_payday_calls(
        mocked_payday_upload,
        expected_payday_times_called,
        expected_payday_request,
        change_payday_request=False,
    )
    await check_db_transactions_status(cron_context, expected_db_statuses)
