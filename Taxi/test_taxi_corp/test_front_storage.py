import pytest


@pytest.mark.parametrize(
    ['json', 'expected_length', 'client_id'],
    [
        pytest.param({'key': 'key1', 'value': 'test1'}, 1, 'client1'),
        pytest.param({'key': 'key2', 'value': 'test2'}, 2, 'client1'),
        pytest.param({'key': 'key1', 'value': 'test1'}, 1, 'client2'),
    ],
)
async def test_front_storage(
        taxi_corp_auth_client, db, expected_length, json, client_id,
):
    path = '/1.0/client/{client}/front_storage'.format(client=client_id)
    response = await taxi_corp_auth_client.post(path, json=json)
    assert response.status == 200

    client = await db.corp_front_storage.find(
        {'client_id': client_id},
    ).to_list(None)

    assert len(client) == expected_length


async def test_front_storage_bad_request(taxi_corp_auth_client, db):
    path = '/1.0/client/{client}/front_storage'.format(client='client1')
    response = await taxi_corp_auth_client.post(
        path, json={'key': 'key1', 'valxxx': 'test1'},
    )
    assert response.status == 400
