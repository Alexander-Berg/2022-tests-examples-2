async def test_request_eats_authproxy_user_personal(
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
            'X-Eats-User': (
                ' user_id=12345,'
                ' personal_email_id = 1337ab   ,'
                'personal_phone_id=233223,'
                'eater_uuid=uuid123'
            ),
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'data': {
            'personal_phone_id': '233223',
            'personal_email_id': '1337ab',
            'user_id': '12345',
            'eater_uuid': 'uuid123',
        },
        'personal1': '233223',
        'personal2': '1337ab',
        'personal3': '12345',
        'personal4': 'uuid123',
        'has_personal1': True,
        'has_partner_user_id': False,
        'partner_user_id': 'p_23s2s',
    }
