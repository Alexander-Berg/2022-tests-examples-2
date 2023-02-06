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


async def test_happy_path_with_products(transformer_fixtures):
    await (
        helper.TransformerMarketplaceTest()
        .on_order_cancelled(
            is_place_fault=True,
            place_id='place_1',
            order_type='marketplace',
            products=[
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
                business_type='restaurant',
                delivery_type='marketplace',
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
                    amount='14',
                    commission_type='goods',
                ),
            ),
        )
        .expect_accounting(
            client_id='123456', amount='200.00', account_type='gmv',
        )
        .expect_fine(
            client_id='123456',
            fine_reason='cancel',
            actual_amount='14.00',
            calculated_amount='14.00',
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
        helper.TransformerMarketplaceTest()
        .on_order_cancelled(
            is_place_fault=True,
            place_id='place_1',
            order_type='marketplace',
            service_fee_amount='50',
            currency=currency,
            products=[
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
                business_type='restaurant',
                delivery_type='marketplace',
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
                commission=common.make_commission(
                    product_type='product',
                    product_id='product__002',
                    amount='14',
                    commission_type='goods',
                    currency=currency,
                ),
            ),
        )
        .expect_accounting(
            client_id='123456', amount='200.00', account_type='gmv',
        )
        .expect_fine(
            client_id='123456',
            fine_reason='cancel',
            actual_amount='14.00',
            calculated_amount='14.00',
            currency=currency,
        )
        .run(transformer_fixtures)
    )


