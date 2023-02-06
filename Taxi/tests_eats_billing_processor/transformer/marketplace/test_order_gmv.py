import pytest

from tests_eats_billing_processor import rules
from tests_eats_billing_processor.transformer import common
from tests_eats_billing_processor.transformer.marketplace import helper


async def test_happy_path_one_event(transformer_fixtures):
    await (
        helper.TransformerMarketplaceTest()
        .on_order_gmv(place_id='place_1', gmv_amount='200')
        .using_business_rules(
            place_id='place_1',
            client_info=rules.client_info(client_id='123456'),
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
                    amount='40',
                    commission_type='goods',
                ),
            ),
        )
        .expect_accounting(
            account_type='gmv', client_id='123456', amount='200.00',
        )
        .run(transformer_fixtures)
    )


async def test_happy_path_many_events(transformer_fixtures):
    await (
        helper.TransformerMarketplaceTest()
        .on_order_gmv(place_id='place_1', gmv_amount='200')
        .on_order_gmv(place_id='place_1', gmv_amount='300')
        .using_business_rules(
            place_id='place_1',
            client_info=rules.client_info(client_id='123456'),
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
                    amount='40',
                    commission_type='goods',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(client_id='123456'),
                commission=common.make_commission(
                    product_type='product',
                    product_id='product__002',
                    amount='-40',
                    commission_type='goods',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(client_id='123456'),
                commission=common.make_commission(
                    product_type='product',
                    product_id='product__002',
                    amount='55',
                    commission_type='goods',
                ),
            ),
        )
        .expect_accounting(
            account_type='gmv', client_id='123456', amount='300.00',
        )
        .run(transformer_fixtures)
    )


