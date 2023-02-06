import pytest

from tests_driver_diagnostics import utils


@pytest.mark.parametrize(
    'exclude_not_allowed_categories, details, expected_response',
    [
        (
            False,
            {
                'efficiency/fetch_tags_classes': ['econom by tags: tag1'],
                'infra/fetch_profile_classes': ['business by req: req1'],
            },
            'ui_all_categories_blocked.json',
        ),
        (
            False,
            {
                'efficiency/fetch_tags_classes': [
                    'econom by tags: unknown_tag',
                ],
                'infra/fetch_profile_classes': ['business by req: req1'],
            },
            'ui_unknown_or_hidden_tag.json',
        ),
        (
            False,
            {
                'efficiency/fetch_tags_classes': [
                    'econom by tags: hidden_reason_tag',
                ],
                'infra/fetch_profile_classes': ['business by req: req1'],
            },
            'ui_unknown_or_hidden_tag.json',
        ),
        (
            False,
            {
                'efficiency/fetch_tags_classes': [
                    'econom by tags: unknown_tag',
                ],
                'infra/fetch_profile_classes': ['business by req: req1'],
                'infra/fetch_categories': ['child_tariff by childchairs'],
            },
            'ui_no_requested_category.json',
        ),
        (
            False,
            {
                'efficiency/fetch_tags_classes': ['econom by tags: tag1'],
                'infra/fetch_profile_classes': ['business by req: req1'],
                'infra/fetch_categories': ['child_tariff by childchairs'],
            },
            'ui_all_categories_blocked.json',
        ),
        (
            True,
            {
                'efficiency/fetch_tags_classes': ['econom by tags: tag1'],
                'infra/fetch_profile_classes': ['business by req: req1'],
                'infra/fetch_categories': ['child_tariff by childchairs'],
            },
            'ui_all_categories_blocked.json',
        ),
    ],
)
@pytest.mark.experiments3(filename='diagnostics_categories_block.json')
async def test_driver_ui_restrictions_all_categories_block(
        taxi_driver_diagnostics,
        mock_fleet_parks_list,
        candidates,
        driver_categories_api,
        load_json,
        taxi_config,
        exclude_not_allowed_categories,
        details,
        expected_response,
):
    taxi_config.set_values(
        {
            'DRIVER_DIAGNOSTICS_EXCLUDE_NOT_ALLOWED_CATEGORIES': (
                exclude_not_allowed_categories
            ),
        },
    )

    candidates.set_response_reasons({}, details)
    driver_categories_api.set_categories(['econom', 'business'])

    response = await taxi_driver_diagnostics.post(
        'driver/v1/driver-diagnostics/v1/ui/restrictions',
        headers=utils.get_auth_headers(),
        json=utils.get_default_body(),
    )
    assert response.status_code == 200
    assert response.json() == load_json(expected_response)
