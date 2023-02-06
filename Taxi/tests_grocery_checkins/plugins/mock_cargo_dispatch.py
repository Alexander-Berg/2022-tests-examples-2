import pytest

DUMMY_CONFIRM_RESPONSE = {
    'result': 'test_result',
    'new_status': 'test_status',
    'new_route': [],
    'waybill_info': {
        'waybill': {
            'router_id': 'test_router_id',
            'external_ref': 'waybill_ref',
            'points': [],
            'taxi_order_requirements': {},
            'special_requirements': {'virtual_tariffs': []},
            'optional_return': False,
            'items': [],
        },
        'dispatch': {
            'revision': 10,
            'created_ts': '2021-01-24T18:18:00+01:00',
            'updated_ts': '2021-01-24T18:18:00+01:00',
            'is_waybill_accepted': True,
            'is_waybill_declined': False,
            'is_performer_assigned': True,
            'status': 'processing',
        },
        'execution': {'points': [], 'paper_flow': False, 'segments': []},
        'diagnostics': {},
        'segments': [],
    },
}


@pytest.fixture(name='cargo_dispatch', autouse=True)
def mock_cargo_dispatch(mockserver):
    class Context:
        def __init__(self):
            self.confirm_times_called = 0

    context = Context()

    @mockserver.json_handler('/cargo-dispatch/v1/waybill/exchange/confirm')
    def _mock_confirm(request):
        context.confirm_times_called += 1
        return DUMMY_CONFIRM_RESPONSE

    return context
