# pylint: disable=wildcard-import, unused-wildcard-import, import-error, C0411
import collections
import datetime

from driver_categories_api_plugins import *  # noqa: F403 F401
import pytest


def _error_response(mockserver, error_message, status=400):
    return mockserver.make_response(
        json={'message': error_message}, status=status,
    )


@pytest.fixture(name='driver_diagnostics')
def _driver_diagnostics(mockserver, load_json):
    def _get_block_reason_by_position(lat, lon):
        return {
            'block_ids': [f'position_{lat}_{lon}'],
            'block_reason': f'Position {lat} {lon}',
            'deeplink': '/deeplink1',
            'is_enabled': False,
            'name': 'econom',
        }

    @mockserver.json_handler(
        '/driver-diagnostics/internal/driver-diagnostics/v1/categories/'
        'restrictions',
    )
    def _internal_driver_diagnostics_v1_categories_restrictions(request):
        assert 'Accept-Language' in request.headers
        assert 'User-Agent' in request.headers
        park_driver_profile_id = (
            f'{request.json["driver_params"]["park_id"]}'
            f'_{request.json["driver_params"]["driver_profile_id"]}'
        )
        response_dict = load_json('driver_diagnostics.json')
        response_categories = response_dict['categories'].get(
            park_driver_profile_id, [],
        )
        response = {'categories': []}
        for category_item in response_categories:
            response['categories'].append(category_item)

        lat = request.json['position']['lat']
        lon = request.json['position']['lon']

        if lat in [0.0, 1.0, 2.0]:
            response['categories'].append(
                _get_block_reason_by_position(lat, lon),
            )

        return mockserver.make_response(
            json=response,
            content_type='application/json',
            headers={'X-Polling-Delay-Ms': '100'},
        )


@pytest.fixture(name='driver_profiles')
def _driver_profiles(mockserver, load_json):
    @mockserver.json_handler(
        '/driver-profiles/v1/vehicle_bindings/cars/retrieve_by_driver_id',
    )
    def _driver_profiles_v1_vehicle_bindings_cars_retrieve_by_driver_id(
            request,
    ):
        if 'consumer' not in request.args:
            return _error_response(mockserver, 'Missing consumer in query')
        if 'id_in_set' not in request.json or not isinstance(
                request.json['id_in_set'], list,
        ):
            return _error_response(
                mockserver, 'Field \'id_in_set\' is missed or of a wrong type',
            )
        response_dict = load_json('driver_profiles.json')
        response = {'profiles': []}
        for dbid_uuid in request.json['id_in_set']:
            response['profiles'].append(
                response_dict.get(
                    dbid_uuid, {'park_driver_profile_id': dbid_uuid},
                ),
            )
        return mockserver.make_response(
            json=response, content_type='application/json',
        )

    @mockserver.json_handler(
        '/driver-profiles/v1/driver/app/profiles/retrieve',
    )
    def _driver_profiles_v1_driver_app_profiles_retrieve(request):
        data = load_json('driver_app_profiles.json')

        assert request.args['consumer'] == 'driver-categories-api'

        profiles = []
        for dbid_uuid in request.json['id_in_set']:
            if dbid_uuid in data:
                profiles.append(
                    {
                        'park_driver_profile_id': dbid_uuid,
                        'data': data[dbid_uuid],
                    },
                )
        response = {'profiles': profiles}
        return mockserver.make_response(json=response)


@pytest.fixture(name='driver_trackstory')
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

    @mockserver.json_handler('/driver-trackstory/query/positions')
    def _query_positions(request):
        response_dict = load_json('driver_trackstory.json')
        driver_id = request.json['driver_ids'][0]
        if driver_id in response_dict:
            item = {
                'position': {
                    'direction': 36,
                    'speed': 2.243076218814374,
                    'timestamp': 1600861713,
                },
                'source': 'Adjusted',
            }
            item['position']['lat'] = response_dict[driver_id]['lat']
            item['position']['lon'] = response_dict[driver_id]['lon']
            return mockserver.make_response(
                json={'results': [[item]]}, status=200,
            )
        return _error_response(mockserver, 'Driver not found', 404)


