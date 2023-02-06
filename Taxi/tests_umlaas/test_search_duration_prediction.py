import pytest

URL = '/umlaas/v1/search-duration-prediction'

PA_HEADERS = {
    'X-YaTaxi-UserId': 'user_id',
    'X-Yandex-UID': '4003514353',
    'X-YaTaxi-PhoneId': '5714f45e98956f06baaae3d4',
}


@pytest.mark.experiments3(filename='umlaas_search_duration_prediction.json')
async def test_static_predictor(taxi_umlaas, load_json):
    request = load_json('request.json')
    response = await taxi_umlaas.post(URL, request, headers=PA_HEADERS)
    assert response.status_code == 200
    assert response.json()['duration'] == 1
