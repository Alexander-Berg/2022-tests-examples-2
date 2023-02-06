# pylint: disable=invalid-name
import pytest


@pytest.fixture(name='billing_subventions_x', autouse=False)
def _billing_subventions(mockserver):
    class BillingSubventionsContext:
        def __init__(self):
            self.virtual_by_driver_response = {'subventions': []}
            self.virtual_by_driver_calls = 0
            self.virtual_by_driver_429_enabled = False
            self.virtual_by_driver_429_enabled_with_msg = False

        def set_virtual_by_driver_response(self, response):
            self.virtual_by_driver_response = response

        def set_virtual_by_driver_429(self, is_body_enabled=False):
            self.virtual_by_driver_429_enabled = not is_body_enabled
            self.virtual_by_driver_429_enabled_with_msg = is_body_enabled

    context = BillingSubventionsContext()

    @mockserver.json_handler('/billing-subventions-x/v1/virtual_by_driver')
    async def _get_virtual_by_driver(request):
        context.virtual_by_driver_calls += 1
        if context.virtual_by_driver_429_enabled:
            return mockserver.make_response(status=429)
        if context.virtual_by_driver_429_enabled_with_msg:
            return mockserver.make_response('Too many requests', status=429)
        return context.virtual_by_driver_response

    return context
