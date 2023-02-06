import psycopg2
import pytest


# FIXME: Fix this mock when 'yandex-ofd' schema was changed.
@pytest.fixture(name='ofd_good_response')
async def mock_ofd_good_response(mockserver):
    @mockserver.json_handler('/yandex-ofd/v1/docs/find')
    def _mock_handler(request):
        return {
            'receipt': {
                'buyerPhoneOrAddress': 'XXXXXXX@gmail.com',
                'cashTotalSum': 0,
                'code': 3,
                'creditSum': 0,
                'dateTime': 1622545380,
                'ecashTotalSum': 49700,
                'fiscalDocumentFormatVer': 2,
                'fiscalDocumentNumber': 138038,
                'fiscalDriveNumber': '9960440300522541',
                'fiscalSign': 266070574,
                'fnsSite': 'www.nalog.ru',
                'items': [
                    {
                        'name': 'Клубника',
                        'nds': 2,
                        'paymentType': 4,
                        'price': 19800,
                        'productType': 1,
                        'providerInn': '9718101499  ',
                        'quantity': 1.0,
                        'sum': 19800,
                    },
                    {
                        'name': 'Паста Nutella ореховая с какао',
                        'nds': 1,
                        'paymentType': 4,
                        'price': 14500,
                        'productType': 1,
                        'providerInn': '9718101499  ',
                        'quantity': 1.0,
                        'sum': 14500,
                    },
                    {
                        'name': (
                            'Хлеб Harry\'s American Sandwich '
                            'пшеничный в нарезке'
                        ),
                        'nds': 2,
                        'paymentType': 4,
                        'price': 7000,
                        'productType': 1,
                        'providerInn': '9718101499  ',
                        'quantity': 1.0,
                        'sum': 7000,
                    },
                    {
                        'name': 'Бананы',
                        'nds': 1,
                        'paymentType': 4,
                        'price': 8400,
                        'productType': 1,
                        'providerInn': '9718101499  ',
                        'quantity': 1.0,
                        'sum': 8400,
                    },
                ],
                'kktRegId': '0002811389062392',
                'machineNumber': '3010001',
                'messageFiscalSign': 11319146021376099969,
                'nds10': 2436,
                'nds18': 3817,
                'operationType': 1,
                'paymentAgentType': 64,
                'prepaidSum': 0,
                'provisionSum': 0,
                'requestNumber': 711,
                'retailAddress': '127410, Москва г, XXXXXXXXXX ш, дом № XXX',
                'retailPlace': 'https://eda.yandex.ru',
                'shiftNumber': 51,
                'taxationType': 1,
                'totalSum': 49700,
                'user': (
                    'Общество с ограниченной ответственностью \"ЯНДЕКС.ЕДА\"'
                ),
                'userInn': '9705114405',
            },
        }


@pytest.fixture(name='ofd_not_found_response')
async def mock_ofd_not_found_response(mockserver):
    @mockserver.json_handler('/yandex-ofd/v1/docs/find')
    def _mock_handler(request):
        return mockserver.make_response('not found', status=404)


async def test_write_ofd_result_to_receipt_info(
        stq_runner, ofd_good_response, pgsql, get_cursor,
):
    _ = await stq_runner.eats_send_receipt_ofd_check.call(
        task_id='test_write_ofd_result_task', kwargs={'request_id': 1},
    )

    cursor = get_cursor()

    cursor.execute(
        'SELECT * '
        'FROM eats_receipts.send_receipt_requests '
        'WHERE id = {!r}'.format(1),
    )
    send_receipt_request = cursor.fetchone()
    document_id = send_receipt_request['document_id']

    cursor.execute(
        f"""SELECT * FROM
        eats_receipts.receipts_info
                   WHERE document_id = '{document_id}'
                   AND originator = 'test_originator'""",
    )

    receipt_info = cursor.fetchone()
    assert receipt_info['created_at'] is not None
    assert receipt_info['info'] is not None
    assert receipt_info['order_id'] == send_receipt_request['order_id']


async def test_idle_on_failed_status(stq_runner, ofd_good_response, pgsql):
    _ = await stq_runner.eats_send_receipt_ofd_check.call(
        task_id='test_write_ofd_result_task', kwargs={'request_id': 2},
    )

    cursor = pgsql['eats_receipts'].cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )
    cursor.execute(
        'SELECT * '
        'FROM eats_receipts.send_receipt_requests '
        'WHERE id = {!r}'.format(2),
    )
    send_receipt_request = cursor.fetchone()

    cursor.execute(
        'SELECT * '
        'FROM eats_receipts.receipts_info '
        'WHERE document_id = {!r} AND originator = \'originator\''.format(
            send_receipt_request['document_id'],
        ),
    )
    receipt_info = cursor.fetchone()

    assert receipt_info is None


async def test_failure_on_not_found(stq_runner, ofd_not_found_response, pgsql):
    _ = await stq_runner.eats_send_receipt_ofd_check.call(
        task_id='test_write_ofd_result_task',
        kwargs={'request_id': 3},
        expect_fail=True,
    )


async def test_database_entry_on_old_task(
        stq_runner, ofd_not_found_response, pgsql, get_cursor,
):
    _ = await stq_runner.eats_send_receipt_ofd_check.call(
        task_id='test_write_ofd_result_task',
        kwargs={'request_id': 4},
        expect_fail=False,
    )
    cursor = get_cursor()

    cursor.execute('SELECT * FROM eats_receipts.stq_failed_tasks')
    result = cursor.fetchall()
    assert result[1][1] == '1'
    assert result[1][2] == 'eats_send_receipt_ofd_check'
    assert result[1][5] is None
    assert (
        result[1][6] == 'Error in \'GET /v1/docs/find\': '
        'Parse error at pos 1, path \'\': Invalid value.'
    )
    assert result[1][7] == '{"request_id":4}'


async def test_failed_task_recovery(
        stq_runner, ofd_good_response, pgsql, get_cursor,
):
    _ = await stq_runner.eats_send_receipt_ofd_check.call(
        task_id='test_write_ofd_result_task', kwargs={'request_id': 1},
    )

    cursor = get_cursor()
    cursor.execute(
        f"""SELECT * FROM
        eats_receipts.stq_failed_tasks""",
    )

    failed_task = cursor.fetchone()
    assert failed_task[5] is not None


async def test_timeout_config(
        stq_runner, ofd_not_found_response, get_cursor, mocked_time,
):
    _ = await stq_runner.eats_send_receipt_ofd_check.call(
        task_id='test_write_ofd_result_task',
        kwargs={'request_id': 3},
        expect_fail=True,
    )

    cursor = get_cursor()
    cursor.execute(
        f"""SELECT * FROM
        eats_receipts.stq_failed_tasks WHERE
        stq_arguments::json->>'request_id'='3'""",
    )
    result = cursor.fetchall()

    assert not result

    mocked_time.sleep(3 * 24 * 60 * 60 + 1)

    _ = await stq_runner.eats_send_receipt_ofd_check.call(
        task_id='test_write_ofd_result_task',
        kwargs={'request_id': 3},
        expect_fail=False,
    )

    cursor.execute(
        f"""SELECT * FROM
        eats_receipts.stq_failed_tasks WHERE
        stq_arguments::json->>'request_id'='3'""",
    )
    result = cursor.fetchall()

    assert result
