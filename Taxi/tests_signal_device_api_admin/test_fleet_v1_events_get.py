import datetime

import dateutil.parser
import pytest
import pytz

from tests_signal_device_api_admin import utils
from tests_signal_device_api_admin import web_common

PROTOCOL = 'https://'
S3_VIDEOS_BUCKET = 'sda-videos'
S3_PHOTOS_BUCKET = 'sda-photos'
MOCK_S3_PRODUCTION_URL = 's3-private.mock.net'
MOCK_S3_TESTING_URL = 's3.mock.net'
S3_SIGNATURE = 'Signature'
S3_AWS_ACCESS_KEY_ID = 'AWSAccessKeyId'
S3_EXPIRES = 'Expires'

VIDEO_PATH = 'some/s3/path.mp4'
PHOTO_PATH = 'some/s3/path.jpg'
GNSS_1 = {  # we check this one for video
    'lat': 54.99250000,
    'lon': 73.36861111,
    'speed_kmph': 34.437895,
    'accuracy_m': 0.61340,
    'direction_deg': 245.895,
}
EVENT_1 = {
    'device_id': 'e58e753c44e548ce9edaec0e0ef9c8c1',
    'device_serial_number': 'AB1',
    'id': '34b3d7ec-30f6-43cf-94a8-911bc8fe404c',
    'event_uploaded_at': '2020-02-27T13:00:00+00:00',
    'event_at': '2020-02-27T12:00:00+00:00',
    'type': 'sleep',
    'gnss': GNSS_1,
    'vehicle': {'plate_number': 'K444AB55', 'id': 'c1'},
    'is_seen': False,
    'resolution': 'hide',
}
GNSS_2 = {  # we check this one for photo
    'lat': 54.99550072,
    'lon': 72.94622044,
}
EVENT_2 = {
    'device_id': '4306de3dfd82406d81ea3c098c80e9ba',
    'device_serial_number': 'AB12FE45DD',
    'id': '54b3d7ec-30f6-43cf-94a8-911bc8fe404c',
    'event_uploaded_at': '2020-02-27T23:55:00+00:00',
    'event_at': '2020-02-26T23:55:00+00:00',
    'type': 'sleep',
    'gnss': GNSS_2,
    'vehicle': {'plate_number': 'K123KK777', 'id': 'c2'},
    'is_seen': False,
}


# Не выносим в общий модуль – скоро удалим /v1/events/list
def check_presigned_url_correctness(event, is_video, is_testing_mds_url):
    five_min_ago = datetime.datetime.now(tz=pytz.UTC) - datetime.timedelta(
        seconds=300,
    )

    def _validate_url(presigned_url, bucket, path):
        assert 'expires_at' in presigned_url
        assert (
            dateutil.parser.parse(presigned_url['expires_at']) > five_min_ago
        )
        assert 'link' in presigned_url
        if is_testing_mds_url:
            url = MOCK_S3_TESTING_URL
        else:
            url = MOCK_S3_PRODUCTION_URL
        assert presigned_url['link'].startswith(
            PROTOCOL + bucket + '.' + url + '/' + path,
        )
        assert S3_AWS_ACCESS_KEY_ID in presigned_url['link']
        assert S3_SIGNATURE in presigned_url['link']
        assert S3_EXPIRES in presigned_url['link']

    external_presigned_url = None

    if is_video:
        assert 'presigned_url' in event['video']
        presigned_url = event['video']['presigned_url']

        assert 'presigned_url' in event['external_video']
        external_presigned_url = event['external_video']['presigned_url']
        bucket = S3_VIDEOS_BUCKET
        path = VIDEO_PATH
    else:
        assert 'presigned_url' in event['photo']
        presigned_url = event['photo']['presigned_url']

        assert 'presigned_url' in event['external_photo']
        external_presigned_url = event['external_photo']['presigned_url']

        bucket = S3_PHOTOS_BUCKET
        path = PHOTO_PATH

    _validate_url(presigned_url, bucket, path)
    if external_presigned_url:
        _validate_url(presigned_url, bucket, path)


