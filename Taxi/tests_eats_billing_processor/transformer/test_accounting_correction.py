import pytest

from tests_eats_billing_processor import rules
from tests_eats_billing_processor.transformer import common
from tests_eats_billing_processor.transformer import helper


@pytest.mark.parametrize(
    'amount, product_type, billing_frequency, expect_product_type',
    [
        pytest.param('100', 'product', 'daily', 'product'),
        pytest.param('100', 'product', 'weekly', 'product_weekly'),
        pytest.param('100', 'product', None, 'product'),
        pytest.param('100', 'delivery', 'daily', 'delivery'),
        pytest.param('100', 'delivery', 'weekly', 'delivery_weekly'),
        pytest.param('100', 'delivery', None, 'delivery'),
        pytest.param('100', 'retail', 'daily', 'retail'),
        pytest.param('100', 'retail', 'weekly', 'retail'),
        pytest.param('100', 'retail', None, 'retail'),
    ],
)
async def test_payment_account_correction(
        transformer_fixtures,
        amount,
        product_type,
        billing_frequency,
        expect_product_type,
):
    data = {
        'amount': amount,
        'correction_id': '12345',
        'currency': 'RUB',
        'order_nr': '201217-305204',
        'originator': 'tariff_editor',
        'place_id': '123456',
        'product_type': product_type,
        'transaction_date': '2021-07-10T12:22:00',
    }
    await (
        helper.TransformerTest()
        .with_order_nr('201217-305204')
        .insert_input_event(kind='payment_accounting_correction', data=data)
        .using_business_rules(
            place_id='123456',
            client_info=rules.client_info(client_id='123456'),
            commission=rules.make_commission(
                commission_type='place_delivery',
                params=rules.simple_commission(
                    commission='10',
                    acquiring_commission='10',
                    fix_commission='10',
                ),
                billing_frequency=billing_frequency,
            ),
        )
        .expect(
            common.billing_event(
                client_id='123456',
                payment=common.payment(
                    payment_method='account_correction',
                    product_type=expect_product_type,
                    amount=amount,
                    product_id='account_correction',
                ),
                payload={'correction_id': '12345'},
            ),
        )
        .expect_stq_call_id(1)
        .run(transformer_fixtures)
    )


