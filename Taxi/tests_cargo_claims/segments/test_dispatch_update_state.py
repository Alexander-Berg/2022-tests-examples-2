# pylint: disable=too-many-lines
import pytest

from testsuite.utils import matching


GET_TAXI_PERFORMER_INFO_SQL = """
    SELECT
        cs.uuid AS segment_uuid,
        p.dispatch_revision,
        p.taxi_order_id,
        p.order_alias_id,
        p.phone_pd_id,
        p.name,
        p.driver_id,
        p.park_id,
        p.park_clid,
        p.park_name,
        p.park_org_name,
        p.car_id,
        p.car_number,
        p.car_model,
        p.lookup_version
    FROM cargo_claims.taxi_performer_info AS p
    INNER JOIN cargo_claims.claim_segments AS cs
        ON cs.id = p.segment_id
    WHERE cs.uuid = %s
"""


@pytest.fixture(name='get_segment_info')
def _get_segment_info(pgsql):
    async def _wrapper(segment_id: str, check_performer: bool = True):
        cursor = pgsql['cargo_claims'].dict_cursor()

        performer_info = None
        cursor.execute(GET_TAXI_PERFORMER_INFO_SQL, (segment_id,))
        result = cursor.fetchone()
        if result:
            performer_info = dict(result)

        cursor.execute(
            """
            SELECT  dispatch_revision,
                    status,
                    resolution,
                    cargo_order_id,
                    provider_order_id,
                    route_id,
                    router_id
            FROM cargo_claims.claim_segments
            WHERE uuid = %s
        """,
            (segment_id,),
        )
        segment = dict(cursor.fetchone())

        if performer_info and check_performer:
            assert (
                segment['provider_order_id'] == performer_info['taxi_order_id']
            )

        return {'segment': segment, 'performer': performer_info}

    return _wrapper


async def test_performer_found(
        taxi_cargo_claims,
        get_segment,
        get_segment_info,
        get_segment_id,
        create_segment,
        build_segment_update_request,
        stq,
        taxi_order_id='taxi_order_id_1',
):
    await create_segment()
    segment_id = await get_segment_id()

    for _ in range(2):
        response = await taxi_cargo_claims.post(
            'v1/segments/dispatch/bulk-update-state',
            json={
                'segments': [
                    build_segment_update_request(segment_id, taxi_order_id),
                ],
            },
        )
        assert response.status_code == 200

        info = await get_segment_info(segment_id)
        assert info == {
            'performer': {
                'segment_uuid': segment_id,
                'dispatch_revision': 1,
                'taxi_order_id': taxi_order_id,
                'order_alias_id': 'order_alias_id_1',
                'phone_pd_id': '+70000000000_pd',
                'name': 'Kostya',
                'driver_id': 'driver_id1',
                'park_id': 'park_id1',
                'park_clid': 'park_clid1',
                'park_name': 'park_name_1',
                'park_org_name': 'park_org_name_1',
                'car_id': 'car_id_1',
                'car_number': 'car_number_1',
                'car_model': 'car_model_1',
                'lookup_version': 1,
            },
            'segment': {
                'dispatch_revision': 1,
                'provider_order_id': taxi_order_id,
                'cargo_order_id': matching.AnyString(),
                'resolution': None,
                'status': 'performer_found',
                'route_id': None,
                'router_id': None,
            },
        }

    claim_id = (await get_segment(segment_id))['diagnostics']['claim_id']

    assert stq.cargo_claims_documents_store.times_called == 1
    stq_call = stq.cargo_claims_documents_store.next_call()
    assert stq_call['kwargs']['claim_id'] == claim_id
    assert stq_call['kwargs']['document_type'] == 'act'
    assert stq_call['kwargs']['status'] == 'performer_found'
    assert stq_call['kwargs']['driver_id'] == 'driver_id1'
    assert stq_call['kwargs']['park_id'] == 'park_id1'

    # not called for not post-payment claims
    assert stq.cargo_claims_set_payment_performer.times_called == 0

    assert stq.cargo_claims_create_confirmation_codes.times_called == 1
    assert (
        stq.cargo_claims_create_confirmation_codes.next_call()['kwargs'][
            'claim_uuid'
        ]
        == claim_id
    )


async def test_cancelled_by_early_hold(
        taxi_cargo_claims,
        get_segment_id,
        create_segment,
        build_segment_update_request,
        pgsql,
        get_default_headers,
        taxi_order_id='taxi_order_id_1',
):
    await create_segment()
    segment_id = await get_segment_id()

    response = await taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={
            'segments': [
                build_segment_update_request(
                    segment_id,
                    taxi_order_id,
                    resolution='cancelled_by_early_hold',
                ),
            ],
        },
    )
    assert response.status_code == 200

    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute('SELECT source, code FROM cargo_claims.claim_warnings')
    assert ('taxi_requirements', 'cancelled_by_early_hold') in cursor


@pytest.mark.config(
    CARGO_CLAIMS_DISTLOCK_PROCESSING_EVENTS_SETTINGS={
        'enabled': True,
        'sleep_ms': 50,
        'new_event_chunk_size': 1,
    },
)
async def test_performer_found_event_created(
        taxi_cargo_claims,
        get_segment,
        get_segment_info,
        get_segment_id,
        create_segment,
        procaas_claim_status_filter,
        procaas_event_kind_filter,
        build_segment_update_request,
        stq,
        pgsql,
        taxi_order_id='taxi_order_id_1',
):
    await procaas_claim_status_filter()
    await procaas_event_kind_filter()

    await create_segment()
    segment_id = await get_segment_id()
    response = await taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={
            'segments': [
                build_segment_update_request(segment_id, taxi_order_id),
            ],
        },
    )
    assert response.status_code == 200
    claim_id = (await get_segment(segment_id))['diagnostics']['claim_id']
    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        f"""
            SELECT * FROM cargo_claims.processing_events
            WHERE item_id = '{claim_id}'
        """,
    )
    event = list(cursor)[3]
    assert event[1] == claim_id
    assert event[4]['data'] == {
        'claim_revision': 6,
        'claim_origin': 'api',
        'corp_client_id': '01234567890123456789012345678912',
        'driver_profile_id': 'driver_id1',
        'park_id': 'park_id1',
        'is_terminal': False,
        'current_point_id': 1,
        'phoenix_claim': False,
        'skip_client_notify': False,
        'cargo_order_id': '9db1622e-582d-4091-b6fc-4cb2ffdc12c0',
        'zone_id': 'moscow',
        'custom_context': {},
    }


