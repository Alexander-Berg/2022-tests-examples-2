import pytest

URL = '/umlaas/v1/logistics-performer-availability'


@pytest.mark.experiments3(filename='experiment_exploration_config.json')
@pytest.mark.experiments3(filename='experiment_params.json')
@pytest.mark.experiments3(filename='experiment_model.json')
async def test_ml_test_exploration(taxi_umlaas, load_json):
    request = load_json('request.json')
    response = await taxi_umlaas.post(URL, request)
    assert response.status_code == 200
    assert response.json()['performer_available'] is True


@pytest.mark.experiments3(filename='experiment_exploitation_config.json')
@pytest.mark.experiments3(filename='experiment_params.json')
@pytest.mark.experiments3(filename='experiment_model.json')
async def test_ml_test_predictor(taxi_umlaas, load_json):
    request = load_json('request.json')
    response = await taxi_umlaas.post(URL, request)
    assert response.status_code == 200
    assert response.json()['performer_available'] is False


@pytest.mark.experiments3(filename='experiment_exploration_config.json')
@pytest.mark.experiments3(filename='experiment_params.json')
@pytest.mark.experiments3(filename='experiment_model.json')
async def test_custom_features(taxi_umlaas, load_json):
    request = load_json('request_w_custom_features.json')
    response = await taxi_umlaas.post(URL, request)
    assert response.status_code == 200
    assert response.json()['performer_available'] is True


@pytest.mark.experiments3(filename='experiment_heuristic_config.json')
async def test_food_catalog_heuristic(taxi_umlaas, load_json):
    request = load_json('request_zone.json')
    response = await taxi_umlaas.post(URL, request)
    assert response.status_code == 200
    assert response.json()['performer_available'] is True
