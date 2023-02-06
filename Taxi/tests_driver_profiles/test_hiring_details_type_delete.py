import pytest


ENDPOINT = '/v1/contractor/hiring-details/hiring-type'

DEFAULT_AUTHOR = {
    'consumer': 'test',
    'identity': {'type': 'job', 'job_name': 'updater'},
}

DEFAULT_REQUEST = {'author': DEFAULT_AUTHOR}

OK_PARAMS = [
    (
        'park1',
        'driver1',
        [{'field': 'hiring_details.hiring_type', 'new': '', 'old': '1'}],
    ),
    ('park2', 'driver2', []),
    (
        'park3',
        'driver3',
        [{'field': 'hiring_details.hiring_type', 'new': '', 'old': '1'}],
    ),
    ('park4', 'driver4', []),
    ('park5', 'driver5', []),
]


@pytest.fixture(name='get_driver')
def get_driver_from_mongo(mongodb):
    return lambda park_id, contractor_profile_id: mongodb.dbdrivers.find_one(
        dict(park_id=park_id, driver_id=contractor_profile_id),
    )


def _make_params(park_id, contractor_profile_id):
    return {'park_id': park_id, 'contractor_profile_id': contractor_profile_id}


@pytest.mark.parametrize(
    ('park_id', 'contractor_profile_id', 'change_diff'), OK_PARAMS,
)
async def test_success(
        taxi_driver_profiles,
        mockserver,
        get_driver,
        park_id,
        contractor_profile_id,
        change_diff,
):
    driver_before = get_driver(park_id, contractor_profile_id)

    @mockserver.json_handler('/driver-work-rules/service/v1/change-logger')
    def _mock_change_logger(request):
        body = request.json
        body.pop('entity_id')
        assert body == {
            'park_id': park_id,
            'change_info': {
                'object_id': contractor_profile_id,
                'object_type': 'MongoDB.Docs.Driver.DriverDoc',
                'diff': change_diff,
            },
            'author': {
                'dispatch_user_id': '',
                'display_name': 'platform',
                'user_ip': '',
            },
        }
        return {}

    response = await taxi_driver_profiles.delete(
        ENDPOINT,
        params=_make_params(park_id, contractor_profile_id),
        json=DEFAULT_REQUEST,
    )
    assert response.status_code == 204
    if change_diff:
        assert _mock_change_logger.has_calls

    driver_after = get_driver(park_id, contractor_profile_id)
    if driver_before.get('hiring_details', {}).get('hiring_type'):
        assert driver_before != driver_after
        assert _mock_change_logger.has_calls
    assert driver_after['updated_ts'] != driver_before['updated_ts']
    assert driver_after['modified_date'] != driver_before['modified_date']


@pytest.mark.parametrize(
    ('park_id', 'contractor_profile_id'),
    [
        ('park1', 'invalid_driver_id'),
        ('invalid_park_id', 'driver1'),
        ('invalid_park_id', 'invalid_driver_id'),
    ],
)
async def test_driver_not_found(
        taxi_driver_profiles, get_driver, park_id, contractor_profile_id,
):
    driver = get_driver(park_id, contractor_profile_id)

    response = await taxi_driver_profiles.delete(
        ENDPOINT,
        params=_make_params(park_id, contractor_profile_id),
        json=DEFAULT_REQUEST,
    )
    assert response.status_code == 404
    assert driver is None
