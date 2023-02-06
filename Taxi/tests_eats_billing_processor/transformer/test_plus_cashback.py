# pylint: disable=C5521
import datetime

import pytest

from tests_eats_billing_processor import rules
from tests_eats_billing_processor.transformer import common
from tests_eats_billing_processor.transformer.helper import PLUS_CLIENT_ID
from tests_eats_billing_processor.transformer.retail import helper


async def test_plus_cashback_emission(transformer_fixtures):
    await (
        helper.TransformerRetailTest()
        .on_plus_cashback_emission(
            client_id='123456',
            amount='200',
            plus_cashback_amount_per_place='100',
            flow_type='retail',
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
            common.billing_event(
                client_id=PLUS_CLIENT_ID,
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
                client_id='123456',
                commission=common.make_commission(
                    product_type='delivery',
                    amount='100',
                    product_id='plus_cashback_retail',
                    commission_type='plus_cashback',
                ),
            ),
        )
        .run(transformer_fixtures)
    )


@pytest.mark.config(
    EATS_BILLING_PROCESSOR_LAVKA_FEATURES={
        'lavka_cashback_service_id_enabled': True,
    },
)
async def test_plus_cashback_emission_with_cashback_service(
        transformer_fixtures,
):
    await (
        helper.TransformerRetailTest()
        .on_plus_cashback_emission(
            client_id='23456',
            amount='200',
            plus_cashback_amount_per_place='100',
            flow_type='retail',
            payload={'cashback_service': 'lavka', 'place_id': 'place_1'},
        )
        .using_business_rules(
            place_id='place_1',
            client_info=rules.client_info(client_id='23456'),
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
                client_id=PLUS_CLIENT_ID,
                contract_id='1',
                payload={'cashback_service': 'lavka', 'place_id': 'place_1'},
                payment=common.payment(
                    payment_method='yandex_account_topup',
                    product_type='delivery',
                    product_id='grocery_plus_cashback',
                    amount='200',
                    payment_service='yaeda',
                ),
            ),
            common.billing_event(
                client_id='23456',
                contract_id='1',
                commission=common.make_commission(
                    product_type='delivery',
                    amount='100',
                    product_id='plus_cashback_retail',
                    commission_type='plus_cashback',
                ),
            ),
        )
        .run(transformer_fixtures)
    )


@pytest.mark.config(
    EATS_BILLING_PROCESSOR_LAVKA_FEATURES={
        'lavka_cashback_service_id_enabled': True,
    },
)
async def test_plus_cashback_emission_with_order_nr_grocery(
        transformer_fixtures,
):
    await (
        helper.TransformerRetailTest()
        .with_order_nr('1234-grocery')
        .on_plus_cashback_emission(
            client_id='34567',
            amount='200',
            plus_cashback_amount_per_place='100',
            flow_type='retail',
            payload={'place_id': 'place_1', 'cashback_service': 'eda'},
        )
        .using_business_rules(
            place_id='place_1',
            client_info=rules.client_info(client_id='34567'),
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
                client_id=PLUS_CLIENT_ID,
                contract_id='1',
                payload={'place_id': 'place_1', 'cashback_service': 'eda'},
                payment=common.payment(
                    payment_method='yandex_account_topup',
                    product_type='delivery',
                    product_id='grocery_plus_cashback',
                    amount='200',
                    payment_service='yaeda',
                ),
            ),
            common.billing_event(
                client_id='34567',
                contract_id='1',
                commission=common.make_commission(
                    product_type='delivery',
                    amount='100',
                    product_id='plus_cashback_retail',
                    commission_type='plus_cashback',
                ),
            ),
        )
        .run(transformer_fixtures)
    )


