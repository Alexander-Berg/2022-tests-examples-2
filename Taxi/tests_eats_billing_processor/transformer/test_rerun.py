# pylint: disable=too-many-lines
import pytest

from tests_eats_billing_processor import rules
from tests_eats_billing_processor.transformer import common
from tests_eats_billing_processor.transformer import helper


@pytest.mark.pgsql(
    'eats_billing_processor', files=['input_event_for_reverse.sql'],
)
async def test_reverse(transformer_fixtures):
    common.set_rule_name('retail')
    billing_payment = common.billing_event(
        client_id='123456',
        external_payment_id='external_id_1',
        payment=common.payment(
            payment_method='card',
            product_type='product',
            product_id='product__001',
            amount='1500',
            currency='RUB',
        ),
    )
    billing_payment_result = common.billing_event(
        client_id='123456',
        external_payment_id='external_id_1',
        payment=common.payment(
            payment_method='card',
            product_type='product',
            product_id='product__001',
            amount='1000',
            currency='RUB',
        ),
    )
    billing_refund = common.billing_event(
        client_id='123456',
        external_payment_id='external_id_1',
        refund=common.refund(
            payment_method='card',
            product_type='product',
            product_id='product__001',
            amount='1000',
            currency='RUB',
        ),
    )
    billing_refund_result = common.billing_event(
        client_id='123456',
        external_payment_id='external_id_1',
        refund=common.refund(
            payment_method='card',
            product_type='product',
            product_id='product__001',
            amount='1500',
            currency='RUB',
        ),
    )
    billing_commission = common.billing_event(
        client_id='123456',
        external_payment_id='external_id_1',
        commission=common.make_commission(
            product_type='product',
            product_id='some_product_id',
            amount='100',
            currency='RUB',
        ),
    )
    billing_commission_result = common.billing_event(
        client_id='123456',
        external_payment_id='external_id_1',
        commission=common.make_commission(
            product_type='product',
            product_id='some_product_id',
            amount='-100',
            currency='RUB',
        ),
    )
    recalculate_billing_payment = common.billing_event(
        client_id='123456',
        external_payment_id='external_payment_id_1',
        payment=common.payment(
            payment_terminal_id='95426005',
            payment_method='card',
            product_type='delivery',
            product_id='delivery__001',
            amount='99',
            currency='RUB',
        ),
    )

    await (
        helper.TransformerTest()
        .with_order_nr('210405-000001')
        .insert_billing_event(input_event_id='1', data=billing_payment)
        .insert_billing_event(input_event_id='1', data=billing_refund)
        .insert_billing_event(input_event_id='1', data=billing_commission)
        .using_business_rules(
            courier_id='127054',
            client_info=rules.client_info(client_id='123456'),
            commission=rules.make_commission(
                commission_type='courier_delivery',
            ),
        )
        .on_rerun(fix_event_id=1, disable_reverse=False)
        .expect_billing_events(
            events=[
                billing_payment,
                billing_refund,
                billing_commission,
                billing_refund_result,
                billing_payment_result,
                billing_commission_result,
                recalculate_billing_payment,
            ],
        )
        .run(transformer_fixtures)
    )


