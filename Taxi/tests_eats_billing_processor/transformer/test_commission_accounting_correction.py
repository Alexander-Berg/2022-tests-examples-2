import pytest

from tests_eats_billing_processor import rules
from tests_eats_billing_processor.transformer import common
from tests_eats_billing_processor.transformer import helper


@pytest.mark.parametrize(
    'product, detailed_product, billing_frequency,'
    'product_type, commission_type',
    [
        pytest.param(
            'eats_order_commission_marketplace',
            'eats_order_commission_marketplace',
            'daily',
            'product',
            'goods',
        ),
        pytest.param(
            'eats_order_commission_marketplace',
            'eats_order_commission_marketplace',
            'weekly',
            'product',
            'goods_weekly',
        ),
        pytest.param(
            'eats_order_commission_marketplace',
            'eats_order_commission_marketplace',
            None,
            'product',
            'goods',
        ),
        pytest.param(
            'eats_order_commission_own_delivery',
            'eats_order_commission_own_delivery',
            'daily',
            'product',
            'goods',
        ),
        pytest.param(
            'eats_order_commission_own_delivery',
            'eats_order_commission_own_delivery',
            'weekly',
            'product',
            'goods_weekly',
        ),
        pytest.param(
            'eats_order_commission_own_delivery',
            'eats_order_commission_own_delivery',
            None,
            'product',
            'goods',
        ),
        pytest.param(
            'eats_order_commission_pickup',
            'eats_order_commission_pickup',
            'daily',
            'product',
            'pickup',
        ),
        pytest.param(
            'eats_order_commission_pickup',
            'eats_order_commission_pickup',
            'weekly',
            'product',
            'pickup_weekly',
        ),
        pytest.param(
            'eats_order_commission_pickup',
            'eats_order_commission_pickup',
            None,
            'product',
            'pickup',
        ),
        pytest.param(
            'eats_cashback_payback',
            'eats_cashback_payback',
            'daily',
            'product',
            'plus_cashback',
        ),
        pytest.param(
            'eats_cashback_payback',
            'eats_cashback_payback',
            'weekly',
            'product',
            'plus_cashback_weekly',
        ),
        pytest.param(
            'eats_cashback_payback',
            'eats_cashback_payback',
            None,
            'product',
            'plus_cashback',
        ),
        pytest.param(
            'eats_order_commission_retail',
            'eats_order_commission_retail',
            'daily',
            'retail',
            'retail',
        ),
        pytest.param(
            'eats_order_commission_retail',
            'eats_order_commission_retail',
            'weekly',
            'retail',
            'retail',
        ),
        pytest.param(
            'eats_order_commission_retail',
            'eats_order_commission_retail',
            None,
            'retail',
            'retail',
        ),
        pytest.param(
            'eats_cashback_payback_retail',
            'eats_cashback_payback_retail',
            'daily',
            'retail',
            'plus_cashback',
        ),
        pytest.param(
            'eats_cashback_payback_retail',
            'eats_cashback_payback_retail',
            'weekly',
            'retail',
            'plus_cashback',
        ),
        pytest.param(
            'eats_cashback_payback_retail',
            'eats_cashback_payback_retail',
            None,
            'retail',
            'plus_cashback',
        ),
        pytest.param(
            'eats_commission_alco_booking',
            'eats_commission_alco_booking',
            'daily',
            'product',
            'alco_booking',
        ),
        pytest.param(
            'eats_commission_alco_booking',
            'eats_commission_alco_booking',
            'weekly',
            'product',
            'alco_booking_weekly',
        ),
        pytest.param(
            'eats_commission_alco_booking',
            'eats_commission_alco_booking',
            None,
            'product',
            'alco_booking',
        ),
        pytest.param(
            'eats_commission_subscribe_fixed',
            'eats_commission_subscribe_fixed',
            'daily',
            'product',
            'subscribe_fixed',
        ),
        pytest.param(
            'eats_commission_subscribe_fixed',
            'eats_commission_subscribe_fixed',
            'weekly',
            'product',
            'subscribe_fixed',
        ),
        pytest.param(
            'eats_commission_subscribe_fixed',
            'eats_commission_subscribe_fixed',
            None,
            'product',
            'subscribe_fixed',
        ),
        pytest.param(
            'eats_commission_subscribe_gmv',
            'eats_commission_subscribe_gmv',
            'daily',
            'product',
            'subscribe_gmv',
        ),
        pytest.param(
            'eats_commission_subscribe_gmv',
            'eats_commission_subscribe_gmv',
            'weekly',
            'product',
            'subscribe_gmv',
        ),
        pytest.param(
            'eats_commission_subscribe_gmv',
            'eats_commission_subscribe_gmv',
            None,
            'product',
            'subscribe_gmv',
        ),
        pytest.param(
            'eats_order_markup_pickup',
            'eats_order_markup_pickup',
            'daily',
            'product',
            'markup_pickup',
        ),
        pytest.param(
            'eats_order_markup_pickup',
            'eats_order_markup_pickup',
            'weekly',
            'product',
            'markup_pickup_weekly',
        ),
        pytest.param(
            'eats_order_markup_pickup',
            'eats_order_markup_pickup',
            None,
            'product',
            'markup_pickup',
        ),
        pytest.param(
            'eats_order_markup_goods',
            'eats_order_markup_goods',
            'daily',
            'product',
            'markup_goods',
        ),
        pytest.param(
            'eats_order_markup_goods',
            'eats_order_markup_goods',
            'weekly',
            'product',
            'markup_goods_weekly',
        ),
        pytest.param(
            'eats_order_markup_goods',
            'eats_order_markup_goods',
            None,
            'product',
            'markup_goods',
        ),
        pytest.param(
            'eats_delivery_commission_fee',
            'eats_delivery_commission_fee',
            'daily',
            'product',
            'rest_expense_delivery',
        ),
        pytest.param(
            'eats_delivery_commission_fee',
            'eats_delivery_commission_fee',
            'weekly',
            'product',
            'rest_expense_delivery_weekly',
        ),
        pytest.param(
            'eats_delivery_commission_fee',
            'eats_delivery_commission_fee',
            None,
            'product',
            'rest_expense_delivery',
        ),
        pytest.param(
            'eats_delivery_fee',
            'eats_delivery_fee_smz',
            'daily',
            'delivery',
            None,
        ),
        pytest.param(
            'eats_delivery_fee',
            'eats_delivery_fee_smz',
            'weekly',
            'delivery',
            None,
        ),
        pytest.param(
            'eats_delivery_fee',
            'eats_delivery_fee_smz',
            None,
            'delivery',
            None,
        ),
        pytest.param(
            'eats_delivery_fee',
            'eats_delivery_fee_cs',
            'daily',
            'delivery',
            None,
        ),
        pytest.param(
            'eats_delivery_fee',
            'eats_delivery_fee_cs',
            'weekly',
            'delivery',
            None,
        ),
        pytest.param(
            'eats_delivery_fee',
            'eats_delivery_fee_cs',
            None,
            'delivery',
            None,
        ),
        pytest.param(
            'eats_order_commission_inplace',
            'eats_order_commission_inplace',
            'daily',
            'product',
            'inplace',
        ),
        pytest.param(
            'eats_order_commission_inplace',
            'eats_order_commission_inplace',
            'weekly',
            'product',
            'inplace',
        ),
        pytest.param(
            'eats_order_commission_inplace',
            'eats_order_commission_inplace',
            None,
            'product',
            'inplace',
        ),
    ],
)
async def test_place_commission(
        transformer_fixtures,
        product,
        detailed_product,
        billing_frequency,
        product_type,
        commission_type,
):
    data = {
        'amount': '100',
        'correction_id': '12345',
        'currency': 'RUB',
        'detailed_product': detailed_product,
        'order_nr': '201217-305204',
        'originator': 'tariff_editor',
        'place_id': '123456',
        'product': product,
        'transaction_date': '2021-07-10T12:22:00',
    }
    await (
        helper.TransformerTest()
        .with_order_nr('201217-305204')
        .insert_input_event(kind='commission_accounting_correction', data=data)
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
                commission=common.make_commission(
                    product_type=product_type,
                    product_id='account_correction',
                    amount='100',
                    commission_type=commission_type,
                ),
                payload={'correction_id': '12345'},
            ),
        )
        .expect_stq_call_id(1)
        .run(transformer_fixtures)
    )


