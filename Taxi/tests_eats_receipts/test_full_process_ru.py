import psycopg2
import pytest

ORDER_ID = 'test_order'
ORIGINATOR = 'eats-payments'

CHEQUE_DATA = {
    'Sended': True,
    'Status': 'Created',
    'Cheque': {
        'Content': {
            'Type': 1,
            'Positions': [
                {
                    'Quantity': 1,
                    'Price': 5.00,
                    'Tax': 1,
                    'Text': 'Big Mac Burger',
                },
            ],
            'CheckClose': {
                'Payments': [{'Type': 1, 'Amount': 5.00}],
                'TaxationSystem': 0,
            },
            'CustomerContact': 'na.derevyu@dedushke.ru',
        },
        'Id': ORIGINATOR + '/' + ORDER_ID + '/3',
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

TEST_ORIGINATOR_CONFIG = {
    'eats-payments': {
        'url': {'$mockserver': '/v1/receipts/retrieve'},
        'tvm_name': 'eats-payments',
        'agent_type': 64,
    },
    'eats-core': {
        'url': '/v1/core-receipts/retrieve',
        'tvm_name': 'eats-core',
    },
}

TEST_TVM_CONFIG = {
    'eats-payments': 2021618,
    'stq-agent': 2013178,
    'statistics': 201321,
    'personal': 201322,
    'taxi_exp': 2012314,
    'experiments3-proxy': 2015020,
}


@pytest.fixture(autouse=True)
def _personal_mock(mockserver):
    @mockserver.json_handler('/personal/v1/emails/retrieve')
    def _handle(request):
        return {'id': request.json['id'], 'value': 'na.derevyu@dedushke.ru'}


@pytest.fixture(name='receipt_good_response')
async def mock_receipt_good_response(mockserver):
    @mockserver.json_handler('/v1/receipts/retrieve')
    def _mock_handler(request):
        if 'break' in request.json['document_id']:
            country_code = 'FB'
        else:
            country_code = 'RU'
        return {
            'is_refund': True,
            'order': {
                'country_code': country_code,
                'order_nr': ORDER_ID,
                'payment_method': 'card',
            },
            'products': [
                {
                    'id': 'big_mac',
                    'price': '5.00',
                    'supplier_inn': '1234567894',
                    'tax': '20',
                    'title': 'Big Mac Burger',
                },
            ],
            'user_info': {
                'personal_email_id': 'mail_id',
                'personal_phone_id': 'phone_id',
            },
        }


@pytest.mark.config(
    EATS_RECEIPTS_ORIGINATORS=TEST_ORIGINATOR_CONFIG,
    TVM_SERVICES=TEST_TVM_CONFIG,
)
async def test_full_process(
        stq_runner,
        receipt_good_response,
        pgsql,
        stq,
        mockserver,
        taxi_eats_receipts,
):
    await stq_runner.eats_send_receipts_requests.call(
        task_id='eats_send_receipts_requests',
        args=[ORDER_ID + '/refund/create:100500', ORIGINATOR],
    )

    cursor = pgsql['eats_receipts'].cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )

    cursor.execute('SELECT * FROM eats_receipts.send_receipt_requests')
    receipt_request = cursor.fetchone()
    assert receipt_request['document_id'] == ORDER_ID + '/refund/create:100500'
    assert receipt_request['originator'] == ORIGINATOR
    assert receipt_request['created_at'] is not None
    assert receipt_request['created_at'] == receipt_request['updated_at']
    assert receipt_request['status'] == 'created'
    assert receipt_request['user_info'] == '(mail_id,phone_id)'
    assert receipt_request['order_info'] == '(RU,card)'
    assert receipt_request['order_id'] == ORDER_ID

    assert stq.eats_send_receipt.times_called == 1
    assert stq.eats_send_receipt.next_call()['kwargs']['request_id'] == 3

    # next step - sending
    @mockserver.json_handler('/payture/apicheque/Create')
    def _create_handler_payture_create(request):
        assert request.json['Cheque']['Id'] == ORDER_ID + '/3'
        assert request.json['Cheque']['Content']['AgentType'] == 64
        return {
            'Success': True,
            'ErrCode': 'NONE',
            'ErrMessages': [],
            'Status': 'Accepted',
        }

    await stq_runner.eats_send_receipt.call(
        task_id='eats_send_receipt', args=[3],
    )

    assert stq.eats_send_receipt_payture_check.times_called == 1
    assert (
        stq.eats_send_receipt_payture_check.next_call()['kwargs']['request_id']
        == 3
    )

    # next step - checking payture
    @mockserver.json_handler('/payture/apicheque/Status')
    def _mock_handler_payture_status(request):
        assert request.json['ID'] == ORDER_ID + '/3'
        return {'Success': True, 'ErrCode': 'NONE', 'Cheques': [CHEQUE_DATA]}

    await stq_runner.eats_send_receipt_payture_check.call(
        task_id='eats_send_receipt_payture_check', args=[3],
    )

    assert stq.eats_send_receipt_ofd_check.times_called == 1
    assert (
        stq.eats_send_receipt_ofd_check.next_call()['kwargs']['request_id']
        == 3
    )

    # next step - checking ofd

    @mockserver.json_handler('/yandex-ofd/v1/docs/find')
    def _mock_handler_ofd_find(request):
        return {
            'receipt': {
                'buyerPhoneOrAddress': 'na.derevyu@dedushke.ru',
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
                        'name': 'Big Mac Burger',
                        'nds': 2,
                        'paymentType': 4,
                        'price': 500,
                        'productType': 1,
                        'providerInn': '1234567894',
                        'quantity': 1.0,
                        'sum': 500,
                    },
                    {
                        'name': 'Small Mac Burger',
                        'nds': 2,
                        'paymentType': 4,
                        'price': 250,
                        'productType': 1,
                        'providerInn': '1234567894',
                        'quantity': 1.0,
                        'sum': 250,
                    },
                ],
                'kktRegId': '0002811389062392',
                'machineNumber': '3010001',
                'messageFiscalSign': 11319146021376099969,
                'nds10': 0,
                'nds18': 100,
                'operationType': 1,
                'paymentAgentType': 64,
                'prepaidSum': 0,
                'provisionSum': 0,
                'requestNumber': 711,
                'retailAddress': '127410, Москва г, XXXXXXXXXX ш, дом № XXX',
                'retailPlace': 'https://eda.yandex.ru',
                'shiftNumber': 51,
                'taxationType': 1,
                'totalSum': 500,
                'user': (
                    'Общество с ограниченной ответственностью \"ЯНДЕКС.ЕДА\"'
                ),
                'userInn': '9705114405',
            },
        }

    await stq_runner.eats_send_receipt_ofd_check.call(
        task_id='eats_send_receipt_ofd_check', args=[3],
    )

    # step get info
    response = await taxi_eats_receipts.post(
        '/api/v1/receipts/',
        json={'order_id': ORDER_ID, 'originators': [ORIGINATOR]},
    )

    assert (
        response.json()['receipts'][0]['ofd_info']['ofd_receipt_url']
        == 'https://ofd.yandex.ru/vaucher/0002811389062392/138038/266070574'
    )

    assert response.json()['receipts'][0]['sum'] == '750'
