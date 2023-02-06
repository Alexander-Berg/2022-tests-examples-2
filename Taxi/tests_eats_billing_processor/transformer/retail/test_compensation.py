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
from tests_eats_billing_processor.transformer.retail import helper


async def test_compensation(transformer_fixtures):
    await (
        helper.TransformerRetailTest()
        .on_compensation(
            picker_id='picker_1',
            courier_id='courier_1',
            items=[
                common.make_compensation_item(
                    product_type='retail', amount='200',
                ),
                common.make_compensation_item(
                    product_type='delivery', amount='100',
                ),
            ],
        )
        .using_business_rules(
            picker_id='picker_1',
            client_info=rules.client_info(
                client_id='123456', employment='self_employed',
            ),
        )
        .using_business_rules(
            courier_id='courier_1',
            client_info=rules.client_info(
                client_id='23456', employment='courier_service',
            ),
        )
        .expect(
            common.billing_event(
                client_info=rules.client_info(
                    client_id='123456', employment='self_employed',
                ),
                payment=common.payment(
                    payment_method='our_refund',
                    product_type='retail',
                    amount='200',
                    payment_service='yaeda',
                ),
            ),
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
        helper.TransformerRetailTest()
        .on_compensation(
            place_id='place_1',
            picker_id='picker_1',
            service_fee_amount='12.12',
            currency=currency,
            items=[
                common.make_compensation_item(
                    product_type='retail', amount='200',
                ),
            ],
        )
        .using_business_rules(
            picker_id='picker_1',
            client_info=rules.client_info(
                client_id='123456', employment='self_employed',
            ),
        )
        .using_business_rules(
            place_id='place_1',
            client_info=rules.client_info(client_id='654321'),
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
                    amount='-12.12',
                    product_id='service_fee__001',
                    commission_type='service_fee',
                    currency=currency,
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(
                    client_id='123456', employment='self_employed',
                ),
                payment=common.payment(
                    payment_method='our_refund',
                    product_type='retail',
                    amount='200',
                    payment_service='yaeda',
                    currency=currency,
                ),
            ),
        )
        .run(transformer_fixtures)
    )


async def test_compensation_with_discounts(transformer_fixtures):
    await (
        helper.TransformerRetailTest()
        .on_compensation(
            picker_id='picker_2',
            courier_id='courier_2',
            items=[
                common.make_compensation_item(
                    product_type='retail',
                    amount='200',
                    discounts=[
                        common.make_compensation_discount(
                            discount_type='compensation', amount='50',
                        ),
                        common.make_compensation_discount(
                            discount_type='sorrycode', amount='150',
                        ),
                        common.make_compensation_discount(
                            discount_type='employee', amount='250',
                        ),
                        common.make_compensation_discount(
                            discount_type='paid', amount='350',
                        ),
                        common.make_compensation_discount(
                            discount_type='corporate', amount='450',
                        ),
                        common.make_compensation_discount(
                            discount_type='corporate_all', amount='550',
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
            picker_id='picker_2',
            client_info=rules.client_info(
                client_id='23456', employment='courier_service',
            ),
            commission=rules.make_commission(
                commission_type='picker_delivery',
                params=rules.simple_commission(
                    commission='10',
                    acquiring_commission='10',
                    fix_commission='0',
                ),
            ),
        )
        .using_business_rules(
            courier_id='courier_2',
            client_info=rules.client_info(
                client_id='34567', employment='self_employed',
            ),
            commission=rules.make_commission(
                commission_type='courier_delivery',
                params=rules.simple_commission(
                    commission='20',
                    acquiring_commission='20',
                    fix_commission='0',
                ),
            ),
        )
        .expect(
            common.billing_event(
                client_info=rules.client_info(
                    client_id='23456', employment='courier_service',
                ),
                payment=common.payment(
                    payment_method='our_refund',
                    product_type='retail',
                    amount='200',
                    payment_service='yaeda',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(
                    client_id='23456', employment='courier_service',
                ),
                refund=common.refund(
                    payment_method='compensation_promocode',
                    product_type='retail',
                    amount='50',
                    payment_service='yaeda',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(
                    client_id='23456', employment='courier_service',
                ),
                payment=common.payment(
                    payment_method='our_refund',
                    product_type='retail',
                    amount='50',
                    payment_service='yaeda',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(
                    client_id='23456', employment='courier_service',
                ),
                refund=common.refund(
                    payment_method='compensation_promocode',
                    product_type='retail',
                    amount='150',
                    payment_service='yaeda',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(
                    client_id='23456', employment='courier_service',
                ),
                payment=common.payment(
                    payment_method='our_refund',
                    product_type='retail',
                    amount='150',
                    payment_service='yaeda',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(
                    client_id='23456', employment='courier_service',
                ),
                refund=common.refund(
                    payment_method='employee_PC',
                    product_type='retail',
                    amount='250',
                    payment_service='yaeda',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(
                    client_id='23456', employment='courier_service',
                ),
                payment=common.payment(
                    payment_method='our_refund',
                    product_type='retail',
                    amount='250',
                    payment_service='yaeda',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(
                    client_id='23456', employment='courier_service',
                ),
                refund=common.refund(
                    payment_method='paid_PC',
                    product_type='retail',
                    amount='350',
                    payment_service='yaeda',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(
                    client_id='23456', employment='courier_service',
                ),
                payment=common.payment(
                    payment_method='our_refund',
                    product_type='retail',
                    amount='350',
                    payment_service='yaeda',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(
                    client_id='23456', employment='courier_service',
                ),
                refund=common.refund(
                    payment_method='corporate',
                    product_type='retail',
                    amount='450',
                    payment_service='yaeda',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(
                    client_id='23456', employment='courier_service',
                ),
                payment=common.payment(
                    payment_method='our_refund',
                    product_type='retail',
                    amount='450',
                    payment_service='yaeda',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(
                    client_id='23456', employment='courier_service',
                ),
                refund=common.refund(
                    payment_method='corporate',
                    product_type='retail',
                    amount='550',
                    payment_service='yaeda',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(
                    client_id='23456', employment='courier_service',
                ),
                payment=common.payment(
                    payment_method='our_refund',
                    product_type='retail',
                    amount='550',
                    payment_service='yaeda',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(
                    client_id='34567', employment='self_employed',
                ),
                refund=common.refund(
                    payment_method='marketing',
                    product_type='delivery',
                    amount='20',
                    payment_service='yaeda',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(
                    client_id='34567', employment='self_employed',
                ),
                commission=common.make_commission(
                    product_type='delivery', amount='-8',
                ),
            ),
        )
        .run(transformer_fixtures)
    )
