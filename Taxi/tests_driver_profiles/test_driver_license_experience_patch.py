import datetime as dt
import json

import pytest

ENDPOINT = '/v1/driver/license-experience'


@pytest.mark.parametrize('index', [0, 1])
async def test_driver_license_experience_patch(
        taxi_driver_profiles, mockserver, mongodb, index,
):
    park_id = f'dbid_{index}'
    driver_profile_id = f'uuid_{index}'

    doc_before = mongodb.dbdrivers.find_one(
        {'park_id': park_id, 'driver_id': driver_profile_id},
        {'license_experience', 'modified_date', 'updated_ts'},
    )
    lic_exp_old = doc_before.get('license_experience', {})
    changes = [{'category': 'total', 'since': '2017-04-30T00:00:00+03:00'}]

    lic_exp_new = dict(lic_exp_old)
    for change in changes:
        lic_exp_new[change['category']] = change['since']

    def _serialize(lic_exp: dict) -> str:
        if not lic_exp:
            return '{}'

        for key in lic_exp:
            if isinstance(lic_exp[key], str):  # came from request
                lic_exp[key] = (
                    dt.datetime.fromisoformat(lic_exp[key])
                    .astimezone(dt.timezone.utc)
                    .isoformat()
                )
            else:  # datetime came from mongo
                lic_exp[key] = (
                    lic_exp[key].replace(tzinfo=dt.timezone.utc).isoformat()
                )
        return json.dumps(lic_exp).replace(': ', ':')

    @mockserver.json_handler('/driver-work-rules/service/v1/change-logger')
    def _mock_change_logger(request):
        body = request.json
        body.pop('entity_id')
        assert body == {
            'park_id': park_id,
            'change_info': {
                'object_id': driver_profile_id,
                'object_type': 'MongoDB.Docs.Driver.DriverDoc',
                'diff': [
                    {
                        'field': 'LicenseExperience',
                        'old': _serialize(lic_exp_old),
                        'new': _serialize(lic_exp_new),
                    },
                ],
            },
            'author': {
                'dispatch_user_id': '',
                'display_name': 'platform',
                'user_ip': '',
            },
        }

    response = await taxi_driver_profiles.patch(
        ENDPOINT,
        params={'park_id': park_id, 'driver_profile_id': driver_profile_id},
        json={
            'author': {
                'consumer': 'qc',
                'identity': {'type': 'job', 'job_name': 'experience_job'},
            },
            'license_experience': changes,
        },
    )

    assert response.status_code == 200
    assert _mock_change_logger.times_called == 1

    doc_after = mongodb.dbdrivers.find_one(
        {'park_id': park_id, 'driver_id': driver_profile_id},
        {'license_experience', 'modified_date', 'updated_ts'},
    )
    assert (
        doc_after['license_experience']['total']
        == dt.datetime.fromisoformat(changes[0]['since'])
        .astimezone(dt.timezone.utc)
        .replace(tzinfo=None)
    )
    assert doc_after['modified_date'] > doc_before['modified_date']
    assert doc_after['updated_ts'] > doc_before['updated_ts']
