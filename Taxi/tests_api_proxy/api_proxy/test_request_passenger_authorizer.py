async def test_request_passenger_authorizer_pass_flags(
        taxi_api_proxy, mockserver, resources, load_yaml, endpoints,
):
    await resources.safely_create_resource(
        resource_id='test-resource',
        url=mockserver.url('mock-me'),
        method='post',
    )

    handler_def = load_yaml('pass_flags_handler.yaml')
    path = '/test/foo/bar'
    await endpoints.safely_create_endpoint(path, post_handler=handler_def)

    response = await taxi_api_proxy.post(
        'test/foo/bar',
        json={},
        headers={'X-YaTaxi-Pass-Flags': ' flag1, flag2,flag3 flag4   '},
    )
    assert response.status_code == 200
    assert response.json() == {
        'data': {'flag1': True, 'flag2': True, 'flag3': True, 'flag4': True},
        'has_flag1': True,
        'has_flag2': True,
        'has_flag5': False,
        'has_flag6': False,
    }


async def test_request_passenger_authorizer_user_personal(
        taxi_api_proxy, mockserver, resources, load_yaml, endpoints,
):
    await resources.safely_create_resource(
        resource_id='test-resource',
        url=mockserver.url('mock-me'),
        method='post',
    )

    handler_def = load_yaml('user_personal_handler.yaml')
    path = '/test/foo/bar'
    await endpoints.safely_create_endpoint(path, post_handler=handler_def)

    response = await taxi_api_proxy.post(
        'test/foo/bar',
        json={},
        headers={
            'X-YaTaxi-User': (
                ' personal_phone_id=12345,'
                'personal_email_id= dead,'
                ' eats_user_id = 1337ab   '
            ),
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'data': {
            'personal_phone_id': '12345',
            'personal_email_id': 'dead',
            'eats_user_id': '1337ab',
        },
        'personal1': '12345',
        'personal2': 'dead',
        'personal3': '1337ab',
        'has_personal1': True,
        'has_secondary_phone_id': False,
        'secondary_phone_id': '8-800-555-35-35',
    }
