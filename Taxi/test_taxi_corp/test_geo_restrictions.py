import pytest


@pytest.mark.parametrize(
    ['client_id', 'expected_result'],
    [
        (
            'client1',
            {
                'limit': 100,
                'offset': 0,
                'items': [
                    {
                        '_id': 'geo_id_1',
                        'name': '1',
                        'geo': {
                            'center': [37.642639, 55.734894],
                            'radius': 200,
                        },
                        'geo_type': 'circle',
                    },
                    {
                        '_id': 'geo_id_2',
                        'name': '2',
                        'geo': {
                            'center': [37.642639, 55.734894],
                            'radius': 200,
                        },
                        'geo_type': 'circle',
                    },
                ],
                'amount': 2,
            },
        ),
    ],
)
async def test_get_geo_restrictions(
        taxi_corp_auth_client, client_id, expected_result,
):
    response = await taxi_corp_auth_client.get(
        '/1.0/client/{}/geo_restrictions'.format(client_id),
    )

    assert response.status == 200
    assert await response.json() == expected_result


async def test_post_geo_restrictions(taxi_corp_auth_client, db, patch):
    @patch('taxi_corp.api.handlers.v1.geo_restrictions.generate_geo_id')
    def _generate_geo_id():
        return 'geo_id'

    response = await taxi_corp_auth_client.post(
        '/1.0/client/client1/geo_restrictions',
        json={
            'name': 'name',
            'geo_type': 'circle',
            'geo': {'center': [37.642639, 55.734894], 'radius': 200},
        },
    )

    assert response.status == 200
    assert await response.json() == {'_id': 'geo_id'}
    assert (
        await db.corp_geo_restrictions.find_one(
            {'_id': 'geo_id'}, {'created': 0, 'updated': 0},
        )
        == {
            '_id': 'geo_id',
            'client_id': 'client1',
            'name': 'name',
            'is_deleted': False,
            'type': 'office',
            'geo_type': 'circle',
            'geo': {'center': [37.642639, 55.734894], 'radius': 200},
        }
    )


async def test_put_geo_restrictions(taxi_corp_auth_client, db):
    response = await taxi_corp_auth_client.put(
        '/1.0/client/client1/geo_restrictions/geo_id_1',
        json={
            'name': 'name',
            'geo_type': 'circle',
            'geo': {'center': [37.642639, 55.734894], 'radius': 800},
        },
    )

    assert response.status == 200
    assert await response.json() == {'_id': 'geo_id_1'}
    assert (
        await db.corp_geo_restrictions.find_one(
            {'_id': 'geo_id_1'}, {'created': 0, 'updated': 0},
        )
        == {
            '_id': 'geo_id_1',
            'client_id': 'client1',
            'name': 'name',
            'is_deleted': False,
            'type': 'office',
            'geo_type': 'circle',
            'geo': {'center': [37.642639, 55.734894], 'radius': 800},
        }
    )


async def test_delete_geo_restrictions(taxi_corp_auth_client, db):
    response = await taxi_corp_auth_client.delete(
        '/1.0/client/client1/geo_restrictions/geo_id_1',
    )

    assert response.status == 200
    assert await response.json() == {'_id': 'geo_id_1'}
    assert (
        await db.corp_geo_restrictions.find_one(
            {'_id': 'geo_id_1'}, {'created': 0, 'updated': 0},
        )
        == {
            '_id': 'geo_id_1',
            'client_id': 'client1',
            'name': '1',
            'is_deleted': True,
            'type': 'office',
            'geo_type': 'circle',
            'geo': {'center': [37.642639, 55.734894], 'radius': 200},
        }
    )
