import pytest


@pytest.mark.parametrize(
    'driver_profile_id,park_id,is_driver_in_db,expected_triggers',
    [
        ('dpid1', 'pid0', False, []),
        ('dpid2', 'pid2', True, []),
        ('dpid3', 'pid3', True, []),
        ('dpid1', 'pid1', True, ['trigger1', 'trigger8']),
        ('dpid4', 'pid4', False, []),
        ('dpid5', 'pid5', True, ['trigger7']),
    ],
)
@pytest.mark.pgsql(
    'contractor_statistics_view',
    files=['insert_in_triggers_and_contractors.sql'],
)
@pytest.mark.config(CONTRACTOR_STATISTICS_VIEW_INITIALIZE_ENABLED=True)
async def test_api_active_triggers(
        stq,
        taxi_contractor_statistics_view,
        driver_profile_id,
        park_id,
        is_driver_in_db,
        expected_triggers,
):

    headers = {
        'User-Agent': 'Taximeter 9.1 (1234)',
        'Accept-Language': 'ru',
        'X-Request-Application-Version': '9.1',
        'X-YaTaxi-Driver-Profile-Id': driver_profile_id,
        'X-YaTaxi-Park-Id': park_id,
    }
    response = await taxi_contractor_statistics_view.post(
        'driver/v1/contractor-statistics-view/v1/active_triggers',
        headers=headers,
    )

    assert stq.contractor_statistics_view_initialize.times_called != int(
        is_driver_in_db,
    )
    assert response.status_code == 200
    assert response.json()['triggers'] == expected_triggers