async def test_performer_found_not_all_fields(
        taxi_cargo_claims,
        get_segment_id,
        create_segment,
        testpoint,
        build_segment_update_request,
        taxi_order_id='taxi_order_id_1',
):
    await create_segment()
    segment_id = await get_segment_id()

    @testpoint('update-segment-dispatch-state')
    def testpoint_finish(data):
        pass

    response = await taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={
            'segments': [
                build_segment_update_request(
                    segment_id, taxi_order_id, with_park=False,
                ),
            ],
        },
    )

    assert response.status_code == 200
    assert response.json() == {'processed_segment_ids': [segment_id]}

    assert testpoint_finish.next_call()['data'] == {
        'updated_segments_count': 1,
        'segments_with_upserted_performer': 1,
        'segments_with_changed_claim_kind_after_perf_found': 0,
    }


async def test_multiple_calls(
        taxi_cargo_claims,
        get_segment_id,
        create_segment,
        testpoint,
        build_segment_update_request,
        taxi_order_id='taxi_order_id_1',
):
    await create_segment()
    segment_id = await get_segment_id()

    @testpoint('update-segment-dispatch-state')
    def testpoint_finish(data):
        pass

    for i in range(2):
        response = await taxi_cargo_claims.post(
            'v1/segments/dispatch/bulk-update-state',
            json={
                'segments': [
                    build_segment_update_request(segment_id, taxi_order_id),
                ],
            },
        )
        assert response.status_code == 200

        assert testpoint_finish.next_call()['data'] == {
            'updated_segments_count': 1 - i,
            'segments_with_upserted_performer': 1 - i,
            'segments_with_changed_claim_kind_after_perf_found': 0,
        }

    response = await taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={
            'segments': [
                build_segment_update_request(
                    segment_id, 'taxi_order_id_2', revision=2,
                ),
            ],
        },
    )
    assert response.status_code == 200

    assert testpoint_finish.next_call()['data'] == {
        'updated_segments_count': 1,
        'segments_with_upserted_performer': 1,
        'segments_with_changed_claim_kind_after_perf_found': 0,
    }


@pytest.mark.parametrize(
    'resolution, expected_status',
    [('failed', 'cancelled_by_taxi'), ('technical_fail', 'failed')],
)
async def test_resolution(
        taxi_cargo_claims,
        get_segment_info,
        get_segment_id,
        create_segment,
        testpoint,
        build_segment_update_request,
        stq,
        resolution: str,
        expected_status: str,
        taxi_order_id='taxi_order_id_1',
):
    claim_info = await create_segment()
    segment_id = await get_segment_id()

    # prepare
    response = await taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={
            'segments': [
                build_segment_update_request(segment_id, taxi_order_id),
            ],
        },
    )

    assert response.status_code == 200

    @testpoint('update-segment-dispatch-state')
    def testpoint_finish(data):
        pass

    # test
    response = await taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={
            'segments': [
                build_segment_update_request(
                    segment_id,
                    taxi_order_id,
                    revision=2,
                    resolution=resolution,
                ),
            ],
        },
    )

    assert response.status_code == 200

    assert testpoint_finish.next_call()['data'] == {
        'updated_segments_count': 1,
        'segments_with_upserted_performer': 0,
        'segments_with_changed_claim_kind_after_perf_found': 0,
    }

    info = await get_segment_info(segment_id)
    assert info == {
        'performer': {
            'segment_uuid': segment_id,
            'dispatch_revision': 1,
            'taxi_order_id': taxi_order_id,
            'order_alias_id': 'order_alias_id_1',
            'phone_pd_id': '+70000000000_pd',
            'name': 'Kostya',
            'driver_id': 'driver_id1',
            'park_id': 'park_id1',
            'park_clid': 'park_clid1',
            'park_name': 'park_name_1',
            'park_org_name': 'park_org_name_1',
            'car_id': 'car_id_1',
            'car_number': 'car_number_1',
            'car_model': 'car_model_1',
            'lookup_version': 1,
        },
        'segment': {
            'dispatch_revision': 2,
            'provider_order_id': taxi_order_id,
            'cargo_order_id': matching.AnyString(),
            'resolution': 'failed',
            'status': expected_status,
            'route_id': None,
            'router_id': None,
        },
    }

    assert stq.cargo_claims_change_claim_order_price.times_called == 1
    kwargs = stq.cargo_claims_change_claim_order_price.next_call()['kwargs']

    assert kwargs['cargo_ref_id'] == claim_info.claim_id
    assert kwargs['new_price'] == ''
    assert kwargs['reason_code'] == 'dragon_initial_price'

    assert stq.cargo_claims_segment_finished.times_called == 1
    kwargs = stq.cargo_claims_segment_finished.next_call()['kwargs']

    assert kwargs['segment_id'] == segment_id


async def test_order_created(
        taxi_cargo_claims,
        get_segment_info,
        get_segment_id,
        create_segment,
        build_segment_update_request,
        taxi_order_id='taxi_order_id_1',
):
    await create_segment()
    segment_id = await get_segment_id()

    response = await taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={
            'segments': [
                build_segment_update_request(
                    segment_id, taxi_order_id, with_performer=False,
                ),
            ],
        },
    )
    assert response.status_code == 200

    info = await get_segment_info(segment_id)
    assert info == {
        'performer': None,
        'segment': {
            'dispatch_revision': 1,
            'provider_order_id': taxi_order_id,
            'cargo_order_id': matching.AnyString(),
            'resolution': None,
            'status': 'performer_draft',
            'route_id': None,
            'router_id': None,
        },
    }


async def test_performer_found_after_order_created(
        taxi_cargo_claims,
        get_segment_info,
        get_segment_id,
        create_segment,
        build_segment_update_request,
        taxi_order_id='taxi_order_id_1',
):
    await create_segment()
    segment_id = await get_segment_id()

    # Order created
    response = await taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={
            'segments': [
                build_segment_update_request(
                    segment_id, taxi_order_id, with_performer=False,
                ),
            ],
        },
    )
    assert response.status_code == 200

    # Performer found
    response = await taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={
            'segments': [
                build_segment_update_request(
                    segment_id, taxi_order_id, revision=2,
                ),
            ],
        },
    )
    assert response.status_code == 200

    info = await get_segment_info(segment_id)
    assert info['performer']['name'] == 'Kostya'
    assert info['segment']['status'] == 'performer_found'


