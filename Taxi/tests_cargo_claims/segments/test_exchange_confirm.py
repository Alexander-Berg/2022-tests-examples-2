import pytest

from .. import conftest


@pytest.mark.parametrize(
    'visit_order, post_segment_status', [(2, 'delivered'), (1, 'pickuped')],
)
@pytest.mark.now('2020-07-20T11:00:00.00')
async def test_pickup(
        exchange_confirm,
        prepare_state,
        get_segment,
        get_claim_v2,
        visit_order: int,
        post_segment_status: str,
        stq,
):
    segment_id = await prepare_state(visit_order=visit_order)

    segment = await get_segment(segment_id)

    claim_point_id = conftest.get_claim_point_id_by_order(segment, visit_order)

    for _ in range(2):  # call twice to check idempotency
        response = await exchange_confirm(
            segment_id, claim_point_id=claim_point_id,
        )
        assert response.status_code == 200

        segment = await get_segment(segment_id)

        conftest.check_point_visited(segment, claim_point_id)
        assert segment['status'] == post_segment_status

        claim = await get_claim_v2(segment['diagnostics']['claim_id'])
        assert claim['status'] == post_segment_status
        conftest.check_claim_point_visited(claim, claim_point_id)
        assert claim['current_point_id'] == claim_point_id + 1

        assert stq.cargo_claims_xservice_change_status.times_called == 0


@pytest.mark.now('2020-06-22T10:00:01.00Z')
async def test_response_body(
        exchange_confirm, prepare_state, get_segment, stq,
):
    segment_id = await prepare_state(visit_order=1)
    segment = await get_segment(segment_id)
    claim_point_id = conftest.get_claim_point_id_by_order(
        segment, visit_order=1,
    )

    # stq task may be alreay called by prepare_state()
    stq.cargo_claims_documents_store.flush()

    response = await exchange_confirm(
        segment_id, claim_point_id=claim_point_id,
    )
    assert response.status_code == 200

    resp_body = response.json()
    assert resp_body['result'] == 'confirmed'
    assert resp_body['new_status'] == 'delivering'

    assert stq.cargo_claims_documents_store.times_called == 1

    stq_call = stq.cargo_claims_documents_store.next_call()
    claim_id = segment['diagnostics']['claim_id']

    assert stq_call['id'] == f'{claim_id}_act_pickuped'
    kwargs = stq_call['kwargs']
    assert kwargs == {
        'claim_id': claim_id,
        'document_type': 'act',
        'status': 'pickuped',
        'created_ts': {'$date': '2020-06-22T10:00:01.000Z'},
        'log_extra': {'_link': response.headers['X-YaRequestId']},
    }


