# pylint: disable=import-only-modules
import json

import pytest

from tests_grocery_dispatch import configs
from tests_grocery_dispatch import constants as const
from tests_grocery_dispatch.plugins.models import PerformerInfo
from tests_grocery_dispatch.plugins.models import StatusMeta


DISPATCH_TYPE = 'cargo_sync'


@pytest.mark.now(const.NOW)
async def test_order_taking_event_production(
        taxi_grocery_dispatch,
        cargo,
        grocery_dispatch_pg,
        cargo_pg,
        stq,
        published_events,
):
    dispatch = grocery_dispatch_pg.create_dispatch(
        dispatch_name=DISPATCH_TYPE,
        status='scheduled',
        performer=PerformerInfo(),
    )
    cargo_pg.create_claim(
        dispatch_id=dispatch.dispatch_id, claim_id=const.CLAIM_ID,
    )

    cargo.add_performer(
        claim_id=const.CLAIM_ID,
        eats_profile_id=const.EATS_PROFILE_ID,
        driver_id=const.DRIVER_ID,
        park_id=const.PARK_ID,
        name=const.PERFORMER_NAME,
    )

    request = {'dispatch_id': dispatch.dispatch_id}

    # Set performer_found cargo status
    cargo.set_data(
        items=cargo.convert_items(dispatch.order.items),
        status='performer_found',
        courier_name='test_courier_name',
    )
    await taxi_grocery_dispatch.post('/internal/dispatch/v1/status', request)

    # Set pickuped cargo status
    cargo.set_data(
        items=cargo.convert_items(dispatch.order.items), status='pickuped',
    )
    await taxi_grocery_dispatch.post('/internal/dispatch/v1/status', request)

    assert (
        stq.grocery_performer_communications_order_taking_notify.times_called
        == 1
    )

    call_data = (
        stq.grocery_performer_communications_order_taking_notify.next_call()
    )

    # TODO check only expected in test
    # fields that not send
    excluded_fields = {
        'location',
        'door_code_extra',
        'doorbell_name',
        'building_name',
    }
    call_data['kwargs'].pop('log_extra')
    order_arg = json.loads(
        dispatch.order.json(exclude_none=True, exclude=excluded_fields),
    )

    # stq task id
    assert call_data['id'] == f'{dispatch.performer_id}_{dispatch.order_id}'
    # stq kwargs
    assert call_data['kwargs'] == {
        'performer_id': dispatch.performer_id,
        'order': order_arg,
    }

    # wait logbroker publish
    assert (
        (await published_events.wait('grocery-performer-pickup-order'))[1]
        == {
            'order_id': dispatch.order_id,
            'performer_id': dispatch.performer_id,
            'depot_id': dispatch.order.depot_id,
            'timestamp': const.NOW,
        }
    )


@pytest.mark.now(const.NOW)
async def test_order_event_bus_matched_arrived_delivered(
        taxi_grocery_dispatch,
        cargo,
        grocery_dispatch_pg,
        cargo_pg,
        published_events,
):
    dispatch = grocery_dispatch_pg.create_dispatch(
        dispatch_name=DISPATCH_TYPE,
        status='scheduled',
        performer=PerformerInfo(),
        status_meta=StatusMeta(
            cargo_dispatch={'dispatch_delivery_type': 'yandex_taxi'},
        ),
    )
    cargo_pg.create_claim(
        dispatch_id=dispatch.dispatch_id, claim_id=const.CLAIM_ID,
    )

    cargo.add_performer(
        claim_id=const.CLAIM_ID,
        eats_profile_id=const.EATS_PROFILE_ID,
        driver_id=const.DRIVER_ID,
        park_id=const.PARK_ID,
        name=const.PERFORMER_NAME,
    )

    request = {'dispatch_id': dispatch.dispatch_id}

    # event set only for delivered, finished ans matched statuses
    for _, status in enumerate(
            [
                'matched',
                'performer_found',
                'delivery_arrived',
                'ready_for_delivery_confirmation',
                'delivered',
                'delivered_finish',
            ],
    ):
        cargo.set_data(
            items=cargo.convert_items(dispatch.order.items),
            status=status,
            courier_name='test_courier_name',
        )
        await taxi_grocery_dispatch.post(
            '/internal/dispatch/v1/status', request,
        )

    # wait logbroker publish

    assert (await published_events.wait('grocery-order-matched'))[1] == {
        'order_id': dispatch.order_id,
        'performer_id': dispatch.performer_id,
        'depot_id': dispatch.order.depot_id,
        'claim_id': const.CLAIM_ID,
        'timestamp': const.NOW,
        'delivery_type': 'yandex_taxi',
    }

    assert (
        (await published_events.wait('grocery-performer-delivering-arrived'))[
            1
        ]
        == {
            'order_id': dispatch.order_id,
            'performer_id': dispatch.performer_id,
            'depot_id': dispatch.order.depot_id,
            'timestamp': const.NOW,
        }
    )

    assert (await published_events.wait('grocery-order-delivered'))[1] == {
        'order_id': dispatch.order_id,
        'performer_id': dispatch.performer_id,
        'depot_id': dispatch.order.depot_id,
        'timestamp': const.NOW,
    }