async def test_order_created_after_performer_found(
        taxi_cargo_claims,
        get_segment_info,
        get_segment_id,
        create_segment,
        build_segment_update_request,
        taxi_order_id='taxi_order_id_1',
):
    await create_segment()
    segment_id = await get_segment_id()

    # Performer found
    response = await taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={
            'segments': [
                build_segment_update_request(
                    segment_id, taxi_order_id, revision=2,
                ),
            ],
        },
    )
    assert response.status_code == 200

    # Order created
    response = await taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={
            'segments': [
                build_segment_update_request(
                    segment_id,
                    taxi_order_id,
                    with_performer=False,
                    revision=1,
                ),
            ],
        },
    )
    assert response.status_code == 200

    info = await get_segment_info(segment_id)
    assert info['performer']['name'] == 'Kostya'
    assert info['segment']['status'] == 'performer_found'


@pytest.mark.parametrize(
    'is_pickuped, cancel_state, claim_status',
    [
        (False, 'free', 'cancelled'),
        (False, 'paid', 'cancelled_with_payment'),
        (True, 'paid', 'cancelled_with_items_on_hands'),
    ],
)
async def test_notify_cancel_state(
        taxi_cargo_claims,
        prepare_state,
        get_segment,
        get_claim,
        get_segment_id,
        build_segment_update_request,
        is_pickuped: bool,
        cancel_state: str,
        claim_status: str,
        taxi_order_id='taxi_order_id_1',
):
    visit_order = 2 if is_pickuped else 1
    segment_id = await prepare_state(visit_order=visit_order)

    response = await taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={
            'segments': [
                build_segment_update_request(
                    segment_id,
                    taxi_order_id,
                    revision=2,
                    cancel_state=cancel_state,
                ),
            ],
        },
    )
    assert response.status_code == 200

    segment = await get_segment(segment_id)
    claim = await get_claim(segment['diagnostics']['claim_id'])

    assert claim['status'] == claim_status


@pytest.mark.config(CARGO_CLAIMS_UPDATE_TAXI_CANCEL_STATE=False)
async def test_disable_taxi_cancel_state(
        taxi_cargo_claims,
        prepare_state,
        get_segment,
        get_claim,
        get_segment_id,
        build_segment_update_request,
        taxi_order_id='taxi_order_id_1',
):
    segment_id = await prepare_state(visit_order=1)

    response = await taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={
            'segments': [
                build_segment_update_request(
                    segment_id, taxi_order_id, revision=2, cancel_state='paid',
                ),
            ],
        },
    )
    assert response.status_code == 200

    segment = await get_segment(segment_id)
    claim = await get_claim(segment['diagnostics']['claim_id'])

    assert claim['status'] == 'ready_for_pickup_confirmation'


@pytest.mark.parametrize('autocancel_reason', ['candidates_empty', None])
async def test_performer_not_found(
        taxi_cargo_claims,
        get_segment_info,
        get_segment_id,
        create_segment,
        build_segment_update_request,
        get_segment,
        get_claim,
        autocancel_reason,
):
    taxi_order_id = 'taxi_order_id_1'
    await create_segment()
    segment_id = await get_segment_id()

    response = await taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={
            'segments': [
                build_segment_update_request(
                    segment_id,
                    taxi_order_id,
                    with_performer=False,
                    resolution='performer_not_found',
                    autocancel_reason=autocancel_reason,
                ),
            ],
        },
    )
    assert response.status_code == 200

    info = await get_segment_info(segment_id)
    expected = {
        'performer': None,
        'segment': {
            'dispatch_revision': 1,
            'provider_order_id': taxi_order_id,
            'cargo_order_id': matching.AnyString(),
            'resolution': 'performer_not_found',
            'status': 'performer_not_found',
            'route_id': None,
            'router_id': None,
        },
    }
    assert info == expected

    segment = await get_segment(segment_id)
    claim = await get_claim(segment['diagnostics']['claim_id'])

    if autocancel_reason is not None:
        claim['autocancel_reason'] = autocancel_reason


@pytest.mark.parametrize(
    'admin_cancel_reason', ['performer_blame.reason_performer_blame', None],
)
async def test_admin_cancel_reason(
        taxi_cargo_claims,
        get_segment_info,
        get_segment_id,
        create_segment,
        build_segment_update_request,
        get_segment,
        get_claim,
        admin_cancel_reason,
        state_controller,
):
    taxi_order_id = 'taxi_order_id_1'
    await create_segment()
    segment_id = await get_segment_id()

    response = await taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={
            'segments': [
                build_segment_update_request(
                    segment_id,
                    taxi_order_id,
                    with_performer=False,
                    revision=2,
                    resolution='failed',
                    admin_cancel_reason=admin_cancel_reason,
                ),
            ],
        },
    )
    assert response.status_code == 200

    info = await get_segment_info(segment_id)
    expected = {
        'performer': None,
        'segment': {
            'dispatch_revision': 2,
            'provider_order_id': taxi_order_id,
            'cargo_order_id': matching.AnyString(),
            'resolution': 'failed',
            'status': 'cancelled_by_taxi',
            'route_id': None,
            'router_id': None,
        },
    }
    assert info == expected

    segment = await get_segment(segment_id)
    claim = await get_claim(segment['diagnostics']['claim_id'])

    if admin_cancel_reason is not None:
        claim['admin_cancel_reason'] = admin_cancel_reason


async def test_segment_after_reorder(
        taxi_cargo_claims,
        get_segment_info,
        get_segment_id,
        create_segment,
        build_segment_update_request,
        pgsql,
):
    await create_segment()
    segment_id = await get_segment_id()
    taxi_order_id = 'taxi_order_id_1'

    # Set performer_found
    response = await taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={
            'segments': [
                build_segment_update_request(segment_id, taxi_order_id),
            ],
        },
    )
    assert response.status_code == 200
    info = await get_segment_info(segment_id)
    assert info['performer']
    assert info['segment']['status'] == 'performer_found'

    # Reorder segment
    response = await taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={
            'segments': [
                build_segment_update_request(
                    segment_id,
                    taxi_order_id,
                    revision=3,
                    with_performer=False,
                    with_order=False,
                ),
            ],
        },
    )
    assert response.status_code == 200
    info = await get_segment_info(segment_id, check_performer=False)
    assert info['segment']['status'] == 'performer_lookup'


