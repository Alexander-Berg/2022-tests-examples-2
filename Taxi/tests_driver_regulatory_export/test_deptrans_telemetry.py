import datetime
import json

import pytest

_NOW = datetime.datetime(2021, 4, 15, 11, 12, 13, tzinfo=datetime.timezone.utc)
LOCAL_TIMEZONE = (
    datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
)


@pytest.fixture(autouse=True)
def mock_profiles_updates(mockserver):
    @mockserver.json_handler(
        '/deptrans-driver-status/internal/v3/profiles/updates',
    )
    def _mock_profiles_updates(request):
        cursor = request.args.get('cursor')
        if not cursor:
            data = [
                {
                    'license_pd_id': f'number{i}',
                    'status': 'approved',
                    'deptrans_pd_id': f'deptrans_pd_id_{i}',
                }
                for i in range(10)
            ]
            next_cursor = 'cursor_0'
        elif cursor == 'cursor_0':
            data = [
                {
                    'license_pd_id': 'number1',
                    'status': 'approved',
                    'deptrans_pd_id': 'deptrans_pd_id_99',
                },
            ]
            next_cursor = 'last_cursor'
        else:
            data = []
            next_cursor = 'last_cursor'

        return mockserver.make_response(
            status=200, json={'cursor': next_cursor, 'binding': data},
        )

    @mockserver.json_handler('/personal/v1/deptrans_ids/bulk_retrieve')
    def _mock_driver_deptrans_ids(request):
        body = json.loads(request.get_data())
        data = []
        for pd_id in body['items']:
            value = pd_id['id'].rsplit('_', 1)[1]
            data.append({'id': pd_id['id'], 'value': f'{value}01'})
        return mockserver.make_response(status=200, json={'items': data})


