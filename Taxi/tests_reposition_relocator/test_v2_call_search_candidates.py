# pylint: disable=import-error, wrong-import-order, too-many-lines
# pylint: disable=import-only-modules
import copy
import datetime
import json

import flatbuffers
from headers.search_bulk.detail import Driver
from headers.search_bulk.detail import Request
from headers.search_bulk.detail import Response
from headers.search_bulk.detail import SearchParam
from headers.search_bulk.detail import SearchResult
from models.detail import DriverStatus
from models.detail import TransportType
from models.geometry.detail import TrackPoint
from models.geometry.detail import Viewport
import pytest
from reposition_api.fbs.v1.service.offers import GeoPoint
from reposition_api.fbs.v1.service.offers import Offer
from reposition_api.fbs.v1.service.offers import Response as OffersResponse
from yandex.taxi.reposition import Session
from yandex.taxi.reposition import SessionsResponse

from tests_plugins import utils

from .utils import format_execution_timestamp


NIRVANA_CALL_INSTANCE_ID = 'somerandomid'


def to_int(val):
    return int(val * 1000000)


class DriverSearchFbHelper:
    drivers_statuses = dict(
        [
            (DriverStatus.DriverStatus.Offline, 'offline'),
            (DriverStatus.DriverStatus.Free, 'free'),
            (DriverStatus.DriverStatus.OnOrder, 'on-order'),
            (DriverStatus.DriverStatus.Busy, 'busy'),
        ],
    )

    transport_types = dict(
        [
            (TransportType.TransportType.Car, 'car'),
            (TransportType.TransportType.Pedestrian, 'pedestrian'),
            (TransportType.TransportType.Bicycle, 'bicycle'),
            (TransportType.TransportType.ElectricBicycle, 'electric-bicycle'),
            (TransportType.TransportType.Motorcycle, 'motorcycle'),
        ],
    )

    def driver_status_to_string(self, status):
        return self.drivers_statuses.get(status, 'unknown')

    def driver_status_from_string(self, status):
        str_drivers_statuses = dict(
            zip(self.drivers_statuses.values(), self.drivers_statuses.keys()),
        )
        return str_drivers_statuses[status]

    def transport_type_from_string(self, status):
        str_transport_types = dict(
            zip(self.transport_types.values(), self.transport_types.keys()),
        )
        return str_transport_types[status]

    def build_response(self, data):
        builder = flatbuffers.Builder(0)

        results_fbs = []
        for item in data:
            drivers_fbs = []
            for driver in item['drivers']:
                dbid_fbs = builder.CreateString(driver['dbid'])
                uuid_fbs = builder.CreateString(driver['uuid'])
                classes = []
                for driver_class in driver['classes']:
                    classes.append(builder.CreateString(driver_class))
                Driver.DriverStartClassesVector(builder, len(classes))
                for driver_class_fbs in classes:
                    builder.PrependUOffsetTRelative(driver_class_fbs)
                classes_vec = builder.EndVector(len(classes))
                Driver.DriverStart(builder)
                Driver.DriverAddDbid(builder, dbid_fbs)
                Driver.DriverAddUuid(builder, uuid_fbs)
                Driver.DriverAddClasses(builder, classes_vec)
                Driver.DriverAddPosition(
                    builder,
                    TrackPoint.CreateTrackPoint(
                        builder,
                        to_int(driver['position'][0]),
                        to_int(driver['position'][1]),
                        int(utils.timestamp(datetime.datetime.now())),
                        0,
                        0,
                        0,
                        0,
                    ),
                )
                Driver.DriverAddStatus(
                    builder, self.driver_status_from_string(driver['status']),
                )
                Driver.DriverAddTransportType(
                    builder,
                    self.transport_type_from_string(driver['transport_type']),
                )
                drivers_fbs.append(Driver.DriverEnd(builder))

            SearchResult.SearchResultStartDriversVector(
                builder, len(drivers_fbs),
            )
            for driver_fbs in drivers_fbs:
                builder.PrependUOffsetTRelative(driver_fbs)
            drivers_fbs = builder.EndVector(len(drivers_fbs))

            SearchResult.SearchResultStart(builder)
            SearchResult.SearchResultAddSearchId(builder, item['search_id'])
            SearchResult.SearchResultAddDrivers(builder, drivers_fbs)
            results_fbs.append(SearchResult.SearchResultEnd(builder))

        Response.ResponseStartResultsVector(builder, len(results_fbs))
        for result_fbs in results_fbs:
            builder.PrependUOffsetTRelative(result_fbs)
        results_fbs = builder.EndVector(len(results_fbs))

        Response.ResponseStart(builder)
        Response.ResponseAddResults(builder, results_fbs)
        response_fbs = Response.ResponseEnd(builder)
        builder.Finish(response_fbs)
        return builder.Output()

    def build_request(self, data):
        builder = flatbuffers.Builder(0)

        search_datas_fbs = []
        for item in data:
            allowed_classes_fbs = [
                builder.CreateString(allowed_class)
                for allowed_class in item['allowed_classes']
            ]

            SearchParam.SearchParamStartAllowedClassesVector(
                builder, len(allowed_classes_fbs),
            )
            for allowed_class_fbs in allowed_classes_fbs:
                builder.PrependUOffsetTRelative(allowed_class_fbs)
            allowed_classes_fbs = builder.EndVector(len(allowed_classes_fbs))

            statuses_fbs = [
                self.driver_status_from_string(status)
                for status in item['statuses']
            ]

            SearchParam.SearchParamStartStatusesVector(
                builder, len(statuses_fbs),
            )
            for status_fbs in statuses_fbs:
                builder.PrependUint16(status_fbs)
            statuses_fbs = builder.EndVector(len(statuses_fbs))

            SearchParam.SearchParamStart(builder)
            SearchParam.SearchParamAddSearchId(builder, item['search_id'])
            SearchParam.SearchParamAddViewport(
                builder,
                Viewport.CreateViewport(
                    builder,
                    to_int(item['viewport']['top_left'][0]),
                    to_int(item['viewport']['top_left'][1]),
                    to_int(item['viewport']['bottom_right'][0]),
                    to_int(item['viewport']['bottom_right'][1]),
                ),
            )
            SearchParam.SearchParamAddAllowedClasses(
                builder, allowed_classes_fbs,
            )
            SearchParam.SearchParamAddStatuses(builder, statuses_fbs)
            search_datas_fbs.append(SearchParam.SearchParamEnd(builder))

        Request.RequestStartParamsVector(builder, len(search_datas_fbs))
        for search_data_fbs in search_datas_fbs:
            builder.PrependUOffsetTRelative(search_data_fbs)
        search_datas_fbs = builder.EndVector(len(search_datas_fbs))

        Request.RequestStart(builder)
        Request.RequestAddParams(builder, search_datas_fbs)
        request_fbs = Request.RequestEnd(builder)
        builder.Finish(request_fbs)
        return builder.Output()

    def parse_response(self, data):
        results = []
        response = Response.Response.GetRootAsResponse(data, 0)
        for i in range(0, response.ResultsLength()):
            search_result = response.Results(i)

            drivers = []
            for j in range(0, search_result.DriversLength()):
                driver = search_result.Drivers(j)
                # incorrect import on Driver
                # position = driver.Position()
                classes = [
                    driver.Classes(k).decode('utf-8')
                    for k in range(0, driver.ClassesLength())
                ]
                drivers.append(
                    {
                        'dbid': driver.Dbid().decode('utf-8'),
                        'uuid': driver.Uuid().decode('utf-8'),
                        # 'position': {
                        #     'lon': position.Lon() * .000001,
                        #     'lat': position.Lat() * .000001,
                        #     'timestamp': position.Timestamp(),
                        #     'direction': position.Direction(),
                        #     'speed': position.Speed(),
                        #     'source': position.Source(),
                        #     'accuracy': position.Accuracy(),
                        # },
                        'classes': classes,
                        'status': self.driver_status_to_string(
                            driver.Status(),
                        ),
                    },
                )

            results.append(
                {'search_id': search_result.SearchId(), 'drivers': drivers},
            )
        return results

    def parse_request(self, data):
        results = []
        request = Request.Request.GetRootAsRequest(data, 0)
        for i in range(0, request.ParamsLength()):
            search_data = request.Params(i)
            allowed_classes = []
            for j in range(0, search_data.AllowedClassesLength()):
                allowed_classes.append(
                    search_data.AllowedClasses(j).decode('utf-8'),
                )
            statuses = []
            for j in range(0, search_data.StatusesLength()):
                statuses.append(
                    self.driver_status_to_string(search_data.Statuses(j)),
                )

            results.append(
                {
                    'search_id': search_data.SearchId(),
                    #  'point': [
                    #  search_data.Point().Lon(),
                    #  search_data.Point().Lat(),
                    #  ],
                    'allowed_classes': allowed_classes,
                    'statuses': statuses,
                },
            )
        return results


