import copy

import pytest

from taxi_billing_calculators.stq.manual_transactions import (
    task as manual_transactions_task,
)
from taxi_billing_calculators.calculators.manual_transactions import (  # noqa: IS001
    helper as mtr_helper,
    processors_mapping as mtp_mapping,
)
from . import common


_BILLING_PAYOUT_PAYMENTS_SETTINGS = {
    'subvention_misc_netted': {
        'product': 'subvention',
        'detailed_product': 'subsidy_misc',
        'service_id': 111,
        'accounting_table': 'revenues',
    },
    'subvention_misc_paid': {
        'product': 'subvention',
        'detailed_product': 'subsidy_misc',
        'service_id': 137,
        'accounting_table': 'expenses',
    },
    'dooh_fix': {
        'product': 'dooh_fix',
        'detailed_product': 'dooh_fix',
        'service_id': 724,
        'accounting_table': 'expenses',
    },
    'driver_referrals': {
        'product': 'driver_referrals',
        'detailed_product': 'driver_acquisition_channels_referrals',
        'service_id': 137,
        'accounting_table': 'expenses',
    },
    'trip_payment_card': {
        'product': 'trip_payment',
        'detailed_product': 'trip_payment',
        'service_id': 124,
        'accounting_table': 'payments',
    },
    'eats_retail_assembling_marketing_promocode_picker': {
        'product': 'eats_marketing_coupon_picker',
        'detailed_product': 'eats_marketing_promocode_picker',
        'service_id': 663,
        'accounting_table': 'eats_expenses',
    },
    'eats_delivery_fee_tips_delivery_fee_cs': {
        'product': 'eats_delivery_fee',
        'detailed_product': 'delivery_fee_cs',
        'service_id': 645,
        'accounting_table': 'eats_revenues',
    },
    'eats_payments_client_service_fee_payment': {
        'accounting_table': 'eats_payments',
        'detailed_product': 'eats_client_service_fee_payment',
        'product': 'eats_client_service_fee',
        'service_id': 1167,
    },
    'eats_inplace_payments_payment': {
        'accounting_table': 'eats_agent',
        'detailed_product': 'eats_payment',
        'product': 'eats_payment',
        'service_id': 1176,
    },
}


_BILLING_MANUAL_TRANSACTIONS_SETTINGS = {
    'grocery_courier_delivery': {
        'product': 'lavka_product',
        'detailed_product': 'courier_payment',
        'service_id': 322,
        'paid_to': 'partner',
        'processor': 'grocery_courier',
    },
    'grocery_courier_coupon': {
        'product': 'lavka_product',
        'detailed_product': 'courier_payment',
        'service_id': 322,
        'paid_to': 'partner',
        'processor': 'grocery_courier',
    },
    'subvention_misc': {
        'product': 'subvention',
        'detailed_product': 'subsidy_misc',
        'service_id': 228,
        'paid_to': 'performer',
        'processor': 'subvention',
    },
    'commission_cash': {
        'product': 'order',
        'detailed_product': 'gross_commission_trips',
        'service_id': 211,
        'paid_to': 'performer',
        'processor': 'commission',
    },
    'commission_card': {
        'product': 'order',
        'detailed_product': 'gross_commission_trips',
        'service_id': 228,
        'paid_to': 'performer',
        'processor': 'commission',
    },
    'arbitrary_revenues': {
        'category_type': 'universal',
        'description': 'Arbitrary revenues payment',
        'detailed_product': 'default',
        'paid_to': 'partner',
        'product': 'default',
        'service_id': 111,
        'processor': 'arbitrary_revenues',
    },
    'arbitrary_expenses': {
        'category_type': 'universal',
        'description': 'Arbitrary expenses payment',
        'detailed_product': 'default',
        'paid_to': 'partner',
        'product': 'default',
        'service_id': 111,
        'processor': 'arbitrary_expenses',
    },
    'remittance_order': {
        'category_type': 'universal',
        'description': 'Remittance_order event',
        'detailed_product': 'default',
        'paid_to': 'partner',
        'product': 'default',
        'service_id': 0,
        'processor': 'remittance_order',
    },
    'foo_bar': {
        'product': 'foo_bar',
        'detailed_product': 'foo_bar',
        'service_id': 0,
        'paid_to': 'performer',
    },
    'arbitrary_payments': {
        'category_type': 'universal',
        'description': 'Arbitrary payments payment',
        'detailed_product': 'default',
        'paid_to': 'partner',
        'product': 'default',
        'service_id': 0,
        'processor': 'arbitrary_payments',
    },
    'arbitrary_eats_expenses': {
        'category_type': 'universal',
        'description': 'Arbitrary eats expenses payment',
        'detailed_product': 'default',
        'paid_to': 'partner',
        'processor': 'arbitrary_eats_expenses',
        'product': 'default',
        'service_id': 0,
    },
    'arbitrary_eats_revenues': {
        'category_type': 'universal',
        'description': 'Arbitrary eats revenues payment',
        'detailed_product': 'default',
        'paid_to': 'partner',
        'processor': 'arbitrary_eats_revenues',
        'product': 'default',
        'service_id': 0,
    },
    'arbitrary_eats_payments': {
        'category_type': 'universal',
        'description': 'Arbitrary eats payments payment',
        'detailed_product': 'default',
        'paid_to': 'partner',
        'processor': 'arbitrary_eats_payments',
        'product': 'default',
        'service_id': 0,
    },
    'arbitrary_eats_agent': {
        'category_type': 'universal',
        'description': 'Arbitrary eats agent payment',
        'detailed_product': 'default',
        'paid_to': 'partner',
        'processor': 'arbitrary_eats_agent',
        'product': 'default',
        'service_id': 0,
    },
}


