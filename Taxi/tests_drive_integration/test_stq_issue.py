import json

import pytest

PARK_ID = 'db1'
DRIVER_PROFILE_ID = 'uuid1'
DRIVE_ID = 'drive_id1'


@pytest.mark.parametrize('issue_type', ['new', 'replace'])
async def test_issue_key(
        stq, stq_runner, mockserver, experiments3, issue_type, pgsql, load,
):
    experiments3.add_config(
        name='drive_integration_key_permissions',
        consumers=['drive-integration/issue_key'],
        match={
            'enabled': True,
            'consumers': [{'name': 'drive-integration/issue_key'}],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[],
        default_value={'permission_ids': ['id1', 'id2', 'id3']},
    )

    queries = []
    if issue_type == 'replace':
        queries = [load('main_replace.sql')]
    pgsql['drive_integration'].apply_queries(queries)

    @mockserver.json_handler('uapi-keys/internal/v2/keys')
    def mock_internal_keys(request):
        args = json.loads(request.get_data())
        assert args == {
            'key': {
                'consumer_id': 'fleet-api',
                'client_id': 'yndx.drive',
                'entity_id': PARK_ID,
                'permission_ids': ['id1', 'id2', 'id3'],
                'comment': 'created by drive-integration',
            },
            'creator': {'uid': '123321', 'uid_provider': 'yandex'},
        }

        return mockserver.make_response(
            json={
                'auth': {'api_key': '_api_key_api_key_api_key_api_key'},
                'key': {
                    'id': 'some_id',
                    'consumer_id': 'fleet-api',
                    'client_id': 'yndx.drive',
                    'is_enabled': True,
                    'entity_id': PARK_ID,
                    'permission_ids': ['id1', 'id2', 'id3'],
                    'comment': 'created by drive-integration',
                    'creator': {'uid': '123321', 'uid_provider': 'yandex'},
                    'created_at': '2021-05-30T09:00:00+00:00',
                    'updated_at': '2021-06-01T09:00:00+00:00',
                },
            },
            status=200,
        )

    await stq_runner.drive_integration_key_issue.call(
        task_id=PARK_ID + '_' + DRIVER_PROFILE_ID + '_' + DRIVE_ID + '_issue',
        kwargs={
            'park_id': PARK_ID,
            'driver_profile_id': DRIVER_PROFILE_ID,
            'yandex_drive_id': DRIVE_ID,
        },
    )

    assert mock_internal_keys.times_called == 1
    assert stq.drive_integration_key_delivery.times_called == 1

    stq_data = stq.drive_integration_key_delivery.next_call()
    assert stq_data['queue'] == 'drive_integration_key_delivery'
    assert (
        stq_data['id']
        == PARK_ID + '_' + DRIVER_PROFILE_ID + '_' + DRIVE_ID + '_delivery'
    )

    del stq_data['kwargs']['log_extra']
    assert stq_data['kwargs'] == {
        'park_id': PARK_ID,
        'driver_profile_id': DRIVER_PROFILE_ID,
        'yandex_drive_id': DRIVE_ID,
        'delivery_type': 'new_key' if issue_type == 'new' else 'replace_key',
        'api_key': '_api_key_api_key_api_key_api_key',
        'key_id': 'some_id',
    }
