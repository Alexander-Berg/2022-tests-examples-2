import pytest


def _get_paid_cancel_response(
        *, reason='point_is_ready', paid_cancel_max_waiting_time=None,
):
    response = {'reason': reason}
    if paid_cancel_max_waiting_time is not None:
        response['paid_cancel_max_waiting_time'] = paid_cancel_max_waiting_time
    return response.copy()


@pytest.fixture(name='mock_claims_paid_cancel')
def _mock_claims_paid_cancel(mockserver):
    @mockserver.json_handler('/cargo-claims/v1/claims/paid-cancel')
    def mock(request):
        claim_id = request.args['claim_id']
        return context.response_by_claim.get(
            claim_id, _get_paid_cancel_response(),
        )

    class Context:
        def __init__(self):
            self.response_by_claim = {}
            self.handler = mock

    context = Context()

    return context


async def test_200_free(
        happy_path_state_performer_found,
        taxi_cargo_dispatch,
        happy_path_claims_segment_bulk_info_handler,
        mock_claims_paid_cancel,
        waybill_ref='waybill_smart_1',
):
    response = await taxi_cargo_dispatch.post(
        'v1/waybill/paid-cancel', json={'waybill_ref': waybill_ref},
    )
    assert response.status_code == 200
    assert response.json() == _get_paid_cancel_response()


@pytest.mark.parametrize(
    'paid_cancel_response_by_claim, claim_id_with_expected_response',
    [
        (
            {
                'claim_seg1': _get_paid_cancel_response(
                    reason='claim_seg1', paid_cancel_max_waiting_time=10,
                ),
            },
            'claim_seg1',
        ),
        (
            {
                'claim_seg2': _get_paid_cancel_response(
                    reason='claim_seg2', paid_cancel_max_waiting_time=10,
                ),
            },
            'claim_seg2',
        ),
        (
            {
                'claim_seg1': _get_paid_cancel_response(
                    reason='claim_seg1', paid_cancel_max_waiting_time=10,
                ),
                'claim_seg2': _get_paid_cancel_response(
                    reason='claim_seg2', paid_cancel_max_waiting_time=100,
                ),
            },
            'claim_seg2',
        ),
    ],
)
async def test_200_paid(
        happy_path_state_performer_found,
        taxi_cargo_dispatch,
        happy_path_claims_segment_bulk_info_handler,
        mock_claims_paid_cancel,
        paid_cancel_response_by_claim,
        claim_id_with_expected_response,
        waybill_ref='waybill_smart_1',
):
    mock_claims_paid_cancel.response_by_claim = paid_cancel_response_by_claim

    response = await taxi_cargo_dispatch.post(
        'v1/waybill/paid-cancel', json={'waybill_ref': waybill_ref},
    )
    assert response.status_code == 200
    assert (
        response.json()
        == paid_cancel_response_by_claim[claim_id_with_expected_response]
    )


async def test_404_claims(
        happy_path_state_performer_found,
        taxi_cargo_dispatch,
        happy_path_claims_segment_bulk_info_handler,
        mock_claims_paid_cancel,
        mockserver,
        waybill_ref='waybill_smart_1',
):
    mock_claims_paid_cancel.response_by_claim = {
        'claim_seg1': mockserver.make_response(
            json={'code': 'not_found', 'message': 'some_message'}, status=404,
        ),
    }

    response = await taxi_cargo_dispatch.post(
        'v1/waybill/paid-cancel', json={'waybill_ref': waybill_ref},
    )
    assert response.status_code == 404
    assert response.json() == {'code': 'not_found', 'message': 'some_message'}


async def test_no_waybill(
        happy_path_state_performer_found,
        taxi_cargo_dispatch,
        waybill_ref='bad_waybill',
):
    response = await taxi_cargo_dispatch.post(
        'v1/waybill/paid-cancel', json={'waybill_ref': waybill_ref},
    )
    assert response.status_code == 404
