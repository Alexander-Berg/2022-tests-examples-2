# pylint: disable=import-error, import-only-modules, too-many-lines
import copy
import datetime
import json

import flatbuffers
import pytest
from reposition_api.fbs.v1.service.make_offer import OfferResponse
from reposition_api.fbs.v1.service.make_offer import (
    Request as MakeOfferRequest,
)
from reposition_api.fbs.v1.service.make_offer import (
    Response as MakeOfferResponse,
)
from reposition_api.fbs.v1.service.make_offer.Origin import Origin

from .utils import format_execution_timestamp
from .utils import select_named


NIRVANA_CALL_INSTANCE_ID = 'somerandomid'


class MakeOfferFbHelper:
    def read_str(self, fbs_output):
        if not fbs_output:
            return ''
        return fbs_output.decode('utf-8')

    def parse_request(self, data):
        offers = []
        request = MakeOfferRequest.Request.GetRootAsRequest(data, 0)
        for i in range(0, request.OffersLength()):
            offer = request.Offers(i)
            tags = []
            completed_tags = []
            for tag in range(0, offer.TagsLength()):
                tags.append(self.read_str(offer.Tags(tag)))
            for tag in range(0, offer.CompletedTagsLength()):
                completed_tags.append(self.read_str(offer.CompletedTags(tag)))
            meta_request = offer.Metadata()
            meta = dict()
            if meta_request:
                queue_id = self.read_str(meta_request.AirportQueueId())
                if queue_id:
                    meta['airport_queue_id'] = queue_id
                classes = []
                for airport_cl in range(0, meta_request.ClassesLength()):
                    classes.append(
                        self.read_str(meta_request.Classes(airport_cl)),
                    )
                if classes:
                    meta['classes'] = classes
                meta['surge_pin_value'] = meta_request.SurgePinValue()
                meta['is_surge_pin'] = meta_request.IsSurgePin()

            offers.append(
                {
                    'park_db_id': self.read_str(offer.ParkDbId()),
                    'driver_id': self.read_str(offer.DriverId()),
                    'mode_name': self.read_str(offer.ModeName()),
                    'address': self.read_str(offer.Address()),
                    'city': self.read_str(offer.City()),
                    'start_until': datetime.datetime.fromtimestamp(
                        offer.StartUntil(),
                    ),
                    'finish_until': datetime.datetime.fromtimestamp(
                        offer.FinishUntil(),
                    ),
                    'image_id': self.read_str(offer.ImageId()),
                    'name': self.read_str(offer.Name()),
                    'description': self.read_str(offer.Description()),
                    'tags': tags,
                    'completed_tags': completed_tags,
                    'tariff_class': self.read_str(offer.TariffClass()),
                    'origin': offer.Origin(),
                    'auto_accept': offer.AutoAccept(),
                    'metadata': meta,
                },
            )
        return offers

    def build_response(self, data):
        builder = flatbuffers.Builder(0)
        responses = []
        for result in data:
            dbid_fbs = builder.CreateString(result['park_db_id'])
            uuid_fbs = builder.CreateString(result['driver_id'])
            point_id_fbs = builder.CreateString(result['point_id'])
            error_fbs = None
            if 'error' in result:
                error_fbs = builder.CreateString(result['error'])
            OfferResponse.OfferResponseStart(builder)
            OfferResponse.OfferResponseAddDriverId(builder, uuid_fbs)
            OfferResponse.OfferResponseAddParkDbId(builder, dbid_fbs)
            OfferResponse.OfferResponseAddPointId(builder, point_id_fbs)
            if error_fbs:
                OfferResponse.OfferResponseAddError(builder, error_fbs)
            res = OfferResponse.OfferResponseEnd(builder)
            responses.append(res)
        MakeOfferResponse.ResponseStartResultsVector(builder, len(responses))
        for response in responses:
            builder.PrependUOffsetTRelative(response)
        responses_vec = builder.EndVector(len(responses))

        MakeOfferResponse.ResponseStart(builder)
        MakeOfferResponse.ResponseAddResults(builder, responses_vec)
        response = MakeOfferResponse.ResponseEnd(builder)
        builder.Finish(response)
        return builder.Output()