def build_session(
        builder, park_db_id, driver_id, mode_name, submode_name, start, end,
):
    park_db_id_str = builder.CreateString(park_db_id)
    driver_id_str = builder.CreateString(driver_id)
    mode_name_str = builder.CreateString(mode_name)
    if submode_name:
        submode_name_str = builder.CreateString(submode_name)
    Session.SessionStart(builder)
    Session.SessionAddParkDbId(builder, park_db_id_str)
    Session.SessionAddDriverId(builder, driver_id_str)
    Session.SessionAddMode(builder, mode_name_str)
    if submode_name:
        Session.SessionAddSubmode(builder, submode_name_str)
    Session.SessionAddStart(builder, int(utils.timestamp(start)))
    if end:
        Session.SessionAddEnd(builder, int(utils.timestamp(end)))
    return Session.SessionEnd(builder)


def build_sessions_response(data):
    builder = flatbuffers.Builder(0)
    sessions = []
    for session in data:
        sessions.append(
            build_session(
                builder,
                session['park_db_id'],
                session['driver_id'],
                session['mode'],
                session['submode'],
                session['start'],
                session['end'],
            ),
        )
    SessionsResponse.SessionsResponseStartSessionsVector(
        builder, len(sessions),
    )
    for session in sessions:
        builder.PrependUOffsetTRelative(session)
    sessions_vec = builder.EndVector(len(sessions))
    SessionsResponse.SessionsResponseStart(builder)
    SessionsResponse.SessionsResponseAddSessions(builder, sessions_vec)
    sessions_response = SessionsResponse.SessionsResponseEnd(builder)
    builder.Finish(sessions_response)
    return builder.Output()


def create_fbs_offer(
        builder,
        park_id,
        driver_profile_id,
        mode_name,
        used,
        created,
        valid_until,
        point,
):
    park_id_str = builder.CreateString(park_id)
    driver_profile_id_str = builder.CreateString(driver_profile_id)
    mode_name_str = builder.CreateString(mode_name)

    Offer.OfferStart(builder)
    Offer.OfferAddParkId(builder, park_id_str)
    Offer.OfferAddDriverProfileId(builder, driver_profile_id_str)
    Offer.OfferAddModeName(builder, mode_name_str)

    point = GeoPoint.CreateGeoPoint(builder, point[0], point[1])
    Offer.OfferAddPoint(builder, point)

    Offer.OfferAddUsed(builder, used)
    Offer.OfferAddCreated(builder, int(utils.timestamp(created)))
    Offer.OfferAddValidUntil(builder, int(utils.timestamp(valid_until)))

    return Offer.OfferEnd(builder)


def build_offers_response(data):
    builder = flatbuffers.Builder(0)
    offers = []

    for offer in data:
        offers.append(
            create_fbs_offer(
                builder,
                offer['park_id'],
                offer['driver_profile_id'],
                offer['mode'],
                offer['used'],
                offer['created'],
                offer['valid_until'],
                offer['point'],
            ),
        )

    OffersResponse.ResponseStartOffersVector(builder, len(offers))
    for offer in offers:
        builder.PrependUOffsetTRelative(offer)
    offers_vec = builder.EndVector(len(offers))

    OffersResponse.ResponseStart(builder)
    OffersResponse.ResponseAddOffers(builder, offers_vec)

    offers_response = OffersResponse.ResponseEnd(builder)

    builder.Finish(offers_response)

    return builder.Output()


@pytest.mark.config(
    REPOSITION_RELOCATOR_ASYNC_REQUESTS_LIMITS={
        '__default__': {'max_bulk_size': 1000},
    },
)
@pytest.mark.driver_tags_match(
    dbid='1488', uuid='driverSS', tags=['one_required_tag', 'must_have_tag'],
)
@pytest.mark.driver_tags_match(
    dbid='1488', uuid='driverSS2', tags=['spooky_driver'],
)
@pytest.mark.driver_tags_match(
    dbid='parko', uuid='uuido', tags=['must_have_tag'],
)
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.parametrize('candidate_found', [False, True])
@pytest.mark.parametrize('probability', [False, True])
@pytest.mark.now('2020-04-27T15:02:00+0300')
async def test_put(
        taxi_reposition_relocator,
        pgsql,
        mockserver,
        mds_s3_storage,
        load_json,
        now,
        candidate_found,
        probability,
):
    @mockserver.json_handler('/blackbox-team')
    def _mock_blackbox(request):
        return mockserver.make_response(
            json.dumps(
                {
                    'oauth': {
                        'uid': '0000000000000000',
                        'token_id': '0',
                        'device_id': '',
                        'device_name': '',
                        'scope': 'oauth:grant_xtoken',
                        'ctime': '2020-01-01 00:00:00',
                        'issue_time': '2020-01-01 00:00:00',
                        'expire_time': None,
                        'is_ttl_refreshable': False,
                        'client_id': 'any',
                        'client_name': 'any',
                        'client_icon': '',
                        'client_homepage': '',
                        'client_ctime': '2020-01-01 00:00:00',
                        'client_is_yandex': False,
                        'xtoken_id': '',
                        'meta': '',
                    },
                    'uid': {
                        'value': '0000000000000000',
                        'lite': False,
                        'hosted': False,
                    },
                    'login': 'robot-nirvana',
                    'have_password': True,
                    'have_hint': False,
                    'aliases': {'1': 'robot-nirvana'},
                    'karma': {'value': 0},
                    'karma_status': {'value': 0},
                    'dbfields': {'subscription.suid.669': ''},
                    'status': {'value': 'VALID', 'id': 0},
                    'error': 'OK',
                    'connection_id': 't:0',
                },
            ),
            status=200,
        )

    @mockserver.json_handler('/candidates/search-bulk')
    def mock_driver_search_bulk(request):
        helper = DriverSearchFbHelper()

        parsed_request = helper.parse_request(request.get_data())
        parsed_request[0]['statuses'].sort()
        parsed_request[1]['statuses'].sort()

        assert parsed_request == [
            {
                'allowed_classes': ['econom'],
                'statuses': sorted(['free', 'on-order']),
                # 'viewport': {
                # 'top_left': [37, 55],
                # 'bottom_right': [39, 56],
                # },
                'search_id': 0,
            },
            {
                'allowed_classes': ['econom'],
                'statuses': sorted(['free', 'on-order']),
                'search_id': 1,
            },
        ]

        drivers = []
        if candidate_found:
            drivers.append(
                {
                    'dbid': '1488',
                    'uuid': 'driverSS',
                    'position': [37.251330952700464, 55.48777904452022],
                    'classes': ['econom'],
                    'status': 'free',
                    'transport_type': 'car',
                },
            )
            drivers.append(
                {
                    'dbid': '1488',
                    'uuid': 'driverSS2',
                    'position': [37.251330952700464, 55.48777904452022],
                    'classes': ['econom'],
                    'status': 'busy',
                    'transport_type': 'car',
                },
            )
            drivers.append(
                {
                    'dbid': 'parko',
                    'uuid': 'uuido',
                    'position': [37.251330952700464, 55.48777904452022],
                    'classes': ['econom'],
                    'status': 'free',
                    'transport_type': 'car',
                },
            )
        return mockserver.make_response(
            response=helper.build_response(
                [{'search_id': 0, 'drivers': drivers}],
            ),
            content_type='application/x-flatbuffers',
        )

    @mockserver.json_handler('/dispatch-airport/v1/reposition_availability')
    def mock_dispatch_airport(request):
        return mockserver.make_response(
            json.dumps(
                {'allowed': request.json['driver_ids'], 'forbidden': []},
            ),
        )

    mds_s3_storage.put_object(
        '/mds-s3/ae5208e9-e169-4106-b388-704db9061556',
        json.dumps(load_json('requests.json')).encode('utf-8'),
    )
    patched_request = load_json('request.json')

    if not probability:
        del patched_request['data']['options']['air_dist_threshold_list']
        del patched_request['data']['options'][
            'air_dist_include_probability_list'
        ]

    response = await taxi_reposition_relocator.put(
        'v2/call/search_candidates/' + NIRVANA_CALL_INSTANCE_ID,
        headers={'Authorization': 'OAuth any', 'X-Real-IP': '127.0.0.1'},
        json=patched_request,
    )

    assert response.status_code == 200
    assert response.json() == {
        'executionState': {
            'details': '',
            'message': 'Operation done successfully',
            'progress': 1.0,
            'result': 'SUCCESS',
            'status': 'FINISHED',
            'executionTimestamps': {
                'CHECK_AUTH': format_execution_timestamp(now, 0),
                'CREATE_OPERATION': format_execution_timestamp(now, 1),
                'DOWNLOAD_INPUTS': format_execution_timestamp(now, 2),
                'PROCESS_OPERATION': format_execution_timestamp(now, 3),
                'UPLOAD_OUTPUTS': format_execution_timestamp(now, 4),
            },
        },
        'ticket': NIRVANA_CALL_INSTANCE_ID,
    }

    expected_result = load_json('results.json')
    if candidate_found and not probability:
        for request in expected_result['data']:
            for _, candidate in request['candidates'].items():
                candidate['tags'].sort()
        del expected_result['data'][0]['candidates']['db777_driver1']
        del expected_result['data'][0]['demands_sources_candidates']['1']['1'][
            -1
        ]
    else:
        expected_result = {
            'data': [],
            'meta': {'created_at': '2020-04-27T12:02:00+00:00'},
        }

    stored_result = json.loads(
        mds_s3_storage.get_object(
            '/mds-s3/f855d81c-f988-4f35-8b6e-5a133dc0b518',
        ),
    )
    for request in stored_result['data']:
        for _, candidate in request['candidates'].items():
            candidate['tags'].sort()

    assert expected_result == stored_result

    assert mock_driver_search_bulk.times_called == 1
    assert mock_dispatch_airport.times_called == (1 if candidate_found else 0)


