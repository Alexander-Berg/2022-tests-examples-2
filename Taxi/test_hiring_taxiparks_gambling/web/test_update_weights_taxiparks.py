async def request_update_weights(client, data):
    response = await client.post(
        '/taxiparks/update-weights/',
        data=data,
        headers={'Content-Type': 'text/csv'},
    )
    return response


async def test_attempt_to_upload(web_app_client, load_json):
    request = load_json('update_weights_requests.json')['first_csv']

    response = await request_update_weights(web_app_client, request)
    assert response.status == 200


async def test_not_unique_ids(web_app_client, load_json):
    request = load_json('update_weights_requests.json')['not_unique_ids']

    response = await request_update_weights(web_app_client, request)

    response_body = await response.json()
    expectation = (
        'Invalid CSV data! Db IDs must be unique. '
        'This id "DB_ID3" appears twice or more'
    )
    assert response_body['message'] == expectation


async def test_invalid_value_type(web_app_client, load_json):
    async def check(name):
        request = load_json('update_weights_requests.json')[name]

        response = await request_update_weights(web_app_client, request)

        assert response.status == 400
        response_body = await response.json()

        expectation = (
            'Invalid CSV data! '
            'Weights values must be integer between 1 and 100.'
        )
        assert expectation in response_body['message']

    await check('invalid_value_type')
    await check('greater_than_100')


async def test_attempt_to_upload_and_get(web_app_client, load_json):
    async def get_weights(db_id):
        request = {'db_id': db_id}
        response = await web_app_client.get(
            '/taxiparks/get-weights', params=request,
        )
        assert response.status == 200
        response_body = await response.json()
        assert response_body['park']['db_id'] == db_id

    request = load_json('update_weights_requests.json')['first_csv']

    response = await request_update_weights(web_app_client, request)

    assert response.status == 200

    await get_weights('DB_ID3')
    await get_weights('DOESNT_EXIST')
