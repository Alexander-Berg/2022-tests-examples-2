import pytest


@pytest.fixture(name='set_up_order_admin_cancel_menu_v2')
async def _set_up_order_admin_cancel_menu_v2(
        taxi_cargo_dispatch, load_json, taxi_config,
):
    order_admin_cancel_menu = load_json(
        'cargo_dispatch_order_admin_cancel_menu_v2.json',
    )
    taxi_config.set(
        CARGO_DISPATCH_ORDER_ADMIN_CANCEL_MENU_V2=order_admin_cancel_menu,
    )
    await taxi_cargo_dispatch.invalidate_caches()
