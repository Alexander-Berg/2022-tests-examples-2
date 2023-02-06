# pylint: disable=import-error
import datetime

import pytest
from reposition_api.fbs.v1.service.make_offer.Origin import Origin

from tests_dispatch_airport import common
import tests_dispatch_airport.utils as utils


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql(
    'dispatch_airport', files=['drivers_queue.sql', 'driver_events.sql'],
)
@pytest.mark.now('2017-10-15T12:00:00+00:00')
@pytest.mark.parametrize('empty_point', [False, True])
@pytest.mark.parametrize(
    'is_non_default_relocation_resources_cfg_using,'
    'restriction_resources_case_name, use_idempotency_token',
    [
        (False, 'default_restriction_resources', False),
        (False, 'default_restriction_resources', True),
        (True, 'empty_restriction_resources', False),
        (True, 'one_restriction_resources', False),
        (True, 'two_restriction_resources', False),
        (True, 'empty_image_restriction_resources', False),
    ],
)
@pytest.mark.config(
    SVO_POLYGON_NAMES={
        'DL1': {
            'full_text': 'aeroport sheremetevo D',
            'point': [61, 11],
            'target_airport_id': 'svo',
        },
    },
)
@pytest.mark.config(
    DISPATCH_AIRPORT_REPOSITION_PUSH_SETTINGS={'delays': [1, 2, 3]},
)
async def test_relocate_start(
        taxi_dispatch_airport,
        mockserver,
        testpoint,
        pgsql,
        taxi_config,
        load_json,
        empty_point,
        is_non_default_relocation_resources_cfg_using,
        restriction_resources_case_name,
        use_idempotency_token,
):
    @testpoint('send_push')
    def send_push(push):
        return push

    @mockserver.json_handler('/client-notify/v2/push')
    def _client_notify_push(request):
        return {'notification_id': ''}

    driver_id = 'uuid1'
    if is_non_default_relocation_resources_cfg_using:
        taxi_config.set_values(
            {
                'DISPATCH_AIRPORT_RELOCATION_REPOSITION_RESOURCES': (
                    load_json(
                        'resources_configs/'
                        + restriction_resources_case_name
                        + '.json',
                    )
                ),
            },
        )
    expected_translations = load_json(
        'expected_translations/' + restriction_resources_case_name + '.json',
    )

    def _mock(request):
        nonlocal driver_id
        helper = utils.MakeOfferFbHelper()
        driver_has_no_locale = driver_id == 'uuid1'
        expected_request = [
            {
                'address': '',
                'auto_accept': True,
                'city': '',
                'completed_tags': [],
                'description': (
                    expected_translations['description']
                    if driver_has_no_locale
                    else 'en: ' + expected_translations['description']
                ),
                'driver_id': driver_id,
                'finish_until': datetime.datetime(
                    2017, 10, 15, 12, 15, 0, 0, tzinfo=datetime.timezone.utc,
                ),
                'image_id': 'icon',
                'mode_name': 'Sintegro',
                'name': '',
                'origin': Origin.kSintegro,
                'park_db_id': 'dbid',
                'start_until': datetime.datetime(
                    2017, 10, 15, 12, 0, 30, tzinfo=datetime.timezone.utc,
                ),
                'tags': [],
                'tariff_class': '',
                'metadata': {'airport_queue_id': 'svo'},
                'restrictions': (
                    expected_translations['restrictions']
                    if driver_has_no_locale
                    else utils.transform_restrictions_to_eng(
                        expected_translations['restrictions'],
                    )
                ),
            },
        ]
        parsed_request = helper.parse_request(request.get_data())
        if use_idempotency_token:
            expected_request[0]['draft_id'] = 'dispatch-airport/some_token'
        else:
            draft_id = parsed_request[0].pop('draft_id')
            assert draft_id != 'dispatch-airport/some_token'
            assert draft_id.startswith('dispatch-airport')

        assert parsed_request == expected_request

        response_data = [
            {
                'park_db_id': 'dbid',
                'driver_id': driver_id,
                'point_id': '' if empty_point else 'reposition_id',
            },
        ]

        return mockserver.make_response(
            response=helper.build_response(response_data),
            content_type='application/x-flatbuffers',
        )

    @mockserver.json_handler('/reposition-api/v1/service/make_offer')
    def _mock_reposition_api_make_offer(request):
        return _mock(request)

    for car_number, uuid, udid, session_id in [
            ('a123bc', 'uuid1', 'udid1', 'dbid_uuid1_reposition_id'),
            ('a123lm', 'uuid6', 'udid6', 'dbid_uuid6_reposition_id'),
    ]:
        headers = common.DEFAULT_DISPATCH_AIRPORT_HEADER
        if use_idempotency_token:
            headers = {**headers, 'X-Idempotency-Token': 'some_token'}
        driver_id = uuid
        resp = await taxi_dispatch_airport.post(
            '/v1/relocate/start',
            {'car_number': car_number, 'polygon_id': 'DL1'},
            headers=headers,
        )

        r_json = resp.json()
        etalon_json = {'session_id': session_id}
        if empty_point:
            etalon_json = {
                'code': 'CREATE_OFFER_ERROR',
                'message': 'Create offer error',
            }
        assert etalon_json == r_json

        db = pgsql['dispatch_airport']
        etalon = {
            ('udid1', 'old_session_id1', 'relocate_offer_created'): {
                'driver_id': 'dbid_uuid1',
                'airport_id': 'ekb',
                'details': {
                    'relocation_info': {
                        'target_airport_queue_id': 'svo',
                        'taximeter_tariffs': ['comfortplus', 'econom'],
                    },
                },
            },
        }
        if udid == 'udid6':
            etalon = {
                ('udid6', 'old_session_id6', 'relocate_offer_created'): {
                    'driver_id': 'dbid_uuid6',
                    'airport_id': 'ekb',
                    'details': {
                        'relocation_info': {
                            'target_airport_queue_id': 'svo',
                            'taximeter_tariffs': ['comfortplus', 'econom'],
                        },
                    },
                },
            }

        assert utils.get_driver_events(db, udid) == etalon

        if not empty_point:
            for i in range(1, 4):
                push = (await send_push.wait_call())['push']
                assert push['idempotency_token'] == 'dbid_' + uuid + str(i)
                assert push['body'] == {
                    'intent': 'ForcePollingOrder',
                    'service': 'taximeter',
                    'client_id': 'dbid-' + uuid,
                    'ttl': 5,
                    'data': {'code': 1600},
                }

    assert _mock_reposition_api_make_offer.times_called == 2


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql(
    'dispatch_airport', files=['drivers_queue.sql', 'driver_events.sql'],
)
@pytest.mark.now('2017-10-15T12:00:00')
@pytest.mark.config(
    SVO_POLYGON_NAMES={
        'DL1': {
            'full_text': 'aeroport sheremetevo D',
            'point': [61, 11],
            'target_airport_id': 'svo',
        },
    },
)
async def test_relocate_start_save_mode_info(
        taxi_dispatch_airport, mockserver, pgsql, load_json, testpoint, mode,
):
    @testpoint(utils.QUEUE_UPDATER_NAME + '-finished')
    def queue_update_finished(_):
        pass

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(_):
        return {}

    def _mock(request):
        helper = utils.MakeOfferFbHelper()
        driver_id = helper.parse_request(request.get_data())[0]['driver_id']
        response_data = [
            {
                'park_db_id': 'dbid',
                'driver_id': driver_id,
                'point_id': 'reposition_id',
            },
        ]
        return mockserver.make_response(
            response=helper.build_response(response_data),
            content_type='application/x-flatbuffers',
        )

    @mockserver.json_handler('/reposition-api/v1/service/make_offer')
    def _mock_reposition_api_make_offer(request):
        return _mock(request)

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()
    # need to set driver.old_mode_enabled
    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')
    await utils.wait_certain_testpoint('ekb', queue_update_finished)

    await taxi_dispatch_airport.invalidate_caches()

    etalons = load_json('relocation_start_events_etalon.json')
    for car_number, _, udid, session_id in [
            ('a123bc', 'uuid1', 'udid1', 'dbid_uuid1_reposition_id'),
            ('a123lm', 'uuid6', 'udid6', 'dbid_uuid6_reposition_id'),
            ('a123no', 'uuid7', 'udid7', 'dbid_uuid7_reposition_id'),
            ('a123pq', 'uuid8', 'udid8', 'dbid_uuid8_reposition_id'),
    ]:
        resp = await taxi_dispatch_airport.post(
            '/v1/relocate/start',
            {'car_number': car_number, 'polygon_id': 'DL1'},
            headers=common.DEFAULT_DISPATCH_AIRPORT_HEADER,
        )

        r_json = resp.json()
        etalon_json = {'session_id': session_id}
        assert etalon_json == r_json

        db = pgsql['dispatch_airport']
        event = etalons[udid]
        if mode in ['mixed_base_old', 'mixed_base_new'] and event['udid'] in [
                'udid6',
                'udid8',
        ]:
            event['details']['relocation_info']['new_mode_tariffs'] = [
                'comfortplus',
            ]
        assert utils.get_driver_events(db, udid) == {
            (event['udid'], event['old_session_id'], event['event_type']): {
                'driver_id': event['driver_id'],
                'airport_id': event['airport_id'],
                'details': event['details'],
            },
        }


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.config(
    SVO_POLYGON_NAMES={
        'DL1': {
            'full_text': 'aeroport sheremetevo D',
            'point': [61, 11],
            'target_airport_id': 'svo',
        },
    },
)
@pytest.mark.busy_drivers(
    busy_drivers=[
        {
            'driver_id': 'dbid_uuid4',
            'order_id': 'order_id_1',
            'taxi_status': 3,
            'final_destination': {'lat': 11.0, 'lon': 21.0},
        },
    ],
)
@pytest.mark.parametrize(
    'car_number,poligon,status,result',
    [
        (
            'a123hi',
            'DL1',
            200,
            {
                'session_creation_fail_reason_code': 'BUSY_DRIVER',
                'session_creation_fail_reason_msg': 'Driver is busy',
            },
        ),
        (
            'a123de',
            'DL1',
            200,
            {
                'session_creation_fail_reason_code': 'DRIVER_NOT_FOUND',
                'session_creation_fail_reason_msg': (
                    'Driver not found in queue'
                ),
            },
        ),
        (
            'unknown_car',
            'DL1',
            200,
            {
                'session_creation_fail_reason_code': 'DRIVER_NOT_FOUND',
                'session_creation_fail_reason_msg': (
                    'Driver not found in queue'
                ),
            },
        ),
        (
            'a123bc',
            'UNKNOWN_POLYGON',
            404,
            {
                'code': 'POLYGON_NOT_FOUND',
                'message': 'Polygon UNKNOWN_POLYGON not found',
            },
        ),
        (
            'a123fg',
            'DL1',
            500,
            {
                'code': 'INTERNAL_ERROR',
                'message': 'Internal error. Try one more time, please',
            },
        ),
        (
            'a123jk',
            'DL1',
            500,
            {
                'code': 'INTERNAL_ERROR',
                'message': 'Internal error. Try one more time, please',
            },
        ),
    ],
)
@pytest.mark.pgsql('dispatch_airport', files=['drivers_queue.sql'])
async def test_relocate_start_negative(
        taxi_dispatch_airport, pgsql, car_number, poligon, status, result,
):
    resp = await taxi_dispatch_airport.post(
        '/v1/relocate/start',
        {'car_number': car_number, 'polygon_id': poligon},
        headers=common.DEFAULT_DISPATCH_AIRPORT_HEADER,
    )
    assert resp.status_code == status
    assert resp.json() == result

    db = pgsql['dispatch_airport']
    assert not utils.get_driver_events(db)
