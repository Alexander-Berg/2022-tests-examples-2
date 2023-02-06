import json

import pytest

from tests_vgw_api import db_consumers


@pytest.mark.pgsql('vgw_api', files=['pg_vgw_api_without_consumers.sql'])
@pytest.mark.parametrize(
    'request_data',
    [
        (
            {
                'name': 'name_1',
                'enabled': True,
                'quota': 10,
                'gateway_ids': ['id_1', 'id_2'],
            }
        ),
        ({'name': 'name_2', 'enabled': True, 'gateway_ids': []}),
    ],
)
async def test_consumers_post(taxi_vgw_api, pgsql, request_data):
    def assertions(db_data, sent_data):
        assert db_data.name == sent_data['name']
        assert db_data.enabled == sent_data['enabled']
        assert db_data.gateway_ids == sent_data['gateway_ids']

    response1 = await taxi_vgw_api.post(
        'v1/consumers', data=json.dumps(request_data),
    )

    consumers = db_consumers.select_consumers(pgsql)
    assert response1.status_code == 200
    assert response1.json() == {'id': 1}
    assert len(consumers) == 1
    db_consumer = consumers[0]
    assert db_consumer.id == 1
    assertions(consumers[0], request_data)


@pytest.mark.parametrize(
    ('request_data', 'response_code'),
    [
        (
            {
                'name': 'name_1',
                'enabled': True,
                'quota': 10,
                'gateway_ids': ['id_1', 'id_4'],
            },
            404,
        ),
        ({'name': 'name_1', 'gateway_ids': ['id_1']}, 400),
    ],
)
async def test_consumers_post_errors(
        taxi_vgw_api, pgsql, request_data, response_code,
):
    consumers_count = len(db_consumers.select_consumers(pgsql))

    response = await taxi_vgw_api.post(
        'v1/consumers', data=json.dumps(request_data),
    )

    assert len(db_consumers.select_consumers(pgsql)) == consumers_count
    assert response.status_code == response_code
    response_json = response.json()
    assert response_json['code'] == str(response_code)


async def test_consumers_get(taxi_vgw_api, pgsql):
    response = await taxi_vgw_api.get('v1/consumers')
    consumers = db_consumers.select_consumers(pgsql)

    def assertions(db_data, response_data):
        assert db_data.name == response_data['name']
        assert db_data.enabled == response_data['enabled']
        assert db_data.gateway_ids == response_data['gateway_ids']

    assert response.status_code == 200
    for data in response.json():
        consumer_id = data['id']
        assertions(consumers[consumer_id - 1], data)