@pytest.fixture(name='fleet_parks')
def _fleet_parks(mockserver, load_json):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _fleet_parks_v1_parks_list(request):
        query_park_ids = request.json['query']['park']['ids']
        response_dict = load_json('fleet_parks.json')['list']
        response = {'parks': []}
        for park_id in query_park_ids:
            park = {}
            if park_id in response_dict:
                park = response_dict[park_id]
            else:
                park = response_dict['__default__']
            park['id'] = park_id
            response['parks'].append(park)
        return mockserver.make_response(
            json=response, content_type='application/json',
        )

    @mockserver.json_handler('/fleet-parks/v1/parks/robot-settings')
    def _fleet_parks_v1_parks_robot_settings(request):
        if 'query' not in request.json or not isinstance(
                request.json['query'], dict,
        ):
            return _error_response(
                mockserver, 'Field \'query\' is missed or of a wrong type',
            )
        query = request.json['query']
        if 'park' not in query or not isinstance(query['park'], dict):
            return _error_response(
                mockserver,
                'Field \'query.park\' is missed or of a wrong type',
            )
        query_park = query['park']
        if 'ids' not in query_park or not isinstance(query_park['ids'], list):
            return _error_response(
                mockserver,
                'Field \'query.park.ids\' is missed or of a wrong type',
            )
        query_park_ids = query_park['ids']
        if not query_park_ids:
            return _error_response(
                mockserver,
                'Value of \'query.park.ids\': incorrect size, '
                'must be 1 (limit) <= 0 (value)',
            )
        response_dict = load_json('fleet_parks.json')['robot_settings']
        response = {'settings': []}
        for park_id in query_park_ids:
            if park_id in response_dict:
                park = response_dict[park_id]
                park['park_id'] = park_id
                response['settings'].append(park)
        return mockserver.make_response(
            json=response, content_type='application/json',
        )


@pytest.fixture(name='fleet_vehicles')
def _fleet_vehicles(mockserver, load_json):
    @mockserver.json_handler(
        '/fleet-vehicles/v1/vehicles/driver/has-child-tariff',
    )
    def _has_child_tariff(request):
        response_dict = load_json('fleet_vehicles.json')['has-child-tariff']
        item_id = (
            request.args['park_id']
            + '_'
            + request.args['vehicle_id']
            + '_'
            + request.args['driver_profile_id']
        )
        if item_id in response_dict:
            return mockserver.make_response(
                json=response_dict[item_id], status=200,
            )
        return _error_response(mockserver, 'Vehicle is not found', status=404)


@pytest.fixture(name='parks')
def _parks(mockserver, load_json):
    class ParksContext:
        def __init__(self):
            self.search_response = {}

        def set_driver_profiles_search(self, idx=None):
            driver_profiles = load_json('driver-profiles.json')
            if idx:
                profile = driver_profiles['profiles'][idx]
                self.search_response = {'profiles': [profile]}
            else:
                self.search_response = driver_profiles

    context = ParksContext()

    @mockserver.json_handler('/parks/driver-profiles/search')
    def _driver_profiles_search(request):
        return context.search_response

    @mockserver.json_handler('/parks/cars/list')
    def _parks_cars_list(request):
        query_park = request.json['query']['park']
        query_park_id = query_park['id']

        query_field_car_id = []

        if 'car' in query_park and 'id' in query_park['car']:
            query_field_car_id = query_park['car']['id']

        if len(query_field_car_id) != len(set(query_field_car_id)):
            return _error_response(
                mockserver,
                {
                    'error': {
                        'text': (
                            'query.park.car.id must contain unique strings'
                        ),
                    },
                },
            )

        has_field_car_category = False
        if (
                'fields' in request.json
                and 'car' in request.json['fields']
                and 'category' in request.json['fields']['car']
        ):
            has_field_car_category = True

        response_dict = load_json('parks.json')
        response = {'cars': [], 'offset': 0, 'total': 0}
        if query_park_id in response_dict:
            park = response_dict[query_park_id]
            if has_field_car_category:
                for car_id in query_field_car_id:
                    if car_id in park:
                        response['cars'].append(
                            {
                                'brand': '',
                                'category': park[car_id],
                                'color': '',
                                'id': car_id,
                                'model': '',
                                'number': '',
                                'year': 0,
                            },
                        )
                        response['total'] += 1
        return mockserver.make_response(
            json=response, content_type='application/json',
        )

    return context


