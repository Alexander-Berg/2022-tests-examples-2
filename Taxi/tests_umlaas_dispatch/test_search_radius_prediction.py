import pytest

URL = '/umlaas-dispatch/v1/search-radius-prediction'
USER_ID = 'user_id'

PA_HEADERS = {
    'X-YaTaxi-UserId': USER_ID,
    'X-Yandex-UID': '4003514353',
    'X-YaTaxi-PhoneId': '5714f45e98956f06baaae3d4',
}


@pytest.mark.experiments3(filename='model_experiment.json')
@pytest.mark.experiments3(filename='scaling_experiment.json')
@pytest.mark.experiments3(filename='quantile_experiment.json')
@pytest.mark.config(
    ROUTE_RETRIES=1,
    ROUTER_SELECT=[
        {'routers': ['linear-fallback', 'yamaps', 'yamaps-matrix']},
    ],
)
async def test_ml_api(taxi_umlaas_dispatch, load_json):
    request = load_json('request.json')
    response = await taxi_umlaas_dispatch.post(
        URL, request, headers=PA_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json('expected_response.json')


@pytest.mark.experiments3(filename='model_experiment.json')
@pytest.mark.experiments3(filename='scaling_experiment_min_time.json')
@pytest.mark.config(
    ROUTE_RETRIES=1,
    ROUTER_SELECT=[
        {'routers': ['linear-fallback', 'yamaps', 'yamaps-matrix']},
    ],
)
async def test_ml_candidate_choice(taxi_umlaas_dispatch, load_json):
    request = load_json('request.json')
    response = await taxi_umlaas_dispatch.post(
        URL, request, headers=PA_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json('expected_response_min_time.json')


@pytest.mark.experiments3(filename='model_experiment.json')
@pytest.mark.experiments3(filename='scaling_experiment_expand.json')
@pytest.mark.config(
    ROUTE_RETRIES=1,
    ROUTER_SELECT=[
        {'routers': ['linear-fallback', 'yamaps', 'yamaps-matrix']},
    ],
)
async def test_ml_exploration(taxi_umlaas_dispatch, load_json):
    request = load_json('request.json')
    response = await taxi_umlaas_dispatch.post(
        URL, request, headers=PA_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json('expected_response_exploration.json')
