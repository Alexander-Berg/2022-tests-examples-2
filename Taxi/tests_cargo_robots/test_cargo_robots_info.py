EXTERNAL_REF = 'Megatron'
UID = 123456789


async def test_info_ok(
        taxi_cargo_robots, passport_internal_handler, create_robot,
):
    robot_info = await create_robot(UID, EXTERNAL_REF, True)

    response = await taxi_cargo_robots.get(
        'v1/robot/info', params={'external_ref': EXTERNAL_REF},
    )
    assert passport_internal_handler.times_called == 1
    assert response.status == 200
    assert response.json() == robot_info


async def test_info_not_found(
        taxi_cargo_robots, passport_internal_handler, create_robot,
):
    await create_robot(UID, EXTERNAL_REF, False)

    response = await taxi_cargo_robots.get(
        'v1/robot/info', params={'external_ref': EXTERNAL_REF},
    )
    assert passport_internal_handler.times_called == 1
    assert response.status == 404
