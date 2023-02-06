# pylint: disable=redefined-outer-name
import uuid

from aiohttp import web
import pytest

from taxi.generated import db_settings
from taxi.util import dates
from taxi.util import dictionary
from taxi.util import itertools_ext

import taxi_qc_exams.generated.service.mongo.plugin as mongo_plugin
import taxi_qc_exams.generated.service.pytest_init  # noqa:F401

pytest_plugins = [
    'taxi_qc_exams.generated.service.pytest_plugins',
    'taxi.pytest_plugins.experiments',  # experiments1.0 are obsolete
]


class PersonalContext:
    def __init__(self):
        self._storage = dict(license=dict(by_number={}, by_id={}))

    def add(self, pd_type, number, pd_id):
        bucket = self._storage.setdefault(
            pd_type, dict(by_number={}, by_id={}),
        )
        bucket['by_number'][number] = pd_id
        bucket['by_id'][pd_id] = number

    def get(self, pd_type, number=None, pd_id=None):
        bucket = self._storage.setdefault(
            pd_type, dict(by_number={}, by_id={}),
        )
        if number:
            return bucket['by_number'].get(number)
        if pd_id:
            return bucket['by_id'].get(pd_id)

        return bucket


@pytest.fixture
def personal(mockserver):
    context = PersonalContext()

    @mockserver.json_handler('/personal/v1/driver_licenses/find')
    def _driver_licenses_find(request):
        number = request.json['value']
        pd_id = context.get('license', number=number)
        if not pd_id:
            return web.json_response(
                status=404, data=dict(code='NotFound', message='not found'),
            )
        return web.json_response(data=dict(id=pd_id, value=number))

    @mockserver.json_handler('/personal/v1/driver_licenses/store')
    def _driver_licenses_store(request):
        number = request.json['value']
        pd_id = context.get('license', number=number) or uuid.uuid4().hex
        context.add('license', number=number, pd_id=pd_id)
        return web.json_response(data=dict(id=pd_id, value=number))

    return context


class ApiOverDataUpdates:
    def __init__(self, data):
        self.data = data if data else []

    def updates(self, last_revision=None):
        if not last_revision:
            return self.data
        return [x for x in self.data if x['revision'] > last_revision]

    def get(self, **kwargs):
        return itertools_ext.first(self.get_all(**kwargs))

    def get_all(self, **kwargs):
        result = []
        for item in self.data:
            flat_item = dictionary.flatten(item)
            if all([flat_item.get(k) == kwargs[k] for k in kwargs]):
                result.append(item)
        return result


@pytest.fixture
def fleet_vehicles(request, mockserver, load_json):
    marker = request.node.get_closest_marker('fleet_vehicles')
    data = marker.args[0] if marker else load_json('fleet_vehicles.json')
    updates = ApiOverDataUpdates(data)

    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/updates')
    def _mock_updates(request):
        revision = request.query.get(
            'last_known_revision',
        ) or request.json.get('last_known_revision')
        entities = updates.updates(revision)
        headers = {'X-Polling-Delay-Ms': '0'}
        data = {'vehicles': []}
        if entities:
            data['vehicles'] = entities
            data['last_revision'] = entities[-1]['revision']
            data['last_modified'] = dates.timestring(dates.utcnow(), 'UTC')

        return web.json_response(data=data, headers=headers)

    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/retrieve')
    def _mock_retrieve(request):
        vehicles = []
        for park_id_car_id in request.json['id_in_set']:
            data = updates.get(park_id_car_id=park_id_car_id)
            if not data:
                data = dict(park_id_car_id=park_id_car_id)
            vehicles.append(data)

        return web.json_response(data=dict(vehicles=vehicles))


