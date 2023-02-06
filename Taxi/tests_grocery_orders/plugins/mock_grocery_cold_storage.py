import pytest

ORDERS = 'orders'

CHECK_REQUEST = 'check_orders_request'
ITEM_IDS = 'item_ids'
FIELDS = 'fields'
STATUS_CODE = 'status_code'
RESPONSE_BODY = 'response_body'


@pytest.fixture(name='grocery_cold_storage')
def mock_grocery_cold_storage(mockserver):
    state = {}

    class Context:
        def __init__(self):
            state[ORDERS] = {}
            state[ORDERS][CHECK_REQUEST] = False
            state[ORDERS][STATUS_CODE] = 200
            state[ORDERS][RESPONSE_BODY] = {'items': []}
            self.field_names = set()
            self.response_value = []

        def orders_times_called(self):
            return check_orders.times_called

        def check_orders_request(self, item_ids=None, fields=None):
            state[ORDERS][CHECK_REQUEST] = True
            if item_ids is not None:
                state[ORDERS][ITEM_IDS] = item_ids
            if fields is not None:
                state[ORDERS][FIELDS] = fields

        def set_orders_response(self, status_code=200, items=None):
            if not items:
                items = []

            state[ORDERS][STATUS_CODE] = status_code
            state[ORDERS][RESPONSE_BODY] = {'items': items}

            for item in items[0].values():
                self.response_value.append(item)

    context = Context()

    @mockserver.json_handler(
        '/grocery-cold-storage/internal/v1/cold-storage/v1/get/orders',
    )
    def check_orders(request):
        body = request.json

        # import json
        # print('!!!', json.dumps(body, indent=2, sort_keys=True))

        for item in body[FIELDS]:
            context.field_names.add(item['name'])

        assert ITEM_IDS in body
        assert FIELDS in body

        if state[ORDERS][CHECK_REQUEST]:
            if ITEM_IDS in state[ORDERS]:
                assert body[ITEM_IDS] == state[ORDERS][ITEM_IDS]
            if FIELDS in state[ORDERS]:
                assert body[FIELDS] == state[ORDERS][FIELDS]

        return mockserver.make_response(
            status=state[ORDERS][STATUS_CODE],
            json=state[ORDERS][RESPONSE_BODY],
        )

    return context
