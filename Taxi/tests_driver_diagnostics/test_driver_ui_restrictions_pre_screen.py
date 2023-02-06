import pytest

from tests_driver_diagnostics import utils


@pytest.mark.parametrize(
    'reasons, details, expected_response',
    [
        (
            {'some_filter': [], 'partners/deactivated_park': []},
            {},
            'ui_deeplink_pre_screen.json',
        ),
        (
            {},
            {'efficiency/fetch_tags_classes': ['business by tags: tag1']},
            'ui_category_one_reason_without_action.json',
        ),
        (
            {},
            {
                'efficiency/fetch_tags_classes': [
                    'business by tags: tag2',
                    'econom bby tags: hidden_reason_tag',
                ],
            },
            'ui_category_one_reason_with_pre_screen.json',
        ),
        (
            {},
            {
                'efficiency/fetch_tags_classes': [
                    'business by tags: tag1, tag2',
                ],
            },
            'ui_two_category_reasons.json',
        ),
    ],
)
@pytest.mark.experiments3(filename='diagnostics_pre_screen.json')
async def test_driver_ui_restrictions_pre_screen(
        taxi_driver_diagnostics,
        mock_fleet_parks_list,
        candidates,
        driver_categories_api,
        load_json,
        reasons,
        details,
        expected_response,
):
    driver_categories_api.set_categories(
        ['econom', 'comfortplus', 'business', 'child_tariff'],
    )
    candidates.set_response_reasons(reasons, details)

    response = await taxi_driver_diagnostics.post(
        'driver/v1/driver-diagnostics/v1/ui/restrictions',
        headers=utils.get_auth_headers(),
        json=utils.get_default_body(),
    )
    assert response.status_code == 200
    assert response.json() == load_json(expected_response)