async def test_plus_cashback_emission_with_updates(transformer_fixtures):
    await (
        helper.TransformerRetailTest()
        .on_plus_cashback_emission(
            client_id='45678',
            amount='200',
            plus_cashback_amount_per_place='100',
            payload={'place_id': 'place_1', 'cashback_service': 'eda'},
        )
        .on_plus_cashback_emission(
            client_id='45678',
            amount='100',
            plus_cashback_amount_per_place='50',
            flow_type='retail',
            payload={'place_id': 'place_1', 'cashback_service': 'eda'},
        )
        .using_business_rules(
            place_id='place_1',
            client_info=rules.client_info(client_id='45678'),
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
                client_id=PLUS_CLIENT_ID,
                contract_id='1',
                payload={'place_id': 'place_1', 'cashback_service': 'eda'},
                payment=common.payment(
                    payment_method='yandex_account_topup',
                    product_type='delivery',
                    product_id='plus_cashback',
                    amount='200',
                    payment_service='yaeda',
                ),
            ),
            common.billing_event(
                client_id='45678',
                commission=common.make_commission(
                    product_type='delivery',
                    amount='100',
                    product_id='plus_cashback_default',
                    commission_type='plus_cashback',
                ),
            ),
            common.billing_event(
                client_id=PLUS_CLIENT_ID,
                contract_id='1',
                payload={'place_id': 'place_1', 'cashback_service': 'eda'},
                refund=common.refund(
                    payment_method='yandex_account_topup',
                    product_type='delivery',
                    product_id='plus_cashback',
                    amount='200',
                    payment_service='yaeda',
                ),
            ),
            common.billing_event(
                client_id=PLUS_CLIENT_ID,
                contract_id='1',
                payload={'place_id': 'place_1', 'cashback_service': 'eda'},
                payment=common.payment(
                    payment_method='yandex_account_topup',
                    product_type='delivery',
                    product_id='plus_cashback',
                    amount='100',
                    payment_service='yaeda',
                ),
            ),
            common.billing_event(
                client_id='45678',
                commission=common.make_commission(
                    product_type='delivery',
                    amount='-100',
                    product_id='plus_cashback_retail',
                    commission_type='plus_cashback',
                ),
            ),
            common.billing_event(
                client_id='45678',
                commission=common.make_commission(
                    product_type='delivery',
                    amount='50',
                    product_id='plus_cashback_retail',
                    commission_type='plus_cashback',
                ),
            ),
        )
        .run(transformer_fixtures)
    )


async def test_plus_cashback_emission_without_updates(transformer_fixtures):
    await (
        helper.TransformerRetailTest()
        .on_plus_cashback_emission(
            client_id='67890',
            amount='200',
            plus_cashback_amount_per_place='100',
            flow_type='retail',
            payload={'place_id': 'place_1', 'cashback_service': 'eda'},
        )
        .on_plus_cashback_emission(
            client_id='67890',
            amount='200',
            plus_cashback_amount_per_place='100',
            flow_type='retail',
            payload={'place_id': 'place_1', 'cashback_service': 'eda'},
        )
        .using_business_rules(
            place_id='place_1',
            client_info=rules.client_info(client_id='67890'),
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
                client_id=PLUS_CLIENT_ID,
                contract_id='1',
                payload={'place_id': 'place_1', 'cashback_service': 'eda'},
                payment=common.payment(
                    payment_method='yandex_account_topup',
                    product_type='delivery',
                    product_id='plus_cashback',
                    amount='200',
                    payment_service='yaeda',
                ),
            ),
            common.billing_event(
                client_id='67890',
                commission=common.make_commission(
                    product_type='delivery',
                    amount='100',
                    product_id='plus_cashback_retail',
                    commission_type='plus_cashback',
                ),
            ),
        )
        .run(transformer_fixtures)
    )


async def test_plus_cashback_emission_elder_event(transformer_fixtures):
    await (
        helper.TransformerRetailTest()
        .on_plus_cashback_emission(
            client_id='67890',
            amount='200',
            plus_cashback_amount_per_place='100',
            flow_type='retail',
            event_at=datetime.datetime(2021, 12, 15, 12, 0, 0),
            payload={'place_id': 'place_1', 'cashback_service': 'eda'},
        )
        .on_plus_cashback_emission(
            client_id='67890',
            amount='500',
            plus_cashback_amount_per_place='250',
            flow_type='retail',
            event_at=datetime.datetime(2021, 12, 15, 11, 0, 0),
            payload={'place_id': 'place_1', 'cashback_service': 'eda'},
        )
        .using_business_rules(
            place_id='place_1',
            client_info=rules.client_info(client_id='67890'),
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
                client_id=PLUS_CLIENT_ID,
                contract_id='1',
                payload={'place_id': 'place_1', 'cashback_service': 'eda'},
                payment=common.payment(
                    payment_method='yandex_account_topup',
                    product_type='delivery',
                    product_id='plus_cashback',
                    amount='200',
                    payment_service='yaeda',
                ),
            ),
            common.billing_event(
                client_id='67890',
                commission=common.make_commission(
                    product_type='delivery',
                    amount='100',
                    product_id='plus_cashback_retail',
                    commission_type='plus_cashback',
                ),
            ),
        )
        .run(transformer_fixtures)
    )


async def test_payment_update_plus_cashback(transformer_fixtures):
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