async def test_reset_segment_execution(
        taxi_cargo_claims,
        testpoint,
        get_segment,
        get_segment_info,
        get_segment_id,
        create_segment_with_performer,
        build_segment_update_request,
):
    await create_segment_with_performer()
    segment_id = await get_segment_id()

    @testpoint('reset-segment-execution')
    def reset_segment_execution(data):
        pass

    for i in range(2):
        # call twice to check for double updates
        response = await taxi_cargo_claims.post(
            'v1/segments/dispatch/bulk-update-state',
            json={
                'segments': [
                    build_segment_update_request(
                        segment_id,
                        taxi_order_id=None,
                        with_order=False,
                        with_performer=False,
                        revision=2 + i,
                    ),
                ],
            },
        )
        assert response.status_code == 200

    assert reset_segment_execution.next_call()['data'] == {
        'deleted_performer_info_count': 1,
        'deleted_points_ready_for_interact_notifications_count': 0,
        'deleted_documents_count': 0,
        'cleared_claims_count': 1,
        'cleared_claim_segments_count': 1,
        'cleared_claim_segment_points_count': 3,
        'cleared_claim_points_count': 3,
    }
    assert not reset_segment_execution.has_calls

    segment = await get_segment(segment_id)
    for point in segment['points']:
        assert point['visit_status'] == 'pending'
        assert not point['is_resolved']

    assert segment['status'] == 'performer_lookup'

    info = await get_segment_info(segment_id)
    assert info == {
        'performer': None,
        'segment': {
            'cargo_order_id': None,
            'dispatch_revision': 3,
            'provider_order_id': None,
            'resolution': None,
            'status': 'performer_lookup',
            'route_id': None,
            'router_id': None,
        },
    }


async def test_reset_with_order(
        taxi_cargo_claims,
        testpoint,
        get_segment,
        get_segment_info,
        get_segment_id,
        create_segment_with_performer,
        build_segment_update_request,
        taxi_order_id='taxi_order_id_1',
        new_cargo_order_id='1aa9cee6-fabc-43a1-aa71-c5b6ec9ed2eb',
):
    await create_segment_with_performer()
    segment_id = await get_segment_id()

    @testpoint('reset-segment-execution')
    def reset_segment_execution(data):
        pass

    response = await taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={
            'segments': [
                build_segment_update_request(
                    segment_id,
                    taxi_order_id,
                    cargo_order_id=new_cargo_order_id,
                    with_performer=False,
                    revision=2,
                ),
            ],
        },
    )
    assert response.status_code == 200

    assert reset_segment_execution.next_call()['data'] == {
        'deleted_performer_info_count': 1,
        'deleted_points_ready_for_interact_notifications_count': 0,
        'deleted_documents_count': 0,
        'cleared_claims_count': 1,
        'cleared_claim_segments_count': 1,
        'cleared_claim_segment_points_count': 3,
        'cleared_claim_points_count': 3,
    }

    segment = await get_segment(segment_id)
    for point in segment['points']:
        assert point['visit_status'] == 'pending'
        assert not point['is_resolved']

    assert segment['status'] == 'performer_draft'

    info = await get_segment_info(segment_id)
    assert info == {
        'performer': None,
        'segment': {
            'cargo_order_id': new_cargo_order_id,
            'dispatch_revision': 2,
            'provider_order_id': taxi_order_id,
            'resolution': None,
            'status': 'performer_draft',
            'route_id': None,
            'router_id': None,
        },
    }


async def test_reset_with_performer(
        taxi_cargo_claims,
        testpoint,
        get_segment,
        get_segment_info,
        get_segment_id,
        create_segment_with_performer,
        build_segment_update_request,
        taxi_order_id='taxi_order_id_1',
        new_cargo_order_id='1aa9cee6-fabc-43a1-aa71-c5b6ec9ed2eb',
):
    await create_segment_with_performer()
    segment_id = await get_segment_id()

    @testpoint('update-segment-dispatch-state')
    def update_state(data):
        pass

    response = await taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={
            'segments': [
                build_segment_update_request(
                    segment_id,
                    taxi_order_id,
                    cargo_order_id=new_cargo_order_id,
                    with_performer=True,
                    revision=2,
                ),
            ],
        },
    )
    assert response.status_code == 200

    assert update_state.next_call()['data'] == {
        'segments_with_changed_claim_kind_after_perf_found': 0,
        'segments_with_upserted_performer': 1,
        'updated_segments_count': 1,
    }

    info = await get_segment_info(segment_id)
    assert info == {
        'performer': {
            'segment_uuid': segment_id,
            'dispatch_revision': 1,
            'taxi_order_id': taxi_order_id,
            'order_alias_id': 'order_alias_id_1',
            'phone_pd_id': '+70000000000_pd',
            'name': 'Kostya',
            'driver_id': 'driver_id1',
            'park_id': 'park_id1',
            'park_clid': 'park_clid1',
            'park_name': 'park_name_1',
            'park_org_name': 'park_org_name_1',
            'car_id': 'car_id_1',
            'car_number': 'car_number_1',
            'car_model': 'car_model_1',
            'lookup_version': 1,
        },
        'segment': {
            'dispatch_revision': 2,
            'provider_order_id': taxi_order_id,
            'cargo_order_id': new_cargo_order_id,
            'resolution': None,
            'status': 'performer_found',
            'route_id': None,
            'router_id': None,
        },
    }


@pytest.mark.parametrize(
    'resolution', ['failed', 'technical_fail', 'performer_not_found'],
)
async def test_emergency_sms(
        taxi_cargo_claims,
        stq,
        get_segment,
        get_segment_id,
        create_segment,
        build_segment_update_request,
        resolution: str,
        taxi_order_id='taxi_order_id_1',
):
    await create_segment()
    segment_id = await get_segment_id()

    response = await taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={
            'segments': [
                build_segment_update_request(
                    segment_id,
                    taxi_order_id,
                    with_performer=False,
                    resolution=resolution,
                ),
            ],
        },
    )
    assert response.status_code == 200

    assert stq.cargo_claims_send_cancel_sms.times_called == 1
    stq_call = stq.cargo_claims_send_cancel_sms.next_call()

    segment = await get_segment(segment_id)
    claim_id = segment['diagnostics']['claim_id']
    assert stq_call['id'] == claim_id


async def test_autoreorder_flow_callback(
        taxi_cargo_claims,
        get_segment,
        get_segment_id,
        create_segment,
        build_segment_update_request,
        taxi_order_id='taxi_order_id_1',
):
    """
        /bulk-update-state with autoreorder_flow = newway
        => stored autoreorder_flow = newway
    """
    await create_segment()
    segment_id = await get_segment_id()

    response = await taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={
            'segments': [
                build_segment_update_request(
                    segment_id,
                    taxi_order_id,
                    with_performer=False,
                    autoreorder_flow='newway',
                ),
            ],
        },
    )
    assert response.status_code == 200

    info = await get_segment(segment_id)
    assert info['autoreorder_flow'] == 'newway'


