async def test_create(server_client, mongodb):
    response = await server_client.post('mongo/create', json={'field': 1})
    assert response.status_code == 200
    body = response.json()
    doc_id = body.get('_id', None)
    assert isinstance(doc_id, str)

    # read directly from mongodb
    doc = mongodb.example_collection.find_one({'_id': doc_id})
    assert doc == {'_id': doc_id, 'field': 1}


async def test_read_preexisting(server_client):
    # db_example_collection.json
    read_response = await server_client.get('mongo/1')
    assert read_response.status_code == 200
    doc = read_response.json()
    assert doc == {'_id': '1', 'key': 'val'}
