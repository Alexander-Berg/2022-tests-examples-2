import pytest

from tests_signal_device_api_admin import web_common

ENDPOINT = 'fleet/signal-device-api-admin/v1/group'

ERROR_RESPONSE = {'code': 'bad_group', 'message': 'Incorrect group provided'}


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.parametrize(
    'park_id, group_id, group_name, expected_code, err_response',
    [
        (
            'p2',
            '29a168a6-2fe3-401d-9959-ba1b14fd4862',
            'WestCoastCustoms',
            200,
            None,
        ),
        (
            'p228',
            '29a168a6-2fe3-401d-9959-ba1b14fd4862',
            'WestCoastCustoms',
            400,
            ERROR_RESPONSE,
        ),
        (
            'p2',
            'aab168a6-2aa3-4bbd-9959-ba1b14fd4862',
            'WestCoastCustoms',
            400,
            ERROR_RESPONSE,
        ),
        (
            'p1',
            'aab1aaa6-bba3-4bbd-9959-ba1b14fd4862',
            'WestCoastCustoms',
            400,
            ERROR_RESPONSE,
        ),
    ],
)
async def test_group_patch(
        taxi_signal_device_api_admin,
        pgsql,
        park_id,
        group_id,
        group_name,
        expected_code,
        err_response,
        mockserver,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info(park_id),
                    'specifications': ['signalq'],
                },
            ],
        }

    headers = {**web_common.PARTNER_HEADERS_1, 'X-Park-Id': park_id}

    body = {'group_id': group_id, 'group_name': group_name}
    response = await taxi_signal_device_api_admin.patch(
        ENDPOINT, json=body, headers=headers,
    )

    assert response.status_code == expected_code, response.text
    if expected_code == 400:
        assert response.json() == err_response
        return

    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        'SELECT TRUE '
        'FROM signal_device_api.device_groups '
        f'WHERE group_id = \'{group_id}\' AND group_name = \'{group_name}\'',
    )
    assert list(db)