@pytest.mark.config(
    BILLING_MANUAL_TRANSACTIONS_SETTINGS=_BILLING_MANUAL_TRANSACTIONS_SETTINGS,
    BILLING_TLOG_SERVICE_IDS={'commission/card': 228, 'commission/cash': 211},
    BILLING_CALCULATORS_MANUAL_TRANSACTIONS_STQ_SETTINGS={
        '__default__': {
            'one_doc_transactions_size': 500,
            'chunk_size': 10,
            'sleep_between_chunks_sec': 0.5,
        },
    },
    BILLING_PAYOUT_PAYMENTS_SETTINGS=_BILLING_PAYOUT_PAYMENTS_SETTINGS,
)
@pytest.mark.filldb(cities='test_process_doc_manual_transactions')
@pytest.mark.now('2020-10-23T12:40:00+03:00')
@pytest.mark.parametrize(
    'data_path,doc_id',
    [
        ('manual_transactions_split.json', 1001),
        ('manual_transactions_lavka.json', 1001),
        ('manual_transactions_lavka_negative.json', 1001),
        ('manual_transactions_lavka_from_yt.json', 1001),
        ('manual_transactions_subvention_misc.json', 1001),
        ('manual_transactions_commission_cash_rebate.json', 1001),
        ('manual_transactions_commission_card.json', 1001),
        ('manual_transactions_no_settings.json', 1001),
        ('manual_transactions_no_handler.json', 1001),
        ('manual_transactions_arbitrary_revenues.json', 1001),
        ('manual_transactions_arbitrary_payments.json', 1001),
        ('manual_transactions_arbitrary_eats_expenses.json', 1001),
        ('manual_transactions_arbitrary_eats_revenues.json', 1001),
        ('manual_transactions_arbitrary_eats_payments.json', 1001),
        ('manual_transactions_arbitrary_eats_agent.json', 1001),
    ],
)
# pylint: disable=invalid-name
async def test_process_doc_manual_transactions(
        data_path,
        doc_id,
        load_json,
        patch_aiohttp_session,
        response_mock,
        mockserver,
        patch,
        taxi_billing_calculators_stq_manual_transactions_ctx,
):
    json_data = load_json(data_path)

    @patch('yt.wrapper.read_table')
    def _yt_wrapper_read_table(*args, **kwargs):
        return json_data['yt_table_data']

    @patch('taxi.clients.mds_s3.MdsS3Client.download_content')
    async def _download_content(*args, **kwargs):
        mds_file = json_data['mds_file']
        content = '\n'.join(mds_file)
        return bytearray(content.encode('utf-8'))

    @mockserver.json_handler('billing-replication/v1/active-contracts/')
    async def _fetch_active_contracts(*args, **kwargs):
        return json_data.get('billing_replication_contracts', [])

    @mockserver.json_handler(
        'parks-replica/v1/parks/billing_client_id/retrieve',
    )
    def _billing_client_id_retrieve(_):
        return {'billing_client_id': 'billing_client_id_1'}

    @mockserver.json_handler('parks-replica/v1/parks/retrieve')
    def _parks_retrieve(*args, **kwargs):
        return {'parks': [{'park_id': '', 'data': {'city': 'moscow'}}]}

    @mockserver.json_handler('billing-commissions/v1/rules/match')
    async def _get_commission_rules(*args, **kwargs):
        return {
            'agreements': [
                {
                    'vat': '1.2',
                    'rate': {'kind': 'flat'},
                    'cancelation_settings': {
                        'park_billable_cancel_interval': ['1', '2'],
                        'user_billable_cancel_interval': ['1', '2'],
                    },
                    'group': 'base',
                },
            ],
        }

    results = await common.test_process_doc(
        data_path,
        doc_id,
        load_json,
        patch_aiohttp_session,
        response_mock,
        mockserver,
        taxi_billing_calculators_stq_manual_transactions_ctx,
        patch,
        asserts=False,
        stq_queue_task=manual_transactions_task,
    )
    for expected, actual in results:
        assert actual == expected


