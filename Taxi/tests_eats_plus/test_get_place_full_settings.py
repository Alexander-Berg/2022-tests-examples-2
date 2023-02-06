import pytest


@pytest.mark.suspend_periodic_tasks('clean-plus-settings')
@pytest.mark.config(
    EATS_PLUS_SETTINGS_UPDATE_TASK_CONFIGS={
        'enabled': False,
        'update_period_ms': 100,
    },
)
@pytest.mark.parametrize(
    'place_id, expected_response, expected_code',
    [
        (
            1,
            {
                'active': True,
                'eda_cashback': [
                    {
                        'active_from': '2020-11-25T15:43:00+00:00',
                        'active_till': '2020-12-01T15:43:00+00:00',
                        'cashback': 5.0,
                    },
                ],
                'place_cashback': [
                    {
                        'active_from': '2020-11-25T15:43:00+00:00',
                        'active_till': '2020-12-01T15:43:00+00:00',
                        'cashback': 10.0,
                    },
                    {
                        'active_from': '2020-12-01T15:43:00+00:00',
                        'cashback': 7.0,
                    },
                ],
                'place_id': 1,
            },
            200,
        ),
        (
            2,
            {
                'active': False,
                'eda_cashback': [
                    {
                        'active_from': '2020-11-25T15:43:00+00:00',
                        'cashback': 5.0,
                    },
                ],
                'place_cashback': [
                    {
                        'active_from': '2020-11-25T15:43:00+00:00',
                        'cashback': 10.0,
                    },
                ],
                'place_id': 2,
            },
            200,
        ),
        (404, None, 404),
    ],
)
@pytest.mark.now('2020-11-26T00:00:00.000000Z')
async def test_cashback_get_place_full_settings(
        taxi_eats_plus,
        place_id,
        expected_response,
        expected_code,
        passport_blackbox,
):
    passport_blackbox()
    await taxi_eats_plus.invalidate_caches()
    response = await taxi_eats_plus.post(
        '/internal/eats-plus/v1/place/cashback', json={'place_id': place_id},
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        response = response.json()
        assert response == expected_response
