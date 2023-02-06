import pytest

from tests_eats_billing_processor.correction_info import helper


async def test_happy_path_commission(correction_info_fixtures):
    await (
        helper.CorrectionInfoTest()
        .request('123456-654322')
        .response(
            amounts=[
                {
                    'name': 'Доставка ресторана',
                    'amount': '10',
                    'currency': 'RUB',
                    'correction_group': 'commission',
                    'correction_type': 'commission_marketplace',
                    'product': 'eats_order_commission_marketplace',
                    'detailed_product': 'eats_order_commission_marketplace',
                    'read_only': False,
                },
                {
                    'name': 'Своя доставка',
                    'amount': '200',
                    'currency': 'RUB',
                    'correction_group': 'commission',
                    'correction_type': 'commission_own_delivery',
                    'product': 'eats_order_commission_own_delivery',
                    'detailed_product': 'eats_order_commission_own_delivery',
                    'read_only': False,
                },
                {
                    'name': 'Самовывоз',
                    'amount': '300',
                    'currency': 'RUB',
                    'correction_group': 'commission',
                    'correction_type': 'commission_pickup',
                    'product': 'eats_order_commission_pickup',
                    'detailed_product': 'eats_order_commission_pickup',
                    'read_only': False,
                },
                {
                    'name': 'Наша сборка',
                    'amount': '400',
                    'currency': 'RUB',
                    'correction_group': 'commission',
                    'correction_type': 'commission_retail',
                    'product': 'eats_order_commission_retail',
                    'detailed_product': 'eats_order_commission_retail',
                    'read_only': False,
                },
                {
                    'name': 'Баллы плюса (ресторан)',
                    'amount': '500',
                    'currency': 'KZT',
                    'correction_group': 'commission',
                    'correction_type': 'cashback_payback',
                    'product': 'eats_cashback_payback',
                    'detailed_product': 'eats_cashback_payback',
                    'read_only': False,
                },
                {
                    'name': 'Баллы плюса (магазин)',
                    'amount': '600',
                    'currency': 'BYN',
                    'correction_group': 'commission',
                    'correction_type': 'cashback_payback_retail',
                    'product': 'eats_cashback_payback_retail',
                    'detailed_product': 'eats_cashback_payback_retail',
                    'read_only': False,
                },
            ],
            table_format=[
                helper.column_format(
                    column_name='correction_id',
                    column_number=1,
                    title='correction_id',
                ),
                helper.column_format(
                    column_name='Тип',
                    column_number=2,
                    title='correction_group',
                ),
            ],
            corrections=[],
            docs=[
                helper.make_doc(
                    doc_id=1,
                    transaction={
                        'product': 'eats_order_commission_marketplace',
                        'amount_with_vat': '100',
                        'transaction_type': 'payment',
                        'currency': 'RUB',
                        'detailed_product': (
                            'eats_order_commission_marketplace'
                        ),
                    },
                ),
                helper.make_doc(
                    doc_id=12,
                    transaction={
                        'product': 'eats_order_commission_marketplace',
                        'amount_with_vat': '90',
                        'transaction_type': 'refund',
                        'currency': 'RUB',
                        'detailed_product': (
                            'eats_order_commission_marketplace'
                        ),
                    },
                ),
                helper.make_doc(
                    doc_id=2,
                    transaction={
                        'product': 'eats_order_commission_own_delivery',
                        'amount_with_vat': '200',
                        'transaction_type': 'payment',
                        'currency': 'RUB',
                        'detailed_product': (
                            'eats_order_commission_own_delivery'
                        ),
                    },
                ),
                helper.make_doc(
                    doc_id=3,
                    transaction={
                        'product': 'eats_order_commission_pickup',
                        'amount_with_vat': '300',
                        'transaction_type': 'payment',
                        'currency': 'RUB',
                        'detailed_product': 'eats_order_commission_pickup',
                    },
                ),
                helper.make_doc(
                    doc_id=4,
                    transaction={
                        'product': 'eats_order_commission_retail',
                        'amount_with_vat': '400',
                        'transaction_type': 'payment',
                        'currency': 'RUB',
                        'detailed_product': 'eats_order_commission_retail',
                    },
                ),
                helper.make_doc(
                    doc_id=5,
                    transaction={
                        'product': 'eats_cashback_payback',
                        'amount_with_vat': '500',
                        'transaction_type': 'payment',
                        'currency': 'KZT',
                        'detailed_product': 'eats_cashback_payback',
                    },
                ),
                helper.make_doc(
                    doc_id=6,
                    transaction={
                        'product': 'eats_cashback_payback_retail',
                        'amount_with_vat': '600',
                        'transaction_type': 'payment',
                        'currency': 'BYN',
                        'detailed_product': 'eats_cashback_payback_retail',
                    },
                ),
            ],
        )
        .run(correction_info_fixtures)
    )