@pytest.mark.now('2020-10-23T12:40:00+03:00')
@pytest.mark.config(
    BILLING_PAYOUT_PAYMENTS_SETTINGS=_BILLING_PAYOUT_PAYMENTS_SETTINGS,
    BILLING_TLOG_AGGREGATION_SIGN_BY_PRODUCT={
        'subvention': {'payment': 1, 'refund': -1},
    },
    BILLING_MANUAL_TRANSACTIONS_SETTINGS=_BILLING_MANUAL_TRANSACTIONS_SETTINGS,
    BILLING_MANUAL_TRANSACTIONS_VALIDATE_CONTRACTS='enable',
)
@pytest.mark.parametrize(
    'data_path,doc_id',
    [
        ('manual_transactions_yt_remittance_order.json', 1001),
        ('manual_transactions_yt_upload_revenues.json', 1001),
        ('manual_transactions_yt_upload_expenses.json', 1001),
        ('manual_transactions_yt_upload_payments.json', 1001),
        ('manual_transactions_csv_upload.json', 1001),
        ('manual_transactions_csv_upload_wrong_header.json', 1001),
        ('manual_transactions_csv_upload_universal_newline.json', 1001),
    ],
)
# pylint: disable=invalid-name
async def test_process_doc_manual_transactions_upload(
        data_path,
        doc_id,
        load_json,
        patch_aiohttp_session,
        response_mock,
        mockserver,
        patch,
        taxi_billing_calculators_stq_manual_transactions_ctx,
):
    json_data = load_json(data_path)

    @patch('taxi.clients.mds_s3.MdsS3Client.download_content')
    async def _download_content(*args, **kwargs):
        mds_file = json_data['mds_file']
        newline = json_data.get('newline', '\n')
        content = newline.join(mds_file)
        return bytearray(content.encode('utf-8'))

    @patch('yt.wrapper.copy')
    def _yt_wrapper_copy(*args, **kwargs):
        pass

    @patch('yt.wrapper.create_table')
    def _yt_wrapper_create_table(*args, **kwargs):
        pass

    @patch('yt.wrapper.write_table')
    def _yt_wrapper_write_table(*args, **kwargs):
        pass

    @patch('yt.wrapper.read_table')
    def _yt_wrapper_read_table(*args, **kwargs):
        return json_data['yt_table_data']

    actual_contracts_to_check = []

    @mockserver.json_handler('/billing-replication/v1/check_contracts/')
    def _check_contracts(request):
        actual_contracts_to_check.extend(request.json['contracts'])
        check_contracts = copy.deepcopy(request.json['contracts'])
        for contract in check_contracts:
            contract['is_valid'] = True
        return {'contracts': check_contracts}

    results = await common.test_process_doc(
        data_path,
        doc_id,
        load_json,
        patch_aiohttp_session,
        response_mock,
        mockserver,
        taxi_billing_calculators_stq_manual_transactions_ctx,
        patch,
        asserts=False,
        stq_queue_task=manual_transactions_task,
    )
    for expected, actual in results:
        assert actual == expected

    if json_data.get('contracts_to_check') is not None:

        def _sort_contracts(contracts):
            return sorted(
                contracts,
                key=lambda contract: (
                    contract['client_id'],
                    contract['contract_id'],
                    contract['service_id'],
                    contract['currency'],
                ),
            )

        assert _sort_contracts(actual_contracts_to_check) == _sort_contracts(
            json_data['contracts_to_check'],
        )