async def test_happy_path_with_products_many_events(transformer_fixtures):
    await (
        helper.TransformerMarketplaceTest()
        .with_order_nr('1')
        .on_order_cancelled(
            is_place_fault=True,
            place_id='place_1',
            order_type='marketplace',
            products=[
                common.make_reimbursement_payment(
                    payment_type='our_refund',
                    amount='200',
                    product_type='product',
                ),
            ],
            external_id='order_cancelled/1',
        )
        .using_business_rules(
            place_id='place_1',
            client_info=rules.client_info(client_id='123456'),
            fine=rules.make_fine(
                business_type='restaurant',
                delivery_type='marketplace',
                reason='cancellation',
                params=rules.simple_fine(
                    fine='10', fix_fine='20', gmv_limit='20',
                ),
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
                    amount='24',
                    commission_type='goods',
                ),
            ),
        )
        # увеличиваются gmv и штраф
        .expect_accounting(
            client_id='123456', amount='200.00', account_type='gmv',
        )
        .expect_fine(
            client_id='123456',
            fine_reason='cancel',
            actual_amount='24.00',
            calculated_amount='24.00',
        )
        .no_stq_call_expected()
        .run(transformer_fixtures)
    )
    await (
        helper.TransformerMarketplaceTest()
        .with_order_nr('55551')
        .on_order_cancelled(
            is_place_fault=True,
            place_id='place_2',
            order_type='marketplace',
            products=[
                common.make_reimbursement_payment(
                    payment_type='our_refund',
                    amount='200',
                    product_type='product',
                ),
            ],
            external_id='order_cancelled/2',
        )
        .using_business_rules(
            place_id='place_2',
            client_info=rules.client_info(client_id='23456'),
            fine=rules.make_fine(
                business_type='restaurant',
                delivery_type='marketplace',
                reason='cancellation',
                params=rules.simple_fine(
                    fine='10', fix_fine='20', gmv_limit='10',
                ),
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
        # уменьшили gmv_limit до 10, теперь увеличивается
        # только gmv - штраф превышает максимальный
        .expect_accounting(
            client_id='123456', amount='200.00', account_type='gmv',
        )
        .expect_accounting(
            client_id='23456', amount='200.00', account_type='gmv',
        )
        .expect_fine(
            client_id='23456',
            fine_reason='cancel',
            actual_amount='0.00',
            calculated_amount='24.00',
        )
        .no_stq_call_expected()
        .run(transformer_fixtures)
    )
    await (
        helper.TransformerMarketplaceTest()
        .with_order_nr('55552')
        .on_order_cancelled(
            is_place_fault=True,
            place_id='place_3',
            order_type='marketplace',
            products=[
                common.make_reimbursement_payment(
                    payment_type='our_refund',
                    amount='400',
                    product_type='product',
                ),
            ],
            external_id='order_cancelled/3',
        )
        .using_business_rules(
            place_id='place_3',
            client_info=rules.client_info(client_id='34567'),
            fine=rules.make_fine(
                business_type='restaurant',
                delivery_type='marketplace',
                reason='cancellation',
                params=rules.simple_fine(
                    fine='10', fix_fine='20', gmv_limit='20',
                ),
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
                client_info=rules.client_info(client_id='34567'),
                commission=common.make_commission(
                    product_type='product',
                    product_id='product__002',
                    amount='27',
                    commission_type='goods',
                ),
            ),
        )
        # gmv_limit == 20, снова увеличиваются
        # gmv и fine
        .expect_accounting(
            client_id='123456', amount='200.00', account_type='gmv',
        )
        .expect_accounting(
            client_id='23456', amount='200.00', account_type='gmv',
        )
        .expect_accounting(
            client_id='34567', amount='400.00', account_type='gmv',
        )
        .expect_fine(
            client_id='34567',
            fine_reason='cancel',
            actual_amount='27.00',
            calculated_amount='27.00',
        )
        .no_stq_call_expected()
        .run(transformer_fixtures)
    )


async def test_happy_path_with_products_no_fine(transformer_fixtures):
    await (
        helper.TransformerMarketplaceTest()
        .on_order_cancelled(
            place_id='place_2',
            order_type='marketplace',
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
                    product_type='delivery',
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
            common.billing_event(
                client_info=rules.client_info(client_id='23456'),
                payment=common.payment(
                    payment_method='our_refund',
                    payment_service='yaeda',
                    product_type='delivery',
                    amount='200',
                ),
            ),
        )
        .expect_accounting(
            client_id='23456', amount='1000.00', account_type='gmv',
        )
        .run(transformer_fixtures)
    )


async def test_happy_path_with_no_products(transformer_fixtures):
    await (
        helper.TransformerMarketplaceTest()
        .on_order_cancelled(
            place_id='place_3', order_type='marketplace', products=[],
        )
        .using_business_rules(
            place_id='place_3',
            client_info=rules.client_info(client_id='34567'),
        )
        .no_stq_call_expected()
        .run(transformer_fixtures)
    )


async def test_happy_path_reimbursement_required(transformer_fixtures):
    await (
        helper.TransformerMarketplaceTest()
        .on_order_cancelled(
            place_id='place_1',
            order_type='marketplace',
            is_reimbursement_required=True,
            is_payment_expected=True,
            products=[
                common.make_reimbursement_payment(
                    payment_type='our_refund',
                    amount='200',
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
                    payment_method='our_refund',
                    payment_service='yaeda',
                    product_type='product',
                    amount='200',
                ),
            ),
        )
        .expect_accounting(
            client_id='123456', amount='400.00', account_type='gmv',
        )
        .run(transformer_fixtures)
    )


async def test_happy_path_fines(transformer_fixtures):
    await (
        helper.TransformerMarketplaceTest()
        .with_order_nr('1')
        .on_order_cancelled(
            is_place_fault=True,
            place_id='place_1',
            order_type='marketplace',
            products=[
                common.make_reimbursement_payment(
                    payment_type='our_refund',
                    amount='200',
                    product_type='product',
                ),
            ],
            external_id='order_cancelled/1',
        )
        .using_business_rules(
            place_id='place_1',
            client_info=rules.client_info(client_id='123456'),
            fine=rules.make_fine(
                rule_id='rule_1',
                business_type='restaurant',
                delivery_type='marketplace',
                reason='cancellation',
                params=rules.simple_fine(
                    fine='10', fix_fine='20', gmv_limit='10',
                ),
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
        .expect_accounting(
            client_id='123456', amount='200.00', account_type='gmv',
        )
        .expect_fine(
            client_id='123456',
            fine_reason='cancel',
            actual_amount='0.00',
            calculated_amount='24.00',
        )
        .no_stq_call_expected()
        .run(transformer_fixtures)
    )


@pytest.mark.pgsql('eats_billing_processor', files=['fine.sql'])
async def test_happy_path_idempotency(transformer_fixtures):
    await (
        helper.TransformerMarketplaceTest()
        .on_order_cancelled(
            is_place_fault=True,
            place_id='place_1',
            order_type='marketplace',
            products=[
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
                business_type='restaurant',
                delivery_type='marketplace',
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
                    amount='14',
                    commission_type='goods',
                ),
            ),
        )
        .expect_accounting(
            client_id='123456', amount='200.00', account_type='gmv',
        )
        .expect_fine(
            client_id='123456',
            fine_reason='cancel',
            actual_amount='30.00',
            calculated_amount='30.00',
        )
        .no_stq_call_expected()
        .run(transformer_fixtures)
    )


async def test_happy_path_many_products(transformer_fixtures):
    await (
        helper.TransformerMarketplaceTest()
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
                business_type='restaurant',
                delivery_type='marketplace',
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
        helper.TransformerMarketplaceTest()
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
                business_type='restaurant',
                delivery_type='marketplace',
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


async def test_fine_weekly_payment(transformer_fixtures):
    await (
        helper.TransformerMarketplaceTest()
        .with_order_nr('1')
        .on_order_cancelled(
            is_place_fault=True,
            place_id='place_1',
            order_type='marketplace',
            products=[
                common.make_reimbursement_payment(
                    payment_type='our_refund',
                    amount='200',
                    product_type='product',
                ),
            ],
            external_id='order_cancelled/1',
        )
        .using_business_rules(
            place_id='place_1',
            client_info=rules.client_info(client_id='123456'),
            fine=rules.make_fine(
                rule_id='rule_1',
                business_type='restaurant',
                delivery_type='marketplace',
                reason='cancellation',
                params=rules.simple_fine(fine='10', fix_fine='20'),
                billing_frequency='weekly',
            ),
            commission=rules.make_commission(
                commission_type='place_delivery',
                params=rules.simple_commission(
                    commission='10',
                    acquiring_commission='5',
                    fix_commission='10',
                ),
                billing_frequency='weekly',
            ),
        )
        .expect_accounting(
            client_id='123456', amount='200.00', account_type='gmv',
        )
        .expect_fine(
            client_id='123456',
            fine_reason='cancel',
            actual_amount='24.00',
            calculated_amount='24.00',
        )
        .expect(
            common.billing_event(
                client_info=rules.client_info(client_id='123456'),
                commission=common.make_commission(
                    product_type='product',
                    product_id='product__002_weekly',
                    amount='24',
                    commission_type='goods_weekly',
                ),
            ),
        )
        .no_stq_call_expected()
        .run(transformer_fixtures)
    )


async def test_reimbursement_weekly(transformer_fixtures):
    await (
        helper.TransformerMarketplaceTest()
        .on_order_cancelled(
            place_id='place_2',
            order_type='marketplace',
            is_reimbursement_required=True,
            products=[
                common.make_reimbursement_payment(
                    payment_type='our_refund',
                    amount='200',
                    product_type='delivery',
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
                billing_frequency='weekly',
            ),
        )
        .expect(
            common.billing_event(
                client_info=rules.client_info(client_id='23456'),
                payment=common.payment(
                    payment_method='our_refund',
                    payment_service='yaeda',
                    product_type='delivery_weekly',
                    amount='200',
                    product_id='delivery/native_weekly',
                ),
            ),
        )
        .run(transformer_fixtures)
    )
