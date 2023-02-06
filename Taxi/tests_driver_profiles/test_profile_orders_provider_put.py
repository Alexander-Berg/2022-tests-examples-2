import pytest


ENDPOINT = '/v1/profile/orders_provider'

PARK_ID = 'park1'


@pytest.mark.parametrize(
    ('driver_profile_id', 'orders_provider', 'courier_app', 'expected_code'),
    [
        (
            'driver1',
            {
                'cargo': False,
                'eda': True,
                'lavka': False,
                'taxi': True,
                'taxi_walking_courier': False,
                'retail': False,
            },
            None,
            200,
        ),
        (
            'driver1',
            {
                'cargo': False,
                'eda': True,
                'lavka': False,
                'taxi': True,
                'taxi_walking_courier': False,
                'retail': False,
            },
            'taximeter',
            200,
        ),
        (
            'driver666',
            {
                'cargo': False,
                'eda': True,
                'lavka': False,
                'taxi': True,
                'taxi_walking_courier': False,
                'retail': False,
            },
            'taximeter',
            404,
        ),
        ('driver1', {'eda': True}, 'taximeter', 400),
        (
            'driver1',
            {
                'cargo': False,
                'eda': True,
                'lavka': False,
                'taxi': True,
                'taxi_walking_courier': False,
                'retail': False,
            },
            'wrong_app',
            400,
        ),
    ],
)
async def test_courier_orders_provider(
        taxi_driver_profiles,
        mockserver,
        mongodb,
        driver_profile_id,
        orders_provider,
        courier_app,
        expected_code,
):
    def _get_driver():
        return mongodb.dbdrivers.find_one(
            dict(park_id=PARK_ID, driver_id=driver_profile_id),
            {'orders_provider', 'courier_app'},
        )

    author = dict(consumer='qc', identity=dict(type='job', job_name='updater'))
    request_body = dict(author=author, orders_provider=orders_provider)
    if courier_app:
        request_body['courier_app'] = courier_app

    response = await taxi_driver_profiles.put(
        ENDPOINT,
        params=dict(park_id=PARK_ID, driver_profile_id=driver_profile_id),
        json=request_body,
    )
    assert response.status_code == expected_code

    if expected_code == 200:
        driver = _get_driver()
        assert driver['orders_provider'] == orders_provider
        if courier_app:
            assert driver['courier_app'] == courier_app
        else:
            assert 'courier_app' not in driver
