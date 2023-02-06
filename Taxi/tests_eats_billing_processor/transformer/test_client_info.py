from tests_eats_billing_processor import rules
from tests_eats_billing_processor.transformer import common
from tests_eats_billing_processor.transformer import helper


async def test_payment_core_client_info(transformer_fixtures):
    await (
        helper.TransformerTest()
        .with_order_nr('210405-000001')
        .on_payment_received(
            counteragent_id='place_1',
            product_type='product',
            amount='200',
            flow_type='native',
        )
        .using_business_rules(
            place_id='place_1',
            client_info=rules.client_info(
                client_id='23456',
                mvp='mvp_1',
                country_code='RU',
                contract_id='contract_1',
            ),
            commission=rules.make_commission(
                commission_type='place_delivery',
                params=rules.simple_commission(
                    commission='10',
                    acquiring_commission='10',
                    fix_commission='10',
                ),
            ),
        )
        .expect(
            common.billing_event(
                client_info={
                    'id': '23456',
                    'mvp': 'mvp_1',
                    'country_code': 'RU',
                    'contract_id': 'contract_1',
                },
                payment=common.payment(
                    payment_method='card',
                    payment_terminal_id='terminal_1',
                    product_type='product',
                    amount='200',
                    product_id='product/native',
                ),
            ),
        )
        .expect_stq_call_id(1)
        .run(transformer_fixtures)
    )


async def test_payment_courier_commission_core_client_info(
        transformer_fixtures,
):
    await (
        helper.TransformerTest()
        .with_order_nr('210405-000001')
        .on_payment_received(
            counteragent_id='delivery_2',
            product_type='delivery',
            amount='200',
        )
        .using_business_rules(
            courier_id='delivery_2',
            client_info=rules.client_info(
                client_id='23456',
                mvp='mvp_1',
                country_code='RU',
                contract_id='contract_1',
                employment='courier_service',
            ),
            commission=rules.make_commission(
                commission_type='courier_delivery',
                params=rules.simple_commission(
                    commission='5',
                    acquiring_commission='10',
                    fix_commission='10',
                ),
            ),
        )
        .expect(
            common.billing_event(
                client_info={
                    'id': '23456',
                    'mvp': 'mvp_1',
                    'country_code': 'RU',
                    'contract_id': 'contract_1',
                    'employment': 'courier_service',
                },
                payment=common.payment(
                    payment_method='card',
                    payment_terminal_id='terminal_1',
                    product_type='delivery',
                    amount='200',
                    product_id='delivery/native',
                ),
            ),
            common.billing_event(
                client_info={
                    'id': '23456',
                    'mvp': 'mvp_1',
                    'country_code': 'RU',
                    'contract_id': 'contract_1',
                    'employment': 'courier_service',
                },
                commission=common.make_commission(
                    product_type='delivery', amount='40',
                ),
            ),
        )
        .expect_stq_call_id(1)
        .run(transformer_fixtures)
    )


async def test_payment_picker_commission_core_client_info(
        transformer_fixtures,
):
    await (
        helper.TransformerTest()
        .with_order_nr('210405-000001')
        .on_payment_received(
            counteragent_id='picker_2', product_type='assembly', amount='200',
        )
        .using_business_rules(
            picker_id='picker_2',
            client_info=rules.client_info(
                client_id='23456',
                mvp='mvp_1',
                country_code='RU',
                contract_id='contract_1',
                employment='self_employed',
            ),
            commission=rules.make_commission(
                commission_type='picker_delivery',
                params=rules.simple_commission(
                    commission='5',
                    acquiring_commission='10',
                    fix_commission='10',
                ),
            ),
        )
        .expect(
            common.billing_event(
                client_info={
                    'id': '23456',
                    'mvp': 'mvp_1',
                    'country_code': 'RU',
                    'contract_id': 'contract_1',
                    'employment': 'self_employed',
                },
                payment=common.payment(
                    payment_method='card',
                    payment_terminal_id='terminal_1',
                    product_type='assembly',
                    amount='200',
                    product_id='assembly/native',
                ),
            ),
            common.billing_event(
                client_info={
                    'id': '23456',
                    'mvp': 'mvp_1',
                    'country_code': 'RU',
                    'contract_id': 'contract_1',
                    'employment': 'self_employed',
                },
                commission=common.make_commission(
                    product_type='assembly', amount='40',
                ),
            ),
        )
        .expect_stq_call_id(1)
        .run(transformer_fixtures)
    )


