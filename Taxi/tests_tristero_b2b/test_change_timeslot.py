import pytest


@pytest.mark.parametrize('status', [200, 400, 404, 409])
@pytest.mark.parametrize(
    'timeslot',
    [
        None,
        {
            'start': '2021-07-15T17:00:00+00:00',
            'end': '2021-07-15T18:00:00+00:00',
        },
    ],
)
async def test_change_timeslot(
        taxi_tristero_b2b, mockserver, status, timeslot,
):
    order_id = (
        '123e4567-e89b-12d3-a456-426614174000'
        if status != 400
        else 'not_a_uuid'
    )

    @mockserver.json_handler(
        '/tristero-parcels/internal/v1/parcels/v1/change-timeslot',
    )
    def _mock_parcels(request):
        if status == 400:
            assert False
        assert request.json['order_id'] == order_id
        if timeslot is not None:
            assert request.json['timeslot'] == timeslot
        return mockserver.make_response(status=status)

    request_json = {'order_id': order_id}
    if timeslot is not None:
        request_json['timeslot'] = timeslot

    response = await taxi_tristero_b2b.post(
        'tristero/v1/change-timeslot', json=request_json,
    )
    assert response.status_code == status
    assert _mock_parcels.has_calls == (status != 400)
