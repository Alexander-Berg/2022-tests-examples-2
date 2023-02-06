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


def _get_shown_tooltips(udid, pgsql):
    cursor = pgsql['driver-tutorials'].cursor()
    cursor.execute(
        f"""
        SELECT
            tooltip_id
        FROM driver_tutorials.shown_tooltips
        WHERE
            unique_driver_id='{udid}'
        ;""",
    )
    return {item[0] for item in cursor.fetchall()}


@pytest.mark.now('2019-10-08T12:00:00+0300')
@pytest.mark.pgsql('driver-tutorials', files=[])
async def test_shown_tooltips_post(
        taxi_driver_tutorials, unique_drivers, pgsql,
):
    shown_tooltips = ['tooltip_1', 'tooltip_2', 'tooltip_3']
    response = await taxi_driver_tutorials.post(
        'v1/driver/shown-tooltips',
        params=PARAMS,
        headers=HEADERS,
        json={'shown_tooltips': shown_tooltips},
    )
    assert response.status_code == 200
    assert response.json() == {}
    found_shown_tooltips = _get_shown_tooltips('driver_unique_1', pgsql)
    assert set(shown_tooltips) == found_shown_tooltips


@pytest.mark.now('2019-10-08T12:00:00+0300')
@pytest.mark.pgsql('driver-tutorials', files=['shown_tooltips.sql'])
@pytest.mark.config(DRIVER_TUTORIALS_ALLOWED_TOOLTIPS=['allowed_tooltip'])
@pytest.mark.parametrize(
    ('shown_tooltips', 'response_code'),
    [
        (['allowed_tooltip'], 200),
        (['allowed_tooltip', 'not_allowed_tooltip'], 400),
        (['allowed_tooltip', 'allowed_tooltip'], 400),
    ],
)
async def test_shown_tooltips_post_get_allowed(
        taxi_driver_tutorials,
        shown_tooltips,
        response_code,
        unique_drivers,
        pgsql,
):
    response = await taxi_driver_tutorials.post(
        'v1/driver/shown-tooltips',
        params=PARAMS,
        headers=HEADERS,
        json={'shown_tooltips': shown_tooltips},
    )
    assert response.status_code == response_code
    if response_code == 200:
        assert response.json() == {}
        found_shown_tooltips = _get_shown_tooltips('driver_unique_1', pgsql)
        assert set(shown_tooltips).issubset(found_shown_tooltips)


@pytest.mark.now('2019-10-08T12:00:00+0300')
@pytest.mark.pgsql('driver-tutorials', files=['shown_tooltips.sql'])
async def test_shown_tooltips_post_no_unique_id(
        taxi_driver_tutorials, mockserver,
):
    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _mock_not_found(request):
        return {'uniques': [{'park_driver_profile_id': 'park_1_driver_1'}]}

    response = await taxi_driver_tutorials.post(
        'v1/driver/shown-tooltips',
        params=PARAMS,
        headers=HEADERS,
        json={'shown_tooltips': ['tooltip_1']},
    )
    assert response.status_code == 409
    assert response.json() == {'code': '409', 'message': 'Retry later'}
    assert _mock_not_found.times_called == 1