@pytest.mark.pgsql(
    'eats_billing_processor', files=['input_event_for_reverse.sql'],
)
async def test_reverse_skip(transformer_fixtures):
    common.set_rule_name('retail')
    billing_payment = common.billing_event(
        client_id='123456',
        external_payment_id='external_id_1',
        payment=common.payment(
            payment_method='card',
            product_type='product',
            product_id='product__001',
            amount='1500',
            currency='RUB',
        ),
    )
    billing_payment_result = common.billing_event(
        client_id='123456',
        external_payment_id='external_id_1',
        payment=common.payment(
            payment_method='card',
            product_type='product',
            product_id='product__001',
            amount='1000',
            currency='RUB',
        ),
    )
    billing_refund = common.billing_event(
        client_id='123456',
        external_payment_id='external_id_1',
        refund=common.refund(
            payment_method='card',
            product_type='product',
            product_id='product__001',
            amount='1000',
            currency='RUB',
        ),
    )
    billing_commission = common.billing_event(
        client_id='123456',
        external_payment_id='external_id_1',
        commission=common.make_commission(
            product_type='product',
            product_id='some_product_id',
            amount='100',
            currency='RUB',
        ),
    )
    billing_commission_result = common.billing_event(
        client_id='123456',
        external_payment_id='external_id_1',
        commission=common.make_commission(
            product_type='product',
            product_id='some_product_id',
            amount='-100',
            currency='RUB',
        ),
    )
    rec_payment_received = common.billing_event(
        client_id='123456',
        external_payment_id='external_payment_id_1',
        payment=common.payment(
            payment_terminal_id='95426005',
            payment_method='card',
            product_type='delivery',
            product_id='delivery__001',
            amount='99',
            currency='RUB',
        ),
    )
    await (
        helper.TransformerTest()
        .with_order_nr('210405-000001')
        .insert_billing_event(
            input_event_id='1',
            data=billing_payment,
            external_id='reverse/external_id_1',
        )
        .using_business_rules(
            courier_id='127054',
            client_info=rules.client_info(client_id='123456'),
            commission=rules.make_commission(
                commission_type='courier_delivery',
            ),
        )
        .insert_billing_event(input_event_id='1', data=billing_refund)
        .insert_billing_event(input_event_id='1', data=billing_commission)
        .on_rerun(fix_event_id=1)
        .expect_billing_events(
            events=[
                billing_payment,
                billing_refund,
                billing_commission,
                billing_payment_result,
                billing_commission_result,
                rec_payment_received,
            ],
        )
        .run(transformer_fixtures)
    )


