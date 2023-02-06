import pytest

from tests_eats_billing_processor.tlog_writer import helper


@pytest.mark.parametrize(
    'rule, product_type, service_id',
    [
        pytest.param('restaurant', 'product', 629, id='Pay for product'),
        pytest.param('restaurant', 'delivery', 645, id='Pay for delivery'),
        pytest.param('retail', 'retail', 699, id='Pay for retail'),
        pytest.param('retail', 'assembly', 699, id='Pay for assembly'),
        pytest.param('donation', 'donation', 676, id='Pay for donation'),
        pytest.param('inplace', 'product', 1176, id='Inplace payment'),
    ],
)
async def test_card_payments(
        tlog_writer_fixtures, rule, product_type, service_id,
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
            payment=helper.payment_data(
                product_type=product_type,
                amount='150',
                currency='RUB',
                payment_method='card',
                payment_terminal_id='222333',
            ),
        )
        .expect_payment(
            amount='150',
            terminal_id=222333,
            paysys_type='alfa-bank',
            firm_id='32',
            product='eats_payment',
            detailed_product='eats_payment',
            service_id=service_id,
            ignore_in_balance=True,
        )
        .run(tlog_writer_fixtures)
    )


@pytest.mark.parametrize(
    'rule, product_type, service_id, product',
    [
        pytest.param(
            'restaurant',
            'tips',
            645,
            'eats_courier_tips',
            id='Pay for tips restaurant order',
        ),
        pytest.param(
            'shop',
            'tips',
            645,
            'eats_courier_tips',
            id='Pay for tips shop order',
        ),
        pytest.param(
            'retail',
            'tips',
            645,
            'eats_courier_tips',
            id='Pay for tips retail order',
        ),
        pytest.param(
            'restaurant',
            'restaurant_tips',
            629,
            'eats_restaurant_tips',
            id='Pay for restaurant tips',
        ),
    ],
)
async def test_tips(
        tlog_writer_fixtures, rule, product_type, service_id, product,
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
            payment=helper.payment_data(
                product_type=product_type,
                amount='150',
                currency='RUB',
                payment_method='eda_tips',
                payment_terminal_id='222333',
            ),
        )
        .expect_payment(
            amount='150',
            terminal_id=222333,
            paysys_type='payture',
            firm_id='32',
            product=product,
            detailed_product=product,
            service_id=service_id,
            ignore_in_balance=True,
        )
        .run(tlog_writer_fixtures)
    )


@pytest.mark.parametrize(
    'rule, product_type, service_id, product',
    [
        pytest.param(
            'restaurant',
            'product',
            629,
            'eats_badge_corporate',
            id='Pay for product',
        ),
        pytest.param(
            'restaurant',
            'delivery',
            645,
            'eats_badge_corporate',
            id='Pay for delivery',
        ),
        pytest.param(
            'retail',
            'retail',
            699,
            'eats_badge_corporate',
            id='Pay for retail',
        ),
        pytest.param(
            'retail',
            'assembly',
            699,
            'eats_picker_badge',
            id='Pay for assembly',
        ),
    ],
)
async def test_badge_payments(
        tlog_writer_fixtures, rule, product_type, service_id, product,
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
            payment=helper.payment_data(
                product_type=product_type,
                amount='150',
                currency='RUB',
                payment_method='badge_corporate',
            ),
        )
        .expect_payment(
            amount='150',
            paysys_type='yaeda',
            firm_id='32',
            product=product,
            detailed_product=product,
            service_id=service_id,
            ignore_in_balance=True,
        )
        .run(tlog_writer_fixtures)
    )


@pytest.mark.parametrize(
    'rule, payment_method, product, detailed_product',
    [
        pytest.param(
            'restaurant',
            'yandex_account_topup',
            'eats_yandex_account_topup',
            'eats_yandex_account_topup',
            id='yandex_account_topup',
        ),
        pytest.param(
            'retail',
            'yandex_account_withdraw',
            'eats_yandex_account_withdraw',
            'eats_yandex_account_withdraw',
            id='yandex_account_withdraw',
        ),
    ],
)
async def test_yandex_account(
        tlog_writer_fixtures, rule, payment_method, product, detailed_product,
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
            payment=helper.payment_data(
                product_type='delivery',
                amount='150',
                currency='RUB',
                payment_method=payment_method,
                product_id='plus_cashback',
            ),
        )
        .expect_payment(
            amount='150',
            paysys_type='yaeda',
            firm_id='32',
            product=product,
            detailed_product=detailed_product,
            service_id=645,
            ignore_in_balance=True,
        )
        .run(tlog_writer_fixtures)
    )