@pytest.mark.parametrize(
    'product, detailed_product, billing_frequency,'
    'product_type, commission_type',
    [
        pytest.param(
            'eats_order_commission_retail',
            'eats_order_commission_retail',
            'daily',
            'retail',
            'retail',
        ),
        pytest.param(
            'eats_order_commission_retail',
            'eats_order_commission_retail',
            'weekly',
            'retail',
            'retail',
        ),
        pytest.param(
            'eats_order_commission_retail',
            'eats_order_commission_retail',
            None,
            'retail',
            'retail',
        ),
        pytest.param(
            'eats_cashback_payback_retail',
            'eats_cashback_payback_retail',
            'daily',
            'retail',
            'plus_cashback',
        ),
        pytest.param(
            'eats_cashback_payback_retail',
            'eats_cashback_payback_retail',
            'weekly',
            'retail',
            'plus_cashback',
        ),
        pytest.param(
            'eats_cashback_payback_retail',
            'eats_cashback_payback_retail',
            None,
            'retail',
            'plus_cashback',
        ),
        pytest.param(
            'eats_picker_fee', 'eats_picker_fee', 'daily', 'assembly', None,
        ),
        pytest.param(
            'eats_picker_fee', 'eats_picker_fee', 'weekly', 'assembly', None,
        ),
        pytest.param(
            'eats_picker_fee', 'eats_picker_fee', None, 'assembly', None,
        ),
    ],
)
async def test_picker_commission(
        transformer_fixtures,
        product,
        detailed_product,
        billing_frequency,
        product_type,
        commission_type,
):
    data = {
        'amount': '100',
        'correction_id': '12345',
        'currency': 'RUB',
        'detailed_product': detailed_product,
        'order_nr': '201217-305204',
        'originator': 'tariff_editor',
        'picker_id': '123456',
        'product': product,
        'transaction_date': '2021-07-10T12:22:00',
    }
    await (
        helper.TransformerTest()
        .with_order_nr('201217-305204')
        .insert_input_event(kind='commission_accounting_correction', data=data)
        .using_business_rules(
            picker_id='123456',
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
                commission=common.make_commission(
                    product_type=product_type,
                    product_id='account_correction',
                    amount='100',
                    commission_type=commission_type,
                ),
                payload={'correction_id': '12345'},
            ),
        )
        .expect_stq_call_id(1)
        .run(transformer_fixtures)
    )


