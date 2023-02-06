import pytest

from testsuite.utils import matching


# pylint: disable=invalid-name
pytestmark = [pytest.mark.usefixtures('set_up_alive_batch_exp')]


@pytest.fixture(name='state_waybill_requested')
async def _state_waybill_requested(
        happy_path_state_fallback_waybills_proposed, read_waybill_info,
):
    return await read_waybill_info('waybill_fb_1')


async def test_all_points_have_execution(state_waybill_requested):
    waybill = state_waybill_requested
    assert len(waybill['waybill']['points']) == 7
    assert len(waybill['execution']['points']) == 7


async def test_revisions_starts_from_1(state_waybill_requested):
    waybill = state_waybill_requested
    assert waybill['dispatch']['revision'] == 1


async def test_taxi_order_requirements(state_waybill_requested):
    waybill = state_waybill_requested
    assert waybill['waybill']['taxi_order_requirements'] == {
        'taxi_classes': ['express', 'courier'],
        'door_to_door': True,
    }


async def test_no_order_info(state_waybill_requested):
    waybill = state_waybill_requested
    assert 'taxi_order_info' not in waybill['execution']


async def test_taxi_order_info(
        happy_path_state_performer_found, read_waybill_info,
):
    waybill = await read_waybill_info('waybill_fb_3')
    assert 'order_id' in waybill['execution']['taxi_order_info']
    assert (
        waybill['execution']['taxi_order_info']['last_performer_found_ts']
        == matching.any_string
    )
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


async def test_cargo_order_info(
        happy_path_state_performer_found, read_waybill_info,
):
    waybill = await read_waybill_info('waybill_fb_3')
    assert 'order_id' in waybill['execution']['taxi_order_info']
    assert waybill['execution']['state_version'] == 'v1_w_1_s_0'
    assert waybill['execution']['cargo_order_info'] == {
        'final_calc_id': 'cargo-pricing/v1/aaa',
        'order_id': matching.any_string,
        'provider_order_id': 'taxi-id',
        'presetcar_calc_id': 'cargo-pricing/v1/bbb',
        'use_cargo_pricing': True,
        'nondecoupling_client_final_calc_id': 'cargo-pricing/v1/ccc',
        'order_cancel_performer_reason_list': [],
    }


async def test_dispatch_processing(
        happy_path_state_performer_found, read_waybill_info,
):
    waybill = await read_waybill_info('waybill_fb_3')
    assert waybill['dispatch'] == {
        'created_ts': matching.any_string,
        'updated_ts': matching.any_string,
        'is_performer_assigned': False,
        'is_waybill_accepted': True,
        'is_waybill_declined': False,
        'revision': 5,
        'status': 'processing',
        'is_pull_dispatch': False,
    }


async def test_dispatch_resolved(state_cancelled_resolved, read_waybill_info):
    waybill = await read_waybill_info('waybill_fb_3')
    assert waybill['dispatch'] == {
        'created_ts': matching.any_string,
        'updated_ts': matching.any_string,
        'resolved_at': matching.any_string,
        'is_performer_assigned': False,
        'is_waybill_accepted': True,
        'is_waybill_declined': False,
        'revision': 9,
        'status': 'resolved',
        'resolution': 'cancelled',
        'is_pull_dispatch': False,
    }


async def test_special_requirements(
        state_cancelled_resolved, read_waybill_info,
):
    waybill = await read_waybill_info('waybill_fb_3')
    assert waybill['waybill']['special_requirements'] == {
        'virtual_tariffs': [
            {'class': 'cargo', 'special_requirements': [{'id': 'cargo_eds'}]},
        ],
    }


async def test_segments(state_waybill_requested, read_waybill_info):
    waybill = await read_waybill_info('waybill_fb_3')
    assert waybill['execution']['segments'] == [
        {
            'zone_id': 'moscow',
            'corp_client_id': 'corp_client_id_56789012345678912',
            'status': 'segment_status',
            'updated_ts': '1970-01-01T00:00:00+00:00',
            'id': 'seg3',
            'emergency_phone_id': 'emergency_phone_id',
            'client_info': {
                'payment_info': {
                    'type': 'corp',
                    'method_id': 'corp-5e36732e2bc54e088b1466e08e31c486',
                },
            },
            'is_skipped': False,
            'claim_id': 'claim_uuid_1',
            'claim_comment': 'best order',
            'custom_context': {'key_test': 'value_test'},
            'allow_alive_batch_v1': False,
            'allow_alive_batch_v2': False,
            'skip_act': True,
            'pricing': {
                'final_pricing_calc_id': (
                    'cargo-pricing/v1/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
                ),
            },
        },
    ]