@pytest.mark.config(
    EATS_BILLING_PROCESSOR_LAVKA_FEATURES={
        'lavka_cashback_service_id_enabled': True,
    },
)
async def test_payment_update_plus_cashback_with_cashback_service(
        transformer_fixtures,
):
    await (
        helper.TransformerRetailTest()
        .on_payment_update_plus_cashback(
            client_id='90123',
            amount='100',
            payment_method='card',
            product_type='product',
            product_id='plus_cashback',
            payload={'cashback_service': 'store'},
            currency='RUB',
        )
        .using_business_rules(
            place_id='1',
            client_info=rules.client_info(client_id='90123'),
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
                client_id='90123',
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
                    'service_id': '662',
                    'country_code': 'RU',
                },
                payment=common.payment(
                    payment_method='yandex_account_withdraw',
                    product_type='delivery',
                    product_id='grocery_plus_cashback',
                    amount='100',
                    payment_service='yaeda',
                ),
            ),
        )
        .run(transformer_fixtures)
    )


@pytest.mark.config(
    EATS_BILLING_PROCESSOR_LAVKA_FEATURES={
        'lavka_cashback_service_id_enabled': True,
    },
)
async def test_payment_update_plus_cashback_with_order_nr_grocery(
        transformer_fixtures,
):
    await (
        helper.TransformerRetailTest()
        .with_order_nr('1234-grocery')
        .on_payment_update_plus_cashback(
            client_id='1230123',
            amount='100',
            payment_method='card',
            product_type='product',
            product_id='plus_cashback',
            processing_type='store',
            currency='KZT',
        )
        .using_business_rules(
            place_id='1',
            client_info=rules.client_info(client_id='1230123'),
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
                client_id='1230123',
                payment=common.payment(
                    payment_method='card',
                    product_type='product',
                    amount='100',
                    payment_service='yaeda',
                    product_id='plus_cashback',
                    currency='KZT',
                ),
            ),
            common.billing_event(
                client_id=PLUS_CLIENT_ID,
                contract_id='1',
                payload={
                    'product_type': 'product',
                    'amount': '100',
                    'cashback_service': 'lavka',
                    'has_plus': 'true',
                    'order_id': '1234-grocery',
                    'service_id': '662',
                    'country_code': 'KZ',
                },
                payment=common.payment(
                    payment_method='yandex_account_withdraw',
                    product_type='delivery',
                    product_id='grocery_plus_cashback',
                    amount='100',
                    payment_service='yaeda',
                    currency='KZT',
                ),
            ),
        )
        .run(transformer_fixtures)
    )


async def test_payment_update_plus_cashback_with_update(transformer_fixtures):
    await (
        helper.TransformerRetailTest()
        .on_payment_update_plus_cashback(
            client_id='123423',
            amount='100',
            payment_method='card',
            product_type='product',
            product_id='plus_cashback',
            currency='BYN',
        )
        .on_payment_update_plus_cashback(
            client_id='123423',
            amount='50',
            payment_method='card',
            product_type='product',
            product_id='plus_cashback',
            currency='BYN',
        )
        .using_business_rules(
            place_id='1',
            client_info=rules.client_info(client_id='123423'),
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
                client_id='123423',
                payment=common.payment(
                    payment_method='card',
                    product_type='product',
                    amount='100',
                    payment_service='yaeda',
                    product_id='plus_cashback',
                    currency='BYN',
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
                    'country_code': 'BY',
                },
                payment=common.payment(
                    payment_method='yandex_account_withdraw',
                    product_type='delivery',
                    product_id='plus_cashback',
                    amount='100',
                    payment_service='yaeda',
                    currency='BYN',
                ),
            ),
            common.billing_event(
                client_id='123423',
                refund=common.refund(
                    payment_method='card',
                    product_type='product',
                    amount='100',
                    payment_service='yaeda',
                    product_id='plus_cashback',
                    currency='BYN',
                ),
            ),
            common.billing_event(
                client_id='123423',
                payment=common.payment(
                    payment_method='card',
                    product_type='product',
                    amount='50',
                    payment_service='yaeda',
                    product_id='plus_cashback',
                    currency='BYN',
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
                    'country_code': 'BY',
                },
                refund=common.refund(
                    payment_method='yandex_account_withdraw',
                    product_type='delivery',
                    product_id='plus_cashback',
                    amount='100',
                    payment_service='yaeda',
                    currency='BYN',
                ),
            ),
            common.billing_event(
                client_id=PLUS_CLIENT_ID,
                contract_id='1',
                payload={
                    'product_type': 'product',
                    'amount': '50',
                    'cashback_service': 'eda',
                    'has_plus': 'true',
                    'order_id': '123456',
                    'service_id': '645',
                    'country_code': 'BY',
                },
                payment=common.payment(
                    payment_method='yandex_account_withdraw',
                    product_type='delivery',
                    product_id='plus_cashback',
                    amount='50',
                    payment_service='yaeda',
                    currency='BYN',
                ),
            ),
        )
        .run(transformer_fixtures)
    )


