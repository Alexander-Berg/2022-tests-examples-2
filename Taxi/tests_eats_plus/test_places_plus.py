import pytest


@pytest.mark.config(
    EATS_PLUS_SETTINGS_UPDATE_TASK_CONFIGS={
        'enabled': False,
        'update_period_ms': 5,
    },
)
async def test_places_plus(taxi_eats_plus):
    place_ids = [1, 2, 3]
    await taxi_eats_plus.invalidate_caches()

    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/places_plus', json={'place_ids': place_ids},
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'places': [
            {'has_plus': False, 'place_id': 1, 'place_part': 10.0},
            {'has_plus': True, 'place_id': 2, 'place_part': 12.0},
            {'has_plus': False, 'place_id': 3},
        ],
    }
