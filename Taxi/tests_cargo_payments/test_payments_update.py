async def test_happy_path(
        state_payment_created, update_items, taxi_cargo_payments,
):
    state = await state_payment_created()

    await update_items(payment_id=state.payment_id, snapshot_token='token1')

    response = await taxi_cargo_payments.post(
        'v1/payment/info', params={'payment_id': state.payment_id},
    )
    assert response.status_code == 200


async def test_update_invalid_inn_corp(
        state_payment_created, build_update_request, taxi_cargo_payments,
):
    state = await state_payment_created()

    response = await taxi_cargo_payments.post(
        '/api/b2b/cargo-payments/v1/payment/update',
        json=build_update_request(
            payment_id=state.payment_id,
            supplier_inn='0005114405',
            snapshot_token='token1',
        ),
    )

    assert response.status_code == 400


async def test_update_invalid_inn_internal(
        state_payment_created, build_update_request, taxi_cargo_payments,
):
    state = await state_payment_created()

    response = await taxi_cargo_payments.post(
        '/v1/payment/update',
        json=build_update_request(
            payment_id=state.payment_id,
            supplier_inn='0005114405',
            snapshot_token='token1',
        ),
    )

    assert response.status_code == 400


async def test_second_update(state_payment_created, get_payment, update_items):
    state = await state_payment_created()
    await update_items(
        status_code=200, payment_id=state.payment_id, snapshot_token='token1',
    )

    payment = await get_payment(state.payment_id)
    assert payment['revision'] == state.payment_revision + 1

    await update_items(
        status_code=200, payment_id=state.payment_id, snapshot_token='token2',
    )

    payment = await get_payment(state.payment_id)
    assert payment['revision'] == state.payment_revision + 2


async def test_update_idempotent(
        state_payment_created, get_payment, update_items,
):
    state = await state_payment_created()

    await update_items(
        status_code=200, payment_id=state.payment_id, snapshot_token='token1',
    )

    payment = await get_payment(state.payment_id)
    assert payment['revision'] == state.payment_revision + 1

    await update_items(
        status_code=200, payment_id=state.payment_id, snapshot_token='token1',
    )

    payment = await get_payment(state.payment_id)
    assert payment['revision'] == state.payment_revision + 1


async def test_update_expired(
        state_payment_finished, update_items, mocked_time,
):
    state = await state_payment_finished(item_count=2)
    mocked_time.sleep(3600 * 24 * 60)  # 60 days
    await update_items(
        status_code=410,
        payment_id=state.payment_id,
        snapshot_token='token1',
        item_count=1,
    )


async def test_admin_update(
        state_payment_created, admin_update_items, get_payment,
):
    state = await state_payment_created()
    payment = await get_payment(state.payment_id)

    ticket = 'ticket'
    comment = 'comment'
    await admin_update_items(
        status_code=200,
        ticket=ticket,
        comment=comment,
        payment_id=state.payment_id,
        snapshot_token='token1',
        item_count=123,  # changed
    )

    updated_payment = await get_payment(state.payment_id)
    assert updated_payment['items'] != payment['items']
    assert updated_payment['revision'] == payment['revision'] + 1


async def test_admin_update_wrong_status(
        state_payment_confirmed, admin_update_items,
):
    state = await state_payment_confirmed()

    await admin_update_items(
        status_code=410, payment_id=state.payment_id, snapshot_token='token1',
    )


async def test_corp_cabinet_update(
        state_payment_created, corp_cabinet_update_items, get_payment,
):
    state = await state_payment_created()
    payment = await get_payment(state.payment_id)

    await corp_cabinet_update_items(
        status_code=200,
        payment_id=state.payment_id,
        snapshot_token='token1',
        item_count=123,  # changed
    )

    updated_payment = await get_payment(state.payment_id)
    assert updated_payment['items'] != payment['items']

    assert updated_payment['revision'] == payment['revision'] + 1


async def test_corp_cabinet_update_wrong_status(
        state_payment_confirmed, corp_cabinet_update_items,
):
    state = await state_payment_confirmed()

    await corp_cabinet_update_items(
        status_code=410, payment_id=state.payment_id, snapshot_token='token1',
    )


def _find_item(items, article):
    for item in items:
        if item['article'] == article:
            return item
    return None


def _check_returned_count(items, article, returned_count):
    item = _find_item(items, article)
    assert item

    assert item['returned'] == returned_count
