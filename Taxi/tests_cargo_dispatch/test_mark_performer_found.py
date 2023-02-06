import pytest

from testsuite.utils import matching


CARGO_CHANGE_DESTINATIONS = [
    'dragon_performer_found',
    'point_skipped',
    'return',
]


def build_performer_request(waybill_id, cargo_order_id, **kwargs):
    return {
        'waybill_id': waybill_id,
        'order_id': cargo_order_id,
        'taxi_order_id': 'taxi-order-id',
        'order_alias_id': 'taxi-order-alias',
        'phone_pd_id': 'phone_pd_id',
        'name': 'Kostya',
        'driver_id': '789',
        'park_id': '123456789',
        'car_id': '123',
        'car_number': 'А001АА77',
        'car_model': 'KAMAZ',
        'lookup_version': 1,
        'tariff_class': 'cargo',
        **kwargs,
    }


async def test_basic(
        taxi_cargo_dispatch,
        happy_path_state_orders_created,
        read_waybill_info,
        waybill_id='waybill_fb_3',
        cargo_order_id='29533fe3-5fa1-4d91-9e51-57758531a4a1',
):
    waybill0 = await read_waybill_info(waybill_id)
    for revision in (1, 2):
        response = await taxi_cargo_dispatch.post(
            '/v1/waybill/mark/taxi-order-performer-found',
            json=build_performer_request(
                waybill_id, cargo_order_id, lookup_version=revision,
            ),
        )
        assert response.status_code == 200
        waybill = await read_waybill_info(waybill_id)
        assert (
            waybill['dispatch']['revision']
            == waybill0['dispatch']['revision'] + revision
        )

    # check that revision is not incremented
    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/mark/taxi-order-performer-found',
        json=build_performer_request(
            waybill_id, cargo_order_id, lookup_version=1,
        ),
    )
    assert response.status_code == 200


async def test_not_found(
        taxi_cargo_dispatch,
        waybill_id='does-not-exist',
        cargo_order_id='29533fe3-5fa1-4d91-9e51-57758531a4a1',
):
    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/mark/taxi-order-performer-found',
        json=build_performer_request(waybill_id, cargo_order_id),
    )
    assert response.status_code == 404


@pytest.mark.config(CARGO_CHANGE_DESTINATIONS=CARGO_CHANGE_DESTINATIONS)
async def test_change_destinations(
        taxi_cargo_dispatch,
        happy_path_state_orders_created,
        read_waybill_info,
        mockserver,
        load_json,
        get_point_execution_by_visit_order,
        waybill_id='waybill_smart_1',
        cargo_order_id='29533fe3-5fa1-4d91-9e51-57758531a4a1',
):
    point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_id, visit_order=2,
    )

    @mockserver.json_handler('/cargo-orders/v1/order/change-destination')
    def change_destination(request):
        assert request.json == {
            'claim_id': 'claim_seg1',
            'claim_point_id': point['claim_point_id'],
            'dispatch_version': 1,
            'order_id': matching.AnyString(),
            'segment_id': 'seg1',
            'idempotency_token': 'cargo-dispatch-first-call_12_2',
        }
        return {}

    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/mark/taxi-order-performer-found',
        json=build_performer_request(
            waybill_id, cargo_order_id, lookup_version=1,
        ),
    )
    assert response.status_code == 200

    assert change_destination.times_called

    # Test driver info were saved
    waybill = await read_waybill_info(waybill_id)
    assert waybill['execution']['taxi_order_info']['performer_info'] == {
        'driver_id': 'driver_id_1',
        'park_id': 'park_id_1',
        'car_id': '123',
        'car_model': 'KAMAZ',
        'car_number': 'А001АА77',
        'name': 'Kostya',
        'park_name': 'some_park_name',
        'park_org_name': 'some_park_org_name',
        'tariff_class': 'cargo',
        'phone_pd_id': '+70000000000_id',
    }


