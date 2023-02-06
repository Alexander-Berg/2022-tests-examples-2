import datetime

import pytest

from . import conftest


def _mock_order_proc_for_point_actions(now, mocker_archive_get_order_proc):
    mocker_archive_get_order_proc(
        {
            '_id': 'taxi_order_id_1',
            'order': {'nz': 'moscow', 'city': 'Москва'},
            'performer': {'candidate_index': 0},
            'order_link': '8f6802e601b2179177df4a8e89c54b97',
            'aliases': [
                {
                    'generation': 1,
                    'due_optimistic': None,
                    'id': 'order_alias_1',
                    'due': now + datetime.timedelta(minutes=5),
                },
            ],
            'candidates': [
                {'dp_values': {'a': -10}, 'alias_id': 'order_alias_1'},
            ],
            'order_info': {
                'statistics': {'status_updates': [{'c': now, 't': 'waiting'}]},
            },
        },
    )


async def post_exchange_init(get_segment_id, raw_exchange_init, current_point):
    segment_id = await get_segment_id()
    return await raw_exchange_init(segment_id, point_visit_order=current_point)


async def post_exchange_confirm(
        get_segment_id, raw_exchange_confirm, current_point,
):
    segment_id = await get_segment_id()
    return await raw_exchange_confirm(
        segment_id, point_visit_order=current_point,
    )


async def post_return(get_segment_id, raw_exchange_return, current_point):
    segment_id = await get_segment_id()
    return await raw_exchange_return(
        segment_id, point_visit_order=current_point,
    )


async def confirm_pickup(
        iterations,
        get_segment_id,
        raw_exchange_init,
        raw_exchange_confirm,
        current_point,
):
    for _ in range(iterations):
        response = await post_exchange_init(
            get_segment_id, raw_exchange_init, current_point,
        )
        assert response.status_code == 200

        response = await post_exchange_confirm(
            get_segment_id, raw_exchange_confirm, current_point,
        )
        assert response.status_code == 200
        current_point += 1

    return response


@pytest.mark.experiments3(filename='exp3_action_checks.json')
@pytest.mark.parametrize('skip_confirmation', [False, True])
async def test_point_marked_as_skipped(
        taxi_cargo_claims,
        state_controller,
        mockserver,
        skip_confirmation,
        now,
        mocker_archive_get_order_proc,
        get_default_driver_auth_headers,
        get_segment_id,
        raw_exchange_init,
        raw_exchange_confirm,
        raw_exchange_return,
):
    _mock_order_proc_for_point_actions(now, mocker_archive_get_order_proc)

    state_controller.use_create_version('v2')
    state_controller.set_options(skip_confirmation=skip_confirmation)
    claim_info = await state_controller.apply(target_status='pickup_arrived')
    current_point = claim_info.current_state.point_id

    await confirm_pickup(
        1,
        get_segment_id,
        raw_exchange_init,
        raw_exchange_confirm,
        current_point,
    )

    current_point += 1

    response = await post_return(
        get_segment_id, raw_exchange_return, current_point,
    )
    response_json = response.json()
    assert response.status_code == 200, response_json

    assert response_json == {
        'new_status': 'delivering',
        'result': 'confirmed',
        'new_claim_status': 'pickuped',
    }

    # Check db results
    new_claim_info = await state_controller.get_claim_info()
    assert new_claim_info.points[1].visit_status == 'skipped'

    # TODO: fix in CARGODEV-11356
    # assert new_claim_info.points[1].return_reasons ==
    # ['reason_a', 'reason_b']
    # assert new_claim_info.points[1].return_comment ==
    # 'Test return comment'


@pytest.mark.skip('TODO: fix in CARGODEV-11356')
@pytest.mark.experiments3(filename='exp3_action_checks_no_return.json')
async def test_return_not_allowed(
        taxi_cargo_claims,
        state_controller,
        mockserver,
        now,
        mocker_archive_get_order_proc,
        get_default_driver_auth_headers,
        get_segment_id,
        raw_exchange_return,
):
    _mock_order_proc_for_point_actions(now, mocker_archive_get_order_proc)

    claim_info = await state_controller.apply(target_status='pickuped')
    current_point = claim_info.current_state.point_id

    response = await post_return(
        get_segment_id, raw_exchange_return, current_point,
    )
    assert response.status_code == 400