@pytest.mark.parametrize(
    'detailed_product, billing_frequency',
    [
        pytest.param('eats_delivery_fee_smz', 'daily'),
        pytest.param('eats_delivery_fee_smz', 'weekly'),
        pytest.param('eats_delivery_fee_smz', None),
        pytest.param('eats_delivery_fee_cs', 'daily'),
        pytest.param('eats_delivery_fee_cs', 'weekly'),
        pytest.param('eats_delivery_fee_cs', None),
    ],
)
async def test_courier_commission(
        transformer_fixtures, detailed_product, billing_frequency,
):
    data = {
        'amount': '100',
        'correction_id': '12345',
        'currency': 'RUB',
        'detailed_product': detailed_product,
        'order_nr': '201217-305204',
        'originator': 'tariff_editor',
        'courier_id': '123456',
        'product': 'eats_delivery_fee',
        'transaction_date': '2021-07-10T12:22:00',
    }
    await (
        helper.TransformerTest()
        .with_order_nr('201217-305204')
        .insert_input_event(kind='commission_accounting_correction', data=data)
        .using_business_rules(
            courier_id='123456',
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
                commission=common.make_commission(
                    product_type='delivery',
                    product_id='account_correction',
                    amount='100',
                ),
                payload={'correction_id': '12345'},
            ),
        )
        .expect_stq_call_id(1)
        .run(transformer_fixtures)
    )


