import pytest

from tests_eats_billing_processor import rules
from tests_eats_billing_processor.transformer import common
from tests_eats_billing_processor.transformer import helper


async def test_payments(load_json, transformer_fixtures):
    await (
        helper.TransformerTest()
        .with_order_nr('210405-000001')
        .using_business_rules(
            picker_id='4321', client_info=rules.client_info(client_id='1234'),
        )
        .insert_input_event(
            kind='payment_received', data=load_json('payment_received.json'),
        )
        .expect_billing_events(
            events=[load_json('payment_received_result.json')],
        )
        .expect_stq_call_id(1)
        .run(transformer_fixtures)
    )


@pytest.mark.parametrize(
    'currency, client_id, contract_id, mvp',
    [
        pytest.param(
            'RUB',
            helper.SERVICE_FEE_CLIENT_ID_RUB,
            helper.SERVICE_FEE_CONTRACT_ID_RUB,
            'MSKc',
        ),
        pytest.param(
            'KZT',
            helper.SERVICE_FEE_CLIENT_ID_KZT,
            helper.SERVICE_FEE_CONTRACT_ID_KZT,
            'AST',
        ),
        pytest.param(
            'BYN',
            helper.SERVICE_FEE_CLIENT_ID_BYN,
            helper.SERVICE_FEE_CONTRACT_ID_BYN,
            'MNKc',
        ),
    ],
)
async def test_payment_service_fee(
        transformer_fixtures, currency, client_id, contract_id, mvp,
):
    await (
        helper.TransformerTest()
        .with_order_nr('210405-000001')
        .on_payment_received(
            counteragent_id='123456',
            client_id=client_id,
            product_type='service_fee',
            amount='29',
            external_payment_id='external_1',
            currency=currency,
        )
        .expect(
            common.billing_event(
                client_info=rules.client_info(
                    client_id=client_id, contract_id=contract_id, mvp=mvp,
                ),
                payment=common.payment(
                    product_type='service_fee',
                    amount='29',
                    payment_method='card',
                    payment_terminal_id='terminal_1',
                    currency=currency,
                ),
            ),
        )
        .expect_stq_call_id(1)
        .run(transformer_fixtures)
    )


async def test_payments_assembly_commission(load_json, transformer_fixtures):
    data = load_json('payment_received.json')
    data['product_type'] = 'assembly'
    payment_res = load_json('payment_received_result.json')
    payment_res['payment']['product_type'] = 'assembly'
    await (
        helper.TransformerTest()
        .with_order_nr('210405-000001')
        .insert_input_event(kind='payment_received', data=data)
        .using_business_rules(
            picker_id='4321',
            client_info=rules.client_info(client_id='1234'),
            commission=rules.make_commission(
                commission_type='picker_delivery',
                params=rules.simple_commission(
                    commission='70',
                    acquiring_commission='30',
                    fix_commission='10',
                ),
            ),
        )
        .expect_billing_events(
            events=[
                payment_res,
                load_json('payment_received_commission_result.json'),
            ],
        )
        .expect_stq_call_id(1)
        .run(transformer_fixtures)
    )


async def test_payments_product_type_delivery_commission(
        load_json, transformer_fixtures,
):
    data = load_json('payment_received.json')
    data['product_type'] = 'delivery'
    payment_res = load_json('payment_received_result.json')
    payment_res['payment']['product_type'] = 'delivery'
    commission_res = load_json('payment_received_commission_result.json')
    commission_res['commission']['product_type'] = 'delivery'
    await (
        helper.TransformerTest()
        .with_order_nr('210405-000001')
        .insert_input_event(kind='payment_received', data=data)
        .using_business_rules(
            courier_id='4321',
            client_info=rules.client_info(client_id='1234'),
            commission=rules.make_commission(
                commission_type='courier_delivery',
                params=rules.simple_commission(
                    commission='70',
                    acquiring_commission='30',
                    fix_commission='10',
                ),
            ),
        )
        .expect_billing_events(events=[payment_res, commission_res])
        .expect_stq_call_id(1)
        .run(transformer_fixtures)
    )


async def test_payments_assembly_marketplace_commission(
        load_json, transformer_fixtures,
):
    data = load_json('payment_received.json')
    data['product_type'] = 'assembly'
    data['order_type'] = 'marketplace'
    payment_res = load_json('payment_received_result.json')
    payment_res['payment']['product_type'] = 'assembly'
    await (
        helper.TransformerTest()
        .with_order_nr('210405-000001')
        .insert_input_event(kind='payment_received', data=data)
        .using_business_rules(
            place_id='4321', client_info=rules.client_info(client_id='1234'),
        )
        .expect_billing_events(events=[payment_res])
        .expect_stq_call_id(1)
        .run(transformer_fixtures)
    )


