async def test_path_by_ref(
        get_waybill_path_info, happy_path_state_fallback_waybills_proposed,
):
    response = await get_waybill_path_info('waybill_fb_1')
    assert response.status_code == 200
    assert response.json() == {
        'path': [
            {
                'segment_id': 'seg1',
                'visit_order': 1,
                'waybill_point_id': 'seg1_A1_p1',
            },
            {
                'segment_id': 'seg1',
                'visit_order': 2,
                'waybill_point_id': 'seg1_A2_p2',
            },
            {
                'segment_id': 'seg1',
                'visit_order': 3,
                'waybill_point_id': 'seg1_B1_p3',
            },
            {
                'segment_id': 'seg1',
                'visit_order': 4,
                'waybill_point_id': 'seg1_B2_p4',
            },
            {
                'segment_id': 'seg1',
                'visit_order': 5,
                'waybill_point_id': 'seg1_B3_p5',
            },
            {
                'segment_id': 'seg1',
                'visit_order': 6,
                'waybill_point_id': 'seg1_A2_p6',
            },
            {
                'segment_id': 'seg1',
                'visit_order': 7,
                'waybill_point_id': 'seg1_A1_p7',
            },
        ],
        'segments': [{'segment_id': 'seg1', 'claim_id': 'claim_seg1'}],
        'waybill_ref': 'waybill_fb_1',
    }


async def test_get_path_by_cargo_order_id(
        get_waybill_path_info,
        happy_path_state_performer_found,
        read_waybill_info,
        taxi_cargo_dispatch,
):
    waybill_ref = 'waybill_fb_3'

    # Get waybill path by waybill_external_ref
    response_by_waybill_ref = await get_waybill_path_info(waybill_ref)
    assert response_by_waybill_ref.status_code == 200
    path = response_by_waybill_ref.json()

    waybill_info = await read_waybill_info(waybill_ref)

    # Get waybill path by cargo_order_id and check that they are same
    response_by_cargo_order_id = await taxi_cargo_dispatch.post(
        '/v1/waybill/path/info',
        params={'cargo_order_id': waybill_info['diagnostics']['order_id']},
    )
    assert response_by_cargo_order_id.status_code == 200
    assert response_by_cargo_order_id.json() == path


async def test_no_waybill_ref_and_cargo_order_id(taxi_cargo_dispatch):
    response = await taxi_cargo_dispatch.post('/v1/waybill/path/info')
    assert response.status_code == 400


async def test_waybill_ref_and_cargo_order_id(taxi_cargo_dispatch):
    response = await taxi_cargo_dispatch.post(
        '/v1/waybill/path/info',
        params={
            'cargo_order_id': '5e36732e-2bc5-4e08-8b14-66e08e31c486',
            'waybill_external_ref': '123',
        },
    )
    assert response.status_code == 400
