import pytest


LAST_CURSOR = 'last_cursor'


@pytest.fixture(name='eats_shifts', autouse=True)
def mock_eats_shifts(mockserver):
    class Context:
        def __init__(self):
            self.shifts = None

        def set_shifts(self, shifts):
            self.shifts = shifts

    context = Context()

    @mockserver.json_handler(
        '/eats-performer-shifts/internal/eats-performer-shifts/v1/courier-shift-states/updates',  # noqa: E501
    )
    def _mock_shifts_updates(request):
        cursor = request.query.get('cursor', '')
        if cursor == LAST_CURSOR:
            return {'data': {'cursor': LAST_CURSOR, 'shifts': []}}

        shifts = context.shifts
        if shifts is None:
            shifts = []

        return {'data': {'cursor': LAST_CURSOR, 'shifts': shifts}}

    return context
