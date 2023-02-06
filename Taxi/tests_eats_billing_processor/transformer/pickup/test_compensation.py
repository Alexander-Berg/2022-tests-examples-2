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
from tests_eats_billing_processor.transformer.pickup import helper


async def test_compensation(transformer_fixtures):
    await (
        helper.TransformerPickupTest()
        .on_compensation(
            is_place_fault=True,
            place_id='place_1',
            items=[
                common.make_compensation_item(
                    product_type='product', amount='100',
                ),
            ],
        )
        .using_business_rules(
            place_id='place_1',
            client_info=rules.client_info(client_id='123456'),
            fine=rules.make_fine(
                business_type='restaurant',
                delivery_type='pickup',
                reason='return',
                params=rules.simple_fine(fine='10', fix_fine='10'),
            ),
            commission=rules.make_commission(
                commission_type='pickup',
                params=rules.simple_commission(
                    commission='10',
                    acquiring_commission='5',
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
                    amount='20',
                    payment_service='yaeda',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(client_id='123456'),
                payment=common.payment(
                    payment_method='our_refund',
                    product_type='product',
                    currency='RUB',
                    amount='100',
                    payment_service='yaeda',
                ),
            ),
        )
        .expect_accounting(
            client_id='123456', amount='20.00', account_type='fine',
        )
        .expect_fine(
            client_id='123456',
            fine_reason='refund',
            actual_amount='20.00',
            calculated_amount='20.00',
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
        helper.TransformerPickupTest()
        .on_compensation(
            is_place_fault=True,
            place_id='place_1',
            service_fee_amount='100.13',
            currency=currency,
            items=[
                common.make_compensation_item(
                    product_type='product', amount='100',
                ),
            ],
        )
        .using_business_rules(
            place_id='place_1',
            client_info=rules.client_info(client_id='123456'),
            fine=rules.make_fine(
                business_type='restaurant',
                delivery_type='pickup',
                reason='return',
                params=rules.simple_fine(fine='10', fix_fine='10'),
            ),
            commission=rules.make_commission(
                commission_type='pickup',
                params=rules.simple_commission(
                    commission='10',
                    acquiring_commission='5',
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
                    currency=currency,
                    amount='-100.13',
                    product_id='service_fee__001',
                    commission_type='service_fee',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(client_id='123456'),
                refund=common.refund(
                    payment_method='withholding',
                    product_type='product',
                    currency=currency,
                    amount='20',
                    payment_service='yaeda',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(client_id='123456'),
                payment=common.payment(
                    payment_method='our_refund',
                    product_type='product',
                    currency=currency,
                    amount='100',
                    payment_service='yaeda',
                ),
            ),
        )
        .expect_accounting(
            client_id='123456', amount='20.00', account_type='fine',
        )
        .expect_fine(
            client_id='123456',
            fine_reason='refund',
            actual_amount='20.00',
            calculated_amount='20.00',
            currency=currency,
        )
        .run(transformer_fixtures)
    )


async def test_compensation_with_discounts(transformer_fixtures):
    await (
        helper.TransformerPickupTest()
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
            ],
        )
        .using_business_rules(
            place_id='place_2',
            client_info=rules.client_info(client_id='23456'),
            fine=rules.make_fine(
                business_type='restaurant',
                delivery_type='pickup',
                reason='return',
                params=rules.simple_fine(
                    fine='10', fix_fine='10', min_fine='0',
                ),
            ),
            commission=rules.make_commission(
                commission_type='pickup',
                params=rules.simple_commission(
                    commission='10',
                    acquiring_commission='5',
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
        helper.TransformerPickupTest()
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
            ],
        )
        .using_business_rules(
            place_id='place_3',
            client_info=rules.client_info(client_id='23456'),
            commission=rules.make_commission(
                commission_type='pickup',
                params=rules.simple_commission(
                    commission='10',
                    acquiring_commission='5',
                    fix_commission='10',
                ),
            ),
        )
        .expect(
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
        )
        .run(transformer_fixtures)
    )