@pytest.mark.now('2017-10-15T12:00:00')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.pgsql('reposition-relocator', files=['graph_operations.sql'])
async def test_put(
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

    @mockserver.json_handler('reposition-api/v1/service/make_offer')
    def mock_make_offer(request):
        helper = MakeOfferFbHelper()
        expected_request = [
            {
                'address': '',
                'auto_accept': False,
                'city': '',
                'completed_tags': [
                    'reposition_super_surge_from_nirvana_completed',
                ],
                'description': 'Move to high demand area',
                'driver_id': 'uuid',
                'finish_until': datetime.datetime(2017, 10, 15, 21, 18, 46),
                'image_id': 'icon',
                'metadata': {'surge_pin_value': 0.5, 'is_surge_pin': True},
                'mode_name': 'SuperSurge',
                'name': 'SuperSurge',
                'origin': Origin.kRepositionNirvana,
                'park_db_id': 'dbid',
                'start_until': datetime.datetime(2017, 10, 15, 21, 18, 46),
                'tags': ['reposition_super_surge_from_nirvana'],
                'tariff_class': '',
            },
        ]
        response_data = [
            {
                'park_db_id': 'dbid',
                'driver_id': 'uuid',
                'point_id': 'offer_point_id',
            },
        ]
        assert helper.parse_request(request.get_data()) == expected_request
        return mockserver.make_response(
            response=helper.build_response(response_data),
            content_type='application/x-flatbuffers',
        )

    mds_s3_storage.put_object(
        '/mds-s3/ae5208e9-e169-4106-b388-704db9061556',
        json.dumps(load_json('drafts.json')).encode('utf-8'),
    )

    response = await taxi_reposition_relocator.put(
        'v2/call/make_offer/' + NIRVANA_CALL_INSTANCE_ID,
        headers={'Authorization': 'OAuth any', 'X-Real-IP': '127.0.0.1'},
        json=load_json('request.json'),
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
                'CHECK_OPERATION_AUTH': format_execution_timestamp(now, 2),
                'DOWNLOAD_INPUTS': format_execution_timestamp(now, 3),
                'PROCESS_OPERATION': format_execution_timestamp(now, 4),
                'UPLOAD_OUTPUTS': format_execution_timestamp(now, 5),
            },
        },
        'ticket': NIRVANA_CALL_INSTANCE_ID,
    }

    assert load_json('results.json') == json.loads(
        mds_s3_storage.get_object(
            '/mds-s3/f855d81c-f988-4f35-8b6e-5a133dc0b518',
        ),
    )

    assert mock_make_offer.times_called == 1

    tags_to_upload = select_named(
        'SELECT * FROM state.uploading_tags', pgsql['reposition-relocator'],
    )
    assert tags_to_upload == [
        {
            'id': 1,
            'merge_policy': 'append',
            'driver_id': '(dbid,uuid)',
            'tags': ['reposition_offer_sent'],
            'created_at': datetime.datetime(2017, 10, 15, 12, 00, 00),
            'until': datetime.datetime(2017, 10, 15, 18, 18, 46),
        },
    ]


