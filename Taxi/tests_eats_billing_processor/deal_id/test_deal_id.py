import pytest

from tests_eats_billing_processor.deal_id import helper


async def test_happy_path_restaurant(deal_id_fixtures):
    await (
        helper.DealIdTest()
        .using_client_info(
            client_info={
                'id': '12345',
                'contract_id': '55555',
                'country_code': 'RU',
                'mvp': 'br_moscow_adm',
            },
            place_id='place_1',
            rule='restaurant',
        )
        .on_place(
            place_id='place_1',
            place_type='restaurant',
            delivery_type='native',
        )
        .expected_rule_name('restaurant')
        .run(deal_id_fixtures)
    )


async def test_happy_path_marketplace(deal_id_fixtures):
    await (
        helper.DealIdTest()
        .using_client_info(
            client_info={
                'id': '12345',
                'contract_id': '55555',
                'country_code': 'RU',
                'mvp': 'br_moscow_adm',
            },
            courier_id='courier_1',
            rule='marketplace',
        )
        .on_courier(
            courier_id='courier_1',
            place_type='restaurant',
            delivery_type='place',
        )
        .expected_rule_name('marketplace')
        .run(deal_id_fixtures)
    )


async def test_happy_path_pickup(deal_id_fixtures):
    await (
        helper.DealIdTest()
        .using_client_info(
            client_info={
                'id': '12345',
                'contract_id': '55555',
                'country_code': 'RU',
                'mvp': 'br_moscow_adm',
            },
            picker_id='picker_1',
            rule='pickup',
        )
        .on_picker(
            picker_id='picker_1',
            place_type='restaurant',
            delivery_type='pickup',
        )
        .expected_rule_name('pickup')
        .run(deal_id_fixtures)
    )


async def test_happy_path_retail(deal_id_fixtures):
    await (
        helper.DealIdTest()
        .using_client_info(
            client_info={
                'id': '12345',
                'contract_id': '55555',
                'country_code': 'RU',
                'mvp': 'br_moscow_adm',
            },
            place_id='place_1',
            rule='retail',
        )
        .on_place(
            place_id='place_1',
            place_type='shop',
            delivery_type='native',
            assembly_type='native',
        )
        .expected_rule_name('retail')
        .run(deal_id_fixtures)
    )


async def test_happy_path_shop(deal_id_fixtures):
    await (
        helper.DealIdTest()
        .using_client_info(
            client_info={
                'id': '12345',
                'contract_id': '55555',
                'country_code': 'RU',
                'mvp': 'br_moscow_adm',
            },
            place_id='place_1',
            rule='shop',
        )
        .on_place(
            place_id='place_1',
            place_type='shop',
            delivery_type='place',
            assembly_type='native',
        )
        .expected_rule_name('shop')
        .run(deal_id_fixtures)
    )


async def test_happy_path_shop_marketplace(deal_id_fixtures):
    await (
        helper.DealIdTest()
        .using_client_info(
            client_info={
                'id': '12345',
                'contract_id': '55555',
                'country_code': 'RU',
                'mvp': 'br_moscow_adm',
            },
            place_id='place_1',
            rule='shop_marketplace',
        )
        .on_place(
            place_id='place_1',
            place_type='shop',
            delivery_type='place',
            assembly_type='place',
        )
        .expected_rule_name('shop_marketplace')
        .run(deal_id_fixtures)
    )


async def test_happy_path_grocery_client_id(deal_id_fixtures):
    await (
        helper.DealIdTest()
        .using_client_info(
            client_info={
                'id': '12345',
                'contract_id': '55555',
                'country_code': 'RU',
                'mvp': 'br_moscow_adm',
            },
            place_id=helper.GROCERY_CLIENT_ID,
            rule='grocery',
        )
        .on_place(
            place_id=helper.GROCERY_CLIENT_ID,
            place_type='shop',
            delivery_type='place',
            assembly_type='place',
        )
        .expected_rule_name('grocery')
        .run(deal_id_fixtures)
    )


async def test_happy_path_grocery(deal_id_fixtures):
    await (
        helper.DealIdTest()
        .using_client_info(
            client_info={
                'id': '12345',
                'contract_id': '55555',
                'country_code': 'RU',
                'mvp': 'br_moscow_adm',
            },
            place_id='1234',
            rule='grocery',
        )
        .on_place(place_id='1234', place_type='grocery', delivery_type='place')
        .expected_rule_name('grocery')
        .run(deal_id_fixtures)
    )