async def test_waybill_info_admin(
        happy_path_state_performer_found,
        read_waybill_info,
        taxi_cargo_dispatch,
):
    waybill_admin = await taxi_cargo_dispatch.post(
        '/v1/admin/waybill/info',
        params={'waybill_external_ref': 'waybill_fb_3'},
        json={},
        headers={'Accept-Language': 'ru', 'X-Remote-Ip': '0.0.0.0'},
    )
    assert waybill_admin.status_code == 200
    assert 'dispatch' in waybill_admin.json()
    assert 'execution' in waybill_admin.json()
    assert 'waybill' in waybill_admin.json()
    waybill = await read_waybill_info('waybill_fb_3')
    assert (
        waybill['waybill']['external_ref']
        == waybill_admin.json()['waybill']['external_ref']
    )
    cargo_order_id = waybill['diagnostics']['order_id']
    assert cargo_order_id

    waybill_by_order = await taxi_cargo_dispatch.post(
        '/v1/admin/waybill/info',
        params={'cargo_order_id': cargo_order_id},
        json={},
        headers={'Accept-Language': 'ru', 'X-Remote-Ip': '0.0.0.0'},
    )
    assert waybill_by_order.status_code == 200
    assert (
        waybill_by_order.json()['waybill']['external_ref']
        == waybill_admin.json()['waybill']['external_ref']
    )


async def test_waybill_items(state_waybill_requested, read_waybill_info):
    waybill = await read_waybill_info('waybill_fb_3')
    assert waybill['waybill']['items'] == [
        {
            'dropoff_point': 'seg3_B1_p2',
            'item_id': 'seg3_i1',
            'pickup_point': 'seg3_A1_p1',
            'quantity': 1,
            'return_point': 'seg3_A1_p3',
            'title': '{item_id}_title',
            'size': {'height': 0.1, 'length': 0.1, 'width': 0.1},
            'weight': 0.5,
        },
    ]


async def test_points_execution(
        state_waybill_requested,
        read_waybill_info,
        get_point_execution_by_visit_order,
        waybill_ref='waybill_fb_3',
):
    point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=1,
    )

    waybill = await read_waybill_info(waybill_ref)
    assert waybill['execution']['points'][0] == {
        'claim_point_id': point['claim_point_id'],
        'is_return_required': False,
        'is_resolved': False,
        'is_segment_skipped': False,
        'label': 'point_label',
        'last_status_change_ts': '2020-06-10T07:00:00+00:00',
        'location': {'coordinates': [37.5, 55.7], 'id': 'seg3_A1'},
        'need_confirmation': True,
        'leave_under_door': True,
        'meet_outside': True,
        'no_door_call': True,
        'client_name': 'contact_on_loc_{location_id}',
        'phones': [
            {
                'label': 'point_phone_label',
                'type': 'emergency',
                'view': 'main',
            },
        ],
        'point_id': 'seg3_A1_p1',
        'segment_id': 'seg3',
        'type': 'source',
        'eta_calculation_awaited': False,
        'visit_order': 1,
        'visit_status': 'pending',
        'modifier_age_check': True,
        'external_order_id': '1234-5678-seg3_A1',
        'address': {
            'coordinates': [37.5, 55.7],
            'fullname': 'location_fullname',
            'building_name': 'building_name',
            'door_code_extra': 'door_code_extra',
            'doorbell_name': 'doorbell_name',
            'location_id': 'seg3_A1',
            'comment': 'comment_for_seg3_A1',
        },
        'changelog': [
            {
                'status': 'pending',
                'timestamp': '2020-08-15T14:31:38.055956+00:00',
                'cargo_order_id': '5e36732e-2bc5-4e08-8b14-66e08e31c486',
            },
            {
                'driver_id': 'driver_id1',
                'status': 'arrived',
                'timestamp': '2020-08-15T14:33:19.012806+00:00',
            },
            {
                'status': 'skipped',
                'timestamp': '2020-08-15T14:34:31.799456+00:00',
            },
        ],
    }