@pytest.mark.now('2017-10-15T12:00:00')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.pgsql('reposition-relocator', files=['graph_operations.sql'])
async def test_put_airport(
        taxi_reposition_relocator,
        pgsql,
        mockserver,
        mds_s3_storage,
        load_json,
        now,
        testpoint,
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

    @mockserver.json_handler('reposition-api/v1/service/make_offer')
    def mock_make_offer(request):
        helper = MakeOfferFbHelper()
        expected_request = [
            {
                'address': '',
                'auto_accept': False,
                'city': '',
                'completed_tags': [
                    'reposition_airport_from_nirvana_completed',
                ],
                'description': 'Move to high demand area',
                'driver_id': 'uuid',
                'finish_until': datetime.datetime(2017, 10, 15, 21, 18, 46),
                'image_id': 'icon',
                'metadata': {
                    'airport_queue_id': 'dme',
                    'classes': sorted(['econom', 'comfort']),
                    'surge_pin_value': -1.0,
                    'is_surge_pin': False,
                },
                'mode_name': 'Airport',
                'name': 'Airport',
                'origin': Origin.kRepositionNirvana,
                'park_db_id': 'dbid',
                'start_until': datetime.datetime(2017, 10, 15, 21, 18, 46),
                'tags': ['reposition_airport_from_nirvana'],
                'tariff_class': '',
            },
        ]
        response_data = [
            {
                'park_db_id': 'dbid',
                'driver_id': 'uuid',
                'point_id': 'offer_point_id',
            },
        ]

        req_json = helper.parse_request(request.get_data())
        req_json[0]['metadata']['classes'].sort()
        assert req_json == expected_request
        return mockserver.make_response(
            response=helper.build_response(response_data),
            content_type='application/x-flatbuffers',
        )

    @testpoint('offers_statistics.extend_statistics')
    def offers_statistics(data):
        return data

    mds_s3_storage.put_object(
        '/mds-s3/ae5208e9-e169-4106-b388-704db9061556',
        json.dumps(load_json('airport_draft.json')).encode('utf-8'),
    )

    response = await taxi_reposition_relocator.put(
        'v2/call/make_offer/' + NIRVANA_CALL_INSTANCE_ID,
        headers={'Authorization': 'OAuth any', 'X-Real-IP': '127.0.0.1'},
        json=load_json('request.json'),
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
                'CHECK_OPERATION_AUTH': format_execution_timestamp(now, 2),
                'DOWNLOAD_INPUTS': format_execution_timestamp(now, 3),
                'PROCESS_OPERATION': format_execution_timestamp(now, 4),
                'UPLOAD_OUTPUTS': format_execution_timestamp(now, 5),
            },
        },
        'ticket': NIRVANA_CALL_INSTANCE_ID,
    }

    assert load_json('results.json') == json.loads(
        mds_s3_storage.get_object(
            '/mds-s3/f855d81c-f988-4f35-8b6e-5a133dc0b518',
        ),
    )

    assert mock_make_offer.times_called == 1

    tags_to_upload = select_named(
        'SELECT * FROM state.uploading_tags', pgsql['reposition-relocator'],
    )
    assert tags_to_upload == [
        {
            'id': 1,
            'merge_policy': 'append',
            'driver_id': '(dbid,uuid)',
            'tags': ['reposition_offer_sent'],
            'created_at': datetime.datetime(2017, 10, 15, 12, 00, 00),
            'until': datetime.datetime(2017, 10, 15, 18, 18, 46),
        },
    ]

    await taxi_reposition_relocator.run_task(
        'offers_statistics.extend_statistics',
    )
    offers_statistics_data = (await offers_statistics.wait_call())['data']
    assert offers_statistics_data == {'airport_offers': {'dme': 1}}