@pytest.mark.experiments3(filename='exp3_action_checks.json')
@pytest.mark.parametrize('skip_confirmation', [False, True])
async def test_last_point(
        taxi_cargo_claims,
        state_controller,
        get_default_driver_auth_headers,
        mockserver,
        skip_confirmation,
        now,
        mocker_archive_get_order_proc,
        get_segment_id,
        raw_exchange_init,
        raw_exchange_confirm,
        raw_exchange_return,
):
    _mock_order_proc_for_point_actions(now, mocker_archive_get_order_proc)

    state_controller.use_create_version('v2')
    state_controller.set_options(skip_confirmation=skip_confirmation)
    claim_info = await state_controller.apply(target_status='pickup_arrived')
    current_point = claim_info.current_state.point_id

    iterations = 2
    await confirm_pickup(
        iterations,
        get_segment_id,
        raw_exchange_init,
        raw_exchange_confirm,
        current_point,
    )
    current_point += iterations

    @mockserver.json_handler('/int-authproxy/v1/changedestinations')
    def _changedestinations(request):
        assert request.json['disable_price_changing'] is False
        assert request.json['destinations'][0]['fullname'] == '4'
        assert request.json['destinations'][0]['geopoint'] == [37.0, 55.5]
        return conftest.CHANGEDESTINATIONS_RESPONSE

    response = await post_return(
        get_segment_id, raw_exchange_return, current_point,
    )
    response_json = response.json()
    assert response.status_code == 200, response_json
    response_json.pop('new_route', {})
    assert response_json == {
        'new_status': 'returning',
        'result': 'confirmed',
        'new_claim_status': 'returning',
    }

    # TODO: fix in CARGODEV-11356
    # assert _changedestinations.times_called == 1

    # Check db results
    new_claim_info = await state_controller.get_claim_info()
    assert new_claim_info.current_state.point_id == current_point + 1
    assert new_claim_info.points[2].visit_status == 'skipped'

    # TODO: fix in CARGODEV-11356
    # assert new_claim_info.points[2].return_reasons ==
    # ['reason_a', 'reason_b']
    # assert new_claim_info.points[2].return_comment ==
    # 'Test return comment'


@pytest.mark.experiments3(filename='exp3_action_checks.json')
@pytest.mark.parametrize('skip_confirmation', [False, True])
async def test_return_after_complete(
        taxi_cargo_claims,
        state_controller,
        get_default_driver_auth_headers,
        mockserver,
        skip_confirmation,
        now,
        mocker_archive_get_order_proc,
        get_segment_id,
        raw_exchange_init,
        raw_exchange_confirm,
        raw_exchange_return,
):
    _mock_order_proc_for_point_actions(now, mocker_archive_get_order_proc)

    state_controller.use_create_version('v2')
    state_controller.set_options(skip_confirmation=skip_confirmation)
    claim_info = await state_controller.apply(target_status='pickup_arrived')
    current_point = claim_info.current_state.point_id

    await confirm_pickup(
        1,
        get_segment_id,
        raw_exchange_init,
        raw_exchange_confirm,
        current_point,
    )
    current_point += 1

    @mockserver.json_handler('/int-authproxy/v1/changedestinations')
    def _changedestinations(request):
        assert request.json['disable_price_changing'] is True
        assert request.json['destinations'][0]['fullname'] == '3'
        assert request.json['destinations'][0]['geopoint'] == [37.0, 55.0]
        return conftest.CHANGEDESTINATIONS_RESPONSE

    response = await post_return(
        get_segment_id, raw_exchange_return, current_point,
    )

    response_json = response.json()
    assert response.status_code == 200, response_json

    # TODO: fix in CARGODEV-11356
    # assert _changedestinations.times_called == 1

    assert response_json == {
        'new_status': 'delivering',
        'result': 'confirmed',
        'new_claim_status': 'pickuped',
    }
    current_point += 1

    # Complete delivery
    response = await post_exchange_init(
        get_segment_id, raw_exchange_init, current_point,
    )
    assert response.status_code == 200

    # @mockserver.json_handler('/int-authproxy/v1/changedestinations')
    # def _changedestinations(request):
    #     assert request.json['destinations'][0]['fullname'] == '4'
    #     assert request.json['destinations'][0]['geopoint'] == [37.0, 55.5]
    #     return conftest.CHANGEDESTINATIONS_RESPONSE

    response = await post_exchange_confirm(
        get_segment_id, raw_exchange_confirm, current_point,
    )
    response_json = response.json()
    assert response.status_code == 200, response_json

    # TODO: fix in CARGODEV-11356
    # assert _changedestinations.times_called == 1

    assert response_json == {
        'new_status': 'returning',
        'result': 'confirmed',
        'new_claim_status': 'returning',
        'taxi_order_id': 'taxi_order_id_1',
    }
    current_point += 1

    # Complete returning
    response = await post_exchange_init(
        get_segment_id, raw_exchange_init, current_point,
    )
    assert response.status_code == 200

    response = await post_exchange_confirm(
        get_segment_id, raw_exchange_confirm, current_point,
    )

    response_json = response.json()
    assert response.status_code == 200, response_json
    assert response_json == {
        'new_status': 'complete',
        'result': 'confirmed',
        'new_claim_status': 'returned',
        'taxi_order_id': 'taxi_order_id_1',
    }

    # Test points visit_status
    expected_result = ['visited', 'skipped', 'visited', 'visited']

    # Test claim status
    new_claim_info = await state_controller.get_claim_info()
    assert new_claim_info.current_state.status == 'returned'
    for i, point in enumerate(new_claim_info.points):
        assert point.visit_status == expected_result[i]


