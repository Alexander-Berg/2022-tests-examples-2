import datetime
import json

import pytest
import pytz

_NOW = datetime.datetime(
    2021, 4, 15, 11, 12, 13, tzinfo=pytz.timezone('Europe/Moscow'),
)
_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S+03:00'


@pytest.mark.config(
    DRIVER_REGULATORY_KAZAN_TELEMETRY={
        'allowed_classes': [
            'econom',
            'comfort',
            'comfortplus',
            'business',
            'child_tariff',
            'uberx',
            'uberselect',
            'uberkids',
        ],
        'bottom_right': [31.019161, 59.535121],
        'make_yt_logs': False,
        'send_interval_ms': 40000,
        'telemetry_enabled': True,
        'kazan_send_settings': {
            'batch_size': 100,
            'enabled': True,
            'dry_run': True,
            'endpoint': '',
            'retries': 1,
            'timeout': 1000,
        },
        'top_left': [29.325238, 60.270897],
    },
)
@pytest.mark.now(_NOW.strftime(_TIME_FORMAT))
async def test_kazan_telemetry(
        mockserver, testpoint, taxi_driver_regulatory_export, load_json,
):
    @testpoint('rnis-kazan-send-testpoint')
    def rnis_kazan_send_testpoint(arg):
        pass

    @mockserver.json_handler('/candidates/list-profiles')
    def _list_profiles(request):
        return {
            'drivers': [
                {
                    'position': [10.001, 10.001],
                    'id': 'dbid0_uuid0',
                    'dbid': 'dbid0',
                    'uuid': 'uuid0',
                    'status': {
                        'status': 'busy',
                        'orders': [],
                        'driver': 'verybusy',
                        'taximeter': 'busy',
                    },
                    'car_number': 'Х496НК77',  # has permission in Spb
                    'position_info': {
                        'timestamp': '2021-01-01T13:37:00+00:00',
                    },
                },
                {
                    'position': [10.001, 10.001],
                    'id': 'dbid1_uuid1',
                    'dbid': 'dbid1',
                    'uuid': 'uuid1',
                    'status': {
                        'status': 'busy',
                        'orders': [],
                        'driver': 'verybusy',
                        'taximeter': 'busy',
                    },
                    'car_number': 'T000QC',  # from Moscow
                    'position_info': {
                        'timestamp': '2021-01-01T13:37:00+00:00',
                    },
                },
                {
                    'position': [10.001, 10.001],
                    'id': 'dbid2_uuid2',
                    'dbid': 'dbid2',
                    'uuid': 'uuid2',
                    'status': {
                        'status': 'busy',
                        'orders': [],
                        'driver': 'verybusy',
                        'taximeter': 'busy',
                    },
                    'car_number': 'A000AA',  # no permission
                    'position_info': {
                        'timestamp': '2021-01-01T13:37:00+00:00',
                    },
                },
            ],
        }

    @mockserver.json_handler('/personal/v1/driver_licenses/bulk_retrieve')
    def _mock_driver_license(request):
        body = json.loads(request.get_data())
        profiles = []
        for driver_id in body['items']:
            tmp = driver_id['id']
            profiles.append({'value': 'license_' + tmp, 'id': tmp})
        body = {'items': profiles}
        return mockserver.make_response(json.dumps(body), 200)

    @mockserver.json_handler(
        '/deptrans-driver-status/internal/v3/profiles/updates',
    )
    def _mock_profiles_updates(request):
        return mockserver.make_response(
            status=200, json={'cursor': 'something', 'binding': []},
        )

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _mock_driver_profiles(request):
        body = json.loads(request.get_data())
        profiles = []
        for driver_id in body['id_in_set']:
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
                        'license': {'pd_id': 'number1', 'country': ''},
                        'phone_pd_ids': [{'pd_id': 'phone_pd_id_4'}],
                        'email_pd_ids': [],
                    },
                },
            )
        body = {'profiles': profiles}
        return mockserver.make_response(json.dumps(body), 200)

    async with taxi_driver_regulatory_export.spawn_task(
            'distlock/kazan_telemetry',
    ):
        expected = load_json('expected_rnis_request_body.json')
        result = (await rnis_kazan_send_testpoint.wait_call())['arg']
        assert expected == result
