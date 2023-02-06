import pytest

CARGO_DISPATCHES = 'cargo_dispatches'

CHECK_REQUEST = 'check_cargo_dispatches_request'
ITEM_IDS = 'item_ids'
FIELDS = 'fields'
STATUS_CODE = 'status_code'
RESPONSE_BODY = 'response_body'


@pytest.fixture(name='grocery_cold_storage')
def mock_grocery_cold_storage(mockserver):
    state = {}

    @mockserver.json_handler(
        '/grocery-cold-storage/internal/v1/'
        'cold-storage/v1/get/cargo_dispatches',
    )
    def check_cargo_dispatches(request):
        body = request.json

        assert ITEM_IDS in body
        assert FIELDS in body

        if state[CARGO_DISPATCHES][CHECK_REQUEST]:
            if ITEM_IDS in state[CARGO_DISPATCHES]:
                assert body[ITEM_IDS] == state[CARGO_DISPATCHES][ITEM_IDS]
            if FIELDS in state[CARGO_DISPATCHES]:
                assert body[FIELDS] == state[CARGO_DISPATCHES][FIELDS]

        return mockserver.make_response(
            status=state[CARGO_DISPATCHES][STATUS_CODE],
            json=state[CARGO_DISPATCHES][RESPONSE_BODY],
        )

    class Context:
        def __init__(self):
            state[CARGO_DISPATCHES] = {}
            state[CARGO_DISPATCHES][CHECK_REQUEST] = False
            state[CARGO_DISPATCHES][STATUS_CODE] = 200
            state[CARGO_DISPATCHES][RESPONSE_BODY] = {'items': []}

        def cargo_dispatches_times_called(self):
            return check_cargo_dispatches.times_called

        def check_cargo_dispatches_request(self, item_ids=None, fields=None):
            state[CARGO_DISPATCHES][CHECK_REQUEST] = True
            if item_ids is not None:
                state[CARGO_DISPATCHES][ITEM_IDS] = item_ids
            if fields is not None:
                state[CARGO_DISPATCHES][FIELDS] = fields

        def set_cargo_dispatches_response(self, status_code=200, items=None):
            if not items:
                items = []

            state[CARGO_DISPATCHES][STATUS_CODE] = status_code
            state[CARGO_DISPATCHES][RESPONSE_BODY] = {'items': items}

    context = Context()
    return context
