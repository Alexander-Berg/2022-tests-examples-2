import pytest
import yaml

from tests_eats_billing_processor import rules
from tests_eats_billing_processor.transformer import common
from tests_eats_billing_processor.transformer import helper


@pytest.mark.config(
    EATS_BILLING_PROCESSOR_RULES=yaml.load(
        """
default:
    billing_payment:
        - skip:
            - test#tlog-transactions:
                    order-nr: "55555"
""",
        Loader=yaml.SafeLoader,
    ),
)
async def test_tlog_transactions(testpoint, transformer_fixtures):
    payment = common.billing_event(
        client_info=rules.client_info(client_id='12345'),
        version='2',
        payment=common.payment(
            payment_method='card',
            product_type='product',
            product_id='product__001',
            currency='RUB',
            amount='1500',
            payment_terminal_id='553344',
        ),
    )
    result = {}

    @testpoint('skip_event')
    def skip_testpoint(data):
        nonlocal result
        result = data

    await (
        helper.TransformerTest()
        .with_order_nr('555555')
        .insert_input_event(kind='billing_payment', data=payment)
        .tlog_docs(
            docs=[
                helper.make_doc(
                    doc_id=1,
                    transaction={
                        'product': 'eats_marketing_coupon',
                        'amount_with_vat': '100',
                        'currency': 'RUB',
                        'transaction_type': 'payment',
                        'payload': {'product': 'product'},
                        'detailed_product': 'eats_marketing_promotion',
                    },
                ),
                helper.make_doc(
                    doc_id=12,
                    transaction={
                        'product': 'eats_marketing_coupon_employee',
                        'amount_with_vat': '50',
                        'currency': 'RUB',
                        'transaction_type': 'refund',
                        'payload': {'product': 'product'},
                        'detailed_product': 'eats_marketing_coupon_employee',
                    },
                ),
                helper.make_doc(
                    doc_id=2,
                    transaction={
                        'product': 'eats_support_coupon',
                        'amount_with_vat': '200',
                        'currency': 'RUB',
                        'transaction_type': 'payment',
                        'payload': {'product': 'product'},
                        'detailed_product': 'eats_support_coupon',
                    },
                ),
                helper.make_doc(
                    doc_id=3,
                    transaction={
                        'product': 'eats_b2b_coupon',
                        'amount_with_vat': '300',
                        'currency': 'RUB',
                        'transaction_type': 'payment',
                        'payload': {'product': 'product'},
                        'detailed_product': 'eats_b2b_coupon',
                    },
                ),
                helper.make_doc(
                    doc_id=4,
                    transaction={
                        'product': 'eats_b2b_coupon_picker',
                        'amount_with_vat': '400',
                        'currency': 'RUB',
                        'transaction_type': 'payment',
                        'payload': {'product': 'product'},
                        'detailed_product': 'eats_b2b_coupon_picker',
                    },
                ),
                helper.make_doc(
                    doc_id=5,
                    transaction={
                        'product': 'eats_payment_not_received',
                        'amount_with_vat': '500',
                        'currency': 'RUB',
                        'transaction_type': 'payment',
                        'payload': {'product': 'product'},
                        'detailed_product': 'eats_payment_not_received',
                    },
                ),
                helper.make_doc(
                    doc_id=6,
                    transaction={
                        'product': 'eats_account_correction',
                        'amount_with_vat': '600',
                        'currency': 'RUB',
                        'transaction_type': 'payment',
                        'payload': {'product': 'product'},
                        'detailed_product': 'eats_account_correction',
                    },
                ),
                helper.make_doc(
                    doc_id=7,
                    transaction={
                        'product': 'eats_marketing_coupon',
                        'amount': '100',
                        'currency': 'RUB',
                        'transaction_type': 'payment',
                        'payload': {'product': 'delivery'},
                        'detailed_product': 'eats_marketing_promotion',
                    },
                ),
                helper.make_doc(
                    doc_id=8,
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
                    doc_id=8,
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
        .no_stq_call_expected()
        .run(transformer_fixtures)
    )

    assert skip_testpoint.times_called == 1
    assert result == {
        'test': [
            {
                'product_type': 'product',
                'amount': '100',
                'transaction_type': 'payment',
                'product': 'eats_marketing_coupon',
                'detailed_product': 'eats_marketing_promotion',
            },
            {
                'product_type': 'product',
                'amount': '50',
                'transaction_type': 'refund',
                'product': 'eats_marketing_coupon_employee',
                'detailed_product': 'eats_marketing_coupon_employee',
            },
            {
                'product_type': 'product',
                'amount': '200',
                'transaction_type': 'payment',
                'product': 'eats_support_coupon',
                'detailed_product': 'eats_support_coupon',
            },
            {
                'product_type': 'product',
                'amount': '300',
                'transaction_type': 'payment',
                'product': 'eats_b2b_coupon',
                'detailed_product': 'eats_b2b_coupon',
            },
            {
                'product_type': 'product',
                'amount': '400',
                'transaction_type': 'payment',
                'product': 'eats_b2b_coupon_picker',
                'detailed_product': 'eats_b2b_coupon_picker',
            },
            {
                'product_type': 'product',
                'amount': '500',
                'transaction_type': 'payment',
                'product': 'eats_payment_not_received',
                'detailed_product': 'eats_payment_not_received',
            },
            {
                'product_type': 'product',
                'amount': '600',
                'transaction_type': 'payment',
                'product': 'eats_account_correction',
                'detailed_product': 'eats_account_correction',
            },
            {
                'product_type': 'delivery',
                'amount': '100',
                'transaction_type': 'payment',
                'product': 'eats_marketing_coupon',
                'detailed_product': 'eats_marketing_promotion',
            },
        ],
    }
