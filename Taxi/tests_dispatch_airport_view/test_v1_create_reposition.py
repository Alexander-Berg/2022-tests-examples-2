import json

import pytest

import tests_dispatch_airport_view.utils as utils

URL = '/driver/v1/dispatch-airport-view/v1/create_reposition'

DRIVER_META = {
    'dbid_uuid1': {'updated_ts': '1001', 'geobus_ts': '1001'},
    'dbid_uuid3': {'updated_ts': '1003', 'geobus_ts': '1003'},
    'dbid_uuid4': {'updated_ts': '1004', 'geobus_ts': '1004'},
    'dbid_uuid5': {'updated_ts': '1005', 'geobus_ts': '1005'},
    'dbid_uuid6': {'updated_ts': '1006', 'geobus_ts': '1006'},
    'dbid_uuid7': {'updated_ts': '1007', 'geobus_ts': '1007'},
    'dbid_uuid8': {
        'updated_ts': '1008',
        'geobus_ts': '1008',
        'is_hidden': 'false',
    },
    'dbid_uuid9': {
        'updated_ts': '1009',
        'geobus_ts': '1009',
        'is_hidden': 'true',
    },
}


def _make_headers(uuid):
    return {
        **utils.HEADERS,
        'X-YaTaxi-Park-Id': 'dbid',
        'X-YaTaxi-Driver-Profile-Id': uuid,
    }


@pytest.mark.redis_store(
    # driver hashes
    [
        'hmset',
        utils.driver_info_key('dbid_uuid1'),
        {
            **DRIVER_META['dbid_uuid1'],
            'pins': json.dumps(
                [
                    utils.ekb_pin_point(
                        True,
                        3660,
                        {'econom': 900, 'comfortplus': 300, 'vip': 1200},
                    ),
                ],
            ),
        },
    ],
    [
        'hmset',
        utils.driver_info_key('dbid_uuid3'),
        {
            **DRIVER_META['dbid_uuid3'],
            'pins': json.dumps(
                [
                    utils.ekb_pin_point(
                        False,
                        3660,
                        {'econom': 900, 'comfortplus': 300, 'vip': 1200},
                        last_allowed={
                            'time': '2021-12-12T09:09:00+00:00',
                            'state': 0,
                        },
                    ),
                ],
            ),
        },
    ],
    [
        'hmset',
        utils.driver_info_key('dbid_uuid4'),
        {
            **DRIVER_META['dbid_uuid4'],
            'pins': json.dumps(
                [
                    {
                        'airport_id': 'ekb',
                        'pin_point': utils.AIRPORT_EKB_POSITION,
                        'state': int(utils.PinState.kAllowedOldMode),
                        'class_wait_times': {
                            'econom': 900,
                            'comfortplus': 300,
                            'vip': 1200,
                        },
                    },
                ],
            ),
        },
    ],
    [
        'hmset',
        utils.driver_info_key('dbid_uuid5'),
        {
            **DRIVER_META['dbid_uuid5'],
            'pins': json.dumps(
                [
                    {
                        'airport_id': 'ekb',
                        'pin_point': utils.AIRPORT_EKB_POSITION,
                        'state': int(utils.PinState.kNotAllowed),
                        'class_wait_times': {
                            'econom': 900,
                            'comfortplus': 300,
                            'vip': 1200,
                        },
                        'last_allowed': {
                            'time': '2021-12-12T09:09:00+00:00',
                            'state': 1,
                        },
                    },
                ],
            ),
        },
    ],
)
@pytest.mark.now('2021-12-12T09:09:09.000Z')
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.config(DISPATCH_AIRPORT_VIEW_ALLOW_PIN_REPOSITION=True)
@pytest.mark.config(DISPATCH_AIRPORT_VIEW_PIN_REPOSITION_AVAILABLE_TTL=10)
async def test_create_reposition_success(
        taxi_dispatch_airport_view, mockserver, testpoint, taxi_config, mode,
):
    @mockserver.json_handler('/reposition-api/v1/service/make_offer')
    def _mock_reposition_api_make_offer(request):
        helper = utils.MakeOfferFbHelper()
        parsed_request = helper.parse_request(request.get_data())
        driver_id = parsed_request[0]['driver_id']
        if driver_id in ['uuid4', 'uuid5']:
            assert (
                parsed_request[0]['metadata']['is_dispatch_airport_pin']
                is True
            )
        else:
            assert (
                parsed_request[0]['metadata']['is_dispatch_airport_pin']
                is False
            )
        return mockserver.make_response(
            response=helper.build_response(
                [
                    {
                        'park_db_id': 'dbid',
                        'driver_id': driver_id,
                        'point_id': 'reposition_id' + driver_id,
                    },
                ],
            ),
            content_type='application/x-flatbuffers',
        )

    @testpoint('account_class_in_reposition')
    def account_class_in_reposition(class_name):
        return class_name

    # uuid1 - available pin allowed_all
    # uuid3 - unavailable pin, but was recently available
    # udid4 - available pin allowed_old_mode
    # uuid5 - unavailable pin, but was recently available old_mode

    for uuid in ['uuid1', 'uuid3', 'uuid4', 'uuid5']:
        actual_response = await taxi_dispatch_airport_view.post(
            URL, {'airport': 'ekb'}, headers=_make_headers(uuid),
        )
        # no classes remain
        if mode == 'new' and uuid in ['uuid4', 'uuid5']:
            assert actual_response.status_code == 409
            continue

        assert actual_response.status_code == 200
        assert actual_response.json()['point_id'] == 'reposition_id' + uuid

        class_names = sorted(
            [
                account_class_in_reposition.next_call()['class_name']
                for _ in range(account_class_in_reposition.times_called)
            ],
        )
        if uuid in ['uuid1', 'uuid3'] or mode in ['old', 'new']:
            assert class_names == ['comfortplus', 'econom', 'vip']
        elif mode == 'mixed_base_old':
            assert class_names == ['econom', 'vip']
        else:
            assert class_names == ['econom']


