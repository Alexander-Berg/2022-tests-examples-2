import pytest

from tests_driver_diagnostics import utils


@pytest.mark.parametrize(
    'expected_response,reasons,details',
    [
        (
            'ui_multiple_block_reasons.json',
            {
                'infra/fetch_profile_classes': [],
                'infra/fetch_final_classes': [],
            },
            {
                'partners/fetch_exams_classes': [
                    'econom by exams: exam1, exam2',
                ],
                'efficiency/fetch_tags_classes': [
                    'econom by tags: tag1, tag2, hidden_reason_tag',
                ],
                'infra/fetch_profile_classes': ['econom by grade'],
            },
        ),
        (
            'ui_single_reason_no_pre_screen.json',
            {},
            {'efficiency/fetch_tags_classes': ['econom by tags: tag1']},
        ),
        (
            'ui_single_reason_pre_screen.json',
            {},
            {
                'partners/fetch_license_experience_classes': [
                    'econom by experience',
                ],
                'efficiency/fetch_tags_classes': [
                    'econom by tags: hidden_reason_tag',
                ],
            },
        ),
        ('ui_category_available.json', {}, {}),
    ],
)
@pytest.mark.experiments3(filename='diagnostics_classes_block.json')
async def test_driver_ui_category(
        taxi_driver_diagnostics,
        mock_fleet_parks_list,
        candidates,
        driver_categories_api,
        load_json,
        expected_response,
        details,
        reasons,
):
    candidates.set_response_reasons(reasons, details)
    driver_categories_api.set_categories(
        ['econom', 'comfortplus', 'business', 'ultimate'],
    )

    response = await taxi_driver_diagnostics.post(
        'driver/v1/driver-diagnostics/v1/ui/restrictions/category',
        headers=utils.get_auth_headers(),
        json={
            'position': {'lon': 37.590533, 'lat': 55.733863},
            'client_reasons': [],
            'category': 'econom',
        },
    )
    assert response.status_code == 200
    assert response.json() == load_json(expected_response)


@pytest.mark.parametrize(
    'expected_response,reasons,details,position',
    [
        (
            'ui_category_coordinates_not_found.json',
            {},
            {},
            {'lon': 0, 'lat': 0},
        ),
        ('ui_category_zone_not_found.json', {}, {}, {'lon': 10, 'lat': 20}),
    ],
)
@pytest.mark.experiments3(filename='diagnostics_classes_block.json')
async def test_driver_ui_coordinates_or_zone_not_found(
        taxi_driver_diagnostics,
        mock_fleet_parks_list,
        candidates,
        driver_categories_api,
        load_json,
        expected_response,
        details,
        reasons,
        position,
):
    candidates.set_response_reasons({}, {})
    driver_categories_api.set_categories(
        ['econom', 'comfortplus', 'business', 'ultimate'],
    )

    response = await taxi_driver_diagnostics.post(
        'driver/v1/driver-diagnostics/v1/ui/restrictions/category',
        headers=utils.get_auth_headers(),
        json={
            'position': position,
            'client_reasons': [],
            'category': 'econom',
        },
    )
    assert response.status_code == 200
    assert response.json() == load_json(expected_response)
