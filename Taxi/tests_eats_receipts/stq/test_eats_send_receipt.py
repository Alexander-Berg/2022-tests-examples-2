import pytest

TEST_ORIGINATOR_CONFIG = {
    'originator': {
        'url': {'$mockserver': '/v1/receipts/retrieve'},
        'tvm_name': 'originator',
        'agent_type': 64,
    },
}

TEST_ORIGINATOR_CONFIG_WITH_EXTRA_OPTIONS = {
    'originator': {
        'url': {'$mockserver': '/v1/receipts/retrieve'},
        'tvm_name': 'originator',
        'group_type': 'some_group',
    },
}

PAYTURE_SUCCESSFUL_RESPONSE = {
    'Success': True,
    'ErrCode': 'NONE',
    'ErrMessages': [],
    'Status': 'Accepted',
}


@pytest.fixture(autouse=True)
def _personal_mock(mockserver):
    @mockserver.json_handler('/personal/v1/emails/retrieve')
    def _emails_handle(request):
        return {'id': request.json['id'], 'value': 'na.derevyu@dedushke.ru'}

    @mockserver.json_handler('/personal/v1/tins/retrieve')
    def _tins_handle(request):
        return {'id': request.json['id'], 'value': '479753957665'}


@pytest.fixture(name='payture_simple_success')
def _payture_simple_success(mockserver):
    @mockserver.json_handler('/payture/apicheque/Create')
    def _handle(request):
        assert request.json['Cheque']['Content']['AgentType'] == 64
        assert 'Group' not in request.json['Cheque']
        return PAYTURE_SUCCESSFUL_RESPONSE


@pytest.fixture(name='payture_simple_success_extra_options')
def _payture_simple_success_extra_options(mockserver):
    @mockserver.json_handler('/payture/apicheque/Create')
    def _handle(request):
        assert 'AgentType' not in request.json['Cheque']['Content']
        assert request.json['Cheque']['Group'] == 'some_group'
        return PAYTURE_SUCCESSFUL_RESPONSE


# Навскидку не получается упростить этот мок из-за
# test_cheque_not_found_scenario, там какая-то магия. TODO упростить
@pytest.fixture(name='payture_create_success')
def _payture_create_success(mockserver):
    class Handler:
        def __init__(self):
            self.last_request_ = None

        def last_request(self):
            return self.last_request_

        def handle(self, request):
            self.last_request_ = request.json
            assert self.last_request_['Cheque']['Content']['AgentType'] == 64
            return PAYTURE_SUCCESSFUL_RESPONSE

    handler = Handler()

    @mockserver.json_handler('/payture/apicheque/Create')
    def _handle(request):
        return handler.handle(request)

    return handler


async def _happy_path_flow(
        stq_runner, get_cursor, create_send_receipt_request, stq,
):
    test_doc_id = 'test_doc_id'
    req_id = create_send_receipt_request(
        status='created', document_id=test_doc_id,
    )

    await stq_runner.eats_send_receipt.call(
        task_id='test_update_status_task', kwargs={'request_id': req_id},
    )

    assert stq.eats_send_receipt_payture_check.times_called == 1
    payture_check_req_id = stq.eats_send_receipt_payture_check.next_call()[
        'kwargs'
    ]['request_id']

    cursor = get_cursor()
    cursor.execute(
        f'SELECT status, service_name '
        f'FROM eats_receipts.send_receipt_requests '
        f'WHERE id = {req_id}',
    )
    status, service = cursor.fetchone()
    assert status == 'sent'
    assert service == 'payture'

    cursor.execute(
        f'SELECT document_id, status '
        f'FROM eats_receipts.send_receipt_payture_info '
        f'WHERE id = {payture_check_req_id}',
    )
    doc_id, status = cursor.fetchone()
    assert doc_id == test_doc_id
    assert status == 'pending'


@pytest.mark.config(EATS_RECEIPTS_ORIGINATORS=TEST_ORIGINATOR_CONFIG)
async def test_happy_path(
        stq_runner,
        get_cursor,
        create_send_receipt_request,
        stq,
        payture_simple_success,
):
    await _happy_path_flow(
        stq_runner, get_cursor, create_send_receipt_request, stq,
    )


