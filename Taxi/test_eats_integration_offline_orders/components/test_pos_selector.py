import pytest

from eats_integration_offline_orders.components.pos import pos_selector
from eats_integration_offline_orders.internal import enums


@pytest.mark.parametrize('pos_type', ['iiko', 'rkeeper', 'quick_resto'])
async def test_pos_selector(web_context, pos_type):

    assert web_context.pos_selector(pos_type)


@pytest.mark.config(
    EATS_INTEGRATION_OFFLINE_ORDERS_SETTINGS={'fake_pos_enabled': True},
)
async def test_pos_selector_not_raise_if_fake_enabled(web_context):

    assert web_context.pos_selector(enums.POSClientTypes.FAKE.value)


@pytest.mark.config(
    EATS_INTEGRATION_OFFLINE_ORDERS_SETTINGS={'fake_pos_enabled': False},
)
async def test_pos_selector_raise_if_fake_disabled(web_context):

    with pytest.raises(pos_selector.POSSelectorException):
        web_context.pos_selector(enums.POSClientTypes.FAKE.value)
