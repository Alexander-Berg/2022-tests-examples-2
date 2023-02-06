CONFIGS_VALUES_URL = 'configs/values'


async def test_bad(taxi_uconfigs):
    response = await taxi_uconfigs.post(CONFIGS_VALUES_URL, json={})
    assert response.status_code == 200
    assert 'BAD' not in response.json()['configs']
