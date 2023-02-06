import base64


async def test_idempotency(
        state_virtual_client_created, create_payment, get_payment,
):
    """
        Test double request is ok.
    """
    state = await state_virtual_client_created()

    for _ in range(2):
        payment = await create_payment(
            virtual_client_id=state.default_virtual_client_id,
        )

        payment = await get_payment(payment['payment_id'])
        assert len(payment['items']) == 2


async def test_empty_contacts(
        state_virtual_client_created, create_payment, get_payment,
):
    state = await state_virtual_client_created()
    payment = await create_payment(
        virtual_client_id=state.default_virtual_client_id,
        email=None,
        phone=None,
    )

    payment = await get_payment(payment['payment_id'])
    assert payment['details']['customer'] == {}


async def test_agent_type(
        state_virtual_client_created, create_payment, get_payment,
):
    state = await state_virtual_client_created()
    payment = await create_payment(
        virtual_client_id=state.default_virtual_client_id, agent_type='none',
    )

    payment = await get_payment(payment['payment_id'])
    for item in payment['items']:
        assert item['agent_type'] == 'none'


async def test_item_mark(
        state_virtual_client_created, create_payment, get_payment,
):
    state = await state_virtual_client_created()
    mark = {
        'kind': 'gs1_data_matrix_base64',
        'code': base64.b64encode(
            b']C1010460043993125621JgXJ5.T\x1d8005',
        ).decode(),
    }

    payment = await create_payment(
        virtual_client_id=state.default_virtual_client_id, item_mark=mark,
    )

    payment = await get_payment(payment['payment_id'])
    for item in payment['items']:
        assert (
            item['mark']['code']
            == base64.b64encode(
                b']C1010460043993125621JgXJ5.T\x1d8005',
            ).decode()
        )