async def test_payment_courier_marketplace_core_client_info(
        transformer_fixtures,
):
    await (
        helper.TransformerTest()
        .with_order_nr('210405-000001')
        .on_payment_received(
            counteragent_id='place_2',
            product_type='delivery',
            amount='200',
            order_type='marketplace',
            flow_type='native',
        )
        .using_business_rules(
            place_id='place_2',
            client_info=rules.client_info(
                client_id='23456',
                mvp='mvp_1',
                country_code='RU',
                contract_id='contract_1',
            ),
            commission=rules.make_commission(
                commission_type='place_delivery',
                params=rules.simple_commission(
                    commission='10',
                    acquiring_commission='10',
                    fix_commission='10',
                ),
            ),
        )
        .expect(
            common.billing_event(
                client_info=rules.client_info(
                    client_id='23456',
                    mvp='mvp_1',
                    country_code='RU',
                    contract_id='contract_1',
                ),
                payment=common.payment(
                    payment_method='card',
                    payment_terminal_id='terminal_1',
                    product_type='delivery',
                    amount='200',
                    product_id='delivery/native',
                ),
            ),
        )
        .expect_stq_call_id(1)
        .run(transformer_fixtures)
    )


async def test_payment_courier_marketplace_core_client_info_fallback(
        transformer_fixtures,
):
    await (
        helper.TransformerTest()
        .with_order_nr('210405-000001')
        .on_payment_received(
            counteragent_id='delivery_2',
            product_type='delivery',
            amount='200',
            order_type='marketplace',
            client_id='45678',
            flow_type='native',
        )
        .using_business_rules(
            place_id='delivery_2',
            client_info=rules.client_info(
                client_id='23456',
                mvp='mvp_1',
                country_code='RU',
                contract_id='contract_1',
            ),
            commission=rules.make_commission(
                commission_type='place_delivery',
                params=rules.simple_commission(
                    commission='10',
                    acquiring_commission='10',
                    fix_commission='10',
                ),
            ),
        )
        .expect(
            common.billing_event(
                client_info=rules.client_info(
                    client_id='23456',
                    contract_id='contract_1',
                    mvp='mvp_1',
                    country_code='RU',
                ),
                payment=common.payment(
                    payment_method='card',
                    payment_terminal_id='terminal_1',
                    product_type='delivery',
                    amount='200',
                    product_id='delivery/native',
                ),
            ),
        )
        .expect_stq_call_id(1)
        .run(transformer_fixtures)
    )


async def test_refund_core_client_info(transformer_fixtures):
    await (
        helper.TransformerTest()
        .with_order_nr('210405-000001')
        .on_payment_refund(
            counteragent_id='place_1',
            product_type='product',
            amount='200',
            flow_type='native',
        )
        .using_business_rules(
            place_id='place_1',
            client_info=rules.client_info(
                client_id='23456',
                mvp='mvp_1',
                country_code='RU',
                contract_id='contract_1',
            ),
            commission=rules.make_commission(
                commission_type='place_delivery',
                params=rules.simple_commission(
                    commission='10',
                    acquiring_commission='10',
                    fix_commission='10',
                ),
            ),
        )
        .expect(
            common.billing_event(
                client_info={
                    'id': '23456',
                    'mvp': 'mvp_1',
                    'country_code': 'RU',
                    'contract_id': 'contract_1',
                },
                refund=common.refund(
                    payment_method='card',
                    payment_terminal_id='terminal_1',
                    product_type='product',
                    amount='200',
                    product_id='product/native',
                ),
            ),
        )
        .expect_stq_call_id(1)
        .run(transformer_fixtures)
    )


async def test_refund_courier_commission_core_client_info(
        transformer_fixtures,
):
    await (
        helper.TransformerTest()
        .with_order_nr('210405-000001')
        .on_payment_refund(
            counteragent_id='courier_1', product_type='delivery', amount='200',
        )
        .using_business_rules(
            courier_id='courier_1',
            client_info=rules.client_info(
                client_id='23456',
                mvp='mvp_1',
                country_code='RU',
                contract_id='contract_1',
                employment='self_employed',
            ),
            commission=rules.make_commission(
                commission_type='courier_delivery',
                params=rules.simple_commission(
                    commission='5',
                    acquiring_commission='10',
                    fix_commission='10',
                ),
            ),
        )
        .expect(
            common.billing_event(
                client_info={
                    'id': '23456',
                    'mvp': 'mvp_1',
                    'country_code': 'RU',
                    'contract_id': 'contract_1',
                    'employment': 'self_employed',
                },
                refund=common.refund(
                    payment_method='card',
                    payment_terminal_id='terminal_1',
                    product_type='delivery',
                    amount='200',
                    product_id='delivery/native',
                ),
            ),
            common.billing_event(
                client_info={
                    'id': '23456',
                    'mvp': 'mvp_1',
                    'country_code': 'RU',
                    'contract_id': 'contract_1',
                    'employment': 'self_employed',
                },
                commission=common.make_commission(
                    product_type='delivery', amount='-40',
                ),
            ),
        )
        .expect_stq_call_id(1)
        .run(transformer_fixtures)
    )