@pytest.mark.config(
    EATS_RECEIPTS_ORIGINATORS=TEST_ORIGINATOR_CONFIG_WITH_EXTRA_OPTIONS,
)
async def test_happy_path_with_options(
        stq_runner,
        get_cursor,
        create_send_receipt_request,
        stq,
        payture_simple_success_extra_options,
):
    await _happy_path_flow(
        stq_runner, get_cursor, create_send_receipt_request, stq,
    )


@pytest.mark.config(EATS_RECEIPTS_ORIGINATORS=TEST_ORIGINATOR_CONFIG)
async def test_no_progress_for_failed_request(
        stq_runner, create_send_receipt_request, stq,
):
    req_id = create_send_receipt_request(status='failed')

    await stq_runner.eats_send_receipt.call(
        task_id='test_update_status_task', kwargs={'request_id': req_id},
    )

    assert stq.eats_send_receipt_payture_check.times_called == 0


@pytest.mark.config(EATS_RECEIPTS_ORIGINATORS=TEST_ORIGINATOR_CONFIG)
async def test_payture_failure(
        stq_runner, create_send_receipt_request, stq, mockserver,
):
    @mockserver.json_handler('/payture/apicheque/Create')
    def _handler(request):
        return mockserver.make_response(status=500)

    req_id = create_send_receipt_request(status='created')
    await stq_runner.eats_send_receipt.call(
        task_id='test_update_status_task',
        kwargs={'request_id': req_id},
        expect_fail=True,
    )

    @mockserver.json_handler('/payture/apicheque/Create')
    def _create_handler(request):
        return {
            'Success': True,
            'ErrCode': 'NONE',
            'ErrMessages': [],
            'Status': 'Accepted',
        }

    await stq_runner.eats_send_receipt.call(
        task_id='test_update_status_task', kwargs={'request_id': req_id},
    )
    assert stq.eats_send_receipt_payture_check.times_called == 1


@pytest.mark.pgsql(
    'eats_receipts',
    queries=[
        """INSERT INTO eats_receipts.send_receipt_payture_info
            (document_id, originator, status)
           VALUES ('test_doc_id', 'originator', 'success');""",
    ],
)
@pytest.mark.config(EATS_RECEIPTS_ORIGINATORS=TEST_ORIGINATOR_CONFIG)
async def test_multiple_calls_with_same_args(
        stq_runner, get_cursor, create_send_receipt_request, stq, mockserver,
):
    @mockserver.json_handler('/payture/apicheque/Create')
    def _create_handler(request):
        return {
            'Success': True,
            'ErrCode': 'NONE',
            'ErrMessages': [],
            'Status': 'Accepted',
        }

    test_doc_id = 'test_doc_id'
    req_id = create_send_receipt_request(
        status='created', originator='originator', document_id=test_doc_id,
    )

    await stq_runner.eats_send_receipt.call(
        task_id=f'test_update_status_task', kwargs={'request_id': req_id},
    )

    assert stq.eats_send_receipt_payture_check.times_called == 1
    payture_check_req_id = stq.eats_send_receipt_payture_check.next_call()[
        'kwargs'
    ]['request_id']

    cursor = get_cursor()
    cursor.execute(
        f'SELECT document_id, status '
        f'FROM eats_receipts.send_receipt_payture_info '
        f'WHERE id = {payture_check_req_id}',
    )
    doc_id, status = cursor.fetchone()
    assert doc_id == test_doc_id
    assert status == 'pending'


async def test_do_nothing_for_non_russian_requests(
        stq_runner, create_send_receipt_request, stq,
):
    req_id = create_send_receipt_request(status='created', country_code='BY')

    await stq_runner.eats_send_receipt.call(
        task_id='test_update_status_task', kwargs={'request_id': req_id},
    )

    assert stq.eats_send_receipt_payture_check.times_called == 0


async def test_do_nothing_for_wrong_payment_type(
        stq_runner, create_send_receipt_request, stq,
):
    req_id = create_send_receipt_request(
        status='created', payment_method='badge',
    )

    await stq_runner.eats_send_receipt.call(
        task_id='test_update_status_task', kwargs={'request_id': req_id},
    )

    assert stq.eats_send_receipt_payture_check.times_called == 0


