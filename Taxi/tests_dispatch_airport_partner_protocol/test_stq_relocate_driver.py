# pylint: disable=import-error
import datetime

import pytest
from reposition_api.fbs.v1.service.make_offer.Origin import Origin

import tests_dispatch_airport_partner_protocol.utils as utils

ORDER_ID = 'order_id1'

PERFORMER_UNIQUE_DRIVER_ID = 'udid1'
HASHED_PERFORMER_UNIQUE_DRIVER_ID = (
    '0cddbf5490863b24960f31c04f00c9ccec98a4dee416b88d82a8da414ca21855'
)

NOW = '2021-06-01T11:59:00Z'

CAR_NUMBER_LATIN = 'Y884OE750'
CAR_NUMBER_CYRILLIC = 'У884ОЕ750'

CAR_INFO = {
    'number': CAR_NUMBER_CYRILLIC,
    'model': 'LegacyOne',
    'mark': 'brand1',
    'color': 'black1',
    'year': 2001,
}

LOCAL_TIMEZONE = (
    datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
)


def check_auth_header(request):
    assert (
        request.headers['Authorization']
        == 'Basic c29tZV9sb2dpbjpzb21lX3Bhc3N3b3Jk'
    )


def fleet_vehicles_handler(mockserver, request, fleet_vehicles_successful):
    if not fleet_vehicles_successful:
        return mockserver.make_response(json={}, status=500)

    body = request.json
    assert body['id_in_set'] == ['dbid1_car_id1']
    assert body['projection'] == [
        'data.number',
        'data.year',
        'data.model',
        'data.brand',
        'data.color',
    ]
    json = {
        'vehicles': [
            {
                'data': {
                    'brand': CAR_INFO['mark'],
                    'color': CAR_INFO['color'],
                    'model': CAR_INFO['model'],
                    'number': CAR_NUMBER_LATIN,
                    'year': CAR_INFO['year'],
                },
                'park_id_car_id': 'dbid1_car_id1',
                'revision': '0_1574328384_71',
            },
        ],
    }
    return mockserver.make_response(json=json, status=200)


def make_offer_handler(mockserver, request, make_offer_successful):
    helper = utils.MakeOfferFbHelper()
    expected_request = [
        {
            'address': '',
            'auto_accept': True,
            'city': '',
            'completed_tags': [],
            'description': 'Проследуйте на дефолтную парковку',
            'driver_id': 'uuid1',
            'finish_until': (
                datetime.datetime(
                    2021,
                    6,
                    1,
                    15,
                    14,
                    0,
                    tzinfo=datetime.timezone(datetime.timedelta(hours=3)),
                )
                .astimezone(LOCAL_TIMEZONE)
                .replace(tzinfo=None)
            ),
            'image_id': 'icon',
            'mode_name': 'Sintegro',
            'name': '',
            'origin': Origin.kDispatchAirportPartnerProtocol,
            'park_db_id': 'dbid1',
            'start_until': (
                datetime.datetime(
                    2021,
                    6,
                    1,
                    14,
                    59,
                    30,
                    tzinfo=datetime.timezone(datetime.timedelta(hours=3)),
                )
                .astimezone(LOCAL_TIMEZONE)
                .replace(tzinfo=None)
            ),
            'tags': [],
            'tariff_class': '',
            'metadata': {'airport_queue_id': 'svo_p22'},
            'restrictions': [],
            'draft_id': 'dispatch-airport-partner-protocol/some_session',
        },
    ]
    response_data = [
        {
            'park_db_id': 'dbid1',
            'driver_id': 'uuid1',
            'point_id': 'reposition_id' if make_offer_successful else '',
        },
    ]
    assert helper.parse_request(request.get_data()) == expected_request
    return mockserver.make_response(
        response=helper.build_response(response_data),
        content_type='application/x-flatbuffers',
    )


def info_reposition_out_handler(
        mockserver, request, reposition_out_successful,
):
    if not reposition_out_successful:
        return mockserver.make_response(json={}, status=500)

    check_auth_header(request)
    body = request.json
    assert body == {
        'polygon_id': 'svo_p22',
        'driver_id': HASHED_PERFORMER_UNIQUE_DRIVER_ID,
        'car': CAR_INFO,
        'reposition_id': 'rep:dbid1_uuid1_reposition_id',
        'arrival_time': '2021-06-01T12:04:00Z',
        'reposition_class': 'econom',
    }
    json = {'status_permission': True, 'status_message': 'success'}
    return mockserver.make_response(json=json, status=200)