@pytest.mark.parametrize('point_visit_status', ['arrived', 'visited'])
async def test_visit_status(
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        read_waybill_info,
        point_visit_status: str,
        waybill_ref='waybill_smart_1',
):
    # prepare execution status, set arrived for only one point
    happy_path_claims_segment_db.set_segment_point_visit_status(
        'seg1', 'p1', point_visit_status, is_caused_by_user=True,
    )
    waybill = await read_waybill_info(waybill_ref)

    # check if visit status changed only for chosen point
    is_chosen_point_found = False
    for point in waybill['execution']['points']:
        is_chosen_point = (
            point['point_id'] == 'seg1_A1_p1' and point['segment_id'] == 'seg1'
        )
        if is_chosen_point:
            is_chosen_point_found = True
            assert point['visit_status'] == point_visit_status
        else:
            assert point['visit_status'] == 'pending'
    assert is_chosen_point_found


async def test_batch_with_one_cancelled_segment_1(
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        run_claims_segment_replication,
        read_waybill_info,
):
    # Client cancel claim with seg2
    happy_path_claims_segment_db.cancel_segment_by_user('seg2')
    await run_claims_segment_replication()

    waybill = await read_waybill_info('waybill_smart_1')
    waybill_points = [
        {
            'is_segment_skipped': point['is_segment_skipped'],
            'segment_id': point['segment_id'],
        }
        for point in waybill['execution']['points']
    ]
    assert waybill_points == [
        {'is_segment_skipped': False, 'segment_id': 'seg1'},
        {'is_segment_skipped': False, 'segment_id': 'seg1'},
        {'is_segment_skipped': True, 'segment_id': 'seg2'},
        {'is_segment_skipped': False, 'segment_id': 'seg1'},
        {'is_segment_skipped': False, 'segment_id': 'seg1'},
        {'is_segment_skipped': False, 'segment_id': 'seg1'},
        {'is_segment_skipped': True, 'segment_id': 'seg2'},
        {'is_segment_skipped': False, 'segment_id': 'seg1'},
        {'is_segment_skipped': False, 'segment_id': 'seg1'},
        {'is_segment_skipped': True, 'segment_id': 'seg2'},
    ]

    waybill_segments = [
        {'is_skipped': segment['is_skipped'], 'segment_id': segment['id']}
        for segment in waybill['execution']['segments']
    ]
    assert sorted(waybill_segments, key=lambda s: s['segment_id']) == [
        {'is_skipped': False, 'segment_id': 'seg1'},
        {'is_skipped': True, 'segment_id': 'seg2'},
    ]


async def test_admin_and_internal_responses_is_same(
        happy_path_state_performer_found,
        read_waybill_info,
        taxi_cargo_dispatch,
):
    waybill_ref = 'waybill_fb_3'

    # Get admin waybill response by waybill_external_ref
    waybill_admin_resp = await taxi_cargo_dispatch.post(
        '/v1/admin/waybill/info', params={'waybill_external_ref': waybill_ref},
    )
    waybill_admin_by_external_ref = waybill_admin_resp.json()

    # Get internal waybill response
    waybill_internal = await read_waybill_info('waybill_fb_3')
    cargo_order_id = waybill_internal['diagnostics']['order_id']

    # Get admin waybill response by cargo_order_id
    waybill_admin_resp = await taxi_cargo_dispatch.post(
        '/v1/admin/waybill/info',
        params={'cargo_order_id': cargo_order_id},
        json={},
        headers={'Accept-Language': 'ru', 'X-Remote-Ip': '0.0.0.0'},
    )
    waybill_admin_by_cargo_order = waybill_admin_resp.json()

    assert (
        waybill_admin_by_external_ref['execution']['points']
        == waybill_internal['execution']['points']
    )
    assert (
        waybill_admin_by_cargo_order['execution']['points']
        == waybill_internal['execution']['points']
    )


async def test_points_visit_order(
        happy_path_state_smart_waybills_proposed, read_waybill_info,
):
    waybill = await read_waybill_info('waybill_smart_1')

    detail_points = sorted(
        waybill['waybill']['points'], key=lambda x: x['point_id'],
    )
    detail_points_order = [point['visit_order'] for point in detail_points]

    execution_points = sorted(
        waybill['execution']['points'], key=lambda x: x['point_id'],
    )
    execution_points_order = [
        point['visit_order'] for point in execution_points
    ]

    assert detail_points_order == execution_points_order