async def test_change_price_on_user_cancel(
        taxi_cargo_claims,
        create_segment,
        get_segment_id,
        build_segment_update_request,
        get_default_headers,
        stq,
        mock_cargo_pricing_calc,
        mock_waybill_info,
        taxi_order_id='taxi_order_id_1',
):
    creator = await create_segment()
    segment_id = await get_segment_id()

    response = await taxi_cargo_claims.post(
        f'/api/integration/v2/claims/cancel',
        params={'claim_id': creator.claim_id},
        json={'version': 1, 'cancel_state': 'paid'},
        headers=get_default_headers(),
    )
    assert response.status_code == 200

    # dispatch notify claims about dispatch_segment resolved
    response = await taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={
            'segments': [
                build_segment_update_request(
                    segment_id,
                    taxi_order_id,
                    revision=2,
                    resolution='cancelled',
                ),
            ],
        },
    )
    assert response.status_code == 200

    # check stq is set on cancel
    assert stq.cargo_claims_change_claim_order_price.times_called == 1
    kwargs = stq.cargo_claims_change_claim_order_price.next_call()['kwargs']

    assert kwargs['cargo_ref_id'] == creator.claim_id
    assert kwargs['new_price'] == ''
    assert kwargs['reason_code'] == 'dragon_initial_price'


async def test_expired_segment(
        taxi_cargo_claims,
        get_segment_info,
        get_segment_id,
        create_segment,
        testpoint,
        build_segment_update_request,
        stq,
):
    await create_segment()
    segment_id = await get_segment_id()
    response = await taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={
            'segments': [
                build_segment_update_request(
                    segment_id,
                    taxi_order_id=None,
                    with_order=False,
                    with_performer=False,
                    resolution='performer_not_found',
                ),
            ],
        },
    )
    assert response.status_code == 200

    info = await get_segment_info(segment_id)
    assert info == {
        'performer': None,
        'segment': {
            'dispatch_revision': 1,
            'resolution': 'performer_not_found',
            'status': 'performer_not_found',
            'cargo_order_id': None,
            'provider_order_id': None,
            'route_id': None,
            'router_id': None,
        },
    }


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_claims_execution_reset',
    consumers=['cargo-claims/geocoder'],
    clauses=[],
    default_value={
        'reset_points_on_new_driver_found': True,
        'validate_driver_on_arrive_at_point': False,
    },
    is_config=True,
)
async def test_reset_with_new_driver(
        taxi_cargo_claims,
        testpoint,
        get_segment,
        get_segment_info,
        get_segment_id,
        create_segment_with_performer,
        get_default_cargo_order_id,
        build_segment_update_request,
        taxi_order_id='taxi_order_id_1',
):
    """
    Expected new status: performer_draft
    """

    await create_segment_with_performer()
    segment_id = await get_segment_id()

    @testpoint('reset-segment-execution')
    def reset_segment_execution(data):
        pass

    response = await taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={
            'segments': [
                build_segment_update_request(
                    segment_id,
                    taxi_order_id,
                    with_performer=True,
                    driver_id='new_driver_132',
                    revision=2,
                ),
            ],
        },
    )
    assert response.status_code == 200

    assert reset_segment_execution.next_call()['data'] == {
        'deleted_performer_info_count': 1,
        'deleted_points_ready_for_interact_notifications_count': 0,
        'deleted_documents_count': 0,
        'cleared_claims_count': 1,
        'cleared_claim_segments_count': 1,
        'cleared_claim_segment_points_count': 3,
        'cleared_claim_points_count': 3,
    }

    segment = await get_segment(segment_id)
    for point in segment['points']:
        assert point['visit_status'] == 'pending'
        assert not point['is_resolved']

    assert segment['status'] == 'performer_found'

    info = await get_segment_info(segment_id)
    assert info == {
        'performer': {
            'segment_uuid': segment_id,
            'dispatch_revision': 1,
            'taxi_order_id': taxi_order_id,
            'order_alias_id': 'order_alias_id_1',
            'phone_pd_id': '+70000000000_pd',
            'name': 'Kostya',
            'driver_id': 'new_driver_132',
            'park_id': 'park_id1',
            'park_clid': 'park_clid1',
            'park_name': 'park_name_1',
            'park_org_name': 'park_org_name_1',
            'car_id': 'car_id_1',
            'car_number': 'car_number_1',
            'car_model': 'car_model_1',
            'lookup_version': 1,
        },
        'segment': {
            'cargo_order_id': get_default_cargo_order_id,
            'dispatch_revision': 2,
            'provider_order_id': taxi_order_id,
            'resolution': None,
            'status': 'performer_found',
            'route_id': None,
            'router_id': None,
        },
    }


@pytest.mark.parametrize(
    'with_resolution', [None, 'performer_not_found', 'cancelled'],
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_claims_execution_reset',
    consumers=['cargo-claims/geocoder'],
    clauses=[],
    default_value={
        'reset_points_on_new_driver_found': True,
        'validate_driver_on_arrive_at_point': False,
        'reset_points_on_empty_driver': True,
    },
    is_config=True,
)
async def test_reset_with_empty_driver(
        taxi_cargo_claims,
        testpoint,
        get_segment,
        get_segment_info,
        get_segment_id,
        create_segment_with_performer,
        get_default_cargo_order_id,
        build_segment_update_request,
        with_resolution,
        taxi_order_id='taxi_order_id',
):
    await create_segment_with_performer()
    segment_id = await get_segment_id()

    @testpoint('reset-segment-execution')
    def reset_segment_execution(data):
        pass

    update_state_segment = {}
    if with_resolution:
        update_state_segment = build_segment_update_request(
            segment_id,
            taxi_order_id,
            with_performer=True,
            driver_id='driver_id1',
            revision=2,
            autocancel_reason='candidates_no_one_accepted',
            resolution=with_resolution,
        )
    else:
        update_state_segment = build_segment_update_request(
            segment_id, taxi_order_id, with_performer=False, revision=2,
        )
    response = await taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={'segments': [update_state_segment]},
    )
    assert response.status_code == 200

    if with_resolution == 'cancelled':
        assert reset_segment_execution.times_called == 0
    else:
        assert reset_segment_execution.next_call()['data'] == {
            'deleted_performer_info_count': 1,
            'deleted_points_ready_for_interact_notifications_count': 0,
            'deleted_documents_count': 0,
            'cleared_claims_count': 1,
            'cleared_claim_segments_count': 1,
            'cleared_claim_segment_points_count': 3,
            'cleared_claim_points_count': 3,
        }

    segment = await get_segment(segment_id)
    assert (
        segment['status'] == 'performer_found'
        if with_resolution == 'cancelled'
        else 'performer_draft'
    )

    info = await get_segment_info(segment_id)
    if with_resolution == 'cancelled':
        assert info['performer'] is not None
    else:
        assert info['performer'] is None