async def test_payments_delivery_commission(load_json, transformer_fixtures):
    data = load_json('payment_received.json')
    data['product_type'] = 'delivery'
    data['amount'] = '150'
    payment_res = load_json('payment_received_result.json')
    payment_res['payment']['product_type'] = 'delivery'
    payment_res['payment']['amount'] = '150'
    commission = load_json('payment_received_commission_result.json')
    commission['commission']['product_type'] = 'delivery'
    commission['commission'][
        'amount'
    ] = '48.5'  # (150 (5+10))/100 == 22.5 + 26
    await (
        helper.TransformerTest()
        .with_order_nr('210405-000001')
        .insert_input_event(kind='payment_received', data=data)
        .using_business_rules(
            courier_id='4321',
            client_info=rules.client_info(client_id='1234'),
            commission=rules.make_commission(
                commission_type='courier_delivery',
                params=rules.simple_commission(
                    commission='5',
                    acquiring_commission='10',
                    fix_commission='26',
                ),
            ),
        )
        .expect_billing_events(events=[payment_res, commission])
        .expect_stq_call_id(1)
        .run(transformer_fixtures)
    )


async def test_payments_product_type_donation_commission(
        load_json, transformer_fixtures,
):
    data = load_json('payment_received.json')
    data['product_type'] = 'donation'
    payment_res = load_json('payment_received_result.json')
    payment_res['payment']['product_type'] = 'donation'
    payment_res['client']['contract_id'] = '3636412'
    payment_res['client']['mvp'] = 'MSKc'
    commission_res = load_json('payment_received_commission_result.json')
    commission_res['commission']['product_type'] = 'donation'
    commission_res['commission']['amount'] = '2.71'
    commission_res['client']['contract_id'] = '3636412'
    commission_res['client']['mvp'] = 'MSKc'
    await (
        helper.TransformerTest()
        .with_order_nr('210405-000001')
        .insert_input_event(kind='payment_received', data=data)
        .using_business_rules(
            place_id='1234',
            client_id='1234',
            commission=rules.make_commission(
                commission_type='donation',
                params=rules.simple_commission(
                    commission='1.8',
                    acquiring_commission='0',
                    fix_commission='0',
                ),
            ),
        )
        .expect_billing_events(events=[payment_res, commission_res])
        .expect_stq_call_id(1)
        .run(transformer_fixtures)
    )


async def test_payments_subscribe_commission(load_json, transformer_fixtures):
    data = load_json('commission_subscribe_fixed.json')
    await (
        helper.TransformerTest()
        .with_order_nr('210405-000001')
        .insert_input_event(kind='monthly_payment', data=data)
        .using_business_rules(
            place_id='place_1',
            client_info=rules.client_info(client_id='123456'),
        )
        .expect(
            common.billing_event(
                client_id='123456',
                commission=common.make_commission(
                    product_type='product',
                    product_id='subscribe_fixed',
                    amount='100',
                    commission_type='subscribe_fixed',
                ),
            ),
        )
        .expect_stq_call_id(1)
        .run(transformer_fixtures)
    )


async def test_refund(load_json, transformer_fixtures):
    await (
        helper.TransformerTest()
        .with_order_nr('210405-000002')
        .using_business_rules(
            picker_id='4321', client_info=rules.client_info(client_id='1234'),
        )
        .insert_input_event(
            kind='payment_refund', data=load_json('payment_refund.json'),
        )
        .expect_billing_events(
            events=[load_json('payment_refund_result.json')],
        )
        .expect_stq_call_id(1)
        .run(transformer_fixtures)
    )


