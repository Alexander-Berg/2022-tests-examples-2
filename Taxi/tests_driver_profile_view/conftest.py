# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from driver_profile_view_plugins import *  # noqa: F403 F401
# pylint: disable=wrong-import-order
import pytest
from tests_driver_profile_view import utils


class ParksContext:
    def __init__(self):
        self.park_info = {}

    def set_park_info(self, dbid, country, city):
        self.park_info[dbid] = (country, city)


@pytest.fixture(name='parks')
def _parks(mockserver):
    context = ParksContext()

    @mockserver.json_handler('/parks/driver-profiles/list')
    def _driver_profiles_list(request):
        request = request.json
        dbid = request['query']['park']['id']
        country, city = context.park_info.get(dbid, ('rus', 'Москва'))
        return {
            'parks': [{'city': city, 'country_id': country}],
            'driver_profiles': [],
            'offset': 0,
            'total': 1,
            'limit': 1,
        }

    @mockserver.json_handler('/parks/driver-profiles/search')
    def _driver_profiles_search(request):
        request = request.json
        dbid = request['query']['park']['id'][0]
        limit = request['limit']
        assert limit == 1
        return {
            'profiles': [
                {'driver': {}, 'park': {'id': dbid, 'is_certified': True}},
            ],
        }

    return context


class FleetParksContext:
    def __init__(self):
        self.parks = utils.DEFAULT_PARKS
        self.return_error = False

    def set_parks(self, parks):
        self.parks = parks

    def set_return_error(self):
        self.return_error = True


@pytest.fixture(name='fleet_parks')
def fleet_parks_request(mockserver):
    context = FleetParksContext()

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _park_list(request):
        if context.return_error:
            return mockserver.make_response(json=utils.ERROR_JSON, status=500)
        return {'parks': context.parks}

    return context


class UniqueDriversContext:
    def __init__(self):
        self.exams = {}
        self.uniques = {}

    def set_exams(self, park_id, driver_profile_id, exams):
        self.exams[park_id + '_' + driver_profile_id] = exams

    def set_unique_driver_id(
            self, park_id, driver_profile_id, unique_driver_id,
    ):
        self.uniques[park_id + '_' + driver_profile_id] = unique_driver_id


@pytest.fixture(name='unique_drivers_mocks')
def unique_drivers_mocks(mockserver):
    context = UniqueDriversContext()

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/exams/retrieve-by-profiles',
    )
    def _exams_retrieve_by_profiles(request):
        request = request.json
        park_driver_profile_id = request['profile_id_in_set'][0]
        if park_driver_profile_id not in context.exams:
            return mockserver.make_response(json=utils.ERROR_JSON, status=500)
        return {
            'exams': [
                {
                    'park_driver_profile_id': park_driver_profile_id,
                    'data': context.exams[park_driver_profile_id],
                },
            ],
        }

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _uniques_retrieve_by_profiles(request):
        request = request.json
        park_driver_profile_id = request['profile_id_in_set'][0]
        if park_driver_profile_id not in context.uniques:
            return mockserver.make_response(json=utils.ERROR_JSON, status=500)
        return {
            'uniques': [
                {
                    'park_driver_profile_id': park_driver_profile_id,
                    'data': {
                        'unique_driver_id': context.uniques[
                            park_driver_profile_id
                        ],
                    },
                },
            ],
        }

    return context


class DriverTrackstoryContext:
    def __init__(self):
        self.lon = 0
        self.lat = 0
        self.should_fail = False


@pytest.fixture(name='driver_trackstory_mocks')
def driver_trackstory_mocks(mockserver):
    context = DriverTrackstoryContext()

    @mockserver.json_handler('/driver-trackstory/position')
    def _position(request):
        if context.should_fail:
            raise mockserver.TimeoutError()
        return {
            'type': 'raw',
            'position': {
                'lon': context.lon,
                'lat': context.lat,
                'timestamp': 0,
            },
        }

    return context


class DriverProtocolContext:
    def __init__(self):
        self.tariffs = utils.DEFAULT_TARIFFS
        self.karma_points = utils.DEFAULT_KARMA_POINTS
        self.exam_score = utils.DEFAULT_EXAM_SCORE
        self.return_error = False

    def set_tariffs(self, tariffs):
        self.tariffs = tariffs

    def set_karma_points(self, karma_points):
        self.karma_points = karma_points

    def set_exam_score(self, exam_score):
        self.exam_score = exam_score

    def set_return_error(self):
        self.return_error = True


@pytest.fixture(name='driver_protocol')
def driver_protocol_request(mockserver):
    context = DriverProtocolContext()

    @mockserver.json_handler('/driver-protocol/service/driver/info')
    def _driver_info(request):
        if context.return_error:
            return mockserver.make_response(json=utils.ERROR_JSON, status=500)
        value = {'exam_date': '2017-04-04T05:32:22+00:00'}
        if context.karma_points:
            value['karma_points'] = context.karma_points
        if context.tariffs:
            value['tariffs'] = context.tariffs
        if context.exam_score:
            value['exam_score'] = context.exam_score
        return value

    return context


class DriverRatingsContext:
    def __init__(self):
        self.rating = utils.DEFAULT_RATING
        self.return_error = False

    def set_ratings(self, rating):
        self.rating = rating

    def set_return_error(self):
        self.return_error = True


@pytest.fixture(name='driver_ratings')
def driver_ratings_request(mockserver):
    context = DriverRatingsContext()

    @mockserver.json_handler('/driver-ratings/v2/driver/rating')
    def _driver_rating(request):
        if context.return_error:
            return mockserver.make_response(json=utils.ERROR_JSON, status=500)
        return context.rating

    return context


class ParksCommute:
    def __init__(self):
        self.clid_mapping = {}

    def set_clid_mapping(self, clid_mapping):
        self.clid_mapping = clid_mapping


@pytest.fixture(name='parks_commute')
def parks_commute_mock(mockserver):
    context = ParksCommute()

    @mockserver.json_handler('/parks-commute/v1/parks/retrieve_by_park_id')
    def _retrieve_by_park_id(request):
        park_id = request.json['id_in_set'][0]
        response_park = {'park_id': park_id}
        if park_id in context.clid_mapping:
            response_park['data'] = {'clid': context.clid_mapping[park_id]}
        return {'parks': [response_park]}

    return context
