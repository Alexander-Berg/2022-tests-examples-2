import pytest

from tests_eats_orders_billing import consts
from tests_eats_orders_billing import helpers


@pytest.mark.parametrize(
    'input_stq_args,'
    'expected_search_request,'
    'search_response,'
    'expected_store_request,'
    'expected_finish_requests,'
    'expected_business_rules_requests,'
    'business_rules_responses,'
    'expected_input_stq_fail',
    [
        # Happy path с 4мя вариантами BillingCorrectionReceipt.
        #
        # На входе:
        # - OrderCreated (retail).
        # - 4 варианта BillingCorrectionReceipt,
        #   отличаются 'operation_type'.
        #
        # На выходе:
        # - 4 варианта CommissionOrder.
        #
        # Проверяем, что:
        # - Для 'income' коммиссия с +.
        # - Для 'income_refund' коммиссия с -.
        # - Для 'expense' коммиссия с -.
        # - Для 'expense_refund' коммиссия с +.
        # - У CommissionOrder заполняется payload.
        # - У CommissionOrder заполняется identity.
        # - В business-rules ходим за коммиссией для ресторана.
        pytest.param(
            # input_stq_args
            helpers.make_raw_events_stq_args(consts.ORDER_NR),
            # expected_search_request
            helpers.make_storage_search_request(consts.ORDER_NR),
            # search_response
            helpers.make_storage_search_response(
                billing_docs=[
                    helpers.make_order_created_doc(),
                    helpers.make_billing_doc(
                        doc_id=2147995772,
                        order_nr=consts.ORDER_NR,
                        kind='BillingCorrectionReceipt',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'transaction_date': consts.OTHER_DATE,
                            'event_at': consts.OTHER_DATE,
                            'place_id': str(consts.PLACE_ID),
                            'sum': '100',
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
                        doc_id=2,
                        order_nr=consts.ORDER_NR,
                        kind='BillingCorrectionReceipt',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'transaction_date': consts.OTHER_DATE,
                            'event_at': consts.OTHER_DATE,
                            'place_id': str(consts.PLACE_ID),
                            'sum': '200',
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
                        doc_id=3,
                        order_nr=consts.ORDER_NR,
                        kind='BillingCorrectionReceipt',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'transaction_date': consts.OTHER_DATE,
                            'event_at': consts.OTHER_DATE,
                            'place_id': str(consts.PLACE_ID),
                            'sum': '300',
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
                        doc_id=4,
                        order_nr=consts.ORDER_NR,
                        kind='BillingCorrectionReceipt',
                        data={
                            'order_nr': consts.ORDER_NR,
                            'transaction_date': consts.OTHER_DATE,
                            'event_at': consts.OTHER_DATE,
                            'place_id': str(consts.PLACE_ID),
                            'sum': '400',
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
            # expected_store_request
            helpers.make_storage_create_request(
                [
                    # income
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='CommissionOrder',
                        external_event_ref=f'CommissionOrder/{consts.ORDER_NR}'
                        '/BillingCorrectionReceipt/2147995772',
                        data={
                            'service_order_id': consts.ORDER_NR,
                            'service_id': 661,  # hardcoded const
                            'dt': consts.OTHER_DATE,
                            'client_id': consts.CLIENT_ID,
                            'transaction_currency': 'RUB',
                            'commission_sum': (
                                '30'
                            ),  # 100 * (5 + 10) / 100 + 15
                            'promocode_sum': '0',
                            'type': 'retail',
                            'total_sum': '30',
                            'identity': (
                                f'CommissionOrder/{consts.ORDER_NR}'
                                '/BillingCorrectionReceipt/2147995772'
                            ),
                            'payload': {
                                'place_id': str(consts.PLACE_ID),
                                'fiscal_drive_number': (
                                    consts.FISCAL_DRIVE_NUMBER
                                ),
                                'fiscal_document_number': (
                                    consts.FISCAL_DOCUMENT_NUMBER
                                ),
                                'fiscal_sign': consts.FISCAL_SIGN,
                                'sum': '100',
                                'commission_rate': '5',
                                'operation_type': consts.BILLING_INCOME,
                                'date': consts.OTHER_DATE,
                            },
                        },
                    ),
                    # income_refund
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='CommissionOrder',
                        external_event_ref=f'CommissionOrder/{consts.ORDER_NR}'
                        '/BillingCorrectionReceipt/2',
                        data={
                            'service_order_id': consts.ORDER_NR,
                            'service_id': 661,  # hardcoded const
                            'dt': consts.OTHER_DATE,
                            'client_id': consts.CLIENT_ID,
                            'transaction_currency': 'RUB',
                            'commission_sum': (
                                '-45'
                            ),  # 200 * (5 + 10) / 100 + 15
                            'promocode_sum': '0',
                            'type': 'retail',
                            'total_sum': '-45',
                            'identity': (
                                f'CommissionOrder/{consts.ORDER_NR}'
                                '/BillingCorrectionReceipt/2'
                            ),
                            'payload': {
                                'place_id': str(consts.PLACE_ID),
                                'fiscal_drive_number': (
                                    consts.FISCAL_DRIVE_NUMBER
                                ),
                                'fiscal_document_number': (
                                    consts.FISCAL_DOCUMENT_NUMBER
                                ),
                                'fiscal_sign': consts.FISCAL_SIGN,
                                'sum': '200',
                                'commission_rate': '5',
                                'operation_type': consts.BILLING_INCOME_REFUND,
                                'date': consts.OTHER_DATE,
                            },
                        },
                    ),
                    # expense
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='CommissionOrder',
                        external_event_ref=f'CommissionOrder/{consts.ORDER_NR}'
                        '/BillingCorrectionReceipt/3',
                        data={
                            'service_order_id': consts.ORDER_NR,
                            'service_id': 661,  # hardcoded const
                            'dt': consts.OTHER_DATE,
                            'client_id': consts.CLIENT_ID,
                            'transaction_currency': 'RUB',
                            'commission_sum': (
                                '-60'
                            ),  # 300 * (5 + 10) / 100 + 15
                            'promocode_sum': '0',
                            'type': 'retail',
                            'total_sum': '-60',
                            'identity': (
                                f'CommissionOrder/{consts.ORDER_NR}'
                                '/BillingCorrectionReceipt/3'
                            ),
                            'payload': {
                                'place_id': str(consts.PLACE_ID),
                                'fiscal_drive_number': (
                                    consts.FISCAL_DRIVE_NUMBER
                                ),
                                'fiscal_document_number': (
                                    consts.FISCAL_DOCUMENT_NUMBER
                                ),
                                'fiscal_sign': consts.FISCAL_SIGN,
                                'sum': '300',
                                'commission_rate': '5',
                                'operation_type': consts.BILLING_EXPENSE,
                                'date': consts.OTHER_DATE,
                            },
                        },
                    ),
                    # expense_refund
                    helpers.make_billing_doc(
                        order_nr=consts.ORDER_NR,
                        kind='CommissionOrder',
                        external_event_ref=f'CommissionOrder/{consts.ORDER_NR}'
                        '/BillingCorrectionReceipt/4',
                        data={
                            'service_order_id': consts.ORDER_NR,
                            'service_id': 661,  # hardcoded const
                            'dt': consts.OTHER_DATE,
                            'client_id': consts.CLIENT_ID,
                            'transaction_currency': 'RUB',
                            'commission_sum': (
                                '75'
                            ),  # 400 * (5 + 10) / 100 + 15
                            'promocode_sum': '0',
                            'type': 'retail',
                            'total_sum': '75',
                            'identity': (
                                f'CommissionOrder/{consts.ORDER_NR}'
                                '/BillingCorrectionReceipt/4'
                            ),
                            'payload': {
                                'place_id': str(consts.PLACE_ID),
                                'fiscal_drive_number': (
                                    consts.FISCAL_DRIVE_NUMBER
                                ),
                                'fiscal_document_number': (
                                    consts.FISCAL_DOCUMENT_NUMBER
                                ),
                                'fiscal_sign': consts.FISCAL_SIGN,
                                'sum': '400',
                                'commission_rate': '5',
                                'operation_type': (
                                    consts.BILLING_EXPENSE_REFUND
                                ),
                                'date': consts.OTHER_DATE,
                            },
                        },
                    ),
                ],
            ),
            # expected_finish_requests
            [
                helpers.make_storage_finish_request(
                    doc_id=2147995772, status='complete',
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
            ],
            # expected_business_rules_requests
            [
                helpers.make_business_rules_request(
                    # кодогенеренная ручка переводит таймштамп в UTC
                    billing_date=consts.OTHER_DATE_UTC,
                    counteragent_type='place',
                    counteragent_details={
                        'place_id': str(consts.PLACE_ID),
                        'commission_type': 'delivery',
                    },
                ),
                helpers.make_business_rules_request(
                    # кодогенеренная ручка переводит таймштамп в UTC
                    billing_date=consts.OTHER_DATE_UTC,
                    counteragent_type='place',
                    counteragent_details={
                        'place_id': str(consts.PLACE_ID),
                        'commission_type': 'delivery',
                    },
                ),
                helpers.make_business_rules_request(
                    # кодогенеренная ручка переводит таймштамп в UTC
                    billing_date=consts.OTHER_DATE_UTC,
                    counteragent_type='place',
                    counteragent_details={
                        'place_id': str(consts.PLACE_ID),
                        'commission_type': 'delivery',
                    },
                ),
                helpers.make_business_rules_request(
                    # кодогенеренная ручка переводит таймштамп в UTC
                    billing_date=consts.OTHER_DATE_UTC,
                    counteragent_type='place',
                    counteragent_details={
                        'place_id': str(consts.PLACE_ID),
                        'commission_type': 'delivery',
                    },
                ),
            ],
            # business_rules_response
            [
                helpers.make_business_rules_response(
                    client_id=consts.CLIENT_ID,
                    commission=5,
                    acquiring_commission=10,
                    fix_commission=15,
                ),
                helpers.make_business_rules_response(
                    client_id=consts.CLIENT_ID,
                    commission=5,
                    acquiring_commission=10,
                    fix_commission=15,
                ),
                helpers.make_business_rules_response(
                    client_id=consts.CLIENT_ID,
                    commission=5,
                    acquiring_commission=10,
                    fix_commission=15,
                ),
                helpers.make_business_rules_response(
                    client_id=consts.CLIENT_ID,
                    commission=5,
                    acquiring_commission=10,
                    fix_commission=15,
                ),
            ],
            # expected_input_stq_fail
            False,
            id='CommissionOrder created.',
        ),
    ],
)
async def test_billing_receipt_validated(
        stq_runner,
        mock_storage_search,
        mock_storage_store,
        mock_storage_finish,
        mock_business_rules,
        mock_create_handler,
        input_stq_args,
        expected_search_request,
        search_response,
        expected_store_request,
        expected_finish_requests,
        expected_business_rules_requests,
        business_rules_responses,
        expected_input_stq_fail,
):
    await helpers.billing_processing_test_func(
        stq_runner,
        mock_storage_search,
        mock_storage_store,
        mock_storage_finish,
        mock_business_rules,
        mock_create_handler,
        input_stq_args,
        expected_search_request,
        search_response,
        expected_store_request,
        expected_finish_requests,
        expected_business_rules_requests,
        business_rules_responses,
        expected_input_stq_fail,
    )
