import pytest

from tests_eats_billing_processor.tlog_writer import helper


@pytest.mark.parametrize(
    'rule',
    [
        pytest.param('restaurant'),
        pytest.param('marketplace'),
        pytest.param('pickup'),
        pytest.param('shop'),
        pytest.param('shop_marketplace'),
    ],
)
async def test_fine(tlog_writer_fixtures, rule):
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
            payment=helper.payment_data(
                product_type='delivery',
                amount='1200',
                currency='RUB',
                payment_method='withholding',
                payment_service='yaeda',
            ),
        )
        .expect_payment(
            amount_with_vat='1200',
            vat_amount='200',
            amount_without_vat='1000',
            firm_id='32',
            product='eats_fine_restaurant',
            detailed_product='eats_fine_restaurant',
            service_id=629,
            ignore_in_balance=True,
        )
        .run(tlog_writer_fixtures)
    )


@pytest.mark.parametrize(
    'rule',
    [
        pytest.param('restaurant'),
        pytest.param('marketplace'),
        pytest.param('pickup'),
        pytest.param('shop'),
        pytest.param('shop_marketplace'),
    ],
)
async def test_fine_appeal(tlog_writer_fixtures, rule):
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
            payment=helper.payment_data(
                product_type='delivery',
                amount='1200',
                currency='RUB',
                payment_method='withholding_correct',
                payment_service='yaeda',
            ),
        )
        .expect_payment(
            amount_with_vat='1200',
            vat_amount='200',
            amount_without_vat='1000',
            firm_id='32',
            product='eats_fine_restaurant_correction',
            detailed_product='eats_fine_restaurant_correction',
            service_id=629,
            ignore_in_balance=True,
        )
        .run(tlog_writer_fixtures)
    )
