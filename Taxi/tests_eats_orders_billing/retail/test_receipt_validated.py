import pytest

from tests_eats_orders_billing import consts
from tests_eats_orders_billing import helpers


@pytest.mark.parametrize(
    'input_stq_args,'
    'expected_search_request,'
    'search_response,'
    'expected_store_request,'
    'expected_finish_requests,'
    'expected_output_stq_args,'
    'expected_input_stq_fail',
    [
        # Happy path с 4 вариантами ReceiptValidated.
        #
        # На входе:
        # - OrderCreated (retail).
        # - 4 варианта ReceiptValidated.
        #
        # На выходе:
        # - 4 варианта BillingReceiptValidated.
        #
        # Проверяем, что:
        # - Создаются BillingReceiptValidated
        #   с правильным маппингом operation_type.
        pytest.param(
            # input_stq_args
            helpers.make_raw_events_stq_args(consts.ORDER_NR),
            # expected_search_request
            helpers.make_storage_search_request(consts.ORDER_NR),
            # search_response
            helpers.make_storage_search_response(
                billing_docs=[
                    helpers.make_billing_doc(
                        doc_id=1,
                        order_nr=consts.ORDER_NR,
                        kind='OrderCreated',
                        data={
                            'orderType': 'retail',
                            'currency': 'RUB',
                            'placeId': consts.PLACE_ID,
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=2,
                        order_nr=consts.ORDER_NR,
                        kind='ReceiptValidated',
                        data={
                            'date': consts.OTHER_DATE,
                            'sum': 109800,
                            'fiscal_drive_number': consts.FISCAL_DRIVE_NUMBER,
                            'fiscal_document_number': (
                                consts.FISCAL_DOCUMENT_NUMBER
                            ),
                            'fiscal_sign': consts.FISCAL_SIGN,
                            'operation_type': consts.RAW_INCOME,
                            'items': [],
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=3,
                        order_nr=consts.ORDER_NR,
                        kind='ReceiptValidated',
                        data={
                            'date': consts.OTHER_DATE,
                            'sum': 109810,
                            'fiscal_drive_number': consts.FISCAL_DRIVE_NUMBER,
                            'fiscal_document_number': (
                                consts.FISCAL_DOCUMENT_NUMBER
                            ),
                            'fiscal_sign': consts.FISCAL_SIGN,
                            'operation_type': consts.RAW_EXPENSE,
                            'items': [],
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=4,
                        order_nr=consts.ORDER_NR,
                        kind='ReceiptValidated',
                        data={
                            'date': consts.OTHER_DATE,
                            'sum': 109820,
                            'fiscal_drive_number': consts.FISCAL_DRIVE_NUMBER,
                            'fiscal_document_number': (
                                consts.FISCAL_DOCUMENT_NUMBER
                            ),
                            'fiscal_sign': consts.FISCAL_SIGN,
                            'operation_type': consts.RAW_INCOME_REFUND,
                            'items': [],
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=5,
                        order_nr=consts.ORDER_NR,
                        kind='ReceiptValidated',
                        data={
                            'date': consts.OTHER_DATE,
                            'sum': 109830,
                            'fiscal_drive_number': consts.FISCAL_DRIVE_NUMBER,
                            'fiscal_document_number': (
                                consts.FISCAL_DOCUMENT_NUMBER
                            ),
                            'fiscal_sign': consts.FISCAL_SIGN,
                            'operation_type': consts.RAW_EXPENSE_REFUND,
                            'items': [],
                        },
                    ),
                ],
            ),
            # expected_store_request
            helpers.make_storage_create_request(
                [
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='BillingReceiptValidated',
                        external_event_ref='BillingReceiptValidated/'
                        f'{consts.ORDER_NR}/'
                        f'{consts.FISCAL_DRIVE_NUMBER}/'
                        f'{consts.FISCAL_DOCUMENT_NUMBER}/'
                        f'{109800}',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'transaction_date': consts.OTHER_DATE,
                            'event_at': consts.OTHER_DATE,
                            'place_id': str(consts.PLACE_ID),
                            'sum': '1098',
                            'currency': 'RUB',
                            'operation_type': consts.BILLING_INCOME,
                            'fiscal_drive_number': consts.FISCAL_DRIVE_NUMBER,
                            'fiscal_document_number': (
                                consts.FISCAL_DOCUMENT_NUMBER
                            ),
                            'fiscal_sign': consts.FISCAL_SIGN,
                        },
                    ),
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='BillingReceiptValidated',
                        external_event_ref='BillingReceiptValidated/'
                        f'{consts.ORDER_NR}/'
                        f'{consts.FISCAL_DRIVE_NUMBER}/'
                        f'{consts.FISCAL_DOCUMENT_NUMBER}/'
                        f'{109810}',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'transaction_date': consts.OTHER_DATE,
                            'event_at': consts.OTHER_DATE,
                            'place_id': str(consts.PLACE_ID),
                            'sum': '1098.1',
                            'currency': 'RUB',
                            'operation_type': consts.BILLING_EXPENSE,
                            'fiscal_drive_number': consts.FISCAL_DRIVE_NUMBER,
                            'fiscal_document_number': (
                                consts.FISCAL_DOCUMENT_NUMBER
                            ),
                            'fiscal_sign': consts.FISCAL_SIGN,
                        },
                    ),
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='BillingReceiptValidated',
                        external_event_ref='BillingReceiptValidated/'
                        f'{consts.ORDER_NR}/'
                        f'{consts.FISCAL_DRIVE_NUMBER}/'
                        f'{consts.FISCAL_DOCUMENT_NUMBER}/'
                        f'{109820}',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'transaction_date': consts.OTHER_DATE,
                            'event_at': consts.OTHER_DATE,
                            'place_id': str(consts.PLACE_ID),
                            'sum': '1098.2',
                            'currency': 'RUB',
                            'operation_type': consts.BILLING_INCOME_REFUND,
                            'fiscal_drive_number': consts.FISCAL_DRIVE_NUMBER,
                            'fiscal_document_number': (
                                consts.FISCAL_DOCUMENT_NUMBER
                            ),
                            'fiscal_sign': consts.FISCAL_SIGN,
                        },
                    ),
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='BillingReceiptValidated',
                        external_event_ref='BillingReceiptValidated/'
                        f'{consts.ORDER_NR}/'
                        f'{consts.FISCAL_DRIVE_NUMBER}/'
                        f'{consts.FISCAL_DOCUMENT_NUMBER}/'
                        f'{109830}',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'transaction_date': consts.OTHER_DATE,
                            'event_at': consts.OTHER_DATE,
                            'place_id': str(consts.PLACE_ID),
                            'sum': '1098.3',
                            'currency': 'RUB',
                            'operation_type': consts.BILLING_EXPENSE_REFUND,
                            'fiscal_drive_number': consts.FISCAL_DRIVE_NUMBER,
                            'fiscal_document_number': (
                                consts.FISCAL_DOCUMENT_NUMBER
                            ),
                            'fiscal_sign': consts.FISCAL_SIGN,
                        },
                    ),
                ],
            ),
            # expected_finish_requests
            [
                helpers.make_storage_finish_request(
                    doc_id=1, status='complete',
                ),
                helpers.make_storage_finish_request(
                    doc_id=2, status='complete',
                ),
                helpers.make_storage_finish_request(
                    doc_id=3, status='complete',
                ),
                helpers.make_storage_finish_request(
                    doc_id=4, status='complete',
                ),
                helpers.make_storage_finish_request(
                    doc_id=5, status='complete',
                ),
            ],
            # expected_output_stq_args
            helpers.make_billing_events_stq_kwargs(order_nr=consts.ORDER_NR),
            # expected_input_stq_fail
            False,
            id='BillingReceiptValidated created.',
        ),
        # Кейс с ReceiptValidated нулевой суммой.
        #
        # На входе:
        # - OrderCreated (retail).
        # - ReceiptValidated с нулевой суммой.
        #
        # На выходе:
        # - Ничего.
        #
        # Проверяем, что:
        # - Не создаются BillingReceiptValidated для нулевых сумм.
        pytest.param(
            # input_stq_args
            helpers.make_raw_events_stq_args(consts.ORDER_NR),
            # expected_search_request
            helpers.make_storage_search_request(consts.ORDER_NR),
            # search_response
            helpers.make_storage_search_response(
                billing_docs=[
                    helpers.make_billing_doc(
                        doc_id=1,
                        order_nr=consts.ORDER_NR,
                        kind='OrderCreated',
                        data={
                            'orderType': 'retail',
                            'currency': 'RUB',
                            'placeId': consts.PLACE_ID,
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=2,
                        order_nr=consts.ORDER_NR,
                        kind='ReceiptValidated',
                        data={
                            'date': consts.OTHER_DATE,
                            'sum': 0,
                            'fiscal_drive_number': consts.FISCAL_DRIVE_NUMBER,
                            'fiscal_document_number': (
                                consts.FISCAL_DOCUMENT_NUMBER
                            ),
                            'fiscal_sign': consts.FISCAL_SIGN,
                            'operation_type': consts.RAW_INCOME,
                            'items': [],
                        },
                    ),
                ],
            ),
            # expected_store_request
            None,
            # expected_finish_requests
            None,
            # expected_output_stq_args
            None,
            # expected_input_stq_fail
            False,
            id='No BillingReceiptValidated created with zero sum.',
        ),
    ],
)
async def test_receipt_validated(
        stq_runner,
        stq,
        mock_storage_search,
        mock_storage_store,
        mock_storage_finish,
        input_stq_args,
        expected_search_request,
        search_response,
        expected_store_request,
        expected_finish_requests,
        expected_output_stq_args,
        expected_input_stq_fail,
):
    await helpers.raw_processing_test_func(
        stq_runner,
        stq,
        mock_storage_search,
        mock_storage_store,
        mock_storage_finish,
        input_stq_args,
        expected_search_request,
        search_response,
        expected_store_request,
        expected_finish_requests,
        expected_output_stq_args,
        expected_input_stq_fail,
    )
