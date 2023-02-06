import pytest


DEFAULT_HEADERS = {
    'X-Driver-Session': 'qwerty',
    'Accept-Language': 'en',
    'X-YaTaxi-Park-Id': '777',
    'X-YaTaxi-Driver-Profile-Id': '888',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.77 (456)',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
}


@pytest.mark.now('2020-05-05T00:00:12Z')
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
@pytest.mark.config(
    SUBVENTION_VIEW_MAP_TARIFF_CLASSES=True,
    SUBVENTION_VIEW_GEO_BOOKING_CONSTRAINTS_PRIORITIES=[
        {'name': 'activity', 'priority': 2},
        {'name': 'geoarea', 'priority': 1},
        {'name': 'tariff_classes', 'priority': 0},
    ],
)
async def test_driver_fix_like_restrictions_in_geo_booking(
        mockserver,
        now,
        bss,
        taxi_subvention_view,
        load_json,
        driver_authorizer,
        unique_drivers,
        activity,
        candidates,
        experiments3,
):
    unique_drivers.add_driver('777', '888', 'udid')
    activity.add_driver('udid', 70)
    driver_authorizer.set_session('777', 'qwerty', '888')
    current_point = [37.6, 55.75]

    bss.add_rule(load_json('geo_booking_rule.json'))

    experiments3.add_experiments_json(
        load_json('driver_fix_restrictions_in_geo_booking_experiment.json'),
    )

    candidates_response = load_json('candidates_profiles_response.json')
    candidates_response['point'] = current_point
    candidates.load_profiles(candidates_response)

    subventions_ids = ['_id/subvention_1']

    await taxi_subvention_view.invalidate_caches()

    assert len(current_point) == 2
    lon, lat = current_point

    await taxi_subvention_view.invalidate_caches()
    response = await taxi_subvention_view.get(
        '/v1/status?'
        'lon={}&lat={}&subventions_id={}{}'.format(
            lon, lat, ','.join(subventions_ids), '&order_id=',
        ),
        headers=DEFAULT_HEADERS,
    )

    assert response.status_code == 200
    response = response.json()

    assert response == load_json('expected_response_geo_booking.json')
