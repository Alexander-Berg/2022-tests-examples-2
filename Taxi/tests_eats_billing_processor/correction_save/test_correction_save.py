import pytest

from tests_eats_billing_processor.correction_save import helper


async def test_happy_path(correction_save_fixtures):
    await (
        helper.CorrectionSaveTest()
        .request(
            order_nr='123456-654322',
            login='anton-vorobev',
            amount='700.00',
            currency='RUB',
            ticket='TESTESTMASHA-200',
            correction_type='product',
            correction_group='payment',
        )
        .expect_amount(amount='200.00')
        .docs(
            docs=[
                helper.make_doc(
                    doc_id=1,
                    transaction={
                        'product': 'eats_marketing_coupon',
                        'amount_with_vat': '500',
                        'currency': 'RUB',
                        'transaction_type': 'payment',
                        'payload': {'product': 'product'},
                        'detailed_product': 'eats_marketing_promotion',
                    },
                ),
            ],
        )
        .run(correction_save_fixtures)
    )


async def test_happy_path_all_negative(correction_save_fixtures):
    await (
        helper.CorrectionSaveTest()
        .request(
            order_nr='123456-654322',
            login='anton-vorobev',
            amount='1400.00',
            currency='RUB',
            ticket='TESTESTMASHA-200',
            correction_type='all_negative',
            correction_group='all',
        )
        .expect_amount(amount='-1400.00')
        .docs(
            docs=[
                helper.make_doc(
                    doc_id=1,
                    transaction={
                        'product': 'eats_marketing_coupon',
                        'amount_with_vat': '700',
                        'currency': 'RUB',
                        'transaction_type': 'payment',
                        'payload': {'product': 'product'},
                        'detailed_product': 'eats_marketing_promotion',
                    },
                ),
                helper.make_doc(
                    doc_id=2,
                    transaction={
                        'product': 'eats_support_coupon',
                        'amount_with_vat': '700',
                        'currency': 'RUB',
                        'transaction_type': 'payment',
                        'payload': {'product': 'product'},
                        'detailed_product': 'eats_support_coupon',
                    },
                ),
            ],
        )
        .run(correction_save_fixtures)
    )


@pytest.mark.parametrize(
    'amount, expect_amount',
    [
        pytest.param('700', '200.00'),
        pytest.param('1000', '500.00'),
        pytest.param('0', '-500.00'),
    ],
)
async def test_happy_path_commission(
        correction_save_fixtures, amount, expect_amount,
):
    await (
        helper.CorrectionSaveTest()
        .request(
            order_nr='123456-654322',
            login='anton-vorobev',
            amount=amount,
            currency='RUB',
            ticket='FINRETAIL-200',
            correction_type='commission_marketplace',
            correction_group='commission',
            product='eats_order_commission_marketplace',
            detailed_product='eats_order_commission_marketplace',
        )
        .expect_amount(amount=expect_amount)
        .docs(
            docs=[
                helper.make_doc(
                    doc_id=1,
                    transaction={
                        'product': 'eats_order_commission_marketplace',
                        'amount_with_vat': '1000',
                        'currency': 'RUB',
                        'transaction_type': 'payment',
                        'detailed_product': (
                            'eats_order_commission_marketplace'
                        ),
                    },
                ),
                helper.make_doc(
                    doc_id=2,
                    transaction={
                        'product': 'eats_order_commission_marketplace',
                        'amount_with_vat': '500',
                        'currency': 'RUB',
                        'transaction_type': 'refund',
                        'detailed_product': (
                            'eats_order_commission_marketplace'
                        ),
                    },
                ),
            ],
        )
        .run(correction_save_fixtures)
    )


async def test_fail(correction_save_fixtures):
    await (
        helper.CorrectionSaveTest()
        .request(
            order_nr='123456-654322',
            login='anton-vorobev',
            amount='500.00',
            currency='RUB',
            ticket='FINRETAIL-200',
            correction_type='product',
            correction_group='payment',
            product='eats_marketing_coupon',
            detailed_product='eats_marketing_coupon',
        )
        .should_fail(status=500, code='500', message='Internal Server Error')
        .run(correction_save_fixtures)
    )


async def test_incorrect_ticket(correction_save_fixtures):
    await (
        helper.CorrectionSaveTest()
        .request(
            order_nr='123456-654322',
            login='anton-vorobev',
            amount='500.00',
            currency='RUB',
            ticket='incorrect',
            correction_type='product',
            correction_group='incorrect',
            product='eats_marketing_coupon',
            detailed_product='eats_marketing_coupon',
        )
        .should_fail(status=409, code='409', message='Недопустимый тикет')
        .run(correction_save_fixtures)
    )


@pytest.mark.parametrize(
    'amount, correction_type, correction_group, product, detailed_product',
    [
        pytest.param('500', 'product', 'payment', None, None),
        pytest.param('100', 'product', 'payment', None, None),
        pytest.param('200', 'product', 'payment', None, None),
        pytest.param('500', 'all_negative', 'all', None, None),
        pytest.param(
            '100',
            'commission_marketplace',
            'commission',
            'eats_order_commission_marketplace',
            'eats_order_commission_marketplace',
        ),
        pytest.param(
            '-200',
            'commission_marketplace',
            'commission',
            'eats_order_commission_marketplace',
            'eats_order_commission_marketplace',
        ),
        pytest.param(
            '250',
            'commission_marketplace',
            'commission',
            'eats_order_commission_marketplace',
            'eats_order_commission_marketplace',
        ),
    ],
)
async def test_incorrect_amount(
        correction_save_fixtures,
        amount,
        correction_type,
        correction_group,
        product,
        detailed_product,
):
    await (
        helper.CorrectionSaveTest()
        .request(
            order_nr='123456-654322',
            login='anton-vorobev',
            amount=amount,
            currency='RUB',
            ticket='FINRETAIL-1234',
            correction_type=correction_type,
            correction_group=correction_group,
            product=product,
            detailed_product=detailed_product,
        )
        .docs(
            docs=[
                helper.make_doc(
                    doc_id=1,
                    transaction={
                        'product': 'eats_marketing_coupon_employee',
                        'amount_with_vat': '200',
                        'currency': 'RUB',
                        'transaction_type': 'payment',
                        'payload': {'product': 'product'},
                        'detailed_product': 'eats_marketing_coupon_employee',
                    },
                ),
                helper.make_doc(
                    doc_id=2,
                    transaction={
                        'product': 'eats_order_commission_marketplace',
                        'amount_with_vat': '100',
                        'currency': 'RUB',
                        'transaction_type': 'payment',
                        'detailed_product': (
                            'eats_order_commission_marketplace'
                        ),
                    },
                ),
            ],
        )
        .should_fail(status=409, code='409', message='Недопустимая сумма')
        .run(correction_save_fixtures)
    )