@pytest.mark.now(const.NOW)
async def test_no_duplication_events_if_status_not_changed_after_update(
        taxi_grocery_dispatch,
        cargo,
        grocery_dispatch_pg,
        cargo_pg,
        published_events,
):
    dispatch = grocery_dispatch_pg.create_dispatch(
        dispatch_name=DISPATCH_TYPE,
        status='scheduled',
        performer=PerformerInfo(),
    )
    cargo_pg.create_claim(
        dispatch_id=dispatch.dispatch_id, claim_id=const.CLAIM_ID,
    )

    cargo.add_performer(
        claim_id=const.CLAIM_ID,
        eats_profile_id=const.EATS_PROFILE_ID,
        driver_id=const.DRIVER_ID,
        park_id=const.PARK_ID,
        name=const.PERFORMER_NAME,
    )

    request = {'dispatch_id': dispatch.dispatch_id}

    # Set performer_found cargo status
    cargo.set_data(
        items=cargo.convert_items(dispatch.order.items),
        status='performer_found',
        courier_name='test_courier_name',
    )

    # call update status twice
    await taxi_grocery_dispatch.post('/internal/dispatch/v1/status', request)
    await taxi_grocery_dispatch.post('/internal/dispatch/v1/status', request)

    # Set pickuped cargo status
    cargo.set_data(
        items=cargo.convert_items(dispatch.order.items), status='pickuped',
    )
    await taxi_grocery_dispatch.post('/internal/dispatch/v1/status', request)
    previous_events = (
        await published_events.wait_until('grocery-performer-pickup-order')
    )[2]
    assert len(previous_events) == 1


@pytest.mark.now(const.NOW)
async def test_delivery_cancel_when_order_canceled(
        taxi_grocery_dispatch,
        mockserver,
        cargo,
        grocery_dispatch_pg,
        cargo_pg,
        published_events,
):

    dispatch_info = grocery_dispatch_pg.create_dispatch(
        dispatch_name=DISPATCH_TYPE,
        status='scheduled',
        performer=PerformerInfo(),
    )
    cargo_pg.create_claim(
        dispatch_id=dispatch_info.dispatch_id,
        claim_id=const.CLAIM_ID,
        claim_version=123,
    )

    cargo.add_performer(
        claim_id=const.CLAIM_ID,
        eats_profile_id=const.EATS_PROFILE_ID,
        driver_id=const.DRIVER_ID,
        park_id=const.PARK_ID,
        name=const.PERFORMER_NAME,
    )

    cargo.set_data(
        items=cargo.convert_items(dispatch_info.order.items),
        delivered_eta_ts=const.DELIVERY_ETA_TS,
        version=123,
        courier_name='test_courier_name',
    )

    req = {'dispatch_id': dispatch_info.dispatch_id, 'cancel_type': 'paid'}

    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/claims/cancel',
    )
    def _mock_cancel(request):
        version = request.json['version']
        assert version == 123

        return {
            'id': request.args['claim_id'],
            'status': 'cancelled',
            'version': version,
        }

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/cancel', req,
    )
    assert response.status_code == 200
    assert _mock_cancel.times_called == 1

    assert (
        (await published_events.wait('grocery-order-delivery-canceled'))[1]
        == {
            'order_id': dispatch_info.order_id,
            'performer_id': dispatch_info.performer_id,
            'depot_id': dispatch_info.order.depot_id,
            'timestamp': const.NOW,
        }
    )