async def test_reverse_update(transformer_fixtures):
    payment_plus = common.billing_event(
        client_id='82058879',
        contract_id='1',
        payload={
            'payload': 'test',
            'place_id': 'place_1',
            'cashback_service': 'eda',
        },
        payment=common.payment(
            payment_method='yandex_account_topup',
            product_type='delivery',
            product_id='plus_cashback',
            amount='200',
            payment_service='yaeda',
        ),
    )
    commission_plus = common.billing_event(
        client_id='123456',
        commission=common.make_commission(
            product_type='delivery',
            amount='100',
            product_id='plus_cashback_default',
            commission_type='plus_cashback',
        ),
    )
    payment_plus_1 = common.billing_event(
        client_id='82058879',
        contract_id='1',
        payload={
            'payload': 'test',
            'place_id': 'place_1',
            'cashback_service': 'eda',
        },
        payment=common.payment(
            payment_method='yandex_account_topup',
            product_type='delivery',
            product_id='plus_cashback',
            amount='500',
            payment_service='yaeda',
        ),
    )
    commission_plus_1 = common.billing_event(
        client_id='123456',
        commission=common.make_commission(
            product_type='delivery',
            amount='900',
            product_id='plus_cashback_default',
            commission_type='plus_cashback',
        ),
    )
    refund_plus = common.billing_event(
        client_id='82058879',
        contract_id='1',
        payload={
            'payload': 'test',
            'place_id': 'place_1',
            'cashback_service': 'eda',
        },
        refund=common.refund(
            payment_method='yandex_account_topup',
            product_type='delivery',
            product_id='plus_cashback',
            amount='200',
            payment_service='yaeda',
        ),
    )
    refund_commission_plus = common.billing_event(
        client_id='123456',
        commission=common.make_commission(
            product_type='delivery',
            amount='-100',
            product_id='plus_cashback_default',
            commission_type='plus_cashback',
        ),
    )
    await (
        helper.TransformerTest()
        .on_plus_cashback_emission(
            client_id='123456',
            amount='200',
            plus_cashback_amount_per_place='100',
            payload={
                'payload': 'test',
                'place_id': 'place_1',
                'cashback_service': 'eda',
            },
        )
        .on_plus_cashback_emission(
            client_id='123456',
            amount='500',
            plus_cashback_amount_per_place='900',
            payload={
                'payload': 'test',
                'place_id': 'place_1',
                'cashback_service': 'eda',
            },
        )
        .using_business_rules(
            place_id='place_1',
            client_info=rules.client_info(client_id='123456'),
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
            payment_plus,
            commission_plus,
            refund_plus,
            payment_plus_1,
            refund_commission_plus,
            commission_plus_1,
        )
        .run(transformer_fixtures)
    )
    await (
        helper.TransformerTest()
        .on_rerun(fix_event_id=2)
        .using_business_rules(
            place_id='place_1',
            client_info=rules.client_info(client_id='123456'),
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
            payment_plus,
            commission_plus,
            refund_plus,
            payment_plus_1,
            refund_commission_plus,
            commission_plus_1,
            common.billing_event(
                client_id='82058879',
                contract_id='1',
                payload={
                    'payload': 'test',
                    'place_id': 'place_1',
                    'cashback_service': 'eda',
                },
                payment=common.payment(
                    payment_method='yandex_account_topup',
                    product_type='delivery',
                    product_id='plus_cashback',
                    amount='200',
                    payment_service='yaeda',
                ),
            ),
            common.billing_event(
                client_id='82058879',
                contract_id='1',
                payload={
                    'payload': 'test',
                    'place_id': 'place_1',
                    'cashback_service': 'eda',
                },
                refund=common.refund(
                    payment_method='yandex_account_topup',
                    product_type='delivery',
                    product_id='plus_cashback',
                    amount='500',
                    payment_service='yaeda',
                ),
            ),
            common.billing_event(
                client_id='123456',
                commission=common.make_commission(
                    product_type='delivery',
                    amount='100',
                    product_id='plus_cashback_default',
                    commission_type='plus_cashback',
                ),
            ),
            common.billing_event(
                client_id='123456',
                commission=common.make_commission(
                    product_type='delivery',
                    amount='-900',
                    product_id='plus_cashback_default',
                    commission_type='plus_cashback',
                ),
            ),
            common.billing_event(
                client_id='82058879',
                contract_id='1',
                payload={
                    'payload': 'test',
                    'place_id': 'place_1',
                    'cashback_service': 'eda',
                },
                refund=common.refund(
                    payment_method='yandex_account_topup',
                    product_type='delivery',
                    product_id='plus_cashback',
                    amount='200',
                    payment_service='yaeda',
                ),
            ),
            common.billing_event(
                client_id='82058879',
                contract_id='1',
                payload={
                    'payload': 'test',
                    'place_id': 'place_1',
                    'cashback_service': 'eda',
                },
                payment=common.payment(
                    payment_method='yandex_account_topup',
                    product_type='delivery',
                    product_id='plus_cashback',
                    amount='500',
                    payment_service='yaeda',
                ),
            ),
            common.billing_event(
                client_id='123456',
                commission=common.make_commission(
                    product_type='delivery',
                    amount='-100',
                    product_id='plus_cashback_default',
                    commission_type='plus_cashback',
                ),
            ),
            common.billing_event(
                client_id='123456',
                commission=common.make_commission(
                    product_type='delivery',
                    amount='900',
                    product_id='plus_cashback_default',
                    commission_type='plus_cashback',
                ),
            ),
        )
        .expect_stq_call_id(2)
        .run(transformer_fixtures)
    )


OVERRIDDEN_RERUN_RULES = {
    'retail': {
        'payment_received': [
            {
                'create': [
                    {'transaction_date#xget': '/event/transaction_date'},
                    {'external_payment_id#xget': '/event/external_payment_id'},
                    {
                        'client#object': [
                            {'id': '123456'},
                            {'contract_id': 'test_contract_id'},
                        ],
                    },
                    {
                        'payment#object': [
                            {'product_type#xget': '/event/product_type'},
                            {'amount': '10.99'},
                            {'currency#xget': '/event/currency'},
                            {'product_id#xget': '/event/product_id'},
                            {'payment_method#xget': '/event/payment_method'},
                        ],
                    },
                ],
            },
        ],
    },
}