async def test_happy_path_grocery_order_nr(deal_id_fixtures):
    await (
        helper.DealIdTest()
        .on_order_nr('123456-grocery')
        .using_client_info(
            client_info={
                'id': '12345',
                'contract_id': '55555',
                'country_code': 'RU',
                'mvp': 'br_moscow_adm',
            },
            place_id='87432897',
            rule='grocery_eats_flow',
        )
        .on_place(
            place_id='87432897',
            place_type='shop',
            delivery_type='place',
            assembly_type='place',
        )
        .expected_rule_name('grocery_eats_flow')
        .run(deal_id_fixtures)
    )


async def test_happy_path_grocery_eats_flow(deal_id_fixtures):
    await (
        helper.DealIdTest()
        .using_client_info(
            client_info={
                'id': '12345',
                'contract_id': '55555',
                'country_code': 'RU',
                'mvp': 'br_moscow_adm',
            },
            place_id='1234',
            rule='grocery_eats_flow',
        )
        .on_place(
            place_id='1234', place_type='grocery', delivery_type='native',
        )
        .expected_rule_name('grocery_eats_flow')
        .run(deal_id_fixtures)
    )


async def test_assembly_for_restaurant_fail(deal_id_fixtures):
    await (
        helper.DealIdTest()
        .using_client_info(
            client_info={
                'id': '12345',
                'contract_id': '55555',
                'country_code': 'RU',
                'mvp': 'br_moscow_adm',
            },
            place_id='place_1',
            rule='restaurant',
        )
        .on_place(
            place_id='place_1',
            place_type='restaurant',
            delivery_type='native',
            assembly_type='native',
        )
        .should_fail(
            400,
            'INCORRECT_DATA',
            'Inconsistent data: place = \'restaurant\' cannot have '
            'delivery_type = \'native\' and assembly_type = \'native\'',
        )
        .run(deal_id_fixtures)
    )


async def test_inconsistent_data_for_shop_fail(deal_id_fixtures):
    await (
        helper.DealIdTest()
        .using_client_info(
            client_info={
                'id': '12345',
                'contract_id': '55555',
                'country_code': 'RU',
                'mvp': 'br_moscow_adm',
            },
            place_id='place_1',
            rule='shop',
        )
        .on_place(
            place_id='place_1',
            place_type='shop',
            delivery_type='native',
            assembly_type='place',
        )
        .should_fail(
            400,
            'INCORRECT_DATA',
            'Inconsistent data: place = \'shop\' cannot have '
            'delivery_type = \'native\' and assembly_type = \'place\'',
        )
        .run(deal_id_fixtures)
    )


@pytest.mark.config(
    EATS_BILLING_PROCESSOR_FEATURES={'client_info_check': True},
)
async def test_incomplete_get_info_response_fail(deal_id_fixtures):
    await (
        helper.DealIdTest()
        .using_client_info(
            client_info={
                'id': '12345',
                'contract_id': '55555',
                'mvp': 'br_moscow_adm',
            },
            place_id='place_1',
            rule='restaurant',
        )
        .on_place(
            place_id='place_1',
            place_type='restaurant',
            delivery_type='native',
        )
        .should_fail(404, 'NOT_FOUND', 'Incomplete client info')
        .run(deal_id_fixtures)
    )


async def test_no_duplicate_token(deal_id_fixtures):
    deal_id_test = helper.DealIdTest()
    await (
        deal_id_test.using_client_info(
            client_info={
                'id': '12345',
                'contract_id': '55555',
                'country_code': 'RU',
                'mvp': 'br_moscow_adm',
            },
            place_id='place_1',
            rule='restaurant',
        )
        .on_place(
            place_id='place_1',
            place_type='restaurant',
            delivery_type='native',
        )
        .expected_rule_name('restaurant')
        .run(deal_id_fixtures)
    )

    token = deal_id_test.token()

    await (
        deal_id_test.using_client_info(
            client_info={
                'id': '12345',
                'contract_id': '55555',
                'country_code': 'RU',
                'mvp': 'br_moscow_adm',
            },
            place_id='place_1',
            rule='restaurant',
        )
        .on_place(
            place_id='place_1', place_type='restaurant', delivery_type='place',
        )
        .expected_rule_name('restaurant')
        .run(deal_id_fixtures)
    )

    assert token == deal_id_test.token()
