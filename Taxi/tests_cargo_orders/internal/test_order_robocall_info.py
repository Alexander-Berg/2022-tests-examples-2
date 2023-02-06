async def test_happy_path(
        taxi_cargo_orders,
        prepare_order_client_robocall,
        prepare_robocall_attempt,
):
    order_id = '9db1622e-582d-4091-b6fc-4cb2ffdc12c0'
    point_id = 'point_id_1'
    claim_id = 'test_claim_id_1'

    prepare_order_client_robocall(
        order_id,
        point_id,
        claim_id=claim_id,
        reason='client_not_responding',
        created_ts='2021-10-10T10:00:00+03:00',
        updated_ts='2021-10-10T10:10:00+03:00',
    )

    prepare_robocall_attempt(
        order_id,
        point_id,
        0,  # attempt_id
        resolution='no_answer',
        created_ts='2021-10-10T10:00:01+03:00',
        updated_ts='2021-10-10T10:00:02+03:00',
    )
    prepare_robocall_attempt(
        order_id,
        point_id,
        1,  # attempt_id
        resolution='no_answer',
        created_ts='2021-10-10T10:00:11+03:00',
        updated_ts='2021-10-10T10:00:12+03:00',
    )
    prepare_robocall_attempt(
        order_id,
        point_id,
        2,  # attempt_id
        resolution=None,  # Running attempt will be skipped.
        created_ts='2021-10-10T10:00:21+03:00',
        updated_ts='2021-10-10T10:00:22+03:00',
    )

    response = await taxi_cargo_orders.get(
        'internal/cargo-orders/v1/robocall/info' + f'?claim_id={claim_id}',
    )
    assert response.status_code == 200
    assert response.json() == {
        'robocall_attempts': [
            {
                'finished_at': '2021-10-10T07:00:02+00:00',
                'started_at': '2021-10-10T07:00:01+00:00',
                'status': 'client_not_answered',
            },
            {
                'finished_at': '2021-10-10T07:00:12+00:00',
                'started_at': '2021-10-10T07:00:11+00:00',
                'status': 'client_not_answered',
            },
        ],
        'robocall_requested_at': '2021-10-10T07:00:00+00:00',
    }


async def test_not_found_attempts(
        taxi_cargo_orders, prepare_order_client_robocall,
):
    order_id = '9db1622e-582d-4091-b6fc-4cb2ffdc12c0'
    point_id = 'point_id_1'
    claim_id = 'test_claim_id_1'

    prepare_order_client_robocall(
        order_id,
        point_id,
        claim_id=claim_id,
        reason='client_not_responding',
        created_ts='2021-10-10T10:00:00+03:00',
        updated_ts='2021-10-10T10:10:00+03:00',
    )

    response = await taxi_cargo_orders.get(
        'internal/cargo-orders/v1/robocall/info' + f'?claim_id={claim_id}',
    )
    assert response.status_code == 200
    assert response.json() == {
        'robocall_attempts': [],
        'robocall_requested_at': '2021-10-10T07:00:00+00:00',
    }


async def test_not_found_robocall(taxi_cargo_orders):
    claim_id = 'test_claim_id_1'

    response = await taxi_cargo_orders.get(
        'internal/cargo-orders/v1/robocall/info' + f'?claim_id={claim_id}',
    )
    assert response.status_code == 200
    assert response.json() == {}
