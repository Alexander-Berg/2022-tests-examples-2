import pytest

URL = '/umlaas-dispatch/v1/personal-conversion'
USER_ID = 'user_id'

PA_HEADERS = {
    'X-YaTaxi-UserId': USER_ID,
    'X-Yandex-UID': '4003514353',
    'X-YaTaxi-PhoneId': '5714f45e98956f06baaae3d4',
}


@pytest.mark.experiments3(filename='no_exploration_experiment.json')
@pytest.mark.experiments3(filename='model_params_experiment.json')
@pytest.mark.experiments3(filename='model_type_experiment.json')
async def test_ml_api(taxi_umlaas_dispatch, load_json):
    request = load_json('request.json')
    response = await taxi_umlaas_dispatch.post(
        URL, request, headers=PA_HEADERS,
    )
    assert response.status_code == 200
    res = response.json()

    for prediction in res['predictions']:
        assert prediction['verdict'] is False


@pytest.mark.experiments3(filename='exploration_experiment.json')
@pytest.mark.experiments3(filename='model_params_experiment.json')
@pytest.mark.experiments3(filename='model_type_experiment.json')
async def test_exploration(taxi_umlaas_dispatch, load_json):
    request = load_json('request.json')
    response = await taxi_umlaas_dispatch.post(
        URL, request, headers=PA_HEADERS,
    )
    assert response.status_code == 200
    res = response.json()

    for prediction in res['predictions']:
        assert prediction['verdict'] is True


@pytest.mark.experiments3(filename='no_exploration_experiment.json')
@pytest.mark.experiments3(
    filename='model_params_experiment_low_threshold.json',
)
@pytest.mark.experiments3(filename='model_type_experiment.json')
async def test_low_threshold(taxi_umlaas_dispatch, load_json):
    request = load_json('request.json')
    response = await taxi_umlaas_dispatch.post(
        URL, request, headers=PA_HEADERS,
    )
    assert response.status_code == 200
    res = response.json()

    for prediction in res['predictions']:
        assert prediction['verdict'] is True
