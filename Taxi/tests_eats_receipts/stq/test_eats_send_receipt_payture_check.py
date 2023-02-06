import pytest

CHEQUE_DATA = {
    'Sended': True,
    'Status': 'Accepted',
    'Cheque': {
        'Content': {
            'Type': 1,
            'Positions': [
                {'Quantity': 1.23, 'Price': 12.3, 'Tax': 1, 'Text': 'Cola'},
            ],
            'CheckClose': {
                'Payments': [{'Type': 1, 'Amount': 22}],
                'TaxationSystem': 5,
            },
            'CustomerContact': '79995554444',
        },
        'Id': '1',
        'DeviceSN': 'devicesn',
        'DeviceRN': 'device_rn',
        'FSNumber': 'fsnumber',
        'OFDName': 'ofd_name',
        'OFDWebsite': 'ofdwebsite',
        'OFDINN': 'ofdinn',
        'FNSWebsite': 'fnswebsite',
        'CompanyINN': 'companyinn',
        'CompanyName': 'companyname',
        'DocumentNumber': 123,
        'ShiftNumber': 123,
        'DocumentIndex': 1,
        'ProcessedAt': 'processedat',
        'Change': 123.1,
        'FP': 'fiscal_sign',
    },
}


@pytest.mark.now('2021-05-23T10:00:01.00Z')
@pytest.mark.parametrize(
    [
        'task_id',
        'request_id',
        'expect_fail',
        'result',
        'ofd_stq_times',
        'send_receipt_stq_times',
        'payture_response',
    ],
    [
        ('2', 2, True, None, 0, 0, {}),
        (
            '1',
            1,
            False,
            {
                'status': 'Created',
                'device_rn': 'device_rn',
                'document_number': '123',
                'fiscal_sign': 'fiscal_sign',
                'ofd_name': 'ofd_name',
                'request_id': 2,
            },
            1,
            0,
            {
                'Success': True,
                'ErrCode': 'NONE',
                'Cheques': [
                    dict(CHEQUE_DATA, Status='Accepted'),
                    dict(CHEQUE_DATA, Status='Created'),
                ],
            },
        ),
        (
            '3',
            3,
            False,
            None,
            0,
            1,
            {'Success': False, 'ErrCode': 'CHEQUE_NOT_FOUND', 'Cheques': []},
        ),
        (
            '4',
            4,
            True,
            None,
            0,
            0,
            {'Success': True, 'ErrCode': 'NONE', 'Cheques': [CHEQUE_DATA]},
        ),
        (
            '5',
            5,
            True,
            None,
            0,
            0,
            {
                'Success': True,
                'ErrCode': 'NONE',
                'Cheques': [CHEQUE_DATA, CHEQUE_DATA, CHEQUE_DATA],
            },
        ),
        (
            '6',
            6,
            False,
            None,
            0,
            0,
            {'Success': True, 'ErrCode': 'NONE', 'Cheques': [CHEQUE_DATA]},
        ),
    ],
)
async def test_status_payture_handler(
        stq_runner,
        stq,
        get_cursor,
        mockserver,
        task_id,
        request_id,
        expect_fail,
        result,
        ofd_stq_times,
        send_receipt_stq_times,
        payture_response,
):
    @mockserver.json_handler('/payture/apicheque/Status')
    def _mock_handler(request):
        return payture_response

    await stq_runner.eats_send_receipt_payture_check.call(
        task_id=task_id,
        kwargs={'request_id': request_id},
        expect_fail=expect_fail,
    )

    cursor = get_cursor()

    cursor.execute('SELECT * FROM eats_receipts.send_receipt_ofd_info')
    receipt_request = cursor.fetchone()

    if receipt_request is not None:
        assert receipt_request['status'] == result['status']
        assert receipt_request['device_rn'] == result['device_rn']
        assert receipt_request['document_number'] == result['document_number']
        assert receipt_request['fiscal_sign'] == result['fiscal_sign']
        assert receipt_request['ofd_name'] == result['ofd_name']
        assert receipt_request['request_id'] == request_id
    else:
        assert receipt_request == result

    assert stq.eats_send_receipt_ofd_check.times_called == ofd_stq_times
    if ofd_stq_times != 0:
        call_info = stq.eats_send_receipt_ofd_check.next_call()
        assert call_info['id'] == task_id
        assert call_info['kwargs']['request_id'] == request_id

    assert stq.eats_send_receipt.times_called == send_receipt_stq_times
    if send_receipt_stq_times != 0:
        call_info = stq.eats_send_receipt.next_call()
        assert call_info['id'] == task_id
        assert call_info['kwargs']['request_id'] == 3

    if task_id == '6':
        cursor.execute('SELECT * FROM eats_receipts.stq_failed_tasks')
        result = cursor.fetchone()
        assert result[1] == '210623-123456'
        assert result[2] == 'eats_send_receipt_payture_check'
        assert result[5] is None
        assert result[6] == 'Did not received valid status'
        assert result[7] == '{"request_id":6}'


@pytest.mark.now
async def test_timeout_config(stq_runner, mockserver, get_cursor, mocked_time):
    @mockserver.json_handler('/payture/apicheque/Status')
    def _mock_handler(request):
        return """{\'Success\': False,
                \'ErrCode\': \'CHEQUE_NOT_FOUND\',
                \'Cheques\': []}"""

    await stq_runner.eats_send_receipt_payture_check.call(
        task_id='test_write_payture_result_task',
        kwargs={'request_id': 7},
        expect_fail=True,
    )

    cursor = get_cursor()
    cursor.execute(
        f"""SELECT * FROM
        eats_receipts.stq_failed_tasks WHERE
        stq_arguments::json->>'request_id'='7'""",
    )
    result = cursor.fetchall()

    assert not result

    mocked_time.sleep(3 * 24 * 60 * 60 + 1)

    await stq_runner.eats_send_receipt_payture_check.call(
        task_id='test_write_payture_result_task',
        kwargs={'request_id': 7},
        expect_fail=False,
    )

    cursor.execute(
        f"""SELECT * FROM
        eats_receipts.stq_failed_tasks WHERE
        stq_arguments::json->>'request_id'='7'""",
    )
    result = cursor.fetchall()

    assert result
