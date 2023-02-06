from . import utils


@utils.send_order_events_config()
async def test_drop_picker_200(
        taxi_eats_picker_orders,
        create_order,
        get_last_order_status,
        mock_processing,
):
    order_id = create_order(eats_id='42', picker_id='1', last_version=1)

    response = await taxi_eats_picker_orders.delete(
        '/api/v1/picker?eats_id=42',
    )

    last_order_status = get_last_order_status(order_id)
    assert last_order_status['state'] == 'new'
    assert last_order_status['author_id'] is None

    assert response.status == 200

    assert mock_processing.times_called == 1


@utils.send_order_events_config()
async def test_drop_picker_202(
        taxi_eats_picker_orders, create_order, mock_processing,
):
    create_order(eats_id='42', picker_id='1', last_version=1)

    response = await taxi_eats_picker_orders.delete(
        '/api/v1/picker?eats_id=42',
    )

    assert response.status == 200

    response = await taxi_eats_picker_orders.delete(
        '/api/v1/picker?eats_id=42',
    )

    assert response.status == 202

    assert mock_processing.times_called == 1


async def test_drop_picker_404(taxi_eats_picker_orders, create_order):
    create_order(eats_id='42', picker_id='1', last_version=1)

    response = await taxi_eats_picker_orders.delete(
        '/api/v1/picker?eats_id=43',
    )

    assert response.status == 404


async def test_drop_picker_409(taxi_eats_picker_orders, create_order):
    create_order(eats_id='42', picker_id='1', last_version=1, state='complete')

    response = await taxi_eats_picker_orders.delete(
        '/api/v1/picker?eats_id=42',
    )

    assert response.status == 409


@utils.send_order_events_config()
async def test_check_delete(
        taxi_eats_picker_orders, create_order, mock_processing,
):
    create_order(eats_id='42', picker_id='1', last_version=1, state='assigned')

    # check info about picker
    response = await taxi_eats_picker_orders.get('/api/v1/order?eats_id=42')
    assert response.status == 200
    payload = response.json()['payload']

    assert payload['status'] == 'assigned'
    assert 'picker_comment' in payload
    assert 'picker_phone_id' in payload
    assert 'picker_name' in payload

    # drop picker
    response = await taxi_eats_picker_orders.delete(
        '/api/v1/picker?eats_id=42',
    )
    assert response.status == 200

    # check info about picker
    response = await taxi_eats_picker_orders.get('/api/v1/order?eats_id=42')
    assert response.status == 200
    payload = response.json()['payload']

    assert payload['status'] == 'new'
    assert 'picker_id' not in payload
    assert 'picker_comment' not in payload
    assert 'picker_phone_id' not in payload
    assert 'picker_name' not in payload

    assert mock_processing.times_called == 1