@pytest.mark.config(
    REPOSITION_RELOCATOR_ASYNC_REQUESTS_LIMITS={
        '__default__': {'max_bulk_size': 1000},
    },
)
@pytest.mark.driver_tags_match(
    dbid='1488', uuid='driverSS', tags=['one_required_tag', 'must_have_tag'],
)
@pytest.mark.driver_tags_match(
    dbid='1488', uuid='driverSS2', tags=['spooky_driver'],
)
@pytest.mark.driver_tags_match(
    dbid='parko', uuid='uuido', tags=['must_have_tag'],
)
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.now('2020-04-27T15:02:00+0300')
async def test_put_min_dist(
        taxi_reposition_relocator,
        pgsql,
        mockserver,
        mds_s3_storage,
        load_json,
        now,
):
    @mockserver.json_handler('/blackbox-team')
    def _mock_blackbox(request):
        return mockserver.make_response(
            json.dumps(
                {
                    'oauth': {
                        'uid': '0000000000000000',
                        'token_id': '0',
                        'device_id': '',
                        'device_name': '',
                        'scope': 'oauth:grant_xtoken',
                        'ctime': '2020-01-01 00:00:00',
                        'issue_time': '2020-01-01 00:00:00',
                        'expire_time': None,
                        'is_ttl_refreshable': False,
                        'client_id': 'any',
                        'client_name': 'any',
                        'client_icon': '',
                        'client_homepage': '',
                        'client_ctime': '2020-01-01 00:00:00',
                        'client_is_yandex': False,
                        'xtoken_id': '',
                        'meta': '',
                    },
                    'uid': {
                        'value': '0000000000000000',
                        'lite': False,
                        'hosted': False,
                    },
                    'login': 'robot-nirvana',
                    'have_password': True,
                    'have_hint': False,
                    'aliases': {'1': 'robot-nirvana'},
                    'karma': {'value': 0},
                    'karma_status': {'value': 0},
                    'dbfields': {'subscription.suid.669': ''},
                    'status': {'value': 'VALID', 'id': 0},
                    'error': 'OK',
                    'connection_id': 't:0',
                },
            ),
            status=200,
        )

    @mockserver.json_handler('/candidates/search-bulk')
    def mock_driver_search_bulk(request):
        helper = DriverSearchFbHelper()

        parsed_request = helper.parse_request(request.get_data())
        parsed_request[0]['statuses'].sort()
        parsed_request[1]['statuses'].sort()
        parsed_request[2]['statuses'].sort()

        assert parsed_request == [
            {
                'allowed_classes': ['econom'],
                'statuses': sorted(['free', 'on-order']),
                'search_id': 0,
            },
            {
                'allowed_classes': ['econom'],
                'statuses': sorted(['free', 'on-order']),
                'search_id': 1,
            },
            {
                'allowed_classes': ['econom'],
                'statuses': sorted(['free', 'on-order']),
                'search_id': 2,
            },
        ]

        drivers = [
            {
                'dbid': '1488',
                'uuid': 'driverSS2',
                'position': [37.635330952700464, 55.73877904452022],
                'classes': ['econom'],
                'status': 'busy',
                'transport_type': 'car',
            },
            {
                'dbid': 'parko',
                'uuid': 'uuido',
                'position': [37.637330952700464, 55.74077904452022],
                'classes': ['econom'],
                'status': 'free',
                'transport_type': 'car',
            },
        ]

        drivers2 = [
            {
                'dbid': '1488',
                'uuid': 'driverSS',
                'position': [39.251330952700464, 55.48777904452022],
                'classes': ['econom'],
                'status': 'free',
                'transport_type': 'car',
            },
        ]

        return mockserver.make_response(
            response=helper.build_response(
                [
                    {'search_id': 0, 'drivers': drivers},
                    {'search_id': 2, 'drivers': drivers2},
                ],
            ),
            content_type='application/x-flatbuffers',
        )

    @mockserver.json_handler('/dispatch-airport/v1/reposition_availability')
    def mock_dispatch_airport(request):
        return mockserver.make_response(
            json.dumps(
                {'allowed': request.json['driver_ids'], 'forbidden': []},
            ),
        )

    mds_s3_storage.put_object(
        '/mds-s3/ae5208e9-e169-4106-b388-704db9061556',
        json.dumps(load_json('requests_min_distance.json')).encode('utf-8'),
    )

    patched_request = load_json('request.json')
    patched_request['data']['options']['min_air_distance'] = 200
    del patched_request['data']['options']['air_dist_threshold_list']
    del patched_request['data']['options']['air_dist_include_probability_list']
    del patched_request['data']['options']['driver_tags_all_of']
    del patched_request['data']['options']['driver_tags_any_of']
    del patched_request['data']['options']['driver_tags_none_of']

    response = await taxi_reposition_relocator.put(
        'v2/call/search_candidates/' + NIRVANA_CALL_INSTANCE_ID,
        headers={'Authorization': 'OAuth any', 'X-Real-IP': '127.0.0.1'},
        json=patched_request,
    )

    assert response.status_code == 200
    assert response.json() == {
        'executionState': {
            'details': '',
            'message': 'Operation done successfully',
            'progress': 1.0,
            'result': 'SUCCESS',
            'status': 'FINISHED',
            'executionTimestamps': {
                'CHECK_AUTH': format_execution_timestamp(now, 0),
                'CREATE_OPERATION': format_execution_timestamp(now, 1),
                'DOWNLOAD_INPUTS': format_execution_timestamp(now, 2),
                'PROCESS_OPERATION': format_execution_timestamp(now, 3),
                'UPLOAD_OUTPUTS': format_execution_timestamp(now, 4),
            },
        },
        'ticket': NIRVANA_CALL_INSTANCE_ID,
    }

    expected_result = load_json('results_min_distance.json')
    stored_result = json.loads(
        mds_s3_storage.get_object(
            '/mds-s3/f855d81c-f988-4f35-8b6e-5a133dc0b518',
        ),
    )
    for request in stored_result['data']:
        for _, candidate in request['candidates'].items():
            candidate['tags'].sort()

    assert expected_result == stored_result

    assert mock_driver_search_bulk.times_called == 1
    assert mock_dispatch_airport.times_called == 1