@pytest.mark.config(CARGO_CHANGE_DESTINATIONS=CARGO_CHANGE_DESTINATIONS)
async def test_success_after_failed_request(
        taxi_cargo_dispatch,
        happy_path_state_orders_created,
        read_waybill_info,
        mockserver,
        load_json,
        waybill_id='waybill_smart_1',
        cargo_order_id='29533fe3-5fa1-4d91-9e51-57758531a4a1',
):
    # Fail first request
    @mockserver.json_handler('/cargo-orders/v1/order/change-destination')
    def change_destination(request):
        return mockserver.make_response(status=500, json={})

    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/mark/taxi-order-performer-found',
        json=build_performer_request(
            waybill_id, cargo_order_id, lookup_version=1,
        ),
    )
    assert response.status_code == 500
    assert change_destination.times_called

    # Second request success
    @mockserver.json_handler('/cargo-orders/v1/order/change-destination')
    def _change_destination(request):
        return {}

    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/mark/taxi-order-performer-found',
        json=build_performer_request(
            waybill_id, cargo_order_id, lookup_version=1,
        ),
    )
    assert response.status_code == 200
    assert _change_destination.times_called

    # Test driver info were saved
    waybill = await read_waybill_info(waybill_id)
    assert waybill['execution']['taxi_order_info']['performer_info'] == {
        'driver_id': 'driver_id_1',
        'park_id': 'park_id_1',
        'car_id': '123',
        'car_model': 'KAMAZ',
        'car_number': 'А001АА77',
        'name': 'Kostya',
        'park_name': 'some_park_name',
        'park_org_name': 'some_park_org_name',
        'tariff_class': 'cargo',
        'phone_pd_id': '+70000000000_id',
    }


@pytest.mark.skip()
async def test_eta_stored(
        taxi_cargo_dispatch,
        happy_path_state_orders_created,
        mock_driver_trackstory,
        mock_employee_timer,
        exp_cargo_next_point_eta_settings,
        get_point_execution_by_visit_order,
        stq,
        waybill_id='waybill_fb_3',
        cargo_order_id='29533fe3-5fa1-4d91-9e51-57758531a4a1',
):
    mock_employee_timer.expected_request = {
        'point_from': [37.57839202, 55.7350642],
        'point_to': [37.5, 55.7],
        'employer': 'eda',
        'park_driver_profile_id': '123456789_789',
    }

    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/mark/taxi-order-performer-found',
        json=build_performer_request(waybill_id, cargo_order_id),
    )
    assert response.status_code == 200

    assert mock_employee_timer.handler.times_called == 1

    # check for eta on first point
    next_point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_id, visit_order=1,
    )
    assert next_point['eta'] == '2020-07-20T11:08:00+00:00'

    # check taximeter is notified about new /state version
    assert stq.cargo_update_setcar_state_version.times_called == 1
    stq_call = stq.cargo_update_setcar_state_version.next_call()
    assert stq_call['kwargs']['driver_profile_id'] == '789'
    assert stq_call['kwargs']['park_id'] == '123456789'
    assert not stq_call['kwargs']['send_taximeter_push']


@pytest.mark.skip()
async def test_eta_stored_batch_first_segment_skipped(
        taxi_cargo_dispatch,
        happy_path_state_orders_created,
        mock_driver_trackstory,
        mock_employee_timer,
        exp_cargo_next_point_eta_settings,
        get_point_execution_by_visit_order,
        happy_path_claims_segment_db,
        waybill_id='waybill_smart_1',
        cargo_order_id='29533fe3-5fa1-4d91-9e51-57758531a4a1',
):
    """
    Waybill 'waybill_smart_1':
        seg1_A1_p1 (11) -> seg1_A2_p2 (12) -> seg2_A1_p1 (21) ->
        seg1_B1_p3 (13) -> seg1_B2_p4 (14) -> seg1_B3_p5 (15) ->
        seg2_B1_p2 (22) -> seg1_A2_p6 (12) -> seg1_A1_p7 (11) ->
        seg2_C1_p3 (23)

    Here skip seq1.
    """
    mock_employee_timer.expected_request = None

    # Client cancel claim with seg1
    happy_path_claims_segment_db.cancel_segment_by_user('seg1')

    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/mark/taxi-order-performer-found',
        json=build_performer_request(waybill_id, cargo_order_id),
    )
    assert response.status_code == 200

    assert mock_employee_timer.handler.times_called == 1

    # check for eta on first point of second segment
    next_point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_id, visit_order=3,
    )
    assert next_point['eta'] == '2020-07-20T11:08:00+00:00'


