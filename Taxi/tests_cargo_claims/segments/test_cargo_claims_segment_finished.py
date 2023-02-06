import pytest

from testsuite.utils import matching


@pytest.fixture(name='mock_payment_cancel')
def _mock_payment_cancel(mockserver):
    @mockserver.json_handler('/cargo-payments/v1/payment/cancel')
    def mock(request):
        context.last_request = request
        if context.status_code == 200:
            return {'payment_id': request.json['payment_id'], 'revision': 1}
        return mockserver.make_response(
            status=context.status_code,
            json={
                'code': context.error_code,
                'message': context.error_message,
            },
        )

    class Context:
        def __init__(self):
            self.last_request = None
            self.status_code = 200
            self.error_code = 'bad_request'
            self.error_message = 'error message'
            self.handler = mock

    context = Context()

    return context


async def test_cancel_not_called(
        prepare_state,
        mock_payment_create,
        mock_payment_status,
        mock_payment_cancel,
        exp_cargo_payment_virtual_clients,
        stq_runner,
):
    """
        Check v1/payment/cancel is not called on sucessfully
        delivered claims.

        Segment:
            A1->B2->B3->C4
    """
    segment_id = await prepare_state(payment_method='card', visit_order=4)

    await stq_runner.cargo_claims_segment_finished.call(
        task_id='test', kwargs={'segment_id': segment_id},
    )

    assert mock_payment_cancel.handler.times_called == 0


async def test_cancel_payments_on_cancel(
        create_segment_with_performer,
        taxi_cargo_claims,
        get_default_headers,
        get_segment_id_by_claim,
        mock_payment_create,
        mock_payment_cancel,
        exp_cargo_payment_virtual_clients,
        mock_cargo_pricing_calc,
        stq_runner,
        mock_waybill_info,
):
    """
        Check v1/payment/cancel is called on stq if claim is
        canceled by client.

        Segment:
            A1->B2->B3->C4
    """
    claim_info = await create_segment_with_performer(payment_method='card')
    segment_id = await get_segment_id_by_claim(claim_info.claim_id)

    response = await taxi_cargo_claims.post(
        f'/api/integration/v2/claims/cancel',
        params={'claim_id': claim_info.claim_id},
        json={'version': 1, 'cancel_state': 'paid'},
        headers=get_default_headers(),
    )
    assert response.status_code == 200

    await stq_runner.cargo_claims_segment_finished.call(
        task_id='test', kwargs={'segment_id': segment_id},
    )

    assert mock_payment_cancel.handler.times_called == 2
    assert mock_payment_cancel.last_request.json == {
        'payment_id': matching.AnyString(),
    }


async def test_cancel_payments_on_return(
        prepare_state,
        exchange_return,
        mock_payment_status,
        mock_payment_create,
        mock_payment_cancel,
        exp_cargo_payment_virtual_clients,
        stq_runner,
        mock_create_event,
):
    """
        Check v1/payment/cancel is called on stq if some points skipped.

        Segment:
            A1->B2->B3->C4
    """
    mock_create_event()

    segment_id = await prepare_state(payment_method='card', visit_order=3)
    await exchange_return(segment_id=segment_id, point_visit_order=3)

    await stq_runner.cargo_claims_segment_finished.call(
        task_id='test', kwargs={'segment_id': segment_id},
    )

    assert mock_payment_cancel.handler.times_called == 1
    assert mock_payment_cancel.last_request.json == {
        'payment_id': matching.AnyString(),
    }