@pytest.mark.config(
    REPOSITION_RELOCATOR_ASYNC_REQUESTS_LIMITS={
        '__default__': {'max_bulk_size': 1000},
    },
)
@pytest.mark.driver_tags_match(
    dbid='1488', uuid='driverSS', tags=['one_required_tag', 'must_have_tag'],
)
@pytest.mark.driver_tags_match(
    dbid='1488', uuid='driverSS2', tags=['spooky_driver'],
)
@pytest.mark.driver_tags_match(
    dbid='parko', uuid='uuido', tags=['must_have_tag'],
)
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.now('2020-04-27T15:02:00+0300')
async def test_put_min_dist_global_discard(
        taxi_reposition_relocator,
        pgsql,
        mockserver,
        mds_s3_storage,
        load_json,
        now,
):
    @mockserver.json_handler('/blackbox-team')
    def _mock_blackbox(request):
        return mockserver.make_response(
            json.dumps(
                {
                    'oauth': {
                        'uid': '0000000000000000',
                        'token_id': '0',
                        'device_id': '',
                        'device_name': '',
                        'scope': 'oauth:grant_xtoken',
                        'ctime': '2020-01-01 00:00:00',
                        'issue_time': '2020-01-01 00:00:00',
                        'expire_time': None,
                        'is_ttl_refreshable': False,
                        'client_id': 'any',
                        'client_name': 'any',
                        'client_icon': '',
                        'client_homepage': '',
                        'client_ctime': '2020-01-01 00:00:00',
                        'client_is_yandex': False,
                        'xtoken_id': '',
                        'meta': '',
                    },
                    'uid': {
                        'value': '0000000000000000',
                        'lite': False,
                        'hosted': False,
                    },
                    'login': 'robot-nirvana',
                    'have_password': True,
                    'have_hint': False,
                    'aliases': {'1': 'robot-nirvana'},
                    'karma': {'value': 0},
                    'karma_status': {'value': 0},
                    'dbfields': {'subscription.suid.669': ''},
                    'status': {'value': 'VALID', 'id': 0},
                    'error': 'OK',
                    'connection_id': 't:0',
                },
            ),
            status=200,
        )

    @mockserver.json_handler('/candidates/search-bulk')
    def mock_driver_search_bulk(request):
        helper = DriverSearchFbHelper()

        parsed_request = helper.parse_request(request.get_data())
        pos = [38, 55]
        if parsed_request[0]['allowed_classes'][0] == 'comfort':
            pos = [39, 55]

        drivers = [
            {
                'dbid': '1488',
                'uuid': 'driverSS',
                'position': pos,
                'classes': ['econom', 'comfort'],
                'status': 'busy',
                'transport_type': 'car',
            },
        ]

        return mockserver.make_response(
            response=helper.build_response(
                [{'search_id': 0, 'drivers': drivers}],
            ),
            content_type='application/x-flatbuffers',
        )

    @mockserver.json_handler('/dispatch-airport/v1/reposition_availability')
    def mock_dispatch_airport(request):
        return mockserver.make_response(
            json.dumps(
                {'allowed': request.json['driver_ids'], 'forbidden': []},
            ),
        )

    mds_s3_storage.put_object(
        '/mds-s3/ae5208e9-e169-4106-b388-704db9061556',
        json.dumps(load_json('requests_min_distance_discard.json')).encode(
            'utf-8',
        ),
    )

    patched_request = load_json('request.json')
    patched_request['data']['options']['min_air_distance'] = 200
    del patched_request['data']['options']['air_dist_threshold_list']
    del patched_request['data']['options']['air_dist_include_probability_list']
    del patched_request['data']['options']['driver_tags_all_of']
    del patched_request['data']['options']['driver_tags_any_of']
    del patched_request['data']['options']['driver_tags_none_of']

    response = await taxi_reposition_relocator.put(
        'v2/call/search_candidates/' + NIRVANA_CALL_INSTANCE_ID,
        headers={'Authorization': 'OAuth any', 'X-Real-IP': '127.0.0.1'},
        json=patched_request,
    )

    assert response.status_code == 200
    assert response.json() == {
        'executionState': {
            'details': '',
            'message': 'Operation done successfully',
            'progress': 1.0,
            'result': 'SUCCESS',
            'status': 'FINISHED',
            'executionTimestamps': {
                'CHECK_AUTH': format_execution_timestamp(now, 0),
                'CREATE_OPERATION': format_execution_timestamp(now, 1),
                'DOWNLOAD_INPUTS': format_execution_timestamp(now, 2),
                'PROCESS_OPERATION': format_execution_timestamp(now, 3),
                'UPLOAD_OUTPUTS': format_execution_timestamp(now, 4),
            },
        },
        'ticket': NIRVANA_CALL_INSTANCE_ID,
    }

    expected_result = {
        'data': [],
        'meta': {'created_at': '2020-04-27T12:02:00+00:00'},
    }
    stored_result = json.loads(
        mds_s3_storage.get_object(
            '/mds-s3/f855d81c-f988-4f35-8b6e-5a133dc0b518',
        ),
    )
    assert expected_result == stored_result
    assert mock_driver_search_bulk.times_called == 2
    assert mock_dispatch_airport.times_called == 2


@pytest.mark.config(
    REPOSITION_RELOCATOR_PARALLEL_REQUEST_PROCESSING_COUNT=6,
    REPOSITION_RELOCATOR_ASYNC_REQUESTS_LIMITS={
        '__default__': {'max_bulk_size': 1000},
    },
)
@pytest.mark.driver_tags_match(
    dbid='1488', uuid='driverSS', tags=['one_required_tag', 'must_have_tag'],
)
@pytest.mark.driver_tags_match(
    dbid='1488', uuid='driverSS2', tags=['spooky_driver'],
)
@pytest.mark.driver_tags_match(
    dbid='parko', uuid='uuido', tags=['must_have_tag'],
)
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.now('2020-04-27T15:02:00+0300')
async def test_put_multiple_requests(
        taxi_reposition_relocator,
        pgsql,
        mockserver,
        mds_s3_storage,
        load_json,
        now,
):
    @mockserver.json_handler('/blackbox-team')
    def _mock_blackbox(request):
        return mockserver.make_response(
            json.dumps(
                {
                    'oauth': {
                        'uid': '0000000000000000',
                        'token_id': '0',
                        'device_id': '',
                        'device_name': '',
                        'scope': 'oauth:grant_xtoken',
                        'ctime': '2020-01-01 00:00:00',
                        'issue_time': '2020-01-01 00:00:00',
                        'expire_time': None,
                        'is_ttl_refreshable': False,
                        'client_id': 'any',
                        'client_name': 'any',
                        'client_icon': '',
                        'client_homepage': '',
                        'client_ctime': '2020-01-01 00:00:00',
                        'client_is_yandex': False,
                        'xtoken_id': '',
                        'meta': '',
                    },
                    'uid': {
                        'value': '0000000000000000',
                        'lite': False,
                        'hosted': False,
                    },
                    'login': 'robot-nirvana',
                    'have_password': True,
                    'have_hint': False,
                    'aliases': {'1': 'robot-nirvana'},
                    'karma': {'value': 0},
                    'karma_status': {'value': 0},
                    'dbfields': {'subscription.suid.669': ''},
                    'status': {'value': 'VALID', 'id': 0},
                    'error': 'OK',
                    'connection_id': 't:0',
                },
            ),
            status=200,
        )

    @mockserver.json_handler('/candidates/search-bulk')
    def mock_driver_search_bulk(request):
        helper = DriverSearchFbHelper()

        parsed_request = helper.parse_request(request.get_data())
        parsed_request[0]['statuses'].sort()
        parsed_request[1]['statuses'].sort()

        assert parsed_request == [
            {
                'allowed_classes': ['econom'],
                'statuses': sorted(['free', 'on-order']),
                'search_id': 0,
            },
            {
                'allowed_classes': ['econom'],
                'statuses': sorted(['free', 'on-order']),
                'search_id': 1,
            },
        ]

        drivers = [
            {
                'dbid': '1488',
                'uuid': 'driverSS',
                'position': [37.251330952700464, 55.48777904452022],
                'classes': ['econom'],
                'status': 'free',
                'transport_type': 'car',
            },
            {
                'dbid': '1488',
                'uuid': 'driverSS2',
                'position': [37.251330952700464, 55.48777904452022],
                'classes': ['econom'],
                'status': 'busy',
                'transport_type': 'car',
            },
            {
                'dbid': 'parko',
                'uuid': 'uuido',
                'position': [37.251330952700464, 55.48777904452022],
                'classes': ['econom'],
                'status': 'free',
                'transport_type': 'car',
            },
        ]
        return mockserver.make_response(
            response=helper.build_response(
                [{'search_id': 0, 'drivers': drivers}],
            ),
            content_type='application/x-flatbuffers',
        )

    @mockserver.json_handler('/dispatch-airport/v1/reposition_availability')
    def mock_dispatch_airport(request):
        return mockserver.make_response(
            json.dumps(
                {'allowed': request.json['driver_ids'], 'forbidden': []},
            ),
        )

    request_cnt = 25
    requests = load_json('requests.json')
    for i in range(1, request_cnt):
        new_data = copy.deepcopy(requests['data'][0])
        new_data['request_info']['request_id'] += '_' + str(i)
        requests['data'].append(new_data)

    mds_s3_storage.put_object(
        '/mds-s3/ae5208e9-e169-4106-b388-704db9061556',
        json.dumps(requests).encode('utf-8'),
    )

    patched_request = load_json('request.json')
    del patched_request['data']['options']['air_dist_threshold_list']
    del patched_request['data']['options']['air_dist_include_probability_list']

    response = await taxi_reposition_relocator.put(
        'v2/call/search_candidates/' + NIRVANA_CALL_INSTANCE_ID,
        headers={'Authorization': 'OAuth any', 'X-Real-IP': '127.0.0.1'},
        json=patched_request,
    )

    assert response.status_code == 200
    assert response.json() == {
        'executionState': {
            'details': '',
            'message': 'Operation done successfully',
            'progress': 1.0,
            'result': 'SUCCESS',
            'status': 'FINISHED',
            'executionTimestamps': {
                'CHECK_AUTH': format_execution_timestamp(now, 0),
                'CREATE_OPERATION': format_execution_timestamp(now, 1),
                'DOWNLOAD_INPUTS': format_execution_timestamp(now, 2),
                'PROCESS_OPERATION': format_execution_timestamp(now, 3),
                'UPLOAD_OUTPUTS': format_execution_timestamp(now, 4),
            },
        },
        'ticket': NIRVANA_CALL_INSTANCE_ID,
    }

    expected_result = load_json('results.json')
    for i in range(1, request_cnt):
        new_data = copy.deepcopy(expected_result['data'][0])
        new_data['request_info']['request_id'] += '_' + str(i)
        expected_result['data'].append(new_data)

    for request in expected_result['data']:
        for _, candidate in request['candidates'].items():
            candidate['tags'].sort()
        del request['candidates']['db777_driver1']
        del request['demands_sources_candidates']['1']['1'][-1]

    stored_result = json.loads(
        mds_s3_storage.get_object(
            '/mds-s3/f855d81c-f988-4f35-8b6e-5a133dc0b518',
        ),
    )
    for request in stored_result['data']:
        for _, candidate in request['candidates'].items():
            candidate['tags'].sort()

    assert expected_result == stored_result

    assert mock_driver_search_bulk.times_called == request_cnt
    assert mock_dispatch_airport.times_called == request_cnt


