EATS_HEADERS = {
    'X-YaTaxi-Session': 'eats:123',
    'X-Yandex-UID': 'sample meta_user_uid',
    'X-YaTaxi-PhoneId': 'sample phone_id',
    'X-YaTaxi-User': (
        ' personal_phone_id=sample meta_personal_phone_id,'
        ' eats_user_id=sample meta_eats_user_id,'
    ),
}


async def test_sample_base(taxi_test_service, mockserver):
    async with taxi_test_service.capture_logs() as capture:

        @mockserver.json_handler('/test-service/sample-super-app')
        def _handler(request):
            return mockserver.make_response()

        response = await taxi_test_service.get(
            '/sample-super-app', headers=EATS_HEADERS,
        )

        assert response.status_code == 200

        data = capture.select()

        for elem in data:
            if (
                    'stopwatch_name' in elem
                    and elem['stopwatch_name']
                    == 'http/handler-echo_supper_app-get'
            ):
                assert elem['meta_user_uid'] == 'sample meta_user_uid'
                assert elem['phone_id'] == 'sample phone_id'
                assert (
                    elem['meta_personal_phone_id']
                    == 'sample meta_personal_phone_id'
                )
                assert elem['meta_eats_user_id'] == 'sample meta_eats_user_id'


async def test_sample_error(taxi_test_service, mockserver):
    @mockserver.json_handler('/test-service/sample-super-app')
    def _handler(request):
        return mockserver.make_response()

    response = await taxi_test_service.get('/sample-super-app')

    assert response.status_code == 401
