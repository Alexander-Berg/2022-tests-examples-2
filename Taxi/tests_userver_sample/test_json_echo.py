# -*- coding: utf-8 -*-
async def test_json_echo(taxi_userver_sample):
    params = {'привет': 'мир'}
    response = await taxi_userver_sample.post('json-echo', json=params)
    assert response.status_code == 200
    assert (
        response.headers['content-type'] == 'application/json; charset=utf-8'
    )
    assert response.encoding == 'utf-8'
    assert response.json() == params