async def test_happy_path_payments(correction_info_fixtures):
    await (
        helper.CorrectionInfoTest()
        .request('123456-654322')
        .response(
            amounts=[
                {
                    'name': 'Стоимость блюд',
                    'amount': '2050',
                    'currency': 'RUB',
                    'correction_group': 'payment',
                    'correction_type': 'product',
                    'read_only': False,
                },
                {
                    'name': 'Стоимость товаров',
                    'amount': '200',
                    'currency': 'RUB',
                    'correction_group': 'payment',
                    'correction_type': 'retail',
                    'read_only': False,
                },
                {
                    'name': 'Стоимость доставки',
                    'amount': '100',
                    'currency': 'RUB',
                    'correction_group': 'payment',
                    'correction_type': 'delivery',
                    'read_only': False,
                },
            ],
            table_format=[
                helper.column_format(
                    column_name='correction_id',
                    column_number=1,
                    title='correction_id',
                ),
                helper.column_format(
                    column_name='Тип',
                    column_number=2,
                    title='correction_group',
                ),
            ],
            corrections=[],
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
                        'product': 'eats_marketing_coupon',
                        'amount_with_vat': '50',
                        'currency': 'RUB',
                        'transaction_type': 'refund',
                        'payload': {'product': 'product'},
                        'detailed_product': 'eats_marketing_promotion',
                    },
                ),
                helper.make_doc(
                    doc_id=2,
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
                    doc_id=3,
                    transaction={
                        'product': 'eats_support_coupon',
                        'amount_with_vat': '300',
                        'currency': 'RUB',
                        'transaction_type': 'payment',
                        'payload': {'product': 'product'},
                        'detailed_product': 'eats_support_coupon',
                    },
                ),
                helper.make_doc(
                    doc_id=4,
                    transaction={
                        'product': 'eats_b2b_coupon',
                        'amount_with_vat': '400',
                        'currency': 'RUB',
                        'transaction_type': 'payment',
                        'payload': {'product': 'product'},
                        'detailed_product': 'eats_b2b_coupon_corporate',
                    },
                ),
                helper.make_doc(
                    doc_id=5,
                    transaction={
                        'product': 'eats_b2b_coupon_picker',
                        'amount_with_vat': '500',
                        'currency': 'RUB',
                        'transaction_type': 'payment',
                        'payload': {'product': 'product'},
                        'detailed_product': 'eats_b2b_coupon_picker',
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
                        'amount_with_vat': '100',
                        'currency': 'RUB',
                        'transaction_type': 'payment',
                        'payload': {'product': 'delivery'},
                        'detailed_product': 'eats_marketing_promotion',
                    },
                ),
                helper.make_doc(
                    doc_id=8,
                    transaction={
                        'product': 'eats_marketing_coupon',
                        'amount_with_vat': '100',
                        'currency': 'RUB',
                        'transaction_type': 'payment',
                        'payload': {'product': 'retail'},
                        'detailed_product': 'eats_marketing_promotion',
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
        .run(correction_info_fixtures)
    )


async def test_happy_path_all_negative(correction_info_fixtures):
    await (
        helper.CorrectionInfoTest()
        .request('123456-654322')
        .response(
            amounts=[
                {
                    'name': 'Стоимость блюд',
                    'amount': '2050',
                    'currency': 'RUB',
                    'correction_group': 'payment',
                    'correction_type': 'product',
                    'read_only': False,
                },
                {
                    'name': 'Стоимость товаров',
                    'amount': '100',
                    'currency': 'RUB',
                    'correction_group': 'payment',
                    'correction_type': 'retail',
                    'read_only': False,
                },
                {
                    'name': 'Стоимость доставки',
                    'amount': '100',
                    'currency': 'RUB',
                    'correction_group': 'payment',
                    'correction_type': 'delivery',
                    'read_only': False,
                },
                {
                    'name': 'Отрицательная',
                    'amount': '2250',
                    'currency': 'RUB',
                    'correction_group': 'all',
                    'correction_type': 'all_negative',
                    'read_only': False,
                },
            ],
            table_format=[
                helper.column_format(
                    column_name='correction_id',
                    column_number=1,
                    title='correction_id',
                ),
                helper.column_format(
                    column_name='Тип',
                    column_number=2,
                    title='correction_group',
                ),
            ],
            corrections=[],
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
                        'product': 'eats_marketing_coupon',
                        'amount_with_vat': '50',
                        'currency': 'RUB',
                        'transaction_type': 'refund',
                        'payload': {'product': 'product'},
                        'detailed_product': 'eats_marketing_promotion',
                    },
                ),
                helper.make_doc(
                    doc_id=2,
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
                    doc_id=3,
                    transaction={
                        'product': 'eats_support_coupon',
                        'amount_with_vat': '300',
                        'currency': 'RUB',
                        'transaction_type': 'payment',
                        'payload': {'product': 'product'},
                        'detailed_product': 'eats_support_coupon',
                    },
                ),
                helper.make_doc(
                    doc_id=4,
                    transaction={
                        'product': 'eats_b2b_coupon',
                        'amount_with_vat': '400',
                        'currency': 'RUB',
                        'transaction_type': 'payment',
                        'payload': {'product': 'product'},
                        'detailed_product': 'eats_b2b_coupon_corporate',
                    },
                ),
                helper.make_doc(
                    doc_id=5,
                    transaction={
                        'product': 'eats_b2b_coupon_picker',
                        'amount_with_vat': '500',
                        'currency': 'RUB',
                        'transaction_type': 'payment',
                        'payload': {'product': 'product'},
                        'detailed_product': 'eats_b2b_coupon_picker',
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
                        'amount_with_vat': '100',
                        'currency': 'RUB',
                        'transaction_type': 'payment',
                        'payload': {'product': 'delivery'},
                        'detailed_product': 'eats_marketing_promotion',
                    },
                ),
                helper.make_doc(
                    doc_id=8,
                    transaction={
                        'product': 'eats_marketing_coupon',
                        'amount_with_vat': '100',
                        'currency': 'RUB',
                        'transaction_type': 'payment',
                        'payload': {'product': 'retail'},
                        'detailed_product': 'eats_marketing_promotion',
                    },
                ),
                helper.make_doc(
                    doc_id=9,
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
                    doc_id=10,
                    transaction={
                        'product': 'eats_badge_corporate',
                        'amount_with_vat': '100',
                        'currency': 'RUB',
                        'transaction_type': 'refund',
                        'payload': {'product': 'retail'},
                        'detailed_product': 'eats_badge_corporate',
                    },
                ),
                helper.make_doc(
                    doc_id=11,
                    transaction={
                        'product': 'eats_payment',
                        'amount_with_vat': '100',
                        'currency': 'RUB',
                        'transaction_type': 'payment',
                        'payload': {'product': 'retail'},
                        'detailed_product': 'eats_payment',
                    },
                ),
                helper.make_doc(
                    doc_id=12,
                    transaction={
                        'product': 'eats_payment',
                        'amount_with_vat': '100',
                        'currency': 'RUB',
                        'transaction_type': 'refund',
                        'payload': {'product': 'retail'},
                        'detailed_product': 'eats_payment',
                    },
                ),
                helper.make_doc(
                    doc_id=13,
                    transaction={
                        'product': 'eats_picker_badge',
                        'amount_with_vat': '100',
                        'currency': 'RUB',
                        'transaction_type': 'payment',
                        'payload': {'product': 'retail'},
                        'detailed_product': 'eats_picker_badge',
                    },
                ),
                helper.make_doc(
                    doc_id=14,
                    transaction={
                        'product': 'eats_picker_badge',
                        'amount_with_vat': '100',
                        'currency': 'RUB',
                        'transaction_type': 'refund',
                        'payload': {'product': 'retail'},
                        'detailed_product': 'eats_picker_badge',
                    },
                ),
            ],
        )
        .run(correction_info_fixtures)
    )


