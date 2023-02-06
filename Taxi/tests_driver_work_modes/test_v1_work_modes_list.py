import pytest


ENDPOINT_URL = 'v1/work-modes/list'


@pytest.mark.config(TVM_ENABLED=False)
@pytest.mark.parametrize(
    'park_id, driver_profile_id, is_driver_fix_enabled',
    [
        ('park1', 'driver1', True),
        ('park1', 'driver2', False),
        ('park1', 'driver3', False),
        ('park3', 'driver6', False),
    ],
)
async def test_ok(
        taxi_driver_work_modes,
        driver_profiles,
        driver_work_rules,
        mock_fleet_parks_list,
        park_id,
        driver_profile_id,
        is_driver_fix_enabled,
):
    response = await taxi_driver_work_modes.get(
        ENDPOINT_URL,
        params={'park_id': park_id, 'driver_profile_id': driver_profile_id},
    )

    assert mock_fleet_parks_list.times_called == 0
    assert response.status_code == 200, response.text
    assert response.json() == {
        'work_modes': [
            {'id': 'orders', 'is_enabled': True},
            {'id': 'driver_fix', 'is_enabled': is_driver_fix_enabled},
        ],
    }


@pytest.mark.parametrize(
    'park_id,driver_profile_id',
    [('not_existed_park_id', 'driver1'), ('park1', 'not_existed_driver_id')],
)
async def test_not_found(
        taxi_driver_work_modes,
        driver_profiles,
        driver_work_rules,
        park_id,
        driver_profile_id,
):
    response = await taxi_driver_work_modes.get(
        ENDPOINT_URL,
        params={'park_id': park_id, 'driver_profile_id': driver_profile_id},
    )

    assert response.status_code == 404
    assert response.json() == {
        'code': 'driver_not_found',
        'message': 'Driver not found',
    }


@pytest.mark.config(DRIVER_WORK_MODES_ENABLE_DRIVER_FIX_FOR_INDIVIDUALS=True)
async def test_driver_fix_mode_for_ie_park_not_found(
        taxi_driver_work_modes,
        driver_profiles,
        driver_work_rules,
        mock_fleet_parks_list,
        mockserver,
):
    response = await taxi_driver_work_modes.get(
        ENDPOINT_URL,
        params={'park_id': 'invalid_park_id', 'driver_profile_id': 'driver1'},
    )

    assert mock_fleet_parks_list.times_called == 1
    assert driver_work_rules.has_calls() == 0
    assert response.status_code == 404, response.text
    assert response.json() == {'code': '404', 'message': 'Park not found'}


@pytest.mark.config(DRIVER_WORK_MODES_ENABLE_DRIVER_FIX_FOR_INDIVIDUALS=True)
@pytest.mark.parametrize(
    'park_id, driver_profile_id, has_dwr_called, is_driver_fix_enabled',
    [
        (
            # according to the responses
            # driver works in work rule with is_driver_fix_enabled == true and
            # fleet-parks park is individual entrepreneur
            'park2',
            'driver1',
            False,
            True,
        ),
        (
            # according to the responses
            # driver works in work rule with is_driver_fix_enabled == false and
            # fleet-parks park is individual entrepreneur
            'park2',
            'driver2',
            False,
            True,
        ),
        (
            # according to the responses
            # driver has absent work-rule
            'park3',
            'driver6',
            False,
            False,
        ),
        (
            # according to the responses
            # driver works in work rule with is_driver_fix_enabled == false and
            # fleet-parks park is not individual entrepreneur
            'park3',
            'driver7',
            True,
            False,
        ),
    ],
)
async def test_driver_fix_mode_for_ie_ok(
        taxi_driver_work_modes,
        driver_profiles,
        driver_work_rules,
        mock_fleet_parks_list,
        mockserver,
        park_id,
        driver_profile_id,
        has_dwr_called,
        is_driver_fix_enabled,
):
    response = await taxi_driver_work_modes.get(
        ENDPOINT_URL,
        params={'park_id': park_id, 'driver_profile_id': driver_profile_id},
    )

    assert mock_fleet_parks_list.times_called == 1
    assert driver_work_rules.has_calls() == has_dwr_called
    assert response.status_code == 200, response.text
    assert response.json() == {
        'work_modes': [
            {'id': 'orders', 'is_enabled': True},
            {'id': 'driver_fix', 'is_enabled': is_driver_fix_enabled},
        ],
    }
