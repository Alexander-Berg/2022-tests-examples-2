import json


async def test_get_groceries_list(web_app_client, db, open_file):
    response = await web_app_client.get('/api/v1/groceries/list')
    assert response.status == 200
    content = await response.json()

    with open_file('expected_result.json') as json_file:
        expected_result = json.load(json_file)

    assert content == expected_result
