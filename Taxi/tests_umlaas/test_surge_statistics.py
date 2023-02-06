import pytest


@pytest.mark.config(SURGE_STATISTICS_ML_PREDICTOR_ENABLED=True)
@pytest.mark.experiments3(
    filename='umlaas_surge_fixed_points_trends_version.json',
)
async def test_ml_test_api(taxi_umlaas, load_json):
    request = load_json('request.json')
    response = await taxi_umlaas.post(
        '/umlaas/v1/surge-statistics', json=request,
    )
    assert response.status_code == 200

    response_by_category = response.json().get('by_category', {})
    expected_by_category = load_json('exp_mock_response.json')['by_category']

    assert response_by_category.keys() == expected_by_category.keys()

    predictions_request_set = set()
    predictions_expected_set = set()
    for _, item in response_by_category.items():
        for result in item['results']:
            predictions_request_set.add(result['name'])

    for _, item in expected_by_category.items():
        for result in item['results']:
            predictions_expected_set.add(result['name'])
    assert predictions_request_set == predictions_expected_set
