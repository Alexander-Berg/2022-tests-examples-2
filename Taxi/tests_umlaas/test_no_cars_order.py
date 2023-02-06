import pytest

URL = '/umlaas/v1/no-cars-order'
USER_ID = 'user_id'

PA_HEADERS = {
    'X-YaTaxi-UserId': USER_ID,
    'X-Yandex-UID': '4003514353',
    'X-YaTaxi-PhoneId': '5714f45e98956f06baaae3d4',
}


@pytest.mark.experiments3(filename='experiment_config.json')
@pytest.mark.experiments3(filename='experiment_model_version.json')
async def test_ml_test_api(taxi_umlaas, load_json):
    request = load_json('request.json')
    response = await taxi_umlaas.post(URL, request, headers=PA_HEADERS)
    assert response.status_code == 200
    expected_response = load_json('expected_response.json')
    tariff_set = set()
    for expected_verdict in expected_response['verdicts']:
        tariff_set.add(expected_verdict['tariff_class'])

    for verdict in response.json()['verdicts']:
        assert verdict['tariff_class'] in tariff_set
        assert verdict['no_cars_order_permitted'] is False
        assert verdict['paid_supply_permitted'] is True