async def test_payment_update_plus_cashback_refund(transformer_fixtures):
    await (
        helper.TransformerRetailTest()
        .on_payment_update_plus_cashback(
            client_id='123423',
            amount='0',
            payment_method='card',
            product_type='product',
            product_id='plus_cashback',
            currency='BYN',
            event_at=datetime.datetime(2021, 12, 27, 12, 0, 0),
        )
        .on_payment_update_plus_cashback(
            client_id='123423',
            amount='100',
            payment_method='card',
            product_type='product',
            product_id='plus_cashback',
            currency='BYN',
            event_at=datetime.datetime(2021, 12, 27, 11, 0, 0),
        )
        .using_business_rules(
            place_id='1',
            client_info=rules.client_info(client_id='123423'),
            commission=rules.make_commission(
                commission_type='place_delivery',
                params=rules.simple_commission(
                    commission='10',
                    acquiring_commission='0',
                    fix_commission='10',
                ),
            ),
        )
        .no_stq_call_expected()
        .run(transformer_fixtures)
    )


async def test_payment_update_plus_cashback_refund_2_runs(
        transformer_fixtures,
):
    await (
        helper.TransformerRetailTest()
        .on_payment_update_plus_cashback(
            client_id='123423',
            amount='0',
            payment_method='card',
            product_type='product',
            product_id='plus_cashback',
            currency='BYN',
            event_at=datetime.datetime(2021, 12, 27, 12, 0, 0),
        )
        .using_business_rules(
            place_id='1',
            client_info=rules.client_info(client_id='123423'),
            commission=rules.make_commission(
                commission_type='place_delivery',
                params=rules.simple_commission(
                    commission='10',
                    acquiring_commission='0',
                    fix_commission='10',
                ),
            ),
        )
        .no_stq_call_expected()
        .run(transformer_fixtures)
    )

    await (
        helper.TransformerRetailTest()
        .on_payment_update_plus_cashback(
            client_id='123423',
            amount='100',
            payment_method='card',
            product_type='product',
            product_id='plus_cashback',
            currency='BYN',
            event_at=datetime.datetime(2021, 12, 27, 11, 0, 0),
        )
        .using_business_rules(
            place_id='1',
            client_id='123423',
            commission=rules.make_commission(
                commission_type='place_delivery',
                params=rules.simple_commission(
                    commission='10',
                    acquiring_commission='0',
                    fix_commission='10',
                ),
            ),
        )
        .no_stq_call_expected()
        .run(transformer_fixtures)
    )


async def test_payment_update_plus_cashback_without_update(
        transformer_fixtures,
):
    await (
        helper.TransformerRetailTest()
        .on_payment_update_plus_cashback(
            client_id='234562',
            amount='100',
            payment_method='card',
            product_type='product',
            product_id='plus_cashback',
        )
        .on_payment_update_plus_cashback(
            client_id='234562',
            amount='100',
            payment_method='card',
            product_type='product',
            product_id='plus_cashback',
        )
        .using_business_rules(
            place_id='1',
            client_info=rules.client_info(client_id='234562'),
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
                client_id='234562',
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
                payload={
                    'product_type': 'product',
                    'amount': '100',
                    'cashback_service': 'eda',
                    'has_plus': 'true',
                    'order_id': '123456',
                    'service_id': '645',
                    'country_code': 'RU',
                },
                contract_id='1',
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


async def test_commission_update_with_payment(transformer_fixtures):
    await (
        helper.TransformerRetailTest()
        .on_payment_received(
            counteragent_id='courier_1',
            client_id='123456',
            product_type='delivery',
            amount='200',
        )
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
        .using_business_rules(
            place_id='place_1',
            client_info=rules.client_info(client_id='123456'),
            commission=rules.make_commission(
                commission_type='place_delivery',
                params=rules.simple_commission(
                    commission='15',
                    acquiring_commission='5',
                    fix_commission='3',
                ),
            ),
        )
        .using_business_rules(
            courier_id='courier_1',
            client_info=rules.client_info(client_id='123456'),
            commission=rules.make_commission(
                commission_type='courier_delivery',
                params=rules.simple_commission(
                    commission='15',
                    acquiring_commission='5',
                    fix_commission='3',
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
                    product_type='delivery', amount='43',
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
                    amount='200',
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
        )
        .run(transformer_fixtures)
    )
