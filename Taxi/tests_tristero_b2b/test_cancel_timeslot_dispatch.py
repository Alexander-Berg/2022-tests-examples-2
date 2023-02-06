import pytest


@pytest.mark.parametrize('status', [200, 400, 404, 409])
async def test_cancel_timeslot_dispatch(taxi_tristero_b2b, mockserver, status):
    order_id = (
        '123e4567-e89b-12d3-a456-426614174000'
        if status != 400
        else 'not_a_uuid'
    )

    @mockserver.json_handler(
        '/tristero-parcels/internal/v1/parcels/cancel-timeslot-dispatch',
    )
    def _mock_parcels(request):
        if status == 400:
            assert False
        assert request.json['order_id'] == order_id
        return mockserver.make_response(status=status)

    response = await taxi_tristero_b2b.post(
        'tristero/v1/cancel-timeslot-dispatch', json={'order_id': order_id},
    )
    assert response.status_code == status