@pytest.mark.config(EATS_BILLING_PROCESSOR_RERUN_RULES=OVERRIDDEN_RERUN_RULES)
@pytest.mark.pgsql(
    'eats_billing_processor', files=['input_event_for_reverse.sql'],
)
async def test_reverse_rerun_rules(transformer_fixtures):
    common.set_rule_name('retail')
    billing_payment = common.billing_event(
        client_id='123456',
        external_payment_id='external_id_1',
        payment=common.payment(
            payment_method='card',
            product_type='product',
            product_id='product__001',
            amount='1500',
            currency='RUB',
        ),
    )
    billing_refund_result = common.billing_event(
        client_id='123456',
        external_payment_id='external_id_1',
        refund=common.refund(
            payment_method='card',
            product_type='product',
            product_id='product__001',
            amount='1500',
            currency='RUB',
        ),
    )
    recalculate_billing_payment = common.billing_event(
        client_id='123456',
        external_payment_id='external_payment_id_1',
        payment=common.payment(
            payment_method='card',
            product_type='delivery',
            product_id='delivery__001',
            amount='10.99',
            currency='RUB',
        ),
    )

    await (
        helper.TransformerTest('retail')
        .with_order_nr('210405-000001')
        .insert_billing_event(input_event_id='1', data=billing_payment)
        .using_business_rules(
            courier_id='127054',
            client_info=rules.client_info(client_id='123456'),
            commission=rules.make_commission(
                commission_type='courier_delivery',
            ),
        )
        .on_rerun(fix_event_id=1)
        .expect_billing_events(
            events=[
                billing_payment,
                billing_refund_result,
                recalculate_billing_payment,
            ],
        )
        .run(transformer_fixtures)
    )


OVERRIDDEN_RERUN_RULES = {
    'default': {
        'payment_received': [
            {
                'create': [
                    {'transaction_date#xget': '/event/transaction_date'},
                    {'external_payment_id#xget': '/event/external_payment_id'},
                    {
                        'client#object': [
                            {'id': '123456'},
                            {'contract_id': 'test_contract_id'},
                        ],
                    },
                    {
                        'payment#object': [
                            {'product_type#xget': '/event/product_type'},
                            {'amount': '30'},
                            {'currency#xget': '/event/currency'},
                            {'product_id#xget': '/event/product_id'},
                            {'payment_method#xget': '/event/payment_method'},
                        ],
                    },
                ],
            },
        ],
    },
}


@pytest.mark.config(EATS_BILLING_PROCESSOR_RERUN_RULES=OVERRIDDEN_RERUN_RULES)
@pytest.mark.pgsql(
    'eats_billing_processor', files=['input_event_for_reverse.sql'],
)
async def test_reverse_rerun_default_rules(transformer_fixtures):
    billing_payment = common.billing_event(
        client_id='123456',
        external_payment_id='external_id_1',
        payment=common.payment(
            payment_method='card',
            product_type='product',
            product_id='product__001',
            amount='1500',
            currency='RUB',
        ),
    )
    billing_refund_result = common.billing_event(
        client_id='123456',
        external_payment_id='external_id_1',
        refund=common.refund(
            payment_method='card',
            product_type='product',
            product_id='product__001',
            amount='1500',
            currency='RUB',
        ),
    )
    recalculate_billing_payment = common.billing_event(
        client_id='123456',
        external_payment_id='external_payment_id_1',
        payment=common.payment(
            payment_method='card',
            product_type='delivery',
            product_id='delivery__001',
            amount='30',
            currency='RUB',
        ),
    )

    await (
        helper.TransformerTest('retail')
        .with_order_nr('210405-000001')
        .insert_billing_event(input_event_id='1', data=billing_payment)
        .using_business_rules(
            courier_id='127054',
            client_info=rules.client_info(client_id='123456'),
            commission=rules.make_commission(
                commission_type='courier_delivery',
            ),
        )
        .on_rerun(fix_event_id=1)
        .expect_billing_events(
            events=[
                billing_payment,
                billing_refund_result,
                recalculate_billing_payment,
            ],
        )
        .run(transformer_fixtures)
    )


