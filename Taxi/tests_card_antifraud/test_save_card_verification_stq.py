def select_verification(pgsql, user_uid, device_id, card_id):
    cursor = pgsql['card_antifraud'].cursor()
    cursor.execute(
        (
            f'SELECT * '
            f'FROM card_antifraud.cards_verification '
            f'WHERE yandex_uid = \'{user_uid}\''
            f'AND device_id = \'{device_id}\''
            f'AND card_id = \'{card_id}\''
        ),
    )
    return list(cursor)


async def test_save_card_verification(stq_runner, mockserver, pgsql):
    card_id = 'x-123456'
    yandex_uid = '1234'
    device_id = 'test_device_id'

    pg_result = select_verification(pgsql, yandex_uid, device_id, card_id)
    assert not pg_result

    @mockserver.json_handler('/user-api/users/get')
    def _mock_users(request):
        return {'id': 'test_id', 'metrica_device_id': device_id}

    user_id = '4321'
    verification_id = 'verification_1'
    verification_status = 'in_progress'
    verification_method = 'standard2_3ds'

    x3ds_url = 'test_3ds_url'
    random_amount_tries_left = 0
    finish_binding_url = 'test_url'
    args = [
        user_id,
        verification_id,
        card_id,
        yandex_uid,
        verification_status,
        verification_method,
        x3ds_url,
        random_amount_tries_left,
        finish_binding_url,
    ]

    task_id = '123'
    await stq_runner.save_card_verification.call(task_id=task_id, args=args)

    pg_result = select_verification(pgsql, yandex_uid, device_id, card_id)
    assert len(pg_result) == 1

    for item in (
            verification_id,
            verification_status,
            verification_method,
            x3ds_url,
            random_amount_tries_left,
            finish_binding_url,
    ):
        assert item in pg_result[0]


async def test_no_metrica_id(stq_runner, mockserver, pgsql):
    card_id = 'x-123456'
    yandex_uid = '1234'
    device_id = 'test_device_id'

    pg_result = select_verification(pgsql, yandex_uid, device_id, card_id)
    assert not pg_result

    @mockserver.json_handler('/user-api/users/get')
    def _mock_users(request):
        return {'id': 'test_id'}

    user_id = '4321'
    verification_id = 'verification_1'
    verification_status = 'in_progress'
    verification_method = 'standard2'
    args = [
        user_id,
        verification_id,
        card_id,
        yandex_uid,
        verification_status,
        verification_method,
    ]

    task_id = '123'
    await stq_runner.save_card_verification.call(task_id=task_id, args=args)

    pg_result = select_verification(pgsql, yandex_uid, device_id, card_id)
    assert not pg_result
