import pytest

TARIFF_TO_TAG = {
    'scooters': 'order_mode_scooters',
    'lavka': 'order_mode_lavka',
    'eda': 'order_mode_eda',
    'cargo': 'order_mode_cargo',
    'cargocorp': 'order_mode_cargo',
}


@pytest.fixture(name='mock_cargo_orders_performer_info')
def _mock_cargo_orders_performer_info(mockserver):
    @mockserver.json_handler('/cargo-orders/v1/performers/bulk-info')
    async def _handler(request):
        return {
            'performers': [
                {
                    'order_id': request.json['orders_ids'][0],
                    'order_alias_id': '1234',
                    'phone_pd_id': '+70000000000_id',
                    'name': 'Kostya',
                    'driver_id': 'driver_id_1',
                    'park_id': 'park_id_1',
                    'park_name': 'some_park_name',
                    'park_org_name': 'some_park_org_name',
                    'car_id': '123',
                    'car_number': 'А001АА77',
                    'car_model': 'KAMAZ',
                    'lookup_version': 1,
                    'tariff_class': 'cargo',
                    'revision': 1,
                },
            ],
        }


def _callback_config():
    return {
        'description': (
            'Исполнитель слишком долго выполняет заказ.'
            ' {explain_have_items_on_hands}{explain_next_point_type}'
            '{explain_only_last_point_left}'
        ),
        'hints': {
            'have_items_on_hands': [
                {
                    'message': (
                        'Исполнитель не забрал посылку (судя по статусам). '
                    ),
                    'value': True,
                },
                {'message': 'Исполнитель забрал посылку. ', 'value': False},
            ],
            'next_point_type': [
                {
                    'message': 'Исполнитель не подтвердил получение посылки. ',
                    'point_type': 'source',
                },
                {
                    'message': 'Исполнитель не подтвердил передачу посылки. ',
                    'point_type': 'destination',
                },
                {
                    'message': (
                        'Не подтвержден возврат товара на склад'
                        '(нужно вернуть товар отправителю). '
                    ),
                    'point_type': 'return',
                },
            ],
            'only_last_point_left': [
                {
                    'message': (
                        'Возможно исполнитель просто забыл закрыть заказ. '
                    ),
                    'value': True,
                },
                {'message': '', 'value': False},
            ],
        },
        'queue': 'functional_driver',
        'summary': 'ПРОТУХШИЙ ЗАКАЗ доставки {taxi_order_id}',
        'tags': ['cargo_expired_callback'],
        'extra_support_tags_by_tariff': TARIFF_TO_TAG,
    }


@pytest.mark.config(
    CARGO_DISPATCH_EXPIRED_ORDERS_SETTINGS={
        'enabled': True,
        'support_call_inactive_seconds_by_tariff': {'__default__': -100},
        'support_call_inactive_seconds': -100,
        'unprocessed_limit': 1000,
    },
)
async def test_support_notified(
        happy_path_state_performer_found,
        stq,
        run_expired_orders,
        read_waybill_info,
        mock_cargo_orders_performer_info,
        waybill_ref='waybill_fb_3',
):
    """
        Performer found only for waybill_fb_3.
        Its time to notify support due to
            `now + support_call_inactive_seconds_by_tariff < last update`.

        Check for stq and its parameters.
    """
    result = await run_expired_orders()
    assert result['stats'] == {
        'skiped_expired_orders': 0,
        'support_tickets_created': 1,
        'total_expired_orders': 1,
    }
    assert stq.support_info_cargo_callback_on_expired.times_called == 1

    waybill_info = await read_waybill_info(waybill_ref)
    cargo_order_id = waybill_info['diagnostics']['order_id']
    taxi_order_id = waybill_info['execution']['taxi_order_info']['order_id']

    kwargs = stq.support_info_cargo_callback_on_expired.next_call()['kwargs']
    assert kwargs['cargo_order_id'] == cargo_order_id
    assert kwargs['driver_phone_id'] == '+70000000000_id'
    assert kwargs['taxi_order_id'] == f'taxi_{cargo_order_id}'
    assert kwargs['waybill_ref'] == waybill_ref
    # no points visited
    assert kwargs['support_meta'] == {
        'description': (
            'Исполнитель слишком долго выполняет заказ. Исполнитель забрал '
            'посылку. Исполнитель не подтвердил получение посылки. '
        ),
        'queue': 'functional_driver',
        'summary': f'ПРОТУХШИЙ ЗАКАЗ доставки {taxi_order_id}',
        'tags': ['cargo_expired_callback'],
    }


