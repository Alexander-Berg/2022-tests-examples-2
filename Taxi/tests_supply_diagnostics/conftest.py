import json

import pytest
# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from supply_diagnostics_plugins import *  # noqa: F403 F401


@pytest.fixture(autouse=True)
def mock_parks_activation(mockserver):
    @mockserver.handler('/parks-activation/v1/parks/activation/updates')
    def _updates(request):
        parks1 = [
            {
                'revision': 1,
                'last_modified': '1970-01-15T03:56:07.000',
                'park_id': 'park1',
                'city_id': 'spb',
                'data': {
                    'deactivated': False,
                    'can_cash': False,
                    'can_card': False,
                    'can_coupon': True,
                    'can_corp': False,
                },
            },
            {
                'revision': 2,
                'last_modified': '1970-01-15T03:56:07.000',
                'park_id': 'park2',
                'city_id': 'spb',
                'data': {
                    'deactivated': True,
                    'deactivated_reason': 'reason1',
                    'can_cash': True,
                    'can_card': True,
                    'can_coupon': False,
                    'can_corp': True,
                },
            },
            {
                'revision': 3,
                'last_modified': '1970-01-15T03:56:07.000',
                'park_id': 'park3',
                'city_id': 'spb',
                'data': {
                    'deactivated': True,
                    'deactivated_reason': 'reason2',
                    'can_cash': True,
                    'can_card': True,
                    'can_coupon': False,
                    'can_corp': True,
                },
            },
        ]
        last_known_revision = request.json.get('last_known_revision', -1)
        parks2 = [park for park in parks1 if park['revision'] != 2]
        holes = request.json.get('additional_revisions')
        parks = parks1 if holes else parks2
        parks = [
            park
            for park in parks
            if (
                park['revision'] > last_known_revision
                or park['revision'] in holes
            )
        ]
        response_json = {'last_revision': 3, 'parks_activation': parks}
        return mockserver.make_response(json.dumps(response_json), 200)


@pytest.fixture(autouse=True)
def mock_tracker_analytics(mockserver):
    @mockserver.json_handler('/tracker-analytics/1.0/drivers-positions')
    def _driver_profiles(request):
        return {
            'drivers': [
                {
                    'driver_id': 'dbid3_uuid3',
                    'park_db_id': 'dbid3',
                    'driver_uuid': 'uuid3',
                    'driver_status': 'status',
                    'tx_status': 'status',
                    'geopoint': [37.876763, 44.79853699999753],
                    'car_classes': ['econom', 'business'],
                    'unique_driver_id': 'dbid1_uuid1',
                    'allowed_payment_methods': ['card', 'cash'],
                },
            ],
        }
