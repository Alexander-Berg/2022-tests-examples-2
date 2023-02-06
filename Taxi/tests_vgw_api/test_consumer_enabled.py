import json

import pytest

from tests_vgw_api import db_consumers


@pytest.mark.parametrize(
    ('params', 'request_data'),
    [({'id': 1}, {'enabled': True}), ({'id': 1}, {'enabled': False})],
)
async def test_consumer_enabled_put(taxi_vgw_api, pgsql, params, request_data):

    response = await taxi_vgw_api.put(
        'v1/consumers/enabled', params=params, data=json.dumps(request_data),
    )

    assert response.status_code == 200
    assert response.json() == {}
    db_enabled = db_consumers.select_consumer_enabled(pgsql, params['id'])
    assert db_enabled == request_data['enabled']


@pytest.mark.parametrize(
    ('params', 'request_data', 'response_code'),
    [
        ({'id': 'asdsa'}, {'enabled': True}, 400),
        ({'id': 1}, {'enabled': 1}, 400),
        ({'id': 39}, {'enabled': True}, 404),
    ],
)
async def test_consumer_enabled_put_errors(
        taxi_vgw_api, params, request_data, response_code,
):

    response = await taxi_vgw_api.put(
        'v1/consumers/enabled', params=params, data=json.dumps(request_data),
    )

    assert response.status_code == response_code
    response_json = response.json()
    assert response_json['code'] == str(response_code)
