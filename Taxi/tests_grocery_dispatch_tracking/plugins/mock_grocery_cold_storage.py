import pytest

DEPOT_STATE = 'depot-state'

CHECK_REQUEST = 'check_depot_state_request'
ITEM_IDS = 'item_ids'
FIELDS = 'fields'
STATUS_CODE = 'status_code'
RESPONSE_BODY = 'response_body'


@pytest.fixture(name='grocery_cold_storage')
def mock_grocery_cold_storage(mockserver):
    state = {}

    @mockserver.json_handler(
        '/grocery-cold-storage/internal/v1/cold-storage/v1/get/depot-state',
    )
    def check_depot_state(request):
        body = request.json

        assert ITEM_IDS in body
        assert FIELDS in body

        if state[DEPOT_STATE][CHECK_REQUEST]:
            if ITEM_IDS in state[DEPOT_STATE]:
                assert body[ITEM_IDS] == state[DEPOT_STATE][ITEM_IDS]
            if FIELDS in state[DEPOT_STATE]:
                assert body[FIELDS] == state[DEPOT_STATE][FIELDS]

        return mockserver.make_response(
            status=state[DEPOT_STATE][STATUS_CODE],
            json=state[DEPOT_STATE][RESPONSE_BODY],
        )

    class Context:
        def __init__(self):
            state[DEPOT_STATE] = {}
            state[DEPOT_STATE][CHECK_REQUEST] = False
            state[DEPOT_STATE][STATUS_CODE] = 200
            state[DEPOT_STATE][RESPONSE_BODY] = {'items': []}

        def depot_state_times_called(self):
            return check_depot_state.times_called

        def check_depot_state_request(self, item_ids=None, fields=None):
            state[DEPOT_STATE][CHECK_REQUEST] = True
            if item_ids is not None:
                state[DEPOT_STATE][ITEM_IDS] = item_ids
            if fields is not None:
                state[DEPOT_STATE][FIELDS] = fields

        def set_depot_state_response(self, status_code=200, items=None):
            if not items:
                items = []

            state[DEPOT_STATE][STATUS_CODE] = status_code
            state[DEPOT_STATE][RESPONSE_BODY] = {'items': items}

    context = Context()
    return context
