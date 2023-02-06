# pylint: disable=import-only-modules
# pylint: disable=redefined-outer-name
# flake8: noqa: F401, F811

import pytest


@pytest.mark.parametrize(
    ['test_data_json'],
    [('test_data_if_success.json',), ('test_data_if_failed.json',)],
)
@pytest.mark.parametrize(
    'exp_name',
    [
        pytest.param(
            'fallback_enabled',
            marks=(
                pytest.mark.client_experiments3(
                    file_with_default_response='exp3_fallback_enabled.json',
                ),
            ),
        ),
        pytest.param(
            'fallback_disabled',
            marks=(
                pytest.mark.client_experiments3(
                    file_with_default_response='exp3_fallback_disabled.json',
                ),
            ),
        ),
    ],
)
async def test_get_tariff_category(
        web_app_client,
        cache_shield,
        tariffs_context,
        individual_tariffs_mockserver,
        test_data_json,
        exp_name,
        load_json,
):
    test_data = load_json(test_data_json)
    tariff_category_id = test_data['tariff_category_id']
    expected_status = test_data['expected_status']
    expected_data = test_data['expected_data']
    individual_tariffs_response = test_data['individual_tariffs_response']

    if test_data_json == 'test_data_if_failed.json':
        tariffs_context.set_error(404, individual_tariffs_response)
    else:
        tariffs_context.set_tariffs(individual_tariffs_response)

    response = await web_app_client.get(
        '/v2/tariff/by_category', params={'category_id': tariff_category_id},
    )
    data = await response.json()

    assert response.status == expected_status
    assert data == expected_data