@pytest.mark.redis_store(
    # driver hashes
    [
        'hmset',
        utils.driver_info_key('dbid_uuid1'),
        {
            **DRIVER_META['dbid_uuid1'],
            'pins': json.dumps(
                [
                    utils.ekb_pin_point(
                        True,
                        3660,
                        {'econom': 900, 'comfortplus': 300, 'vip': 1200},
                    ),
                ],
            ),
        },
    ],
)
@pytest.mark.now('2021-12-12T09:00:00.000Z')
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.config(DISPATCH_AIRPORT_VIEW_ALLOW_PIN_REPOSITION=True)
@pytest.mark.config(DISPATCH_AIRPORT_VIEW_PIN_REPOSITION_AVAILABLE_TTL=10)
@pytest.mark.config(
    DISPATCH_AIRPORT_VIEW_REPOSITION_PUSH_SETTINGS={'delays': [1, 2, 3]},
)
async def test_create_reposition_notifications(
        taxi_dispatch_airport_view, mockserver, testpoint, mocked_time,
):
    @testpoint('send_push')
    def send_push(push):
        return push

    @mockserver.json_handler('/reposition-api/v1/service/make_offer')
    def _mock_reposition_api_make_offer(request):
        helper = utils.MakeOfferFbHelper()
        parsed_request = helper.parse_request(request.get_data())
        driver_id = parsed_request[0]['driver_id']
        return mockserver.make_response(
            response=helper.build_response(
                [
                    {
                        'park_db_id': 'dbid',
                        'driver_id': driver_id,
                        'point_id': 'reposition_id',
                    },
                ],
            ),
            content_type='application/x-flatbuffers',
        )

    uuid = 'uuid1'
    actual_response = await taxi_dispatch_airport_view.post(
        URL, {'airport': 'ekb'}, headers=_make_headers(uuid),
    )

    assert actual_response.status_code == 200

    for i in range(1, 4):
        push = (await send_push.wait_call())['push']
        assert push['idempotency_token'] == 'dbid_uuid1' + str(i)
        assert push['body'] == {
            'intent': 'ForcePollingOrder',
            'service': 'taximeter',
            'client_id': 'dbid-uuid1',
            'ttl': 5,
            'data': {'code': 1600},
        }


