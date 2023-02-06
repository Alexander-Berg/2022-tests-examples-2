import json

import pytest


ENDPOINT = '/v1/driver/medical-card'
LOGGER_ENDPOINT = '/driver-work-rules/service/v1/change-logger'


@pytest.mark.parametrize(
    'driver_profile_id,is_enabled,issue_date,old_value,new_value,'
    'mock_times_called',
    [
        ('uuid0', False, None, '{}', '{"is_enabled":false}', 1),
        (
            'uuid0',
            None,
            '2019-01-10T22:39:50+03:00',
            '{}',
            '{"issue_date":"2019-01-10T19:39:50+00:00"}',
            1,
        ),
        (
            'uuid1',
            True,
            '2019-01-10T22:39:50+03:00',
            '{"is_enabled":false,'
            '"issue_date":"2018-11-20T14:04:14.517+00:00"}',
            '{"is_enabled":true,"issue_date":"2019-01-10T19:39:50+00:00"}',
            1,
        ),
        (
            'uuid1',
            True,
            None,
            '{"is_enabled":false,'
            '"issue_date":"2018-11-20T14:04:14.517+00:00"}',
            '{"is_enabled":true,'
            '"issue_date":"2018-11-20T14:04:14.517+00:00"}',
            1,
        ),
        ('uuid1', False, '2018-11-20T17:04:14.517+03:00', None, None, 0),
    ],
)
async def test_driver_meical_card_patch(
        taxi_driver_profiles,
        mockserver,
        mongodb,
        driver_profile_id,
        is_enabled,
        issue_date,
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
                'object_id': driver_profile_id,
                'object_type': 'MongoDB.Docs.Driver.DriverDoc',
                'diff': [
                    {
                        'field': 'MedicalCard',
                        'old': old_value,
                        'new': new_value,
                    },
                ],
            },
            'author': {
                'dispatch_user_id': driver_profile_id,
                'display_name': 'driver',
                'user_ip': '',
            },
        }

    old_driver = mongodb.dbdrivers.find_one(
        {'park_id': 'park1', 'driver_id': driver_profile_id},
        {'modified_date', 'updated_ts'},
    )

    medical_card = {}
    if is_enabled is not None:
        medical_card['is_enabled'] = is_enabled
    if issue_date is not None:
        medical_card['issue_date'] = issue_date

    response = await taxi_driver_profiles.patch(
        ENDPOINT,
        params={'park_id': 'park1', 'driver_profile_id': driver_profile_id},
        data=json.dumps(
            {
                'author': {
                    'consumer': 'driver-profile-view',
                    'identity': {
                        'type': 'driver',
                        'driver_profile_id': driver_profile_id,
                    },
                },
                'medical_card': medical_card,
            },
        ),
    )

    assert response.status_code == 200
    assert _mock_change_logger.times_called == mock_times_called

    driver = mongodb.dbdrivers.find_one(
        {'park_id': 'park1', 'driver_id': driver_profile_id},
        {'medical_card', 'modified_date', 'updated_ts'},
    )
    if is_enabled is not None:
        assert driver['medical_card']['is_enabled'] == is_enabled
    assert driver['modified_date'] > old_driver['modified_date']
    assert driver['updated_ts'] > old_driver['updated_ts']


@pytest.mark.parametrize(
    'driver_profile_id, issue_date, old_value, new_value',
    [
        (
            'uuid0',
            '2019-01-10T22:39:50+03:00',
            '{}',
            '{"issue_date":"2019-01-10T19:39:50+00:00"}',
        ),
    ],
)
async def test_qc_meical_card_patch(
        taxi_driver_profiles,
        mockserver,
        mongodb,
        driver_profile_id,
        issue_date,
        old_value,
        new_value,
):
    @mockserver.json_handler(LOGGER_ENDPOINT)
    def _mock_change_logger(request):
        body = json.loads(request.get_data())
        body.pop('entity_id')
        assert body == {
            'park_id': 'park1',
            'change_info': {
                'object_id': driver_profile_id,
                'object_type': 'MongoDB.Docs.Driver.DriverDoc',
                'diff': [
                    dict(field='MedicalCard', old=old_value, new=new_value),
                ],
            },
            'author': dict(
                display_name='platform', dispatch_user_id='', user_ip='',
            ),
        }

    old_driver = mongodb.dbdrivers.find_one(
        {'park_id': 'park1', 'driver_id': driver_profile_id},
        {'modified_date', 'updated_ts'},
    )

    medical_card = dict(issue_date=issue_date)
    response = await taxi_driver_profiles.patch(
        ENDPOINT,
        params={'park_id': 'park1', 'driver_profile_id': driver_profile_id},
        data=json.dumps(
            {
                'author': {
                    'consumer': 'qc',
                    'identity': {
                        'type': 'job',
                        'job_name': 'medcard_issue_date',
                    },
                },
                'medical_card': medical_card,
            },
        ),
    )

    assert response.status_code == 200
    assert _mock_change_logger.times_called == 1

    driver = mongodb.dbdrivers.find_one(
        {'park_id': 'park1', 'driver_id': driver_profile_id},
        {'medical_card', 'modified_date', 'updated_ts'},
    )
    assert driver['modified_date'] > old_driver['modified_date']
    assert driver['updated_ts'] > old_driver['updated_ts']