async def test_happy_path_many_events_additional_commission(
        transformer_fixtures,
):
    await (
        helper.TransformerMarketplaceTest()
        .on_order_gmv(place_id='place_1', gmv_amount='200')
        .on_order_gmv(place_id='place_1', gmv_amount='300')
        .using_business_rules(
            place_id='place_1',
            client_info=rules.client_info(client_id='123456'),
            commission=rules.make_commission(
                commission_type='place_delivery',
                params=rules.simple_commission(
                    commission='10',
                    acquiring_commission='5',
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
                    amount='40',
                    commission_type='goods',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(client_id='123456'),
                commission=common.make_commission(
                    product_type='product',
                    product_id='subscribe_gmv',
                    amount='10',
                    commission_type='subscribe_gmv',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(client_id='123456'),
                commission=common.make_commission(
                    product_type='product',
                    product_id='product__002',
                    amount='-40',
                    commission_type='goods',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(client_id='123456'),
                commission=common.make_commission(
                    product_type='product',
                    product_id='product__002',
                    amount='55',
                    commission_type='goods',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(client_id='123456'),
                commission=common.make_commission(
                    product_type='product',
                    product_id='subscribe_gmv',
                    amount='-10',
                    commission_type='subscribe_gmv',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(client_id='123456'),
                commission=common.make_commission(
                    product_type='product',
                    product_id='subscribe_gmv',
                    amount='15',
                    commission_type='subscribe_gmv',
                ),
            ),
        )
        .expect_accounting(
            account_type='gmv', client_id='123456', amount='300.00',
        )
        .run(transformer_fixtures)
    )


@pytest.mark.pgsql('eats_billing_processor', files=['order_gmv.sql'])
async def test_happy_path_one_event_with_no_update_account(
        transformer_fixtures,
):
    await (
        helper.TransformerMarketplaceTest()
        .on_order_gmv(place_id='place_1', gmv_amount='200')
        .using_business_rules(
            place_id='place_1',
            client_info=rules.client_info(client_id='123456'),
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
                    amount='40',
                    commission_type='goods',
                ),
            ),
        )
        .expect_accounting(
            account_type='gmv', client_id='123456', amount='1200.00',
        )
        .run(transformer_fixtures)
    )


async def test_happy_path_markup_commission(transformer_fixtures):
    await (
        helper.TransformerMarketplaceTest()
        .on_order_gmv(
            place_id='place_1', gmv_amount='200', dynamic_price='100',
        )
        .using_business_rules(
            place_id='place_1',
            client_info=rules.client_info(client_id='123456'),
            commission=rules.make_commission(
                commission_type='place_delivery',
                params=rules.simple_commission(
                    commission='30',
                    acquiring_commission='0',
                    fix_commission='0',
                ),
            ),
        )
        .using_business_rules(
            place_id='place_1',
            client_info=rules.client_info(client_id='123456'),
            commission=rules.make_commission(
                commission_type='markup',
                params=rules.simple_commission(
                    commission='50',
                    acquiring_commission='0',
                    fix_commission='0',
                ),
            ),
        )
        .expect(
            common.billing_event(
                client_info=rules.client_info(client_id='123456'),
                commission=common.make_commission(
                    product_type='product',
                    product_id='product__002',
                    amount='30',
                    commission_type='goods',
                ),
            ),
        )
        .expect(
            common.billing_event(
                client_info=rules.client_info(client_id='123456'),
                commission=common.make_commission(
                    product_type='product',
                    product_id='markup_goods',
                    amount='50',
                    commission_type='markup_goods',
                ),
            ),
        )
        .expect_accounting(
            account_type='gmv', client_id='123456', amount='200.00',
        )
        .run(transformer_fixtures)
    )


async def test_weekly_payments(transformer_fixtures):
    await (
        helper.TransformerMarketplaceTest()
        .on_order_gmv(
            place_id='place_1', gmv_amount='200', dynamic_price='100',
        )
        .using_business_rules(
            place_id='place_1',
            client_info=rules.client_info(client_id='123456'),
            commission=rules.make_commission(
                commission_type='place_delivery',
                params=rules.simple_commission(
                    commission='30',
                    acquiring_commission='0',
                    fix_commission='0',
                ),
                billing_frequency='weekly',
            ),
        )
        .using_business_rules(
            place_id='place_1',
            client_info=rules.client_info(client_id='123456'),
            commission=rules.make_commission(
                commission_type='markup',
                params=rules.simple_commission(
                    commission='50',
                    acquiring_commission='0',
                    fix_commission='0',
                ),
            ),
        )
        .expect(
            common.billing_event(
                client_info=rules.client_info(client_id='123456'),
                commission=common.make_commission(
                    product_type='product',
                    product_id='product__002_weekly',
                    amount='30',
                    commission_type='goods_weekly',
                ),
            ),
        )
        .expect(
            common.billing_event(
                client_info=rules.client_info(client_id='123456'),
                commission=common.make_commission(
                    product_type='product',
                    product_id='markup_goods_weekly',
                    amount='50',
                    commission_type='markup_goods_weekly',
                ),
            ),
        )
        .expect_accounting(
            account_type='gmv', client_id='123456', amount='200.00',
        )
        .run(transformer_fixtures)
    )


@pytest.mark.pgsql(
    'eats_billing_processor', files=['billing_commission_weekly.sql'],
)
async def test_update_stored_weekly_commission(transformer_fixtures):
    await (
        helper.TransformerMarketplaceTest()
        .on_order_gmv(place_id='place_1', gmv_amount='200')
        .using_business_rules(
            place_id='place_1',
            client_info=rules.client_info(client_id='12345'),
            commission=rules.make_commission(
                commission_type='place_delivery',
                params=rules.simple_commission(
                    commission='30',
                    acquiring_commission='0',
                    fix_commission='0',
                ),
                billing_frequency='daily',
            ),
        )
        .expect(
            common.billing_event(
                client_info=rules.client_info(client_id='12345'),
                transaction_date='2021-04-05T08:25:00+00:00',
                rule='default',
                commission=common.make_commission(
                    product_type='product',
                    product_id='product__002',
                    amount='-100',
                    commission_type='goods',
                ),
            ),
        )
        .expect(
            common.billing_event(
                client_info=rules.client_info(client_id='12345'),
                commission=common.make_commission(
                    product_type='product',
                    product_id='product__002',
                    amount='60',
                    commission_type='goods',
                ),
            ),
        )
        .expect_accounting(
            account_type='gmv', client_id='12345', amount='200.00',
        )
        .expect_stq_call_id(2)
        .run(transformer_fixtures)
    )


@pytest.mark.pgsql(
    'eats_billing_processor', files=['billing_commission_daily.sql'],
)
async def test_update_new_weekly_commission(transformer_fixtures):
    await (
        helper.TransformerMarketplaceTest()
        .on_order_gmv(place_id='place_1', gmv_amount='200')
        .using_business_rules(
            place_id='place_1',
            client_info=rules.client_info(client_id='12345'),
            commission=rules.make_commission(
                commission_type='place_delivery',
                params=rules.simple_commission(
                    commission='30',
                    acquiring_commission='0',
                    fix_commission='0',
                ),
                billing_frequency='weekly',
            ),
        )
        .expect(
            common.billing_event(
                client_info=rules.client_info(client_id='12345'),
                transaction_date='2021-04-05T08:25:00+00:00',
                commission=common.make_commission(
                    product_type='product',
                    product_id='product__002_weekly',
                    amount='-100',
                    commission_type='goods_weekly',
                ),
            ),
        )
        .expect(
            common.billing_event(
                client_info=rules.client_info(client_id='12345'),
                commission=common.make_commission(
                    product_type='product',
                    product_id='product__002_weekly',
                    amount='60',
                    commission_type='goods_weekly',
                ),
            ),
        )
        .expect_accounting(
            account_type='gmv', client_id='12345', amount='200.00',
        )
        .expect_stq_call_id(2)
        .run(transformer_fixtures)
    )
