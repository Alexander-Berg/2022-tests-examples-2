import pytest


class MockPricingAdminContext:
    def __init__(self):
        self._variables_response = {'ride': {}, 'fix': {}, 'trip': {}}

    def set_variables_response(self, resp):
        self._variables_response = resp

    def get_variables(self, request):
        return self._variables_response


@pytest.fixture(autouse=True)
def mock_pricing_admin(mockserver):
    ctx = MockPricingAdminContext()

    # pylint: disable=unused-variable
    @mockserver.json_handler('/pricing-admin/v1/settings/variables')
    def get_variables(request):
        return ctx.get_variables(request)

    return ctx
