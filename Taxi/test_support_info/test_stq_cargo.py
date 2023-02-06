import pytest

from taxi.clients import startrack

from support_info import stq_task


async def test_eda_callback_happy_path(
        support_info_app_stq,
        mock_st_create_ticket,
        mock_personal_single_phone,
):
    mock_personal_single_phone('+70009999987')
    await stq_task.cargo_eda_callback_on_cancel(
        support_info_app_stq,
        request_id='123',
        driver_phone_id='driver_phone_id_1',
        taxi_order_id='taxi_order_id_1',
        eda_order_id='eda_order_1',
    )
    create_ticket_kwargs = mock_st_create_ticket.calls[0]['kwargs']
    assert create_ticket_kwargs == {
        'queue': 'CARGOEDACANCEL',
        'description': (
            'Курьер хочет отменить заказ. '
            'Необходимо связаться с ним в ближайшее время'
        ),
        'summary': 'Запрос на обратный звонок по заказу еды eda_order_1',
        'unique': '123-eda-callback-on-cancel',
        'custom_fields': {
            'userPhone': '+70009999987',
            'FoodOrderNr': 'eda_order_1',
            'OrderId': 'taxi_order_id_1',
        },
        'tags': ['cargo_eda_cancel_callback'],
    }


async def test_no_eda_order_id(
        support_info_app_stq,
        mock_st_create_ticket,
        mock_personal_single_phone,
):
    mock_personal_single_phone('+70009999987')
    await stq_task.cargo_eda_callback_on_cancel(
        support_info_app_stq,
        request_id='123',
        driver_phone_id='driver_phone_id_1',
        taxi_order_id='taxi_order_id_1',
    )
    create_ticket_kwargs = mock_st_create_ticket.calls[0]['kwargs']
    assert create_ticket_kwargs['custom_fields'] == {
        'userPhone': '+70009999987',
        'OrderId': 'taxi_order_id_1',
    }


async def test_eda_callback_already_created(
        support_info_app_stq, mock_personal_single_phone, patch,
):
    @patch('taxi.clients.startrack.StartrackAPIClient.create_ticket')
    async def _ticket_create(*args, **kwargs):
        raise startrack.ConflictError

    mock_personal_single_phone('+70009999987')
    await stq_task.cargo_eda_callback_on_cancel(
        support_info_app_stq,
        request_id='123',
        driver_phone_id='driver_phone_id_1',
        taxi_order_id='taxi_order_id_1',
        eda_order_id='eda_order_1',
    )
    assert _ticket_create.calls


@pytest.mark.config(CARGO_CALLBACKS_ON_EXPIRED_ENABLED=True)
async def test_callback_expired_happy_path(
        support_info_app_stq,
        mock_st_create_ticket,
        mock_personal_single_phone,
        driver_phone='70009999987',
        driver_phone_id='driver_phone_id_1',
        taxi_order_id='taxi_order_id_1',
        cargo_order_id='cargo_order_id_1',
        waybill_ref='waybill_ref_1',
):
    support_meta = {
        'queue': 'functional_driver',
        'summary': 'some summary',
        'description': 'some description',
        'tags': ['some_tag'],
    }
    mock_personal_single_phone(driver_phone)
    await stq_task.cargo_callback_on_expired(
        support_info_app_stq,
        request_id='123',
        driver_phone_id=driver_phone_id,
        taxi_order_id=taxi_order_id,
        cargo_order_id=cargo_order_id,
        waybill_ref=waybill_ref,
        support_meta=support_meta,
    )

    create_ticket_kwargs = mock_st_create_ticket.calls[0]['kwargs']
    assert create_ticket_kwargs == {
        'queue': 'functional_driver',
        'description': support_meta['description'],
        'summary': support_meta['summary'],
        'unique': '123-callback-on-expired',
        'custom_fields': {
            'driverPhone': driver_phone,
            'OrderId': taxi_order_id,
        },
        'tags': support_meta['tags'],
    }
