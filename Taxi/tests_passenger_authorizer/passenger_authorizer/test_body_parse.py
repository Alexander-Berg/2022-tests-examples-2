import json


async def test_user_in_body(
        taxi_passenger_authorizer, blackbox_service, mockserver, testpoint,
):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/3.0/user_id_in_body')
    def test(request):

        # Auth headers
        assert request.headers['X-Yandex-Login'] == 'login'
        assert request.headers['X-Yandex-Uid'] == '100'
        assert (
            request.headers['X-YaTaxi-Pass-Flags']
            == 'phonish,credentials=token-bearer'
        )
        assert request.headers['X-YaTaxi-UserId'] == '12345'

        return {'id': '123'}

    blackbox_service.set_token_info('test_token', uid='100')

    response = await taxi_passenger_authorizer.post(
        '3.0/user_id_in_body',
        data=json.dumps({'id': '12345'}),
        bearer='test_token',
    )
    assert response.status_code == 200
    assert response.json() == {'id': '123'}


async def test_no_user_in_body(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/3.0/user_id_in_body')
    def test(request):
        assert False

    blackbox_service.set_token_info('test_token', uid='100')

    response = await taxi_passenger_authorizer.post(
        '3.0/user_id_in_body',
        data=json.dumps({'id1': '12345'}),
        bearer='test_token',
    )
    assert response.status_code == 401


async def test_no_user_no_json(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/3.0/user_id_in_body')
    def test(request):
        assert False

        return {'id': '123'}

    blackbox_service.set_token_info('test_token', uid='100')

    response = await taxi_passenger_authorizer.post(
        '3.0/user_id_in_body', data='', bearer='test_token',
    )
    assert response.status_code == 401


async def test_user_in_header_and_body(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/3.0/user_id_in_body')
    def test(request):

        # Auth headers
        assert request.headers['X-Yandex-Login'] == 'login'
        assert request.headers['X-Yandex-Uid'] == '100'
        assert (
            request.headers['X-YaTaxi-Pass-Flags']
            == 'phonish,credentials=token-bearer'
        )
        assert request.headers['X-YaTaxi-UserId'] == '12345'

        return {'id': '123'}

    blackbox_service.set_token_info('test_token', uid='100')

    response = await taxi_passenger_authorizer.post(
        '3.0/user_id_in_body',
        data=json.dumps({}),
        bearer='test_token',
        headers={'X-YaTaxi-UserId': '12345'},
    )
    assert response.status_code == 200
    assert response.json() == {'id': '123'}
