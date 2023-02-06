EXTERNAL_REF = 'Megatron'
UID = 123456789
BLACKBOX_UID = '123'


async def test_create_ok(
        taxi_cargo_robots,
        passport_internal_handler_ctx,
        passport_internal_handler,
):
    passport_internal_handler_ctx.response = (
        200,
        {'uid': UID, 'status': 'ok'},
    )
    for _ in range(2):
        response = await taxi_cargo_robots.post(
            'v1/robot/create',
            params={'external_ref': EXTERNAL_REF, 'user_ip': 'user_ip'},
        )
        assert response.status == 200
        response_json = response.json()
        assert response_json['external_ref'] == EXTERNAL_REF
        assert response_json['yandex_uid'] == str(UID)

    assert passport_internal_handler.times_called == 1


async def test_create_already_registered(
        taxi_cargo_robots,
        passport_internal_handler_ctx,
        passport_internal_handler,
        blackbox_service,
        create_robot,
):
    robot_info = await create_robot(UID, EXTERNAL_REF, False)

    passport_internal_handler_ctx.response = (
        200,
        {'errors': ['account.already_registered'], 'status': 'error'},
    )
    blackbox_service.set_user_info(BLACKBOX_UID, robot_info['login'])

    response = await taxi_cargo_robots.post(
        'v1/robot/create',
        params={'external_ref': EXTERNAL_REF, 'user_ip': 'user_ip'},
    )
    assert response.status == 200
    response_json = response.json()
    assert response_json['external_ref'] == EXTERNAL_REF
    assert response_json['yandex_uid'] == BLACKBOX_UID
    assert passport_internal_handler.times_called == 2


async def test_create_password_invalid(
        taxi_cargo_robots,
        passport_internal_handler_ctx,
        passport_internal_handler,
        create_robot,
):
    await create_robot(UID, EXTERNAL_REF, False)

    response = await taxi_cargo_robots.get(
        'v1/robot/info', params={'external_ref': EXTERNAL_REF},
    )
    assert response.status == 404

    passport_internal_handler_ctx.response = (
        200,
        {
            'errors': ['a.b', 'password.weak', 'login.invalid', 'q.r'],
            'status': 'error',
        },
    )
    passport_internal_handler_ctx.alternative_response = (
        200,
        {'uid': UID, 'status': 'ok'},
    )
    response = await taxi_cargo_robots.post(
        'v1/robot/create',
        params={'external_ref': EXTERNAL_REF, 'user_ip': 'user_ip'},
    )
    assert response.status == 200
    response_json = response.json()
    assert response_json['external_ref'] == EXTERNAL_REF
    assert response_json['yandex_uid'] == str(UID)
    assert passport_internal_handler.times_called == 3
    assert passport_internal_handler_ctx.alternative_response is None
