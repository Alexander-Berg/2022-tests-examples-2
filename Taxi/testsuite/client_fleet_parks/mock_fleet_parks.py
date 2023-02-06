"""
Mocks for fleet-parks.
"""

import pytest

RESPONSE500 = {'code': '500', 'message': 'InternalError'}


class FleetParksContext:
    def __init__(self, load_json):
        self.parks = load_json('parks.json')
        self.return_error = False
        self.mock_parks_list = None
        self.times_called = 0

    def set_parks(self, parks):
        self.parks = parks

    def set_return_error(self):
        self.return_error = True


@pytest.fixture
def mock_fleet_parks_list(mockserver, load_json):
    context = FleetParksContext(load_json)

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_parks_list(request):
        context.times_called += 1
        if context.return_error:
            return mockserver.make_response(json=RESPONSE500, status=500)
        ids = set(request.json.get('query').get('park').get('ids'))
        return {'parks': [park for park in context.parks if park['id'] in ids]}

    context.mock_parks_list = _mock_parks_list

    return context


@pytest.fixture
def fleet_parks_shard(mockserver):
    @mockserver.json_handler('/fleet-parks/v1/shard/info')
    def mock_shard_info(request):
        park_id = request.json.get('park_id')
        if not park_id:
            return mockserver.make_response(
                'park id is null or empty' % park_id, status=403,
            )

        return {
            'orders': {'table_name': 'orders_0', 'shard_number': 0},
            'payments': {'table_name': 'payments_0', 'shard_number': 0},
            'transactions': {
                'table_name': 'transactions_0',
                'shard_number': 0,
            },
            'payments_agg': {
                'table_name': 'payments_agg_0',
                'shard_number': 0,
            },
            'changes': {'table_name': 'changes_0', 'shard_number': 0},
            'feedbacks': {'table_name': 'feedbacks_0', 'shard_number': 0},
            'passengers': {'table_name': 'passengers_0', 'shard_number': 0},
        }

    return mock_shard_info