@pytest.mark.now('2020-04-27T15:02:00+0300')
@pytest.mark.config(
    REPOSITION_RELOCATOR_ASYNC_REQUESTS_LIMITS={
        '__default__': {'max_bulk_size': 1000},
    },
)
@pytest.mark.driver_tags_match(
    dbid='1488', uuid='driverSS', tags=['one_required_tag', 'must_have_tag'],
)
@pytest.mark.driver_tags_match(
    dbid='db777',
    uuid='driver1',
    tags=['must_have_tag', 'another_required_tag'],
)
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.parametrize('discard_all_in_reposition', [False, True])
@pytest.mark.parametrize('reposition_filtered_modes', [None, ['poi']])
@pytest.mark.parametrize('min_time_since_last_offer_completion', [None, 120])
@pytest.mark.parametrize('min_time_since_last_offer_creation', [None, 0, 120])
async def test_put_with_reposition(
        taxi_reposition_relocator,
        pgsql,
        mockserver,
        mds_s3_storage,
        load_json,
        now,
        discard_all_in_reposition,
        reposition_filtered_modes,
        min_time_since_last_offer_completion,
        min_time_since_last_offer_creation,
):
    @mockserver.json_handler('/blackbox-team')
    def _mock_blackbox(request):
        return mockserver.make_response(
            json.dumps(
                {
                    'oauth': {
                        'uid': '0000000000000000',
                        'token_id': '0',
                        'device_id': '',
                        'device_name': '',
                        'scope': 'oauth:grant_xtoken',
                        'ctime': '2020-01-01 00:00:00',
                        'issue_time': '2020-01-01 00:00:00',
                        'expire_time': None,
                        'is_ttl_refreshable': False,
                        'client_id': 'any',
                        'client_name': 'any',
                        'client_icon': '',
                        'client_homepage': '',
                        'client_ctime': '2020-01-01 00:00:00',
                        'client_is_yandex': False,
                        'xtoken_id': '',
                        'meta': '',
                    },
                    'uid': {
                        'value': '0000000000000000',
                        'lite': False,
                        'hosted': False,
                    },
                    'login': 'robot-nirvana',
                    'have_password': True,
                    'have_hint': False,
                    'aliases': {'1': 'robot-nirvana'},
                    'karma': {'value': 0},
                    'karma_status': {'value': 0},
                    'dbfields': {'subscription.suid.669': ''},
                    'status': {'value': 'VALID', 'id': 0},
                    'error': 'OK',
                    'connection_id': 't:0',
                },
            ),
            status=200,
        )

    @mockserver.json_handler('/candidates/search-bulk')
    def mock_driver_search_bulk(request):
        helper = DriverSearchFbHelper()

        parsed_request = helper.parse_request(request.get_data())
        parsed_request[0]['statuses'].sort()
        parsed_request[1]['statuses'].sort()

        assert parsed_request == [
            {
                'allowed_classes': ['econom'],
                'statuses': sorted(['free', 'on-order']),
                'search_id': 0,
            },
            {
                'allowed_classes': ['econom'],
                'statuses': sorted(['free', 'on-order']),
                'search_id': 1,
            },
        ]

        drivers = [
            {
                'dbid': '1488',
                'uuid': 'driverSS',
                'position': [37.251330952700464, 55.48777904452022],
                'classes': ['econom'],
                'status': 'free',
                'transport_type': 'car',
            },
            {
                'dbid': 'db777',
                'uuid': 'driver1',
                'position': [37.251330952700464, 55.48777904452022],
                'classes': ['econom'],
                'status': 'free',
                'transport_type': 'car',
            },
        ]

        return mockserver.make_response(
            response=helper.build_response(
                [{'search_id': 0, 'drivers': drivers}],
            ),
            content_type='application/x-flatbuffers',
        )

    @mockserver.json_handler('/reposition-api/v1/service/sessions')
    def mock_service_sessions(request):
        response = build_sessions_response(
            [
                {
                    'park_db_id': 'db777',
                    'driver_id': 'driver1',
                    'mode': 'poi',
                    'end': (
                        None
                        if discard_all_in_reposition
                        else datetime.datetime(2020, 4, 27, 15, 2, 0)
                        - datetime.timedelta(
                            seconds=min_time_since_last_offer_completion - 1,
                        )
                    ),
                    'submode': None,
                    'start': datetime.datetime(2020, 4, 27, 12, 0, 0),
                },
            ],
        )

        return mockserver.make_response(
            response=response, content_type='application/x-flatbuffers',
        )

    @mockserver.json_handler('/reposition-api/v1/service/offers')
    def mock_service_offers(request):
        return mockserver.make_response(
            response=build_offers_response(
                [
                    {
                        'park_id': 'db777',
                        'driver_profile_id': 'driver1',
                        'mode': 'poi',
                        'used': True,
                        'created': (
                            datetime.datetime(2020, 4, 27, 15, 10, 0)
                            - datetime.timedelta(
                                seconds=min_time_since_last_offer_creation - 1,
                            )
                            if min_time_since_last_offer_creation > 0
                            else datetime.datetime(2020, 4, 26, 10, 0, 0)
                        ),
                        'valid_until': datetime.datetime(
                            2020, 4, 27, 15, 10, 0,
                        ),
                        'point': [37, 55],
                    },
                    {
                        'park_id': '1488',
                        'driver_profile_id': 'driverSS',
                        'mode': 'home',
                        'used': True,
                        'created': (
                            datetime.datetime(2020, 4, 27, 15, 10, 0)
                            - datetime.timedelta(
                                seconds=min_time_since_last_offer_creation,
                            )
                            if min_time_since_last_offer_creation > 0
                            else datetime.datetime(2020, 4, 26, 10, 0, 0)
                        ),
                        'valid_until': datetime.datetime(
                            2020, 4, 27, 15, 10, 0,
                        ),
                        'point': [37, 55],
                    },
                ],
            ),
            content_type='application/x-flatbuffers',
        )

    @mockserver.json_handler('/dispatch-airport/v1/reposition_availability')
    def mock_dispatch_airport(request):
        return mockserver.make_response(
            json.dumps(
                {'allowed': request.json['driver_ids'], 'forbidden': []},
            ),
        )

    if not reposition_filtered_modes and (
            min_time_since_last_offer_creation is not None
            or min_time_since_last_offer_completion is not None
    ):
        return

    mds_s3_storage.put_object(
        '/mds-s3/ae5208e9-e169-4106-b388-704db9061556',
        json.dumps(load_json('requests.json')).encode('utf-8'),
    )

    request = load_json('request.json')
    request['data']['options'][
        'discard_all_in_reposition'
    ] = discard_all_in_reposition
    if reposition_filtered_modes:
        request['data']['options'][
            'reposition_filtered_modes'
        ] = reposition_filtered_modes
    if min_time_since_last_offer_completion is not None:
        request['data']['options'][
            'min_time_since_last_offer_completion'
        ] = int(min_time_since_last_offer_completion)
    if min_time_since_last_offer_creation is not None:
        request['data']['options'][
            'min_time_since_last_offer_creation'
        ] = min_time_since_last_offer_creation
    del request['data']['options']['air_dist_threshold_list']
    del request['data']['options']['air_dist_include_probability_list']

    response = await taxi_reposition_relocator.put(
        'v2/call/search_candidates/' + NIRVANA_CALL_INSTANCE_ID,
        headers={'Authorization': 'OAuth any', 'X-Real-IP': '127.0.0.1'},
        json=request,
    )

    assert response.status_code == 200
    assert response.json() == {
        'executionState': {
            'details': '',
            'message': 'Operation done successfully',
            'progress': 1.0,
            'result': 'SUCCESS',
            'status': 'FINISHED',
            'executionTimestamps': {
                'CHECK_AUTH': format_execution_timestamp(now, 0),
                'CREATE_OPERATION': format_execution_timestamp(now, 1),
                'DOWNLOAD_INPUTS': format_execution_timestamp(now, 2),
                'PROCESS_OPERATION': format_execution_timestamp(now, 3),
                'UPLOAD_OUTPUTS': format_execution_timestamp(now, 4),
            },
        },
        'ticket': NIRVANA_CALL_INSTANCE_ID,
    }

    expected_result = load_json('results.json')
    for request in expected_result['data']:
        for _, candidate in request['candidates'].items():
            candidate['tags'].sort()

    stored_result = json.loads(
        mds_s3_storage.get_object(
            '/mds-s3/f855d81c-f988-4f35-8b6e-5a133dc0b518',
        ),
    )
    for request in stored_result['data']:
        for _, candidate in request['candidates'].items():
            candidate['tags'].sort()

    if (
            discard_all_in_reposition
            or min_time_since_last_offer_completion is not None
            or min_time_since_last_offer_creation is not None
    ):
        del expected_result['data'][0]['candidates']['db777_driver1']
        del expected_result['data'][0]['demands_sources_candidates']['1']['1'][
            -1
        ]

    assert expected_result == stored_result

    assert mock_driver_search_bulk.times_called == 1
    assert mock_service_sessions.times_called == (
        1
        if discard_all_in_reposition
        or min_time_since_last_offer_completion is not None
        else 0
    )
    assert mock_service_offers.times_called == (
        1 if min_time_since_last_offer_creation is not None else 0
    )
    assert mock_dispatch_airport.times_called == 1