@pytest.mark.parametrize(
    'source_products, dest_products',
    [
        # One-to-one transformation
        (
            [
                {
                    'id': 'big_mac',
                    'parent': None,
                    'price': '5.00',
                    'supplier_inn': '123456789012',
                    'tax': '20',
                    'title': 'Big Mac Burger',
                },
                {
                    'id': 'fries',
                    'parent': None,
                    'price': '2.00',
                    'supplier_inn': '123456789012',
                    'tax': '10',
                    'title': 'French fries',
                },
            ],
            [
                {
                    'AgentType': 64,
                    'Quantity': 1.0,
                    'Price': 5.0,
                    'Tax': 1,
                    'Text': 'Big Mac Burger',
                    'SupplierINN': '123456789012',
                },
                {
                    'AgentType': 64,
                    'Quantity': 1.0,
                    'Price': 2.0,
                    'Tax': 2,
                    'Text': 'French fries',
                    'SupplierINN': '123456789012',
                },
            ],
        ),
        # Union of same products
        (
            [
                {
                    'id': '4_cheeze',
                    'parent': None,
                    'price': '20.0',
                    'supplier_inn': '123456789012',
                    'tax': '20',
                    'title': 'Quattro formaggio',
                },
                {
                    'id': '4_cheeze',
                    'parent': None,
                    'price': '20.0',
                    'supplier_inn': '123456789012',
                    'tax': '20',
                    'title': 'Quattro formaggio',
                },
                {
                    'id': 'fries',
                    'parent': None,
                    'price': '2.00',
                    'supplier_inn': '123456789012',
                    'tax': '10',
                    'title': 'French fries',
                },
                {
                    'id': '4_cheeze',
                    'parent': None,
                    'price': '20.0',
                    'supplier_inn': '123456789012',
                    'tax': '20',
                    'title': 'Quattro formaggio',
                },
            ],
            [
                {
                    'AgentType': 64,
                    'Quantity': 1.0,
                    'Price': 2.0,
                    'Tax': 2,
                    'Text': 'French fries',
                    'SupplierINN': '123456789012',
                },
                {
                    'AgentType': 64,
                    'Quantity': 3.0,
                    'Price': 20.0,
                    'Tax': 1,
                    'Text': 'Quattro formaggio',
                    'SupplierINN': '123456789012',
                },
            ],
        ),
    ],
)
@pytest.mark.config(EATS_RECEIPTS_ORIGINATORS=TEST_ORIGINATOR_CONFIG)
async def test_products_conversion(
        stq_runner,
        create_send_receipt_request,
        mockserver,
        source_products,
        dest_products,
):
    @mockserver.json_handler('/payture/apicheque/Create')
    def _create_handler(request):
        assert request.json['Cheque']['Content']['Positions'] == dest_products
        return {
            'Success': True,
            'ErrCode': 'NONE',
            'ErrMessages': [],
            'Status': 'Accepted',
        }

    test_doc_id = 'test_doc_id'
    req_id = create_send_receipt_request(
        status='created', document_id=test_doc_id, products=source_products,
    )

    await stq_runner.eats_send_receipt.call(
        task_id=f'test_update_status_task', kwargs={'request_id': req_id},
    )


@pytest.mark.config(EATS_RECEIPTS_ORIGINATORS=TEST_ORIGINATOR_CONFIG)
async def test_cheque_not_found_scenario(
        stq_runner,
        create_send_receipt_request,
        mockserver,
        stq,
        payture_create_success,
        get_cursor,
):
    test_doc_id = 'test_doc_id'
    req_id = create_send_receipt_request(
        status='created', document_id=test_doc_id,
    )

    await stq_runner.eats_send_receipt.call(
        task_id='test_update_status_task', kwargs={'request_id': req_id},
    )

    assert stq.eats_send_receipt_payture_check.times_called == 1

    @mockserver.json_handler('/payture/apicheque/Status')
    def _handle(request):
        assert (
            request.json['ID']
            == payture_create_success.last_request()['Cheque']['Id']
        )
        return {'Success': False, 'ErrCode': 'CHEQUE_NOT_FOUND'}

    args = stq.eats_send_receipt_payture_check.next_call()
    await stq_runner.eats_send_receipt_payture_check.call(
        task_id=args['id'], kwargs=args['kwargs'],
    )

    assert stq.eats_send_receipt.times_called == 1
    args = stq.eats_send_receipt.next_call()
    assert args['kwargs']['request_id'] == req_id

    @mockserver.json_handler('/payture/apicheque/Create')
    def _handler(request):
        return {
            'Success': True,
            'ErrCode': 'CHEQUE_DUPLICATE',
            'ErrMessages': [],
            'Status': 'Unknown',
        }

    await stq_runner.eats_send_receipt.call(
        task_id=args['id'], kwargs=args['kwargs'],
    )

    assert stq.eats_send_receipt_payture_check.times_called == 1
    args = stq.eats_send_receipt_payture_check.next_call()

    cursor = get_cursor()
    cursor.execute(
        f'SELECT status '
        f'FROM eats_receipts.send_receipt_payture_info '
        f'WHERE id = {args["kwargs"]["request_id"]}',
    )
    (status,) = cursor.fetchone()
    assert status == 'pending'