@pytest.mark.config(
    BILLING_MANUAL_TRANSACTIONS_SETTINGS=_BILLING_MANUAL_TRANSACTIONS_SETTINGS,
    BILLING_PAYOUT_PAYMENTS_SETTINGS={
        'subvention_misc_netted': {
            'product': 'subvention',
            'detailed_product': 'subsidy_misc',
            'service_id': 111,
            'accounting_table': 'revenues',
        },
        'subvention_misc_paid': {
            'product': 'subvention',
            'detailed_product': 'subsidy_misc',
            'service_id': 137,
            'accounting_table': 'expenses',
        },
        'not_in_aggr_sign': {
            'product': 'not_in_aggr_sign_product',
            'detailed_product': 'detailed_product',
            'service_id': 100,
            'accounting_table': 'revenues',
        },
        'trip_payment_card': {
            'product': 'trip_payment',
            'detailed_product': 'trip_payment',
            'service_id': 124,
            'accounting_table': 'payments',
        },
        'eats_retail_assembling_marketing_promocode_picker': {
            'product': 'eats_marketing_coupon_picker',
            'detailed_product': 'eats_marketing_promocode_picker',
            'service_id': 663,
            'accounting_table': 'eats_expenses',
        },
        'eats_delivery_fee_tips_delivery_fee_cs': {
            'product': 'eats_delivery_fee',
            'detailed_product': 'delivery_fee_cs',
            'service_id': 645,
            'accounting_table': 'eats_revenues',
        },
        'eats_payments_client_service_fee_payment': {
            'accounting_table': 'eats_payments',
            'detailed_product': 'eats_client_service_fee_payment',
            'product': 'eats_client_service_fee',
            'service_id': 1167,
        },
        'eats_inplace_payments_payment': {
            'accounting_table': 'eats_agent',
            'detailed_product': 'eats_payment',
            'product': 'eats_payment',
            'service_id': 1176,
        },
    },
    BILLING_TLOG_AGGREGATION_SIGN_BY_PRODUCT={
        'subvention': {'payment': 1, 'refund': -1},
    },
)
@pytest.mark.parametrize(
    'data_path',
    [
        'valid_grocery_courier_delivery.json',
        'valid_grocery_courier_coupon.json',
        'grocery_courier_delivery_zero_amount.json',
        'grocery_courier_delivery_big_amount.json',
        'grocery_courier_delivery_wrong_header.json',
        'grocery_courier_delivery_wrong_vat.json',
        'grocery_courier_delivery_wrong_client_id.json',
        'grocery_courier_delivery_not_int_client_id.json',
        'grocery_courier_delivery_not_int_contract_id.json',
        'grocery_courier_delivery_wrong_invoice_date.json',
        'grocery_courier_delivery_invalid_decimal.json',
        'valid_revenues.json',
        'valid_expenses.json',
        'valid_payments.json',
        'valid_remittance_order.json',
        'valid_remittance_order_signalq_rent.json',
        'valid_remittance_order_cancel.json',
        'remittance_order_not_all_required.json',
        'remittance_order_big_amount.json',
        'remittance_order_cancel_payload_required.json',
        'remittance_order_not_int_client_id.json',
        'remittance_order_not_int_contract_id.json',
        'revenues_not_all_required_fields.json',
        'revenues_empty_bci.json',
        'revenues_negative_amount.json',
        'revenues_big_amount.json',
        'revenues_zero_amount.json',
        'revenues_wrong_invoice_date.json',
        'revenues_wrong_transaction_type.json',
        'revenues_not_in_payments_config.json',
        'revenues_not_in_aggr_sign_config.json',
        'revenues_wrong_template_name.json',
        'revenues_wrong_template_context.json',
        'revenues_invalid_decimal.json',
        'revenues_not_int_client_id.json',
        'revenues_not_int_contract_id.json',
        'valid_eats_expenses.json',
        'valid_eats_revenues.json',
        'valid_eats_payments.json',
        'valid_eats_agent.json',
    ],
)
# pylint: disable=invalid-name
async def test_manual_transactions_validators(
        data_path,
        load_json,
        taxi_billing_calculators_stq_manual_transactions_ctx,
        patch,
        mockserver,
):
    json_data = load_json(data_path)
    transaction_type = json_data['transaction_type']
    # pylint: disable=protected-access
    ctx = taxi_billing_calculators_stq_manual_transactions_ctx
    config = ctx.config
    settings = config.BILLING_MANUAL_TRANSACTIONS_SETTINGS[transaction_type]
    validator_cls = mtp_mapping.get_processor_class(
        settings['processor'],
    ).get_validator_class()
    data_validator = validator_cls(
        config=config,
        billing_replication_client=ctx.billing_replication_client,
        table_rows=json_data['table_rows'],
        log_extra={},
    )

    @mockserver.json_handler('/billing-replication/v1/check_contracts/')
    def _check_contracts(request):
        check_contracts = request.json['contracts']
        for contract in check_contracts:
            contract['is_valid'] = True
        return {'contracts': check_contracts}

    actual_amount_details = None
    exception_happened = None
    try:
        actual_amount_details = await data_validator.validate(
            validate_contracts=True,
        )
    except mtr_helper.ManualTransactionDataValidationException as err:
        exception_happened = err
    assert (
        bool(exception_happened)
        == json_data['is_validation_exception_expected']
    ), exception_happened
    assert actual_amount_details == json_data['expected_amount_details']
