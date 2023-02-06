# pylint: disable=import-error,too-many-lines

import pytest


@pytest.mark.now('2019-09-11T13:42:15+0300')
async def test_pipline_wrong_pipeline(taxi_yagr_adv, redis_store, testpoint):
    park_id = 'sberty'
    driver_id = 'sqwerty1'
    params = {'pipeline': 'unknown', 'uuid': f'{park_id}_{driver_id}'}
    data_args = {'positions': []}

    response = await taxi_yagr_adv.post(
        '/v2/position/store',
        params=params,
        json=data_args,
        headers={'X-YaFts-Client-Service-Tvm': '123'},
    )
    assert response.status_code == 404
