from aiohttp import web
import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from blocklist_plugins import *  # noqa: F403 F401

from tests_blocklist import dates
from tests_blocklist import utils


@pytest.fixture(name='predicate_request')
def _get_predicate_request(load_json):
    list_request = load_json('predicate_request.json')
    return list_request


@pytest.fixture(name='list_request')
def _get_list_request(load_json):
    list_request = load_json('list_request.json')
    return list_request


@pytest.fixture(name='headers')
def _get_headers(load_json):
    headers = load_json('admin_headers.json')
    return headers


@pytest.fixture(name='add_request')
def _get_add_request(load_json):
    add_request = load_json('add_request.json')
    return add_request


class ApiOverDataUpdates:
    def __init__(self, data):
        self.data = data if data else []

    def updates(self, last_revision=None):
        if not last_revision:
            return self.data
        return [x for x in self.data if x['revision'] > last_revision]

    def get(self, **kwargs):
        try:
            return next(iter(self.get_all(**kwargs)))
        except StopIteration:
            return None

    def get_all(self, **kwargs):

        result = []
        for item in self.data:
            flat_item = utils.flatten(item)
            if all([flat_item.get(k) == kwargs[k] for k in kwargs]):
                result.append(item)
        return result


class FleetVehiclesContext:
    def __init__(self):
        self.park_id_car_ids = {}

    def set_park_cars(self, park_id_car_ids):
        self.park_id_car_ids = park_id_car_ids


@pytest.fixture(autouse=True)
def fleet_vehicles(request, mockserver, load_json):
    marker = request.node.get_closest_marker('fleet_vehicles')
    data = marker.args[0] if marker else load_json('fleet_vehicles.json')
    updates = ApiOverDataUpdates(data)
    context = FleetVehiclesContext()

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

    @mockserver.json_handler(
        '/fleet-vehicles/v1/vehicles/retrieve_by_number_with_normalization',
    )
    def _mock_retrieve_by_car_number(request):
        result = []
        for i in request.json.get('numbers_in_set', []):
            for x in context.park_id_car_ids.get(i):
                x['number'] = i.lower()
                val = {'data': x, 'park_id_car_id': x['park_id_car_id']}
                result.append(val)

        return {'vehicles': result}

    return context


class DriverProfilesContext:
    def __init__(self):
        self.cars_drivers = {}
        self.licenses_drivers = {}
        self.licenses_data = {}
        self.park_id_car_id_drivers = {}
        self.drivers_app_profile = {}

    def set_cars_drivers(self, cars_drivers):
        self.cars_drivers = cars_drivers

    def set_licenses_drivers(self, licenses_drivers):
        self.licenses_drivers = licenses_drivers

    def set_park_id_car_ids_drivers(self, park_id_car_id_drivers):
        self.park_id_car_id_drivers = park_id_car_id_drivers

    def set_drivers_app_profile(self, drivers_app_profile):
        self.drivers_app_profile = drivers_app_profile


@pytest.fixture(autouse=True)
def driver_profiles(request, mockserver, load_json):
    marker = request.node.get_closest_marker('driver_profiles')
    data = marker.args[0] if marker else load_json('driver_profiles.json')
    updates = ApiOverDataUpdates(data)
    context = DriverProfilesContext()

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
        '/driver-profiles/v1/driver/app/profiles/retrieve',
    )
    def _app_profiles_retrieve(request):
        result = []

        for i in request.json.get('id_in_set', []):
            result.append(
                {
                    'data': context.drivers_app_profile[i],
                    'park_driver_profile_id': i,
                },
            )

        return {'profiles': result}

    @mockserver.json_handler(
        '/driver-profiles/v1/driver/profiles/retrieve_by_park_id',
    )
    def _mock_retrieve_by_park_id(request):
        result = []

        for i in request.json.get('park_id_in_set', []):
            result.append(
                {
                    'park_id': i,
                    'profiles': [
                        {'data': {}, 'park_driver_profile_id': x}
                        for x in context.cars_drivers.get(i, [])
                    ],
                },
            )

        return {'profiles_by_park_id': result}

    @mockserver.json_handler(
        '/driver-profiles/v1/driver/profiles/retrieve_by_license',
    )
    def _mock_retrieve_by_license_id(request):
        result = []

        for i in request.json.get('driver_license_in_set', []):
            result.append(
                {
                    'driver_license': i,
                    'profiles': [
                        {
                            'data': x,
                            'park_driver_profile_id': x['driver_profile_id'],
                        }
                        for x in context.licenses_drivers.get(i, [])
                    ],
                },
            )

        return {'profiles_by_license': result}

    @mockserver.json_handler(
        '/driver-profiles/v1/vehicle_bindings'
        '/drivers/retrieve_by_park_id_car_id',
    )
    def _mock_retrieve_by_park_id_car_id(request):
        result = []

        for i in request.json.get('park_id_car_id_in_set', []):
            result.append(
                {
                    'park_id_car_id': i,
                    'profiles': [
                        {
                            'data': x,
                            'park_driver_profile_id': x['driver_profile_id'],
                        }
                        for x in context.park_id_car_id_drivers.get(i, [])
                    ],
                },
            )

        return {'profiles_by_park_id_car_id': result}

    return context