@pytest.mark.parametrize(
    'billing_frequency',
    [pytest.param('daily'), pytest.param('weekly'), pytest.param(None)],
)
async def test_donation(transformer_fixtures, billing_frequency):
    data = {
        'amount': '100',
        'correction_id': '12345',
        'currency': 'RUB',
        'detailed_product': 'eats_donation_agent_reward',
        'order_nr': '201217-305204',
        'originator': 'tariff_editor',
        'place_id': '123456',
        'product': 'eats_donation_agent_reward',
        'transaction_date': '2021-07-10T12:22:00',
    }
    await (
        helper.TransformerTest()
        .with_order_nr('201217-305204')
        .insert_input_event(kind='commission_accounting_correction', data=data)
        .using_business_rules(
            place_id=common.DONATION_CLIENT_ID,
            client_info=rules.client_info(
                client_id=common.DONATION_CLIENT_ID,
                contract_id=common.DONATION_CONTRACT_ID,
                mvp='MSKc',
            ),
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
                client_info=rules.client_info(
                    client_id=common.DONATION_CLIENT_ID,
                    contract_id=common.DONATION_CONTRACT_ID,
                    mvp='MSKc',
                ),
                commission=common.make_commission(
                    product_type='donation',
                    product_id='account_correction',
                    amount='100',
                ),
                payload={'correction_id': '12345'},
            ),
        )
        .expect_stq_call_id(1)
        .run(transformer_fixtures)
    )


@pytest.mark.parametrize(
    'billing_frequency, currency, client_id, contract_id, mvp',
    [
        pytest.param(
            'daily',
            'RUB',
            common.SERVICE_FEE_CLIENT_ID_RUB,
            common.SERVICE_FEE_CONTRACT_ID_RUB,
            'MSKc',
        ),
        pytest.param(
            'weekly',
            'RUB',
            common.SERVICE_FEE_CLIENT_ID_RUB,
            common.SERVICE_FEE_CONTRACT_ID_RUB,
            'MSKc',
        ),
        pytest.param(
            None,
            'RUB',
            common.SERVICE_FEE_CLIENT_ID_RUB,
            common.SERVICE_FEE_CONTRACT_ID_RUB,
            'MSKc',
        ),
        pytest.param(
            'daily',
            'BYN',
            common.SERVICE_FEE_CLIENT_ID_BYN,
            common.SERVICE_FEE_CONTRACT_ID_BYN,
            'MNKc',
        ),
        pytest.param(
            'weekly',
            'BYN',
            common.SERVICE_FEE_CLIENT_ID_BYN,
            common.SERVICE_FEE_CONTRACT_ID_BYN,
            'MNKc',
        ),
        pytest.param(
            None,
            'BYN',
            common.SERVICE_FEE_CLIENT_ID_BYN,
            common.SERVICE_FEE_CONTRACT_ID_BYN,
            'MNKc',
        ),
        pytest.param(
            'daily',
            'KZT',
            common.SERVICE_FEE_CLIENT_ID_KZT,
            common.SERVICE_FEE_CONTRACT_ID_KZT,
            'AST',
        ),
        pytest.param(
            'weekly',
            'KZT',
            common.SERVICE_FEE_CLIENT_ID_KZT,
            common.SERVICE_FEE_CONTRACT_ID_KZT,
            'AST',
        ),
        pytest.param(
            None,
            'KZT',
            common.SERVICE_FEE_CLIENT_ID_KZT,
            common.SERVICE_FEE_CONTRACT_ID_KZT,
            'AST',
        ),
    ],
)
async def test_service_fee(
        transformer_fixtures,
        billing_frequency,
        currency,
        client_id,
        contract_id,
        mvp,
):
    data = {
        'amount': '100',
        'correction_id': '12345',
        'currency': currency,
        'detailed_product': 'eats_client_service_fee',
        'order_nr': '201217-305204',
        'originator': 'tariff_editor',
        'place_id': '123456',
        'product': 'eats_client_service_fee',
        'transaction_date': '2021-07-10T12:22:00',
    }
    await (
        helper.TransformerTest()
        .with_order_nr('201217-305204')
        .insert_input_event(kind='commission_accounting_correction', data=data)
        .using_business_rules(
            place_id='123456',
            client_info=rules.client_info(
                client_id=client_id, contract_id=contract_id, mvp=mvp,
            ),
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
                client_info=rules.client_info(
                    client_id=client_id, contract_id=contract_id, mvp=mvp,
                ),
                commission=common.make_commission(
                    product_type='service_fee',
                    product_id='account_correction',
                    amount='100',
                    commission_type='service_fee',
                    currency=currency,
                ),
                payload={'correction_id': '12345'},
            ),
        )
        .expect_stq_call_id(1)
        .run(transformer_fixtures)
    )