@pytest.mark.redis_store(
    # driver hashes
    [
        'hmset',
        utils.driver_info_key('dbid_uuid1'),
        {
            **DRIVER_META['dbid_uuid1'],
            'pins': json.dumps(
                [utils.ekb_pin_point(True, 3660, {'econom': 3660})],
            ),
        },
    ],
    [
        'hmset',
        utils.driver_info_key('dbid_uuid3'),
        {
            **DRIVER_META['dbid_uuid3'],
            'pins': json.dumps(
                [utils.kamenskuralsky_pin_point(True, 3660, {'econom': 3660})],
            ),
        },
    ],
    [
        'hmset',
        utils.driver_info_key('dbid_uuid4'),
        {
            **DRIVER_META['dbid_uuid4'],
            'pins': json.dumps(
                [utils.ekb_pin_point(True, 3660, {'econom': 3660})],
            ),
        },
    ],
    [
        'hmset',
        utils.driver_info_key('dbid_uuid5'),
        {
            **DRIVER_META['dbid_uuid5'],
            'pins': json.dumps(
                [utils.ekb_pin_point(True, 3660, {'econom': 3660})],
            ),
        },
    ],
    [
        'hmset',
        utils.driver_info_key('dbid_uuid6'),
        {
            **DRIVER_META['dbid_uuid6'],
            'pins': json.dumps(
                [utils.ekb_pin_point(False, 3660, {'econom': 3660})],
            ),
        },
    ],
    [
        'hmset',
        utils.driver_info_key('dbid_uuid7'),
        {
            **DRIVER_META['dbid_uuid7'],
            'pins': json.dumps(
                [
                    utils.ekb_pin_point(
                        True,
                        3660,
                        {'econom': 900, 'comfortplus': 300, 'vip': 1200},
                    ),
                ],
            ),
        },
    ],
    [
        'hmset',
        utils.driver_info_key('dbid_uuid8'),
        {
            **DRIVER_META['dbid_uuid8'],
            'pins': json.dumps(
                [
                    utils.ekb_pin_point(
                        False,
                        3660,
                        {'econom': 900, 'comfortplus': 300, 'vip': 1200},
                        last_allowed={
                            'time': '2021-12-12T09:08:58+00:00',
                            'state': 0,
                        },
                    ),
                ],
            ),
        },
    ],
    [
        'hmset',
        utils.driver_info_key('dbid_uuid9'),
        {**DRIVER_META['dbid_uuid9'], 'pins': json.dumps([])},
    ],
)
@pytest.mark.busy_drivers(
    busy_drivers=[
        {
            'driver_id': 'dbid_uuid4',
            'order_id': 'order_id_4',
            'taxi_status': 3,
            'final_destination': {
                'lat': utils.NOTIFICATION_EKB_POSITION[1],
                'lon': utils.NOTIFICATION_EKB_POSITION[0],
            },
        },
    ],
)
@pytest.mark.config(DISPATCH_AIRPORT_VIEW_PIN_REPOSITION_AVAILABLE_TTL=10)
@pytest.mark.now('2021-12-12T09:09:09.000')
@pytest.mark.geoareas(filename='geoareas.json')
async def test_create_reposition_failure(
        taxi_dispatch_airport_view, mockserver, taxi_config,
):
    @mockserver.json_handler('/reposition-api/v1/service/make_offer')
    def _mock_reposition_api_make_offer(request):
        helper = utils.MakeOfferFbHelper()
        parsed_request = helper.parse_request(request.get_data())
        return mockserver.make_response(
            response=helper.build_response(
                [
                    {
                        'park_db_id': 'dbid',
                        'driver_id': parsed_request[0]['driver_id'],
                        'point_id': '',
                    },
                ],
            ),
            content_type='application/x-flatbuffers',
        )

    # dbid_uuid1 - airport not found
    # dbid_uuid2 - driver not found in cache
    # dbid_uuid3 - pin not found in driver_pins
    # dbid_uuid4 - busy driver
    # dbid_uuid5 - reposition /v1/service/make_offer create offer error
    # dbid_uuid6 - pin is unavailable
    # dbid_uuid7 - pin is forbidden by config
    # dbid_uuid8 - pin was available 11 seconds ago, but
    # reposition_available_ttl is only 10 seconds
    # dbid_uuid9 - pin is hidden

    etalons = {
        'uuid1': {
            'status_code': 404,
            'response': {
                'code': 'AIRPORT_NOT_FOUND',
                'message': 'Pin is not available',
            },
        },
        'uuid2': {
            'status_code': 404,
            'response': {
                'code': 'DRIVER_NOT_FOUND',
                'message': 'Pin is not available',
            },
        },
        'uuid3': {
            'status_code': 404,
            'response': {
                'code': 'PIN_NOT_FOUND',
                'message': 'Pin is not available',
            },
        },
        'uuid4': {
            'status_code': 404,
            'response': {
                'code': 'BUSY_DRIVER',
                'message': 'Pin is not available',
            },
        },
        'uuid5': {
            'status_code': 500,
            'response': {
                'code': 'CREATE_OFFER_ERROR',
                'message': 'Pin is not available',
            },
        },
        'uuid6': {
            'status_code': 409,
            'response': {
                'code': 'PIN_UNAVAILABLE',
                'message': 'Pin is not available',
            },
        },
        'uuid7': {
            'status_code': 400,
            'response': {
                'code': 'PIN_FORBIDDEN',
                'message': 'Pin is not available',
            },
        },
        'uuid8': {
            'status_code': 409,
            'response': {
                'code': 'PIN_UNAVAILABLE',
                'message': 'Pin is not available',
            },
        },
        'uuid9': {
            'status_code': 404,
            'response': {
                'code': 'WRONG_PROVIDER',
                'message': 'Pin is not available',
            },
        },
    }
    for uuid, etalon_response in etalons.items():
        taxi_config.set_values(
            {'DISPATCH_AIRPORT_VIEW_ALLOW_PIN_REPOSITION': (uuid != 'uuid7')},
        )
        await taxi_dispatch_airport_view.invalidate_caches()

        actual_response = await taxi_dispatch_airport_view.post(
            URL,
            {'airport': 'krasnodar' if uuid == 'uuid1' else 'ekb'},
            headers=_make_headers(uuid),
        )
        print('uuid = ', uuid)
        assert actual_response.status_code == etalon_response['status_code']
        assert actual_response.json() == etalon_response['response']
