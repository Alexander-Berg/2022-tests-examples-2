# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import dataclasses
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import pytest

from driver_priority_plugins import *  # noqa: F403 F401


PRIORITY_TOPIC = 'priority'
PRIORITY_TOPIC_TAGS: List[str] = ['silver', 'platinum', 'tag1', 'tag3', 'tag5']


@pytest.fixture
def service_client_default_headers():
    return {'Accept-Language': 'en'}


def pytest_collection_modifyitems(config, items):
    for item in items:
        item.add_marker(pytest.mark.geoareas(filename='geoareas.json'))
        item.add_marker(pytest.mark.tariffs(filename='tariffs.json'))


@pytest.fixture(name='tags_v1_topics_relations', autouse=True)
def mock_tags_v1_topics_relations(mockserver):
    @mockserver.json_handler('/tags/v1/topics_relations')
    def _mock_v1_topics_relations(request):
        body = request.json
        assert body['only_cached'] is False
        assert body['topics'] == [PRIORITY_TOPIC]
        return {'priority': PRIORITY_TOPIC_TAGS}


_DRIVER_TAXIMETER_MARKER = 'driver_taximeter'
_DRIVERS_CAR_IDS_MARKER = 'drivers_car_ids'
_DRIVER_TRACKSTORY_MARKER = 'driver_trackstory'
_FLEET_VEHICLES_MARKER = 'fleet_vehicles'
_UNIQUE_DRIVERS_MARKER = 'unique_drivers'


class DriverProfilesContext:
    def __init__(self):
        self.taximeters = {}
        self.car_ids = {}
        self.count_calls = {}

    def reset(self):
        self.taximeters = {}
        self.car_ids = {}
        self.count_calls = {}

    def set_taximeter_info(
            self,
            profile: str,
            platform: Optional[str] = None,
            version: Optional[str] = None,
            version_type: Optional[str] = None,
    ):
        taximeter = {}
        if platform is not None:
            taximeter['platform'] = platform
        if version is not None:
            taximeter['version'] = version
        if version_type is not None:
            taximeter['version_type'] = version_type
        self.taximeters[profile] = taximeter

    def set_car_ids(self, data):
        assert isinstance(data, dict)
        self.car_ids = data

    def add_calls(self, handler):
        self.count_calls.setdefault(handler, 0)
        self.count_calls[handler] += 1

    def has_calls(self, handler: str):
        return self.count_calls.get(handler, 0) != 0


def pytest_configure(config):
    config.addinivalue_line(
        'markers', f'{_DRIVER_TAXIMETER_MARKER}: driver profiles taximeter',
    )
    config.addinivalue_line(
        'markers', f'{_DRIVERS_CAR_IDS_MARKER}: driver profiles car_ids',
    )
    config.addinivalue_line(
        'markers', f'{_DRIVER_TRACKSTORY_MARKER}: driver trackstory',
    )
    config.addinivalue_line(
        'markers', f'{_FLEET_VEHICLES_MARKER}: fleet vehicles',
    )
    config.addinivalue_line(
        'markers', f'{_UNIQUE_DRIVERS_MARKER}: unique drivers',
    )


