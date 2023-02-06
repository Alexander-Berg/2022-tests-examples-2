import pytest

LAST_CURSOR = 'last_cursor'
SHIFTS_V2 = [
    {
        'store_id': '12345567',
        'store_external_id': 'depot_id_1',
        'courier_id': 'courier_id_1',
        'shift_id': '12345',
        'status': 'in_progress',
        'started_at': '2021-01-24T17:19:00+00:00',
        'closes_at': '2021-01-24T18:19:00+00:00',
        'updated_ts': '2021-01-24T17:19:00+00:00',
    },
    {
        'store_id': '12345567',
        'store_external_id': 'depot_id_3',
        'courier_id': 'courier_id_3',
        'shift_id': '23545',
        'status': 'waiting',
        'started_at': '2021-01-24T17:19:00+00:00',
        'closes_at': '2021-01-24T18:19:00+00:00',
        'updated_ts': '2021-01-24T17:19:00+00:00',
    },
    {
        'store_id': '12345567',
        'store_external_id': 'depot_id_4',
        'courier_id': 'courier_id_4',
        'shift_id': '25234',
        'status': 'paused',
        'started_at': '2021-01-24T17:19:00+00:00',
        'closes_at': '2021-01-24T18:19:00+00:00',
        'updated_ts': '2021-01-24T17:19:00+00:00',
    },
    {
        'store_id': '12345567',
        'store_external_id': 'depot_id_2',
        'courier_id': 'courier_id_2',
        'shift_id': '54321',
        'status': 'closed',
        'started_at': '2021-01-24T17:19:00+00:00',
        'closes_at': '2021-01-24T18:19:00+00:00',
        'updated_ts': '2021-01-24T17:19:00+00:00',
    },
    {
        'store_id': '12345567',
        'store_external_id': 'depot_id_2',
        'courier_id': None,
        'shift_id': '54325',
        'status': 'request',
        'started_at': '2021-01-24T17:19:00+00:00',
        'closes_at': '2021-01-24T18:19:00+00:00',
        'updated_ts': '2021-01-24T17:19:00+00:00',
    },
    {
        'store_id': '12345567',
        'store_external_id': 'depot_id_2',
        'courier_id': 'courier_id_0',
        'shift_id': '54329',
        'status': 'closed',
        'started_at': None,
        'closes_at': None,
        'updated_ts': '2021-01-24T17:19:00+00:00',
    },
]


@pytest.fixture(autouse=False, name='grocery_wms')
def mock_grocery_wms(mockserver):
    class Context:
        def __init__(self):
            self.shifts = None

        def set_couriers_shifts(self, shifts):
            self.shifts = shifts

    context = Context()

    @mockserver.json_handler(
        '/grocery-wms/api/external/courier_shifts_v2/updates',
    )
    def _mock_wms_shifts_updates_v2(request):
        assert request.json['filter'] == 'all'
        shifts = context.shifts
        if shifts is None:
            shifts = SHIFTS_V2

        if request.json['cursor'] == LAST_CURSOR:
            return {'cursor': LAST_CURSOR, 'shifts': []}

        return {'cursor': LAST_CURSOR, 'shifts': shifts}

    return context