async def test_refund_picker_commission_core_client_info(transformer_fixtures):
    await (
        helper.TransformerTest()
        .with_order_nr('210405-000001')
        .on_payment_refund(
            counteragent_id='picker_1', product_type='assembly', amount='200',
        )
        .using_business_rules(
            picker_id='picker_1',
            client_info=rules.client_info(
                client_id='23456',
                mvp='mvp_1',
                country_code='RU',
                contract_id='contract_1',
                employment='self_employed',
            ),
            commission=rules.make_commission(
                commission_type='picker_delivery',
                params=rules.simple_commission(
                    commission='5',
                    acquiring_commission='10',
                    fix_commission='10',
                ),
            ),
        )
        .expect(
            common.billing_event(
                client_info={
                    'id': '23456',
                    'mvp': 'mvp_1',
                    'country_code': 'RU',
                    'contract_id': 'contract_1',
                    'employment': 'self_employed',
                },
                refund=common.refund(
                    payment_method='card',
                    payment_terminal_id='terminal_1',
                    product_type='assembly',
                    amount='200',
                    product_id='assembly/native',
                ),
            ),
            common.billing_event(
                client_info={
                    'id': '23456',
                    'mvp': 'mvp_1',
                    'country_code': 'RU',
                    'contract_id': 'contract_1',
                    'employment': 'self_employed',
                },
                commission=common.make_commission(
                    product_type='assembly', amount='-40',
                ),
            ),
        )
        .expect_stq_call_id(1)
        .run(transformer_fixtures)
    )


async def test_refund_courier_marketplace_core_client_info(
        transformer_fixtures,
):
    await (
        helper.TransformerTest()
        .with_order_nr('210405-000001')
        .on_payment_refund(
            counteragent_id='place_1',
            product_type='delivery',
            amount='200',
            order_type='marketplace',
            flow_type='native',
        )
        .using_business_rules(
            place_id='place_1',
            client_info=rules.client_info(
                client_id='23456',
                mvp='mvp_1',
                country_code='RU',
                contract_id='contract_1',
            ),
            commission=rules.make_commission(
                commission_type='place_delivery',
                params=rules.simple_commission(
                    commission='10',
                    acquiring_commission='10',
                    fix_commission='10',
                ),
            ),
        )
        .expect(
            common.billing_event(
                client_info=rules.client_info(
                    client_id='23456',
                    mvp='mvp_1',
                    country_code='RU',
                    contract_id='contract_1',
                ),
                refund=common.refund(
                    payment_method='card',
                    payment_terminal_id='terminal_1',
                    product_type='delivery',
                    amount='200',
                    product_id='delivery/native',
                ),
            ),
        )
        .expect_stq_call_id(1)
        .run(transformer_fixtures)
    )


async def test_refund_courier_marketplace_core_client_info_fallback(
        transformer_fixtures,
):
    await (
        helper.TransformerTest()
        .with_order_nr('210405-000001')
        .on_payment_refund(
            counteragent_id='courier_1',
            product_type='delivery',
            amount='200',
            order_type='marketplace',
            client_id='56789',
            flow_type='native',
        )
        .using_business_rules(
            place_id='courier_1',
            client_info=rules.client_info(client_id='23456', mvp='mvp_1'),
            commission=rules.make_commission(
                commission_type='place_delivery',
                params=rules.simple_commission(
                    commission='10',
                    acquiring_commission='10',
                    fix_commission='10',
                ),
            ),
        )
        .expect(
            common.billing_event(
                client_info=rules.client_info(
                    client_id='23456',
                    mvp='mvp_1',
                    contract_id='test_contract_id',
                ),
                refund=common.refund(
                    payment_method='card',
                    payment_terminal_id='terminal_1',
                    product_type='delivery',
                    amount='200',
                    product_id='delivery/native',
                ),
            ),
        )
        .expect_stq_call_id(1)
        .run(transformer_fixtures)
    )