@pytest.mark.experiments3(filename='exp3_action_checks.json')
@pytest.mark.parametrize('skip_confirmation', [False, True])
async def test_double_return(
        taxi_cargo_claims,
        state_controller,
        get_default_driver_auth_headers,
        mockserver,
        skip_confirmation,
        now,
        mocker_archive_get_order_proc,
        get_segment_id,
        raw_exchange_init,
        raw_exchange_confirm,
        raw_exchange_return,
):
    _mock_order_proc_for_point_actions(now, mocker_archive_get_order_proc)

    state_controller.use_create_version('v2')
    state_controller.set_options(skip_confirmation=skip_confirmation)
    claim_info = await state_controller.apply(target_status='pickup_arrived')
    current_point = claim_info.current_state.point_id

    await confirm_pickup(
        1,
        get_segment_id,
        raw_exchange_init,
        raw_exchange_confirm,
        current_point,
    )
    current_point += 1

    @mockserver.json_handler('/int-authproxy/v1/changedestinations')
    def _changedestinations(request):
        assert request.json['disable_price_changing'] is True
        assert request.json['destinations'][0]['fullname'] == '3'
        assert request.json['destinations'][0]['geopoint'] == [37.0, 55.0]
        return conftest.CHANGEDESTINATIONS_RESPONSE

    response = await post_return(
        get_segment_id, raw_exchange_return, current_point,
    )
    response_json = response.json()
    assert response.status_code == 200, response_json

    # TODO: fix in CARGODEV-11356
    # assert _changedestinations.times_called == 1

    assert response_json == {
        'new_status': 'delivering',
        'result': 'confirmed',
        'new_claim_status': 'pickuped',
    }
    current_point += 1

    # @mockserver.json_handler('/int-authproxy/v1/changedestinations')
    # def _changedestinations(request):
    #     assert request.json['destinations'][0]['fullname'] == '4'
    #     assert request.json['destinations'][0]['geopoint'] == [37.0, 55.5]
    #     return conftest.CHANGEDESTINATIONS_RESPONSE

    response = await post_return(
        get_segment_id, raw_exchange_return, current_point,
    )
    response_json = response.json()
    assert response.status_code == 200, response_json

    # TODO: fix in CARGODEV-11356
    # assert _changedestinations.times_called == 1

    response_json.pop('new_route', {})
    assert response_json == {
        'new_status': 'returning',
        'result': 'confirmed',
        'new_claim_status': 'returning',
    }

    # Test points visit_status
    expected_result = ['visited', 'skipped', 'skipped', 'pending']

    # Test claim status
    new_claim_info = await state_controller.get_claim_info()
    assert new_claim_info.current_state.status == 'returning'
    for i, point in enumerate(new_claim_info.points):
        assert point.visit_status == expected_result[i]


@pytest.mark.experiments3(filename='exp3_action_checks.json')
@pytest.mark.parametrize('skip_confirmation', [False, True])
async def test_return_from_delivery_confirmation(
        taxi_cargo_claims,
        state_controller,
        get_default_driver_auth_headers,
        mockserver,
        skip_confirmation,
        now,
        mocker_archive_get_order_proc,
        get_segment_id,
        raw_exchange_init,
        raw_exchange_confirm,
        raw_exchange_return,
):
    _mock_order_proc_for_point_actions(now, mocker_archive_get_order_proc)

    state_controller.use_create_version('v2')
    state_controller.set_options(skip_confirmation=skip_confirmation)
    claim_info = await state_controller.apply(target_status='pickup_arrived')
    current_point = claim_info.current_state.point_id

    await confirm_pickup(
        1,
        get_segment_id,
        raw_exchange_init,
        raw_exchange_confirm,
        current_point,
    )
    current_point += 1

    # Change claim status to ready_for_delivery_confirmation
    response = await post_exchange_init(
        get_segment_id, raw_exchange_init, current_point,
    )
    assert response.status_code == 200

    response = await post_return(
        get_segment_id, raw_exchange_return, current_point,
    )
    response_json = response.json()
    assert response.status_code == 200, response_json
    assert response_json == {
        'new_status': 'delivering',
        'result': 'confirmed',
        'new_claim_status': 'pickuped',
    }
    current_point += 1

    # Test points visit_status
    expected_result = ['visited', 'skipped', 'pending', 'pending']

    # Test claim status
    new_claim_info = await state_controller.get_claim_info()
    assert new_claim_info.current_state.status == 'pickuped'
    for i, point in enumerate(new_claim_info.points):
        assert point.visit_status == expected_result[i]


