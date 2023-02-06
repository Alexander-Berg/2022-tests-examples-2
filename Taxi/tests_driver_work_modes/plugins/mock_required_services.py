# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=redefined-outer-name
import pytest

from tests_driver_work_modes import utils


BILLING_CLIENT_ID = '123'
NOW = '2021-02-19T22:46:00+00:00'


def _make_parks_replica_response(clids):
    return {
        'parks': [
            {'park_id': clid, 'billing_client_id': BILLING_CLIENT_ID}
            for clid in clids
        ],
    }


def _make_fleet_parks_response(parks_params):
    return {'parks': [utils.make_park(**param) for param in parks_params]}


def _make_driver_profiles_response(driver_params):
    return {
        'profiles_by_park_id': [
            {
                'park_id': 'park1',
                'profiles': [
                    {
                        'park_driver_profile_id': 'park_driver_id',
                        'data': {
                            'work_status': param['status'],
                            'uuid': param['driver_id'],
                        },
                    }
                    for param in driver_params
                ],
            },
        ],
    }


def _make_parks_replica_request():
    return {'billing_client_ids': [BILLING_CLIENT_ID], 'at': NOW}


def _make_fleet_parks_request(clids):
    return {'query': {'park': {'clids': clids}}}


def _make_driver_profiles_request(parks_params):
    parks = _make_fleet_parks_response(parks_params)['parks']
    park_ids = [
        park['id']
        for park in parks
        if park['is_active'] and park['driver_partner_source']
    ]
    return {
        'park_id_in_set': park_ids,
        'projection': ['data.work_status', 'data.uuid'],
    }


@pytest.fixture(name='mock_required_services')
def _mock_required_services(mockserver):
    class Context:
        def __init__(self):
            self.clids = []
            self.parks_params = []
            self.driver_params = []
            self.make_driver_response = True

        def set_data(
                self,
                clids=None,
                parks_params=None,
                driver_params=None,
                make_driver_response=None,
        ):
            if clids is not None:
                self.clids = clids
            if parks_params is not None:
                self.parks_params = parks_params
            if driver_params is not None:
                self.driver_params = driver_params
            if make_driver_response is not None:
                self.make_driver_response = make_driver_response

        @property
        def has_mock_parks_replica_calls(self):
            return mock_parks_replica.has_calls

        @property
        def has_mock_driver_profiles_calls(self):
            return mock_driver_profiles.has_calls

        @property
        def has_mock_fleet_parks_calls(self):
            return mock_fleet_parks.has_calls

    context = Context()

    @mockserver.json_handler(
        '/parks-replica/v1/parks/by_billing_client_id/retrieve_bulk',
    )
    def mock_parks_replica(request):
        assert request.json == _make_parks_replica_request()
        return _make_parks_replica_response(context.clids)

    @mockserver.json_handler('/fleet-parks/v1/parks/list-by-clids')
    def mock_fleet_parks(request):
        assert request.json == _make_fleet_parks_request(context.clids)
        return _make_fleet_parks_response(context.parks_params)

    @mockserver.json_handler(
        '/driver-profiles/v1/driver/profiles/retrieve_by_park_id',
    )
    def mock_driver_profiles(request):
        assert request.json == _make_driver_profiles_request(
            context.parks_params,
        )
        if context.make_driver_response:
            return _make_driver_profiles_response(context.driver_params)
        return context.driver_params

    return context