async def test_get_info_by_segment_id(
        get_waybill_path_info,
        happy_path_state_performer_found,
        read_waybill_info,
        taxi_cargo_dispatch,
):
    waybill_ref = 'waybill_fb_3'

    # Get waybill by waybill_external_ref
    waybill_info = await read_waybill_info(waybill_ref)

    # Get waybill by cargo_order_id and check that they are same
    response_by_cargo_order_id = await taxi_cargo_dispatch.post(
        '/v1/waybill/info',
        params={
            'segment_id': waybill_info['waybill']['points'][0]['segment_id'],
        },
    )
    assert response_by_cargo_order_id.status_code == 200
    assert response_by_cargo_order_id.json() == waybill_info


async def test_get_info_by_cargo_order_id(
        get_waybill_path_info,
        happy_path_state_performer_found,
        read_waybill_info,
        taxi_cargo_dispatch,
):
    waybill_ref = 'waybill_fb_3'

    # Get waybill by waybill_external_ref
    waybill_info = await read_waybill_info(waybill_ref)

    # Get waybill by cargo_order_id and check that they are same
    response_by_cargo_order_id = await taxi_cargo_dispatch.post(
        '/v1/waybill/info',
        params={'cargo_order_id': waybill_info['diagnostics']['order_id']},
    )
    assert response_by_cargo_order_id.status_code == 200
    assert response_by_cargo_order_id.json() == waybill_info


async def test_no_waybill_ref_and_cargo_order_id(taxi_cargo_dispatch):
    response = await taxi_cargo_dispatch.post('/v1/waybill/info')
    assert response.status_code == 400


async def test_waybill_ref_and_cargo_order_id(taxi_cargo_dispatch):
    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/info',
        params={
            'cargo_order_id': '5e36732e-2bc5-4e08-8b14-66e08e31c486',
            'waybill_external_ref': '123',
        },
    )
    assert response.status_code == 400


async def test_get_actual_waybill(
        taxi_cargo_dispatch,
        happy_path_state_performer_found,
        happy_path_state_seg4_routers_chosen,
        waybill_from_segments,
        request_waybill_update_proposition,
        run_choose_waybills,
        mock_cargo_orders_bulk_info,
        read_waybill_info,
        update_proposition_alive_batch_stq,
):
    """
    Alive dragon
    Get new waybill by old_external_ref
    """
    mock_cargo_orders_bulk_info(tariff_class='eda')
    new_waybill_ref = 'new_waybill_ref'

    # Propose new waybill
    proposition = await waybill_from_segments(
        'smart_router', new_waybill_ref, 'seg1', 'seg2', 'seg4',
    )
    response = await request_waybill_update_proposition(
        proposition, 'waybill_smart_1',
    )
    assert response.status_code == 200

    await run_choose_waybills()
    await update_proposition_alive_batch_stq(
        new_waybill_ref, wait_testpoint=False,
    )

    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/info', params={'waybill_external_ref': 'waybill_smart_1'},
    )
    waybill = await read_waybill_info('waybill_smart_1', actual_waybill=True)
    assert response.status_code == 200
    assert waybill['waybill']['external_ref'] == new_waybill_ref


async def test_get_initial_waybill(
        taxi_cargo_dispatch,
        happy_path_state_performer_found,
        waybill_from_segments,
        request_waybill_update_proposition,
        run_choose_waybills,
        mock_cargo_orders_bulk_info,
        read_waybill_info,
        happy_path_state_seg4_routers_chosen,
):
    mock_cargo_orders_bulk_info(tariff_class='eda')

    # Propose waybill update
    proposition = await waybill_from_segments(
        'smart_router', 'update_propositions', 'seg1', 'seg2', 'seg4',
    )
    response = await request_waybill_update_proposition(
        proposition, 'waybill_smart_1',
    )
    assert response.status_code == 200

    waybill = await read_waybill_info('waybill_smart_1', actual_waybill=False)
    assert response.status_code == 200
    assert waybill['waybill']['external_ref'] == 'waybill_smart_1'


async def test_segment_allow_alive_batch(
        happy_path_state_first_import,
        set_up_segment_routers_exp,
        run_choose_routers,
        read_waybill_info,
        get_segment_info,
        propose_from_segments,
        run_choose_waybills,
):
    # Set up
    await set_up_segment_routers_exp(
        allow_alive_batch_v1=True, allow_alive_batch_v2=True,
    )
    await run_choose_routers()

    seginfo = await get_segment_info('seg1')
    assert seginfo['segment']['allow_alive_batch_v1']
    assert seginfo['segment']['allow_alive_batch_v2']

    await propose_from_segments('fallback_router', 'waybill_fb_1', 'seg1')
    await run_choose_waybills()

    waybill = await read_waybill_info('waybill_fb_1')
    assert waybill['execution']['segments'][0]['allow_alive_batch_v1']
    assert waybill['execution']['segments'][0]['allow_alive_batch_v2']


