import psycopg2
import pytest

ORDER_ID = 'test_order'
ORIGINATOR = 'eats-payments'

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
            country_code = 'KZ'
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
                {
                    'id': 'big_mac',
                    'price': '5.00',
                    'supplier_inn': '1234567894',
                    'tax': '20',
                    'title': 'Big Mac Burger',
                },
                {
                    'id': 'small_mac',
                    'price': '2.50',
                    'supplier_inn': '1234567894',
                    'tax': '20',
                    'title': 'Small Mac Burger',
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
        experiments3,
):
    experiments3.add_config(
        name='eats_receipts_buhta',
        consumers=['eats-receipts/buhta'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {'enabled': True},
            },
        ],
    )

    await stq_runner.eats_send_receipts_requests.call(
        task_id='eats_send_receipts_requests',
        args=[ORDER_ID + '/refund/create:100500', ORIGINATOR],
    )

    cursor = pgsql['eats_receipts'].cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )

    cursor.execute('SELECT * FROM eats_receipts.send_receipt_requests')
    receipt_request = cursor.fetchone()
    assert receipt_request is not None
    assert receipt_request['document_id'] == ORDER_ID + '/refund/create:100500'
    assert receipt_request['originator'] == ORIGINATOR
    assert receipt_request['created_at'] is not None
    assert receipt_request['created_at'] == receipt_request['updated_at']
    assert receipt_request['status'] == 'created'
    assert receipt_request['user_info'] == '(mail_id,phone_id)'
    assert receipt_request['order_info'] == '(KZ,card)'
    assert receipt_request['order_id'] == ORDER_ID

    assert stq.eats_send_receipt.times_called == 1
    assert stq.eats_send_receipt.next_call()['kwargs']['request_id'] == 3

    # next step - sending
    @mockserver.json_handler(
        '/buhta-kz-api-eats/api/v1/orgs/5639/kassa/sales/async',
    )
    def _create_handler_buhta_create(request):
        assert request.json['ref_id'] is not None
        return mockserver.make_response(status=200, json={})

    await stq_runner.eats_send_receipt.call(
        task_id='eats_send_receipt', args=[3],
    )

    cursor = pgsql['eats_receipts'].cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )

    cursor.execute('SELECT * FROM eats_receipts.receipts_info')
    receipt_request = cursor.fetchall()
    print(receipt_request)

    # step get info
    response = await taxi_eats_receipts.post(
        '/api/v1/receipts/',
        json={'order_id': ORDER_ID, 'originators': [ORIGINATOR]},
    )

    assert response.json()['receipts'][0]['ofd_info']['ofd_name'] == 'Buhta'

    assert response.json()['receipts'][0]['ofd_info'][
        'ofd_receipt_url'
    ].startswith('https://buhta.kz/yt/')

    assert response.json()['receipts'][0]['sum'] == '12.5'


@pytest.mark.config(
    EATS_RECEIPTS_ORIGINATORS=TEST_ORIGINATOR_CONFIG,
    TVM_SERVICES=TEST_TVM_CONFIG,
    EATS_RECEIPTS_BUHTA_SETTINGS={
        'org': '5639',
        'url_template': 'https://buhta.kz/yt/{}',
        'new_url_template': (
            'https://buhta.com/receipt/etp/eda/{}?receipt_num={}'
        ),
        'tin': 'its-a-tin',
    },
)
async def test_full_process_with_new_api(
        stq_runner,
        receipt_good_response,
        pgsql,
        stq,
        mockserver,
        taxi_eats_receipts,
        experiments3,
):
    experiments3.add_config(
        name='eats_receipts_buhta',
        consumers=['eats-receipts/buhta'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {'enabled': True},
            },
        ],
    )
    experiments3.add_config(
        name='eats_receipts_buhta_new_api',
        consumers=['eats-receipts/buhta'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {'new_api': True},
            },
        ],
    )

    await stq_runner.eats_send_receipts_requests.call(
        task_id='eats_send_receipts_requests',
        args=[ORDER_ID + '/refund/create:100500', ORIGINATOR],
    )

    cursor = pgsql['eats_receipts'].cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )

    cursor.execute('SELECT * FROM eats_receipts.send_receipt_requests')
    receipt_request = cursor.fetchone()
    assert receipt_request is not None
    assert receipt_request['document_id'] == ORDER_ID + '/refund/create:100500'
    assert receipt_request['originator'] == ORIGINATOR
    assert receipt_request['created_at'] is not None
    assert receipt_request['created_at'] == receipt_request['updated_at']
    assert receipt_request['status'] == 'created'
    assert receipt_request['user_info'] == '(mail_id,phone_id)'
    assert receipt_request['order_info'] == '(KZ,card)'
    assert receipt_request['order_id'] == ORDER_ID

    assert stq.eats_send_receipt.times_called == 1
    assert stq.eats_send_receipt.next_call()['kwargs']['request_id'] == 3

    # sending with new api
    @mockserver.json_handler(
        '/buhta-kz-api-eats-new/v1alpha1/etp/kassa/receipts',
    )
    def _create_handler_buhta_create(request):
        assert request.json['receipt']['receipt_num'] is not None
        assert request.json['receipt']['items'][0]['qty'] == '2'
        return mockserver.make_response(status=200, json={})

    await stq_runner.eats_send_receipt.call(
        task_id='eats_send_receipt', args=[3],
    )

    cursor = pgsql['eats_receipts'].cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )

    cursor.execute('SELECT * FROM eats_receipts.receipts_info')
    receipt_request = cursor.fetchall()
    print(receipt_request)

    # step get info
    response = await taxi_eats_receipts.post(
        '/api/v1/receipts/',
        json={'order_id': ORDER_ID, 'originators': [ORIGINATOR]},
    )

    assert response.json()['receipts'][0]['ofd_info']['ofd_name'] == 'Buhta'

    assert response.json()['receipts'][0]['ofd_info'][
        'ofd_receipt_url'
    ].startswith('https://buhta.com/receipt/etp/eda/')

    assert response.json()['receipts'][0]['sum'] == '12.5'