async def test_returning_to_delivered(
        create_segment_with_performer,
        state_controller,
        get_current_claim_point,
        get_db_segment_ids,
        exchange_confirm,
        prepare_state,
        pgsql,
):
    await create_segment_with_performer()
    await state_controller.apply(target_status='returning', fresh_claim=False)

    segment_ids = await get_db_segment_ids()
    segment_id = segment_ids[0]

    cursor = pgsql['cargo_claims'].conn.cursor()
    cursor.execute(
        f"""
        UPDATE cargo_claims.claim_segments cs
        SET revision = cs.revision + 1,
            status = 'returning'
        WHERE cs.uuid = '{segment_id}'
        """,
    )

    response = await exchange_confirm(
        segment_id,
        claim_point_id=2,
        with_support=True,
        last_known_status='returning',
    )

    expected_response = {
        'new_claim_status': 'delivered',
        'new_status': 'complete',
        'result': 'confirmed',
        'taxi_order_id': 'taxi_order_id',
    }
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.skip('TODO: fix in CARGODEV-11356')
async def test_returning_to_pickuped_in_multipoints(
        get_default_cargo_order_id,
        taxi_cargo_claims,
        state_controller,
        get_db_segment_ids,
        exchange_confirm,
        create_claim_for_segment,
        create_segment_for_claim,
        pgsql,
):
    claim = await create_claim_for_segment(
        use_create_v2=True, multipoints=True, with_return=True,
    )
    await create_segment_for_claim(claim.claim_id)

    claim_info = await state_controller.apply(
        target_status='pickuped', next_point_order=2, fresh_claim=False,
    )

    segment_ids = await get_db_segment_ids()
    segment_id = segment_ids[0]

    request_body = {
        'cargo_ref_id': claim_info.claim_id,
        'point_id': 2,
        'last_known_status': 'delivering',
        'comment': 'I did not find any warehouse at point',
    }

    response = await taxi_cargo_claims.post(
        'driver/v1/cargo-claims/v1/cargo/return',
        json=request_body,
        headers=conftest.get_default_driver_auth_headers(),
    )

    cursor = pgsql['cargo_claims'].conn.cursor()
    cursor.execute(
        f"""
        UPDATE cargo_claims.claim_segments cs
        SET revision = cs.revision + 1,
            status = 'returning',
            cargo_order_id = '{get_default_cargo_order_id}'
        WHERE cs.uuid = '{segment_id}'
        """,
    )

    response = await exchange_confirm(
        segment_id,
        claim_point_id=2,
        with_support=True,
        last_known_status='returning',
    )

    expected_response = {
        'new_claim_status': 'pickuped',
        'new_status': 'delivering',
        'result': 'confirmed',
        'taxi_order_id': 'taxi_order_id_1',
    }
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.skip('TODO: fix in CARGODEV-11356')
async def test_returning_several_points_in_multipoints(
        get_default_cargo_order_id,
        taxi_cargo_claims,
        state_controller,
        get_db_segment_ids,
        exchange_confirm,
        create_claim_for_segment,
        create_segment_for_claim,
        pgsql,
):
    claim = await create_claim_for_segment(
        use_create_v2=True, multipoints=True, with_return=True,
    )
    await create_segment_for_claim(claim.claim_id)

    claim_info = await state_controller.apply(
        target_status='pickuped', next_point_order=2, fresh_claim=False,
    )

    segment_ids = await get_db_segment_ids()
    segment_id = segment_ids[0]

    request_body = {
        'cargo_ref_id': claim_info.claim_id,
        'point_id': 2,
        'last_known_status': 'delivering',
        'comment': 'I did not find any warehouse at point',
    }

    response = await taxi_cargo_claims.post(
        'driver/v1/cargo-claims/v1/cargo/return',
        json=request_body,
        headers=conftest.get_default_driver_auth_headers(),
    )

    assert response.status_code == 200

    request_body['point_id'] = 3

    response = await taxi_cargo_claims.post(
        'driver/v1/cargo-claims/v1/cargo/return',
        json=request_body,
        headers=conftest.get_default_driver_auth_headers(),
    )

    assert response.status_code == 200

    cursor = pgsql['cargo_claims'].conn.cursor()
    cursor.execute(
        f"""
        UPDATE cargo_claims.claim_segments cs
        SET revision = cs.revision + 1,
            status = 'returning',
            cargo_order_id = '{get_default_cargo_order_id}'
        WHERE cs.uuid = '{segment_id}'
        """,
    )

    response = await exchange_confirm(
        segment_id,
        claim_point_id=3,
        with_support=True,
        last_known_status='returning',
    )

    expected_response = {
        'new_claim_status': 'returning',
        'new_status': 'returning',
        'result': 'confirmed',
        'taxi_order_id': 'taxi_order_id_1',
    }
    assert response.status_code == 200
    assert response.json() == expected_response


async def test_skip_return_point_on_happypath(
        exchange_confirm, prepare_state, get_segment,
):
    segment_id = await prepare_state(visit_order=2)
    segment = await get_segment(segment_id)
    claim_point_id = conftest.get_claim_point_id_by_order(
        segment, visit_order=2,
    )
    response = await exchange_confirm(
        segment_id, claim_point_id=claim_point_id,
    )
    assert response.status_code == 200

    # Check
    segment = await get_segment(segment_id)
    return_point = segment['points'][2]
    assert return_point['type'] == 'return'
    assert return_point['is_resolved']
    assert return_point['resolution']['is_skipped']


async def test_dragon_next_point_scheduled(
        exchange_confirm, prepare_state, get_segment, stq,
):
    segment_id = await prepare_state(visit_order=1)
    segment = await get_segment(segment_id)
    claim_point_id = conftest.get_claim_point_id_by_order(
        segment, visit_order=1,
    )
    response = await exchange_confirm(
        segment_id, claim_point_id=claim_point_id,
    )
    assert response.status_code == 200

    assert stq.cargo_dragon_next_point.times_called == 2
    for _ in range(2):
        call = stq.cargo_dragon_next_point.next_call()
        assert call['kwargs']['segment_id'] == segment_id
        assert call['kwargs']['claim_point_id'] == claim_point_id
        assert call['kwargs']['notify_taxi'] is False