class DriverProtocolContext:
    def __init__(self):
        self.messages = []

    def get_messages(self):
        return self.messages


@pytest.fixture(name='driver_protocol')
def _driver_protocol(mockserver):
    context = DriverProtocolContext()

    @mockserver.json_handler('/driver-protocol/service/chat/add')
    def _add_handler(request):
        context.messages.append(
            {
                'channel': request.json.get('channel'),
                'park_id': request.args.get('db'),
                'driver_id': request.json.get('driver'),
                'source': request.json.get('user_login'),
                'message': request.json.get('msg'),
            },
        )
        return mockserver.make_response('', 200)

    return context


class FleetNotificationsContext:
    def __init__(self):
        self.messages = []
        self.parks = []

    def get_messages(self):
        return self.messages

    def set_parks(self, parks):
        self.parks = parks


@pytest.fixture(name='fleet_notifications')
def _fleet_notifications(mockserver):
    context = FleetNotificationsContext()

    @mockserver.json_handler(
        '/fleet-notifications/v1/notifications/external-message',
    )
    def _retrieve_fleet_notifications_handler(request):
        context.messages.append(
            {
                'park_id': request.json['destinations'],
                'title': request.json['payload']['title'],
                'message': request.json['payload']['text'],
                'notification_types': request.json['notification_types'],
            },
        )
        return mockserver.make_response('', 200)

    return context


@pytest.fixture(name='fleet_notifications_with_exceptions')
def _fleet_notifications_with_exceptions(mockserver):
    context = FleetNotificationsContext()

    @mockserver.json_handler(
        '/fleet-notifications/v1/notifications/external-message',
    )
    def _retrieve_fleet_notifications_handler(request):
        allowed_parks = set(d['park_id'] for d in request.json['destinations'])
        if allowed_parks & set(context.parks):
            context.messages.append(
                {
                    'park_id': request.json['destinations'],
                    'title': request.json['payload']['title'],
                    'message': request.json['payload']['text'],
                    'notification_types': request.json['notification_types'],
                },
            )
            return mockserver.make_response('', 200)

        return mockserver.make_response('', 400)

    return context


class PersonalContext:
    def __init__(self):
        self.data = dict()

    def set_data(self, data):
        self.data = data


@pytest.fixture(name='personal')
def _personal(mockserver):
    context = PersonalContext()

    @mockserver.json_handler('/personal/v1/driver_licenses/bulk_retrieve')
    def _retrieve_pd_handler(request):
        result = []
        driver_licenses = context.data.get('driver_licenses', [])

        for item in request.json.get('items', []):
            item_id = item['id']
            if item_id in driver_licenses:
                result.append(
                    {'id': item_id, 'value': driver_licenses[item_id]},
                )

        return {'items': result}

    return context


class FleetParksContext:
    def __init__(self):
        self.parks = {}

    def set_parks(self, parks):
        self.parks = parks


@pytest.fixture(name='fleet_parks')
def fleet_parks(mockserver):
    context = FleetParksContext()

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_retrieve_park_list(request):
        result = []
        for i in request.json['query']['park']['ids']:
            result.append(context.parks[i])
        return {'parks': result}

    return context


@pytest.fixture(name='fleet_parks_with_exceptions')
def fleet_parks_with_exceptions(mockserver):
    context = FleetParksContext()

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_retrieve_park_list(request):
        result = []
        for i in request.json['query']['park']['ids']:
            if i not in context.parks:
                return mockserver.make_response('', 400)
            result.append(context.parks[i])
        return {'parks': result}

    return context