@pytest.mark.pgsql('eats_billing_processor', files=['test_corrections.sql'])
async def test_happy_path_transactions(correction_info_fixtures):
    await (
        helper.CorrectionInfoTest()
        .request('123456-654322')
        .response(
            amounts=[
                {
                    'name': 'Стоимость блюд',
                    'amount': '100',
                    'currency': 'RUB',
                    'correction_group': 'payment',
                    'correction_type': 'product',
                    'read_only': False,
                },
                {
                    'name': 'Доставка ресторана',
                    'amount': '100',
                    'currency': 'RUB',
                    'correction_group': 'commission',
                    'correction_type': 'commission_marketplace',
                    'product': 'eats_order_commission_marketplace',
                    'detailed_product': 'eats_order_commission_marketplace',
                    'read_only': True,
                },
                {
                    'name': 'Отрицательная',
                    'amount': '100',
                    'currency': 'RUB',
                    'correction_group': 'all',
                    'correction_type': 'all_negative',
                    'read_only': False,
                },
            ],
            table_format=[
                helper.column_format(
                    column_name='correction_id',
                    column_number=1,
                    title='correction_id',
                ),
                helper.column_format(
                    column_name='Тип',
                    column_number=2,
                    title='correction_group',
                ),
            ],
            corrections=[
                {
                    'amount': '20',
                    'currency': 'RUB',
                    'ticket': 'ticket',
                    'login': 'aklevosh',
                    'correction_type': 'Блюда',
                    'correction_group': 'Платеж',
                    'correction_id': 1,
                    'created_at': '2022-03-30T21:00:00+00:00',
                    'make_tlog': True,
                },
                {
                    'amount': '20',
                    'currency': 'RUB',
                    'login': 'aklevosh',
                    'ticket': 'ticket',
                    'correction_type': 'Доставка ресторана',
                    'correction_group': 'Комиссия',
                    'product': 'eats_order_commission_marketplace',
                    'detailed_product': 'eats_order_commission_marketplace',
                    'correction_id': 2,
                    'created_at': '2022-03-30T21:00:00+00:00',
                    'make_tlog': False,
                },
            ],
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
                    doc_id=2,
                    transaction={
                        'product': 'eats_order_commission_marketplace',
                        'amount_with_vat': '100',
                        'transaction_type': 'payment',
                        'currency': 'RUB',
                        'detailed_product': (
                            'eats_order_commission_marketplace'
                        ),
                    },
                ),
            ],
        )
        .run(correction_info_fixtures)
    )


async def test_fail(correction_info_fixtures):
    await (
        helper.CorrectionInfoTest()
        .request('123456-654321')
        .expect_fail()
        .run(correction_info_fixtures)
    )