@pytest.mark.parametrize(
    'currency, client_id, contract_id, mvp, country_code',
    [
        pytest.param(
            'RUB',
            helper.SERVICE_FEE_CLIENT_ID_RUB,
            helper.SERVICE_FEE_CONTRACT_ID_RUB,
            'MSKc',
            'RU',
        ),
        pytest.param(
            'KZT',
            helper.SERVICE_FEE_CLIENT_ID_KZT,
            helper.SERVICE_FEE_CONTRACT_ID_KZT,
            'AST',
            'KZ',
        ),
        pytest.param(
            'BYN',
            helper.SERVICE_FEE_CLIENT_ID_BYN,
            helper.SERVICE_FEE_CONTRACT_ID_BYN,
            'MNKc',
            'BY',
        ),
    ],
)
async def test_refund_service_fee(
        transformer_fixtures,
        currency,
        client_id,
        contract_id,
        mvp,
        country_code,
):
    await (
        helper.TransformerTest()
        .with_order_nr('210405-000002')
        .on_payment_refund(
            counteragent_id='123456',
            client_id=client_id,
            product_type='service_fee',
            amount='29',
            external_payment_id='external_1',
            currency=currency,
        )
        .expect(
            common.billing_event(
                client_info=rules.client_info(
                    client_id=client_id,
                    contract_id=contract_id,
                    mvp=mvp,
                    country_code=country_code,
                ),
                refund=common.refund(
                    product_type='service_fee',
                    amount='29',
                    payment_method='card',
                    payment_terminal_id='terminal_1',
                    currency=currency,
                ),
            ),
        )
        .expect_stq_call_id(1)
        .run(transformer_fixtures)
    )


async def test_refund_assembly_commission(load_json, transformer_fixtures):
    data = load_json('payment_refund.json')
    data['product_type'] = 'assembly'
    refund_res = load_json('payment_refund_result.json')
    refund_res['refund']['product_type'] = 'assembly'
    await (
        helper.TransformerTest()
        .with_order_nr('210405-000002')
        .insert_input_event(kind='payment_refund', data=data)
        .using_business_rules(
            picker_id='4321',
            client_info=rules.client_info(client_id='1234'),
            commission=rules.make_commission(
                commission_type='picker_delivery',
                params=rules.simple_commission(
                    commission='1',
                    acquiring_commission='0',
                    fix_commission='2',
                ),
            ),
        )
        .expect_billing_events(
            events=[
                refund_res,
                load_json('payment_refund_commission_result.json'),
            ],
        )
        .expect_stq_call_id(1)
        .run(transformer_fixtures)
    )


async def test_refund_product_type_delivery_commission(
        load_json, transformer_fixtures,
):
    data = load_json('payment_refund.json')
    data['product_type'] = 'delivery'
    refund_res = load_json('payment_refund_result.json')
    refund_res['refund']['product_type'] = 'delivery'
    commission_res = load_json('payment_refund_commission_result.json')
    commission_res['commission']['product_type'] = 'delivery'
    await (
        helper.TransformerTest()
        .with_order_nr('210405-000002')
        .insert_input_event(kind='payment_refund', data=data)
        .using_business_rules(
            courier_id='4321',
            client_info=rules.client_info(client_id='1234'),
            commission=rules.make_commission(
                commission_type='courier_delivery',
                params=rules.simple_commission(
                    commission='1',
                    acquiring_commission='0',
                    fix_commission='2',
                ),
            ),
        )
        .expect_billing_events(events=[refund_res, commission_res])
        .expect_stq_call_id(1)
        .run(transformer_fixtures)
    )


async def test_refund_assembly_marketplace_commission(
        load_json, transformer_fixtures,
):
    data = load_json('payment_refund.json')
    data['product_type'] = 'assembly'
    data['order_type'] = 'marketplace'
    refund_res = load_json('payment_refund_result.json')
    refund_res['refund']['product_type'] = 'assembly'
    await (
        helper.TransformerTest()
        .with_order_nr('210405-000002')
        .insert_input_event(kind='payment_refund', data=data)
        .using_business_rules(
            place_id='4321', client_info=rules.client_info(client_id='1234'),
        )
        .expect_billing_events(events=[refund_res])
        .expect_stq_call_id(1)
        .run(transformer_fixtures)
    )


async def test_refund_delivery_commission(load_json, transformer_fixtures):
    data = load_json('payment_refund.json')
    data['product_type'] = 'delivery'
    refund_res = load_json('payment_refund_result.json')
    refund_res['refund']['product_type'] = 'delivery'
    commission = load_json('payment_refund_commission_result.json')
    commission['commission']['product_type'] = 'delivery'
    commission['commission']['amount'] = '-13'
    await (
        helper.TransformerTest()
        .with_order_nr('210405-000002')
        .insert_input_event(kind='payment_refund', data=data)
        .using_business_rules(
            courier_id='4321',
            client_info=rules.client_info(client_id='1234'),
            commission=rules.make_commission(
                commission_type='courier_delivery',
                params=rules.simple_commission(
                    commission='15',
                    acquiring_commission='5',
                    fix_commission='3',
                ),
            ),
        )
        .expect_billing_events(events=[refund_res, commission])
        .expect_stq_call_id(1)
        .run(transformer_fixtures)
    )
