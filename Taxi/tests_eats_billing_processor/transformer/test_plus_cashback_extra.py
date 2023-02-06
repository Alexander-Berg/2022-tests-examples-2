# pylint: disable=C5521
from tests_eats_billing_processor import rules
from tests_eats_billing_processor.transformer import common
from tests_eats_billing_processor.transformer.helper import PLUS_CLIENT_ID
from tests_eats_billing_processor.transformer.retail import helper


async def test_payment_update_plus_cashback_products(transformer_fixtures):
    await (
        helper.TransformerRetailTest()
        .on_payment_update_plus_cashback(
            client_id='89012',
            amount='100',
            payment_method='card',
            product_type='product',
            product_id='plus_cashback',
            currency='RUB',
        )
        .using_business_rules(
            place_id='1',
            client_info=rules.client_info(client_id='89012'),
            commission=rules.make_commission(
                commission_type='place_delivery',
                params=rules.simple_commission(
                    commission='10',
                    acquiring_commission='0',
                    fix_commission='10',
                ),
            ),
        )
        .expect(
            common.billing_event(
                client_id='89012',
                payment=common.payment(
                    payment_method='card',
                    product_type='product',
                    amount='100',
                    payment_service='yaeda',
                    product_id='plus_cashback',
                ),
            ),
            common.billing_event(
                client_id=PLUS_CLIENT_ID,
                contract_id='1',
                payload={
                    'product_type': 'product',
                    'amount': '100',
                    'cashback_service': 'eda',
                    'has_plus': 'true',
                    'order_id': '123456',
                    'service_id': '645',
                    'country_code': 'RU',
                },
                payment=common.payment(
                    payment_method='yandex_account_withdraw',
                    product_type='delivery',
                    product_id='plus_cashback',
                    amount='100',
                    payment_service='yaeda',
                ),
            ),
        )
        .run(transformer_fixtures)
    )


async def test_payment_update_plus_cashback_delivery(transformer_fixtures):
    await (
        helper.TransformerRetailTest()
        .on_payment_update_plus_cashback(
            client_id='34567',
            amount='101',
            payment_method='card',
            product_type='delivery',
            product_id='plus_cashback',
            currency='RUB',
            counteragent_id='9',
        )
        .expect(
            common.billing_event(
                client_id=PLUS_CLIENT_ID,
                contract_id='1',
                payload={
                    'product_type': 'delivery',
                    'amount': '101',
                    'cashback_service': 'eda',
                    'has_plus': 'true',
                    'order_id': '123456',
                    'service_id': '645',
                    'country_code': 'RU',
                    'issuer': 'marketing',
                    'ticket': 'NEWSERVICE-1430',
                    'cashback_type': 'withdraw',
                    'campaign_name': 'OD delivery',
                },
                payment=common.payment(
                    payment_method='yandex_account_withdraw',
                    product_type='delivery',
                    product_id='plus_cashback',
                    amount='101',
                    payment_service='yaeda',
                ),
            ),
        )
        .run(transformer_fixtures)
    )


async def test_payment_update_plus_cashback_service_fee(transformer_fixtures):
    await (
        helper.TransformerRetailTest()
        .on_payment_update_plus_cashback(
            client_id='45678',
            amount='102',
            payment_method='card',
            product_type='service_fee',
            product_id='plus_cashback',
            currency='RUB',
            counteragent_id='7',
        )
        .expect(
            common.billing_event(
                client_id=PLUS_CLIENT_ID,
                contract_id='1',
                payload={
                    'product_type': 'service_fee',
                    'amount': '102',
                    'cashback_service': 'eda',
                    'has_plus': 'true',
                    'order_id': '123456',
                    'service_id': '645',
                    'country_code': 'RU',
                    'issuer': 'marketing',
                    'ticket': 'NEWSERVICE-1430',
                    'cashback_type': 'withdraw',
                    'campaign_name': 'OD service_fee',
                },
                payment=common.payment(
                    payment_method='yandex_account_withdraw',
                    product_type='service_fee',
                    product_id='plus_cashback',
                    amount='102',
                    payment_service='yaeda',
                ),
            ),
        )
        .run(transformer_fixtures)
    )


