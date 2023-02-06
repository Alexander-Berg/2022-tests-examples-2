import pytest


@pytest.mark.parametrize(
    '_id, code, answer',
    [
        (
            '8cb814078d854e6c9d21039923621110',
            200,
            {'name': 'John', 'greetings': 'Hi'},
        ),
        (
            '11111111111111111111111111111111',
            404,
            {
                'code': 'not-found',
                'message': 'Document with required id is not found',
            },
        ),
    ],
)
async def test_mongo_get_by_id(_id, code, answer, web_app_client):
    response = await web_app_client.get('/mongo/get_by_id', params={'id': _id})
    assert response.status == code
    content = await response.json()
    assert content == answer


async def test_mongo_insert_once(web_app_client, mongo):
    body = {'name': 'Beta', 'greetings': 'Gamma'}
    response = await web_app_client.post('/mongo/insert_document', json=body)
    assert response.status == 200

    document = await mongo.users.find_one(
        {'name': 'Beta', 'greetings': 'Gamma'},
    )
    assert document


async def test_mongo_insert_twice(web_app_client, mongo):
    body = {'name': 'Beta', 'greetings': 'Gamma'}
    await web_app_client.post('/mongo/insert_document', json=body)
    response = await web_app_client.post('/mongo/insert_document', json=body)
    assert response.status == 409
    content = await response.json()
    assert content == {
        'code': 'conflict',
        'message': 'Trying to insert already added document',
    }