@pytest.mark.parametrize('will_be_thrown', (False, True))
async def test_update_state_for_partly_invalid_bulk(
        taxi_cargo_claims,
        build_segment_update_request,
        create_segment_with_performer,
        get_db_segment_ids,
        taxi_config,
        state_controller,
        will_be_thrown,
        taxi_order_id='taxi_order_id_1',
):
    taxi_config.set(CARGO_CLAIMS_UPDATE_SEGMENT_STATE_THROW=will_be_thrown)

    await create_segment_with_performer(claim_index=0)
    await create_segment_with_performer(claim_index=1)
    seg1, seg2 = await get_db_segment_ids()

    # don't create segment, we want get exception
    response = await taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={
            'segments': [
                build_segment_update_request(seg1, taxi_order_id),
                build_segment_update_request(
                    'invalid_segment_id', taxi_order_id,
                ),
                build_segment_update_request(seg2, taxi_order_id),
            ],
        },
    )

    if will_be_thrown:
        assert response.json() == {
            'code': '500',
            'message': 'Internal Server Error',
        }
    else:
        assert response.status_code == 200
        response_segments = sorted(response.json()['processed_segment_ids'])
        assert response_segments == sorted([seg1, seg2])


@pytest.mark.parametrize(
    'segment_revision, expected_processed_segment_ids',
    [
        (1, [matching.AnyString()]),
        # Dispatch has outdated segment version, so do not update segment
        (0, []),
    ],
)
async def test_use_segment_revision(
        taxi_cargo_claims,
        get_segment_info,
        get_segment_id,
        get_segment,
        create_segment,
        build_segment_update_request,
        segment_revision: int,
        expected_processed_segment_ids: list,
        taxi_order_id='taxi_order_id_1',
):
    await create_segment()
    segment_id = await get_segment_id()

    response = await taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={
            'segments': [
                build_segment_update_request(
                    segment_id,
                    taxi_order_id,
                    with_performer=False,
                    segment_revision=segment_revision,
                ),
            ],
        },
    )
    assert response.status_code == 200
    assert (
        response.json()['processed_segment_ids']
        == expected_processed_segment_ids
    )

    info = await get_segment_info(segment_id)
    if expected_processed_segment_ids:
        # Segment was updated
        assert info == {
            'performer': None,
            'segment': {
                'dispatch_revision': 1,
                'provider_order_id': taxi_order_id,
                'cargo_order_id': matching.AnyString(),
                'resolution': None,
                'status': 'performer_draft',
                'route_id': None,
                'router_id': None,
            },
        }
    else:
        # Segment was not updated
        assert info == {
            'performer': None,
            'segment': {
                'dispatch_revision': 0,
                'provider_order_id': None,
                'cargo_order_id': None,
                'resolution': None,
                'status': 'performer_lookup',
                'route_id': None,
                'router_id': None,
            },
        }


async def test_reset_segment_with_revision(
        taxi_cargo_claims,
        testpoint,
        get_segment,
        get_segment_info,
        get_segment_id,
        create_segment_with_performer,
        build_segment_update_request,
        taxi_order_id='taxi_order_id_2',
):
    # Dispatch request: segment_revision = X
    # Then segment was reset, and revision was set to X + 1
    # Then we updated segment and revision was set to X + 2

    await create_segment_with_performer()
    segment_id = await get_segment_id()

    @testpoint('reset-segment-execution')
    def reset_segment_execution(data):
        pass

    response = await taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={
            'segments': [
                build_segment_update_request(
                    segment_id,
                    taxi_order_id=taxi_order_id,
                    cargo_order_id='1aa9cee6-fabc-43a1-aa71-c5b6ec9ed2eb',
                    with_performer=False,
                    revision=2,
                    segment_revision=2,
                ),
            ],
        },
    )

    assert reset_segment_execution.has_calls

    assert response.status_code == 200
    assert response.json()['processed_segment_ids'] == [matching.AnyString()]

    seg = await get_segment(segment_id)
    assert seg['claim_revision'] == 4


async def test_payment_performer_found(
        enable_payment_on_delivery,
        mock_payments_check_token,
        create_segment_with_performer,
        stq,
        mock_payment_create,
        mock_payment_set_performer,
        get_segment_info,
        taxi_order_id='taxi_order_id_1',
):
    """
        Check cargo_claims_set_payment_performer was called.
    """
    segment_info = await create_segment_with_performer(payment_method='card')
    segment_id = segment_info.id

    info = await get_segment_info(segment_id)
    assert info['performer']['name'] == 'Kostya'
    assert info['segment']['status'] == 'performer_found'

    assert stq.cargo_claims_set_payment_performer.times_called == 1


@pytest.fixture(name='mock_stq_errors')
async def _mock_stq_errors(mockserver):
    async def wrapper():
        @mockserver.json_handler(
            r'/stq-agent/queues/api/add/(?P<queue_name>\w+)/bulk', regex=True,
        )
        async def mock(request, queue_name):
            if context.status_code == 500:
                return mockserver.make_response(
                    status=context.status_code,
                    json={
                        'code': context.error_code,
                        'message': context.error_message,
                    },
                )
            data = request.json
            response = {'tasks': []}
            for task in data['tasks']:
                response['tasks'].append(
                    {
                        'task_id': task['task_id'],
                        'add_result': {'code': context.task_result_code},
                    },
                )
            return response

        class Context:
            def __init__(self):
                self.task_result_code = 500
                self.status_code = 200
                self.handler = mock
                self.error_code = 'internal_error'
                self.error_message = 'error message'

        context = Context()
        return context

    return wrapper


@pytest.mark.parametrize(
    'bulk_add_status_code,bulk_add_task_result_code', [(200, 500), (500, 200)],
)
@pytest.mark.config(
    STQ_AGENT_CLIENT_QOS={'__default__': {'attempts': 1, 'timeout-ms': 1000}},
)
async def test_payment_performer_found_stq_error(
        taxi_cargo_claims,
        enable_payment_on_delivery,
        mock_payments_check_token,
        create_segment_with_performer,
        stq,
        mock_payment_create,
        mock_payment_set_performer,
        mock_stq_errors,
        get_segment_info,
        build_segment_update_request,
        bulk_add_status_code: int,
        bulk_add_task_result_code: int,
        taxi_order_id='taxi_order_id_1',
):
    """
        Check stq set bulk failure doesn't lead to 500 on whole handler.
    """
    segment_info = await create_segment_with_performer(payment_method='card')
    segment_id = segment_info.id
    stq.cargo_claims_set_payment_performer.flush()

    # mock bulk to return result codes 500
    my_stq = await mock_stq_errors()
    my_stq.status_code = bulk_add_status_code
    my_stq.task_result_code = bulk_add_task_result_code

    response = await taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={
            'segments': [
                build_segment_update_request(segment_id, taxi_order_id),
            ],
        },
    )
    assert response.status_code == 200
    # check no segments processed
    assert response.json() == {'processed_segment_ids': []}
    assert my_stq.handler.times_called == 2