@pytest.mark.pgsql(
    'eats_billing_processor', files=['input_event_for_reverse.sql'],
)
async def test_reverse_disable(transformer_fixtures):
    billing_payment = common.billing_event(
        client_id='123456',
        external_payment_id='external_id_1',
        payment=common.payment(
            payment_method='card',
            product_type='product',
            product_id='product__001',
            amount='1500',
            currency='RUB',
        ),
    )
    billing_refund = common.billing_event(
        client_id='123456',
        external_payment_id='external_id_1',
        refund=common.refund(
            payment_method='card',
            product_type='product',
            product_id='product__001',
            amount='1000',
            currency='RUB',
        ),
    )
    billing_commission = common.billing_event(
        client_id='123456',
        external_payment_id='external_id_1',
        commission=common.make_commission(
            product_type='product',
            product_id='some_product_id',
            amount='100',
            currency='RUB',
        ),
    )
    recalculate_billing_payment = common.billing_event(
        client_id='123456',
        external_payment_id='external_payment_id_1',
        payment=common.payment(
            payment_terminal_id='95426005',
            payment_method='card',
            product_type='delivery',
            product_id='delivery__001',
            amount='99',
            currency='RUB',
        ),
    )

    await (
        helper.TransformerTest()
        .with_order_nr('210405-000001')
        .insert_billing_event(
            input_event_id='1', data=billing_payment, external_id='1/0',
        )
        .insert_billing_event(
            input_event_id='1', data=billing_refund, external_id='1/1',
        )
        .insert_billing_event(
            input_event_id='1', data=billing_commission, external_id='1/2',
        )
        .using_business_rules(
            courier_id='127054',
            client_info=rules.client_info(client_id='123456'),
            commission=rules.make_commission(
                commission_type='courier_delivery',
            ),
        )
        .on_rerun(fix_event_id=1, disable_reverse=True)
        .expect_billing_events(
            events=[
                billing_payment,
                billing_refund,
                billing_commission,
                recalculate_billing_payment,
            ],
        )
        .run(transformer_fixtures)
    )


@pytest.mark.pgsql(
    'eats_billing_processor', files=['billing_event_selection.sql'],
)
async def test_reverse_selection_events(transformer_fixtures):
    common.set_rule_name('retail')
    billing_payment = common.billing_event(
        client_id='123456',
        external_payment_id='external_id_1',
        payment=common.payment(
            payment_method='card',
            product_type='product',
            product_id='product__001',
            amount='1500',
            currency='RUB',
        ),
    )
    billing_payment_result = common.billing_event(
        client_id='123456',
        external_payment_id='external_id_1',
        payment=common.payment(
            payment_method='card',
            product_type='product',
            product_id='product__001',
            amount='1000',
            currency='RUB',
        ),
    )
    billing_refund = common.billing_event(
        client_id='123456',
        external_payment_id='external_id_1',
        refund=common.refund(
            payment_method='card',
            product_type='product',
            product_id='product__001',
            amount='1000',
            currency='RUB',
        ),
    )
    billing_refund_result = common.billing_event(
        client_id='123456',
        external_payment_id='external_id_1',
        refund=common.refund(
            payment_method='card',
            product_type='product',
            product_id='product__001',
            amount='1500',
            currency='RUB',
        ),
    )
    billing_commission = common.billing_event(
        client_id='123456',
        external_payment_id='external_id_1',
        commission=common.make_commission(
            product_type='product',
            product_id='some_product_id',
            amount='100',
            currency='RUB',
        ),
    )
    billing_commission_result = common.billing_event(
        client_id='123456',
        external_payment_id='external_id_1',
        commission=common.make_commission(
            product_type='product',
            product_id='some_product_id',
            amount='-100',
            currency='RUB',
        ),
    )
    recalculate_billing_payment = common.billing_event(
        client_id='123456',
        external_payment_id='external_payment_id_1',
        payment=common.payment(
            payment_terminal_id='95426005',
            payment_method='card',
            product_type='delivery',
            product_id='delivery__001',
            amount='99',
            currency='RUB',
        ),
    )

    await (
        helper.TransformerTest()
        .with_order_nr('201217-305204')
        .insert_billing_event(
            input_event_id='1', data=billing_payment, external_id='1/1',
        )
        .insert_billing_event(
            input_event_id='1', data=billing_refund, external_id='1/2',
        )
        .using_business_rules(
            courier_id='127054',
            client_info=rules.client_info(client_id='123456'),
            commission=rules.make_commission(
                commission_type='courier_delivery',
            ),
        )
        .on_rerun(fix_event_id=1)
        .expect_billing_events(
            events=[
                billing_commission,
                billing_payment,
                billing_refund,
                billing_refund_result,
                billing_payment_result,
                billing_commission_result,
                recalculate_billing_payment,
            ],
        )
        .run(transformer_fixtures)
    )


