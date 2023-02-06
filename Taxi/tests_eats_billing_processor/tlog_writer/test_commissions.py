import pytest

from tests_eats_billing_processor.tlog_writer import helper


@pytest.mark.parametrize(
    'rule, product_type, commission_type,'
    'product, detailed_product, service_id',
    [
        pytest.param(
            'marketplace',
            'product',
            'goods',
            'eats_order_commission_marketplace',
            'eats_order_commission_marketplace',
            628,
            id='Commission marketplace',
        ),
        pytest.param(
            'restaurant',
            'product',
            'goods',
            'eats_order_commission_own_delivery',
            'eats_order_commission_own_delivery',
            628,
            id='Commission restaurant',
        ),
        pytest.param(
            'shop',
            'product',
            'goods',
            'eats_order_commission_own_delivery',
            'eats_order_commission_own_delivery',
            628,
            id='Commission shop',
        ),
        pytest.param(
            'pickup',
            'product',
            'pickup',
            'eats_order_commission_pickup',
            'eats_order_commission_pickup',
            628,
            id='Commission pickup',
        ),
        pytest.param(
            'retail',
            'retail',
            'retail',
            'eats_order_commission_retail',
            'eats_order_commission_retail',
            661,
            id='Commission retail',
        ),
        pytest.param(
            'restaurant',
            'product',
            'rest_expense_delivery',
            'eats_order_commission_own_delivery',
            'eats_delivery_commission_fee',
            628,
            id='Commission place compensations',
        ),
        pytest.param(
            'grocery',
            'product',
            'goods',
            'eats_order_commission_own_delivery',
            'eats_order_commission_own_delivery',
            628,
            id='Commission grocery product',
        ),
        pytest.param(
            'grocery',
            'delivery',
            'goods',
            'eats_order_commission_own_delivery',
            'eats_order_commission_own_delivery',
            628,
            id='Commission grocery delivery',
        ),
        pytest.param(
            'inplace',
            'product',
            'inplace',
            'eats_order_commission_inplace',
            'eats_order_commission_inplace',
            1177,
            id='Commission inplace',
        ),
        pytest.param(
            'marketplace',
            'product',
            'subscribe_gmv',
            'eats_commission_subscribe_fixed',
            'eats_commission_subscribe_fixed',
            628,
            id='Commission subscribe',
        ),
        pytest.param(
            'restaurant',
            'product',
            'subscribe_fixed',
            'eats_commission_subscribe_fixed',
            'eats_commission_subscribe_fixed',
            628,
            id='Commission fixed subscribe',
        ),
    ],
)
async def test_place_commission(
        tlog_writer_fixtures,
        rule,
        product_type,
        commission_type,
        product,
        detailed_product,
        service_id,
):
    await (
        helper.TlogWriterTest()
        .with_rule(rule)
        .on_billing_event(
            client=helper.client_info(
                client_id='12345',
                contract_id='55555',
                country_code='RU',
                mvp='br_moscow_adm',
            ),
            commission=helper.commission_data(
                product_type=product_type,
                amount='1200',
                currency='RUB',
                commission_type=commission_type,
            ),
        )
        .expect_payment(
            amount_with_vat='1200',
            vat_amount='200',
            amount_without_vat='1000',
            firm_id='32',
            product=product,
            detailed_product=detailed_product,
            service_id=service_id,
            ignore_in_balance=True,
        )
        .run(tlog_writer_fixtures)
    )


@pytest.mark.parametrize(
    'employment, product, detailed_product',
    [
        pytest.param(
            'courier_service',
            'eats_delivery_fee',
            'eats_delivery_fee_cs',
            id='Commission courier service delivery',
        ),
        pytest.param(
            'self_employed',
            'eats_delivery_fee',
            'eats_delivery_fee_smz',
            id='Commission self employed courier delivery',
        ),
    ],
)
async def test_courier_commission(
        tlog_writer_fixtures, employment, product, detailed_product,
):
    await (
        helper.TlogWriterTest()
        .with_rule('retail')
        .on_billing_event(
            client=helper.client_info(
                client_id='12345',
                contract_id='55555',
                country_code='RU',
                mvp='br_moscow_adm',
                employment=employment,
            ),
            commission=helper.commission_data(
                product_type='delivery', amount='1200', currency='RUB',
            ),
        )
        .expect_payment(
            amount_with_vat='1200',
            vat_amount='200',
            amount_without_vat='1000',
            firm_id='32',
            product=product,
            detailed_product=detailed_product,
            service_id=645,
            ignore_in_balance=True,
        )
        .run(tlog_writer_fixtures)
    )


