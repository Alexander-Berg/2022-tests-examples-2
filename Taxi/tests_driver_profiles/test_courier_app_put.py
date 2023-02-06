import pytest


ENDPOINT = '/v1/profile/courier-app'

PARK_ID = 'park1'


@pytest.mark.parametrize(
    ('driver_profile_id', 'courier_app', 'expected_code'),
    [
        ('driver1', 'taximeter', 200),
        ('driver666', 'taximeter', 404),
        ('driver1', 'wrong_app', 400),
    ],
)
async def test_courier_app_set(
        taxi_driver_profiles,
        mockserver,
        mongodb,
        driver_profile_id,
        courier_app,
        expected_code,
):
    def _get_driver():
        return mongodb.dbdrivers.find_one(
            dict(park_id=PARK_ID, driver_id=driver_profile_id),
            {'courier_app'},
        )

    author = dict(consumer='qc', identity=dict(type='job', job_name='updater'))
    request_body = dict(author=author, courier_app=courier_app)

    response = await taxi_driver_profiles.put(
        ENDPOINT,
        params=dict(park_id=PARK_ID, driver_profile_id=driver_profile_id),
        json=request_body,
    )
    assert response.status_code == expected_code

    if expected_code == 200:
        driver = _get_driver()
        assert driver['courier_app'] == courier_app
