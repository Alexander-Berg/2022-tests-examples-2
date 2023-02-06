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


async def test_happy_path_with_products(transformer_fixtures):
    await (
        helper.TransformerRetailTest()
        .on_order_cancelled(
            picker_id='picker_1',
            amount_picker_paid='1000',
            products=[
                common.make_reimbursement_payment(
                    payment_type='marketing',
                    amount='1000',
                    product_type='assembly',
                ),
                common.make_reimbursement_payment(
                    payment_type='our_refund',
                    amount='200',
                    product_type='retail',
                ),
            ],
        )
        .using_business_rules(
            picker_id='picker_1',
            client_info=rules.client_info(
                client_id='123456', employment='courier_service',
            ),
            commission=rules.make_commission(
                commission_type='picker_delivery',
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
                    client_id='123456', employment='courier_service',
                ),
                payment=common.payment(
                    payment_method='marketing',
                    payment_service='yaeda',
                    product_type='assembly',
                    amount='1000',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(
                    client_id='123456', employment='courier_service',
                ),
                external_payment_id=0,
                commission=common.make_commission(
                    product_type='assembly', amount='210',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(
                    client_id='123456', employment='courier_service',
                ),
                payment=common.payment(
                    payment_method='our_refund',
                    payment_service='yaeda',
                    product_type='retail',
                    amount='200',
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
        helper.TransformerRetailTest()
        .on_order_cancelled(
            picker_id='picker_1',
            service_fee_amount='100',
            currency=currency,
            products=[
                common.make_marketing_payment(
                    marketing_type='marketing',
                    amount='100',
                    product_type='product',
                ),
            ],
        )
        .using_business_rules(
            picker_id='picker_1',
            client_info=rules.client_info(client_id='123456'),
        )
        .expect(
            common.billing_event(
                client_info=rules.client_info(
                    client_id=client_id,
                    contract_id=contract_id,
                    mvp=mvp,
                    country_code=country_code,
                ),
                commission=common.make_commission(
                    product_type='service_fee',
                    amount='100',
                    product_id='service_fee__001',
                    commission_type='service_fee',
                    currency=currency,
                ),
            ),
        )
        .run(transformer_fixtures)
    )


async def test_happy_path_with_no_products(transformer_fixtures):
    await (
        helper.TransformerRetailTest()
        .on_order_cancelled(picker_id='picker_1', products=[])
        .no_stq_call_expected()
        .run(transformer_fixtures)
    )


async def test_happy_path_with_payment_expected(transformer_fixtures):
    await (
        helper.TransformerRetailTest()
        .on_order_cancelled(
            picker_id='picker_2',
            amount_picker_paid='1000',
            is_payment_expected=True,
            products=[
                common.make_reimbursement_payment(
                    payment_type='marketing',
                    amount='1000',
                    product_type='assembly',
                ),
                common.make_reimbursement_payment(
                    payment_type='payment_not_received',
                    amount='200',
                    product_type='retail',
                ),
            ],
        )
        .using_business_rules(
            picker_id='picker_2',
            client_info=rules.client_info(
                client_id='23456', employment='self_employed',
            ),
            commission=rules.make_commission(
                commission_type='picker_delivery',
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
                    client_id='23456', employment='self_employed',
                ),
                payment=common.payment(
                    payment_method='marketing',
                    payment_service='yaeda',
                    product_type='assembly',
                    amount='1000',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(
                    client_id='23456', employment='self_employed',
                ),
                external_payment_id=0,
                commission=common.make_commission(
                    product_type='assembly', amount='210',
                ),
            ),
        )
        .run(transformer_fixtures)
    )


async def test_happy_path_with_no_reimbursement(transformer_fixtures):
    await (
        helper.TransformerRetailTest()
        .on_order_cancelled(
            picker_id='picker_3',
            is_reimbursement_required=False,
            products=[
                common.make_reimbursement_payment(
                    payment_type='marketing',
                    amount='1000',
                    product_type='product',
                ),
                common.make_reimbursement_payment(
                    payment_type='our_refund',
                    amount='200',
                    product_type='retail',
                ),
            ],
        )
        .using_business_rules(
            picker_id='picker_3',
            client_info=rules.client_info(client_id='34567'),
        )
        .no_stq_call_expected()
        .run(transformer_fixtures)
    )


async def test_no_picker_id_incorrect_data_happy_path(transformer_fixtures):
    await (
        helper.TransformerRetailTest()
        .on_order_cancelled(
            is_reimbursement_required=False,
            products=[
                common.make_reimbursement_payment(
                    payment_type='invalid_type',
                    amount='1000',
                    product_type='invalid_product_type',
                ),
                common.make_reimbursement_payment(
                    payment_type='invalid_type2',
                    amount='200',
                    product_type='invalid_product_type',
                ),
            ],
        )
        .no_stq_call_expected()
        .run(transformer_fixtures)
    )


async def test_amount_picker_paid_zero(transformer_fixtures):
    await (
        helper.TransformerRetailTest()
        .on_order_cancelled(
            picker_id='picker_2',
            amount_picker_paid='0',
            products=[
                common.make_reimbursement_payment(
                    payment_type='marketing',
                    amount='1000',
                    product_type='product',
                ),
            ],
        )
        .no_stq_call_expected()
        .run(transformer_fixtures)
    )