@pytest.mark.now('2020-04-27T15:02:00+0300')
@pytest.mark.config(
    REPOSITION_RELOCATOR_ASYNC_REQUESTS_LIMITS={
        '__default__': {'max_bulk_size': 1000},
    },
)
@pytest.mark.driver_tags_match(
    dbid='1488', uuid='driverSS', tags=['one_required_tag', 'must_have_tag'],
)
@pytest.mark.driver_tags_match(
    dbid='db777',
    uuid='driver1',
    tags=['another_required_tag', 'must_have_tag'],
)
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.parametrize('free_status_time_threshold', [None, 900])
async def test_put_free_status_time_threshold(
        taxi_reposition_relocator,
        pgsql,
        mockserver,
        mds_s3_storage,
        load_json,
        now,
        free_status_time_threshold,
):
    @mockserver.json_handler('/blackbox-team')
    def _mock_blackbox(request):
        return mockserver.make_response(
            json.dumps(
                {
                    'oauth': {
                        'uid': '0000000000000000',
                        'token_id': '0',
                        'device_id': '',
                        'device_name': '',
                        'scope': 'oauth:grant_xtoken',
                        'ctime': '2020-01-01 00:00:00',
                        'issue_time': '2020-01-01 00:00:00',
                        'expire_time': None,
                        'is_ttl_refreshable': False,
                        'client_id': 'any',
                        'client_name': 'any',
                        'client_icon': '',
                        'client_homepage': '',
                        'client_ctime': '2020-01-01 00:00:00',
                        'client_is_yandex': False,
                        'xtoken_id': '',
                        'meta': '',
                    },
                    'uid': {
                        'value': '0000000000000000',
                        'lite': False,
                        'hosted': False,
                    },
                    'login': 'robot-nirvana',
                    'have_password': True,
                    'have_hint': False,
                    'aliases': {'1': 'robot-nirvana'},
                    'karma': {'value': 0},
                    'karma_status': {'value': 0},
                    'dbfields': {'subscription.suid.669': ''},
                    'status': {'value': 'VALID', 'id': 0},
                    'error': 'OK',
                    'connection_id': 't:0',
                },
            ),
            status=200,
        )

    @mockserver.json_handler('/candidates/search-bulk')
    def mock_driver_search_bulk(request):
        helper = DriverSearchFbHelper()

        parsed_request = helper.parse_request(request.get_data())
        parsed_request[0]['statuses'].sort()
        parsed_request[1]['statuses'].sort()

        assert parsed_request == [
            {
                'allowed_classes': ['econom'],
                'statuses': sorted(['free', 'on-order']),
                'search_id': 0,
            },
            {
                'allowed_classes': ['econom'],
                'statuses': sorted(['free', 'on-order']),
                'search_id': 1,
            },
        ]

        drivers = [
            {
                'dbid': '1488',
                'uuid': 'driverSS',
                'position': [37.251330952700464, 55.48777904452022],
                'classes': ['econom'],
                'status': 'free',
                'transport_type': 'car',
            },
            {
                'dbid': 'db777',
                'uuid': 'driver1',
                'position': [37.251330952700464, 55.48777904452022],
                'classes': ['econom'],
                'status': 'free',
                'transport_type': 'car',
            },
        ]

        return mockserver.make_response(
            response=helper.build_response(
                [{'search_id': 0, 'drivers': drivers}],
            ),
            content_type='application/x-flatbuffers',
        )

    @mockserver.json_handler('/contractor-status-history/events')
    def mock_driver_status(request):
        assert json.loads(request.get_data()) == {
            'interval': {'duration': 900},
            'contractors': [
                {'park_id': 'db777', 'profile_id': 'driver1'},
                {'park_id': '1488', 'profile_id': 'driverSS'},
            ],
            'verbose': False,
        }

        return mockserver.make_response(
            json.dumps(
                {
                    'contractors': [
                        {
                            'park_id': '1488',
                            'profile_id': 'driverSS',
                            'events': [],
                        },
                        {
                            'park_id': 'db777',
                            'profile_id': 'driver1',
                            'events': [
                                {
                                    'status': 'online',
                                    'timestamp': (
                                        1587988320  # 10 minutes passed
                                    ),
                                },
                            ],
                        },
                    ],
                },
            ),
            status=200,
            content_type='application/json',
        )

    mds_s3_storage.put_object(
        '/mds-s3/ae5208e9-e169-4106-b388-704db9061556',
        json.dumps(load_json('requests.json')).encode('utf-8'),
    )

    patched_request = load_json('request.json')
    del patched_request['data']['options']['air_dist_threshold_list']
    del patched_request['data']['options']['air_dist_include_probability_list']
    del patched_request['data']['options']['filter_by_dispatch_airport']
    if free_status_time_threshold:
        patched_request['data']['options'][
            'free_status_time_threshold'
        ] = free_status_time_threshold

    response = await taxi_reposition_relocator.put(
        'v2/call/search_candidates/' + NIRVANA_CALL_INSTANCE_ID,
        headers={'Authorization': 'OAuth any', 'X-Real-IP': '127.0.0.1'},
        json=patched_request,
    )

    assert response.status_code == 200
    assert response.json() == {
        'executionState': {
            'details': '',
            'message': 'Operation done successfully',
            'progress': 1.0,
            'result': 'SUCCESS',
            'status': 'FINISHED',
            'executionTimestamps': {
                'CHECK_AUTH': format_execution_timestamp(now, 0),
                'CREATE_OPERATION': format_execution_timestamp(now, 1),
                'DOWNLOAD_INPUTS': format_execution_timestamp(now, 2),
                'PROCESS_OPERATION': format_execution_timestamp(now, 3),
                'UPLOAD_OUTPUTS': format_execution_timestamp(now, 4),
            },
        },
        'ticket': NIRVANA_CALL_INSTANCE_ID,
    }

    expected_result = load_json('results.json')
    for request in expected_result['data']:
        for _, candidate in request['candidates'].items():
            candidate['tags'].sort()

    if free_status_time_threshold:
        del expected_result['data'][0]['candidates']['db777_driver1']
        del expected_result['data'][0]['demands_sources_candidates']['1']['1'][
            1
        ]

    stored_result = json.loads(
        mds_s3_storage.get_object(
            '/mds-s3/f855d81c-f988-4f35-8b6e-5a133dc0b518',
        ),
    )
    for request in stored_result['data']:
        for _, candidate in request['candidates'].items():
            candidate['tags'].sort()

    assert expected_result == stored_result

    assert mock_driver_search_bulk.times_called == 1
    assert mock_driver_status.times_called == (
        1 if free_status_time_threshold else 0
    )


