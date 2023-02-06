import copy

import pytest

from tests_driver_diagnostics import utils


DEFAULT_JSON = {
    'driver_application': {
        'version_type': '',
        'version': '9.40',
        'platform': 'android',
    },
    'driver_params': {
        'park_id': 'park_id1',
        'driver_profile_id': 'driver_id1',
        'accept_language': 'ru',
    },
    'position': {'lat': 55.744094, 'lon': 37.627920},
    'categories': ['econom', 'business', 'comfortplus'],
}


@pytest.mark.experiments3(filename='diagnostics_categories_restrictions.json')
async def test_driver_categories_restrictions(
        taxi_driver_diagnostics, mock_fleet_parks_list, candidates,
):
    candidates.set_response_reasons(
        {},
        {
            'partners/fetch_exams_classes': ['econom by exams: exam1'],
            'efficiency/fetch_tags_classes': ['business by tags: tag1'],
            'infra/fetch_profile_classes': ['business by requirements: req1'],
            'infra/fetch_final_classes': ['econom, business by final result'],
        },
    )

    response = await taxi_driver_diagnostics.post(
        '/internal/driver-diagnostics/v1/categories/restrictions',
        headers=utils.get_headers(),
        json=DEFAULT_JSON,
    )
    assert response.status_code == 200
    assert response.json() == {
        'categories': [
            {
                'block_ids': ['partners/fetch_exams_classes'],
                'block_reason': 'Экзамены не пройдены',
                'deeplink': 'taximeter://category_diagnostics?category=econom',
                'is_enabled': False,
                'name': 'econom',
            },
            {
                'block_ids': [
                    'efficiency/fetch_tags_classes',
                    'infra/fetch_profile_classes',
                ],
                'block_reason': 'Несколько причин блокировки',
                'deeplink': (
                    'taximeter://category_diagnostics?category=business'
                ),
                'is_enabled': False,
                'name': 'business',
            },
            {'is_enabled': True, 'name': 'comfortplus'},
        ],
    }


@pytest.mark.experiments3(filename='diagnostics_categories_restrictions.json')
@pytest.mark.config(
    DRIVER_DIAGNOSTICS_SKIP_REASONS_FOR_CATEGORIES=[
        'infra/fetch_profile_classes.grade',
    ],
)
async def test_driver_categories_restrictions_skip_unvisible_reasons(
        taxi_driver_diagnostics, mock_fleet_parks_list, candidates,
):
    candidates.set_response_reasons(
        {},
        {
            'efficiency/fetch_tags_classes': [
                'business by tags: tag1, hidden_reason_tag',
            ],
            'infra/fetch_profile_classes': ['business by grade'],
            'partners/fetch_exams_classes': ['econom by exams: exam1'],
        },
    )

    response = await taxi_driver_diagnostics.post(
        '/internal/driver-diagnostics/v1/categories/restrictions',
        headers=utils.get_headers(),
        json=DEFAULT_JSON,
    )
    assert response.status_code == 200
    assert response.json() == {
        'categories': [
            {
                'block_ids': ['partners/fetch_exams_classes'],
                'block_reason': 'Экзамены не пройдены',
                'deeplink': 'taximeter://category_diagnostics?category=econom',
                'is_enabled': False,
                'name': 'econom',
            },
            {
                'block_ids': [
                    'efficiency/fetch_tags_classes',
                    'efficiency/fetch_tags_classes',
                ],
                'block_reason': 'Несколько причин блокировки',
                'deeplink': (
                    'taximeter://category_diagnostics?category=business'
                ),
                'is_enabled': False,
                'name': 'business',
            },
            {'is_enabled': True, 'name': 'comfortplus'},
        ],
    }


@pytest.mark.experiments3(filename='diagnostics_categories_restrictions.json')
async def test_driver_categories_restrictions_zero_coordinates(
        taxi_driver_diagnostics, mock_fleet_parks_list, candidates,
):
    candidates.set_response_reasons(
        {},
        {
            'partners/fetch_exams_classes': ['econom by exams: exam1'],
            'efficiency/fetch_tags_classes': ['business by tags: tag1'],
            'infra/fetch_profile_classes': ['business by requirements: req1'],
            'infra/fetch_final_classes': ['econom, business by final result'],
        },
    )

    zero_coordinate_params = copy.deepcopy(DEFAULT_JSON)
    zero_coordinate_params['position']['lat'] = 0
    zero_coordinate_params['position']['lon'] = 0
    response = await taxi_driver_diagnostics.post(
        '/internal/driver-diagnostics/v1/categories/restrictions',
        headers=utils.get_headers(),
        json=zero_coordinate_params,
    )
    assert response.status_code == 200
    assert response.json() == {
        'categories': [
            {
                'block_ids': ['coordinates_not_found'],
                'block_reason': 'Не смогли определить координаты водителя',
                'deeplink': 'taximeter://category_diagnostics?category=econom',
                'is_enabled': False,
                'name': 'econom',
            },
            {
                'block_ids': ['coordinates_not_found'],
                'block_reason': 'Не смогли определить координаты водителя',
                'deeplink': (
                    'taximeter://category_diagnostics?category=business'
                ),
                'is_enabled': False,
                'name': 'business',
            },
            {
                'block_ids': ['coordinates_not_found'],
                'block_reason': 'Не смогли определить координаты водителя',
                'deeplink': (
                    'taximeter://category_diagnostics?category=comfortplus'
                ),
                'is_enabled': False,
                'name': 'comfortplus',
            },
        ],
    }


@pytest.mark.experiments3(filename='diagnostics_categories_restrictions.json')
async def test_driver_categories_restrictions_zone_not_found(
        taxi_driver_diagnostics, mock_fleet_parks_list, candidates,
):
    candidates.set_response_reasons(
        {},
        {
            'partners/fetch_exams_classes': ['econom by exams: exam1'],
            'efficiency/fetch_tags_classes': ['business by tags: tag1'],
            'infra/fetch_profile_classes': ['business by requirements: req1'],
            'infra/fetch_final_classes': ['econom, business by final result'],
        },
    )

    zero_coordinate_params = copy.deepcopy(DEFAULT_JSON)
    zero_coordinate_params['position']['lat'] = 10
    zero_coordinate_params['position']['lon'] = 20
    response = await taxi_driver_diagnostics.post(
        '/internal/driver-diagnostics/v1/categories/restrictions',
        headers=utils.get_headers(),
        json=zero_coordinate_params,
    )
    assert response.status_code == 200
    assert response.json() == {
        'categories': [
            {
                'block_ids': ['zone_not_found'],
                'block_reason': 'Не смогли определить зону водителя',
                'deeplink': 'taximeter://category_diagnostics?category=econom',
                'is_enabled': False,
                'name': 'econom',
            },
            {
                'block_ids': ['zone_not_found'],
                'block_reason': 'Не смогли определить зону водителя',
                'deeplink': (
                    'taximeter://category_diagnostics?category=business'
                ),
                'is_enabled': False,
                'name': 'business',
            },
            {
                'block_ids': ['zone_not_found'],
                'block_reason': 'Не смогли определить зону водителя',
                'deeplink': (
                    'taximeter://category_diagnostics?category=comfortplus'
                ),
                'is_enabled': False,
                'name': 'comfortplus',
            },
        ],
    }