def check_and_clean_media(event, is_testing_mds_url=False):
    if 'gnss' in event and event['gnss'] == GNSS_1:
        assert 'video' in event
        check_presigned_url_correctness(event, True, is_testing_mds_url)
        event.pop('video')
        event.pop('external_video')
        assert 'photo' not in event
    elif 'gnss' in event and event['gnss'] == GNSS_2:
        assert 'photo' in event
        check_presigned_url_correctness(event, False, is_testing_mds_url)
        event.pop('photo')
        event.pop('external_photo')
        assert 'video' not in event
    return event


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.parametrize(
    'headers, event_id, code, event',
    [
        (
            {**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
            EVENT_1['id'],
            200,
            EVENT_1,
        ),
        (
            {**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
            EVENT_2['id'],
            200,
            EVENT_2,
        ),
        (
            {**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
            '24b3d7ec-30f6-43cf-94a8-911bc8fe404c',
            404,
            {'code': 'event_not_found', 'message': 'Event not found'},
        ),
    ],
)
async def test_ok_partners(
        taxi_signal_device_api_admin,
        headers,
        event_id,
        code,
        event,
        mockserver,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info(),
                    'specifications': ['signalq'],
                },
            ],
        }

    response = await taxi_signal_device_api_admin.get(
        f'fleet/signal-device-api-admin/v1/events',
        params={'event_id': event_id},
        headers=headers,
    )
    assert response.status_code == code, response.text
    assert check_and_clean_media(response.json()) == event


EVENT_WITH_CAR = {
    'device_id': 'e58e753c44e548ce9edaec0e0ef9c8c1',
    'device_serial_number': 'AB1',
    'event_at': '2020-02-27T12:00:00+00:00',
    'event_uploaded_at': '2020-02-27T13:00:00+00:00',
    'gnss': {
        'accuracy_m': 0.6134,
        'direction_deg': 245.895,
        'lat': 54.9925,
        'lon': 73.36861111,
        'speed_kmph': 34.437895,
    },
    'id': '34b3d7ec-30f6-43cf-94a8-911bc8fe404c',
    'type': 'sleep',
    'vehicle': {'id': 'c1', 'plate_number': 'K444AB55'},
    'is_seen': False,
}

EVENT_WITH_DRIVER = {
    'device_id': 'e58e753c44e548ce9edaec0e0ef9c8c1',
    'device_serial_number': 'AB1',
    'driver': {
        'first_name': 'Petr',
        'id': 'd1',
        'last_name': 'Ivanov',
        'license_number': '7723306794',
        'middle_name': 'D`',
        'phones': ['+79265975310'],
    },
    'event_at': '2020-02-27T13:02:00+00:00',
    'event_uploaded_at': '2020-02-27T13:02:00+00:00',
    'gnss': {'lat': 54.9455, 'lon': 73.36822151, 'speed_kmph': 89.437895},
    'id': '44b3d7ec-30f6-43cf-94a8-911bc8fe404c',
    'type': 'driver_lost',
    'vehicle': {'id': 'c1', 'plate_number': 'K444AB55'},
    'is_seen': False,
}

DRIVER_PROFILES_LIST_RESPONSE = {
    'driver_profiles': [
        {
            'driver_profile': {
                'first_name': 'Petr',
                'middle_name': 'D`',
                'last_name': 'Ivanov',
                'driver_license': {
                    'expiration_date': '2025-08-07T00:00:00+0000',
                    'issue_date': '2015-08-07T00:00:00+0000',
                    'normalized_number': '7723306794',
                    'number': '7723306794',
                },
                'id': 'd1',
                'phones': ['+79265975310'],
            },
        },
    ],
    'offset': 0,
    'parks': [{'id': 'p1'}],
    'total': 1,
    'limit': 1,
}


@pytest.mark.pgsql('signal_device_api_meta_db', files=['drivers_search.sql'])
@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.parametrize(
    'event_id, event',
    [
        (EVENT_WITH_DRIVER['id'], EVENT_WITH_DRIVER),
        (EVENT_WITH_CAR['id'], EVENT_WITH_CAR),
    ],
)
async def test_with_drivers(
        taxi_signal_device_api_admin, parks, event_id, event, mockserver,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info(),
                    'specifications': ['signalq'],
                },
            ],
        }

    parks.set_driver_profiles_response(DRIVER_PROFILES_LIST_RESPONSE)

    response = await taxi_signal_device_api_admin.get(
        f'fleet/signal-device-api-admin/v1/events',
        params={'event_id': event_id},
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
    )

    assert response.status_code == 200, response.text

    if event_id == EVENT_WITH_DRIVER['id']:
        assert parks.driver_profiles_list.times_called == 1
        parks_request = parks.driver_profiles_list.next_call()['request'].json
        assert parks_request == {
            'query': {'park': {'id': 'p1', 'driver_profile': {'id': ['d1']}}},
            'fields': {
                'driver_profile': [
                    'id',
                    'first_name',
                    'middle_name',
                    'last_name',
                    'driver_license',
                    'phones',
                ],
            },
            'limit': 1,
            'offset': 0,
        }

    assert response.json() == event


def _get_demo_event_id(event_id):
    return utils.get_decoded_cursor(event_id).split('|')[1]


@pytest.mark.config(
    SIGNAL_DEVICE_API_ADMIN_DEMO_SETTINGS_V2={
        'timings': {
            'working_day_start': 8,
            'working_day_end': 20,
            'working_days_amount': 7,
        },
        'comments': ['Комментарий 1', 'Комментарий 2', 'Комментарий 3'],
        'media': {'__default__': {}},
        'devices': web_common.DEMO_DEVICES,
        'events': web_common.DEMO_EVENTS,
        'vehicles': web_common.DEMO_VEHICLES,
        'groups': [],
        'drivers': web_common.DEMO_DRIVERS,
    },
)
@pytest.mark.parametrize(
    'event_id, expected_code',
    [
        pytest.param('e6', 200, id='device exists'),
        pytest.param('no such device', 404, id='no such device'),
    ],
)
async def test_demo_events_get(
        taxi_signal_device_api_admin, event_id, expected_code, mockserver,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info('no such park'),
                    'specifications': ['taxi'],
                },
            ],
        }

    response = await taxi_signal_device_api_admin.get(
        f'fleet/signal-device-api-admin/v1/events',
        params={
            'event_id': utils.get_encoded_events_cursor(
                '2020-02-27T13:02:00+00:00', event_id,
            ),
        },
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'no such park'},
    )
    assert response.status_code == expected_code, response.text

    if response.status_code != 200:
        return

    response_json = response.json()
    assert (
        _get_demo_event_id(response_json['id']) == event_id
        and response_json['type'] == web_common.DEMO_EVENTS[5]['event_type']
        and response_json['driver'] == web_common.DEMO_DRIVERS[0]
        and response_json['vehicle'] == web_common.DEMO_VEHICLES[1]
    )