@pytest.mark.now('2020-04-27T15:02:00+0300')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.parametrize('missing_type', ['inputs', 'outputs'])
async def test_put_missing_io(
        taxi_reposition_relocator,
        pgsql,
        mockserver,
        mds_s3_storage,
        load_json,
        now,
        missing_type,
):
    @mockserver.json_handler('/blackbox-team')
    def _mock_blackbox(request):
        return mockserver.make_response(
            json.dumps(
                {
                    'oauth': {
                        'uid': '0000000000000000',
                        'token_id': '0',
                        'device_id': '',
                        'device_name': '',
                        'scope': 'oauth:grant_xtoken',
                        'ctime': '2020-01-01 00:00:00',
                        'issue_time': '2020-01-01 00:00:00',
                        'expire_time': None,
                        'is_ttl_refreshable': False,
                        'client_id': 'any',
                        'client_name': 'any',
                        'client_icon': '',
                        'client_homepage': '',
                        'client_ctime': '2020-01-01 00:00:00',
                        'client_is_yandex': False,
                        'xtoken_id': '',
                        'meta': '',
                    },
                    'uid': {
                        'value': '0000000000000000',
                        'lite': False,
                        'hosted': False,
                    },
                    'login': 'robot-nirvana',
                    'have_password': True,
                    'have_hint': False,
                    'aliases': {'1': 'robot-nirvana'},
                    'karma': {'value': 0},
                    'karma_status': {'value': 0},
                    'dbfields': {'subscription.suid.669': ''},
                    'status': {'value': 'VALID', 'id': 0},
                    'error': 'OK',
                    'connection_id': 't:0',
                },
            ),
            status=200,
        )

    patched_request = load_json('request.json')
    patched_request['data'][missing_type] = {}

    response = await taxi_reposition_relocator.put(
        'v2/call/search_candidates/' + NIRVANA_CALL_INSTANCE_ID,
        headers={'Authorization': 'OAuth any', 'X-Real-IP': '127.0.0.1'},
        json=patched_request,
    )

    expected_details = ''
    if missing_type == 'inputs':
        expected_details = (
            'Exception: Operation required inputs: '
            '[requests], missing: [requests]'
        )
    else:
        expected_details = (
            'Exception: Operation required outputs: '
            '[results], missing: [results]'
        )

    assert response.status_code == 200
    assert response.json() == {
        'executionState': {
            'details': expected_details,
            'message': 'Operation search/search_candidates runtime failure',
            'progress': 1.0,
            'result': 'FAILURE',
            'status': 'FINISHED',
            'executionTimestamps': {
                'CHECK_AUTH': format_execution_timestamp(now, 0),
                'CREATE_OPERATION': format_execution_timestamp(now, 1),
            },
        },
        'ticket': NIRVANA_CALL_INSTANCE_ID,
    }


@pytest.mark.config(
    REPOSITION_RELOCATOR_ASYNC_REQUESTS_LIMITS={
        '__default__': {},
        'candidates_bulk_search': {'max_bulk_size': 1000},
    },
)
@pytest.mark.now('2020-04-27T15:02:00+0300')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
async def test_put_candidates_error(
        taxi_reposition_relocator,
        pgsql,
        mockserver,
        mds_s3_storage,
        load_json,
        now,
):
    @mockserver.json_handler('/blackbox-team')
    def _mock_blackbox(request):
        return mockserver.make_response(
            json.dumps(
                {
                    'oauth': {
                        'uid': '0000000000000000',
                        'token_id': '0',
                        'device_id': '',
                        'device_name': '',
                        'scope': 'oauth:grant_xtoken',
                        'ctime': '2020-01-01 00:00:00',
                        'issue_time': '2020-01-01 00:00:00',
                        'expire_time': None,
                        'is_ttl_refreshable': False,
                        'client_id': 'any',
                        'client_name': 'any',
                        'client_icon': '',
                        'client_homepage': '',
                        'client_ctime': '2020-01-01 00:00:00',
                        'client_is_yandex': False,
                        'xtoken_id': '',
                        'meta': '',
                    },
                    'uid': {
                        'value': '0000000000000000',
                        'lite': False,
                        'hosted': False,
                    },
                    'login': 'robot-nirvana',
                    'have_password': True,
                    'have_hint': False,
                    'aliases': {'1': 'robot-nirvana'},
                    'karma': {'value': 0},
                    'karma_status': {'value': 0},
                    'dbfields': {'subscription.suid.669': ''},
                    'status': {'value': 'VALID', 'id': 0},
                    'error': 'OK',
                    'connection_id': 't:0',
                },
            ),
            status=200,
        )

    @mockserver.json_handler('/candidates/search-bulk')
    def mock_driver_search_bulk(request):
        return mockserver.make_response('', 500)

    mds_s3_storage.put_object(
        '/mds-s3/ae5208e9-e169-4106-b388-704db9061556',
        json.dumps(load_json('requests.json')).encode('utf-8'),
    )

    response = await taxi_reposition_relocator.put(
        'v2/call/search_candidates/' + NIRVANA_CALL_INSTANCE_ID,
        headers={'Authorization': 'OAuth any', 'X-Real-IP': '127.0.0.1'},
        json=load_json('request.json'),
    )

    # TODO(sandyre): fixed texts for reposition request errors
    assert response.status_code == 200

    patched_response = response.json()
    patched_response['executionState']['details'] = ''

    assert patched_response == {
        'executionState': {
            'details': '',
            'message': 'Operation done successfully',
            'progress': 1.0,
            'result': 'SUCCESS',
            'status': 'FINISHED',
            'executionTimestamps': {
                'CHECK_AUTH': format_execution_timestamp(now, 0),
                'CREATE_OPERATION': format_execution_timestamp(now, 1),
                'DOWNLOAD_INPUTS': format_execution_timestamp(now, 2),
                'PROCESS_OPERATION': format_execution_timestamp(now, 3),
                'UPLOAD_OUTPUTS': format_execution_timestamp(now, 4),
            },
        },
        'ticket': NIRVANA_CALL_INSTANCE_ID,
    }

    expected_result = {
        'data': [],
        'meta': {'created_at': '2020-04-27T12:02:00+00:00'},
    }

    stored_result = json.loads(
        mds_s3_storage.get_object(
            '/mds-s3/f855d81c-f988-4f35-8b6e-5a133dc0b518',
        ),
    )

    assert expected_result == stored_result

    assert mock_driver_search_bulk.times_called == 3


