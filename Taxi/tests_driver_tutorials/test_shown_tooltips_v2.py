import pytest

PARK_ID = 'park_1'
DRIVER_ID = 'driver_1'
PARAMS = {'park_id': PARK_ID}


HEADERS = {
    'X-YaTaxi-Park-Id': PARK_ID,
    'X-YaTaxi-Driver-Profile-Id': DRIVER_ID,
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.10 (228)',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
}


@pytest.mark.now('2019-10-08T12:00:00+0300')
@pytest.mark.pgsql('driver-tutorials', files=['shown_tooltips.sql'])
async def test_shown_tooltips_v2_get(taxi_driver_tutorials, unique_drivers):
    shown_tooltips = ['tooltip_1', 'tooltip_2', 'tooltip_3']
    response = await taxi_driver_tutorials.get(
        'driver/v1/tutorials/v2/shown-tooltips',
        params=PARAMS,
        headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {
        'shown_tooltips': [
            {'id': tooltip, 'first_shown_at': '2019-10-08T09:00:00+00:00'}
            for tooltip in shown_tooltips
        ],
    }


@pytest.mark.now('2019-10-08T12:00:00+0300')
@pytest.mark.pgsql('driver-tutorials', files=['shown_tooltips.sql'])
async def test_shown_tooltips_v2_get_no_unique_id(
        taxi_driver_tutorials, mockserver,
):
    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _mock_not_found(request):
        return {'uniques': [{'park_driver_profile_id': 'park_1_driver_1'}]}

    response = await taxi_driver_tutorials.get(
        'driver/v1/tutorials/v2/shown-tooltips',
        params=PARAMS,
        headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {'shown_tooltips': []}
    assert _mock_not_found.times_called == 1
