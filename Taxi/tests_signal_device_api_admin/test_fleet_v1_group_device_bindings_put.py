import typing

import pytest

from tests_signal_device_api_admin import utils
from tests_signal_device_api_admin import web_common

ENDPOINT = 'fleet/signal-device-api-admin/v1/group/device-bindings'

BAD_GROUP_RESPONSE = {
    'code': 'bad_group',
    'message': 'Incorrect group provided',
}


def make_bad_devices_response(public_ids: typing.List[str]):
    return {
        'code': 'bad_devices',
        'message': 'There are incorrect devices',
        'bad_devices': public_ids,
    }


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.parametrize(
    'park_id, device_ids, group_id, expected_code, err_response',
    [
        (
            'p1',
            ['e58e753c44e548ce9edaec0e0ef9c8c1'],
            '3bd269aa-3aca-494b-8bbb-88f99847464a',
            200,
            None,
        ),
        (
            'p2',
            [
                '77748dae0a3244ebb9e1b8d244982c28',
                '11449fbd4c7760578456c4a123456789',
            ],
            '29a168a6-2fe3-401d-9959-ba1b14fd4862',
            200,
            None,
        ),
        (
            'p1',
            ['e58e753c44e548ce9edaec0e0ef9c8c1'],
            '1db9bcc6-982c-46ff-a161-78fa1817be01',
            400,
            BAD_GROUP_RESPONSE,
        ),
        (
            'p2',
            ['e58e753c44e548ce9edaec0e0ef9c8c1'],
            '29a168a6-2fe3-401d-9959-ba1b14fd4862',
            400,
            make_bad_devices_response(['e58e753c44e548ce9edaec0e0ef9c8c1']),
        ),
        (
            'p2',
            [
                '4306de3dfd82406d81ea3c098c80e9ba',
                'e58e753c44e548ce9edaec0e0ef9c8c1',
                '77748dae0a3244ebb9e1b8d244982c28',
            ],
            '29a168a6-2fe3-401d-9959-ba1b14fd4862',
            400,
            make_bad_devices_response(
                [
                    '4306de3dfd82406d81ea3c098c80e9ba',
                    '77748dae0a3244ebb9e1b8d244982c28',
                ],
            ),
        ),
    ],
)
async def test_group_device_bindings_put(
        taxi_signal_device_api_admin,
        pgsql,
        park_id,
        device_ids,
        group_id,
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

    response = await taxi_signal_device_api_admin.put(
        ENDPOINT,
        json={'group_id': group_id, 'device_ids': device_ids},
        headers=headers,
    )

    assert response.status_code == expected_code, response.text
    if expected_code == 400:
        response_json = response.json()
        if err_response.get('bad_devices') is None:
            assert response_json == err_response
        else:
            assert response_json['code'] == err_response['code']
            assert response_json['message'] == err_response['message']
            utils.unordered_lists_are_equal(
                response_json['bad_devices'], err_response['bad_devices'],
            )
        return

    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        f"""
        SELECT group_id
        FROM signal_device_api.park_device_profiles
        WHERE device_id = ANY (
            SELECT id
            FROM signal_device_api.devices
            WHERE public_id IN ('{"','".join(device_ids)}')
        ) AND park_id = \'{park_id}\' AND is_active;
        """,
    )
    db_result = list(db)
    assert len(db_result) == len(device_ids)
    assert db_result == [(group_id,) for _ in range(len(device_ids))]


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.parametrize(
    'park_id, device_ids, group_id, new_updated',
    [
        (
            'p2',
            [
                '77748dae0a3244ebb9e1b8d244982c28',
                '11449fbd4c7760578456c4a123456789',
            ],
            '29a168a6-2fe3-401d-9959-ba1b14fd4862',
            [None, '2020-02-27T00:00:00+03:00'],
        ),
        (
            'p2',
            ['11449fbd4c7760578456c4a123456789'],
            '29a168a6-2fe3-401d-9959-ba1b14fd4862',
            ['2020-02-27T00:00:00+03:00'],
        ),
    ],
)
async def test_group_device_bindings_put_partial_updated(
        taxi_signal_device_api_admin,
        pgsql,
        park_id,
        device_ids,
        group_id,
        new_updated,
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

    response = await taxi_signal_device_api_admin.put(
        ENDPOINT,
        json={'group_id': group_id, 'device_ids': device_ids},
        headers=headers,
    )

    assert response.status_code == 200, response.text

    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        f"""
        SELECT group_id, updated_at
        FROM signal_device_api.park_device_profiles
        WHERE device_id = ANY (
            SELECT id
            FROM signal_device_api.devices
            WHERE public_id IN ('{"','".join(device_ids)}')
        ) AND park_id = \'{park_id}\' AND is_active
        ORDER BY device_id ASC;
        """,
    )
    db_result = list(db)
    assert len(db_result) == len(device_ids)
    for i, row in enumerate(db_result):
        assert row[0] == group_id
        if new_updated[i] is not None:
            assert (
                utils.convert_datetime_in_tz(
                    row[1], 'Europe/Moscow',
                ).isoformat()
                == new_updated[i]
            )
