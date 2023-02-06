import pytest

from tests_eats_billing_processor.billing_processor import helper


async def test_core_write_back(billing_processor_fixtures):
    payment1 = billing_processor_fixtures.load_json('billing_payment.json')
    payment2 = billing_processor_fixtures.load_json('billing_payment.json')
    payment2['external_payment_id'] = 'another_payment'
    commission1 = billing_processor_fixtures.load_json(
        'billing_commission.json',
    )
    refund1 = billing_processor_fixtures.load_json('billing_refund.json')
    refund2 = billing_processor_fixtures.load_json('billing_refund.json')
    refund2['external_payment_id'] = 'another_payment'
    commission2 = billing_processor_fixtures.load_json(
        'billing_commission.json',
    )
    commission2['commission']['amount'] = '-20'
    commission3 = billing_processor_fixtures.load_json(
        'billing_commission.json',
    )
    commission3['external_payment_id'] = 'yet_another_payment'
    await (
        helper.BillingProcessorTest()
        .for_order_nr('123456-654321')
        .insert_billing_event(data=payment1)
        .insert_billing_event(data=payment2)
        .insert_billing_event(data=commission1)
        .insert_billing_event(data=refund1)
        .insert_billing_event(data=refund2)
        .insert_billing_event(data=commission2)
        .insert_billing_event(data=commission3)
        .checking_columns('kind', 'orig_id')
        .expect_transfers(
            ('payment', None),
            ('payment', None),
            ('commission', 1),
            ('refund', None),
            ('refund', None),
            ('commission', 4),
            ('commission', None),
        )
        .expect_core_write_back(
            ('payment', '1500', '10'),
            ('payment', '1500', '0'),
            ('refund', '150', '20'),
            ('refund', '150', '0'),
            ('commission', '10'),
        )
        .run(billing_processor_fixtures)
    )


async def test_core_write_back_with_white_list(billing_processor_fixtures):
    payment = billing_processor_fixtures.load_json('billing_payment.json')
    await (
        helper.BillingProcessorTest()
        .for_order_nr('123456-654321')
        .insert_billing_event(data=payment)
        .checking_columns('kind', 'orig_id')
        .expect_transfers(('payment', None))
        .expect_core_write_back(('payment', '1500', '0'))
        .run(billing_processor_fixtures)
    )


async def test_account_correction_disable(billing_processor_fixtures):
    payment = billing_processor_fixtures.load_json('billing_payment.json')
    payment['payload']['correction_id'] = '123456'
    await (
        helper.BillingProcessorTest()
        .for_order_nr('123456-654321')
        .insert_billing_event(data=payment)
        .run(billing_processor_fixtures)
    )


@pytest.mark.config(
    EDA_CORE_SWITCH_TO_EATS_BILLING_PROCESSOR={
        'plus_billing_tlog_start_date': '2030-01-01T00:00:00+03:00',
    },
)
@pytest.mark.pgsql(
    'eats_billing_processor', files=['test_input_event_plus.sql'],
)
async def test_core_write_back_plus_disable(billing_processor_fixtures):
    payment = billing_processor_fixtures.load_json('billing_payment.json')
    await (
        helper.BillingProcessorTest()
        .for_order_nr('123456-654321')
        .insert_billing_event(data=payment, input_event_id=1)
        .insert_billing_event(data=payment, input_event_id=2)
        .checking_columns('kind', 'orig_id')
        .expect_transfers(('payment', None), ('payment', None))
        .run(billing_processor_fixtures)
    )


@pytest.mark.config(
    EDA_CORE_SWITCH_TO_EATS_BILLING_PROCESSOR={
        'plus_billing_tlog_start_date': '2010-01-01T00:00:00+03:00',
    },
)
@pytest.mark.pgsql(
    'eats_billing_processor', files=['test_input_event_plus.sql'],
)
async def test_core_write_back_plus_enable(billing_processor_fixtures):
    payment = billing_processor_fixtures.load_json('billing_payment.json')
    await (
        helper.BillingProcessorTest()
        .for_order_nr('123456-654321')
        .insert_billing_event(data=payment, input_event_id=1)
        .insert_billing_event(data=payment, input_event_id=2)
        .checking_columns('kind', 'orig_id')
        .expect_transfers(('payment', None), ('payment', None))
        .expect_core_write_back(
            ('payment', '1500', '0'), ('payment', '1500', '0'),
        )
        .run(billing_processor_fixtures)
    )


@pytest.mark.config(
    EDA_CORE_SWITCH_TO_EATS_BILLING_PROCESSOR={
        'retail_billing_tlog_start_date': '2030-01-01T00:00:00+03:00',
    },
)
@pytest.mark.pgsql(
    'eats_billing_processor', files=['test_input_event_retail.sql'],
)
async def test_core_write_back_retail(billing_processor_fixtures):
    payment = billing_processor_fixtures.load_json('billing_payment.json')
    payment['transaction_date'] = '2030-01-01T12:11:00+00:00'
    payment1 = billing_processor_fixtures.load_json('billing_payment.json')
    await (
        helper.BillingProcessorTest()
        .for_order_nr('123456-654321')
        .insert_billing_event(data=payment, input_event_id=2)
        .insert_billing_event(data=payment1, input_event_id=2)
        .checking_columns('kind', 'orig_id')
        .expect_transfers(('payment', None))
        .expect_transfers(('payment', None))
        .expect_core_write_back(('payment', '1500', '0'))
        .run(billing_processor_fixtures)
    )


