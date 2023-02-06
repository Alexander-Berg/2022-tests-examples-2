import pytest

from generated.models import eats_core_order_integration
from generated.models import eats_core_retail

from eats_order_integration.internal import entities
from eats_order_integration.internal import exceptions


ENGINE_ID = 12121


@pytest.fixture(autouse=True)
def _integration_engines_config(client_experiments3):
    client_experiments3.add_record(
        consumer='eats_order_integration/integration_engines_config',
        config_name='eats_order_integration_integration_engines_config',
        args=[{'name': 'engine_name', 'type': 'string', 'value': 'iGooods'}],
        value={'engine_name': 'iGooods', 'engine_class_name': 'IgooodsEngine'},
    )


async def test_should_call_create_order_if_need_to_create(
        partner_mocks, web_context, load_json, order_integration_mock,
):
    engine = await web_context.engine_selector.select_engine(ENGINE_ID)
    order = eats_core_order_integration.Order.deserialize(
        load_json('order.json')['for_create'],
    )
    await engine.send_order(order)
    assert partner_mocks['fetch_token'].has_calls
    assert partner_mocks['create_order'].has_calls
    assert not partner_mocks['update_order'].has_calls


async def test_should_call_update_order_if_need_to_update(
        partner_mocks, web_context, load_json, order_integration_mock,
):
    engine = await web_context.engine_selector.select_engine(ENGINE_ID)
    order = eats_core_order_integration.Order.deserialize(
        load_json('order.json')['for_update'],
    )
    await engine.send_order(order)
    assert partner_mocks['fetch_token'].has_calls
    assert not partner_mocks['create_order'].has_calls
    assert partner_mocks['update_order'].has_calls


async def test_get_order_status(partner_mocks, web_context, load_json):
    engine = await web_context.engine_selector.select_engine(ENGINE_ID)

    order = eats_core_order_integration.Order.deserialize(
        load_json('order.json')['for_check_status'],
    )
    status = await engine.get_order_status(order)

    assert partner_mocks['fetch_token'].has_calls
    assert partner_mocks['order_status'].has_calls
    assert status == entities.OrderStatus.NEW


async def test_cancel_order(partner_mocks, web_context):
    engine = await web_context.engine_selector.select_engine(ENGINE_ID)

    await engine.cancel_order(
        eats_core_order_integration.Order(
            order_nr='1',
            external_id='external_id',
            place_id='place_id_1',
            place_group_id='place_group_id_1',
            order_info=None,
        ),
    )

    assert partner_mocks['fetch_token'].has_calls
    assert partner_mocks['order_status'].has_calls


async def test_should_raise_error_if_settings_has_extra_fields(web_context):
    engine = await web_context.engine_selector.select_engine(ENGINE_ID)
    with pytest.raises(exceptions.SettingsHasExtraProperties):
        await engine.parse_settings(
            eats_core_retail.OrderInfo(
                order_options={
                    'vendorHost': 'a',
                    'clientId': 'b',
                    'clientSecret': 'a',
                    'scope': 'a',
                    'some_prop': 1,
                },
                place_group_id='1',
                integration_engine_id='1',
            ),
        )


async def test_should_raise_send_order_if_have_not_inner_error(
        web_context, load_json,
):
    engine = await web_context.engine_selector.select_engine(ENGINE_ID)
    order = eats_core_order_integration.Order.deserialize(
        load_json('order.json')['for_create'],
    )
    with pytest.raises(exceptions.SendOrderError):
        await engine.send_order(order)


async def test_should_raise_inner_error(
        web_context, load_json, partner_mocks, order_integration_mock,
):
    engine = await web_context.engine_selector.select_engine(ENGINE_ID)
    order = eats_core_order_integration.Order.deserialize(
        load_json('order.json')['for_update_with_error'],
    )
    with pytest.raises(exceptions.CannotResendOrder):
        await engine.send_order(order)


async def test_should_correct_send_token_for_different_partners(
        web_context, load_json, partner_mocks, order_integration_mock,
):
    engine = await web_context.engine_selector.select_engine(ENGINE_ID)
    # take order with place_Group_id1
    # check token it has be token1
    # take order with place_group_id2
    # check token it has be token2
    # we can check calls, it has be 2

    order = eats_core_order_integration.Order.deserialize(
        load_json('order.json')['for_create'],
    )
    await engine.send_order(order)

    order2 = eats_core_order_integration.Order.deserialize(
        load_json('order.json')['for_create_2'],
    )
    await engine.send_order(order2)

    assert partner_mocks['fetch_token'].times_called == 2
    assert partner_mocks['create_order'].times_called == 2
