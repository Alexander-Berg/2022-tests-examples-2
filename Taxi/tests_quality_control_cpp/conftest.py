# pylint: disable=wildcard-import
# pylint: disable=unused-wildcard-import
# pylint: disable=import-error
# pylint: disable=redefined-outer-name
import json
import os

import pytest
from quality_control_cpp_plugins import *  # noqa: F403 F401


EMPTY_CURSOR_REQUEST = {
    'cursor': '1',
    'modified': '2019-01-16T17:28:55Z',
    'items': [
        {'id': '1', 'type': 'driver', 'exams': []},
        {'id': '2', 'type': 'driver', 'exams': []},
        {'id': '3', 'type': 'driver', 'exams': []},
        {'id': '4', 'type': 'driver', 'exams': []},
        {'id': '5', 'type': 'driver', 'exams': []},
        {'id': '6', 'type': 'driver', 'exams': []},
    ],
}

REQUEST_CURSOR_1 = {
    'cursor': '2',
    'modified': '2019-01-16T17:28:55Z',
    'items': [
        {'id': '1', 'type': 'driver', 'exams': []},
        {'id': '2', 'type': 'driver', 'exams': []},
        {'id': '3', 'type': 'driver', 'exams': []},
        {'id': '4', 'type': 'driver', 'exams': []},
        {'id': '7', 'type': 'driver', 'exams': []},
    ],
}


def _error_response(mockserver, error_message, status=400):
    return mockserver.make_response(
        json={'message': error_message}, status=status,
    )


@pytest.fixture(name='qc_state_mock', autouse=True)
def _qc_state_mock(mockserver):
    @mockserver.json_handler('/api/v1/state/list')
    def _qc_state_list_handler(request):
        cursor = request.args.getone('cursor', None)
        assert request.args['limit'] == '6'
        if cursor == '1':
            return REQUEST_CURSOR_1
        if not cursor:
            return EMPTY_CURSOR_REQUEST
        return {'cursor': '3', 'modified': '2019-01-16T17:28:55Z', 'items': []}


@pytest.fixture(autouse=True)
def _quality_control_mock(mockserver, load_json):
    @mockserver.handler('/quality-control/api/v1/state/list')
    def _api_v1_state_list(request):
        return mockserver.make_response(status=200, json=dict())


@pytest.fixture(name='remove_trash', scope='function', autouse=True)
def _remove_trash():
    assert os.system('rm -rf /tmp/quality-control-cpp/*') == 0


class ParksContext:
    def __init__(self):
        self.driver_profiles_lists = {}

    def set_driver_profiles_list(self, park_id, driver_uuid, filename):
        self.driver_profiles_lists['Park:' + park_id + driver_uuid] = filename


@pytest.fixture(name='parks')
def _parks(mockserver, load_json):
    context = ParksContext()

    @mockserver.json_handler('/parks/driver-profiles/list')
    def _driver_profiles_list(request):
        park = request.json.get('query', {}).get('park', {})
        park_id = park.get('id')
        driver_uuids = park.get('driver_profile', {}).get('id', [])
        fields = request.json.get('fields', [])
        if not park_id or not driver_uuids or not fields:
            return mockserver.make_response('{"message": "empty param"}', 400)

        key = 'Park:' + park_id + driver_uuids[0]
        if key not in context.driver_profiles_lists:
            return mockserver.make_response('{"message": "not found"}', 404)

        return mockserver.make_response(
            json.dumps(load_json(context.driver_profiles_lists[key])), 200,
        )

    return context


class TaximeterXServiceContext:
    def __init__(self):
        self.qc_pass_response = {}

    def set_qc_pass(self, pass_id, response):
        self.qc_pass_response['QcPass:' + pass_id] = response


@pytest.fixture(name='taximeter_xservice')
def _taximeter_xservice(mockserver, load_json):
    context = TaximeterXServiceContext()

    @mockserver.json_handler('/taximeter-xservice/utils/qc/pass')
    def _utils_qc_pass(request):
        pass_id = request.args.get('pass_id')
        if not pass_id:
            return mockserver.make_response('empty param', 400)

        key = 'QcPass:' + pass_id
        if key not in context.qc_pass_response:
            return mockserver.make_response('empty param', 400)

        return mockserver.make_response(
            json.dumps(context.qc_pass_response[key]), 200,
        )

    return context


class PlotvaMlContext:
    def __init__(self):
        self.verify_response = {}
        self.media_ids = {}

    def set_verify_response(self, response):
        self.verify_response = response

    def set_existing_media_ids(self, media_ids):
        self.media_ids = set(media_ids)


