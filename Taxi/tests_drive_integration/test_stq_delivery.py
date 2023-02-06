# pylint: disable=import-only-modules
import json

import pytest

from tests_drive_integration.utils import select_named

PARK_ID = 'db1'
DRIVER_PROFILE_ID = 'uuid1'
DRIVE_ID = 'drive_id1'


@pytest.mark.parametrize('issue_type', ['new', 'replace'])
async def test_key_delivery(stq_runner, mockserver, issue_type, pgsql, load):
    queries = [load('main_replace.sql')]
    pgsql['drive_integration'].apply_queries(queries)

    @mockserver.json_handler('admin-yandex-drive/user_tags/add')
    def mock_driver_user_tags(request):
        args = json.loads(request.get_data())
        assert args == {
            'tag': 'taxi_fleet_auth_info',
            'object_id': DRIVE_ID,
            'fields': [
                {'key': 'apikey', 'value': '_api_key_api_key_api_key_api_key'},
                {'key': 'client_id', 'value': 'yndx.drive'},
                {'key': 'park_id', 'value': PARK_ID},
                {'key': 'profile_id', 'value': DRIVER_PROFILE_ID},
            ],
        }

        return mockserver.make_response(
            json={
                'tagged_objects': [
                    {'tag_id': ['tag_123'], 'object_id': DRIVE_ID},
                ],
            },
            status=200,
        )

    await stq_runner.drive_integration_key_delivery.call(
        task_id=PARK_ID
        + '_'
        + DRIVER_PROFILE_ID
        + '_'
        + DRIVE_ID
        + '_delivery',
        kwargs={
            'park_id': PARK_ID,
            'driver_profile_id': DRIVER_PROFILE_ID,
            'yandex_drive_id': DRIVE_ID,
            'delivery_type': (
                'new_key' if issue_type == 'new' else 'replace_key'
            ),
            'api_key': '_api_key_api_key_api_key_api_key',
            'key_id': 'some_id',
        },
    )

    assert mock_driver_user_tags.times_called == 1

    rows = select_named(
        'SELECT * FROM state.drivers', pgsql['drive_integration'],
    )
    assert len(rows) == 1
    assert rows[0] == {
        'taxi_driver_id': f'({PARK_ID},{DRIVER_PROFILE_ID})',
        'yandex_drive_id': DRIVE_ID,
        'key_id': 'some_id',
        'tag_id': 'tag_123',
        'issue_state': 'issued',
    }