@pytest.mark.now('2017-10-15T12:00:00')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.pgsql('reposition-relocator', files=['graph_operations.sql'])
@pytest.mark.parametrize('profile_status', ('free', 'busy'))
@pytest.mark.parametrize('duplicate_offers', (True, False))
async def test_put_autoaccepted_offers(
        taxi_reposition_relocator,
        pgsql,
        mockserver,
        mds_s3_storage,
        load_json,
        testpoint,
        now,
        profile_status,
        duplicate_offers,
):
    yt_requests = dict()

    @testpoint('reposition-relocator::yt_log_offers')
    def _yt_log_offers(data):
        yt_requests.update(data)

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

    @mockserver.json_handler('/candidates/profiles')
    def mock_candidates_profiles(request):
        return mockserver.make_response(
            json.dumps(
                {
                    'drivers': [
                        {
                            'dbid': 'dbid',
                            'uuid': 'uuid',
                            'position': [37.619757, 55.753215],
                            'status': {
                                'taximeter': profile_status,
                                'orders': [],
                            },
                        },
                        {
                            'dbid': 'dbid',
                            'uuid': 'uuid1',
                            'position': [37.619757, 55.753215],
                            'status': {
                                'taximeter': 'busy',
                                'some_info': 'free',
                            },
                        },
                    ],
                },
            ),
            status=200,
        )

    @mockserver.json_handler('reposition-api/v1/service/make_offer')
    def mock_make_offer(request):
        helper = MakeOfferFbHelper()
        expected_request = []
        response_data = []
        if profile_status == 'free':
            expected_request = [
                {
                    'address': '',
                    'auto_accept': True,
                    'city': '',
                    'completed_tags': [
                        'reposition_super_surge_from_nirvana_completed',
                    ],
                    'description': 'Move to high demand area',
                    'driver_id': 'uuid',
                    'finish_until': datetime.datetime(
                        2017, 10, 15, 21, 18, 46,
                    ),
                    'image_id': 'icon',
                    'metadata': {'surge_pin_value': 0.5, 'is_surge_pin': True},
                    'mode_name': 'SuperSurge',
                    'name': 'SuperSurge',
                    'origin': Origin.kRepositionNirvana,
                    'park_db_id': 'dbid',
                    'start_until': datetime.datetime(2017, 10, 15, 21, 18, 46),
                    'tags': ['reposition_super_surge_from_nirvana'],
                    'tariff_class': '',
                },
            ]
            response_data = [
                {
                    'park_db_id': 'dbid',
                    'driver_id': 'uuid',
                    'point_id': 'offer_point_id',
                },
            ]
        assert helper.parse_request(request.get_data()) == expected_request
        return mockserver.make_response(
            response=helper.build_response(response_data),
            content_type='application/x-flatbuffers',
        )

    drafts = load_json('drafts.json')
    drafts['data'].append(copy.deepcopy(drafts['data'][0]))
    drafts['data'][0]['draft_id'] += '_0'
    drafts['data'][0]['driver_id']['driver_profile_id'] += '1'

    if duplicate_offers:
        drafts['data'].append(drafts['data'][0])
    mds_s3_storage.put_object(
        '/mds-s3/ae5208e9-e169-4106-b388-704db9061556',
        json.dumps(drafts).encode('utf-8'),
    )

    request = load_json('request.json')
    request['data']['options']['auto_accept'] = True
    response = await taxi_reposition_relocator.put(
        'v2/call/make_offer/' + NIRVANA_CALL_INSTANCE_ID,
        headers={'Authorization': 'OAuth any', 'X-Real-IP': '127.0.0.1'},
        json=request,
    )

    assert response.status_code == 200
    if duplicate_offers:
        assert response.json() == {
            'executionState': {
                'details': (
                    'Exception: Provided multiple auto accepted'
                    ' offers for the driver dbid_uuid1'
                ),
                'message': 'Operation reposition/make_offer runtime failure',
                'progress': 1.0,
                'result': 'FAILURE',
                'status': 'FINISHED',
                'executionTimestamps': {
                    'CHECK_AUTH': format_execution_timestamp(now, 0),
                    'CREATE_OPERATION': format_execution_timestamp(now, 1),
                    'CHECK_OPERATION_AUTH': format_execution_timestamp(now, 2),
                    'DOWNLOAD_INPUTS': format_execution_timestamp(now, 3),
                    'PROCESS_OPERATION': format_execution_timestamp(now, 4),
                },
            },
            'ticket': NIRVANA_CALL_INSTANCE_ID,
        }

        assert mock_candidates_profiles.times_called == 0
        assert mock_make_offer.times_called == 0
        return

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
                'CHECK_OPERATION_AUTH': format_execution_timestamp(now, 2),
                'DOWNLOAD_INPUTS': format_execution_timestamp(now, 3),
                'PROCESS_OPERATION': format_execution_timestamp(now, 4),
                'UPLOAD_OUTPUTS': format_execution_timestamp(now, 5),
            },
        },
        'ticket': NIRVANA_CALL_INSTANCE_ID,
    }

    if profile_status == 'free':
        assert load_json('results.json') == json.loads(
            mds_s3_storage.get_object(
                '/mds-s3/f855d81c-f988-4f35-8b6e-5a133dc0b518',
            ),
        )

        assert yt_requests == {
            'draft_id': 'some_random_string',
            'offer_id': 'offer_point_id',
        }

        assert mock_candidates_profiles.times_called == 1
        assert mock_make_offer.times_called == 1

        tags_to_upload = select_named(
            'SELECT * FROM state.uploading_tags',
            pgsql['reposition-relocator'],
        )
        assert tags_to_upload == [
            {
                'id': 1,
                'merge_policy': 'append',
                'driver_id': '(dbid,uuid)',
                'tags': ['reposition_offer_sent'],
                'created_at': datetime.datetime(2017, 10, 15, 12, 00, 00),
                'until': datetime.datetime(2017, 10, 15, 18, 18, 46),
            },
        ]
    else:
        assert (
            {'meta': {'created_at': '2017-10-15T12:00:00+00:00'}, 'data': []}
            == json.loads(
                mds_s3_storage.get_object(
                    '/mds-s3/f855d81c-f988-4f35-8b6e-5a133dc0b518',
                ),
            )
        )

        assert mock_candidates_profiles.times_called == 1
        assert mock_make_offer.times_called == 1

        tags_to_upload = select_named(
            'SELECT * FROM state.uploading_tags',
            pgsql['reposition-relocator'],
        )
        assert tags_to_upload == []