async def test_picker_commission(tlog_writer_fixtures):
    await (
        helper.TlogWriterTest()
        .with_rule('retail')
        .on_billing_event(
            client=helper.client_info(
                client_id='12345',
                contract_id='55555',
                country_code='RU',
                mvp='br_moscow_adm',
                employment='courier_service',
            ),
            commission=helper.commission_data(
                product_type='assembly', amount='1200', currency='RUB',
            ),
        )
        .expect_payment(
            amount_with_vat='1200',
            vat_amount='200',
            amount_without_vat='1000',
            firm_id='32',
            product='eats_picker_fee',
            detailed_product='eats_picker_fee',
            service_id=699,
            ignore_in_balance=True,
        )
        .run(tlog_writer_fixtures)
    )


async def test_donation_commission(tlog_writer_fixtures):
    await (
        helper.TlogWriterTest()
        .with_rule('donation')
        .on_billing_event(
            client=helper.client_info(
                client_id='12345',
                contract_id='55555',
                country_code='RU',
                mvp='br_moscow_adm',
            ),
            commission=helper.commission_data(
                product_type='donation', amount='0.01', currency='RUB',
            ),
        )
        .expect_payment(
            amount_with_vat='0.01',
            vat_amount='0',
            amount_without_vat='0.01',
            firm_id='32',
            product='eats_donation_agent_reward',
            detailed_product='eats_donation_agent_reward',
            service_id=676,
            ignore_in_balance=True,
        )
        .run(tlog_writer_fixtures)
    )


@pytest.mark.parametrize(
    'rule, product, detailed_product, service_id',
    [
        pytest.param(
            'marketplace',
            'eats_cashback_payback',
            'eats_cashback_payback',
            628,
            id='Plus commission marketplace',
        ),
        pytest.param(
            'restaurant',
            'eats_cashback_payback',
            'eats_cashback_payback',
            628,
            id='Plus commission restaurant',
        ),
        pytest.param(
            'shop',
            'eats_cashback_payback',
            'eats_cashback_payback',
            628,
            id='Plus commission shop',
        ),
        pytest.param(
            'retail',
            'eats_cashback_payback_retail',
            'eats_cashback_payback_retail',
            661,
            id='Plus commission retail',
        ),
    ],
)
async def test_plus_commission(
        tlog_writer_fixtures, rule, product, detailed_product, service_id,
):
    await (
        helper.TlogWriterTest()
        .with_rule(rule)
        .on_billing_event(
            client=helper.client_info(
                client_id='12345',
                contract_id='55555',
                country_code='RU',
                mvp='MSKc',
            ),
            commission=helper.commission_data(
                product_type='delivery',
                amount='1200',
                currency='RUB',
                commission_type='plus_cashback',
            ),
        )
        .expect_payment(
            amount_with_vat='1200',
            vat_amount='200',
            amount_without_vat='1000',
            firm_id='32',
            product=product,
            detailed_product=detailed_product,
            service_id=service_id,
            ignore_in_balance=True,
        )
        .run(tlog_writer_fixtures)
    )


@pytest.mark.parametrize(
    'rule, product_type, product_id, product,'
    'detailed_product, service_id, payload',
    [
        pytest.param(
            'restaurant',
            'product',
            'goods',
            'eats_order_commission_own_delivery',
            'eats_order_commission_own_delivery',
            628,
            'product',
        ),
        pytest.param(
            'retail',
            'retail',
            'retail',
            'eats_order_commission_retail',
            'eats_order_commission_retail',
            661,
            'retail',
        ),
        pytest.param(
            'shop',
            'product',
            'markup_goods',
            'eats_order_markup_goods',
            'eats_order_markup_goods',
            628,
            'product',
        ),
        pytest.param(
            'marketplace',
            'product',
            'goods',
            'eats_order_commission_marketplace',
            'eats_order_commission_marketplace',
            628,
            'product',
        ),
    ],
)
@pytest.mark.pgsql(
    'eats_billing_processor',
    files=['test_order_accounting_correction_commission.sql'],
)
async def test_commission_accounting_correction(
        tlog_writer_fixtures,
        rule,
        product_type,
        product_id,
        product,
        detailed_product,
        service_id,
        payload,
):
    await (
        helper.TlogWriterTest()
        .with_rule(rule)
        .on_billing_event(
            client=helper.client_info(
                client_id='12345',
                contract_id='55555',
                country_code='RU',
                mvp='br_moscow_adm',
            ),
            commission=helper.commission_data(
                product_type=product_type,
                amount='1200',
                commission_type=product_id,
                currency='RUB',
            ),
            payload={'correction_id': '1'},
        )
        .expect_payment(
            amount_with_vat='1200',
            vat_amount='200',
            amount_without_vat='1000',
            firm_id='32',
            product=product,
            detailed_product=detailed_product,
            service_id=service_id,
            ignore_in_balance=True,
            payload={'product': payload},
        )
        .check_tlog_flag()
        .run(tlog_writer_fixtures)
    )
