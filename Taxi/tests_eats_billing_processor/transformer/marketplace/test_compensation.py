# pylint: disable=import-only-modules
import pytest

from tests_eats_billing_processor import rules
from tests_eats_billing_processor.transformer import common
from tests_eats_billing_processor.transformer.helper import (
    SERVICE_FEE_CLIENT_ID_BYN,
)
from tests_eats_billing_processor.transformer.helper import (
    SERVICE_FEE_CLIENT_ID_KZT,
)
from tests_eats_billing_processor.transformer.helper import (
    SERVICE_FEE_CLIENT_ID_RUB,
)
from tests_eats_billing_processor.transformer.helper import (
    SERVICE_FEE_CONTRACT_ID_BYN,
)
from tests_eats_billing_processor.transformer.helper import (
    SERVICE_FEE_CONTRACT_ID_KZT,
)
from tests_eats_billing_processor.transformer.helper import (
    SERVICE_FEE_CONTRACT_ID_RUB,
)
from tests_eats_billing_processor.transformer.marketplace import helper


async def test_compensation(transformer_fixtures):
    await (
        helper.TransformerMarketplaceTest()
        .on_compensation(
            is_place_fault=True,
            place_id='place_1',
            items=[
                common.make_compensation_item(
                    product_type='product', amount='200',
                ),
                common.make_compensation_item(
                    product_type='delivery', amount='100',
                ),
            ],
        )
        .using_business_rules(
            place_id='place_1',
            client_info=rules.client_info(client_id='123456'),
            fine=rules.make_fine(
                business_type='restaurant',
                delivery_type='marketplace',
                reason='return',
                params=rules.simple_fine(fine='10', fix_fine='10'),
            ),
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
                client_info=rules.client_info(client_id='123456'),
                refund=common.refund(
                    payment_method='withholding',
                    product_type='product',
                    currency='RUB',
                    amount='30',
                    payment_service='yaeda',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(client_id='123456'),
                payment=common.payment(
                    payment_method='our_refund',
                    product_type='product',
                    currency='RUB',
                    amount='200',
                    payment_service='yaeda',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(client_id='123456'),
                payment=common.payment(
                    payment_method='our_refund',
                    product_type='delivery',
                    currency='RUB',
                    amount='100',
                    payment_service='yaeda',
                ),
            ),
        )
        .expect_accounting(
            client_id='123456', amount='30.00', account_type='fine',
        )
        .expect_fine(
            client_id='123456',
            fine_reason='refund',
            actual_amount='30.00',
            calculated_amount='30.00',
        )
        .run(transformer_fixtures)
    )


@pytest.mark.parametrize(
    'currency, client_id, contract_id, mvp, country_code',
    [
        pytest.param(
            'RUB',
            SERVICE_FEE_CLIENT_ID_RUB,
            SERVICE_FEE_CONTRACT_ID_RUB,
            'MSKc',
            'RU',
        ),
        pytest.param(
            'KZT',
            SERVICE_FEE_CLIENT_ID_KZT,
            SERVICE_FEE_CONTRACT_ID_KZT,
            'AST',
            'KZ',
        ),
        pytest.param(
            'BYN',
            SERVICE_FEE_CLIENT_ID_BYN,
            SERVICE_FEE_CONTRACT_ID_BYN,
            'MNKc',
            'BY',
        ),
    ],
)
@pytest.mark.now('2021-11-25T09:00:00+00:00')
async def test_compensation_service_fee(
        transformer_fixtures,
        currency,
        client_id,
        contract_id,
        mvp,
        country_code,
):
    await (
        helper.TransformerMarketplaceTest()
        .on_compensation(
            is_place_fault=True,
            place_id='place_1',
            service_fee_amount='100',
            currency=currency,
            items=[
                common.make_compensation_item(
                    product_type='delivery', amount='100',
                ),
            ],
        )
        .using_business_rules(
            place_id='place_1',
            client_info=rules.client_info(client_id='123456'),
            fine=rules.make_fine(
                rule_id='rule_1',
                business_type='restaurant',
                delivery_type='marketplace',
                reason='return',
                params=rules.simple_fine(fine='10', fix_fine='10'),
            ),
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
                transaction_date='2021-11-25T06:00:00+00:00',
                client_info=rules.client_info(
                    client_id=client_id,
                    contract_id=contract_id,
                    mvp=mvp,
                    country_code=country_code,
                ),
                commission=common.make_commission(
                    product_type='service_fee',
                    amount='-100',
                    product_id='service_fee__001',
                    commission_type='service_fee',
                    currency=currency,
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(client_id='123456'),
                payment=common.payment(
                    payment_method='our_refund',
                    product_type='delivery',
                    currency=currency,
                    amount='100',
                    payment_service='yaeda',
                ),
            ),
        )
        .run(transformer_fixtures)
    )


async def test_compensation_with_discounts(transformer_fixtures):
    await (
        helper.TransformerMarketplaceTest()
        .on_compensation(
            is_place_fault=True,
            place_id='place_2',
            items=[
                common.make_compensation_item(
                    product_type='product',
                    amount='200',
                    discounts=[
                        common.make_compensation_discount(
                            discount_type='compensation', amount='50',
                        ),
                    ],
                ),
                common.make_compensation_item(
                    product_type='delivery',
                    amount='100',
                    discounts=[
                        common.make_compensation_discount(
                            discount_type='marketing', amount='20',
                        ),
                    ],
                ),
            ],
        )
        .using_business_rules(
            place_id='place_2',
            client_info=rules.client_info(client_id='23456'),
            fine=rules.make_fine(
                business_type='restaurant',
                delivery_type='marketplace',
                reason='return',
                params=rules.simple_fine(
                    fine='10', fix_fine='10', min_fine='0',
                ),
            ),
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
                client_info=rules.client_info(client_id='23456'),
                refund=common.refund(
                    payment_method='withholding',
                    product_type='product',
                    amount='35',
                    payment_service='yaeda',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(client_id='23456'),
                payment=common.payment(
                    payment_method='our_refund',
                    product_type='product',
                    amount='200',
                    payment_service='yaeda',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(client_id='23456'),
                refund=common.refund(
                    payment_method='compensation_promocode',
                    product_type='product',
                    amount='50',
                    payment_service='yaeda',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(client_id='23456'),
                payment=common.payment(
                    payment_method='our_refund',
                    product_type='product',
                    amount='50',
                    payment_service='yaeda',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(client_id='23456'),
                payment=common.payment(
                    payment_method='our_refund',
                    product_type='delivery',
                    amount='100',
                    payment_service='yaeda',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(client_id='23456'),
                refund=common.refund(
                    payment_method='marketing',
                    product_type='delivery',
                    amount='20',
                    payment_service='yaeda',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(client_id='23456'),
                payment=common.payment(
                    payment_method='our_refund',
                    product_type='delivery',
                    amount='20',
                    payment_service='yaeda',
                ),
            ),
        )
        .expect_accounting(
            client_id='23456', amount='35.00', account_type='fine',
        )
        .expect_fine(
            client_id='23456',
            fine_reason='refund',
            actual_amount='35.00',
            calculated_amount='35.00',
        )
        .run(transformer_fixtures)
    )


async def test_compensation_with_discounts_no_fine(transformer_fixtures):
    await (
        helper.TransformerMarketplaceTest()
        .on_compensation(
            place_id='place_3',
            items=[
                common.make_compensation_item(
                    product_type='product',
                    amount='200',
                    discounts=[
                        common.make_compensation_discount(
                            discount_type='compensation', amount='50',
                        ),
                    ],
                ),
                common.make_compensation_item(
                    product_type='delivery',
                    amount='100',
                    discounts=[
                        common.make_compensation_discount(
                            discount_type='marketing', amount='20',
                        ),
                    ],
                ),
            ],
        )
        .using_business_rules(
            place_id='place_3',
            client_info=rules.client_info(client_id='34567'),
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
                client_info=rules.client_info(client_id='34567'),
                payment=common.payment(
                    payment_method='our_refund',
                    product_type='product',
                    amount='200',
                    payment_service='yaeda',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(client_id='34567'),
                refund=common.refund(
                    payment_method='compensation_promocode',
                    product_type='product',
                    amount='50',
                    payment_service='yaeda',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(client_id='34567'),
                payment=common.payment(
                    payment_method='our_refund',
                    product_type='product',
                    amount='50',
                    payment_service='yaeda',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(client_id='34567'),
                payment=common.payment(
                    payment_method='our_refund',
                    product_type='delivery',
                    amount='100',
                    payment_service='yaeda',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(client_id='34567'),
                refund=common.refund(
                    payment_method='marketing',
                    product_type='delivery',
                    amount='20',
                    payment_service='yaeda',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(client_id='34567'),
                payment=common.payment(
                    product_type='delivery',
                    amount='20',
                    payment_method='our_refund',
                    payment_service='yaeda',
                ),
            ),
        )
        .run(transformer_fixtures)
    )


async def test_weekly_payment(transformer_fixtures):
    await (
        helper.TransformerMarketplaceTest()
        .on_compensation(
            is_place_fault=True,
            place_id='place_1',
            items=[
                common.make_compensation_item(
                    product_type='product',
                    amount='100',
                    discounts=[
                        common.make_compensation_discount(
                            discount_type='marketing', amount='20',
                        ),
                    ],
                ),
            ],
        )
        .using_business_rules(
            place_id='place_1',
            client_info=rules.client_info(client_id='123456'),
            fine=rules.make_fine(
                business_type='restaurant',
                delivery_type='marketplace',
                reason='return',
                params=rules.simple_fine(fine='10', fix_fine='10'),
            ),
            commission=rules.make_commission(
                commission_type='place_delivery',
                params=rules.simple_commission(
                    commission='10',
                    acquiring_commission='0',
                    fix_commission='10',
                ),
                billing_frequency='weekly',
            ),
        )
        .expect(
            common.billing_event(
                client_info=rules.client_info(client_id='123456'),
                refund=common.refund(
                    payment_method='withholding',
                    product_type='product_weekly',
                    currency='RUB',
                    amount='22',
                    payment_service='yaeda',
                    product_id='product/native_weekly',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(client_id='123456'),
                payment=common.payment(
                    payment_method='our_refund',
                    product_type='product_weekly',
                    currency='RUB',
                    amount='100',
                    payment_service='yaeda',
                    product_id='product/native_weekly',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(client_id='123456'),
                refund=common.refund(
                    payment_method='marketing',
                    product_type='product_weekly',
                    amount='20',
                    payment_service='yaeda',
                    product_id='product/native_weekly',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(client_id='123456'),
                payment=common.payment(
                    payment_method='our_refund',
                    product_type='product_weekly',
                    currency='RUB',
                    amount='20',
                    payment_service='yaeda',
                    product_id='product/native_weekly',
                ),
            ),
        )
        .expect_accounting(
            client_id='123456', amount='22.00', account_type='fine',
        )
        .expect_fine(
            client_id='123456',
            fine_reason='refund',
            actual_amount='22.00',
            calculated_amount='22.00',
        )
        .run(transformer_fixtures)
    )