@pytest.mark.experiments3(filename='exp3_action_checks.json')
@pytest.mark.parametrize('skip_confirmation', [False, True])
async def test_v1_claim_return_send_point(
        taxi_cargo_claims,
        state_controller,
        get_default_driver_auth_headers,
        skip_confirmation,
        now,
        mocker_archive_get_order_proc,
        get_segment_id,
        raw_exchange_init,
        raw_exchange_confirm,
        raw_exchange_return,
):
    _mock_order_proc_for_point_actions(now, mocker_archive_get_order_proc)

    state_controller.set_options(skip_confirmation=skip_confirmation)
    claim_info = await state_controller.apply(target_status='pickup_arrived')
    current_point = claim_info.current_state.point_id

    await confirm_pickup(
        1,
        get_segment_id,
        raw_exchange_init,
        raw_exchange_confirm,
        current_point,
    )
    current_point += 1

    response = await post_return(
        get_segment_id, raw_exchange_return, current_point,
    )
    response_json = response.json()
    assert response.status_code == 200, response_json
    response_json.pop('new_route', {})
    assert response_json == {
        'new_status': 'returning',
        'result': 'confirmed',
        'new_claim_status': 'returning',
    }
    current_point += 1

    response = await post_exchange_init(
        get_segment_id, raw_exchange_init, current_point,
    )
    assert response.status_code == 200

    response = await post_exchange_confirm(
        get_segment_id, raw_exchange_confirm, current_point,
    )
    assert response.status_code == 200

    # Check db results
    # Test points visit_status
    expected_result = ['visited', 'skipped', 'visited']

    # Test claim status
    new_claim_info = await state_controller.get_claim_info()
    assert new_claim_info.current_state.point_id is None
    assert new_claim_info.current_state.status == 'returned'
    for i, point in enumerate(new_claim_info.points):
        assert point.visit_status == expected_result[i]


@pytest.mark.experiments3(filename='exp3_action_checks.json')
@pytest.mark.parametrize('skip_confirmation', [False, True])
async def test_v1_claim_confirm_send_point(
        taxi_cargo_claims,
        state_controller,
        get_default_driver_auth_headers,
        skip_confirmation,
        now,
        mocker_archive_get_order_proc,
        get_segment_id,
        raw_exchange_init,
        raw_exchange_confirm,
):
    _mock_order_proc_for_point_actions(now, mocker_archive_get_order_proc)

    state_controller.set_options(skip_confirmation=skip_confirmation)
    claim_info = await state_controller.apply(target_status='pickup_arrived')
    current_point = claim_info.current_state.point_id

    response = await confirm_pickup(
        2,
        get_segment_id,
        raw_exchange_init,
        raw_exchange_confirm,
        current_point,
    )
    current_point += 1

    response_json = response.json()
    assert response.status_code == 200, response_json
    response_json.pop('new_route', {})
    assert response_json == {
        'new_status': 'complete',
        'result': 'confirmed',
        'new_claim_status': 'delivered',
        'taxi_order_id': 'taxi_order_id_1',
    }

    # Check db results
    # Test points visit_status
    expected_result = ['visited', 'visited', 'skipped']

    # Test claim status
    new_claim_info = await state_controller.get_claim_info()
    assert new_claim_info.current_state.status == 'delivered'

    # TODO: fix in CARGODEV-11356
    # assert new_claim_info.current_state.point_id is None

    for i, point in enumerate(new_claim_info.points):
        assert point.visit_status == expected_result[i]


