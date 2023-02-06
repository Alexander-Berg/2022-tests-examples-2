CONFIGS_VALUES_URL = 'configs/values'


async def test_empty(taxi_uconfigs):
    response_1 = await taxi_uconfigs.post(CONFIGS_VALUES_URL, json={'ids': []})
    response_2 = await taxi_uconfigs.post(CONFIGS_VALUES_URL, json={})
    assert response_1.status_code == 200
    assert response_2.status_code == 200
    assert response_1.json() == response_2.json()
