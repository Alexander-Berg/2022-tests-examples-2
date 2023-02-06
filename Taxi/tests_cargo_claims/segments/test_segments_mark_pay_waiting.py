import uuid

import pytest


DEFAULT_HEADERS = {'X-Real-IP': '12.34.56.78'}


def _build_arrive_at_point_request(*, claim_point_id, cargo_order_id):
    return {
        'cargo_order_id': cargo_order_id,
        'last_known_status': 'delivering',
        'point_id': claim_point_id,
        'idempotency_token': '100500',
        'driver': {'park_id': 'some_park', 'driver_profile_id': 'some_driver'},
    }


# status:       pickuped,
# next point:   B1 (first destination point)
# post-payment: enabled
@pytest.fixture(name='state_ready_for_pay_waiting')
def _state_ready_for_pay_waiting(
        enable_payment_on_delivery,
        mock_payments_check_token,
        mock_payment_create,
        create_segment_with_performer,
        do_prepare_segment_state,
        get_current_claim_point,
        taxi_cargo_claims,
        get_default_cargo_order_id,
):
    async def _wrapper(payment_method='card', **kwargs):
        segment = await create_segment_with_performer(
            payment_method=payment_method, **kwargs,
        )
        state = await do_prepare_segment_state(
            segment, visit_order=2, last_exchange_init=False,
        )
        current_point_id = await get_current_claim_point(segment.claim_id)

        response = await taxi_cargo_claims.post(
            '/v1/segments/arrive_at_point',
            params={'segment_id': segment.id},
            json=_build_arrive_at_point_request(
                claim_point_id=current_point_id,
                cargo_order_id=get_default_cargo_order_id,
            ),
            headers=DEFAULT_HEADERS,
        )
        assert response.status_code == 200
        return state

    return _wrapper


def _build_request(*, claim_id, segment_id, claim_point_id):
    return {
        'claim_id': claim_id,
        'segment_id': segment_id,
        'claim_point_id': claim_point_id,
    }


@pytest.fixture(name='mark_pay_waiting')
async def _mark_pay_waiting(taxi_cargo_claims, get_point_info):
    async def _wrapper(*, segment_id, visit_order):
        _, payment_ref_id = await get_point_info(
            segment_id=segment_id, visit_order=2,
        )

        response = await taxi_cargo_claims.post(
            '/v1/claims/payments/pay-waiting',
            params={'payment_ref_id': payment_ref_id},
        )

        assert response.status_code == 200
        return response.json()

    return _wrapper


@pytest.fixture(name='get_point_info')
async def _get_point_info(get_segment):
    async def _wrapper(*, segment_id, visit_order):
        segment = await get_segment(segment_id)
        for point in segment['points']:
            if point['visit_order'] == visit_order:
                return point['claim_point_id'], point['post_payment']['id']
        assert False, f'No point with visit_order {visit_order}'

    return _wrapper


@pytest.mark.config(
    CARGO_CLAIMS_DISTLOCK_PROCESSING_EVENTS_SETTINGS={
        'enabled': True,
        'sleep_ms': 50,
        'new_event_chunk_size': 2,
    },
)
async def test_change_to_pay_waiting(
        procaas_claim_status_filter,
        procaas_event_kind_filter,
        taxi_cargo_claims,
        state_ready_for_pay_waiting,
        mark_pay_waiting,
        get_segment,
        get_claim,
        query_processing_events,
        mock_payment_status,
        payment_method='card',
):
    """
        Check status changed to pay_waiting after delivery_arrived.

        delivery_arrived->(payment_confirmed)->pay_waiting
    """
    await procaas_claim_status_filter()
    await procaas_event_kind_filter()
    segment = await state_ready_for_pay_waiting()

    response_json = await mark_pay_waiting(
        segment_id=segment.id, visit_order=2,
    )
    assert response_json == {'new_status': 'pay_waiting'}

    segment_info = await get_segment(segment.id)
    assert segment_info['status'] == 'pay_waiting'

    claim_info = await get_claim(segment.claim_id)
    assert claim_info['status'] == 'pay_waiting'

    events = query_processing_events(segment.claim_id)
    assert len(events) == 9
    assert events[7].payload['data'].pop('claim_revision') > 0
    assert events[7].payload == {
        'data': {
            'corp_client_id': '01234567890123456789012345678912',
            'claim_origin': 'api',
            'phoenix_claim': False,
            'is_terminal': False,
            'current_point_id': 2,
            'skip_client_notify': False,
            'zone_id': 'moscow',
        },
        'kind': 'status-change-succeeded',
        'status': 'delivery_arrived',
    }
    assert events[8].payload['data'].pop('claim_revision') > 0
    assert events[8].payload == {
        'data': {
            'corp_client_id': '01234567890123456789012345678912',
            'claim_origin': 'api',
            'phoenix_claim': False,
            'is_terminal': False,
            'current_point_id': 2,
            'skip_client_notify': False,
        },
        'kind': 'status-change-succeeded',
        'status': 'pay_waiting',
    }


