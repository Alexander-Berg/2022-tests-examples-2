import json

import pytest


ENDPOINT = '/v1/driver/is-readonly'
LOGGER_ENDPOINT = '/driver-work-rules/service/v1/change-logger'


@pytest.mark.parametrize(
    'contractor_profile_id,is_readonly,old_value,'
    'new_value,mock_times_called',
    [
        ('uuid0', True, '{}', '{"is_readonly":true}', 1),
        ('uuid1', True, '{"is_readonly":true}', '{}', 0),
        ('uuid1', False, '{"is_readonly":true}', '{"is_readonly":false}', 1),
    ],
)
async def test_driver_is_readonly_patch(
        taxi_driver_profiles,
        mockserver,
        mongodb,
        contractor_profile_id,
        is_readonly,
        old_value,
        new_value,
        mock_times_called,
):
    @mockserver.json_handler(LOGGER_ENDPOINT)
    def _mock_change_logger(request):
        body = json.loads(request.get_data())
        body.pop('entity_id')
        assert body == {
            'park_id': 'park1',
            'change_info': {
                'object_id': contractor_profile_id,
                'object_type': 'MongoDB.Docs.Driver.DriverDoc',
                'diff': [
                    {
                        'field': 'IsReadonly',
                        'old': old_value,
                        'new': new_value,
                    },
                ],
            },
            'author': {
                'display_name': 'platform',
                'user_ip': '',
                'dispatch_user_id': '',
            },
        }

    old_driver = mongodb.dbdrivers.find_one(
        {'park_id': 'park1', 'driver_id': contractor_profile_id},
        {'modified_date', 'updated_ts'},
    )

    response = await taxi_driver_profiles.patch(
        ENDPOINT,
        params={
            'park_id': 'park1',
            'contractor_profile_id': contractor_profile_id,
        },
        json={
            'author': {
                'consumer': 'contractor-profiles-manager',
                'identity': {
                    'type': 'job',
                    'job_name': 'pro-profiles-removal-cron',
                },
            },
            'data': {'is_readonly': is_readonly},
        },
    )

    assert response.status_code == 200
    assert _mock_change_logger.times_called == mock_times_called

    driver = mongodb.dbdrivers.find_one(
        {'park_id': 'park1', 'driver_id': contractor_profile_id},
        {'is_readonly', 'modified_date', 'updated_ts'},
    )
    if is_readonly is not None:
        assert driver['is_readonly'] == is_readonly
    assert driver['modified_date'] > old_driver['modified_date']
    assert driver['updated_ts'] > old_driver['updated_ts']