@pytest.fixture(name='plotva_ml')
def _plotva_ml(mockserver):
    context = PlotvaMlContext()

    @mockserver.json_handler('/plotva-ml/biometrics/verify/v1')
    def _verify_handler(request):
        request_media = (
            request.json['target_media'] + request.json['reference_media']
        )
        for media in request_media:
            for media_item in media['items']:
                assert media_item['id'] in context.media_ids
        return mockserver.make_response(
            json.dumps(context.verify_response), 200,
        )

    return context


class BiometryEtalonsContext:
    def __init__(self):
        self.retrieve_response = {}
        self.store_response = {}
        self.stored_media = {}

    def set_retrieve_response(self, response):
        self.retrieve_response = response

    def set_store_response(self, response):
        self.store_response = response


@pytest.fixture(name='biometry_etalons')
def _biometry_etalons(mockserver):
    context = BiometryEtalonsContext()

    @mockserver.json_handler('/biometry-etalons/service/v1/retrieve')
    def _retrieve_handler(request):
        return mockserver.make_response(
            json.dumps(context.retrieve_response), 200,
        )

    @mockserver.handler('/biometry-etalons/service/v1/store')
    def _store_handler(request):
        context.stored_media = request.json['etalon_media']
        return mockserver.make_response('{}', 200)

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
    def _retrieve_handler(request):
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

    def get_messages(self):
        return self.messages


@pytest.fixture(name='fleet_notifications')
def _fleet_notifications(mockserver):
    context = FleetNotificationsContext()

    @mockserver.json_handler(
        '/fleet-notifications/v1/notifications/external-message',
    )
    def _retrieve_handler(request):
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


# TODO Can it be merged with client-driver-profiles library?


class DriverProfilesContext:
    def __init__(self):
        self.cars_drivers = {}
        self.drivers_app_profile = {}

    def set_cars_drivers(self, cars_drivers):
        self.cars_drivers = cars_drivers

    def set_drivers_app_profile(self, drivers_app_profile):
        self.drivers_app_profile = drivers_app_profile


@pytest.fixture(name='driver_profiles', autouse=True)
def _driver_profiles(mockserver):
    context = DriverProfilesContext()
    prefix = '/driver-profiles/v1'

    @mockserver.json_handler(prefix + '/driver/profiles/retrieve')
    def _retrieve_handler(request):
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'something_random',
                    'data': {
                        'license_experience': {
                            # format from api-over-data
                            'some_category': '2020-01-01T00:00:00.000',
                        },
                    },
                },
            ],
        }

    @mockserver.json_handler(
        prefix + '/vehicle_bindings/drivers/retrieve_by_park_id_car_id',
    )
    def _retrieve_by_park_id_car_id(request):
        result = []

        for i in request.json.get('park_id_car_id_in_set', []):
            result.append(
                {
                    'park_id_car_id': i,
                    'profiles': [
                        {'data': {}, 'park_driver_profile_id': x}
                        for x in context.cars_drivers.get(i, [])
                    ],
                },
            )

        return {'profiles_by_park_id_car_id': result}

    @mockserver.json_handler(prefix + '/driver/app/profiles/retrieve')
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

    return context


@pytest.fixture(name='driver_trackstory', autouse=True)
def _driver_trackstory(mockserver, load_json):
    @mockserver.json_handler('/driver-trackstory/position')
    def _position(request):
        response_dict = load_json('driver_trackstory.json')
        if request.json['driver_id'] in response_dict:
            response = {
                'position': {
                    'direction': 36,
                    'speed': 2.243076218814374,
                    'timestamp': 1600861713,
                },
                'type': 'adjusted',
            }
            response['position']['lat'] = response_dict[
                request.json['driver_id']
            ]['lat']
            response['position']['lon'] = response_dict[
                request.json['driver_id']
            ]['lon']
            return mockserver.make_response(json=response, status=200)
        return _error_response(mockserver, 'Driver not found', 404)


@pytest.fixture
def mongodb_settings(mongodb_settings):
    mongodb_settings['mqc_confirmations']['settings']['database'] = 'mqc'
    return mongodb_settings


class TagsMocksContext:
    def __init__(self):
        self.tags = []

    def set_tags(self, new_tags: list):
        self.tags = new_tags


@pytest.fixture(name='tags_mocks')
def _tags_mocks(mockserver, autouse=True):
    context = TagsMocksContext()

    @mockserver.json_handler('/driver-tags/v1/drivers/match/profile')
    def _mock_driver_tags_v1_drivers_match_profile(request):
        return {'tags': context.tags}

    return context
