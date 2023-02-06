import pytest

from eats_order_integration.generated.service.swagger.models import (
    api as order_models,
)


@pytest.mark.pgsql('eats_order_integration', files=['places.sql'])
async def test_get_marketplace_order(
        stq3_context,
        mockserver,
        load_json,
        order_meta_info_mock,
        eats_eaters_mock,
        personal_mock,
        eats_core_order_integration_mock,
        eats_order_revision_mock,
):

    order = await stq3_context.order_composer.order_get(order_nr='order_nr')
    assert order.serialize() == load_json('order.json')
    assert isinstance(order, order_models.Order)
    assert isinstance(order.order_info, order_models.MarketplaceOrder)