@pytest.fixture(name='taximeter_xservice')
def _taximeter_xservice(mockserver, load_json):
    @mockserver.json_handler('/taximeter-xservice/utils/qc/child_seats')
    def _taximeter_xservice_utils_qc_child_seats(request):
        park_id = request.json.get('park_id', '')
        car_id = request.json.get('car_id', '')
        driver_id = request.json.get('driver_id', '')
        response_dict = load_json('taximeter_xservice.json')
        response = {'confirmed': False}
        if (
                park_id in response_dict
                and car_id in response_dict[park_id]
                and driver_id in response_dict[park_id][car_id]
        ):
            response = response_dict[park_id][car_id][driver_id]
        return mockserver.make_response(
            json=response, content_type='application/json',
        )


@pytest.fixture(name='driver_mode_subscription')
def _driver_mode_subscription(mockserver, load_json):
    @mockserver.json_handler('/driver-mode-subscription/v1/mode/get')
    def _v1_mode_get(request):
        return {
            'active_mode': 'driver_fix',
            'active_mode_type': 'driver_fix',
            'active_since': datetime.datetime.now().strftime(
                '%Y-%m-%dT%H:%M:%SZ',
            ),
        }


@pytest.fixture(name='candidates')
def _candidates(mockserver, load_json):
    @mockserver.json_handler('/candidates/profiles')
    def _profiles(request):
        response = load_json('candidates.json')
        return response


@pytest.fixture(name='driver_tags')
def _driver_tags(mockserver, load_json):
    @mockserver.json_handler('/driver-tags/v1/drivers/match/profile')
    def _v1_drivers_match_profile(request):
        response_dict = load_json('driver-tags.json')
        tags = response_dict.get(
            f'{request.json["dbid"]}_{request.json["uuid"]}',
        )
        return tags if tags else {'tags': []}


@pytest.fixture
def service_client_default_headers():
    return {'User-Agent': 'Taximeter 9.49 (9765)'}


@pytest.fixture(name='contractor_transport')
def _contractor_transport(mockserver, load_json):
    class Context:
        def __init__(self):
            self.contractor_id = None

        def set_contractor_id(self, park_id, driver_id):
            self.contractor_id = f'{park_id}_{driver_id}'

    context = Context()

    @mockserver.json_handler(
        'contractor-transport/v1/transport-active/retrieve-by-contractor-id',
    )
    def _transport_active(request):
        return {
            'contractors_transport': [
                {
                    'contractor_id': context.contractor_id,
                    'transport_active': {
                        'type': 'car',
                        'vehicle_id': 'car_66',
                    },
                    'revision': '',
                },
            ],
        }

    return context


@pytest.fixture(name='tags')
def _tags(mockserver, load_json):
    class Context:
        def __init__(self):
            self.append = None
            self.remove = None

        def set_tags(self, append, remove):
            self.append = collections.Counter(append)
            self.remove = collections.Counter(remove)

    context = Context()

    @mockserver.json_handler('/tags/v2/upload')
    def _tags_upload(request):
        if 'append' in request.json:
            actual_append = [
                x['name'] for x in request.json['append'][0]['tags']
            ]
        else:
            actual_append = None
        assert context.append == collections.Counter(actual_append)

        if 'remove' in request.json:
            actual_remove = [
                x['name'] for x in request.json['remove'][0]['tags']
            ]
        else:
            actual_remove = None
        assert context.remove == collections.Counter(actual_remove)

        return {}

    return context


@pytest.fixture(name='tags_assign')
def _tags_assign(mockserver, load_json):
    class Context:
        def __init__(self):
            self.assign_tags = None

        def set_tags(self, assign_tags):
            self.assign_tags = collections.Counter(assign_tags)

    context = Context()

    @mockserver.json_handler('/tags/v1/assign')
    def _tags_upload(request):
        tags = request.json['entities'][0]['tags']
        actual_assign_tags = []
        if tags:
            actual_assign_tags = [key for key, value in tags.items()]
        assert context.assign_tags == collections.Counter(actual_assign_tags)

        return {}

    return context
