import pytest

PARAM_COURIER_EXISTS = pytest.mark.parametrize(
    'courier_exists', [True, False]
)

PARAM_FIELDS = pytest.mark.parametrize([
    'field_name', 'field_getter'
], [
    ('taxi_driver_uuid', lambda order: order.courier.taxi_driver_uuid),
    ('courier_vin', lambda order: order.courier.vin),
])


@PARAM_COURIER_EXISTS
@PARAM_FIELDS
async def test_new_value(
        tap, dataset, api, uuid,
        field_name, field_getter,
        courier_exists
):
    t = await api(role='token:web.external.tokens.0')

    with tap:
        order = await _create_and_check_order(
            tap, dataset, uuid, set_courier=courier_exists
        )

        new_value = uuid()
        if courier_exists:
            tap.ne(field_getter(order), new_value, f'{field_name} старый')

        await t.post_ok(
            'api_external_orders_set_courier',
            json={
                'store_id': order.store_id,
                'external_id': order.external_id,
                'courier_name': 'Иванов Иван',
                'courier_arrival_time': '2021-01-01T23:34:42+04:00',
                'related_orders': [order.order_id],
                'courier_external_id': uuid(),
                field_name: new_value
            }
        )
        t.status_is(200, diag=True)

        tap.ok(await order.reload(), 'ордер перегружен')
        tap.ok(order.courier, 'есть курьер в ордере')
        tap.eq(field_getter(order), new_value, f'{field_name} новый')


@PARAM_COURIER_EXISTS
@PARAM_FIELDS
async def test_missing(
        tap, dataset, api, uuid,
        field_name, field_getter,
        courier_exists
):
    t = await api(role='token:web.external.tokens.0')

    with tap:
        order = await _create_and_check_order(
            tap, dataset, uuid, set_courier=courier_exists
        )

        if courier_exists:
            old_value = field_getter(order)
        else:
            old_value = None

        await t.post_ok(
            'api_external_orders_set_courier',
            json={
                'store_id': order.store_id,
                'external_id': order.external_id,
                'courier_name': 'Иванов Иван',
                'courier_arrival_time': '2021-01-01T23:34:42+04:00',
                'related_orders': [order.order_id],
                'courier_external_id': uuid()
            }
        )
        t.status_is(200, diag=True)

        tap.ok(await order.reload(), 'ордер перегружен')
        tap.ok(order.courier, 'есть курьер в ордере')
        tap.eq(field_getter(order), old_value,
               f'{field_name} остался старым')


@PARAM_COURIER_EXISTS
@PARAM_FIELDS
async def test_none(
        tap, dataset, api, uuid,
        field_name, field_getter,
        courier_exists
):
    t = await api(role='token:web.external.tokens.0')

    with tap:
        order = await _create_and_check_order(
            tap, dataset, uuid, set_courier=courier_exists
        )

        if courier_exists:
            tap.ok(field_getter(order), f'{field_name} есть')

        await t.post_ok(
            'api_external_orders_set_courier',
            json={
                'store_id': order.store_id,
                'external_id': order.external_id,
                'courier_name': 'Иванов Иван',
                'courier_arrival_time': '2021-01-01T23:34:42+04:00',
                'related_orders': [order.order_id],
                'courier_external_id': uuid(),
                field_name: None
            }
        )
        t.status_is(200, diag=True)

        tap.ok(await order.reload(), 'ордер перегружен')
        tap.ok(order.courier, 'есть курьер в ордере')
        tap.is_ok(field_getter(order), None, f'{field_name} стал пустым')


@pytest.mark.parametrize('bad_value', ['', ' ', '\t'])
@PARAM_FIELDS
async def test_invalid(
        tap, dataset, api, uuid,
        field_name, field_getter,
        bad_value
):
    assert field_getter  # hack for passing pylint

    t = await api(role='token:web.external.tokens.0')

    with tap:
        order = await _create_and_check_order(tap, dataset, uuid)
        await t.post_ok(
            'api_external_orders_set_courier',
            json={
                'store_id': order.store_id,
                'external_id': order.external_id,
                'courier_name': 'Иванов Иван',
                'courier_arrival_time': '2021-01-01T23:34:42+04:00',
                'related_orders': [order.order_id],
                'courier_external_id': uuid(),
                field_name: bad_value
            }
        )
        t.status_is(400, diag=True)


async def _create_and_check_order(
        tap, dataset, uuid,
        set_courier: bool = False
):
    courier = None
    if set_courier:
        courier = {
            'vin': uuid(),
            'taxi_driver_uuid': uuid(),
        }

    order = await dataset.order(courier=courier)

    tap.ok(order, 'ордер создан')

    if set_courier:
        tap.ok(order.courier, 'курьер есть в заказе')
    else:
        tap.ok(not order.courier, 'курьера в заказе нет')

    return order