async def test_change_after_pay_waiting(
        taxi_cargo_claims,
        state_ready_for_pay_waiting,
        mark_pay_waiting,
        exchange_init,
        mock_payment_status,
        payment_method='card',
):
    """
        Check pay_waiting -> ready_for_delivery_confirmation is valid
        status transation.

        state: payment is finished.
    """
    segment = await state_ready_for_pay_waiting()

    await mark_pay_waiting(segment_id=segment.id, visit_order=2)

    await exchange_init(segment.id, 2)


async def test_payment_cost(
        taxi_cargo_claims,
        state_ready_for_pay_waiting,
        mark_pay_waiting,
        mock_payment_status,
        get_point_info,
        stq,
        get_payment_info,
        cost='20.0000',
):
    segment = await state_ready_for_pay_waiting()

    await mark_pay_waiting(segment_id=segment.id, visit_order=2)

    _, payment_ref_id = await get_point_info(
        segment_id=segment.id, visit_order=2,
    )

    response = await taxi_cargo_claims.post(
        'v1/claims/payments/finish',
        params={'payment_ref_id': payment_ref_id},
        json={'cost': '20.0000'},
    )
    assert response.status == 200

    payment = await get_payment_info(
        claim_id=segment.claim_id, payment_id=payment_ref_id,
    )
    assert payment['cost'] == cost


async def test_payment_invoice_link(
        taxi_cargo_claims,
        state_ready_for_pay_waiting,
        mark_pay_waiting,
        mock_payment_status,
        get_point_info,
        stq,
        get_payment_info,
        cost='20.0000',
        invoice_link='https://ofd.yandex.ru/vaucher/'
        '0005312316002718/9410/2604520024',
):
    segment = await state_ready_for_pay_waiting()

    await mark_pay_waiting(segment_id=segment.id, visit_order=2)

    _, payment_ref_id = await get_point_info(
        segment_id=segment.id, visit_order=2,
    )

    response = await taxi_cargo_claims.post(
        'v1/claims/payments/finish',
        params={'payment_ref_id': payment_ref_id},
        json={'cost': cost, 'invoice_link': invoice_link},
    )
    assert response.status == 200

    payment = await get_payment_info(
        claim_id=segment.claim_id, payment_id=payment_ref_id,
    )
    assert payment['invoice_link'] == invoice_link


async def test_payment_finish(
        taxi_cargo_claims,
        state_ready_for_pay_waiting,
        mark_pay_waiting,
        mock_payment_status,
        get_payment_info,
        get_point_info,
        stq,
):
    """
        Check finish payment after pay_waiting.

        state: payment is finished.
    """
    segment = await state_ready_for_pay_waiting()

    await mark_pay_waiting(segment_id=segment.id, visit_order=2)

    claim_point_id, payment_ref_id = await get_point_info(
        segment_id=segment.id, visit_order=2,
    )

    # Check payments/finish OK
    response = await taxi_cargo_claims.post(
        'v1/claims/payments/finish',
        params={'payment_ref_id': payment_ref_id},
        json={'cost': '20.0000'},
    )
    assert response.status == 200

    # Check stq was called
    assert stq.cargo_claims_payment_finish.times_called == 1
    stq_params = stq.cargo_claims_payment_finish.next_call()
    assert stq_params['id'] == str(uuid.UUID(payment_ref_id))
    stq_params['kwargs'].pop('log_extra')
    assert stq_params['kwargs'] == {
        'claim_id': segment.claim_id,
        'claim_point_id': claim_point_id,
    }
    # Check is_paid is set
    payment = await get_payment_info(
        claim_id=segment.claim_id, payment_id=payment_ref_id,
    )
    assert payment['is_paid']


async def test_payment_finish_stq(
        state_ready_for_pay_waiting,
        mark_pay_waiting,
        exchange_init,
        mock_payment_status,
        get_point_info,
        get_claim,
        get_segment,
        stq_runner,
        payment_method='card',
):
    """
        Check status change pay_waiting -> ready_for_delivery_confirmation.

        state: payment is finished.
    """
    segment = await state_ready_for_pay_waiting()

    await mark_pay_waiting(segment_id=segment.id, visit_order=2)

    claim_point_id, payment_ref_id = await get_point_info(
        segment_id=segment.id, visit_order=2,
    )

    await stq_runner.cargo_claims_payment_finish.call(
        task_id=payment_ref_id, args=[segment.claim_id, claim_point_id],
    )

    # Check status changed for both segment and claim
    claim = await get_claim(segment.claim_id)
    assert claim['status'] == 'ready_for_delivery_confirmation'

    segment = await get_segment(segment.id)
    assert segment['status'] == 'ready_for_delivery_confirmation'