@pytest.mark.now(const.NOW)
@configs.DISPATCH_CLAIM_CONFIG
@configs.DISPATCH_GENERAL_CONFIG
@configs.DISPATCH_COMMENT_CONFIG
@configs.DISPATCH_BATCHING_CONFIG
@configs.DISPATCH_DEPOT_ADDRESS_CONFIG
@configs.DISPATCH_PRIORITY_CONFIG_TAXI
async def test_delivery_cancel_when_order_rescheduled(
        taxi_grocery_dispatch,
        yamaps_local,
        personal,
        cargo,
        experiments3,
        grocery_dispatch_pg,
        cargo_pg,
        published_events,
        grocery_supply,
        stq,
        stq_runner,
):

    performer = PerformerInfo()
    cargo.add_performer(
        claim_id=const.CLAIM_ID,
        eats_profile_id=performer.eats_profile_id,
        driver_id=performer.driver_id,
        park_id=performer.park_id,
    )

    cargo.add_performer(
        claim_id=const.CLAIM_ID_2,
        eats_profile_id=const.PROFILE_ID,
        driver_id=const.DRIVER_ID,
        park_id=const.PARK_ID,
    )

    dispatch = grocery_dispatch_pg.create_dispatch(
        dispatch_name=DISPATCH_TYPE,
        status='scheduled',
        status_meta=StatusMeta(is_order_assembled=True),
        performer=performer,
    )
    assert dispatch.performer_id == performer.performer_id
    cargo_pg.create_claim(
        dispatch_id=dispatch.dispatch_id, claim_id=const.CLAIM_ID,
    )

    cargo.set_data(
        items=cargo.convert_items(dispatch.order.items),
        new_claim=const.CLAIM_ID_2,
        delivered_eta_ts=const.DELIVERY_ETA_TS,
        courier_name='test_courier_name',
    )

    request = {
        'order_id': dispatch.order_id,
        'options': {'taxi_only': True, 'disable_batching': True},
        'idempotency_token': 'token',
    }

    # will be checked at cargo mock
    cargo.custom_context = {
        'delivery_flags': {'is_forbidden_to_be_in_batch': True},
        'external_feature_prices': {'external_order_created_ts': const.NOW_TS},
        'depot_id': dispatch.order.depot_id,
        'lavka_has_market_parcel': False,
        'order_id': dispatch.order.order_id,
        'dispatch_wave': 1,
        'created': dispatch.order.created.isoformat(),
        'weight': 0.0,
        'dispatch_id': dispatch.dispatch_id,
        'region_id': 213,
        'personal_phone_id': dispatch.order.personal_phone_id,
    }
    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v2/manual/reschedule', request,
    )
    assert response.status_code == 200
    assert stq.grocery_dispatch_reschedule_executor.times_called == 1

    task_id = f'{dispatch.dispatch_id}_token'
    await stq_runner.grocery_dispatch_reschedule_executor.call(
        task_id=task_id,
        kwargs={
            'dispatch_id': dispatch.dispatch_id,
            'idempotency_token': 'token',
        },
    )

    assert dispatch.performer_id != performer.performer_id
    assert (
        (await published_events.wait('grocery-order-delivery-canceled'))[1]
        == {
            'order_id': dispatch.order_id,
            'performer_id': performer.performer_id,
            'depot_id': dispatch.order.depot_id,
            'timestamp': const.NOW,
        }
    )
