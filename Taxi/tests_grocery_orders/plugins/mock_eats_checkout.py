import pytest


DEFAULT_EATS_ORDER_ID = '123456-789012'


@pytest.fixture(name='eats_checkout', autouse=True)
def mock_eats_checkout(mockserver):
    class Context:
        def __init__(self):
            self.eats_order_id = DEFAULT_EATS_ORDER_ID

        def set_eats_order_id(self, eats_order_id):
            self.eats_order_id = eats_order_id

        @property
        def times_grocery_checkout_called(self):
            return grocery_checkout.times_called

        def grocery_checkout_flush(self):
            grocery_checkout.flush()

    context = Context()

    @mockserver.json_handler('/eats-checkout/grocery/checkout')
    def grocery_checkout(request):
        return {'payload': {'number': context.eats_order_id}}

    return context
