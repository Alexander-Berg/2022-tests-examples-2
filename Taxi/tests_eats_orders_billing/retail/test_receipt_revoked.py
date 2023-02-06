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
        # На входе сырые события:
        #   OrderCreated
        #   ReceiptRevoked
        #   (нет других событий о чеке)
        # На выходе billing-события:
        # ничего. Падаем
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
                        kind='ReceiptRevoked',
                        data={
                            'date': consts.REVOKED_AT,
                            'reason': consts.REVOKE_REASON,
                            'revoking_external_event_ref': (
                                consts.REVOKING_EXT_EVENT_REF
                            ),
                            'user_id': consts.USER_ID,
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
            True,
            id='Event "ReceiptRevoked" without receipt events',
        ),
        # На входе сырые события:
        #   OrderCreated
        #   ReceiptValidated
        #   ReceiptRevoked
        #
        # На выходе billing-события:
        #   BillingReceiptValidated
        #   BillingReceiptRevoked
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
                        external_event_ref=consts.REVOKING_EXT_EVENT_REF,
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
                        kind='ReceiptRevoked',
                        data={
                            'date': consts.REVOKED_AT,
                            'reason': consts.REVOKE_REASON,
                            'revoking_external_event_ref': (
                                consts.REVOKING_EXT_EVENT_REF
                            ),
                            'user_id': consts.USER_ID,
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
                        kind='BillingReceiptRevoked',
                        external_event_ref='BillingReceiptRevoked/'
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
            ],
            # expected_output_stq_args
            helpers.make_billing_events_stq_kwargs(order_nr=consts.ORDER_NR),
            # expected_input_stq_fail
            False,
            id='Event "ReceiptRevoked" and "ReceiptValidated"',
        ),
        # На входе сырые события:
        #   OrderCreated
        #   ReceiptValidated 2
        #   ReceiptRevoked
        #   CorrectionReceipt 2
        #
        # На выходе billing-события:
        #   BillingReceiptValidated
        #   BillingReceiptRevoked
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
                        external_event_ref=f'{consts.REVOKING_EXT_EVENT_REF}'
                        '/1',
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
                        external_event_ref=f'{consts.OTHER_EXTERNAL_EVENT_REF}'
                        '/1',
                        kind='ReceiptValidated',
                        data={
                            'date': consts.OTHER_DATE,
                            'sum': 109801,
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
                        doc_id=4,
                        order_nr=consts.ORDER_NR,
                        external_event_ref=f'{consts.OTHER_EXTERNAL_EVENT_REF}'
                        '/2',
                        kind='CorrectionReceipt',
                        data={
                            'date': consts.OTHER_DATE,
                            'sum': 100500,
                            'operation_type': consts.RAW_EXPENSE_REFUND,
                            'currency': 'RUB',
                            'items': [],
                            'payload': {},
                            'fiscal_drive_number': consts.FISCAL_DRIVE_NUMBER,
                            'fiscal_document_number': (
                                consts.FISCAL_DOCUMENT_NUMBER
                            ),
                            'fiscal_sign': consts.FISCAL_SIGN,
                            'source': consts.OPERATOR,
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=5,
                        order_nr=consts.ORDER_NR,
                        external_event_ref=f'{consts.REVOKING_EXT_EVENT_REF}'
                        '/2',
                        kind='CorrectionReceipt',
                        data={
                            'date': consts.OTHER_DATE,
                            'sum': 100501,
                            'operation_type': consts.RAW_EXPENSE_REFUND,
                            'currency': 'RUB',
                            'items': [],
                            'payload': {},
                            'fiscal_drive_number': consts.FISCAL_DRIVE_NUMBER,
                            'fiscal_document_number': (
                                consts.FISCAL_DOCUMENT_NUMBER
                            ),
                            'fiscal_sign': consts.FISCAL_SIGN,
                            'source': consts.OPERATOR,
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=6,
                        order_nr=consts.ORDER_NR,
                        kind='ReceiptRevoked',
                        data={
                            'date': consts.REVOKED_AT,
                            'reason': consts.REVOKE_REASON,
                            'revoking_external_event_ref': (
                                f'{consts.REVOKING_EXT_EVENT_REF}/1'
                            ),
                            'user_id': consts.USER_ID,
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=7,
                        order_nr=consts.ORDER_NR,
                        kind='ReceiptRevoked',
                        data={
                            'date': consts.REVOKED_AT,
                            'reason': consts.REVOKE_REASON,
                            'revoking_external_event_ref': (
                                f'{consts.REVOKING_EXT_EVENT_REF}/2'
                            ),
                            'user_id': consts.USER_ID,
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
                        f'{109801}',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'transaction_date': consts.OTHER_DATE,
                            'event_at': consts.OTHER_DATE,
                            'place_id': str(consts.PLACE_ID),
                            'sum': '1098.01',
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
                        kind='BillingCorrectionReceipt',
                        external_event_ref='BillingCorrectionReceipt/'
                        f'{consts.ORDER_NR}/'
                        f'{consts.FISCAL_DRIVE_NUMBER}/'
                        f'{consts.FISCAL_DOCUMENT_NUMBER}/'
                        f'{100500}',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'transaction_date': consts.OTHER_DATE,
                            'event_at': consts.OTHER_DATE,
                            'place_id': str(consts.PLACE_ID),
                            'sum': '1005',
                            'currency': 'RUB',
                            'operation_type': consts.BILLING_EXPENSE_REFUND,
                            'fiscal_drive_number': consts.FISCAL_DRIVE_NUMBER,
                            'fiscal_document_number': (
                                consts.FISCAL_DOCUMENT_NUMBER
                            ),
                            'fiscal_sign': consts.FISCAL_SIGN,
                        },
                    ),
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='BillingCorrectionReceipt',
                        external_event_ref='BillingCorrectionReceipt/'
                        f'{consts.ORDER_NR}/'
                        f'{consts.FISCAL_DRIVE_NUMBER}/'
                        f'{consts.FISCAL_DOCUMENT_NUMBER}/'
                        f'{100501}',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'transaction_date': consts.OTHER_DATE,
                            'event_at': consts.OTHER_DATE,
                            'place_id': str(consts.PLACE_ID),
                            'sum': '1005.01',
                            'currency': 'RUB',
                            'operation_type': consts.BILLING_EXPENSE_REFUND,
                            'fiscal_drive_number': consts.FISCAL_DRIVE_NUMBER,
                            'fiscal_document_number': (
                                consts.FISCAL_DOCUMENT_NUMBER
                            ),
                            'fiscal_sign': consts.FISCAL_SIGN,
                        },
                    ),
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='BillingReceiptRevoked',
                        external_event_ref='BillingReceiptRevoked/'
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
                        kind='BillingReceiptRevoked',
                        external_event_ref='BillingReceiptRevoked/'
                        f'{consts.ORDER_NR}/'
                        f'{consts.FISCAL_DRIVE_NUMBER}/'
                        f'{consts.FISCAL_DOCUMENT_NUMBER}/'
                        f'{100501}',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'transaction_date': consts.OTHER_DATE,
                            'event_at': consts.OTHER_DATE,
                            'place_id': str(consts.PLACE_ID),
                            'sum': '1005.01',
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
                helpers.make_storage_finish_request(
                    doc_id=6, status='complete',
                ),
                helpers.make_storage_finish_request(
                    doc_id=7, status='complete',
                ),
            ],
            # expected_output_stq_args
            helpers.make_billing_events_stq_kwargs(order_nr=consts.ORDER_NR),
            # expected_input_stq_fail
            False,
            id='Multiple receipt events and revokes',
        ),
    ],
)
async def test_receipt_revoked(
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
