import pytest


REQUEST_EXAMPLE = {
    'acceptance_id': 'some_acceptance_id',
    'courier_id': 'some_courier_id',
    'depot_id': 'some_depot_id',
    'delivery_date': '2022-06-21',
    'courier_name': 'Иванов Иван Иванович',
    'order_data': [
        {'ref_order': 'market_order_1', 'vendor': 'beru'},
        {'ref_order': 'market_order_2', 'vendor': 'beru'},
    ],
}


async def test_acceptance_ok(taxi_tristero_b2b, mockserver):
    @mockserver.json_handler(
        '/tristero-parcels/internal/v1/parcels/v1/acceptance',
    )
    def _mock_parcels(request):
        assert request.json == REQUEST_EXAMPLE
        return mockserver.make_response(status=200)

    response = await taxi_tristero_b2b.post(
        '/tristero/v1/acceptance', json=REQUEST_EXAMPLE,
    )
    assert response.status_code == 200


async def test_acceptance_500(taxi_tristero_b2b, mockserver):
    @mockserver.json_handler(
        '/tristero-parcels/internal/v1/parcels/v1/acceptance',
    )
    def _mock_parcels(request):
        return mockserver.make_response(status=500)

    response = await taxi_tristero_b2b.post(
        '/tristero/v1/acceptance', json=REQUEST_EXAMPLE,
    )
    assert response.status_code == 500


@pytest.mark.parametrize('error_status', [400, 403, 404, 409, 410])
async def test_acceptance_wms_errors(
        taxi_tristero_b2b, mockserver, error_status,
):
    @mockserver.json_handler(
        '/tristero-parcels/internal/v1/parcels/v1/acceptance',
    )
    def _mock_parcels(request):
        return mockserver.make_response(
            json={'code': str(error_status), 'message': 'error_message'},
            status=error_status,
        )

    response = await taxi_tristero_b2b.post(
        '/tristero/v1/acceptance', json=REQUEST_EXAMPLE,
    )
    assert response.status_code == error_status
    assert response.json() == {
        'code': str(error_status),
        'message': 'error_message',
    }