@pytest.mark.parametrize(
    'source_products, dest_products',
    [
        # One-to-one transformation
        (
            [
                {
                    'id': 'big_mac',
                    'parent': None,
                    'price': '5.00',
                    'supplier_inn': '123456789012',
                    'tax': '20',
                    'title': 'Big Mac Burger',
                },
                {
                    'id': 'fries',
                    'parent': None,
                    'price': '2.00',
                    'supplier_inn': '123456789012',
                    'tax': '10',
                    'title': 'French fries',
                },
            ],
            [
                {
                    'Quantity': 1.0,
                    'Price': 5.0,
                    'Tax': 1,
                    'Text': 'Big Mac Burger',
                },
                {
                    'Quantity': 1.0,
                    'Price': 2.0,
                    'Tax': 2,
                    'Text': 'French fries',
                },
            ],
        ),
    ],
)
@pytest.mark.config(
    EATS_RECEIPTS_ORIGINATORS=TEST_ORIGINATOR_CONFIG_WITH_EXTRA_OPTIONS,
)
async def test_products_conversion_without_agent(
        stq_runner,
        create_send_receipt_request,
        mockserver,
        source_products,
        dest_products,
):
    @mockserver.json_handler('/payture/apicheque/Create')
    def _create_handler(request):
        assert request.json['Cheque']['Content']['Positions'] == dest_products
        return {
            'Success': True,
            'ErrCode': 'NONE',
            'ErrMessages': [],
            'Status': 'Accepted',
        }

    test_doc_id = 'test_doc_id'
    req_id = create_send_receipt_request(
        status='created', document_id=test_doc_id, products=source_products,
    )

    await stq_runner.eats_send_receipt.call(
        task_id=f'test_update_status_task', kwargs={'request_id': req_id},
    )


@pytest.mark.config(EATS_RECEIPTS_ORIGINATORS=TEST_ORIGINATOR_CONFIG)
async def test_get_inn_by_inn_id_from_personal(
        stq_runner, create_send_receipt_request, mockserver,
):
    @mockserver.json_handler('/payture/apicheque/Create')
    def _create_handler(request):
        print(request.json)
        assert request.json['Cheque']['Content']['Positions'] == [
            {
                'Quantity': 1.0,
                'Price': 5.0,
                'Tax': 1,
                'Text': 'Big Mac Burger',
                'AgentType': 64,
                'SupplierINN': '479753957665',
            },
            {
                'Quantity': 1.0,
                'Price': 2.0,
                'Tax': 2,
                'Text': 'French fries',
                'AgentType': 64,
                'SupplierINN': '479753957665',
            },
        ]
        return {
            'Success': True,
            'ErrCode': 'NONE',
            'ErrMessages': [],
            'Status': 'Accepted',
        }

    test_doc_id = 'test_doc_id'
    req_id = create_send_receipt_request(
        status='created',
        document_id=test_doc_id,
        products=[
            {
                'id': 'big_mac',
                'parent': None,
                'price': '5.00',
                'supplier_inn_id': 'inn_id',
                'tax': '20',
                'title': 'Big Mac Burger',
            },
            {
                'id': 'fries',
                'parent': None,
                'price': '2.00',
                'supplier_inn_id': 'inn_id',
                'tax': '10',
                'title': 'French fries',
            },
        ],
    )

    await stq_runner.eats_send_receipt.call(
        task_id=f'test_update_status_task', kwargs={'request_id': req_id},
    )
