import pytest

GROCERY_SHIFTS_DEFAULT_RESPONSE = {'depot_ids': ['1']}


@pytest.fixture(autouse=True, name='grocery_shifts')
def mock_grocery_shifts_depots(mockserver):
    class Context:
        def __init__(self):
            self.couriers_shifts_response = None

        def set_couriers_shifts_response(self, response):
            self.couriers_shifts_response = response

        def times_couriers_shifts_called(self):
            return mock_grocery_shifts_depots_.times_called

    context = Context()

    @mockserver.json_handler(
        '/grocery-checkins/internal/checkins/v1/grocery-shifts/depots',
    )
    def mock_grocery_shifts_depots_(request):
        if context.couriers_shifts_response is not None:
            return context.couriers_shifts_response

        return GROCERY_SHIFTS_DEFAULT_RESPONSE

    return context
