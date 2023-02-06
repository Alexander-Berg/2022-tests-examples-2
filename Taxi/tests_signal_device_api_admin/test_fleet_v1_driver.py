import pytest

from tests_signal_device_api_admin import web_common

ENDPOINT = 'fleet/signal-device-api-admin/v1/driver'

FLEET_PARKS_RESPONSE = {
    'parks': [
        {
            'city_id': 'CITY_ID1',
            'country_id': 'rus',
            'demo_mode': False,
            'id': 'p1',
            'is_active': True,
            'is_billing_enabled': True,
            'is_franchising_enabled': False,
            'locale': 'ru',
            'login': 'LOGIN1',
            'name': 'NAME1',
            'specifications': ['signalq'],
            'geodata': {'lat': 1, 'lon': 1, 'zoom': 1},
        },
    ],
}


def _count_not_delete_events(pgsql):
    db = pgsql['signal_device_api_meta_db'].cursor()
    query_str = (
        'SELECT COUNT(*) '
        'FROM signal_device_api.events e '
        'WHERE e.resolution IS NULL '
        '   OR e.resolution != \'delete\' '
    )
    db.execute(query_str)
    return list(db)[0][0]


def _count_no_driver_rows(pgsql, db_name):
    db = pgsql['signal_device_api_meta_db'].cursor()
    query_str = (
        'SELECT COUNT(*) '
        f'FROM signal_device_api.{db_name} '
        'WHERE driver_detected IS NULL '
    )
    db.execute(query_str)
    return list(db)[0][0]


@pytest.mark.config(
    SIGNAL_DEVICE_API_ADMIN_S3_MDS_URL_SETTINGS_V2={
        'url': '',
        'photos_bucket_name': 'sda-photos',
        'videos_bucket_name': 'sda-videos',
        'files_bucket_name': 'sda-files',
    },
)
@pytest.mark.pgsql('signal_device_api_meta_db', files=['test_data.sql'])
@pytest.mark.parametrize(
    'driver_profile_id, left_events_amount, null_history_amount, '
    'null_statuses_amount, expected_code',
    [
        pytest.param('d1', 1, 2, 1, 200, id='test_one'),
        pytest.param('d2', 3, 1, 0, 200, id='no_events_for_driver'),
    ],
)
async def test_general(
        taxi_signal_device_api_admin,
        pgsql,
        driver_profile_id,
        left_events_amount,
        null_history_amount,
        null_statuses_amount,
        expected_code,
        mockserver,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _get_specs(request):
        if driver_profile_id == 'd3':
            FLEET_PARKS_RESPONSE['parks'][0]['specifications'] = [
                'signalq',
                'taxi',
            ]
            return FLEET_PARKS_RESPONSE
        FLEET_PARKS_RESPONSE['parks'][0]['specifications'] = ['signalq']
        return FLEET_PARKS_RESPONSE

    @mockserver.json_handler(
        '/signal-device-tracks/internal/signal-device-tracks/v1/events',
    )
    def _delete_tracks(request):
        return {}

    @mockserver.json_handler(
        '/biometry-etalons/internal/biometry-etalons/v1/profile',
    )
    def _delete_profile(request):
        return {}

    @mockserver.json_handler(
        '/driver-profiles/internal/v1/driver/fill-with-trash',
    )
    def _get_profile(request):
        return mockserver.make_response(status=200)

    @mockserver.json_handler(
        '/driver-profiles/v1/driver/changes-history/remove-by-request',
    )
    def _delete_history(request):
        return mockserver.make_response(status=200)

    response = await taxi_signal_device_api_admin.delete(
        ENDPOINT,
        params={'driver_profile_id': driver_profile_id},
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
    )
    assert response.status_code == expected_code

    if expected_code != 200:
        return

    assert _count_not_delete_events(pgsql) == left_events_amount
    assert (
        _count_no_driver_rows(pgsql, 'status_history') == null_history_amount
    )
    assert _count_no_driver_rows(pgsql, 'statuses') == null_statuses_amount
