EXTERNAL_REF = 'Megatron'
UID = 123456789
TOKEN_RESPONSE = {
    'token_type': 'token_type',
    'access_token': 'access_token',
    'expires_in': 124234123534,
    'refresh_token': 'refresh_token',
}
AUTHORIZATION = 'Basic Y2xpZW50X2lkOnNlY3JldA=='


async def test_token_ok(
        taxi_cargo_robots, oauth_handler_ctx, oauth_handler, create_robot,
):
    await create_robot(UID, EXTERNAL_REF, True)
    oauth_handler_ctx.response = (200, TOKEN_RESPONSE)

    response = await taxi_cargo_robots.post(
        'v1/robot/token', params={'external_ref': EXTERNAL_REF},
    )
    assert oauth_handler.times_called == 1
    assert response.status == 200
    assert response.json()['token'] == 'access_token'


async def test_token_oauth_error(
        taxi_cargo_robots, oauth_handler_ctx, oauth_handler, create_robot,
):
    await create_robot(UID, EXTERNAL_REF, True)
    oauth_handler_ctx.response = (
        403,
        {'error': 'error', 'error_description': 'description'},
    )

    response = await taxi_cargo_robots.post(
        'v1/robot/token', params={'external_ref': EXTERNAL_REF},
    )
    assert oauth_handler.times_called == 1
    assert response.status == 500


async def test_token_unregistered_robot(
        taxi_cargo_robots, oauth_handler, create_robot,
):
    await create_robot(UID, EXTERNAL_REF, False)
    response = await taxi_cargo_robots.post(
        'v1/robot/token', params={'external_ref': EXTERNAL_REF},
    )
    assert oauth_handler.times_called == 0
    assert response.status == 404


async def test_token_request(
        taxi_cargo_robots, passport_internal_handler, mockserver, create_robot,
):
    await create_robot(UID, EXTERNAL_REF, True)
    passport_request = passport_internal_handler.next_call()['request'].form

    @mockserver.json_handler('/yandex-oauth/token')
    def oauth_token(request):
        assert 'Authorization' in request.headers
        assert request.headers['Authorization'] == AUTHORIZATION
        assert request.form['username'] == passport_request['login']
        assert request.form['password'] == passport_request['password']

        return mockserver.make_response(json=TOKEN_RESPONSE, status=200)

    response = await taxi_cargo_robots.post(
        'v1/robot/token', params={'external_ref': EXTERNAL_REF},
    )
    assert oauth_token.times_called == 1
    assert response.status == 200
    assert response.json()['token'] == TOKEN_RESPONSE['access_token']
