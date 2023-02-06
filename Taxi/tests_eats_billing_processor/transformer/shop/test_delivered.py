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
from tests_eats_billing_processor.transformer.shop import helper


async def test_happy_path_with_products(transformer_fixtures):
    await (
        helper.TransformerShopTest()
        .on_order_delivered(
            place_id='place_1',
            courier_id='courier_1',
            products=[
                common.make_marketing_payment(
                    marketing_type='marketing',
                    amount='100',
                    product_type='product',
                ),
                common.make_marketing_payment(
                    marketing_type='marketing_promocode',
                    amount='200',
                    product_type='product',
                ),
                common.make_marketing_payment(
                    marketing_type='compensation',
                    amount='400',
                    product_type='delivery',
                ),
            ],
            flow_type='native',
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
        .using_business_rules(
            courier_id='courier_1',
            client_info=rules.client_info(client_id='23456'),
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
                client_info=rules.client_info(client_id='123456'),
                payment=common.payment(
                    payment_method='marketing',
                    payment_service='yaeda',
                    product_type='product',
                    amount='100',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(client_id='123456'),
                payment=common.payment(
                    payment_method='marketing_promocode',
                    payment_service='yaeda',
                    product_type='product',
                    amount='200',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(client_id='23456'),
                payment=common.payment(
                    payment_method='compensation_promocode',
                    payment_service='yaeda',
                    product_type='delivery',
                    amount='400',
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
async def test_happy_path_service_fee(
        transformer_fixtures,
        currency,
        client_id,
        contract_id,
        mvp,
        country_code,
):
    await (
        helper.TransformerShopTest()
        .on_order_delivered(
            place_id='place_1',
            courier_id='courier_1',
            service_fee_amount='100',
            currency=currency,
            products=[
                common.make_marketing_payment(
                    marketing_type='marketing',
                    amount='100',
                    product_type='retail',
                ),
            ],
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
        .using_business_rules(
            courier_id='courier_1',
            client_info=rules.client_info(client_id='23456'),
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
                transaction_date='2021-07-20T12:35:00+00:00',
                client_info=rules.client_info(
                    client_id=client_id, contract_id=contract_id, mvp=mvp,
                ),
                commission=common.make_commission(
                    product_type='service_fee',
                    amount='100',
                    product_id='service_fee__001',
                    commission_type='service_fee',
                    currency=currency,
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(client_id='123456'),
                payment=common.payment(
                    payment_method='marketing',
                    payment_service='yaeda',
                    product_type='retail',
                    amount='100',
                    currency=currency,
                ),
            ),
        )
        .run(transformer_fixtures)
    )