@pytest.mark.pgsql(
    'eats_billing_processor', files=['input_event_for_reverse.sql'],
)
async def test_reverse_rule_from_billing_event(transformer_fixtures):
    billing_payment = common.billing_event(
        client_id='123456',
        external_payment_id='external_id_1',
        rule='restaurant',
        payment=common.payment(
            payment_method='card',
            product_type='product',
            product_id='product__001',
            amount='1000',
            currency='RUB',
        ),
    )
    reverse_billing_payment = common.billing_event(
        client_id='123456',
        external_payment_id='external_id_1',
        rule='restaurant',
        refund=common.refund(
            payment_method='card',
            product_type='product',
            product_id='product__001',
            amount='1000',
            currency='RUB',
        ),
    )
    recalculate_billing_payment = common.billing_event(
        client_id='123456',
        external_payment_id='external_payment_id_1',
        rule='retail',
        payment=common.payment(
            payment_terminal_id='95426005',
            payment_method='card',
            product_type='delivery',
            product_id='delivery__001',
            amount='99',
            currency='RUB',
        ),
    )

    await (
        helper.TransformerTest()
        .with_order_nr('210405-000001')
        .insert_billing_event(input_event_id='1', data=billing_payment)
        .using_business_rules(
            courier_id='127054',
            client_info=rules.client_info(client_id='123456'),
            commission=rules.make_commission(
                commission_type='courier_delivery',
            ),
        )
        .on_rerun(fix_event_id=1, disable_reverse=False)
        .expect_billing_events(
            events=[
                billing_payment,
                reverse_billing_payment,
                recalculate_billing_payment,
            ],
        )
        .run(transformer_fixtures)
    )


async def test_rerun_rules_override(transformer_fixtures):
    await (
        helper.TransformerTest('retail')
        .on_payment_received(
            counteragent_id='counterparty_1',
            client_id='123456',
            product_type='delivery',
            amount='200',
        )
        .using_business_rules(
            courier_id='counterparty_1',
            client_info=rules.client_info(client_id='123456'),
            commission=rules.make_commission(
                commission_type='courier_delivery',
                params=rules.simple_commission(
                    commission='10',
                    acquiring_commission='10',
                    fix_commission='10',
                ),
            ),
        )
        .expect(
            common.billing_event(
                client_id='123456',
                payment=common.payment(
                    payment_method='card',
                    payment_terminal_id='terminal_1',
                    product_type='delivery',
                    amount='200',
                ),
            ),
            common.billing_event(
                client_id='123456',
                commission=common.make_commission(
                    product_type='delivery', amount='50',
                ),
            ),
        )
        .run(transformer_fixtures)
    )

    await (
        helper.TransformerTest('retail')
        .using_business_rules(
            courier_id='counterparty_1',
            client_info=rules.client_info(client_id='123456'),
            commission=rules.make_commission(
                commission_type='courier_delivery',
                params=rules.simple_commission(
                    commission='20',
                    acquiring_commission='20',
                    fix_commission='20',
                ),
            ),
        )
        .on_rerun(fix_event_id=1, rule_override='restaurant')
        .expect(
            common.billing_event(
                client_id='123456',
                payment=common.payment(
                    payment_method='card',
                    payment_terminal_id='terminal_1',
                    product_type='delivery',
                    amount='200',
                ),
            ),
            common.billing_event(
                client_id='123456',
                commission=common.make_commission(
                    product_type='delivery', amount='50',
                ),
            ),
            common.billing_event(
                client_id='123456',
                refund=common.refund(
                    payment_method='card',
                    payment_terminal_id='terminal_1',
                    product_type='delivery',
                    amount='200',
                ),
            ),
            common.billing_event(
                client_id='123456',
                commission=common.make_commission(
                    product_type='delivery', amount='-50',
                ),
            ),
            common.billing_event(
                client_id='123456',
                rule='restaurant',
                payment=common.payment(
                    payment_method='card',
                    payment_terminal_id='terminal_1',
                    product_type='delivery',
                    amount='200',
                ),
            ),
            common.billing_event(
                client_id='123456',
                rule='restaurant',
                commission=common.make_commission(
                    product_type='delivery', amount='100',
                ),
            ),
        )
        .run(transformer_fixtures)
    )
