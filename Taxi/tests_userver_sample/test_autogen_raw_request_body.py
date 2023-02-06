import json

import pytest


@pytest.mark.parametrize(
    'request_json',
    [
        pytest.param({}, id='empty json'),
        pytest.param(
            {'param_1': 'value_1', 'param_2': 2}, id='json with data',
        ),
        pytest.param(
            {'param_1': 'value_1', 'param_2': 2, 'extra_param': [1, 2, 3]},
            id='json with extra data',
        ),
    ],
)
async def test_raw_request_json_body(taxi_userver_sample, request_json):
    data = json.dumps(request_json)
    headers = {'content-type': 'application/json'}

    response = await taxi_userver_sample.post(
        '/autogen/raw-request-with-body', data=data, headers=headers,
    )
    assert response.status_code == 200
    assert response.text == data

    response = await taxi_userver_sample.put(
        '/autogen/raw-request-with-body', data=data, headers=headers,
    )
    assert response.status_code == 200
    assert response.text == data

    response = await taxi_userver_sample.patch(
        '/autogen/raw-request-with-body', data=data, headers=headers,
    )
    assert response.status_code == 200
    assert response.text == data


async def test_raw_request_without_body(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        '/autogen/raw-request-without-body',
    )
    assert response.status_code == 200
    assert response.text == ''

    response = await taxi_userver_sample.get(
        '/autogen/raw-request-without-body',
    )
    assert response.status_code == 200
    assert response.text == ''

    response = await taxi_userver_sample.delete(
        '/autogen/raw-request-without-body',
    )
    assert response.status_code == 200
    assert response.text == ''