@pytest.mark.geoareas(filename='geoareas_moscow.json')
async def test_forbidden(
        taxi_reposition_relocator, pgsql, mockserver, load_json,
):
    @mockserver.json_handler('/blackbox-team')
    def _mock_blackbox(request):
        return mockserver.make_response(
            json.dumps(
                {
                    'oauth': {
                        'uid': '0000000000000000',
                        'token_id': '0',
                        'device_id': '',
                        'device_name': '',
                        'scope': 'oauth:grant_xtoken',
                        'ctime': '2020-01-01 00:00:00',
                        'issue_time': '2020-01-01 00:00:00',
                        'expire_time': None,
                        'is_ttl_refreshable': False,
                        'client_id': 'any',
                        'client_name': 'any',
                        'client_icon': '',
                        'client_homepage': '',
                        'client_ctime': '2020-01-01 00:00:00',
                        'client_is_yandex': False,
                        'xtoken_id': '',
                        'meta': '',
                    },
                    'uid': {
                        'value': '0000000000000000',
                        'lite': False,
                        'hosted': False,
                    },
                    'login': 'any',
                    'have_password': True,
                    'have_hint': False,
                    'aliases': {'1': 'any'},
                    'karma': {'value': 0},
                    'karma_status': {'value': 0},
                    'dbfields': {'subscription.suid.669': ''},
                    'status': {'value': 'VALID', 'id': 0},
                    'error': 'OK',
                    'connection_id': 't:0',
                },
            ),
            status=200,
        )

    response = await taxi_reposition_relocator.put(
        'v2/call/search_candidates/' + NIRVANA_CALL_INSTANCE_ID,
        headers={'Authorization': 'OAuth any', 'X-Real-IP': '127.0.0.1'},
        json=load_json('request.json'),
    )

    assert response.status_code == 200
    assert response.json() == {
        'executionState': {
            'details': 'User is not allowed to perform this action',
            'message': 'Unauthorized user',
            'progress': 1.0,
            'result': 'FAILURE',
            'status': 'FINISHED',
        },
        'ticket': NIRVANA_CALL_INSTANCE_ID,
    }


@pytest.mark.nofilldb()
@pytest.mark.config(REPOSITION_RELOCATOR_PROCESSOR_ENABLED=False)
async def test_disabled(taxi_reposition_relocator, load_json):
    response = await taxi_reposition_relocator.put(
        'v2/call/echo/' + NIRVANA_CALL_INSTANCE_ID,
        headers={'Authorization': 'OAuth any', 'X-Real-IP': '127.0.0.1'},
        json=load_json('request.json'),
    )

    assert response.status_code == 200
    assert response.json() == {
        'executionState': {
            'details': 'Switcher is off in config',
            'message': 'Processor is disabled',
            'progress': 1.0,
            'result': 'FAILURE',
            'status': 'FINISHED',
        },
        'ticket': NIRVANA_CALL_INSTANCE_ID,
    }


@pytest.mark.config(
    REPOSITION_RELOCATOR_ASYNC_REQUESTS_LIMITS={
        '__default__': {'max_bulk_size': 1000},
    },
)
@pytest.mark.driver_tags_match(
    dbid='1488', uuid='driverSS', tags=['one_required_tag', 'must_have_tag'],
)
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.parametrize('dispatch_airport_filtering', [True, False])
@pytest.mark.now('2020-04-27T15:02:00+0300')
async def test_dispatch_airport_filtering(
        taxi_reposition_relocator,
        pgsql,
        mockserver,
        mds_s3_storage,
        load_json,
        now,
        dispatch_airport_filtering,
):
    @mockserver.json_handler('/blackbox-team')
    def _mock_blackbox(request):
        return mockserver.make_response(
            json.dumps(
                {
                    'oauth': {
                        'uid': '0000000000000000',
                        'token_id': '0',
                        'device_id': '',
                        'device_name': '',
                        'scope': 'oauth:grant_xtoken',
                        'ctime': '2020-01-01 00:00:00',
                        'issue_time': '2020-01-01 00:00:00',
                        'expire_time': None,
                        'is_ttl_refreshable': False,
                        'client_id': 'any',
                        'client_name': 'any',
                        'client_icon': '',
                        'client_homepage': '',
                        'client_ctime': '2020-01-01 00:00:00',
                        'client_is_yandex': False,
                        'xtoken_id': '',
                        'meta': '',
                    },
                    'uid': {
                        'value': '0000000000000000',
                        'lite': False,
                        'hosted': False,
                    },
                    'login': 'robot-nirvana',
                    'have_password': True,
                    'have_hint': False,
                    'aliases': {'1': 'robot-nirvana'},
                    'karma': {'value': 0},
                    'karma_status': {'value': 0},
                    'dbfields': {'subscription.suid.669': ''},
                    'status': {'value': 'VALID', 'id': 0},
                    'error': 'OK',
                    'connection_id': 't:0',
                },
            ),
            status=200,
        )

    @mockserver.json_handler('/candidates/search-bulk')
    def mock_driver_search_bulk(request):
        helper = DriverSearchFbHelper()

        parsed_request = helper.parse_request(request.get_data())
        parsed_request[0]['statuses'].sort()
        parsed_request[1]['statuses'].sort()

        assert parsed_request == [
            {
                'allowed_classes': ['econom'],
                'statuses': sorted(['free', 'on-order']),
                'search_id': 0,
            },
            {
                'allowed_classes': ['econom'],
                'statuses': sorted(['free', 'on-order']),
                'search_id': 1,
            },
        ]

        drivers = [
            {
                'dbid': '1488',
                'uuid': 'driverSS',
                'position': [37.251330952700464, 55.48777904452022],
                'classes': ['econom'],
                'status': 'free',
                'transport_type': 'car',
            },
            {
                'dbid': '1488',
                'uuid': 'driverSS2',
                'position': [37.251330952700464, 55.48777904452022],
                'classes': ['econom'],
                'status': 'busy',
                'transport_type': 'car',
            },
            {
                'dbid': 'parko',
                'uuid': 'uuido',
                'position': [37.251330952700464, 55.48777904452022],
                'classes': ['econom'],
                'status': 'free',
                'transport_type': 'car',
            },
        ]
        return mockserver.make_response(
            response=helper.build_response(
                [{'search_id': 0, 'drivers': drivers}],
            ),
            content_type='application/x-flatbuffers',
        )

    @mockserver.json_handler('/dispatch-airport/v1/reposition_availability')
    def mock_dispatch_airport(request):
        return mockserver.make_response(
            json.dumps(
                {
                    'allowed': (
                        []
                        if dispatch_airport_filtering
                        else request.json['driver_ids']
                    ),
                    'forbidden': (
                        [
                            {
                                'driver_id': driver,
                                'reason': 'I dont want to pass',
                            }
                            for driver in request.json['driver_ids']
                        ]
                        if dispatch_airport_filtering
                        else []
                    ),
                },
            ),
        )

    mds_s3_storage.put_object(
        '/mds-s3/ae5208e9-e169-4106-b388-704db9061556',
        json.dumps(load_json('requests.json')).encode('utf-8'),
    )
    patched_request = load_json('request.json')

    del patched_request['data']['options']['air_dist_threshold_list']
    del patched_request['data']['options']['air_dist_include_probability_list']

    response = await taxi_reposition_relocator.put(
        'v2/call/search_candidates/' + NIRVANA_CALL_INSTANCE_ID,
        headers={'Authorization': 'OAuth any', 'X-Real-IP': '127.0.0.1'},
        json=patched_request,
    )

    assert response.status_code == 200
    assert response.json() == {
        'executionState': {
            'details': '',
            'message': 'Operation done successfully',
            'progress': 1.0,
            'result': 'SUCCESS',
            'status': 'FINISHED',
            'executionTimestamps': {
                'CHECK_AUTH': format_execution_timestamp(now, 0),
                'CREATE_OPERATION': format_execution_timestamp(now, 1),
                'DOWNLOAD_INPUTS': format_execution_timestamp(now, 2),
                'PROCESS_OPERATION': format_execution_timestamp(now, 3),
                'UPLOAD_OUTPUTS': format_execution_timestamp(now, 4),
            },
        },
        'ticket': NIRVANA_CALL_INSTANCE_ID,
    }

    if not dispatch_airport_filtering:
        expected_result = load_json('results.json')
        for request in expected_result['data']:
            for _, candidate in request['candidates'].items():
                candidate['tags'].sort()
        del expected_result['data'][0]['candidates']['db777_driver1']
        del expected_result['data'][0]['demands_sources_candidates']['1']['1'][
            -1
        ]
    else:
        expected_result = {
            'data': [],
            'meta': {'created_at': '2020-04-27T12:02:00+00:00'},
        }

    stored_result = json.loads(
        mds_s3_storage.get_object(
            '/mds-s3/f855d81c-f988-4f35-8b6e-5a133dc0b518',
        ),
    )
    for request in stored_result['data']:
        for _, candidate in request['candidates'].items():
            candidate['tags'].sort()

    assert expected_result == stored_result

    assert mock_driver_search_bulk.times_called == 1
    assert mock_dispatch_airport.times_called == 1