@pytest.mark.experiments3(filename='exp3_action_checks.json')
async def test_outdated(
        taxi_cargo_claims,
        state_controller,
        get_default_driver_auth_headers,
        mockserver,
        now,
        mocker_archive_get_order_proc,
        get_segment_id,
        raw_exchange_return,
):
    _mock_order_proc_for_point_actions(now, mocker_archive_get_order_proc)

    state_controller.use_create_version('v2')
    claim_info = await state_controller.apply(
        target_status='pickuped', next_point_order=2,
    )
    current_point = claim_info.current_state.point_id

    @mockserver.json_handler('/int-authproxy/v1/changedestinations')
    def _changedestinations(request):
        assert request.json['disable_price_changing'] is True
        assert request.json['destinations'][0]['fullname'] == '3'
        assert request.json['destinations'][0]['geopoint'] == [37.0, 55.0]
        return conftest.CHANGEDESTINATIONS_RESPONSE

    for _ in range(2):
        response = await post_return(
            get_segment_id, raw_exchange_return, current_point,
        )
        assert response.status_code == 200
        # called once for first call

        # TODO: fix in CARGODEV-11356
        # assert _changedestinations.times_called == 1

    response = await post_return(
        get_segment_id, raw_exchange_return, current_point - 1,
    )

    # TODO: fix in CARGODEV-11356
    # assert response.status_code == 200


@pytest.mark.skip('TODO: fix in CARGODEV-11356')
@pytest.mark.experiments3(filename='exp3_action_checks.json')
async def test_sms_on_the_way(
        taxi_cargo_claims,
        state_controller,
        get_default_driver_auth_headers,
        stq,
        now,
        mocker_archive_get_order_proc,
        get_segment_id,
        raw_exchange_init,
        raw_exchange_confirm,
        raw_exchange_return,
):
    _mock_order_proc_for_point_actions(now, mocker_archive_get_order_proc)

    state_controller.use_create_version('v2')
    claim_info = await state_controller.apply(target_status='performer_found')
    claim_id = claim_info.claim_id
    current_point = claim_info.current_state.point_id

    await confirm_pickup(
        1,
        get_segment_id,
        raw_exchange_init,
        raw_exchange_confirm,
        current_point,
    )
    current_point += 1

    assert stq.cargo_claims_send_on_the_way_sms.times_called == 1
    stq_params = stq.cargo_claims_send_on_the_way_sms.next_call()
    stq_params['kwargs'].pop('log_extra')
    assert stq_params['kwargs'] == {
        'claim_id': claim_id,
        'claim_point_id': str(current_point),
    }

    response = await post_return(
        get_segment_id, raw_exchange_return, current_point,
    )
    assert response.status_code == 200
    current_point += 1

    assert stq.cargo_claims_send_on_the_way_sms.times_called == 1
    stq_params = stq.cargo_claims_send_on_the_way_sms.next_call()
    stq_params['kwargs'].pop('log_extra')
    assert stq_params['kwargs'] == {
        'claim_id': claim_id,
        'claim_point_id': str(current_point),
    }


def get_point_comments(pgsql):
    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        'SELECT return_comment, return_reasons '
        'FROM cargo_claims.claim_points '
        'ORDER BY id ASC',
    )
    return list(cursor)


@pytest.mark.skip('TODO: fix in CARGODEV-11356')
@pytest.mark.experiments3(filename='exp3_action_checks.json')
async def test_return_comments(
        taxi_cargo_claims,
        state_controller,
        pgsql,
        get_default_driver_auth_headers,
        now,
        mocker_archive_get_order_proc,
        get_segment_id,
        raw_exchange_init,
        raw_exchange_confirm,
        raw_exchange_return,
):
    _mock_order_proc_for_point_actions(now, mocker_archive_get_order_proc)

    state_controller.use_create_version('v2')
    claim_info = await state_controller.apply(target_status='pickup_arrived')
    current_point = claim_info.current_state.point_id

    await confirm_pickup(
        1,
        get_segment_id,
        raw_exchange_init,
        raw_exchange_confirm,
        current_point,
    )
    current_point += 1

    assert get_point_comments(pgsql) == [
        (None, None),
        (None, None),
        (None, None),
        (None, None),
    ]

    response = await post_return(
        get_segment_id, raw_exchange_return, current_point,
    )
    assert response.status_code == 200
    current_point += 1

    assert get_point_comments(pgsql) == [
        (None, None),
        ('Test return comment', ['reason_a', 'reason_b']),
        (None, None),
        (None, None),
    ]

    response = await post_return(
        get_segment_id, raw_exchange_return, current_point,
    )
    assert response.status_code == 200
    current_point += 1

    assert get_point_comments(pgsql) == [
        (None, None),
        ('Test return comment', ['reason_a', 'reason_b']),
        ('Test return comment', ['reason_a', 'reason_b']),
        (None, None),
    ]