@pytest.mark.config(
    CARGO_CLAIMS_DISTLOCK_PROCESSING_EVENTS_SETTINGS={
        'enabled': True,
        'sleep_ms': 50,
        'new_event_chunk_size': 1,
    },
)
@pytest.mark.parametrize(
    'is_pickuped, cancel_state, claim_status, tariff_class, order_flow_type',
    [
        (False, 'free', 'cancelled', 'eda', 'native'),
        (False, 'paid', 'cancelled_with_payment', 'eda', 'native'),
        (True, 'paid', 'cancelled_with_items_on_hands', 'lavka', 'retail'),
    ],
)
async def test_bulk_update_segment_cancel_procaas_event(
        taxi_cargo_claims,
        prepare_state,
        get_segment,
        get_claim,
        build_segment_update_request,
        pgsql,
        procaas_claim_status_filter,
        procaas_event_kind_filter,
        tariff_class,
        order_flow_type,
        is_pickuped: bool,
        cancel_state: str,
        claim_status: str,
        taxi_order_id='taxi_order_id_1',
):
    await procaas_claim_status_filter()
    await procaas_event_kind_filter()

    due = '2020-08-14T18:37:00+00:00'
    visit_order = 2 if is_pickuped else 1
    segment_id = await prepare_state(
        visit_order=visit_order,
        taxi_class=tariff_class,
        custom_context={'order_flow_type': order_flow_type},
        due=due,
    )

    response = await taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={
            'segments': [
                build_segment_update_request(
                    segment_id,
                    taxi_order_id,
                    revision=2,
                    cancel_state=cancel_state,
                ),
            ],
        },
    )
    assert response.status_code == 200

    segment = await get_segment(segment_id)
    claim = await get_claim(segment['diagnostics']['claim_id'])

    assert claim['status'] == claim_status

    claim_id = (await get_segment(segment_id))['diagnostics']['claim_id']
    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        f"""
        SELECT id, payload FROM cargo_claims.processing_events
        WHERE item_id = '{claim_id}'
        """,
    )

    data = list(cursor)
    assert len(data) == 7 if not is_pickuped else 8
    (new_index, new_payload) = data[0]
    assert new_index == 1
    assert new_payload == {
        'data': {
            'claim_uuid': claim_id,
            'claim_origin': 'api',
            'corp_client_id': segment['corp_client_id'],
            'is_terminal': False,
            'skip_client_notify': False,
        },
        'kind': 'status-change-succeeded',
        'status': 'new',
    }

    (found_index, found_payload) = data[3]
    assert found_index == 4
    assert found_payload == {
        'data': {
            'claim_revision': 6,
            'corp_client_id': segment['corp_client_id'],
            'driver_profile_id': segment['performer_info']['driver_id'],
            'claim_origin': 'api',
            'park_id': segment['performer_info']['park_id'],
            'is_terminal': False,
            'current_point_id': 1,
            'phoenix_claim': False,
            'skip_client_notify': False,
            'cargo_order_id': '9db1622e-582d-4091-b6fc-4cb2ffdc12c0',
            'zone_id': 'moscow',
            'tariff_class': tariff_class,
            'due': due,
            'custom_context': {'order_flow_type': order_flow_type},
        },
        'kind': 'status-change-succeeded',
        'status': 'performer_found',
    }

    (pickup_arrived_index, pickup_arrived_payload) = data[4]
    assert pickup_arrived_index == 5
    assert pickup_arrived_payload == {
        'data': {
            'is_terminal': False,
            'claim_origin': 'api',
            'claim_revision': 7,
            'phoenix_claim': False,
            'current_point_id': 1,
            'skip_client_notify': False,
            'corp_client_id': segment['corp_client_id'],
            'custom_context': {'order_flow_type': order_flow_type},
            'zone_id': 'moscow',
        },
        'kind': 'status-change-succeeded',
        'status': 'pickup_arrived',
    }

    (rfpc_index, rfpc_payload) = data[5]
    assert rfpc_index == 6
    assert 'claim_revision' in rfpc_payload['data']
    del rfpc_payload['data']['claim_revision']
    assert rfpc_payload == {
        'data': {
            'phoenix_claim': False,
            'claim_origin': 'api',
            'is_terminal': False,
            'current_point_id': 1,
            'skip_client_notify': False,
            'corp_client_id': segment['corp_client_id'],
        },
        'kind': 'status-change-succeeded',
        'status': 'ready_for_pickup_confirmation',
    }

    (terminal_index, terminal_payload) = data[6 if not is_pickuped else 9]
    assert terminal_index == 7 if not is_pickuped else 10
    assert 'claim_revision' in terminal_payload['data']
    del terminal_payload['data']['claim_revision']
    assert terminal_payload == {
        'data': {
            'cargo_order_id': segment['cargo_order_id'],
            'corp_client_id': segment['corp_client_id'],
            'claim_origin': 'api',
            'driver_profile_id': segment['performer_info']['driver_id'],
            'park_id': segment['performer_info']['park_id'],
            'lookup_version': 1,
            'phoenix_claim': False,
            'is_terminal': True,
            'current_point_id': 1 if not is_pickuped else 2,
            'resolution': 'failed',
            'route_points': [],
            'skip_client_notify': False,
            'zone_id': 'moscow',
            'custom_context': {'order_flow_type': order_flow_type},
        },
        'kind': 'status-change-succeeded',
        'status': claim_status,
    }


