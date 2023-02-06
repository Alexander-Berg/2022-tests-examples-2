async def test_sample_v1_action_put(taxi_eats_api_coverage_test):
    response = await taxi_eats_api_coverage_test.put(
        'sample/v1/action', json={'id': '1', 'action': 'standing'},
    )
    assert response.status_code == 200


async def test_v1_pay(taxi_eats_api_coverage_test):
    response = await taxi_eats_api_coverage_test.post('v1/pay/shipper')
    assert response.status_code == 200

    response = await taxi_eats_api_coverage_test.post('v1/pay/carrier')
    assert response.status_code == 200

    response = await taxi_eats_api_coverage_test.post('v1/pay/some')
    assert response.status_code == 200