@pytest.mark.parametrize(
    'product_type, product, billing_frequency',
    [
        pytest.param('product', 'product', 'daily'),
        pytest.param('product_weekly', 'product', 'weekly'),
        pytest.param('product', 'product', None),
        pytest.param('delivery', 'delivery', 'daily'),
        pytest.param('delivery_weekly', 'delivery', 'weekly'),
        pytest.param('delivery', 'delivery', None),
        pytest.param('retail', 'retail', 'daily'),
        pytest.param('retail', 'retail', 'weekly'),
        pytest.param('retail', 'retail', None),
    ],
)
async def test_all_negative_account_correction(
        transformer_fixtures, product_type, product, billing_frequency,
):
    data = {
        'amount': '1000',
        'correction_id': '12345',
        'currency': 'RUB',
        'order_nr': '201217-305204',
        'originator': 'tariff_editor',
        'place_id': '123456',
        'transaction_date': '2021-07-10T12:22:00',
    }
    await (
        helper.TransformerTest()
        .with_order_nr('201217-305204')
        .insert_input_event(kind='all_accounting_correction', data=data)
        .using_business_rules(
            place_id='123456',
            client_info=rules.client_info(client_id='123456'),
            commission=rules.make_commission(
                commission_type='place_delivery',
                params=rules.simple_commission(
                    commission='10',
                    acquiring_commission='10',
                    fix_commission='10',
                ),
                billing_frequency=billing_frequency,
            ),
        )
        .expect(
            common.billing_event(
                client_id='123456',
                refund=common.payment(
                    payment_method='marketing',
                    product_type=product_type,
                    amount='100',
                    product_id='account_correction',
                ),
                payload={'correction_id': '12345'},
            ),
            common.billing_event(
                client_id='123456',
                payment=common.payment(
                    payment_method='marketing',
                    product_type=product_type,
                    amount='100',
                    product_id='account_correction',
                ),
                payload={'correction_id': '12345'},
            ),
            common.billing_event(
                client_id='123456',
                refund=common.payment(
                    payment_method='marketing_promocode',
                    product_type=product_type,
                    amount='100',
                    product_id='account_correction',
                ),
                payload={'correction_id': '12345'},
            ),
            common.billing_event(
                client_id='123456',
                payment=common.payment(
                    payment_method='marketing_promocode',
                    product_type=product_type,
                    amount='100',
                    product_id='account_correction',
                ),
                payload={'correction_id': '12345'},
            ),
            common.billing_event(
                client_id='123456',
                refund=common.payment(
                    payment_method='employee_PC',
                    product_type=product_type,
                    amount='100',
                    product_id='account_correction',
                ),
                payload={'correction_id': '12345'},
            ),
            common.billing_event(
                client_id='123456',
                payment=common.payment(
                    payment_method='employee_PC',
                    product_type=product_type,
                    amount='100',
                    product_id='account_correction',
                ),
                payload={'correction_id': '12345'},
            ),
            common.billing_event(
                client_id='123456',
                refund=common.payment(
                    payment_method='compensation_promocode',
                    product_type=product_type,
                    amount='100',
                    product_id='account_correction',
                ),
                payload={'correction_id': '12345'},
            ),
            common.billing_event(
                client_id='123456',
                payment=common.payment(
                    payment_method='compensation_promocode',
                    product_type=product_type,
                    amount='100',
                    product_id='account_correction',
                ),
                payload={'correction_id': '12345'},
            ),
            common.billing_event(
                client_id='123456',
                refund=common.payment(
                    payment_method='corporate',
                    product_type=product_type,
                    amount='100',
                    product_id='account_correction',
                ),
                payload={'correction_id': '12345'},
            ),
            common.billing_event(
                client_id='123456',
                payment=common.payment(
                    payment_method='corporate',
                    product_type=product_type,
                    amount='100',
                    product_id='account_correction',
                ),
                payload={'correction_id': '12345'},
            ),
            common.billing_event(
                client_id='123456',
                refund=common.payment(
                    payment_method='paid_PC',
                    product_type=product_type,
                    amount='100',
                    product_id='account_correction',
                ),
                payload={'correction_id': '12345'},
            ),
            common.billing_event(
                client_id='123456',
                payment=common.payment(
                    payment_method='paid_PC',
                    product_type=product_type,
                    amount='100',
                    product_id='account_correction',
                ),
                payload={'correction_id': '12345'},
            ),
            common.billing_event(
                client_id='123456',
                refund=common.payment(
                    payment_method='picker_corp',
                    product_type=product_type,
                    amount='100',
                    product_id='account_correction',
                ),
                payload={'correction_id': '12345'},
            ),
            common.billing_event(
                client_id='123456',
                payment=common.payment(
                    payment_method='picker_corp',
                    product_type=product_type,
                    amount='100',
                    product_id='account_correction',
                ),
                payload={'correction_id': '12345'},
            ),
            common.billing_event(
                client_id='123456',
                payment=common.payment(
                    payment_method='our_refund',
                    product_type=product_type,
                    amount='100',
                    product_id='account_correction',
                ),
                payload={'correction_id': '12345'},
            ),
            common.billing_event(
                client_id='123456',
                payment=common.payment(
                    payment_method='cashback',
                    product_type=product_type,
                    amount='100',
                    product_id='account_correction',
                ),
                payload={'correction_id': '12345'},
            ),
            common.billing_event(
                client_id='123456',
                refund=common.payment(
                    payment_method='payment_not_received',
                    product_type=product_type,
                    amount='100',
                    product_id='account_correction',
                ),
                payload={'correction_id': '12345'},
            ),
            common.billing_event(
                client_id='123456',
                refund=common.payment(
                    payment_method='account_correction',
                    product_type=product_type,
                    amount='100',
                    product_id='account_correction',
                ),
                payload={'correction_id': '12345'},
            ),
            common.billing_event(
                client_id='123456',
                payment=common.payment(
                    payment_method='payment_not_received',
                    product_type=product_type,
                    amount='100',
                    product_id='account_correction',
                ),
                payload={'correction_id': '12345'},
            ),
            common.billing_event(
                client_id='123456',
                payment=common.payment(
                    payment_method='account_correction',
                    product_type=product_type,
                    amount='100',
                    product_id='account_correction',
                ),
                payload={'correction_id': '12345'},
            ),
            common.billing_event(
                client_id='123456',
                refund=common.payment(
                    payment_method='our_refund',
                    product_type=product_type,
                    amount='100',
                    product_id='account_correction',
                ),
                payload={'correction_id': '12345'},
            ),
            common.billing_event(
                client_id='123456',
                refund=common.payment(
                    payment_method='cashback',
                    product_type=product_type,
                    amount='100',
                    product_id='account_correction',
                ),
                payload={'correction_id': '12345'},
            ),
        )
        .tlog_docs(
            docs=[
                helper.make_doc(
                    doc_id=1,
                    transaction={
                        'product': 'eats_marketing_coupon',
                        'amount_with_vat': '100',
                        'currency': 'RUB',
                        'transaction_type': 'payment',
                        'payload': {'product': product},
                        'detailed_product': 'eats_marketing_promotion',
                    },
                ),
                helper.make_doc(
                    doc_id=2,
                    transaction={
                        'product': 'eats_marketing_coupon',
                        'amount_with_vat': '100',
                        'currency': 'RUB',
                        'transaction_type': 'refund',
                        'payload': {'product': product},
                        'detailed_product': 'eats_marketing_promotion',
                    },
                ),
                helper.make_doc(
                    doc_id=3,
                    transaction={
                        'product': 'eats_marketing_coupon',
                        'amount_with_vat': '100',
                        'currency': 'RUB',
                        'transaction_type': 'payment',
                        'payload': {'product': product},
                        'detailed_product': 'eats_marketing_promocode',
                    },
                ),
                helper.make_doc(
                    doc_id=4,
                    transaction={
                        'product': 'eats_marketing_coupon',
                        'amount_with_vat': '100',
                        'currency': 'RUB',
                        'transaction_type': 'refund',
                        'payload': {'product': product},
                        'detailed_product': 'eats_marketing_promocode',
                    },
                ),
                helper.make_doc(
                    doc_id=5,
                    transaction={
                        'product': 'eats_marketing_coupon_employee',
                        'amount_with_vat': '100',
                        'currency': 'RUB',
                        'transaction_type': 'payment',
                        'payload': {'product': product},
                        'detailed_product': 'eats_marketing_coupon_employee',
                    },
                ),
                helper.make_doc(
                    doc_id=6,
                    transaction={
                        'product': 'eats_marketing_coupon_employee',
                        'amount_with_vat': '100',
                        'currency': 'RUB',
                        'transaction_type': 'refund',
                        'payload': {'product': product},
                        'detailed_product': 'eats_marketing_coupon_employee',
                    },
                ),
                helper.make_doc(
                    doc_id=7,
                    transaction={
                        'product': 'eats_support_coupon',
                        'amount_with_vat': '100',
                        'currency': 'RUB',
                        'transaction_type': 'payment',
                        'payload': {'product': product},
                        'detailed_product': 'eats_support_coupon',
                    },
                ),
                helper.make_doc(
                    doc_id=8,
                    transaction={
                        'product': 'eats_support_coupon',
                        'amount_with_vat': '100',
                        'currency': 'RUB',
                        'transaction_type': 'refund',
                        'payload': {'product': product},
                        'detailed_product': 'eats_support_coupon',
                    },
                ),
                helper.make_doc(
                    doc_id=9,
                    transaction={
                        'product': 'eats_b2b_coupon',
                        'amount_with_vat': '100',
                        'currency': 'RUB',
                        'transaction_type': 'payment',
                        'payload': {'product': product},
                        'detailed_product': 'eats_b2b_coupon_corporate',
                    },
                ),
                helper.make_doc(
                    doc_id=10,
                    transaction={
                        'product': 'eats_b2b_coupon',
                        'amount_with_vat': '100',
                        'currency': 'RUB',
                        'transaction_type': 'refund',
                        'payload': {'product': product},
                        'detailed_product': 'eats_b2b_coupon_corporate',
                    },
                ),
                helper.make_doc(
                    doc_id=11,
                    transaction={
                        'product': 'eats_b2b_coupon',
                        'amount_with_vat': '100',
                        'currency': 'RUB',
                        'transaction_type': 'payment',
                        'payload': {'product': product},
                        'detailed_product': 'eats_b2b_coupon_paid_pc',
                    },
                ),
                helper.make_doc(
                    doc_id=12,
                    transaction={
                        'product': 'eats_b2b_coupon',
                        'amount_with_vat': '100',
                        'currency': 'RUB',
                        'transaction_type': 'refund',
                        'payload': {'product': product},
                        'detailed_product': 'eats_b2b_coupon_paid_pc',
                    },
                ),
                helper.make_doc(
                    doc_id=13,
                    transaction={
                        'product': 'eats_b2b_coupon_picker',
                        'amount_with_vat': '100',
                        'currency': 'RUB',
                        'transaction_type': 'payment',
                        'payload': {'product': product},
                        'detailed_product': 'eats_b2b_coupon_picker',
                    },
                ),
                helper.make_doc(
                    doc_id=14,
                    transaction={
                        'product': 'eats_b2b_coupon_picker',
                        'amount_with_vat': '100',
                        'currency': 'RUB',
                        'transaction_type': 'refund',
                        'payload': {'product': product},
                        'detailed_product': 'eats_b2b_coupon_picker',
                    },
                ),
                helper.make_doc(
                    doc_id=15,
                    transaction={
                        'product': 'eats_payment_not_received',
                        'amount_with_vat': '100',
                        'currency': 'RUB',
                        'transaction_type': 'payment',
                        'payload': {'product': product},
                        'detailed_product': 'eats_payment_not_received',
                    },
                ),
                helper.make_doc(
                    doc_id=16,
                    transaction={
                        'product': 'eats_payment_not_received',
                        'amount_with_vat': '100',
                        'currency': 'RUB',
                        'transaction_type': 'refund',
                        'payload': {'product': product},
                        'detailed_product': 'eats_payment_not_received',
                    },
                ),
                helper.make_doc(
                    doc_id=17,
                    transaction={
                        'product': 'eats_our_refund',
                        'amount_with_vat': '100',
                        'currency': 'RUB',
                        'transaction_type': 'payment',
                        'payload': {'product': product},
                        'detailed_product': 'eats_our_refund',
                    },
                ),
                helper.make_doc(
                    doc_id=18,
                    transaction={
                        'product': 'eats_our_refund',
                        'amount_with_vat': '100',
                        'currency': 'RUB',
                        'transaction_type': 'refund',
                        'payload': {'product': product},
                        'detailed_product': 'eats_our_refund',
                    },
                ),
                helper.make_doc(
                    doc_id=19,
                    transaction={
                        'product': 'eats_account_correction',
                        'amount_with_vat': '100',
                        'currency': 'RUB',
                        'transaction_type': 'payment',
                        'payload': {'product': product},
                        'detailed_product': 'eats_account_correction',
                    },
                ),
                helper.make_doc(
                    doc_id=20,
                    transaction={
                        'product': 'eats_account_correction',
                        'amount_with_vat': '100',
                        'currency': 'RUB',
                        'transaction_type': 'refund',
                        'payload': {'product': product},
                        'detailed_product': 'eats_account_correction',
                    },
                ),
                helper.make_doc(
                    doc_id=21,
                    transaction={
                        'product': 'eats_coupon_plus',
                        'amount': '100',
                        'currency': 'RUB',
                        'transaction_type': 'payment',
                        'payload': {'product': product},
                        'detailed_product': 'eats_coupon_plus',
                    },
                ),
                helper.make_doc(
                    doc_id=22,
                    transaction={
                        'product': 'eats_coupon_plus',
                        'amount': '100',
                        'currency': 'RUB',
                        'transaction_type': 'refund',
                        'payload': {'product': product},
                        'detailed_product': 'eats_coupon_plus',
                    },
                ),
                helper.make_doc(
                    doc_id=23,
                    transaction={
                        'product': 'eats_badge_corporate',
                        'amount_with_vat': '100',
                        'currency': 'RUB',
                        'transaction_type': 'payment',
                        'payload': {'product': 'retail'},
                        'detailed_product': 'eats_badge_corporate',
                    },
                ),
                helper.make_doc(
                    doc_id=24,
                    transaction={
                        'product': 'eats_payment',
                        'amount_with_vat': '100',
                        'currency': 'RUB',
                        'transaction_type': 'payment',
                        'payload': {'product': 'retail'},
                        'detailed_product': 'eats_payment',
                    },
                ),
            ],
        )
        .expect_stq_call_id(1)
        .run(transformer_fixtures)
    )
