import pytest

from tests_driver_diagnostics import utils


@pytest.mark.parametrize(
    'dp_reasons,candidates_reasons,expected_response',
    [
        (
            {'need_childchair_photos': []},
            {
                'infra/fetch_categories': [
                    'child_tariff by confirmed_childchairs',
                ],
            },
            'ui_childchairs.json',
        ),
        (
            {},
            {
                'infra/fetch_categories': [
                    'child_tariff by confirmed_childchairs',
                ],
            },
            'ui_nested_screens_all_good.json',
        ),
        (
            {'need_childchair_photos': []},
            {},
            'ui_nested_screens_all_good.json',
        ),
        (
            {'need_childchair_photos': []},
            {'infra/fetch_categories': ['econom by category_blocked']},
            'ui_econom_category_blocked.json',
        ),
    ],
)
@pytest.mark.experiments3(filename='diagnostics_dkb_childchairs.json')
async def test_driver_ui_restrictions_dkb_childchairs(
        taxi_driver_diagnostics,
        mock_fleet_parks_list,
        candidates,
        driver_profiles,
        driver_protocol,
        load_json,
        candidates_reasons,
        dp_reasons,
        driver_categories_api,
        expected_response,
):
    driver_categories_api.set_categories(
        ['econom', 'comfortplus', 'business', 'child_tariff'],
    )
    candidates.set_response_reasons(candidates_reasons, {})
    driver_protocol.set_driver_blocks(dp_reasons, {})

    response = await taxi_driver_diagnostics.post(
        'driver/v1/driver-diagnostics/v1/ui/restrictions',
        headers=utils.get_auth_headers(),
        json=utils.get_default_body(),
    )
    assert response.status_code == 200
    assert response.json() == load_json(expected_response)


@pytest.mark.parametrize(
    'requested_categories, exclude_not_allowed_categories, details, '
    'expected_response',
    [
        (['econom'], False, {}, 'ui_empty.json'),
        (
            ['econom'],
            False,
            {'infra/fetch_categories': ['child_tariff by childchairs']},
            'ui_need_childchairs.json',
        ),
        (
            ['econom', 'child_tariff'],
            False,
            {'infra/fetch_categories': ['child_tariff by childchairs']},
            'ui_need_childchairs.json',
        ),
        (['econom'], True, {}, 'ui_empty.json'),
        (
            ['econom'],
            True,
            {'infra/fetch_categories': ['child_tariff by childchairs']},
            'ui_empty.json',
        ),
        (
            ['econom', 'child_tariff'],
            True,
            {'infra/fetch_categories': ['child_tariff by childchairs']},
            'ui_need_childchairs.json',
        ),
    ],
)
@pytest.mark.experiments3(filename='diagnostics_childchairs.json')
async def test_driver_ui_restrictions_childchairs(
        taxi_driver_diagnostics,
        mock_fleet_parks_list,
        candidates,
        driver_profiles,
        driver_categories_api,
        load_json,
        taxi_config,
        requested_categories,
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
    driver_categories_api.set_categories(requested_categories)

    response = await taxi_driver_diagnostics.post(
        'driver/v1/driver-diagnostics/v1/ui/restrictions',
        headers=utils.get_auth_headers(),
        json=utils.get_default_body(),
    )
    assert response.status_code == 200
    assert response.json() == load_json(expected_response)