@pytest.mark.parametrize('skip_init', [False, True])
async def test_support_paper_act(
        mockserver,
        exchange_confirm,
        prepare_state,
        get_segment,
        skip_init: bool,
        stq,
):
    @mockserver.json_handler('/esignature-issuer/v1/signatures/confirm')
    def signature_confirm(request):
        pass

    segment_id = await prepare_state(
        visit_order=1, last_exchange_init=not skip_init,
    )
    segment = await get_segment(segment_id)
    claim_point_id = conftest.get_claim_point_id_by_order(
        segment, visit_order=1,
    )

    # stq task may be alreay called by prepare_state()
    stq.cargo_claims_documents_store.flush()

    response = await exchange_confirm(
        segment_id,
        claim_point_id=claim_point_id,
        with_driver=False,
        paper_flow=True,
        with_support=True,
    )
    assert response.status_code == 200

    segment = await get_segment(segment_id)
    assert segment['status'] == 'pickuped'

    assert signature_confirm.times_called == 0
    assert stq.cargo_claims_documents_store.times_called == 0


async def test_support_audit(
        taxi_cargo_claims,
        mockserver,
        exchange_confirm,
        prepare_state,
        get_segment,
        check_audit,
):
    segment_id = await prepare_state(visit_order=1)
    segment = await get_segment(segment_id)
    claim_point_id = conftest.get_claim_point_id_by_order(
        segment, visit_order=1,
    )

    response = await exchange_confirm(
        segment_id,
        claim_point_id=claim_point_id,
        with_driver=False,
        paper_flow=True,
        with_support=True,
    )
    assert response.status_code == 200

    await check_audit(segment['diagnostics']['claim_id'])


@pytest.mark.parametrize(
    'last_known_status, expected_response_code',
    [('delivering', 409), (None, 200)],
)
async def test_no_last_known_status_validation_for_batch(
        taxi_cargo_claims,
        create_segment_with_performer,
        state_controller,
        get_current_claim_point,
        get_db_segment_ids,
        exchange_confirm,
        last_known_status,
        expected_response_code,
):
    await create_segment_with_performer()
    claim_info = await state_controller.apply(
        target_status='performer_found', fresh_claim=False,
    )
    current_claim_point = await get_current_claim_point(claim_info.claim_id)
    segment_ids = await get_db_segment_ids()
    segment_id = segment_ids[0]

    await exchange_confirm(
        segment_id,
        claim_point_id=current_claim_point,
        skip_last_known_status=(last_known_status is None),
        last_known_status=last_known_status,
        response_code=expected_response_code,
    )


# status:       pickuped,
# next point:   B1 (first destination point)
# post-payment: enabled
@pytest.fixture(name='state_ready_for_exchange')
def _state_ready_for_exchange(
        enable_payment_on_delivery,
        mock_payments_check_token,
        mock_payment_create,
        create_segment_with_performer,
        do_prepare_segment_state,
):
    async def _wrapper(payment_method='card', **kwargs):
        segment = await create_segment_with_performer(
            payment_method=payment_method, **kwargs,
        )
        return await do_prepare_segment_state(
            segment, visit_order=2, last_exchange_init=True,
        )

    return _wrapper


async def test_confirm_is_not_allowed_till_pay(
        taxi_cargo_claims,
        state_ready_for_exchange,
        get_current_claim_point,
        mock_payment_status,
        exchange_confirm,
):
    """
        exchange/confirm is not allowed until payment received.
    """

    segment = await state_ready_for_exchange()

    mock_payment_status.is_paid = False
    current_point_id = await get_current_claim_point(segment.claim_id)

    response = await exchange_confirm(
        segment.id, claim_point_id=current_point_id, response_code=409,
    )
    assert response.json()['code'] == 'payment_required'


@pytest.mark.now('2020-06-22T10:00:01.00Z')
async def test_race(
        exchange_confirm, prepare_state, get_segment, testpoint, pgsql,
):
    # Point was confirmed and timeout was happened
    # So cargo-dispatch retried request
    # And 'GetSegmentInfo' fetched old version

    segment_id = await prepare_state(visit_order=1)
    segment = await get_segment(segment_id)
    claim_point_id = conftest.get_claim_point_id_by_order(
        segment, visit_order=1,
    )

    @testpoint('segment-info-fetched')
    def update_point(data):
        cursor = pgsql['cargo_claims'].conn.cursor()
        cursor.execute(
            f"""
            UPDATE cargo_claims.claim_segment_points csp
            SET revision = csp.revision + 1,
                visit_status = 'visited'
            WHERE csp.claim_point_id = {claim_point_id}
            """,
        )

    await exchange_confirm(
        segment_id, claim_point_id=claim_point_id, response_code=200,
    )
    await update_point.wait_call()