@pytest.mark.config(
    EATS_BILLING_PROCESSOR_FEATURES={
        'core_write_back_enabled': True,
        'core_write_back_whitelist': ['billing_refund'],
    },
    EATS_BILLING_PROCESSOR_TRANSACTION_FILTER={
        'test_filter': {
            'filter': {'kind': {'in': ['billing_payment']}},
            'enabled': True,
        },
    },
)
async def test_core_write_back_without_white_list(billing_processor_fixtures):
    payment = billing_processor_fixtures.load_json('billing_payment.json')
    await (
        helper.BillingProcessorTest()
        .for_order_nr('123456-654321')
        .insert_billing_event(data=payment)
        .checking_columns('kind', 'orig_id')
        .expect_transfers(('payment', None))
        .run(billing_processor_fixtures)
    )


async def test_core_write_back_with_product(billing_processor_fixtures):
    payment1 = billing_processor_fixtures.load_json('billing_payment.json')
    payment2 = billing_processor_fixtures.load_json('billing_payment.json')
    payment2['payment']['product_type'] = 'delivery'
    payment2['payment']['product_id'] = 'delivery__001'
    commission1 = billing_processor_fixtures.load_json(
        'billing_commission.json',
    )
    refund1 = billing_processor_fixtures.load_json('billing_refund.json')
    refund2 = billing_processor_fixtures.load_json('billing_refund.json')
    refund2['refund']['product_type'] = 'delivery'
    refund2['refund']['product_id'] = 'delivery__001'
    commission2 = billing_processor_fixtures.load_json(
        'billing_commission.json',
    )
    commission2['commission']['amount'] = '-20'
    commission3 = billing_processor_fixtures.load_json(
        'billing_commission.json',
    )
    commission3['commission']['product_type'] = 'product'
    commission3['commission']['product_id'] = 'product__003'
    await (
        helper.BillingProcessorTest()
        .for_order_nr('123456-654321')
        .insert_billing_event(data=payment1)
        .insert_billing_event(data=payment2)
        .insert_billing_event(data=commission1)
        .insert_billing_event(data=refund1)
        .insert_billing_event(data=refund2)
        .insert_billing_event(data=commission2)
        .insert_billing_event(data=commission3)
        .checking_columns('kind', 'orig_id')
        .expect_transfers(
            ('payment', None),
            ('payment', None),
            ('commission', 1),
            ('refund', None),
            ('refund', None),
            ('commission', 4),
            ('commission', None),
        )
        .expect_core_write_back(
            ('payment', '1500', '10'),
            ('payment', '1500', '0'),
            ('refund', '150', '20'),
            ('refund', '150', '0'),
            ('commission', '10'),
        )
        .run(billing_processor_fixtures)
    )


async def test_core_write_back_two_input_events(billing_processor_fixtures):
    payment1 = billing_processor_fixtures.load_json('billing_payment.json')
    payment2 = billing_processor_fixtures.load_json('billing_payment.json')
    payment2['payment']['product'] = 'another_product'
    commission1 = billing_processor_fixtures.load_json(
        'billing_commission.json',
    )
    await (
        helper.BillingProcessorTest()
        .for_order_nr('123456-654321')
        .insert_billing_event(data=payment1)
        .insert_billing_event(data=payment2, input_event_id=2)
        .insert_billing_event(data=commission1)
        .checking_columns('kind', 'orig_id')
        .expect_transfers(
            ('payment', None), ('commission', 1), ('payment', None),
        )
        .expect_core_write_back(
            ('payment', '1500', '10'), ('payment', '1500', '0'),
        )
        .run(billing_processor_fixtures)
    )


async def test_core_write_back_service_fee(billing_processor_fixtures):
    commission = billing_processor_fixtures.load_json(
        'billing_commission.json',
    )
    commission['commission']['product_id'] = 'service_fee__001'
    commission['commission']['product_type'] = 'service_fee'
    await (
        helper.BillingProcessorTest()
        .for_order_nr('123456-654321')
        .insert_billing_event(data=commission)
        .checking_columns('kind', 'service_id')
        .expect_transfers(('commission', 1167))
        .expect_core_write_back(('commission', '10'))
        .run(billing_processor_fixtures)
    )


async def test_place_compensations(billing_processor_fixtures):
    commission = billing_processor_fixtures.load_json(
        'billing_commission.json',
    )
    commission['commission']['product_id'] = 'rest_expense_delivery'
    commission['commission']['type'] = 'rest_expense_delivery'
    commission['commission']['product_type'] = 'product'
    await (
        helper.BillingProcessorTest()
        .for_order_nr('123456-654321')
        .insert_billing_event(data=commission)
        .checking_columns('kind', 'service_id')
        .expect_transfers(('commission', 628))
        .expect_core_write_back(('commission', '10'))
        .run(billing_processor_fixtures)
    )