@pytest.fixture(name='driver_profiles_mocks')
def _driver_profiles_mocks(mockserver):
    driver_profiles_context = DriverProfilesContext()

    @mockserver.json_handler(
        '/driver-profiles/v1/driver/app/profiles/retrieve',
    )
    def _mock_v1_driver_app_profiles_retrieve(request):
        driver_profiles_context.add_calls('profiles/retrieve')

        profiles = []

        for dbid_uuid in request.json['id_in_set']:
            taximeter = driver_profiles_context.taximeters.get(dbid_uuid, None)
            assert taximeter is not None
            data = {}
            if 'data.taximeter_platform' in request.json['projection']:
                assert 'platform' in taximeter
                data['taximeter_platform'] = taximeter['platform']
            if 'data.taximeter_version' in request.json['projection']:
                assert 'version' in taximeter
                data['taximeter_version'] = taximeter['version']
            if 'data.taximeter_version_type' in request.json['projection']:
                assert 'version_type' in taximeter
                data['taximeter_version_type'] = taximeter['version_type']

            profiles.append(
                {'park_driver_profile_id': dbid_uuid, 'data': data},
            )

        return {'profiles': profiles}

    @mockserver.json_handler(
        '/driver-profiles/v1/vehicle_bindings/cars/retrieve_by_driver_id',
    )
    def _mock_cars_retrieve_by_driver_id(request):
        driver_profiles_context.add_calls('cars/retrieve_by_driver_id')
        assert request.args == {'consumer': 'driver-priority'}

        profiles = []
        for driver_id in request.json['id_in_set']:
            assert driver_id
            for part in driver_id.split('_'):
                assert part
            profile = {'park_driver_profile_id': driver_id}
            if driver_id in driver_profiles_context.car_ids:
                profile['data'] = {
                    'car_id': driver_profiles_context.car_ids[driver_id],
                }
            profiles.append(profile)
        return {'profiles': profiles}

    return driver_profiles_context


@pytest.fixture(name='driver_profiles_fixture', autouse=True)
def _driver_profiles_fixture(driver_profiles_mocks, request):
    driver_profiles_mocks.reset()

    # If not set, driver profile will have no tags specified
    for marker in request.node.iter_markers(_DRIVER_TAXIMETER_MARKER):
        if marker.kwargs:
            driver_profiles_mocks.set_taximeter_info(**marker.kwargs)

    for marker in request.node.iter_markers(_DRIVERS_CAR_IDS_MARKER):
        if marker.kwargs:
            driver_profiles_mocks.set_car_ids(**marker.kwargs)

    yield driver_profiles_mocks

    driver_profiles_mocks.reset()


@dataclasses.dataclass
class TrackstoryContext:
    positions: Dict[str, Any] = dataclasses.field(default_factory=dict)
    calls: int = 0

    def add_call(self):
        self.calls += 1

    def reset(self):
        self.positions = {}
        self.calls = 0

    def set_positions(self, driver_id, lat, lon):
        self.positions[driver_id] = {
            'direction': 36,
            'speed': 2.243076218814374,
            'timestamp': 1600861713,
            'lat': lat,
            'lon': lon,
        }


@pytest.fixture(name='driver_trackstory_mock', autouse=True)
def mock_driver_trackstory_position(mockserver):
    context = TrackstoryContext({})

    @mockserver.json_handler('/driver-trackstory/query/positions')
    def _trackstory_position_fail(request):
        context.add_call()

        driver_ids = request.json['driver_ids']
        assert len(driver_ids) == 1
        driver_id = driver_ids[0]
        if driver_id not in context.positions:
            return mockserver.make_response(json={'results': [[]]}, status=200)

        return mockserver.make_response(
            json={
                'results': [
                    [
                        {
                            'position': context.positions[driver_id],
                            'source': 'Adjusted',
                        },
                    ],
                ],
            },
            status=200,
        )

    return context


@pytest.fixture(name='driver_trackstory_fixture', autouse=True)
def _driver_trackstory_fixture(driver_trackstory_mock, request):
    driver_trackstory_mock.reset()

    for marker in request.node.iter_markers(_DRIVER_TRACKSTORY_MARKER):
        if 'positions' in marker.kwargs:
            for _, position in marker.kwargs['positions'].items():
                for required_key in ['lon', 'lat', 'timestamp']:
                    assert required_key in position
            driver_trackstory_mock.positions = marker.kwargs['positions']

    yield driver_trackstory_mock
    driver_trackstory_mock.reset()


@pytest.fixture(name='mock_yagr', autouse=True)
def mock_yagr(mockserver):
    @mockserver.json_handler('/yagr-raw/service/v2/position/store')
    def _position_store(request):
        assert False, 'client do not know position and cannot store it'

    return _position_store


