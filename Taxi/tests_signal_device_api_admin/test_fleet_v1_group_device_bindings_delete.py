import pytest

from tests_signal_device_api_admin import web_common

ENDPOINT = 'fleet/signal-device-api-admin/v1/group/device-bindings'

ERROR_RESPONSE = {
    'code': 'binded_to_other_group',
    'message': 'Device is binded to other group',
}


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.parametrize(
    'park_id, device_id, group_id, is_device_binded_to_request_park, '
    'expected_mongo_group_id, expected_code, err_response',
    [
        (
            'p1',
            'e58e753c44e548ce9edaec0e0ef9c8c1',
            '3bd269aa-3aca-494b-8bbb-88f99847464a',
            True,
            None,
            200,
            None,
        ),
        (
            'p1',
            'e58e753c44e548ce9edaec0e0ef9c8c1',
            '1db9bcc6-982c-46ff-a161-78fa1817be01',
            True,
            None,
            200,
            None,
        ),
        (
            'p3',
            '11449fbd4c7760578456c4a123456789',
            '2480430f-8dc2-4217-b2d4-1e9806c3bd2a',
            True,
            None,
            200,
            None,
        ),
        (
            'p2',
            '77748dae0a3244ebb9e1b8d244982c28',
            '29a168a6-2fe3-401d-9959-ba1b14fd4862',
            True,
            None,
            200,
            None,
        ),
        (
            'p2',
            '77748dae0a3244ebb9e1b8d244982c28',
            '1db9bcc6-982c-46ff-a161-78fa1817be01',
            True,
            '29a168a6-2fe3-401d-9959-ba1b14fd4862',
            200,
            None,
        ),
        (
            'p2',
            'e58e753c44e548ce9edaec0e0ef9c8c1',
            '29a168a6-2fe3-401d-9959-ba1b14fd4862',
            False,
            None,
            400,
            None,
        ),
        (
            'p1',
            '4306de3dfd82406d81ea3c098c80e9ba',
            '29a168a6-2fe3-401d-9959-ba1b14fd4862',
            False,
            None,
            400,
            None,
        ),
        (
            'p2',
            '77748dae0a3244ebb9e1b8d244982c28',
            '51035bca-2011-4306-b148-8ff08c6f7a31'
            '1db9bcc6-982c-46ff-a161-78fa1817be01',
            True,
            False,
            400,
            ERROR_RESPONSE,
        ),
    ],
)
async def test_group_device_bindings_delete(
        taxi_signal_device_api_admin,
        pgsql,
        park_id,
        device_id,
        group_id,
        is_device_binded_to_request_park,
        expected_mongo_group_id,
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

    response = await taxi_signal_device_api_admin.delete(
        ENDPOINT,
        params={'device_id': device_id},
        json={'group_id': group_id},
        headers=headers,
    )

    assert response.status_code == expected_code, response.text
    if expected_code == 400:
        if err_response is not None:
            assert response.json() == err_response
        return

    if not is_device_binded_to_request_park:
        return

    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        f"""
        SELECT group_id
        FROM signal_device_api.park_device_profiles
        WHERE device_id = (
            SELECT id
            FROM signal_device_api.devices
            WHERE public_id = \'{device_id}\'
        ) AND park_id = \'{park_id}\' AND is_active;
        """,
    )
    db_result = list(db)
    assert db_result
    assert db_result[0][0] == expected_mongo_group_id
