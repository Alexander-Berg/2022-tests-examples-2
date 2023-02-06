import pytest


@pytest.mark.config(
    CANDIDATES_FEATURE_SWITCHES={
        'empty_classes_for_unknown_zones': True,
        'use_empty_classes_check': True,
    },
)
async def test_unknown_zone_error(taxi_candidates):
    body = {
        'limit': 3,
        'zone_id': 'not_actual_zone',
        'point': [55, 35],
        'need_route_path': True,
    }
    response = await taxi_candidates.post('order-search', json=body)
    assert response.status_code == 400


@pytest.mark.config(
    CANDIDATES_FEATURE_SWITCHES={
        'empty_classes_for_unknown_zones': False,
        'use_empty_classes_check': True,
    },
)
async def test_unknown_zone_off(taxi_candidates):
    body = {
        'limit': 3,
        'zone_id': 'not_actual_zone',
        'point': [55, 35],
        'need_route_path': True,
    }
    response = await taxi_candidates.post('order-search', json=body)
    assert response.status_code == 200
