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
        # Happy path с 4 вариантами CorrectionReceipt.
        #
        # На входе:
        # - OrderCreated (retail).
        # - 4 варианта CorrectionReceipt.
        #
        # На выходе:
        # - 4 варианта BillingCorrectionReceipt.
        #
        # Проверяем, что:
        # - Создаются BillingCorrectionReceipt
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
                        kind='StartPickerOrderEvent',
                        data={
                            'picker_id': consts.PICKER_ID,
                            'start_picker_order_at': (consts.OTHER_DATE),
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=3,
                        order_nr=consts.ORDER_NR,
                        kind='CorrectionReceipt',
                        data={
                            'date': consts.OTHER_DATE,
                            'sum': 100500,
                            'operation_type': consts.RAW_INCOME,
                            'currency': 'RUB',
                            'items': [],
                            'payload': {},
                            'fiscal_drive_number': consts.FISCAL_DRIVE_NUMBER,
                            'fiscal_document_number': (
                                consts.FISCAL_DOCUMENT_NUMBER
                            ),
                            'fiscal_sign': consts.FISCAL_SIGN,
                            'source': consts.OPERATOR,
                            'user_id': 'DA45CC6F',
                        },
                    ),
                    helpers.make_billing_doc(
                        doc_id=4,
                        order_nr=consts.ORDER_NR,
                        kind='CorrectionReceipt',
                        data={
                            'date': consts.OTHER_DATE,
                            'sum': 100501,
                            'operation_type': consts.RAW_EXPENSE,
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
                        kind='CorrectionReceipt',
                        data={
                            'date': consts.OTHER_DATE,
                            'sum': 100502,
                            'operation_type': consts.RAW_INCOME_REFUND,
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
                        kind='CorrectionReceipt',
                        data={
                            'date': consts.OTHER_DATE,
                            'sum': 100503,
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
                ],
            ),
            # expected_store_request
            helpers.make_storage_create_request(
                [
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
                        f'{100501}',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'transaction_date': consts.OTHER_DATE,
                            'event_at': consts.OTHER_DATE,
                            'place_id': str(consts.PLACE_ID),
                            'sum': '1005.01',
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
                        kind='BillingCorrectionReceipt',
                        external_event_ref='BillingCorrectionReceipt/'
                        f'{consts.ORDER_NR}/'
                        f'{consts.FISCAL_DRIVE_NUMBER}/'
                        f'{consts.FISCAL_DOCUMENT_NUMBER}/'
                        f'{100502}',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'transaction_date': consts.OTHER_DATE,
                            'event_at': consts.OTHER_DATE,
                            'place_id': str(consts.PLACE_ID),
                            'sum': '1005.02',
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
                        kind='BillingCorrectionReceipt',
                        external_event_ref='BillingCorrectionReceipt/'
                        f'{consts.ORDER_NR}/'
                        f'{consts.FISCAL_DRIVE_NUMBER}/'
                        f'{consts.FISCAL_DOCUMENT_NUMBER}/'
                        f'{100503}',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'transaction_date': consts.OTHER_DATE,
                            'event_at': consts.OTHER_DATE,
                            'place_id': str(consts.PLACE_ID),
                            'sum': '1005.03',
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
            ],
            # expected_output_stq_args
            helpers.make_billing_events_stq_kwargs(order_nr=consts.ORDER_NR),
            # expected_input_stq_fail
            False,
            id='BillingCorrectionReceipt created.',
        ),
        # Кейс с CorrectionReceipt нулевой суммой.
        #
        # На входе:
        # - OrderCreated (retail).
        # - CorrectionReceipt с нулевой суммой.
        #
        # На выходе:
        # - Ничего.
        #
        # Проверяем, что:
        # - Не создаются BillingCorrectionReceipt для нулевых сумм.
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
                        doc_id=3,
                        order_nr=consts.ORDER_NR,
                        kind='CorrectionReceipt',
                        data={
                            'date': consts.OTHER_DATE,
                            'sum': 0,
                            'operation_type': consts.RAW_INCOME,
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
            id='No BillingCorrectionReceipt created with zero sum.',
        ),
    ],
)
async def test_correction_receipt(
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