@pytest.mark.config(
    CARGO_DISPATCH_EXPIRED_ORDERS_SETTINGS={
        'enabled': True,
        'support_call_inactive_seconds_by_tariff': {'__default__': -100},
        'support_call_inactive_seconds': -100,
        'unprocessed_limit': 1000,
    },
)
@pytest.mark.config(CARGO_DISPATCH_SUPPORT_TICKET_COUNTRIES=['blr'])
async def test_support_not_notified(
        happy_path_state_performer_found,
        stq,
        run_expired_orders,
        read_waybill_info,
        mock_cargo_orders_performer_info,
        waybill_ref='waybill_fb_3',
):
    """
        No 'rus' in CARGO_DISPATCH_SUPPORT_TICKET_COUNTRIES
    """
    result = await run_expired_orders()
    assert result['stats'] == {
        'skiped_expired_orders': 1,
        'support_tickets_created': 0,
        'total_expired_orders': 1,
    }

    assert stq.support_info_cargo_callback_on_expired.times_called == 0


@pytest.mark.config(
    CARGO_DISPATCH_EXPIRED_ORDERS_SETTINGS={
        'enabled': True,
        'support_call_inactive_seconds_by_tariff': {'__default__': -100},
        'support_call_inactive_seconds': -100,
        'unprocessed_limit': 1000,
    },
    CARGO_EXPIRED_CALLBACK_SETTINGS=_callback_config(),
)
async def test_support_tag_added(
        happy_path_state_performer_found,
        mock_cargo_orders_bulk_info,
        stq,
        run_expired_orders,
        read_waybill_info,
        mock_cargo_orders_performer_info,
        tariff_class='cargo',
        waybill_ref='waybill_fb_3',
):
    """
        Check support_meta has additional tag depending on
        performer tariff class.
    """
    mock_cargo_orders_bulk_info(tariff_class=tariff_class)
    result = await run_expired_orders()
    assert result['stats'] == {
        'skiped_expired_orders': 0,
        'total_expired_orders': 1,
        'support_tickets_created': 1,
    }
    assert stq.support_info_cargo_callback_on_expired.times_called == 1

    kwargs = stq.support_info_cargo_callback_on_expired.next_call()['kwargs']
    assert kwargs['support_meta']['tags'] == [
        'cargo_expired_callback',
        TARIFF_TO_TAG[tariff_class],
    ]


@pytest.mark.config(
    CARGO_DISPATCH_EXPIRED_ORDERS_SETTINGS={
        'enabled': True,
        'support_call_inactive_seconds_by_tariff': {
            '__default__': -100,
            'cargo': 100,
        },
        'support_call_inactive_seconds': -100,
        'unprocessed_limit': 1000,
    },
    CARGO_EXPIRED_CALLBACK_SETTINGS=_callback_config(),
)
async def test_tariff_check(
        happy_path_state_performer_found,
        mock_cargo_orders_bulk_info,
        stq,
        run_expired_orders,
        read_waybill_info,
        mock_cargo_orders_performer_info,
        tariff_class='cargo',
        waybill_ref='waybill_fb_3',
):
    result = await run_expired_orders()
    assert result['stats'] == {
        'skiped_expired_orders': 1,
        'total_expired_orders': 0,
        'support_tickets_created': 1,
    }
