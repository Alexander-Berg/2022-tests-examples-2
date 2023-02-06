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
        .on_order_cancelled(
            place_id='place_1',
            courier_id='courier_1',
            is_reimbursement_required=True,
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
            place_id='place_1',
            client_info=rules.client_info(client_id='123456'),
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
                payment=common.payment(
                    payment_method='marketing',
                    payment_service='yaeda',
                    product_type='product',
                    amount='1000',
                ),
            ),
        )
        .expect_accounting(
            client_id='123456', amount='1000.00', account_type='gmv',
        )
        .run(transformer_fixtures)
    )


async def test_happy_path_with_products_place_fault(transformer_fixtures):
    await (
        helper.TransformerShopTest()
        .on_order_cancelled(
            is_place_fault=True,
            place_id='place_1',
            courier_id='courier_1',
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
                    product_type='product',
                ),
            ],
        )
        .using_business_rules(
            place_id='place_1',
            client_info=rules.client_info(client_id='123456'),
            fine=rules.make_fine(
                business_type='shop',
                delivery_type='native',
                reason='cancellation',
                params=rules.simple_fine(fine='10', fix_fine='10'),
            ),
            commission=rules.make_commission(
                commission_type='place_delivery',
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
                commission=common.make_commission(
                    product_type='product',
                    product_id='product__002',
                    amount='29',
                    commission_type='goods',
                ),
            ),
        )
        .expect_fine(
            client_id='123456',
            fine_reason='cancel',
            actual_amount='29.00',
            calculated_amount='29.00',
        )
        .expect_accounting(
            client_id='123456', amount='1200.00', account_type='gmv',
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
async def test_happy_path_with_service_fee(
        transformer_fixtures,
        currency,
        client_id,
        contract_id,
        mvp,
        country_code,
):
    await (
        helper.TransformerShopTest()
        .on_order_cancelled(
            place_id='place_1',
            courier_id='courier_1',
            is_reimbursement_required=True,
            service_fee_amount='50',
            currency=currency,
            products=[
                common.make_reimbursement_payment(
                    payment_type='marketing',
                    amount='1000',
                    product_type='product',
                ),
                common.make_reimbursement_payment(
                    payment_type='our_refund',
                    amount='200',
                    product_type='delivery',
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
                    acquiring_commission='0',
                    fix_commission='10',
                ),
            ),
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
                    amount='50',
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
                    product_type='product',
                    amount='1000',
                    currency=currency,
                ),
            ),
        )
        .expect_accounting(
            client_id='123456', amount='1000.00', account_type='gmv',
        )
        .run(transformer_fixtures)
    )


async def test_happy_path_with_no_products(transformer_fixtures):
    await (
        helper.TransformerShopTest()
        .on_order_cancelled(place_id='place_1', products=[])
        .no_stq_call_expected()
        .run(transformer_fixtures)
    )


async def test_happy_path_with_payment_expected(transformer_fixtures):
    await (
        helper.TransformerShopTest()
        .on_order_cancelled(
            place_id='place_2',
            is_payment_expected=True,
            is_reimbursement_required=True,
            products=[
                common.make_reimbursement_payment(
                    payment_type='marketing',
                    amount='1000',
                    product_type='product',
                ),
                common.make_reimbursement_payment(
                    payment_type='payment_not_received',
                    amount='200',
                    product_type='product',
                ),
            ],
        )
        .using_business_rules(
            place_id='place_2',
            client_info=rules.client_info(client_id='23456'),
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
                payment=common.payment(
                    payment_method='marketing',
                    payment_service='yaeda',
                    product_type='product',
                    amount='1000',
                ),
            ),
        )
        .expect_accounting(
            client_id='23456', amount='1200.00', account_type='gmv',
        )
        .run(transformer_fixtures)
    )


async def test_happy_path_with_no_reimbursement(transformer_fixtures):
    await (
        helper.TransformerShopTest()
        .on_order_cancelled(
            place_id='place_3',
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
            place_id='place_3',
            client_info=rules.client_info(client_id='34567'),
        )
        .expect_accounting(
            client_id='34567', amount='1000.00', account_type='gmv',
        )
        .no_stq_call_expected()
        .run(transformer_fixtures)
    )


async def test_no_place_id_incorrect_data_happy_path(transformer_fixtures):
    await (
        helper.TransformerShopTest()
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


async def test_happy_path_many_products(transformer_fixtures):
    await (
        helper.TransformerShopTest()
        .on_order_cancelled(
            is_place_fault=True,
            place_id='place_1',
            products=[
                common.make_reimbursement_payment(
                    payment_type='our_refund',
                    amount='200',
                    product_type='product',
                ),
                common.make_reimbursement_payment(
                    payment_type='our_refund',
                    amount='500',
                    product_type='product',
                ),
                common.make_reimbursement_payment(
                    payment_type='our_refund',
                    amount='1000',
                    product_type='product',
                ),
                common.make_reimbursement_payment(
                    payment_type='our_refund',
                    amount='100',
                    product_type='delivery',
                ),
            ],
        )
        .using_business_rules(
            place_id='place_1',
            client_info=rules.client_info(client_id='123456'),
            fine=rules.make_fine(
                business_type='shop',
                delivery_type='native',
                reason='cancellation',
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
                commission=common.make_commission(
                    product_type='product',
                    product_id='product__002',
                    amount='28',
                    commission_type='goods',
                ),
            ),
        )
        .expect_accounting(
            client_id='123456', amount='1700.00', account_type='gmv',
        )
        .expect_fine(
            client_id='123456',
            fine_reason='cancel',
            actual_amount='28.00',
            calculated_amount='28.00',
        )
        .run(transformer_fixtures)
    )


async def test_happy_path_many_products_additional_commission(
        transformer_fixtures,
):
    await (
        helper.TransformerShopTest()
        .on_order_cancelled(
            is_place_fault=True,
            place_id='place_1',
            products=[
                common.make_reimbursement_payment(
                    payment_type='our_refund',
                    amount='200',
                    product_type='product',
                ),
                common.make_reimbursement_payment(
                    payment_type='our_refund',
                    amount='500',
                    product_type='product',
                ),
                common.make_reimbursement_payment(
                    payment_type='our_refund',
                    amount='1000',
                    product_type='product',
                ),
                common.make_reimbursement_payment(
                    payment_type='our_refund',
                    amount='100',
                    product_type='delivery',
                ),
            ],
        )
        .using_business_rules(
            place_id='place_1',
            client_info=rules.client_info(client_id='123456'),
            fine=rules.make_fine(
                business_type='shop',
                delivery_type='native',
                reason='cancellation',
                params=rules.simple_fine(fine='10', fix_fine='10'),
            ),
            commission=rules.make_commission(
                commission_type='place_delivery',
                params=rules.simple_commission(
                    commission='10',
                    acquiring_commission='0',
                    fix_commission='10',
                    additional_commission='5',
                ),
            ),
        )
        .expect(
            common.billing_event(
                client_info=rules.client_info(client_id='123456'),
                commission=common.make_commission(
                    product_type='product',
                    product_id='product__002',
                    amount='28',
                    commission_type='goods',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(client_id='123456'),
                commission=common.make_commission(
                    product_type='product',
                    product_id='subscribe_gmv',
                    amount='85',
                    commission_type='subscribe_gmv',
                ),
            ),
        )
        .expect_accounting(
            client_id='123456', amount='1700.00', account_type='gmv',
        )
        .expect_fine(
            client_id='123456',
            fine_reason='cancel',
            actual_amount='28.00',
            calculated_amount='28.00',
        )
        .run(transformer_fixtures)
    )