async def test_payment_update_plus_cashback_together(transformer_fixtures):
    await (
        helper.TransformerRetailTest()
        .on_payment_update_plus_cashback(
            client_id='89012',
            amount='100',
            payment_method='card',
            product_type='product',
            product_id='plus_cashback',
            currency='RUB',
        )
        .using_business_rules(
            place_id='1',
            client_info=rules.client_info(client_id='89012'),
            commission=rules.make_commission(
                commission_type='place_delivery',
                params=rules.simple_commission(
                    commission='10',
                    acquiring_commission='0',
                    fix_commission='10',
                ),
            ),
        )
        .expect(
            common.billing_event(
                client_id='89012',
                payment=common.payment(
                    payment_method='card',
                    product_type='product',
                    amount='100',
                    payment_service='yaeda',
                    product_id='plus_cashback',
                ),
            ),
            common.billing_event(
                client_id=PLUS_CLIENT_ID,
                contract_id='1',
                payload={
                    'product_type': 'product',
                    'amount': '100',
                    'cashback_service': 'eda',
                    'has_plus': 'true',
                    'order_id': '123456',
                    'service_id': '645',
                    'country_code': 'RU',
                },
                payment=common.payment(
                    payment_method='yandex_account_withdraw',
                    product_type='delivery',
                    product_id='plus_cashback',
                    amount='100',
                    payment_service='yaeda',
                ),
            ),
        )
        .run(transformer_fixtures)
    )

    await (
        helper.TransformerRetailTest()
        .on_payment_update_plus_cashback(
            client_id='34567',
            amount='101',
            payment_method='card',
            product_type='delivery',
            product_id='plus_cashback',
            currency='RUB',
            counteragent_id='9',
        )
        .expect_stq_call_id(2)
        .expect(
            common.billing_event(
                client_id='89012',
                payment=common.payment(
                    payment_method='card',
                    product_type='product',
                    amount='100',
                    payment_service='yaeda',
                    product_id='plus_cashback',
                ),
            ),
            common.billing_event(
                client_id=PLUS_CLIENT_ID,
                contract_id='1',
                payload={
                    'product_type': 'product',
                    'amount': '100',
                    'cashback_service': 'eda',
                    'has_plus': 'true',
                    'order_id': '123456',
                    'service_id': '645',
                    'country_code': 'RU',
                },
                payment=common.payment(
                    payment_method='yandex_account_withdraw',
                    product_type='delivery',
                    product_id='plus_cashback',
                    amount='100',
                    payment_service='yaeda',
                ),
            ),
            common.billing_event(
                client_id=PLUS_CLIENT_ID,
                contract_id='1',
                payload={
                    'product_type': 'delivery',
                    'amount': '101',
                    'cashback_service': 'eda',
                    'has_plus': 'true',
                    'order_id': '123456',
                    'service_id': '645',
                    'country_code': 'RU',
                    'issuer': 'marketing',
                    'ticket': 'NEWSERVICE-1430',
                    'cashback_type': 'withdraw',
                    'campaign_name': 'OD delivery',
                },
                payment=common.payment(
                    payment_method='yandex_account_withdraw',
                    product_type='delivery',
                    product_id='plus_cashback',
                    amount='101',
                    payment_service='yaeda',
                ),
            ),
        )
        .run(transformer_fixtures)
    )

    await (
        helper.TransformerRetailTest()
        .on_payment_update_plus_cashback(
            client_id='45678',
            amount='102',
            payment_method='card',
            product_type='service_fee',
            product_id='plus_cashback',
            currency='RUB',
            counteragent_id='7',
        )
        .expect_stq_call_id(3)
        .expect(
            common.billing_event(
                client_id='89012',
                payment=common.payment(
                    payment_method='card',
                    product_type='product',
                    amount='100',
                    payment_service='yaeda',
                    product_id='plus_cashback',
                ),
            ),
            common.billing_event(
                client_id=PLUS_CLIENT_ID,
                contract_id='1',
                payload={
                    'product_type': 'product',
                    'amount': '100',
                    'cashback_service': 'eda',
                    'has_plus': 'true',
                    'order_id': '123456',
                    'service_id': '645',
                    'country_code': 'RU',
                },
                payment=common.payment(
                    payment_method='yandex_account_withdraw',
                    product_type='delivery',
                    product_id='plus_cashback',
                    amount='100',
                    payment_service='yaeda',
                ),
            ),
            common.billing_event(
                client_id=PLUS_CLIENT_ID,
                contract_id='1',
                payload={
                    'product_type': 'delivery',
                    'amount': '101',
                    'cashback_service': 'eda',
                    'has_plus': 'true',
                    'order_id': '123456',
                    'service_id': '645',
                    'country_code': 'RU',
                    'issuer': 'marketing',
                    'ticket': 'NEWSERVICE-1430',
                    'cashback_type': 'withdraw',
                    'campaign_name': 'OD delivery',
                },
                payment=common.payment(
                    payment_method='yandex_account_withdraw',
                    product_type='delivery',
                    product_id='plus_cashback',
                    amount='101',
                    payment_service='yaeda',
                ),
            ),
            common.billing_event(
                client_id=PLUS_CLIENT_ID,
                contract_id='1',
                payload={
                    'product_type': 'service_fee',
                    'amount': '102',
                    'cashback_service': 'eda',
                    'has_plus': 'true',
                    'order_id': '123456',
                    'service_id': '645',
                    'country_code': 'RU',
                    'issuer': 'marketing',
                    'ticket': 'NEWSERVICE-1430',
                    'cashback_type': 'withdraw',
                    'campaign_name': 'OD service_fee',
                },
                payment=common.payment(
                    payment_method='yandex_account_withdraw',
                    product_type='service_fee',
                    product_id='plus_cashback',
                    amount='102',
                    payment_service='yaeda',
                ),
            ),
        )
        .run(transformer_fixtures)
    )