@pytest.mark.now('2017-10-15T12:00:00')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.pgsql('reposition-relocator', files=['graph_operations.sql'])
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

    @mockserver.json_handler('reposition-api/v1/service/make_offer')
    def mock_make_offer(_):
        return mockserver.make_response('', 500)

    patched_request = load_json('request.json')
    patched_request['data'][missing_type] = {}

    response = await taxi_reposition_relocator.put(
        'v2/call/make_offer/' + NIRVANA_CALL_INSTANCE_ID,
        headers={'Authorization': 'OAuth any', 'X-Real-IP': '127.0.0.1'},
        json=patched_request,
    )

    expected_details = ''
    if missing_type == 'inputs':
        expected_details = (
            'Exception: Operation required inputs: '
            '[drafts], missing: [drafts]'
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
            'message': 'Operation reposition/make_offer runtime failure',
            'progress': 1.0,
            'result': 'FAILURE',
            'status': 'FINISHED',
            'executionTimestamps': {
                'CHECK_AUTH': format_execution_timestamp(now, 0),
                'CREATE_OPERATION': format_execution_timestamp(now, 1),
                'CHECK_OPERATION_AUTH': format_execution_timestamp(now, 2),
            },
        },
        'ticket': NIRVANA_CALL_INSTANCE_ID,
    }

    assert mock_make_offer.times_called == 0


@pytest.mark.now('2017-10-15T12:00:00')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.pgsql('reposition-relocator', files=['graph_operations.sql'])
async def test_put_reposition_error(
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

    @mockserver.json_handler('reposition-api/v1/service/make_offer')
    def mock_make_offer(request):
        return mockserver.make_response('', 500)

    mds_s3_storage.put_object(
        '/mds-s3/ae5208e9-e169-4106-b388-704db9061556',
        json.dumps(load_json('drafts.json')).encode('utf-8'),
    )

    response = await taxi_reposition_relocator.put(
        'v2/call/make_offer/' + NIRVANA_CALL_INSTANCE_ID,
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
            'message': 'Operation reposition/make_offer runtime failure',
            'progress': 1.0,
            'result': 'FAILURE',
            'status': 'FINISHED',
            'executionTimestamps': {
                'CHECK_AUTH': format_execution_timestamp(now, 0),
                'CREATE_OPERATION': format_execution_timestamp(now, 1),
                'CHECK_OPERATION_AUTH': format_execution_timestamp(now, 2),
                'DOWNLOAD_INPUTS': format_execution_timestamp(now, 3),
                'PROCESS_OPERATION': format_execution_timestamp(now, 4),
            },
        },
        'ticket': NIRVANA_CALL_INSTANCE_ID,
    }

    assert mock_make_offer.times_called == 1


@pytest.mark.now('2017-10-15T12:00:00')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
async def test_put_untrusted(
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

    @mockserver.json_handler('reposition-api/v1/service/make_offer')
    def _mock_make_offer(request):
        return mockserver.make_response('', 500)

    mds_s3_storage.put_object(
        '/mds-s3/ae5208e9-e169-4106-b388-704db9061556',
        json.dumps(load_json('drafts.json')).encode('utf-8'),
    )

    response = await taxi_reposition_relocator.put(
        'v2/call/make_offer/' + NIRVANA_CALL_INSTANCE_ID,
        headers={'Authorization': 'OAuth any', 'X-Real-IP': '127.0.0.1'},
        json=load_json('request.json'),
    )

    assert response.status_code == 200
    assert response.json() == {
        'executionState': {
            'details': (
                'Exception: Graph operation \'graph_make_offer_id\' is '
                'forbidden to be executed, because it\'s not in trusted graph '
                'operations list.'
            ),
            'message': 'Operation reposition/make_offer runtime failure',
            'progress': 1.0,
            'result': 'FAILURE',
            'status': 'FINISHED',
            'executionTimestamps': {
                'CHECK_AUTH': format_execution_timestamp(now, 0),
                'CREATE_OPERATION': format_execution_timestamp(now, 1),
                'CHECK_OPERATION_AUTH': format_execution_timestamp(now, 2),
            },
        },
        'ticket': NIRVANA_CALL_INSTANCE_ID,
    }

    assert _mock_make_offer.times_called == 0


@pytest.mark.filldb()
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

    @mockserver.json_handler('reposition-api/v1/service/make_offer')
    def mock_make_offer(_):
        return mockserver.make_response('', 500)

    response = await taxi_reposition_relocator.put(
        'v2/call/make_offer/' + NIRVANA_CALL_INSTANCE_ID,
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

    assert mock_make_offer.times_called == 0


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