async def test_post_payment_passed(
        state_waybill_requested,
        read_waybill_info,
        get_point_execution_by_visit_order,
        happy_path_claims_segment_db,
        waybill_ref='waybill_fb_3',
        segment_id='seg3',
):
    segment = happy_path_claims_segment_db.get_segment(segment_id)
    segment.set_point_post_payment('p2')

    point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=2,
    )

    assert point['post_payment'] == {
        'id': '757849ca-2e29-45a6-84f7-d576603618bb',
        'method': 'card',
    }


async def test_cargo_c2c_order_id(
        happy_path_state_performer_found,
        happy_path_claims_segment_db,
        read_waybill_info,
):
    expected_order_id = 'cargo_c2c_order_id_1'

    happy_path_claims_segment_db.set_cargo_c2c_order_id(
        'seg3', expected_order_id,
    )
    waybill = await read_waybill_info('waybill_fb_3')

    assert (
        waybill['execution']['segments'][0]['cargo_c2c_order_id']
        == expected_order_id
    )


ORDER_CANCEL_PERFORMER_REASON_LIST = [
    {
        'taxi_order_id': 'taxi-id',
        'cargo_cancel_reason': 'reason',
        'taxi_cancel_reason': 'taxi_cancel_reason',
        'park_id': 'park_id',
        'driver_id': 'driver_id',
        'created_ts': '2020-01-27T15:40:00+00:00',
        'completed': False,
        'guilty': True,
        'need_reorder': True,
        'free_cancellations_limit_exceeded': False,
    },
    {
        'taxi_order_id': 'taxi-id',
        'cargo_cancel_reason': 'cargo_cancel_reason',
        'taxi_cancel_reason': 'taxi_cancel_reason',
        'park_id': 'park_id',
        'driver_id': 'driver_id',
        'created_ts': '2020-01-27T15:40:00+00:00',
        'completed': True,
        'guilty': True,
        'need_reorder': True,
        'free_cancellations_limit_exceeded': False,
    },
]


async def test_admin_waybil_info_with_performer_cancel(
        taxi_cargo_dispatch,
        happy_path_state_performer_found,
        happy_path_state_seg4_routers_chosen,
        mock_cargo_orders_bulk_info,
        read_waybill_info,
        update_proposition_alive_batch_stq,
):
    mock_cargo_orders_bulk_info(
        order_cancel_performer_reason=ORDER_CANCEL_PERFORMER_REASON_LIST,
    )

    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/info', params={'waybill_external_ref': 'waybill_smart_1'},
    )
    waybill = await read_waybill_info('waybill_smart_1', actual_waybill=True)
    assert response.status_code == 200
    assert (
        waybill['execution']['cargo_order_info'][
            'order_cancel_performer_reason_list'
        ]
        == ORDER_CANCEL_PERFORMER_REASON_LIST
    )


async def test_draft_error(
        happy_path_state_performer_found,
        taxi_cargo_dispatch,
        mock_order_error_info,
        waybill_ref='waybill_fb_1',
):
    draft_error = {
        'reason': 'DRAFT_ERROR',
        'message': 'INVALID_PHONE_NUMBER',
        'updated_ts': '2021-01-22T15:30:00+00:00',
    }

    handler = mock_order_error_info(
        expected_request={'waybill_ref': waybill_ref},
        response={'order_error': draft_error},
    )

    response = await taxi_cargo_dispatch.post(
        '/v1/admin/waybill/info',
        params={'waybill_external_ref': waybill_ref},
        json={},
        headers={'Accept-Language': 'ru', 'X-Remote-Ip': '0.0.0.0'},
    )

    assert response.json()['execution']['order_draft_error'] == draft_error

    assert handler.times_called == 1


async def test_segment_in_claims_not_found(
        happy_path_state_performer_found,
        taxi_cargo_dispatch,
        mock_claims_bulk_info,
        # mock_order_error_info,
        mock_cargo_orders_bulk_info,
        waybill_ref='waybill_fb_1',
        segment_id='seg1',
):
    mock_claims_bulk_info(segments_to_ignore=[segment_id])

    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/info',
        params={'waybill_external_ref': waybill_ref},
        json={},
        headers={'Accept-Language': 'ru', 'X-Remote-Ip': '0.0.0.0'},
    )

    assert response.status_code == 404