@pytest.fixture(name='fetch_chain_parent')
async def _fetch_chain_parent(pgsql):
    def wrapper(waybill_ref):
        cursor = pgsql['cargo_dispatch'].cursor()

        cursor.execute(
            """
            SELECT chain_parent_cargo_order_id
            FROM cargo_dispatch.waybills
            WHERE external_ref = %s
        """,
            (waybill_ref,),
        )
        return cursor.fetchone()[0]

    return wrapper


async def test_chain_parent_stored(
        happy_path_chain_order, read_waybill_info, fetch_chain_parent,
):
    first_waybill = await read_waybill_info('waybill_fb_3')
    first_waybill_order_id = first_waybill['diagnostics']['order_id']
    chain_parent_cargo_order_id = fetch_chain_parent('waybill_smart_1')
    assert chain_parent_cargo_order_id == first_waybill_order_id


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_patch_setcar_version_settings',
    consumers=['cargo/patch-setcar-version-settings'],
    clauses=[],
    default_value={'update_on_performer_found': True},
)
async def test_update_setcar(
        taxi_cargo_dispatch,
        happy_path_state_orders_created,
        stq,
        waybill_id='waybill_fb_3',
        cargo_order_id='29533fe3-5fa1-4d91-9e51-57758531a4a1',
):
    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/mark/taxi-order-performer-found',
        json=build_performer_request(
            waybill_id, cargo_order_id, lookup_version=1,
        ),
    )
    assert response.status_code == 200

    # Check stq was set
    assert (
        stq.cargo_increment_and_update_setcar_state_version.times_called == 1
    )
    stq_call = stq.cargo_increment_and_update_setcar_state_version.next_call()
    assert stq_call['kwargs'] == {
        'cargo_order_id': matching.AnyString(),
        'driver_profile_id': '789',
        'park_id': '123456789',
        'log_extra': {'_link': matching.AnyString()},
    }


async def test_payments_notified(
        happy_path_state_orders_created,
        happy_path_claims_segment_db,
        taxi_cargo_dispatch,
        mock_payment_set_performer,
        waybill_id='waybill_smart_1',
        segment_id='seg1',
        cargo_order_id='29533fe3-5fa1-4d91-9e51-57758531a4a1',
):
    """
        Check performer info stored in cargo-payments.
    """
    segment = happy_path_claims_segment_db.get_segment(segment_id)
    segment.set_point_post_payment('p3')
    segment.set_point_post_payment('p4')

    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/mark/taxi-order-performer-found',
        json=build_performer_request(
            waybill_id, cargo_order_id, lookup_version=1,
        ),
    )
    assert response.status_code == 200

    assert mock_payment_set_performer.requests == [
        {
            'payment_id': '757849ca-2e29-45a6-84f7-d576603618bb',
            'performer': {'driver_id': '789', 'park_id': '123456789'},
            'performer_version': 1,
            'segment_revision': 5,
        },
        {
            'payment_id': '757849ca-2e29-45a6-84f7-d576603618bb',
            'performer': {'driver_id': '789', 'park_id': '123456789'},
            'performer_version': 1,
            'segment_revision': 5,
        },
    ]