@dataclasses.dataclass
class VehiclesContext:
    vehicles: Dict[str, Any] = dataclasses.field(default_factory=dict)
    calls: int = 0

    def reset(self):
        self.vehicles = {}
        self.calls = 0

    def add_calls(self, calls=1):
        self.calls = self.calls + calls

    def has_calls(self):
        return self.calls > 0


@pytest.fixture(name='mock_fleet_vehicles', autouse=True)
def _mock_fleet_vehicles(mockserver):
    context = VehiclesContext()

    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/cache-retrieve')
    def _vehicles_cache_retrieve(request):
        context.add_calls()
        assert request.args == {'consumer': 'driver-priority'}
        assert request.json['projection'] == ['data.year']
        ids = request.json['id_in_set']
        vehicles = []
        for park_id_car_id in ids:
            for part in park_id_car_id.split('_'):
                assert part
            vehicle = {'park_id_car_id': park_id_car_id}
            if park_id_car_id in context.vehicles:
                vehicle['data'] = context.vehicles[park_id_car_id]
            vehicles.append(vehicle)

        return mockserver.make_response(
            json={'vehicles': vehicles}, status=200,
        )

    return context


@pytest.fixture(name='fleet_vehicles_fixture', autouse=True)
def _fleet_vehicles_fixture(mock_fleet_vehicles, request):
    mock_fleet_vehicles.reset()

    for marker in request.node.iter_markers(_FLEET_VEHICLES_MARKER):
        if 'data' in marker.kwargs:
            data = marker.kwargs['data']
            for park_id_car_id, vehicle_data in data.items():
                assert park_id_car_id
                mock_fleet_vehicles.vehicles[park_id_car_id] = {
                    'year': vehicle_data.get('year'),
                }

    yield mock_fleet_vehicles

    mock_fleet_vehicles.reset()


@dataclasses.dataclass
class DriverProfilesByUniquesContext:
    ids: Dict[str, Any] = dataclasses.field(default_factory=dict)
    calls: int = 0

    def reset(self):
        self.ids = {}
        self.calls = 0

    def add_calls(self, calls=1):
        self.calls = self.calls + calls

    def has_calls(self):
        return self.calls > 0


@pytest.fixture(name='mock_unique_drivers', autouse=True)
def _mock_unique_drivers(mockserver):
    context = DriverProfilesByUniquesContext()

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/profiles/retrieve_by_uniques',
    )
    def _retrieve_by_uniques(request):
        context.add_calls()
        assert request.args == {'consumer': 'driver-priority'}

        ids = request.json['id_in_set']
        profiles = []
        for unique_driver_id in ids:
            driver_profiles = context.ids.get(unique_driver_id, [])
            if not driver_profiles:
                continue
            data = [
                {
                    'driver_profile_id': driver_profile_id,
                    'park_id': park_id,
                    'park_driver_profile_id': f'{park_id}_{driver_profile_id}',
                }
                for park_id, driver_profile_id in driver_profiles
            ]
            profiles.append(
                {'unique_driver_id': unique_driver_id, 'data': data},
            )

        return mockserver.make_response(
            json={'profiles': profiles}, status=200,
        )

    return context


@pytest.fixture(name='unique_drivers_fixture', autouse=True)
def _unique_drivers_fixture(mock_unique_drivers, request):
    mock_unique_drivers.reset()

    for marker in request.node.iter_markers(_UNIQUE_DRIVERS_MARKER):
        if 'data' in marker.kwargs:
            data = marker.kwargs['data']
            for unique_driver_id, dbid_uuids in data.items():
                mock_unique_drivers.ids[unique_driver_id] = dbid_uuids

    yield mock_unique_drivers

    mock_unique_drivers.reset()


@pytest.fixture(name='driver_ui_profile_v1_mode', autouse=True)
def mock_driver_ui_profile_v1_mode(mockserver):
    @mockserver.json_handler('/driver-ui-profile/v1/mode')
    def _mock_driver_ui_profile_v1_mode(request):
        return mockserver.make_response(
            json={'display_mode': 'taxi', 'display_profile': 'driver'},
            status=200,
        )