@pytest.fixture
def driver_profiles(request, mockserver, load_json):
    marker = request.node.get_closest_marker('driver_profiles')
    data = marker.args[0] if marker else load_json('driver_profiles.json')
    updates = ApiOverDataUpdates(data)

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/updates')
    def _mock_updates(request):
        revision = request.query.get(
            'last_known_revision',
        ) or request.json.get('last_known_revision')
        entities = updates.updates(revision)
        headers = {'X-Polling-Delay-Ms': '0'}
        data = {'profiles': []}
        if entities:
            data['profiles'] = entities
            data['last_revision'] = entities[-1]['revision']
            data['last_modified'] = dates.timestring(dates.utcnow(), 'UTC')

        return web.json_response(data=data, headers=headers)

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _mock_retrieve(request):
        profiles = []
        for park_driver_profile_id in request.json['id_in_set']:
            data = updates.get(park_driver_profile_id=park_driver_profile_id)
            if not data:
                data = dict(park_driver_profile_id=park_driver_profile_id)
            profiles.append(data)

        return web.json_response(data=dict(profiles=profiles))

    @mockserver.json_handler(
        '/driver-profiles/v1/vehicle_bindings'
        '/drivers/retrieve_by_park_id_car_id',
    )
    def _mock_retrieve_by_car(request):
        profiles = []
        for park_id_car_id in request.json['park_id_car_id_in_set']:
            park_id, car_id = park_id_car_id.split('_', 1)
            data = updates.get_all(
                **{'data.park_id': park_id, 'data.car_id': car_id},
            )
            profiles.append(dict(park_id_car_id=park_id_car_id, profiles=data))

        return web.json_response(
            data=dict(profiles_by_park_id_car_id=profiles),
        )


@pytest.fixture(autouse=True)
def mock_mqc_collections(monkeypatch):
    monkeypatch.setitem(
        db_settings.COLLECTIONS,
        'mqc_confirmations',
        db_settings.CollectionData('mqc', 'mqc', 'confirmations'),
    )
    monkeypatch.setitem(
        db_settings.COLLECTIONS,
        'mqc_entities',
        db_settings.CollectionData('mqc', 'mqc', 'qc_entities'),
    )
    monkeypatch.setitem(
        db_settings.COLLECTIONS,
        'mqc_jobs_data',
        db_settings.CollectionData('mqc', 'mqc', 'qc_jobs_data'),
    )
    monkeypatch.setitem(
        db_settings.COLLECTIONS,
        'mqc_notifications',
        db_settings.CollectionData('mqc', 'mqc', 'qc_notifications'),
    )
    monkeypatch.setitem(
        db_settings.COLLECTIONS,
        'mqc_passes',
        db_settings.CollectionData('mqc', 'mqc', 'qc_passes'),
    )
    monkeypatch.setitem(
        db_settings.COLLECTIONS,
        'mqc_settings',
        db_settings.CollectionData('mqc', 'mqc', 'qc_settings'),
    )


@pytest.fixture(autouse=True)
def mock_mongo_plugin():
    # pylint: disable=W0212
    mongo_plugin._COLLECTIONS['mqc_confirmations'] = (
        'mqc',
        'mqc',
        'confirmations',
    )
    mongo_plugin._COLLECTIONS['mqc_entities'] = ('mqc', 'mqc', 'qc_entities')
    mongo_plugin._COLLECTIONS['mqc_jobs_data'] = ('mqc', 'mqc', 'qc_jobs_data')
    mongo_plugin._COLLECTIONS['mqc_passes'] = ('mqc', 'mqc', 'qc_passes')
    mongo_plugin._COLLECTIONS['mqc_settings'] = ('mqc', 'mqc', 'qc_settings')
    # pylint: enable=W0212


@pytest.fixture
def mongodb_settings(mongodb_settings):
    mongodb_settings['mqc_confirmations']['settings']['database'] = 'mqc'
    mongodb_settings['mqc_entities']['settings']['database'] = 'mqc'
    mongodb_settings['mqc_jobs_data']['settings']['database'] = 'mqc'
    mongodb_settings['mqc_notifications']['settings']['database'] = 'mqc'
    mongodb_settings['mqc_passes']['settings']['database'] = 'mqc'
    mongodb_settings['mqc_settings']['settings']['database'] = 'mqc'
    return mongodb_settings
