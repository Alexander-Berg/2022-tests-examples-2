import pytest


class RideDiscountsContext:
    def __init__(self):
        self.calls = 0
        self.brandings_response = []

    def set_brandings_response(self, response):
        self.brandings_response = response


@pytest.fixture(autouse=True)
def ride_discounts(mockserver):
    discounts_context = RideDiscountsContext()

    @mockserver.json_handler('/ride_discounts/v1/brandings')
    def _mock_brandings(request):
        discounts_context.calls += 1
        return discounts_context.brandings_response

    return discounts_context