@pytest.mark.busy_drivers(
    busy_drivers=[
        {
            'driver_id': 'park_id_plus_uuid',
            'order_id': 'order_id_8',
            'taxi_status': 3,
            'final_destination': {
                'lat': 56.39818246923726,
                'lon': 61.92396961914058,
            },
        },
        {
            'driver_id': 'park_id_plus_uuid_1',
            'order_id': 'order_id_9',
            'taxi_status': 3,
            'destination': {
                'lat': 57.39818246923826,
                'lon': 62.92396961914158,
            },
            'final_destination': {
                'lat': 57.39818246923726,
                'lon': 62.92396961914058,
            },
        },
        {
            'driver_id': 'park_id_plus_uuid_2',
            'order_id': 'order_id_10',
            'taxi_status': 3,
            'destination': {'lat': 0.0, 'lon': 0.0},
        },
    ],
)
@pytest.mark.config(
    DEPTRANS_CLASSES_WITHOUT_PERMISSION={
        'business': ['vip', 'ultimate', 'maybach', 'premium_van'],
    },
    DRIVER_REGULATORY_MSK_CAR_NUMBER_EXPR='^.*?(77|99)$',
    DEPTRANS_MKAD_AREA=[
        [62.9234004, 57.3979478],
        [62.9247737, 57.3978437],
        [62.9244411, 57.3984102],
        [62.9236042, 57.3984102],
        [62.9233897, 57.3979536],
    ],
)
@pytest.mark.now(_NOW.isoformat())
async def test_service_based_distlocks(
        mockserver, testpoint, taxi_driver_regulatory_export, taxi_config,
):
    @testpoint('egts-service-send-testpoint')
    def egts_send_testpoint(arg):
        pass

    @testpoint('telemetry-yt-log-testpoint')
    def telemetry_yt_log_testpoint(arg):
        pass

    @mockserver.json_handler('/candidates/deptrans')
    def candidates_mock(request):
        return {
            'format': 'extended',
            'drivers': [
                {
                    'park_driver_id': 'park_id_plus_uuid',
                    'timestamp': 1562337615.0,
                    'geopoint': [37.445259, 55.651325],
                    'free': True,
                    'speed': -1,
                    'id': 'f670ca407abcb78d875860f2ce9360f2',
                    'direction': 326,
                    #  missing permit number for driver
                    'car_number': 'Х237УТ777',
                    'no_permission_classes': ['maybach'],
                },
                {
                    'park_driver_id': 'park_id_plus_uuid_1',
                    'timestamp': 1562337617.0,
                    'geopoint': [32.445259, 53.651325],
                    'free': True,
                    'speed': -1,
                    'id': 'f670ca407abcb78d875860f2ce9360f3',
                    'direction': 60,
                    #  missing permit number for driver
                    'car_number': 'Х237УТ42',  # not msk car number
                    'no_permission_classes': [],
                },
                {
                    'park_driver_id': 'park_id_plus_uuid_2',
                    'timestamp': 1562337618.0,
                    'geopoint': [37.485194, 55.616774],
                    'free': False,
                    'speed': 30,
                    'id': '803be6307530fa2dc6ee8c548bf4c00a',
                    'direction': 147,
                    'permit': '159750',
                    #  missing car_number for driver
                },
            ],
        }

    @mockserver.json_handler('/personal/v1/driver_licenses/bulk_retrieve')
    def mock_driver_license(request):
        body = json.loads(request.get_data())
        profiles = []
        for driver_id in body['items']:
            tmp = driver_id['id']
            profiles.append({'value': 'license_' + tmp, 'id': tmp})
        body = {'items': profiles}
        return mockserver.make_response(json.dumps(body), 200)

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def mock_driver_profiles(request):
        body = json.loads(request.get_data())
        profiles = []
        for driver_id in body['id_in_set']:
            license_pd_id = (
                'number1' if driver_id == 'park_id_plus_uuid' else 'unknown'
            )
            profiles.append(
                {
                    'park_driver_profile_id': driver_id,
                    'revision': '0',
                    'data': {
                        'park_id': '111',
                        'uuid': driver_id,
                        'hiring_details': {
                            'hiring_type': 'commercial',
                            'hiring_date': '1970-01-15T06:56:07.000',
                        },
                        'full_name': {
                            'first_name': 'Иван',
                            'middle_name': 'Иванович',
                            'last_name': 'Иванов',
                        },
                        'license': {'pd_id': license_pd_id, 'country': ''},
                        'phone_pd_ids': [{'pd_id': 'phone_pd_id_4'}],
                        'email_pd_ids': [],
                    },
                },
            )
        body = {'profiles': profiles}
        return mockserver.make_response(json.dumps(body), 200)

    config_value = taxi_config.get('DRIVER_REGULATORY_DEPTRANS_TELEMETRY')
    config_value['make_yt_logs'] = True
    taxi_config.set_values(
        {'DRIVER_REGULATORY_DEPTRANS_TELEMETRY': config_value},
    )

    async with taxi_driver_regulatory_export.spawn_task(
            'distlock/deptrans_telemetry',
    ):
        result = await egts_send_testpoint.wait_call()
        assert result['arg'] == [
            {
                'direction': 326.0,
                'free': True,
                'id': 746561726,
                'lat': 55.651325,
                'lon': 37.445259,
                'speed': 0.0,
                'timestamp': '2019-07-05T14:40:15+00:00',
                'kis_art_id': 9901,
            },
            {
                'direction': 60.0,
                'free': True,
                'id': 1534627880,
                'lat': 53.651325,
                'lon': 32.445259,
                'speed': 0.0,
                'timestamp': '2019-07-05T14:40:17+00:00',
                'kis_art_id': 0,
            },
            {
                'direction': 147.0,
                'free': False,
                'id': 3700669603,
                'lat': 55.616774,
                'lon': 37.485194,
                'speed': 30.0,
                'timestamp': '2019-07-05T14:40:18+00:00',
                'kis_art_id': 0,
            },
        ]

        candidates_request = candidates_mock.next_call()['request'].json
        assert candidates_request == {
            'deptrans': {
                'classes_without_permission': [
                    'vip',
                    'ultimate',
                    'maybach',
                    'premium_van',
                ],
            },
            'format': 'extended',
        }

        assert mock_driver_profiles.has_calls
        assert mock_driver_license.has_calls
        yt_testpoint_arg = await telemetry_yt_log_testpoint.wait_call()
        assert yt_testpoint_arg['arg'] == [
            {
                'car_number': 'Х237УТ777',
                'is_msk_car_number': True,
                'direction': 326.0,
                'free': True,
                'id': (
                    'dfe10ceb8a402ea518d8e89126044a1e'
                    '8a30c1d4db37d5941fcdb7dd3c2dd166'
                ),
                'lat': 55.651325,
                'license_number': '',
                'lon': 37.445259,
                'position_timestamp': '2019-07-05T17:40:15+03:00',
                'speed': 0.0,
                'timestamp': _NOW.astimezone(LOCAL_TIMEZONE).isoformat(),
                'kis_art_id': 9901,
                'park_driver_id': 'park_id_plus_uuid',
                'deptrans_status': 'approved',
                'is_order_final_point_b_in_msk': False,
                'order_final_point_b_lat': 56.39818246923726,
                'order_final_point_b_lon': 61.92396961914058,
                'no_permission_classes': ['maybach'],
            },
            {
                'car_number': 'Х237УТ42',
                'is_msk_car_number': False,
                'direction': 60.0,
                'free': True,
                'id': (
                    '80829fa2ca22493810faeb764d6af9af'
                    'b91443e63de01b5beb06febe481c808b'
                ),
                'lat': 53.651325,
                'license_number': '',
                'lon': 32.445259,
                'position_timestamp': '2019-07-05T17:40:17+03:00',
                'speed': 0.0,
                'timestamp': _NOW.astimezone(LOCAL_TIMEZONE).isoformat(),
                'kis_art_id': 0,
                'park_driver_id': 'park_id_plus_uuid_1',
                'is_order_next_point_b_in_msk': True,
                'order_next_point_b_lat': 57.39818246923826,
                'order_next_point_b_lon': 62.92396961914158,
                'is_order_final_point_b_in_msk': True,
                'order_final_point_b_lat': 57.39818246923726,
                'order_final_point_b_lon': 62.92396961914058,
                'no_permission_classes': [],
            },
            {
                'car_number': '',
                'direction': 147.0,
                'free': False,
                'id': (
                    '80829fa2ca22493810faeb764d6af9af'
                    'b91443e63de01b5beb06febe481c808b'
                ),
                'lat': 55.616774,
                'license_number': '159750',
                'lon': 37.485194,
                'position_timestamp': '2019-07-05T17:40:18+03:00',
                'speed': 30.0,
                'timestamp': _NOW.astimezone(LOCAL_TIMEZONE).isoformat(),
                'kis_art_id': 0,
                'park_driver_id': 'park_id_plus_uuid_2',
                'no_permission_classes': [],
            },
        ]
