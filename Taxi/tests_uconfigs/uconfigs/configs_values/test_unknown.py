CONFIGS_VALUES_URL = 'configs/values'


async def test_unknown(taxi_uconfigs):
    request_body = {'ids': ['UNKNOWN_CONFIG_1', 'UNKNOWN_CONFIG_2']}
    response = await taxi_uconfigs.post(CONFIGS_VALUES_URL, json=request_body)
    assert response.status_code == 200
    assert response.json() == {
        'configs': {},
        'updated_at': '2018-08-24T18:36:00.15Z',
        'not_found': ['UNKNOWN_CONFIG_1', 'UNKNOWN_CONFIG_2'],
    }
