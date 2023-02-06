import datetime
import json

import pytest
import pytz


def timestamp_to_datetime(timestamp):
    splitted = timestamp.split('_')
    dt_by_timestamp = datetime.datetime.fromtimestamp(
        int(splitted[0]), pytz.utc,
    )
    return dt_by_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')


# May cause lots of flaps TODO: fix it TAXIACCESSDATA-389
@pytest.mark.config(
    HIRING_ZD_PUSH_WORKER_SETTINGS={
        'create-tickets-min-time': 30,
        'enable-create-tickets': True,
        'pushed-documents-ttl': 120,
        'work-interval-ms': 5,
    },
    TVM_ENABLED=False,
    HIRING_ZD_PUSH_ENABLE=True,
    HIRING_ZD_PUSH_ENABLE_HIRING_API=True,
    HIRING_ZD_PUSH_ENABLE_INFRANAIM_API=True,
)
@pytest.mark.now('2019-01-01T00:00:00+0000')
@pytest.mark.experiments3(filename='exp.json')
async def test_hiring_zd_push_worker(
        taxi_hiring_zd_push, testpoint, mockserver, load_json, pgsql,
):
    @mockserver.json_handler('/infranaim/api/v1/submit/taxi_selfreg')
    def _infranaim(request):
        expected_requests = load_json('expected_infranaim_request.json')
        profile_id = (
            request.json['params']['park']
            + '_'
            + request.json['params']['driver_uuid']
        )
        assert request.json == expected_requests[profile_id]
        return {'code': 200, 'message': 'ok', 'details': 'no details'}

    @mockserver.json_handler('/hiring-api/v1/tickets/create')
    def _hiring_api(request):
        expected_requests = load_json('expected_hiring_api_request.json')
        params = {
            item['name']: item['value'] for item in request.json['fields']
        }
        profile_id = '{}_{}'.format(params['park'], params['driver_uuid'])
        assert params == expected_requests[profile_id]['params']
        return {
            'code': 'SUCCESS',
            'message': 'ok',
            'details': {'accepted_fields': ['id']},
        }

    # TODO: need to replace this mock by generated TAXIPLATFORM-1396
    @mockserver.json_handler('/parks-commute/v1/parks/retrieve_by_park_id')
    def _parks_commute_retrieve(request):
        return {
            'parks': [
                {
                    'revision': '0_1546300750_1',
                    'park_id': 'park1',
                    'data': {'clid': 'clid1', 'city': 'Moscow'},
                },
                {
                    'revision': '0_1546300750_2',
                    'park_id': 'park2',
                    'data': {'clid': 'clid1', 'city': 'Moscow'},
                },
                {
                    'revision': '0_1546300750_3',
                    'park_id': 'park3',
                    'data': {'clid': 'clid1', 'city': 'Moscow'},
                },
            ],
        }

    # TODO: need to replace this mock by generated TAXIPLATFORM-1396
    @mockserver.json_handler(
        '/driver-profiles/v1/vehicle_bindings/cars/retrieve_by_driver_id',
    )
    def _driver_profiles_retrieve(request):
        return {
            'profiles': [
                {
                    'revision': '0_1546300750_1',
                    'park_driver_profile_id': 'park1_driver1',
                    'data': {'car_id': 'car'},
                },
                {
                    'revision': '0_1546300750_2',
                    'park_driver_profile_id': 'park2_driver2',
                    'data': {'car_id': 'car'},
                },
                {
                    'revision': '0_1546300750_3',
                    'park_driver_profile_id': 'park2_driver3',
                    'data': {'car_id': 'car'},
                },
            ],
        }

    # TODO: need to replace this mock by generated TAXIPLATFORM-1396
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/updates')
    def _driver_profiles_updates(request):
        items = [
            {
                'revision': '0_1546300750_1',
                'park_driver_profile_id': 'park1_driver1',
                'data': {
                    'park_id': 'park1',
                    'uuid': 'driver1',
                    'full_name': {
                        'first_name': 'Дмий',
                        'middle_name': 'Сервич',
                        'last_name': 'Боркий',
                    },
                    'phone_pd_ids': [{'pd_id': 'phone_pd_id_1'}],
                    'created_date': datetime.datetime.now().strftime(
                        '%Y-%m-%dT%H:%M:%S',
                    ),
                    'license_issue_date': '2019-01-01T00:00:10.000',
                    'license_expire_date': '2019-01-01T00:00:10.000',
                    'hiring_source': 'yandex',
                    'license': {'pd_id': 'license_pd_id1'},
                    'hiring_details': {'hiring_type': 'selfreg'},
                    'email_pd_ids': [],
                },
            },
            {
                'revision': '0_1546300750_2',
                'park_driver_profile_id': 'park2_driver2',
                'data': {
                    'park_id': 'park2',
                    'uuid': 'driver2',
                    'full_name': {
                        'first_name': 'Анатой',
                        'middle_name': 'Аольевич',
                        'last_name': 'Зов',
                    },
                    'phone_pd_ids': [{'pd_id': 'phone_pd_id_2'}],
                    'created_date': datetime.datetime.now().strftime(
                        '%Y-%m-%dT%H:%M:%S',
                    ),
                    'license_issue_date': '2019-01-01T00:00:10.000',
                    'license_expire_date': '2019-01-01T00:00:10.000',
                    'hiring_source': 'yandex',
                    'license': {'pd_id': 'license_pd_id2'},
                    'hiring_details': {'hiring_type': 'selfreg'},
                    'email_pd_ids': [],
                },
            },
            {
                'revision': '0_1546300750_3',
                'park_driver_profile_id': 'park2_driver3',
                'data': {
                    'park_id': 'park2',
                    'uuid': 'driver3',
                    'full_name': {
                        'first_name': 'Анатой2',
                        'middle_name': 'Аольевич2',
                        'last_name': 'Зов2',
                    },
                    'phone_pd_ids': [{'pd_id': 'phone_pd_id_3'}],
                    'created_date': datetime.datetime.now().strftime(
                        '%Y-%m-%dT%H:%M:%S',
                    ),
                    'license_issue_date': '2019-01-01T00:00:10.000',
                    'license_expire_date': '2019-01-01T00:00:10.000',
                    'hiring_source': 'yandex',
                    'license': {'pd_id': 'license_pd_id3'},
                    'hiring_details': {'hiring_type': 'selfreg'},
                    'email_pd_ids': [],
                },
            },
            {
                # driver without created_date
                'revision': '0_1546300750_4',
                'park_driver_profile_id': 'park4_driver4',
                'data': {'park_id': 'park4', 'uuid': 'driver4'},
            },
        ]
        response_json = {
            'last_modified': timestamp_to_datetime(items[-1]['revision']),
            'last_revision': items[-1]['revision'],
            'profiles': items,
        }
        return mockserver.make_response(
            json.dumps(response_json),
            200,
            headers={'X-Polling-Delay-Ms': '100'},
        )

    @mockserver.json_handler('/personal/v1/driver_licenses/bulk_retrieve')
    def _retrieve_licenses(request):
        assert request.json['items'] == [
            {'id': 'license_pd_id1'},
            {'id': 'license_pd_id2'},
            {'id': 'license_pd_id3'},
        ]
        return {
            'items': [
                {'id': 'license_pd_id1', 'value': 'license1'},
                {'id': 'license_pd_id2', 'value': 'license2'},
                {'id': 'license_pd_id3', 'value': 'license3'},
            ],
        }

    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    def _retrieve_phones(request):
        assert request.json['items'] == [
            {'id': 'phone_pd_id_1'},
            {'id': 'phone_pd_id_2'},
            {'id': 'phone_pd_id_3'},
        ]
        return {
            'items': [
                {'id': 'phone_pd_id_1', 'value': 'phone1'},
                {'id': 'phone_pd_id_2', 'value': 'phone2'},
                {'id': 'phone_pd_id_3', 'value': 'phone3'},
            ],
        }

    await taxi_hiring_zd_push.run_task('distlock/hiring-zd-push')

    cursor = pgsql['hiring_zd_push'].conn.cursor()
    cursor.execute(
        'SELECT park_driver_profile_id FROM hiring_zd_push.pushed_profiles',
    )
    list_rows = list(cursor)
    assert len(list_rows) == 3
    driver_profile_ids = ['park1_driver1', 'park2_driver2', 'park2_driver3']
    for park_driver_profile_id in list_rows:
        assert park_driver_profile_id[0] in driver_profile_ids

    cursor = pgsql['hiring_zd_push'].conn.cursor()
    cursor.execute('SELECT cursor FROM hiring_zd_push.worker_status')
    list_rows = list(cursor)
    assert len(list_rows) == 1
    assert list_rows[0][0] == '0_1546300750_4'
