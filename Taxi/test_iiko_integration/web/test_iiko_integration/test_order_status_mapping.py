from iiko_integration.model import order as order_model


def test_order_transition_map():
    for status in order_model.InvoiceStatus:
        assert status in order_model.ALLOWED_INVOICE_STATUS_TRANSITIONS
        assert isinstance(
            order_model.ALLOWED_INVOICE_STATUS_TRANSITIONS[status], set,
        )
    for status in order_model.RestaurantStatus:
        assert status in order_model.ALLOWED_RESTAURANT_STATUS_TRANSITIONS
        assert isinstance(
            order_model.ALLOWED_RESTAURANT_STATUS_TRANSITIONS[status], set,
        )