@pytest.mark.config(
    CARGO_CLAIMS_DISTLOCK_PROCESSING_EVENTS_SETTINGS={
        'enabled': True,
        'sleep_ms': 50,
        'new_event_chunk_size': 1,
    },
)
@pytest.mark.parametrize(
    'segment_resolution, claim_status',
    [
        ('failed', 'cancelled_by_taxi'),
        ('technical_fail', 'failed'),
        ('cancelled_by_early_hold', 'failed'),
    ],
)
async def test_failed_resolutions_events(
        taxi_cargo_claims,
        prepare_state,
        get_segment,
        get_claim,
        build_segment_update_request,
        pgsql,
        procaas_claim_status_filter,
        procaas_event_kind_filter,
        claim_status: str,
        segment_resolution: str,
        taxi_order_id='taxi_order_id_1',
):
    await procaas_claim_status_filter()
    await procaas_event_kind_filter()

    segment_id = await prepare_state(visit_order=1)

    # Set performer info for real test
    response = await taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={
            'segments': [
                build_segment_update_request(segment_id, taxi_order_id),
            ],
        },
    )
    assert response.status_code == 200

    response = await taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={
            'segments': [
                build_segment_update_request(
                    segment_id,
                    taxi_order_id,
                    revision=3,
                    resolution=segment_resolution,
                ),
            ],
        },
    )
    assert response.status_code == 200

    segment = await get_segment(segment_id)
    claim_id = segment['diagnostics']['claim_id']
    claim = await get_claim(claim_id)
    assert claim['status'] == claim_status

    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        f"""
        SELECT payload FROM cargo_claims.processing_events
        WHERE item_id = '{claim_id}'
        ORDER BY id
        """,
    )

    data = list(cursor)
    assert len(data) == 7
    payload = data[-1][0]
    assert payload == {
        'data': {
            'cargo_order_id': segment['cargo_order_id'],
            'corp_client_id': segment['corp_client_id'],
            'claim_origin': 'api',
            'phoenix_claim': False,
            'is_terminal': True,
            'claim_revision': 10,
            'current_point_id': 1,
            'resolution': 'failed',
            'route_points': [],
            'skip_client_notify': False,
            'zone_id': 'moscow',
        },
        'kind': 'status-change-succeeded',
        'status': claim_status,
    }


@pytest.mark.parametrize(
    'segment_resolution, expected_claim_status',
    [
        ('failed', 'cancelled_by_taxi'),
        ('performer_not_found', 'performer_not_found'),
    ],
)
async def test_points_resolution(
        taxi_cargo_claims,
        get_segment_id,
        create_segment,
        build_segment_update_request,
        state_controller,
        segment_resolution,
        expected_claim_status,
        taxi_order_id='taxi_order_id_1',
):
    await create_segment()
    segment_id = await get_segment_id()

    response = await taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={
            'segments': [
                build_segment_update_request(
                    segment_id,
                    taxi_order_id,
                    with_performer=False,
                    revision=2,
                    resolution=segment_resolution,
                ),
            ],
        },
    )
    assert response.status_code == 200

    new_claim_info = await state_controller.get_claim_info()
    assert new_claim_info.current_state.status == expected_claim_status

    for point in new_claim_info.points:
        assert point.visit_status == 'skipped'


async def test_router_id(
        taxi_cargo_claims,
        get_segment,
        get_segment_info,
        get_segment_id,
        create_segment,
        build_segment_update_request,
        taxi_order_id='taxi_order_id_1',
        router_id='some_router',
        route_id='12345',
):
    await create_segment()
    segment_id = await get_segment_id()

    response = await taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={
            'segments': [
                build_segment_update_request(
                    segment_id,
                    taxi_order_id,
                    route_id=route_id,
                    router_id=router_id,
                ),
            ],
        },
    )
    assert response.status_code == 200

    info = await get_segment_info(segment_id)
    assert info == {
        'performer': {
            'segment_uuid': segment_id,
            'dispatch_revision': 1,
            'taxi_order_id': taxi_order_id,
            'order_alias_id': 'order_alias_id_1',
            'phone_pd_id': '+70000000000_pd',
            'name': 'Kostya',
            'driver_id': 'driver_id1',
            'park_id': 'park_id1',
            'park_clid': 'park_clid1',
            'park_name': 'park_name_1',
            'park_org_name': 'park_org_name_1',
            'car_id': 'car_id_1',
            'car_number': 'car_number_1',
            'car_model': 'car_model_1',
            'lookup_version': 1,
        },
        'segment': {
            'dispatch_revision': 1,
            'provider_order_id': taxi_order_id,
            'cargo_order_id': matching.AnyString(),
            'resolution': None,
            'status': 'performer_found',
            'route_id': route_id,
            'router_id': router_id,
        },
    }


@pytest.mark.config(
    CARGO_CLAIMS_STQ_CHANGE_PRICE_FROM_BULK_UPDATE_STATE_ENABLED=False,
)
async def test_change_price_disabled(
        taxi_cargo_claims,
        create_segment,
        get_segment_id,
        build_segment_update_request,
        get_default_headers,
        stq,
        mock_cargo_pricing_calc,
        mock_waybill_info,
):
    creator = await create_segment()
    segment_id = await get_segment_id()

    response = await taxi_cargo_claims.post(
        f'/api/integration/v2/claims/cancel',
        params={'claim_id': creator.claim_id},
        json={'version': 1, 'cancel_state': 'paid'},
        headers=get_default_headers(),
    )
    assert response.status_code == 200

    response = await taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={
            'segments': [
                build_segment_update_request(
                    segment_id, segment_id, revision=2, resolution='cancelled',
                ),
            ],
        },
    )
    assert response.status_code == 200

    # check stq is not set
    assert stq.cargo_claims_change_claim_order_price.times_called == 0


async def test_failed_ordercommit(
        taxi_cargo_claims,
        create_segment,
        pgsql,
        procaas_event_kind_filter,
        procaas_claim_status_filter,
):
    await procaas_claim_status_filter()
    await procaas_event_kind_filter()

    claim_info = await create_segment()

    response = await taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={
            'segments': [
                {
                    'autoreorder_flow': 'oldway',
                    'cargo_order_id': '7586b551-fbbc-4880-b01f-ed5f80891a40',
                    'claims_segment_revision': 1,
                    'id': claim_info.claim_id,
                    'resolution': 'technical_fail',
                    'revision': 2,
                    'router_id': 'fallback_router',
                },
            ],
        },
    )
    assert response.status_code == 200

    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        'SELECT id, payload '
        + 'FROM cargo_claims.processing_events '
        + 'WHERE item_id = \'{}\''.format(claim_info.claim_id),
    )
    for row in cursor:
        payload = row[1]['data']
        if payload['is_terminal']:
            terminal_event = row

    assert terminal_event[1] == {
        'data': {
            'corp_client_id': '01234567890123456789012345678912',
            'claim_origin': 'api',
            'phoenix_claim': False,
            'is_terminal': True,
            'resolution': 'failed',
            'route_points': [],
            'skip_client_notify': False,
            'claim_revision': 6,
            'current_point_id': 1,
            'zone_id': 'moscow',
        },
        'kind': 'status-change-succeeded',
        'status': 'failed',
    }