@pytest.mark.now(NOW)
@pytest.mark.config(
    DISPATCH_AIRPORT_PARTNER_PROTOCOL_RELOCATE_DRIVER_SETTINGS={
        'max_attempts': 3,
        'enabled': True,
        'send_offer_enabled': True,
        'send_reposition_out_to_sintegro_enabled': True,
    },
    SVO_POLYGON_NAMES={
        'svo_p22': {
            'full_text': 'repo to svo p22',
            'point': [37.392038, 55.978465],
            'target_airport_id': 'svo_p22',
        },
    },
    FLEET_VEHICLES_CLIENT_QOS={
        '__default__': {'attempts': 1, 'timeout-ms': 200},
    },
    REPOSITION_API_CLIENT_QOS={
        '__default__': {'attempts': 1, 'timeout-ms': 200},
    },
    DISPATCH_AIRPORT_REPOSITION_PUSH_SETTINGS={'delays': [1]},
)
@pytest.mark.parametrize('fleet_vehicles_successful', [True, False])
@pytest.mark.parametrize('make_offer_successful', [True, False])
@pytest.mark.parametrize('reposition_out_successful', [True, False])
@pytest.mark.geoareas(filename='geoareas.json')
async def test_happy_path(
        mockserver,
        taxi_dispatch_airport_partner_protocol,
        stq_runner,
        fleet_vehicles_successful,
        make_offer_successful,
        reposition_out_successful,
):
    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/cache-retrieve')
    def mock_fleet_vehicles(request):
        return fleet_vehicles_handler(
            mockserver, request, fleet_vehicles_successful,
        )

    @mockserver.json_handler('sintegro/aes/hs/info_reposition_out')
    def mock_info_reposition_out(request):
        return info_reposition_out_handler(
            mockserver, request, reposition_out_successful,
        )

    @mockserver.json_handler('/reposition-api/v1/service/make_offer')
    def mock_reposition_api_make_offer(request):
        return make_offer_handler(mockserver, request, make_offer_successful)

    @mockserver.json_handler('/client-notify/v2/push')
    def client_notify_push(request):
        return {'notification_id': ''}

    await taxi_dispatch_airport_partner_protocol.enable_testpoints()
    stq_caller = stq_runner.dispatch_airport_partner_protocol_relocate_driver

    kwargs = {
        'dbid': 'dbid1',
        'uuid': 'uuid1',
        'udid': PERFORMER_UNIQUE_DRIVER_ID,
        'car_id': 'car_id1',
        'target_polygon_id': 'svo_p22',
        'target_class': 'econom',
        'app_locale': 'ru',
        'session_id': 'some_session',
    }

    stq_success = (
        fleet_vehicles_successful
        and make_offer_successful
        and reposition_out_successful
    )

    await stq_caller.call(
        task_id='task_id1', kwargs=kwargs, expect_fail=not stq_success,
    )

    assert mock_fleet_vehicles.times_called == 1
    assert mock_reposition_api_make_offer.times_called == (
        1 if fleet_vehicles_successful else 0
    )

    if make_offer_successful and fleet_vehicles_successful:
        assert mock_info_reposition_out.times_called == 1
        await client_notify_push.wait_call()
    else:
        assert mock_info_reposition_out.times_called == 0
        assert client_notify_push.times_called == 0


@pytest.mark.config(
    DISPATCH_AIRPORT_PARTNER_PROTOCOL_RELOCATE_DRIVER_SETTINGS={
        'max_attempts': 3,
        'enabled': True,
    },
)
@pytest.mark.geoareas(filename='geoareas.json')
async def test_stq_relocate_driver_max_attempts(
        taxi_dispatch_airport_partner_protocol, stq_runner, testpoint,
):
    @testpoint('dispatch_airport_partner_protocol_relocate_driver')
    def testpoint_call(_):
        return {'inject_error': True}

    await taxi_dispatch_airport_partner_protocol.enable_testpoints()
    stq = stq_runner.dispatch_airport_partner_protocol_relocate_driver

    kwargs = {
        'dbid': 'dbid1',
        'uuid': 'uuid1',
        'udid': PERFORMER_UNIQUE_DRIVER_ID,
        'car_id': 'car_id1',
        'target_polygon_id': 'svo_p22',
        'target_class': 'econom',
        'app_locale': 'ru',
        'session_id': 'some_session',
    }

    await stq.call(task_id='task_id1', kwargs=kwargs, expect_fail=True)
    await stq.call(
        task_id='task_id1', kwargs=kwargs, expect_fail=False, exec_tries=3,
    )

    assert testpoint_call.times_called == 2
