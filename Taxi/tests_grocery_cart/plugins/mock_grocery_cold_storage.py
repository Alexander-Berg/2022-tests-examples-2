import pytest

CARTS = 'carts'
CARTS_BY_ORDER_ID = 'carts-by-order-id'
CHECKOUT_DATA = 'checkout_data'

CHECK_REQUEST = 'check_carts_request'
ITEM_IDS = 'item_ids'
FIELDS = 'fields'
STATUS_CODE = 'status_code'
RESPONSE_BODY = 'response_body'


@pytest.fixture(name='grocery_cold_storage')
def mock_grocery_cold_storage(mockserver):
    state = {}

    @mockserver.json_handler(
        '/grocery-cold-storage/internal/v1/cold-storage/v1/get/carts',
    )
    def check_carts(request):
        body = request.json

        assert ITEM_IDS in body
        assert FIELDS in body

        if state[CARTS][CHECK_REQUEST]:
            if ITEM_IDS in state[CARTS]:
                assert body[ITEM_IDS] == state[CARTS][ITEM_IDS]
            if FIELDS in state[CARTS]:
                assert body[FIELDS] == state[CARTS][FIELDS]

        return mockserver.make_response(
            status=state[CARTS][STATUS_CODE], json=state[CARTS][RESPONSE_BODY],
        )

    @mockserver.json_handler(
        '/grocery-cold-storage/internal/v1/cold-storage/v1/get/'
        'carts-by-order-id',
    )
    def check_carts_by_order_id(request):
        body = request.json

        assert ITEM_IDS in body
        assert FIELDS in body

        if state[CARTS_BY_ORDER_ID][CHECK_REQUEST]:
            if ITEM_IDS in state[CARTS_BY_ORDER_ID]:
                assert body[ITEM_IDS] == state[CARTS_BY_ORDER_ID][ITEM_IDS]
            if FIELDS in state[CARTS_BY_ORDER_ID]:
                assert body[FIELDS] == state[CARTS_BY_ORDER_ID][FIELDS]

        return mockserver.make_response(
            status=state[CARTS_BY_ORDER_ID][STATUS_CODE],
            json=state[CARTS_BY_ORDER_ID][RESPONSE_BODY],
        )

    @mockserver.json_handler(
        '/grocery-cold-storage/internal/v1/cold-storage'
        '/v1/get/carts_checkout_data',
    )
    def check_checkout_data(request):
        body = request.json

        assert ITEM_IDS in body
        assert FIELDS in body

        if state[CHECKOUT_DATA][CHECK_REQUEST]:
            if ITEM_IDS in state[CHECKOUT_DATA]:
                assert body[ITEM_IDS] == state[CHECKOUT_DATA][ITEM_IDS]
            if FIELDS in state[CHECKOUT_DATA]:
                assert body[FIELDS] == state[CHECKOUT_DATA][FIELDS]

        return mockserver.make_response(
            status=state[CHECKOUT_DATA][STATUS_CODE],
            json=state[CHECKOUT_DATA][RESPONSE_BODY],
        )

    class Context:
        def __init__(self):
            state[CARTS] = {}
            state[CARTS_BY_ORDER_ID] = {}
            state[CHECKOUT_DATA] = {}

            state[CARTS][CHECK_REQUEST] = False
            state[CARTS_BY_ORDER_ID][CHECK_REQUEST] = False
            state[CHECKOUT_DATA][CHECK_REQUEST] = False

            state[CARTS][STATUS_CODE] = 200
            state[CARTS_BY_ORDER_ID][STATUS_CODE] = 200
            state[CHECKOUT_DATA][STATUS_CODE] = 200

            state[CARTS][RESPONSE_BODY] = {'items': []}
            state[CARTS_BY_ORDER_ID][RESPONSE_BODY] = {'items': []}
            state[CHECKOUT_DATA][RESPONSE_BODY] = {'items': []}

        def carts_times_called(self):
            return check_carts.times_called

        def carts_by_order_id_times_called(self):
            return check_carts_by_order_id.times_called

        def checkout_data_times_called(self):
            return check_checkout_data.times_called

        def check_carts_request(self, item_ids=None, fields=None):
            state[CARTS][CHECK_REQUEST] = True
            if item_ids is not None:
                state[CARTS][ITEM_IDS] = item_ids
            if fields is not None:
                state[CARTS][FIELDS] = fields

        def check_carts_by_order_id_request(self, item_ids=None, fields=None):
            state[CARTS_BY_ORDER_ID][CHECK_REQUEST] = True
            if item_ids is not None:
                state[CARTS_BY_ORDER_ID][ITEM_IDS] = item_ids
            if fields is not None:
                state[CARTS_BY_ORDER_ID][FIELDS] = fields

        def check_checkout_data_request(self, item_ids=None, fields=None):
            state[CHECKOUT_DATA][CHECK_REQUEST] = True
            if item_ids is not None:
                state[CHECKOUT_DATA][ITEM_IDS] = item_ids
            if fields is not None:
                state[CHECKOUT_DATA][FIELDS] = fields

        def set_carts_response(self, status_code=200, items=None):
            if not items:
                items = []

            state[CARTS][STATUS_CODE] = status_code
            state[CARTS][RESPONSE_BODY] = {'items': items}

        def set_carts_by_order_id_response(self, status_code=200, items=None):
            if not items:
                items = []

            state[CARTS_BY_ORDER_ID][STATUS_CODE] = status_code
            state[CARTS_BY_ORDER_ID][RESPONSE_BODY] = {'items': items}

        def set_checkout_data_response(self, status_code=200, items=None):
            if not items:
                items = []

            state[CHECKOUT_DATA][STATUS_CODE] = status_code
            state[CHECKOUT_DATA][RESPONSE_BODY] = {'items': items}

    context = Context()
    return context
